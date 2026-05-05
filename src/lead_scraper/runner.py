"""Точка входа пайплайна: 2GIS → фильтр → Instagram → Telegram."""

from __future__ import annotations

from collections.abc import Sequence

from loguru import logger
from rich.console import Console
from rich.table import Table

from .config import settings
from .filters import evaluate_all
from .models import Lead, LeadVerdict
from .notifier.telegram import TelegramNotifier
from .scraper.instagram import InstagramChecker
from .scraper.two_gis import TwoGisClient
from .storage import LeadsLog, SeenStore

console = Console()


async def run(
    city: str,
    rubrics: Sequence[str],
    max_per_rubric: int,
    *,
    check_instagram: bool = True,
    send_telegram: bool = True,
    min_score: float = 0.0,
) -> list[Lead]:
    """Главный конвейер. Возвращает только хорошие лиды."""
    logger.info("старт: город={}, рубрики={}, лимит={}", city, list(rubrics), max_per_rubric)

    async with TwoGisClient() as dgis:
        places = await dgis.search_many(list(rubrics), city, max_per_rubric)
    logger.info("получено {} уникальных мест", len(places))

    ig: InstagramChecker | None = None
    if check_instagram:
        ig = InstagramChecker()
    try:
        leads = await evaluate_all(places, ig)
    finally:
        if ig is not None:
            await ig.__aexit__(None, None, None)

    good = [
        l
        for l in leads
        if l.verdict == LeadVerdict.GOOD_LEAD and l.score >= min_score
    ]
    good.sort(key=lambda l: l.score, reverse=True)

    _print_summary(leads, good)

    seen = SeenStore(settings.seen_storage)
    log = LeadsLog(settings.leads_storage)
    fresh = [l for l in good if l.place.id not in seen]
    for l in fresh:
        log.append(l)
        seen.add(l.place.id)
    seen.save()

    logger.info("новых лидов для отправки: {} (всего хороших: {})", len(fresh), len(good))

    if send_telegram and settings.telegram_enabled and fresh:
        async with TelegramNotifier() as tg:
            await tg.send_summary(total=len(places), sent=len(fresh))
            await tg.send_leads(fresh)
    elif send_telegram and not settings.telegram_enabled:
        logger.warning("Telegram не настроен — отправка пропущена")

    return fresh


def _print_summary(all_leads: list[Lead], good: list[Lead]) -> None:
    by_verdict: dict[LeadVerdict, int] = {}
    for l in all_leads:
        by_verdict[l.verdict] = by_verdict.get(l.verdict, 0) + 1

    table = Table(title="Итоги фильтрации", show_lines=False)
    table.add_column("Категория", style="cyan")
    table.add_column("Количество", justify="right", style="magenta")
    for verdict, count in by_verdict.items():
        table.add_row(verdict.value, str(count))
    console.print(table)

    if good:
        top = Table(title=f"Топ-{min(15, len(good))} лидов по score")
        top.add_column("#", justify="right", style="dim")
        top.add_column("Название", style="bold")
        top.add_column("Рубрики")
        top.add_column("Телефон")
        top.add_column("IG")
        top.add_column("Score", justify="right", style="green")
        for i, l in enumerate(good[:15], 1):
            p = l.place
            top.add_row(
                str(i),
                p.name,
                ", ".join(p.rubrics[:2]),
                (p.phones[0] if p.phones else "—"),
                (p.primary_instagram or "—"),
                f"{l.score:.2f}",
            )
        console.print(top)
