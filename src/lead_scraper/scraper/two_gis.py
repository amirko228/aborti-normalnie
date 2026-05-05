"""Async-клиент 2GIS Catalog API.

Документация: https://docs.2gis.com/ru/api/search/places/overview
Эндпоинты:
- GET {base}/items                 — поиск компаний
- GET {base}/items/byid            — карточка компании по id (с расширенными полями)
"""

from __future__ import annotations

import asyncio
import re
from collections.abc import AsyncIterator
from typing import Any

import httpx
from loguru import logger
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..config import settings
from ..models import Place, SocialKind

# Поля, которые просим у API. Чем больше — тем дороже запрос, но нам нужны контакты.
_FIELDS = ",".join(
    [
        "items.point",
        "items.adm_div",
        "items.contact_groups",
        "items.rubrics",
        "items.reviews",
        "items.external_content",
        "items.locale",
        "items.flags",
        "items.org",
    ]
)

_PAGE_SIZE = 10  # верхняя граница для демо-ключей; платные тарифы тянут до 50, но 10 безопасно


class TwoGisError(RuntimeError):
    pass


class TwoGisClient:
    """Тонкая обёртка над 2GIS Catalog API c retry/throttle."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._api_key = api_key or settings.dgis_api_key.get_secret_value()
        if not self._api_key:
            raise TwoGisError("DGIS_API_KEY не задан — получите ключ на dev.2gis.ru")
        self._base_url = base_url or settings.dgis_base_url
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout or settings.request_timeout,
            http2=True,
            headers={"User-Agent": "lead-scraper-2gis/0.1"},
        )

    async def __aenter__(self) -> TwoGisClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        params = {**params, "key": self._api_key}
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(4),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.TransportError, httpx.HTTPStatusError)),
            reraise=True,
        ):
            with attempt:
                resp = await self._client.get(path, params=params)
                if resp.status_code == 429:
                    raise httpx.HTTPStatusError("rate-limited", request=resp.request, response=resp)
                resp.raise_for_status()
                data: dict[str, Any] = resp.json()
                meta = data.get("meta", {})
                code = meta.get("code")
                if code and code >= 400:
                    raise TwoGisError(f"2GIS error {code}: {meta.get('error', {})}")
                return data
        raise TwoGisError("unreachable")

    async def search(
        self,
        query: str,
        city: str,
        max_results: int = 200,
    ) -> AsyncIterator[Place]:
        """Поиск компаний по тексту в указанном городе с пагинацией."""
        page = 1
        seen = 0
        while seen < max_results:
            params = {
                "q": query,
                "city": city,
                "page": page,
                "page_size": min(_PAGE_SIZE, max_results - seen),
                "fields": _FIELDS,
                "type": "branch",
                "locale": "ru_RU",
            }
            data = await self._get("/items", params)
            items = data.get("result", {}).get("items", []) or []
            if not items:
                return
            for item in items:
                place = _parse_place(item, fallback_city=city)
                if place is not None:
                    yield place
                    seen += 1
                    if seen >= max_results:
                        return
            total = int(data.get("result", {}).get("total", 0))
            if page * _PAGE_SIZE >= total:
                return
            page += 1
            await asyncio.sleep(0.15)  # бережём API

    async def search_many(
        self,
        rubrics: list[str],
        city: str,
        max_per_rubric: int,
    ) -> list[Place]:
        """Параллельный поиск по нескольким рубрикам с дедупом по id."""
        sem = asyncio.Semaphore(settings.concurrency)

        async def _one(rubric: str) -> list[Place]:
            async with sem:
                logger.info("ищу '{}' в {}", rubric, city)
                out: list[Place] = []
                async for p in self.search(rubric, city, max_per_rubric):
                    out.append(p)
                logger.info("'{}' → {} мест", rubric, len(out))
                return out

        results = await asyncio.gather(*[_one(r) for r in rubrics])
        merged: dict[str, Place] = {}
        for batch in results:
            for p in batch:
                merged.setdefault(p.id, p)
        return list(merged.values())


# ---------- парсинг ответа 2GIS ----------

_PHONE_RE = re.compile(r"[\d+()\-\s]{7,}")


def _parse_place(item: dict[str, Any], fallback_city: str) -> Place | None:
    pid = item.get("id")
    name = item.get("name") or item.get("name_ex", {}).get("primary")
    if not pid or not name:
        return None

    address = item.get("address_name") or item.get("full_address_name") or item.get("address")
    rubrics = [r.get("name") for r in item.get("rubrics", []) if r.get("name")]
    reviews = item.get("reviews") or {}
    rating = reviews.get("general_rating")
    reviews_count = reviews.get("general_review_count")

    point = None
    pt = item.get("point") or {}
    if "lon" in pt and "lat" in pt:
        point = (float(pt["lon"]), float(pt["lat"]))

    city = fallback_city
    for div in item.get("adm_div", []) or []:
        if div.get("type") == "city" and div.get("name"):
            city = div["name"]
            break

    phones: list[str] = []
    emails: list[str] = []
    websites: list[str] = []
    socials: dict[SocialKind, list[str]] = {}

    for group in item.get("contact_groups", []) or []:
        for c in group.get("contacts", []) or []:
            ctype = (c.get("type") or "").lower()
            value = c.get("value") or c.get("text") or c.get("url") or ""
            if not value:
                continue
            if ctype == "phone":
                phones.append(value)
            elif ctype == "email":
                emails.append(value)
            elif ctype == "website":
                websites.append(value)
            elif ctype in {"instagram", "facebook", "vkontakte", "twitter", "youtube", "tiktok"}:
                kind = _SOCIAL_MAP.get(ctype, SocialKind.OTHER)
                socials.setdefault(kind, []).append(value)
            elif ctype == "telegram":
                socials.setdefault(SocialKind.TELEGRAM, []).append(value)
            elif ctype == "whatsapp":
                socials.setdefault(SocialKind.WHATSAPP, []).append(value)
            else:
                # любая ссылка — может быть соцсетью
                kind = _detect_social(value)
                if kind:
                    socials.setdefault(kind, []).append(value)
                elif value.startswith("http"):
                    websites.append(value)

    dgis_url = f"https://2gis.ru/firm/{pid}"

    return Place(
        id=str(pid),
        name=name,
        address=address,
        city=city,
        rubrics=rubrics,
        phones=_dedupe(phones),
        emails=_dedupe(emails),
        websites=_dedupe(websites),
        socials={k: _dedupe(v) for k, v in socials.items()},
        rating=float(rating) if rating is not None else None,
        reviews_count=int(reviews_count) if reviews_count is not None else None,
        point=point,
        dgis_url=dgis_url,
    )


_SOCIAL_MAP = {
    "instagram": SocialKind.INSTAGRAM,
    "facebook": SocialKind.FACEBOOK,
    "vkontakte": SocialKind.VK,
    "youtube": SocialKind.YOUTUBE,
    "tiktok": SocialKind.TIKTOK,
}


def _detect_social(url: str) -> SocialKind | None:
    u = url.lower()
    if "instagram.com" in u:
        return SocialKind.INSTAGRAM
    if "vk.com" in u or "vk.ru" in u:
        return SocialKind.VK
    if "facebook.com" in u or "fb.com" in u:
        return SocialKind.FACEBOOK
    if "t.me" in u or "telegram.me" in u:
        return SocialKind.TELEGRAM
    if "wa.me" in u or "whatsapp.com" in u:
        return SocialKind.WHATSAPP
    if "youtube.com" in u or "youtu.be" in u:
        return SocialKind.YOUTUBE
    if "tiktok.com" in u:
        return SocialKind.TIKTOK
    return None


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        key = x.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(x.strip())
    return out
