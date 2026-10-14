"""Belegmasken nur fuer den freigegebenen Testmandanten (BELEG-020, Teil 2).

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import importlib.util
import pathlib
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.belegvertrag import BELEGARTEN
from app.core.database import SessionLocal, engine
from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
from app.core.screen_definitions_beleg import build_beleg_screen_definition, screen_id
from app.services import studio_draft_store

WURZEL = pathlib.Path(__file__).resolve().parent.parent


def _skript():
    spec = importlib.util.spec_from_file_location("belegmasken_veroeffentlichen", WURZEL / "scripts/belegmasken_veroeffentlichen.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.fixture
def mandant(monkeypatch):
    kennung = f"bm-{uuid.uuid4().hex[:8]}"
    studio_draft_store.use_sql_studio_drafts()
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": kennung})
        db.commit()
    connection = engine.connect()
    transaction = connection.begin()
    monkeypatch.setattr(studio_draft_store, "_sql_session", lambda: Session(bind=connection, join_transaction_mode="create_savepoint"))
    yield kennung
    transaction.rollback()
    connection.close()
    with SessionLocal() as db:
        db.execute(text("DELETE FROM domain_shared.screen_definition_drafts WHERE tenant_id = :t"), {"t": kennung})
        db.execute(text("DELETE FROM domain_shared.tenants WHERE id = :t"), {"t": kennung})
        db.commit()


def test_die_belegmasken_stehen_nicht_in_der_registry_aller_mandanten():
    assert not [k for k in SCREEN_DEFINITION_BUILDERS if k.startswith("beleg/")]
    assert get_screen_definition("beleg/sales-invoice") is None
    assert get_screen_definition("beleg/sales-invoice", tenant_id=f"nie-{uuid.uuid4().hex[:6]}") is None


def test_nur_ein_freigegebener_mandant_wird_angenommen(mandant):
    skript = _skript()
    assert skript.ERLAUBTE_MANDANTEN == {"00000000-0000-0000-0000-000000000051"}
    with pytest.raises(PermissionError):
        skript.veroeffentliche(mandant)
    assert studio_draft_store.list_published_definitions(mandant) == []


def test_veroeffentlicht_sieht_der_mandant_alle_neun_varianten_und_kein_anderer(mandant):
    skript = _skript()
    bericht = skript.veroeffentliche(mandant, erlaubte=frozenset({mandant}))
    assert bericht == {screen_id(art): "veroeffentlicht" for art in BELEGARTEN}
    for art in BELEGARTEN:
        kennung = screen_id(art)
        geliefert = get_screen_definition(kennung, tenant_id=mandant)
        assert geliefert is not None and geliefert["title"] == BELEGARTEN[art].bezeichnung
        erzeugt = build_beleg_screen_definition(art)
        assert [t["key"] for t in geliefert["tabs"]] == [t["key"] for t in erzeugt["tabs"]]
        assert [a["key"] for a in geliefert["actions"]] == [a["key"] for a in erzeugt["actions"]]
        assert get_screen_definition(kennung, tenant_id="anderer-mandant") is None
        assert get_screen_definition(kennung) is None
    # Zwei Kennungen am Entwurf: bearbeitet von der einen, veroeffentlicht von der anderen.
    entwuerfe = studio_draft_store.list_drafts(mandant)
    assert len(entwuerfe) == 9 and {e["status"] for e in entwuerfe} == {"published_temp"}
    assert {(e["created_by"], e["updated_by"]) for e in entwuerfe} == {("belegmasken", "belegmasken-zweitfreigabe")}


def test_ein_zweiter_lauf_aendert_nichts_und_eine_geaenderte_definition_wird_erneuert(mandant, monkeypatch):
    skript = _skript()
    erlaubt = frozenset({mandant})
    skript.veroeffentliche(mandant, erlaubte=erlaubt)
    assert set(skript.veroeffentliche(mandant, erlaubte=erlaubt).values()) == {"aktuell"}

    alle = skript.alle_beleg_screen_definitions()
    alle["beleg/sales-invoice"]["subtitle"] = "geändert"
    monkeypatch.setattr(skript, "alle_beleg_screen_definitions", lambda: alle)
    bericht = skript.veroeffentliche(mandant, erlaubte=erlaubt)
    assert bericht["beleg/sales-invoice"] == "erneuert"
    assert {v for k, v in bericht.items() if k != "beleg/sales-invoice"} == {"aktuell"}
    assert get_screen_definition("beleg/sales-invoice", tenant_id=mandant)["subtitle"] == "geändert"
    assert len(studio_draft_store.list_drafts(mandant)) == 9
