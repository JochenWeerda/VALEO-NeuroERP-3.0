"""Spiegelbetrieb: Preise aus L3 (M6, 26.11.2026) - gegen die echte DB."""
from __future__ import annotations

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from test_spiegel_uebernahme import MAPPING, _artikel, _kunde, _lauf, mandant  # noqa: F401 - Fixture

pytestmark = pytest.mark.integration

MAPPING.update({"PREISTABNR": "preistabelle", "BEZEICHNUNG": "bezeichnung", "PREIS": "preis", "PREISJE": "preis_je",
                "ABMENGE": "ab_menge", "DATUMVON": "gueltig_von", "DATUMBIS": "gueltig_bis"})


def _tabelle(nr: str, name: str) -> dict:
    return {"TYP": "preisliste", "QUELLE": nr, "PREISTABNR": nr, "BEZEICHNUNG": name}


def _apreis(art: str, tab: str, preis: str, je: str = "1", ab: str = "", von: str = "01.01.2026") -> dict:
    return {"TYP": "artikelpreis", "QUELLE": f"{art}|{tab}|{von}|{ab}", "ARTNR": art, "PREISTABNR": tab,
            "PREIS": preis, "PREISJE": je, "ABMENGE": ab, "DATUMVON": von}


def _kpreis(kd: str, art: str, preis: str, je: str = "100") -> dict:
    return {"TYP": "kundenpreis", "QUELLE": f"{kd}|{art}", "KUNDENNR": kd, "ARTNR": art, "PREIS": preis,
            "PREISJE": je, "DATUMVON": "2026-01-01"}


@pytest.fixture
def mit_preisen(mandant):  # noqa: F811
    yield mandant
    with SessionLocal() as db:
        for sql in ("DELETE FROM domain_crm.business_partner_price_agreements WHERE tenant_id = :t",
                    "DELETE FROM domain_pricing.price_list_items WHERE tenant_id = :t",
                    "DELETE FROM domain_pricing.price_lists WHERE tenant_id = :t"):
            db.execute(text(sql), {"t": mandant})
        db.commit()


def test_preisbezug_wird_verlustfrei_in_den_einzelpreis_umgerechnet(mit_preisen):
    t = mit_preisen
    ergebnis = _lauf(t, "pr-1", [
        _artikel("220050", "Diesel"), _tabelle("0", "Groothusen"),
        _apreis("220050", "0", "168,79", je="100"),                 # Diesel-Golden-Master: je 100 l
        _apreis("220050", "0", "160.00", je="100", ab="5000"),      # Staffel ab 5000
        _apreis("220050", "0", "18.37", je="1000", von="01.02.2026"),  # nicht verlustfrei -> Fehler
    ])
    with SessionLocal() as db:
        zeilen = [tuple(r) for r in db.execute(text(
            "SELECT unit_price::text, min_quantity::text FROM domain_pricing.price_list_items WHERE tenant_id = :t "
            "ORDER BY min_quantity"), {"t": t})]

    assert (ergebnis["neu"], ergebnis["fehler"]) == (4, 1)
    assert zeilen == [("1.6879", "0.0000"), ("1.6000", "5000.0000")]  # ohne Staffel: Mindestmenge 0


def test_wiederholung_unveraendert_und_preisaenderung_mit_differenz(mit_preisen):
    t = mit_preisen
    basis = [_artikel("220050", "Diesel"), _tabelle("0", "Groothusen")]
    _lauf(t, "pr-1", basis + [_apreis("220050", "0", "168.79", je="100")])
    zweiter = _lauf(t, "pr-2", basis + [_apreis("220050", "0", "168.79", je="100")])
    dritter = _lauf(t, "pr-3", basis + [_apreis("220050", "0", "170.00", je="100")])

    assert zweiter["unveraendert"] == 3
    assert dritter["geaendert"] == 1


def test_kundenpreis_am_partner_mit_eigenem_preisbezug(mit_preisen):
    t = mit_preisen
    ergebnis = _lauf(t, "kp-1", [_artikel("151704", "ZINTAN"), _kunde("10001", "Hof Janssen"),
                                 _kpreis("10001", "151704", "414.50", je="1"), _kpreis("19999", "151704", "1")])
    with SessionLocal() as db:
        zeile = db.execute(text("SELECT article_number, price_net::text, price_unit, source_type FROM "
                                "domain_crm.business_partner_price_agreements WHERE tenant_id = :t"), {"t": t}).one()

    assert (ergebnis["neu"], ergebnis["fehler"]) == (3, 1)  # unbekannter Kunde -> Fehlerzeile
    assert tuple(zeile) == ("151704", "414.5000", "1", "import")


def test_artikelpreis_ohne_uebernommene_preistabelle_wird_fehlerzeile(mit_preisen):
    ergebnis = _lauf(mit_preisen, "pr-1", [_artikel("220050", "Diesel"), _apreis("220050", "9", "1.00")])

    assert ergebnis["fehler"] == 1

