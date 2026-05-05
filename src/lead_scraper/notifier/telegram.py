"""Отправка готовых лидов в Telegram через aiogram 3."""

from __future__ import annotations

import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter
from loguru import logger

from ..config import settings
from ..models import Lead

# Telegram режет сообщения длиннее 4096 символов. Берём с запасом.
_TG_MSG_LIMIT = 3800


class TelegramNotifier:
    def __init__(self, token: str | None = None, chat_id: str | None = None) -> None:
        self._token = token or settings.telegram_bot_token.get_secret_value()
        self._chat_id = chat_id or settings.telegram_chat_id
        if not self._token or not self._chat_id:
            raise RuntimeError("TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не заданы")
        self._bot = Bot(
            token=self._token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

    async def __aenter__(self) -> TelegramNotifier:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    async def close(self) -> None:
        await self._bot.session.close()

    async def send_summary(self, total: int, sent: int) -> None:
        await self._safe_send(
            f"✅ <b>Парсинг 2GIS завершён</b>\n"
            f"Найдено мест: {total}\nОтобрано лидов: <b>{sent}</b>"
        )

    async def send_lead(self, lead: Lead) -> None:
        await self._safe_send(lead.telegram_message(), disable_web_page_preview=True)

    async def send_leads(self, leads: list[Lead]) -> None:
        """Все лиды одним сообщением (или несколькими частями, если не влезает)."""
        if not leads:
            return
        for chunk in _build_chunks(leads):
            await self._safe_send(chunk, disable_web_page_preview=True)
            await asyncio.sleep(0.5)

    async def _safe_send(self, text: str, *, disable_web_page_preview: bool = False) -> None:
        try:
            await self._bot.send_message(
                chat_id=self._chat_id,
                text=text,
                disable_web_page_preview=disable_web_page_preview,
            )
        except TelegramRetryAfter as e:
            logger.warning("Telegram flood-control: ждём {}s", e.retry_after)
            await asyncio.sleep(e.retry_after + 1)
            await self._bot.send_message(
                chat_id=self._chat_id,
                text=text,
                disable_web_page_preview=disable_web_page_preview,
            )


def _format_lead_compact(idx: int, lead: Lead) -> str:
    """Одна-две строки на лид: название-ссылка, рубрика, рейтинг, контакты."""
    p = lead.place
    name = _esc(p.name)
    title = (
        f'<b>{idx}. <a href="{p.dgis_url}">{name}</a></b>'
        if p.dgis_url
        else f"<b>{idx}. {name}</b>"
    )
    parts = [title]

    meta_bits: list[str] = []
    if p.rating is not None:
        meta_bits.append(f"⭐ {p.rating} ({p.reviews_count or 0})")
    if p.rubrics:
        meta_bits.append(_esc(p.rubrics[0]))
    if p.address:
        meta_bits.append(_esc(p.address))
    if meta_bits:
        parts.append("   " + " · ".join(meta_bits))

    contact_bits: list[str] = []
    if p.phones:
        contact_bits.append("📞 " + _esc(p.phones[0]))
    if p.primary_instagram:
        contact_bits.append("📸 " + _esc(p.primary_instagram))
    if p.emails:
        contact_bits.append("✉️ " + _esc(p.emails[0]))
    if contact_bits:
        parts.append("   " + " | ".join(contact_bits))
    elif lead.contacts_unknown:
        parts.append("   ⚠️ контакты в карточке 2GIS")

    return "\n".join(parts)


def _build_chunks(leads: list[Lead]) -> list[str]:
    """Склеиваем все лиды в одно сообщение (или несколько, если >4096 символов)."""
    header = (
        f"✅ <b>Лиды 2GIS</b> — найдено {len(leads)} мест "
        f"без сайта, отсортировано по score\n"
    )
    chunks: list[str] = []
    buf = [header]
    size = len(header)
    for i, lead in enumerate(leads, 1):
        block = "\n" + _format_lead_compact(i, lead) + "\n"
        if size + len(block) > _TG_MSG_LIMIT and len(buf) > 1:
            chunks.append("".join(buf))
            buf = [f"<b>… продолжение ({len(chunks) + 1})</b>\n", block]
            size = len(buf[0]) + len(block)
        else:
            buf.append(block)
            size += len(block)
    if buf:
        chunks.append("".join(buf))
    return chunks


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
