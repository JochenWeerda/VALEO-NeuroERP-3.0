"""Mandantenpflicht beim Speichern von Belegen (TENANT-DOC-001 Punkt 2).

Ein Beleg ohne Mandant gehoert niemandem: seit den Mandantenslices vom 14.10.2026 findet ihn kein Lese- oder
Schreibweg wieder. Der einzige Schreibweg der Anwendung in ``documents`` nimmt solche Belege nicht mehr an. Die sieben
mandantenlosen Testbelege der gewachsenen Datenbank sind auf Freigabe des Nutzers am 14.10.2026 nach Sicherung
geloescht worden (``docs/quality-assurance/altbelege-mandantenpflicht-20261014.md``).

Geprueft gegen die echte (frische) Datenbank.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.documents.repository import BelegOhneMandant, DocumentRepository


def _vorhanden(nummer: str) -> bool:
    with SessionLocal() as db:
        return db.execute(text("SELECT 1 FROM documents WHERE doc_number = :n"), {"n": nummer}).first() is not None


@pytest.mark.parametrize("daten", [{}, {"tenantId": ""}, {"tenantId": "   "}, {"tenantId": None}, {"tenant_id": "t1"}])
def test_speichern_ohne_mandant_wird_abgewiesen(daten):
    nummer = f"MP-{uuid.uuid4().hex[:10]}"
    with SessionLocal() as db, pytest.raises(BelegOhneMandant):
        DocumentRepository(db).save_document("sales_invoice", nummer, dict(daten))
    assert not _vorhanden(nummer)


def test_aendern_entfernt_den_mandanten_nicht():
    nummer = f"MP-{uuid.uuid4().hex[:10]}"
    with SessionLocal() as db:
        repo = DocumentRepository(db)
        repo.save_document("sales_invoice", nummer, {"tenantId": "t-pflicht", "status": "OFFEN"})
        with pytest.raises(BelegOhneMandant):
            repo.save_document("sales_invoice", nummer, {"status": "BEZAHLT"})
        gespeichert = db.execute(text("SELECT data FROM documents WHERE doc_number = :n"), {"n": nummer}).scalar()
        db.execute(text("DELETE FROM documents WHERE doc_number = :n"), {"n": nummer})
        db.commit()
    assert gespeichert["tenantId"] == "t-pflicht" and gespeichert["status"] == "OFFEN"
