"""Лёгкая проверка Instagram-профиля без логина.

Инстаграм агрессивно ограничивает анонимных, поэтому делаем best-effort:
1. Тянем публичный HTML страницы профиля.
2. Парсим og:description / тег с био — там обычно видны ссылки и счётчики.
3. Ищем признаки наличия сайта в био (ссылка не на соцсеть).

Если IG блокирует — возвращаем None, и решение по лиду принимается по 2GIS.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
from loguru import logger
from selectolax.parser import HTMLParser
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .two_gis import _detect_social  # переиспользуем эвристику

_USERNAME_RE = re.compile(r"instagram\.com/([A-Za-z0-9._]+)")
_FOLLOWERS_RE = re.compile(r"([\d.,KMkmКМ]+)\s+(?:Followers|подписчик)", re.IGNORECASE)
_URL_IN_TEXT_RE = re.compile(r"https?://[^\s\"'<>]+")


@dataclass(slots=True)
class InstagramProfile:
    username: str
    bio: str | None
    external_url: str | None
    followers: int | None
    raw_links: list[str]

    @property
    def has_real_website(self) -> bool:
        if self.external_url and not _detect_social(self.external_url):
            return True
        return any(not _detect_social(u) for u in self.raw_links)


def extract_username(url: str) -> str | None:
    m = _USERNAME_RE.search(url)
    if m:
        username = m.group(1).strip("/")
        return username or None
    # бывает, что в карточке указан просто "@nick"
    if url.startswith("@"):
        return url[1:].strip()
    if "/" not in url and "." not in url:
        return url.strip()
    return None


class InstagramChecker:
    """Best-effort анализатор IG-профиля без авторизации."""

    def __init__(self, timeout: float = 15.0) -> None:
        self._client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={
                # под мобильный браузер — IG отдаёт чуть менее зашифрованный HTML
                "User-Agent": (
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                    "Version/17.0 Mobile/15E148 Safari/604.1"
                ),
                "Accept-Language": "ru,en;q=0.8",
            },
        )

    async def __aenter__(self) -> InstagramChecker:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self._client.aclose()

    async def fetch(self, url_or_username: str) -> InstagramProfile | None:
        username = extract_username(url_or_username)
        if not username:
            return None
        url = f"https://www.instagram.com/{username}/"

        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(2),
                wait=wait_exponential(multiplier=1, min=1, max=4),
                retry=retry_if_exception_type(httpx.TransportError),
                reraise=True,
            ):
                with attempt:
                    resp = await self._client.get(url)
        except httpx.HTTPError as e:
            logger.debug("IG fetch error for {}: {}", username, e)
            return None

        if resp.status_code in (401, 403, 429):
            logger.debug("IG blocked anonymous access for {}", username)
            return InstagramProfile(
                username=username,
                bio=None,
                external_url=None,
                followers=None,
                raw_links=[],
            )
        if resp.status_code >= 400:
            return None

        return _parse_profile_html(username, resp.text)


def _parse_profile_html(username: str, html: str) -> InstagramProfile:
    tree = HTMLParser(html)

    bio: str | None = None
    external_url: str | None = None
    followers: int | None = None

    # 1. og:description — самый надёжный источник у IG
    og = tree.css_first('meta[property="og:description"]')
    if og is not None:
        desc = og.attributes.get("content") or ""
        bio = desc or None
        m = _FOLLOWERS_RE.search(desc)
        if m:
            followers = _parse_compact_number(m.group(1))

    # 2. ld+json — иногда отдаётся как application/ld+json
    for script in tree.css('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.text() or "{}")
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            url = data.get("url")
            if url and "instagram.com" not in url:
                external_url = url
            if not bio and (d := data.get("description")):
                bio = d

    # 3. ищем все http-ссылки в тексте (часто внешний сайт лежит в bio как plain-text)
    raw_links = _URL_IN_TEXT_RE.findall(html)
    raw_links = [u for u in raw_links if _looks_like_user_link(u)]

    if not external_url:
        for u in raw_links:
            if not _is_instagram_internal(u):
                external_url = u
                break

    return InstagramProfile(
        username=username,
        bio=bio,
        external_url=external_url,
        followers=followers,
        raw_links=raw_links[:10],
    )


def _looks_like_user_link(u: str) -> bool:
    try:
        host = urlparse(u).hostname or ""
    except ValueError:
        return False
    if not host:
        return False
    bad = ("cdninstagram", "fbcdn", "facebook.net", "static.cdninstagram", "instagram.com/static")
    return not any(b in u for b in bad)


def _is_instagram_internal(u: str) -> bool:
    host = (urlparse(u).hostname or "").lower()
    return host.endswith("instagram.com") or host.endswith("cdninstagram.com")


def _parse_compact_number(s: str) -> int | None:
    s = s.replace(",", "").replace(" ", "").lower()
    mult = 1
    if s.endswith(("k", "к")):
        mult = 1_000
        s = s[:-1]
    elif s.endswith(("m", "м")):
        mult = 1_000_000
        s = s[:-1]
    try:
        return int(float(s) * mult)
    except ValueError:
        return None
