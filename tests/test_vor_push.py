"""Vertrag der Pruefkette vor dem Push (scripts/vor_push.py)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

WURZEL = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("vor_push", WURZEL / "scripts" / "vor_push.py")
vor_push = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vor_push)


@pytest.mark.parametrize("zeile", [
    "SKIPPED [1] tests/test_x.py:12: TEST_DATABASE_URL (frischer Pruefstand) nicht gesetzt",
    "SKIPPED [5] tests/test_y.py:82: Datenbank nicht erreichbar: Could not parse SQLAlchemy URL from given URL string",
    "SKIPPED [1] tests/test_z.py:9: Existing shared PostgreSQL required",
])
def test_ein_skip_ohne_datenbank_gilt_als_fehler(zeile):
    """19.11.2026: leeres TEST_DATABASE_URL liess DB-Tests still ueberspringen; 'gruen' war nicht geprueft."""
    assert vor_push.STILLER_SKIP.search(zeile)


@pytest.mark.parametrize("zeile", [
    "SKIPPED [1] tests/test_a.py:3: keine Bestandszeile als Vorlage vorhanden",
    "SKIPPED [1] tests/test_b.py:7: Endpoint /api/v1/waagen-vorlagen antwortet mit 404",
])
def test_ein_fachlicher_skip_bleibt_ein_skip(zeile):
    assert not vor_push.STILLER_SKIP.search(zeile)


def test_der_pruefstand_ist_nie_die_entwicklungsdatenbank(monkeypatch):
    monkeypatch.setenv("TEST_DATABASE_URL", "postgresql://u:p@127.0.0.1:5432/valeo_neuro_erp")
    with pytest.raises(SystemExit):
        vor_push._pruefstand_umgebung()


def test_beide_variablen_zeigen_auf_denselben_pruefstand(monkeypatch):
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_URL", "")
    url = vor_push._pruefstand_umgebung()
    import os

    assert url.endswith("/valeo_probe") and os.environ["DATABASE_URL"] == os.environ["TEST_DATABASE_URL"] == url


def test_die_register_aus_den_ci_befunden_sind_dabei():
    """Jeder Eintrag steht fuer eine CI-Runde, die schon einmal rot war."""
    namen = " ".join(name for name, _, _ in vor_push.REGISTER)
    for pflicht in ("Tabellenkatalog", "RLS-Inventar", "Pflichtstruktur", "Doc-Generatoren", "Improvement-Pipelines",
                    "Belegmasken-Versionen", "Maskenfamilien-Versionen", "Studio-Screen-Katalog"):
        assert pflicht in namen
    assert "tests/test_mask_endpoint_inventory.py" in vor_push.IMMER


def test_sperre_haelt_den_pruefstand_und_gibt_ihn_frei(tmp_path, monkeypatch):
    """24.11.2026: vor_push direkt aufgerufen baute den Pruefstand mitten in fremden Laeufen neu - jetzt gesperrt."""
    monkeypatch.setattr(vor_push, "SPERRE", tmp_path / "sperre.lock")
    monkeypatch.delenv("VALEO_PRUEFSTAND_SPERRE", raising=False)
    with vor_push._Sperre():
        assert vor_push.SPERRE.exists()
    assert not vor_push.SPERRE.exists()


def test_verwaiste_sperre_wird_uebernommen(tmp_path, monkeypatch):
    monkeypatch.setattr(vor_push, "SPERRE", tmp_path / "sperre.lock")
    monkeypatch.delenv("VALEO_PRUEFSTAND_SPERRE", raising=False)
    vor_push.SPERRE.write_text("999999999 anderswo")
    monkeypatch.setattr(vor_push, "_lebt", lambda pid: False)
    with vor_push._Sperre():
        assert vor_push.SPERRE.read_text().split()[0] != "999999999"


def test_vom_hook_gehaltene_sperre_wird_nicht_doppelt_genommen(tmp_path, monkeypatch):
    monkeypatch.setattr(vor_push, "SPERRE", tmp_path / "sperre.lock")
    monkeypatch.setenv("VALEO_PRUEFSTAND_SPERRE", "gehalten")
    vor_push.SPERRE.write_text("1 hook")
    with vor_push._Sperre():
        assert vor_push.SPERRE.read_text() == "1 hook"
    assert vor_push.SPERRE.exists()  # gehoert dem Hook
