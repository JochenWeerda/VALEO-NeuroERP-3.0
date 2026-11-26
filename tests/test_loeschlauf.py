"""Loeschlauf mit Vier-Augen-Freigabe (M7, Nutzerentscheid 26.11.2026) - gegen die echte DB."""
from __future__ import annotations

import uuid
from datetime import date

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.core.exceptions import ConflictError, PermissionDeniedError, ValidationFailedError
from app.services import loeschlauf

pytestmark = pytest.mark.integration

STICHTAG = date(2035, 6, 1)
FRIST = date(2034, 12, 31)  # Festsetzungsfrist mit dem Steuerberater geklaert, abgelaufen
ANNA = {"sub": "anna", "name": "Anna"}
BERND = {"sub": "bernd", "name": "Bernd"}
AGENT = {"sub": "codex", "agent_id": "codex", "raw": {"actor_type": "agent"}}


@pytest.fixture
def haus():
    t = f"ll-{uuid.uuid4().hex[:6]}"
    ids = {}
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": t})
        for schluessel, art, datum in (("auftrag", "sales_order", "2026-05-01"), ("angebot", "sales_offer", "2026-04-01"),
                                       ("ls_gebucht", "sales_delivery", "2026-03-01"), ("rechnung", "sales_invoice", "2026-03-01")):
            ids[schluessel] = str(uuid.uuid4())
            db.execute(text("INSERT INTO domain_docflow.document_headers (id, tenant_id, doc_type, doc_number, document_date) "
                            "VALUES (:id, :t, :art, :nr, :d)"), {"id": ids[schluessel], "t": t, "art": art, "nr": schluessel,
                                                                 "d": datum})
        db.execute(text("INSERT INTO domain_docflow.document_items (id, tenant_id, header_id, line_number, "
                        "article_number, quantity) VALUES (:id, :t, :h, 1, 'A-1', 1)"),
                   {"id": str(uuid.uuid4()), "t": t, "h": ids["auftrag"]})
        db.execute(text("INSERT INTO domain_docflow.document_postings (id, tenant_id, header_id, posting_type) "
                        "VALUES (:id, :t, :h, 'post')"), {"id": str(uuid.uuid4()), "t": t, "h": ids["ls_gebucht"]})
        db.commit()
    try:
        yield t, ids
    finally:
        with SessionLocal() as db:
            db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
            for sql in ("DELETE FROM domain_shared.loeschauftraege WHERE tenant_id = :t",
                        "DELETE FROM domain_docflow.document_postings WHERE tenant_id = :t",
                        "DELETE FROM domain_docflow.document_items WHERE tenant_id = :t",
                        "DELETE FROM domain_docflow.document_headers WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": t})
            db.commit()


def _koepfe(t: str) -> set[str]:
    with SessionLocal() as db:
        return {r[0] for r in db.execute(text("SELECT doc_number FROM domain_docflow.document_headers WHERE tenant_id = :t"),
                                         {"t": t})}


def test_vier_augen_lauf_loescht_nur_freigegebene_und_buchungsfreie_belege(haus):
    t, _ = haus
    with SessionLocal() as db:
        auftrag = loeschlauf.beantrage(db, t, "handelsbrief", ANNA, heute=STICHTAG, festsetzungsfrist_offen_bis=FRIST)
    with SessionLocal() as db, pytest.raises(ConflictError, match="Vier-Augen"):
        loeschlauf.entscheide(db, t, auftrag["id"], ANNA, erteilt=True)
    with SessionLocal() as db, pytest.raises(PermissionDeniedError, match="Agenten"):
        loeschlauf.entscheide(db, t, auftrag["id"], AGENT, erteilt=True)
    with SessionLocal() as db, pytest.raises(ConflictError, match="nur freigegebene"):
        loeschlauf.fuehre_aus(db, t, auftrag["id"], ANNA, heute=STICHTAG, festsetzungsfrist_offen_bis=FRIST)
    with SessionLocal() as db:
        loeschlauf.entscheide(db, t, auftrag["id"], BERND, erteilt=True, grund="Frist abgelaufen, Steuerberater bestaetigt")
    with SessionLocal() as db:
        nachweis = loeschlauf.fuehre_aus(db, t, auftrag["id"], ANNA, heute=STICHTAG, festsetzungsfrist_offen_bis=FRIST)

    assert auftrag["anzahl"] == 2
    assert nachweis["geloescht"] == 2
    assert _koepfe(t) == {"ls_gebucht", "rechnung"}


def test_lieferschein_mit_buchungsbezug_wird_uebersprungen(haus):
    t, _ = haus
    with SessionLocal() as db:
        auftrag = loeschlauf.beantrage(db, t, "lieferschein", ANNA, heute=STICHTAG, festsetzungsfrist_offen_bis=FRIST)
        loeschlauf.entscheide(db, t, auftrag["id"], BERND, erteilt=True)
        nachweis = loeschlauf.fuehre_aus(db, t, auftrag["id"], BERND, heute=STICHTAG, festsetzungsfrist_offen_bis=FRIST)

    assert nachweis["geloescht"] == 0
    assert nachweis["mit_buchungsbezug_uebersprungen"] == 1
    assert "ls_gebucht" in _koepfe(t)


def test_gesperrte_kategorien_und_fehlende_festsetzungsfrist_werden_abgewiesen(haus):
    t, _ = haus
    with SessionLocal() as db, pytest.raises(ValidationFailedError, match="nicht freigeschaltet"):
        loeschlauf.beantrage(db, t, "ar_invoice", ANNA, heute=STICHTAG, festsetzungsfrist_offen_bis=FRIST)
    with SessionLocal() as db, pytest.raises(ValidationFailedError, match="Festsetzungsfrist"):
        loeschlauf.beantrage(db, t, "handelsbrief", ANNA, heute=STICHTAG)


def test_abgelehnter_auftrag_loescht_nichts(haus):
    t, _ = haus
    with SessionLocal() as db:
        auftrag = loeschlauf.beantrage(db, t, "handelsbrief", ANNA, heute=STICHTAG, festsetzungsfrist_offen_bis=FRIST)
        loeschlauf.entscheide(db, t, auftrag["id"], BERND, erteilt=False, grund="Rechtsstreit offen")
    with SessionLocal() as db, pytest.raises(ConflictError):
        loeschlauf.fuehre_aus(db, t, auftrag["id"], BERND, heute=STICHTAG, festsetzungsfrist_offen_bis=FRIST)

    assert {"auftrag", "angebot"} <= _koepfe(t)
