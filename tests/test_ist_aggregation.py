"""Unit-Tests für den reinen Artikel→Produktgruppe-Klassifikator der
Ist-Belegaggregation (app/services/ist_aggregation_service.py)."""

import pytest

from app.services.ist_aggregation_service import (
    PRODUKTGRUPPEN_KEYS,
    klassifiziere_artikel,
)

pytestmark = pytest.mark.unit


def test_pflanzenschutz_per_flag():
    assert klassifiziere_artikel("Irgendwas", pflanzenschutzmittel=True) == "pflanzenschutz"


def test_pflanzenschutz_per_warengruppe_und_name():
    assert klassifiziere_artikel("Glyphosat RoundUp Ultra", "Pflanzenschutz") == "pflanzenschutz"
    assert klassifiziere_artikel("Fungizid XY") == "pflanzenschutz"


def test_saatgut_marktfrucht_vs_grundfutter():
    assert klassifiziere_artikel("Winterweizen Saatgut Ponticus", "Saatgut") == "saatgut_marktfrucht"
    assert klassifiziere_artikel("Rapssaatgut Defender", "Saatgut") == "saatgut_marktfrucht"
    # Mais-/Gras-Saatgut zählt zum Grundfutterbau (Milchvieh), nicht Marktfrucht
    assert klassifiziere_artikel("Mais Saatgut Maximus", "Saatgut") == "grundfutterbau"
    assert klassifiziere_artikel("Weidelgras Nachsaat", "Saatgut") == "grundfutterbau"


def test_duenger_marktfrucht_und_grundfutter():
    assert klassifiziere_artikel("NPK-Dünger 20-10-10", "Duenger") == "duenger_marktfrucht"
    assert klassifiziere_artikel("Kalkstickstoff 46", "Duenger") == "duenger_marktfrucht"
    assert klassifiziere_artikel("Stallmist Kompost", "Organisch") == "duenger_marktfrucht"
    # Grünland-Dünger → Grundfutterbau
    assert klassifiziere_artikel("Grünland-Dünger NPK", "Duenger") == "grundfutterbau"


def test_biostimulanzien():
    assert klassifiziere_artikel("Methylobacterium", "Biostimulanzien") == "duenger_marktfrucht"


def test_futtermittel_feindifferenzierung():
    assert klassifiziere_artikel("Weizen Tierfutter Weizenschrot Klasse A", "Futtermittel") == "kraftfutter"
    assert klassifiziere_artikel("Mineralfutter 9000 mit Puffer", "Futtermittel") == "mineral_spezial"
    assert klassifiziere_artikel("Kälber-Milchaustauscher Premium", "Futtermittel") == "kaelber"
    assert klassifiziere_artikel("Klauenpflege Hygiene Dippmittel") == "stallbedarf_hygiene"
    assert klassifiziere_artikel("Rationsservice Beratung") == "beratung_analyse"


def test_getreide_ankauf_ist_kein_betriebsmittel():
    assert klassifiziere_artikel("Gerste Braugerste", "Getreide") is None


def test_leerer_artikel_ist_none():
    assert klassifiziere_artikel() is None
    assert klassifiziere_artikel("", "") is None


def test_alle_ergebnisse_sind_gueltige_keys():
    proben = [
        ("Glyphosat", "Pflanzenschutz", False),
        ("Winterweizen Saatgut", "Saatgut", False),
        ("Mais Saatgut", "Saatgut", False),
        ("NPK-Dünger", "Duenger", False),
        ("Weizenschrot", "Futtermittel", False),
        ("Mineralfutter", "Futtermittel", False),
    ]
    for name, wg, psm in proben:
        key = klassifiziere_artikel(name, wg, pflanzenschutzmittel=psm)
        assert key in PRODUKTGRUPPEN_KEYS
