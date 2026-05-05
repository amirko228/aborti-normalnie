# lead-scraper-2gis

Async-парсер на Python 3.11+, который:

1. Ходит в **2GIS Catalog API** и собирает компании по рубрикам и городу (кафе, рестораны, отели, салоны красоты, барбершопы, магазины, автосервисы и т.п.).
2. Берёт из карточки **контакты и соцсети** (телефоны, email, Instagram, VK, Telegram).
3. **Отбрасывает** тех, у кого уже есть сайт — ни в 2GIS, ни в био Instagram.
4. **Скорит** оставшихся (рейтинг, отзывы, наличие email, активный Instagram) и шлёт самые жирные лиды в **Telegram** через aiogram 3.
5. Запоминает уже отправленных в `data/seen.json`, не дублирует.

То есть на выходе у тебя — список бизнесов, которым реально можно продать сайт или Telegram-бота.

## Стек (всё современное и асинхронное)

| Что                        | Библиотека                                      |
|----------------------------|-------------------------------------------------|
| HTTP                       | `httpx` (async, HTTP/2)                         |
| Конфиг                     | `pydantic-settings` (v2) + `.env`               |
| Модели данных              | `pydantic` v2 + `StrEnum`                       |
| HTML-парсинг (Instagram)   | `selectolax` (быстрее BeautifulSoup в разы)     |
| Retry                      | `tenacity`                                      |
| Telegram                   | `aiogram` 3                                     |
| CLI                        | `typer` + `rich`                                |
| Логи                       | `loguru`                                        |
| Линт / типы                | `ruff`, `mypy --strict`                         |

## Установка

```bash
git clone https://github.com/amirko228/aborti-normalnie.git
cd aborti-normalnie
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# заполни DGIS_API_KEY и (по желанию) TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID
```

### Где взять ключи

- **DGIS_API_KEY** — бесплатный ключ на [dev.2gis.ru](https://dev.2gis.ru/) (Catalog API).
- **TELEGRAM_BOT_TOKEN** — у [@BotFather](https://t.me/BotFather).
- **TELEGRAM_CHAT_ID** — твой собственный chat_id (можно узнать у [@userinfobot](https://t.me/userinfobot)).

## Запуск

```bash
# дефолт: город и рубрики из .env
lead-scraper scrape

# свой город и пара рубрик, по 100 мест на каждую
lead-scraper scrape -c "Казань" -r "кафе" -r "барбершоп" -l 100

# только сбор, без Telegram (пишет в data/leads.jsonl)
lead-scraper scrape --no-telegram

# отбрасывать слабые лиды
lead-scraper scrape --min-score 1.5

# проверить конфиг
lead-scraper check-config
```

## Как устроен пайплайн

```
        ┌──────────────────┐
        │  TwoGisClient    │  httpx + retry, пагинация по /items
        └────────┬─────────┘
                 ▼
        ┌──────────────────┐
        │   Place[]        │  pydantic-модели (контакты, соцсети)
        └────────┬─────────┘
                 ▼
        ┌──────────────────┐
        │  evaluate_all    │  фильтр по рубрике + наличию сайта
        └────────┬─────────┘
                 ▼      (если есть Instagram)
        ┌──────────────────┐
        │ InstagramChecker │  смотрит og:description / external_url
        └────────┬─────────┘
                 ▼
        ┌──────────────────┐
        │ SeenStore + JSONL│  дедуп и история
        └────────┬─────────┘
                 ▼
        ┌──────────────────┐
        │ TelegramNotifier │  aiogram 3 → твой чат
        └──────────────────┘
```

## Логика фильтрации

Место помечается как `GOOD_LEAD`, если **все** условия выполнены:

- рубрика входит в «целевые» (кафе/отель/салон/магазин/...);
- есть хотя бы один контакт (телефон/email/соцсеть);
- в 2GIS не указан реальный сайт (соцсети не считаем за сайт);
- если указан Instagram, в его био тоже **нет** ссылки на сайт.

Скоринг (просто, чтобы наверх всплывали жирные лиды):

| Сигнал                              | +score |
|-------------------------------------|--------|
| 200+ отзывов в 2GIS                 | +2.0   |
| 50–199 отзывов                      | +1.0   |
| Рейтинг ≥ 4.3                       | +0.5   |
| Есть email                          | +0.5   |
| Есть телефон                        | +0.3   |
| Активный Instagram (>500 подписок)  | +1.0   |

## Структура проекта

```
src/lead_scraper/
├── config.py            # pydantic-settings, .env
├── models.py            # Place, Lead, SocialKind, LeadVerdict
├── scraper/
│   ├── two_gis.py       # async-клиент 2GIS + парсинг items
│   └── instagram.py     # best-effort анализ IG-профиля
├── filters.py           # evaluate_place / evaluate_all
├── notifier/
│   └── telegram.py      # aiogram 3 sender
├── storage.py           # SeenStore + JSONL-лог
├── runner.py            # пайплайн целиком
└── cli.py               # typer-команды
```

## Этика и лимиты

- Используем **официальный 2GIS API** с твоим ключом — это легально.
- Instagram скрейпим без логина, best-effort. Если IG отдаёт 401/429 — просто не учитываем био.
- Между запросами стоят небольшие задержки и concurrency-лимит.

## Что можно расширить

- Добавить парсинг карточки `byid` для расширенных полей (часы работы, фото).
- Подключить геопоиск по bbox карты вместо названия города.
- Перенести хранилище с JSON на SQLite/Postgres.
- Добавить `--export csv` для выгрузки в табличку.
- Автозапуск раз в сутки через systemd-timer/cron.
