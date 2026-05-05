"""Логика отбора: какие места — лиды, какие — нет."""

from __future__ import annotations

import asyncio

from loguru import logger

from .config import settings
from .models import Lead, LeadVerdict, Place
from .scraper.instagram import InstagramChecker

# Рубрики, которым реально нужен сайт/телеграм-бот.
_TARGET_KEYWORDS: tuple[str, ...] = (
    "кафе",
    "ресторан",
    "бар",
    "пицц",
    "сушистр",
    "суши",
    "кофе",
    "кондитер",
    "пекарн",
    "столов",
    "буфет",
    "фастфуд",
    "доставка ед",
    "отель",
    "хостел",
    "гостин",
    "апартамент",
    "салон красоты",
    "барбершоп",
    "парикмахер",
    "ноготь",
    "ногт",
    "маникюр",
    "космет",
    "spa",
    "спа",
    "массаж",
    "магазин",
    "бутик",
    "автосервис",
    "шиномонт",
    "автомойк",
    "сто",
    "фитнес",
    "йога",
    "студия танц",
    "ремонт",
    "ателье",
    "химчистк",
    "цветы",
    "флорист",
)


def is_target_business(place: Place) -> bool:
    haystack = " ".join([place.name, *place.rubrics]).lower()
    return any(kw in haystack for kw in _TARGET_KEYWORDS)


def has_any_contact(place: Place) -> bool:
    return bool(place.phones or place.emails or place.socials or place.websites)


def _activity_reasons(place: Place) -> list[str]:
    out: list[str] = []
    if place.reviews_count and place.reviews_count >= 200:
        out.append(f"много отзывов в 2GIS ({place.reviews_count})")
    elif place.reviews_count and place.reviews_count >= 30:
        out.append(f"заметная активность ({place.reviews_count} отзывов)")
    if place.rating and place.rating >= 4.0:
        out.append(f"рейтинг {place.rating}")
    return out


def _activity_score(place: Place) -> float:
    score = 0.0
    if place.reviews_count:
        if place.reviews_count >= 500:
            score += 2.5
        elif place.reviews_count >= 200:
            score += 2.0
        elif place.reviews_count >= 50:
            score += 1.0
        elif place.reviews_count >= 30:
            score += 0.5
    if place.rating and place.rating >= 4.3:
        score += 0.5
    return score


async def evaluate_place(
    place: Place,
    ig_checker: InstagramChecker | None,
) -> Lead:
    reasons: list[str] = []
    score = 0.0

    if not is_target_business(place):
        return Lead(place=place, verdict=LeadVerdict.NOT_TARGET, reasons=["рубрика не целевая"])

    # Если у API-ключа нет прав на contact_groups (демо), всё равно отдаём
    # активные места как кандидатов — пользователь дочекаит контакты руками
    # по ссылке на карточку 2GIS.
    if not has_any_contact(place):
        if place.reviews_count and place.reviews_count >= 30:
            score = _activity_score(place)
            return Lead(
                place=place,
                verdict=LeadVerdict.GOOD_LEAD,
                reasons=[
                    "контакты не пришли из API — открой карточку 2GIS",
                    *_activity_reasons(place),
                ],
                contacts_unknown=True,
                score=round(score, 2),
            )
        return Lead(
            place=place,
            verdict=LeadVerdict.NO_CONTACT,
            reasons=["контактов нет, активность слабая"],
        )

    if place.has_website:
        return Lead(
            place=place,
            verdict=LeadVerdict.HAS_WEBSITE,
            reasons=[f"уже есть сайт: {place.websites[0]}"],
        )

    # Проверяем Instagram, если он есть и в био нет ссылки на сайт.
    ig_has_site: bool | None = None
    ig_followers: int | None = None
    if ig_checker and (ig_url := place.primary_instagram):
        profile = await ig_checker.fetch(ig_url)
        if profile is None:
            reasons.append("Instagram указан, но профиль недоступен")
        else:
            ig_followers = profile.followers
            if profile.has_real_website:
                ig_has_site = True
                return Lead(
                    place=place,
                    verdict=LeadVerdict.HAS_WEBSITE,
                    reasons=[f"в био Instagram есть сайт: {profile.external_url or 'ссылка'}"],
                    instagram_has_website_in_bio=True,
                    instagram_followers=ig_followers,
                )
            ig_has_site = False
            reasons.append("в био Instagram нет ссылки на сайт")
            if ig_followers and ig_followers > 500:
                score += 1.0
                reasons.append(f"активный Instagram ({ig_followers}+ подписчиков)")

    # Скоринг: чем больше отзывов и выше рейтинг — тем интереснее лид.
    if place.reviews_count:
        if place.reviews_count >= 200:
            score += 2.0
            reasons.append(f"много отзывов в 2GIS ({place.reviews_count})")
        elif place.reviews_count >= 50:
            score += 1.0
            reasons.append(f"заметная активность ({place.reviews_count} отзывов)")
    if place.rating and place.rating >= 4.3:
        score += 0.5
        reasons.append(f"хороший рейтинг {place.rating}")
    if place.phones:
        score += 0.3
    if place.emails:
        score += 0.5
        reasons.append("есть email — можно писать КП")

    if not reasons:
        reasons.append("нет сайта, есть контакты — можно предлагать")

    return Lead(
        place=place,
        verdict=LeadVerdict.GOOD_LEAD,
        reasons=reasons,
        instagram_has_website_in_bio=ig_has_site,
        instagram_followers=ig_followers,
        score=round(score, 2),
    )


async def evaluate_all(
    places: list[Place],
    ig_checker: InstagramChecker | None,
) -> list[Lead]:
    sem = asyncio.Semaphore(settings.concurrency)

    async def _one(p: Place) -> Lead:
        async with sem:
            try:
                return await evaluate_place(p, ig_checker)
            except Exception as e:
                logger.warning("evaluate_place упал на {}: {}", p.name, e)
                return Lead(place=p, verdict=LeadVerdict.NO_CONTACT, reasons=[f"ошибка: {e}"])

    return await asyncio.gather(*[_one(p) for p in places])
