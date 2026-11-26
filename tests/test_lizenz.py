"""Lizenzpruefung auf dem Modulregister (M7, 26.11.2026) - ohne Datenbank."""
from __future__ import annotations

import importlib.util
import json
from datetime import date
from pathlib import Path

import pytest

from app.core import lizenz

pytestmark = pytest.mark.unit

_PFAD = Path(__file__).resolve().parents[1] / "scripts" / "lizenz_ausstellen.py"
_spec = importlib.util.spec_from_file_location("lizenz_ausstellen", _PFAD)
werkzeug = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(werkzeug)


@pytest.fixture
def schluessel(tmp_path):
    oeffentlich = werkzeug.schluesselpaar(tmp_path / "test")
    return oeffentlich, (tmp_path / "test.privat").read_text().strip()


def _dokument(privat, **mehr):
    werte = {"kunde": "Muster eG", "module": ["core", "agrar"], "gueltig_bis": date(2027, 12, 31)} | mehr
    return werkzeug.ausstellen(privat, **werte)


def test_gueltige_lizenz_wird_angenommen(schluessel):
    oeffentlich, privat = schluessel
    ergebnis = lizenz.pruefe(_dokument(privat), oeffentlich, heute=date(2026, 11, 26))
    assert ergebnis.module == frozenset({"core", "agrar"})
    assert ergebnis.erlaubt("agrar", None) is True
    assert ergebnis.erlaubt("feeding_advisory", None) is False


def test_manipulierte_lizenz_wird_abgewiesen(schluessel):
    oeffentlich, privat = schluessel
    dokument = _dokument(privat)
    dokument["lizenz"]["module"].append("feeding_advisory")
    with pytest.raises(lizenz.LizenzUngueltig, match="Signatur"):
        lizenz.pruefe(dokument, oeffentlich, heute=date(2026, 11, 26))


def test_abgelaufene_lizenz_wird_abgewiesen(schluessel):
    oeffentlich, privat = schluessel
    with pytest.raises(lizenz.LizenzUngueltig, match="abgelaufen"):
        lizenz.pruefe(_dokument(privat, gueltig_bis=date(2026, 1, 1)), oeffentlich, heute=date(2026, 11, 26))


def test_fremder_schluessel_wird_abgewiesen(schluessel, tmp_path):
    _oeffentlich, privat = schluessel
    fremd = werkzeug.schluesselpaar(tmp_path / "fremd")
    with pytest.raises(lizenz.LizenzUngueltig):
        lizenz.pruefe(_dokument(privat), fremd, heute=date(2026, 11, 26))


def test_mandantenbindung(schluessel):
    oeffentlich, privat = schluessel
    ergebnis = lizenz.pruefe(_dokument(privat, mandanten=["haus-a"]), oeffentlich, heute=date(2026, 11, 26))
    assert ergebnis.erlaubt("agrar", "haus-a") is True
    assert ergebnis.erlaubt("agrar", "haus-b") is False
    assert ergebnis.erlaubt("core", "haus-b") is True


def test_registry_ohne_lizenzpflicht_unveraendert(monkeypatch):
    from app.core.module_registry import registry

    monkeypatch.delenv("VALEO_UMGEBUNG", raising=False)
    monkeypatch.setattr("app.core.module_registry.settings.INSTALLED_MODULES", ["core", "agrar"])
    assert registry.is_enabled("agrar") is True


def test_registry_in_produktion_nur_mit_lizenz(monkeypatch, schluessel, tmp_path):
    from app.core.module_registry import registry

    oeffentlich, privat = schluessel
    monkeypatch.setattr("app.core.module_registry.settings.INSTALLED_MODULES", ["core", "agrar", "feeding_advisory"])
    monkeypatch.setenv("VALEO_UMGEBUNG", "production")
    monkeypatch.delenv("VALEO_LIZENZ_DATEI", raising=False)
    ohne = (registry.is_enabled("core"), registry.is_enabled("agrar"))

    datei = tmp_path / "lizenz.json"
    datei.write_text(json.dumps(_dokument(privat, gueltig_bis=date(2099, 12, 31))), encoding="utf-8")
    monkeypatch.setenv("VALEO_LIZENZ_DATEI", str(datei))
    monkeypatch.setenv("VALEO_LIZENZ_OEFFENTLICHER_SCHLUESSEL", oeffentlich)
    mit = (registry.is_enabled("agrar"), registry.is_enabled("feeding_advisory"))

    assert ohne == (True, False)  # ohne Lizenz nur das Kernmodul
    assert mit == (True, False)   # lizenziert: core, agrar - nicht feeding_advisory
