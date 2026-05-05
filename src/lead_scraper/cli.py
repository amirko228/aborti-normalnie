"""CLI-обёртка над runner.run на Typer."""

from __future__ import annotations

import asyncio
import sys

import typer
from loguru import logger
from rich.console import Console

from .config import settings
from .runner import run

app = typer.Typer(
    add_completion=False,
    help="Парсер 2GIS: ищем малый бизнес без сайта и шлём в Telegram",
    no_args_is_help=False,
)
console = Console()


def _setup_logging(verbose: bool) -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level="DEBUG" if verbose else "INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <7}</level> | {message}",
    )


@app.command()
def scrape(
    city: str = typer.Option(settings.default_city, "--city", "-c", help="Город поиска"),
    rubric: list[str] = typer.Option(  # noqa: B008
        None, "--rubric", "-r", help="Рубрика (можно несколько раз). Пример: -r кафе -r отель"
    ),
    limit: int = typer.Option(
        settings.max_places_per_rubric, "--limit", "-l", help="Лимит мест на одну рубрику"
    ),
    no_instagram: bool = typer.Option(False, "--no-instagram", help="Не проверять Instagram"),
    no_telegram: bool = typer.Option(False, "--no-telegram", help="Не отправлять в Telegram"),
    min_score: float = typer.Option(0.0, "--min-score", help="Отбрасывать лиды со score ниже"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Подробные логи"),
) -> None:
    """Запустить парсинг."""
    _setup_logging(verbose)
    rubrics = rubric or settings.rubrics_list
    if not rubrics:
        console.print("[red]Не указано ни одной рубрики[/red]")
        raise typer.Exit(code=1)

    try:
        leads = asyncio.run(
            run(
                city=city,
                rubrics=rubrics,
                max_per_rubric=limit,
                check_instagram=not no_instagram,
                send_telegram=not no_telegram,
                min_score=min_score,
            )
        )
    except KeyboardInterrupt:
        console.print("[yellow]Прервано пользователем[/yellow]")
        raise typer.Exit(code=130) from None

    console.print(
        f"\n[bold green]Готово.[/bold green] Новых лидов: {len(leads)}. "
        f"Лог: {settings.leads_storage}"
    )


@app.command()
def check_config() -> None:
    """Показать текущую конфигурацию (без секретов)."""
    _setup_logging(False)
    console.print({
        "city": settings.default_city,
        "rubrics": settings.rubrics_list,
        "max_per_rubric": settings.max_places_per_rubric,
        "concurrency": settings.concurrency,
        "dgis_key_set": bool(settings.dgis_api_key.get_secret_value()),
        "telegram_enabled": settings.telegram_enabled,
        "leads_storage": str(settings.leads_storage),
        "seen_storage": str(settings.seen_storage),
    })


def main() -> None:
    app()


if __name__ == "__main__":
    main()
