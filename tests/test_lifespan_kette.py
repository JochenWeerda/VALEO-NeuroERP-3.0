"""Der Start der Anwendung darf nicht an der Zahl der Router scheitern (20.10.2026).

FastAPI verschachtelt je ``include_router`` den Lifespan. Mit ueber 450 Unterroutern sprengte das unter uvicorn den
Python-Stack (RecursionError, alle E2E-Laeufe rot), waehrend die TestClient-Tests ohne Lifespan gruen blieben.
"""
from __future__ import annotations

import asyncio
import sys

from fastapi import APIRouter


def test_sammelrouter_verkettet_keine_standard_lifespans_und_startet_handler_einmal():
    from app.api.v1.api import _Sammelrouter

    sammel = _Sammelrouter()
    aufrufe: list[str] = []
    for nummer in range(600):
        unter = APIRouter()
        if nummer == 0:
            unter.add_event_handler("startup", lambda: aufrufe.append("start"))
        sammel.include_router(unter)

    async def starten() -> None:
        async with sammel.lifespan_context(object()):
            pass

    asyncio.run(starten())
    assert aufrufe == ["start"]


def test_anwendungen_starten_mit_knappem_stack():
    import main as produktion
    from app.main import app

    grenze = sys.getrecursionlimit()
    sys.setrecursionlimit(400)  # deutlich unter dem Standard: Spielraum fuer uvicorn und Middleware
    try:
        for anwendung in (app, produktion.app):
            async def starten(ziel=anwendung) -> None:
                async with ziel.router.lifespan_context(ziel):
                    pass

            asyncio.run(starten())
    finally:
        sys.setrecursionlimit(grenze)
