"""Простое файловое хранилище: дедуп уже отправленных лидов + лог в JSONL."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Lead


class SeenStore:
    """Множество id мест, которые мы уже отправляли — чтобы не спамить повторно."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._ids: set[str] = set()
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                self._ids = set(json.loads(self._path.read_text("utf-8")))
            except (json.JSONDecodeError, OSError):
                self._ids = set()

    def __contains__(self, place_id: str) -> bool:
        return place_id in self._ids

    def add(self, place_id: str) -> None:
        self._ids.add(place_id)

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(sorted(self._ids), ensure_ascii=False), "utf-8")


class LeadsLog:
    """Append-only JSONL c найденными лидами — чтобы потом анализировать/выгружать."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def append(self, lead: Lead) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as f:
            f.write(lead.model_dump_json() + "\n")
