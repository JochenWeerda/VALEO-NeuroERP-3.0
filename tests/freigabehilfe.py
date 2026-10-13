"""Freigabe durch eine zweite Person in Tests (APPROVAL-001).

Tests, die buchen oder stornieren, gehen durch dieselbe Approval Engine wie der Betrieb: anfragen als die Person
des Tests, erteilen als eine zweite. Es gibt keinen Schalter, der die Freigabe abstellt.
"""
from __future__ import annotations

from typing import Any

from app.core.database import SessionLocal
from app.services.docflow_freigabe import DocflowFreigabe
from app.services.docflow_service import DocflowService

# Die Person, die ``tests/testgrenze.py`` anmeldet, und eine zweite.
ERSTE = "5f0c2a9e"
ZWEITE: dict[str, Any] = {"sub": "9a1d7c3b", "name": "m.hansen", "roles": ["admin"]}


def sichere_freigabe(mandant: str, doc_id: str, aktion: str = "post", antragsteller: str = ERSTE) -> str | None:
    """Fragt die noetige Freigabe an und erteilt sie als zweite Person. ``None``, wenn keine noetig ist."""
    with SessionLocal() as db:
        engine = DocflowFreigabe(db, mandant)
        kopf = DocflowService(db, mandant).fetch_header(doc_id)
        if not kopf or not engine.anforderung_fuer(kopf, aktion).zweitfreigabe:
            db.rollback()
            return None
        vorhanden = engine.gueltige(kopf, aktion)
        if vorhanden:
            db.rollback()
            return str(vorhanden["id"])
        anfrage = engine.beantrage(doc_id, aktion, antragsteller, "Test")
        if anfrage["status"] == "requested":
            engine.entscheide(doc_id, str(anfrage["id"]), ZWEITE, True, "Test")
        return str(anfrage["id"])
