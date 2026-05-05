from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class SocialKind(StrEnum):
    INSTAGRAM = "instagram"
    VK = "vk"
    FACEBOOK = "facebook"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    OTHER = "other"


class Contact(BaseModel):
    """Один контакт из карточки 2GIS."""

    type: str
    value: str
    comment: str | None = None


class Place(BaseModel):
    """Место в 2GIS — компания/организация."""

    id: str
    name: str
    address: str | None = None
    city: str | None = None
    rubrics: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    emails: list[str] = Field(default_factory=list)
    websites: list[str] = Field(default_factory=list)
    socials: dict[SocialKind, list[str]] = Field(default_factory=dict)
    rating: float | None = None
    reviews_count: int | None = None
    point: tuple[float, float] | None = None  # (lon, lat)
    dgis_url: str | None = None

    @property
    def has_website(self) -> bool:
        """Реальный сайт, не соцсеть."""
        return any(_looks_like_real_website(u) for u in self.websites)

    @property
    def primary_instagram(self) -> str | None:
        igs = self.socials.get(SocialKind.INSTAGRAM, [])
        return igs[0] if igs else None


def _looks_like_real_website(url: str) -> bool:
    """Сайт != соцсеть/мессенджер."""
    url = url.lower().strip()
    blacklist = (
        "instagram.com",
        "facebook.com",
        "vk.com",
        "vk.ru",
        "ok.ru",
        "t.me",
        "telegram.me",
        "wa.me",
        "whatsapp.com",
        "youtube.com",
        "youtu.be",
        "tiktok.com",
        "2gis.ru",
        "2gis.com",
        "yandex.ru/maps",
        "google.com/maps",
    )
    return not any(b in url for b in blacklist)


class LeadVerdict(StrEnum):
    GOOD_LEAD = "good_lead"
    HAS_WEBSITE = "has_website"
    NOT_TARGET = "not_target"
    NO_CONTACT = "no_contact"


class Lead(BaseModel):
    """Финальный лид, готовый к отправке."""

    place: Place
    verdict: LeadVerdict
    reasons: list[str] = Field(default_factory=list)
    instagram_has_website_in_bio: bool | None = None
    instagram_followers: int | None = None
    score: float = 0.0
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def telegram_message(self) -> str:
        p = self.place
        lines = [
            f"<b>{_escape(p.name)}</b>",
            f"📍 {_escape(p.address or '—')}",
            f"🏷 {_escape(', '.join(p.rubrics) or '—')}",
        ]
        if p.rating is not None:
            lines.append(f"⭐ {p.rating} ({p.reviews_count or 0} отзывов)")
        if p.phones:
            lines.append("📞 " + ", ".join(_escape(x) for x in p.phones[:3]))
        if p.emails:
            lines.append("✉️ " + ", ".join(_escape(x) for x in p.emails[:2]))
        ig = p.primary_instagram
        if ig:
            lines.append(f"📸 {_escape(ig)}")
        if p.dgis_url:
            lines.append(f"🗺 <a href=\"{p.dgis_url}\">Открыть в 2GIS</a>")
        lines.append("")
        lines.append("🎯 <b>Почему это лид:</b>")
        for r in self.reasons:
            lines.append(f"• {_escape(r)}")
        lines.append(f"\n<i>score: {self.score:.2f}</i>")
        return "\n".join(lines)


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
