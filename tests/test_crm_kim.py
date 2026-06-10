"""Unit-Tests für die reinen Mapping-Helfer des KIM-360°-Backends (crm_kim).

Die Endpoints selbst sind tolerante DB-Leser (separat per Smoke/curl geprüft);
hier wird die DB-freie Abbildung Backend->Frontend-Datenmodell getestet."""

import pytest

from app.api.v1.endpoints.crm_kim import (
    _customer_from_row,
    _direction,
    _fallback_summary,
    _log_from_row,
    Customer,
)

pytestmark = pytest.mark.unit


def test_direction_mapping():
    assert _direction("ein") == "INCOMING"
    assert _direction("eingehend") == "INCOMING"
    assert _direction("aus") == "OUTGOING"
    assert _direction(None) == "OUTGOING"


def test_customer_from_row_defaults_und_city():
    c = _customer_from_row({"kunden_nr": "GAP1", "name1": "Hof Test", "plz": "26721", "ort": "Emden"})
    assert c.id == "GAP1" and c.debtorNo == "GAP1"
    assert c.city == "26721 Emden"
    assert c.creditLimit == 0 and c.revenueStatus == "B" and c.abcStatus == "B"
    assert c.alertMessages == []


def test_customer_from_row_satellit_und_alerts_json():
    c = _customer_from_row({
        "kunden_nr": "GAP2", "name1": "Agrar GmbH", "plz": "26", "ort": "X",
        "kv_limit": 50000, "sales_rep_vb": "AO", "dispatcher_disp": "D1",
        "abc_status": "A", "revenue_status": "A", "chef_anweisung": "Nur Vorkasse",
        "alert_messages": '["gesperrt"]',  # JSON-String wird geparst
    })
    assert c.creditLimit == 50000 and c.salesRepresentative == "AO"
    assert c.abcStatus == "A" and c.chefAnweisung == "Nur Vorkasse"
    assert c.alertMessages == ["gesperrt"]


def test_log_from_row_fuehrt_art_und_kurzinfo_separat():
    log = _log_from_row({"id": "x1", "richtung": "ein", "art": "telefon",
                         "kurzinfo": "Rueckruf", "erledigt": False, "bediener": "JW",
                         "wiedervorlage": None, "weiterleitung_an": None, "verweis": None,
                         "created_at": "2026-06-07"}, "GAP1")
    assert log.direction == "INCOMING"
    assert log.art == "telefon"
    assert log.artKurzinfo == "Rueckruf"
    assert log.operator == "JW" and log.completed is False


def test_fallback_summary_risiko_bei_limitueberschreitung():
    cust = Customer(id="G", name="Hof", debtorNo="G", creditLimit=10000,
                    revenueStatus="A", abcStatus="A", alertMessages=[])
    s = _fallback_summary(cust, outstanding=12000, log_count=3, doc_count=0)
    assert s.engine == "fallback"
    assert s.healthScore <= 60  # Auslastung > 90 % -> Risiko/Beobachten
    assert any("Saldo" in r for r in s.risks)


def test_fallback_summary_gesperrt_setzt_risiko():
    cust = Customer(id="G", name="Hof", debtorNo="G", creditLimit=0,
                    revenueStatus="B", abcStatus="B", alertMessages=["Konto gesperrt"])
    s = _fallback_summary(cust, outstanding=0, log_count=0, doc_count=1)
    assert s.healthScore == 35
    assert any("gesperrt" in r.lower() for r in s.risks)
