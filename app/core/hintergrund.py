"""Hintergrund-Tasks mit gehaltener Referenz.

``asyncio.create_task`` haelt den Task nur schwach: Ohne eigene Referenz kann ihn der Garbage Collector vor dem Ende
einsammeln (Python-Dokumentation zu ``create_task``). ``starte`` haelt ihn bis zum Abschluss fest.
"""
from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any

_LAUFEND: set[asyncio.Task[Any]] = set()


def starte(aufgabe: Coroutine[Any, Any, Any]) -> asyncio.Task[Any]:
    task = asyncio.create_task(aufgabe)
    _LAUFEND.add(task)
    task.add_done_callback(_LAUFEND.discard)
    return task
