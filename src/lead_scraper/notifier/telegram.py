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
        for lead in leads:
            await self.send_lead(lead)
            await asyncio.sleep(0.5)  # уважаем rate-limit Telegram

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
