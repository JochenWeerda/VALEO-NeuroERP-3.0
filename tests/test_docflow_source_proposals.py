"""FSX-SOURCE-PROPOSALS — Projektion der Kontrakt- und Fremdlagervorschlaege.

Geprueft wird ``build_proposals``: die deterministische, datenbankfreie Mitte des
Dienstes. Dort sitzt alles, was fachlich schiefgehen kann — Mengenaufteilung,
Einheiten, Kontraktseite, Eigentumsfrage und die Abrechnungsart.

Der Rahmen (Partneraufloesung, SQL) braucht eine Datenbank und ist hier bewusst
nicht abgebildet; er waere ohne echte Daten ohnehin nur nachgezeichnet.

Uebernommen von Codex (Pause), deren Slice-Abnahme Tests verlangt.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.services.docflow_source_proposals import (
    SourceProposalRequest,
    build_proposals,
    unit_factor,
)

pytestmark = pytest.mark.unit

TENANT = "t1"
PARTY = "p1"
ARTICLE = "a-weizen"


def _request(**overrides) -> SourceProposalRequest:
    payload = {
        "party_id": PARTY,
        "direction": "outgoing",
        "document_date": date(2026, 9, 15),
        "lines": [
            {
                "line_id": "L1",
                "article_id": ARTICLE,
                "article_number": "10001",
                "quantity": "100",
                "unit": "t",
            }
        ],
    }
    payload.update(overrides)
    return SourceProposalRequest.model_validate(payload)


def _contract(source_id: str, quantity: str, **overrides) -> dict:
    item = {
        "kind": "contract",
        "tenant_id": TENANT,
        "party_id": PARTY,
        "article_id": ARTICLE,
        "source_id": source_id,
        "reference": f"K-{source_id}",
        "contract_type": "VERKAUF",
        "status": "OFFEN",
        "unit": "t",
        "quantity": Decimal(quantity),
        "valid_from": date(2026, 1, 1),
        "valid_to": date(2026, 12, 31),
        "bio": False,
    }
    item.update(overrides)
    return item


def _stock(source_id: str, quantity: str, **overrides) -> dict:
    item = {
        "kind": "foreign_stock",
        "tenant_id": TENANT,
        "party_id": PARTY,
        "article_id": ARTICLE,
        "source_id": source_id,
        "reference": f"E-{source_id}",
        "unit": "t",
        "quantity": Decimal(quantity),
        "status": "eingelagert",
        "warehouse_id": "L1",
        "charge": "CH-1",
        "storage_type": "fremdware",
    }
    item.update(overrides)
    return item


def _group(result: dict, kind: str, line: int = 0) -> dict:
    return next(g for g in result["lines"][line]["groups"] if g["kind"] == kind)


# -- Mengenaufteilung ----------------------------------------------------------


def test_teilmengen_aus_mehreren_kontrakten() -> None:
    """Der Split ueber mehrere Quellen ist der Kern der Anforderung."""
    result = build_proposals(_request(), [_contract("c1", "60"), _contract("c2", "80")], TENANT)
    group = _group(result, "contract")

    assert [p["source_id"] for p in group["proposals"]] == ["c1", "c2"]
    assert [p["quantity"] for p in group["proposals"]] == ["60", "40"]
    assert group["uncovered_quantity"] == "0"


def test_restmenge_wird_als_ungedeckt_ausgewiesen() -> None:
    """Was nicht gedeckt ist, wird benannt — nicht stillschweigend weggelassen."""
    result = build_proposals(_request(), [_contract("c1", "30")], TENANT)
    group = _group(result, "contract")

    assert group["proposals"][0]["quantity"] == "30"
    assert group["uncovered_quantity"] == "70"


def test_dieselbe_quelle_wird_ueber_zwei_positionen_nicht_doppelt_vergeben() -> None:
    """Das Budget ist die Restmenge, nicht eine Zahl je Position.

    Ohne geteiltes Budget bekaeme jede Position die volle Restmenge angeboten —
    und zwei Positionen wuerden zusammen mehr abrufen, als der Kontrakt hergibt.
    """
    request = _request(
        lines=[
            {"line_id": "L1", "article_id": ARTICLE, "quantity": "60", "unit": "t"},
            {"line_id": "L2", "article_id": ARTICLE, "quantity": "60", "unit": "t"},
        ]
    )
    result = build_proposals(request, [_contract("c1", "100")], TENANT)

    erste = _group(result, "contract", 0)
    zweite = _group(result, "contract", 1)

    assert erste["proposals"][0]["quantity"] == "60"
    assert zweite["proposals"][0]["quantity"] == "40"
    assert zweite["uncovered_quantity"] == "20"

    vergeben = sum(Decimal(p["quantity"]) for g in (erste, zweite) for p in g["proposals"])
    assert vergeben == Decimal(100), f"Ueberbuchung: {vergeben} aus einem 100-t-Kontrakt"


# -- Einheiten -----------------------------------------------------------------


def test_einheitenumrechnung_tonne_zu_kilogramm() -> None:
    request = _request(lines=[{"line_id": "L1", "article_id": ARTICLE, "quantity": "5000", "unit": "kg"}])
    result = build_proposals(request, [_contract("c1", "10")], TENANT)

    proposal = _group(result, "contract")["proposals"][0]
    assert proposal["quantity"] == "5000"
    assert proposal["unit"] == "kg"
    # 10 t Restmenge sind 10000 kg — so wird sie auch ausgewiesen.
    assert proposal["recorded_remaining"] == "10000"


def test_unbekannte_einheit_wird_uebersprungen_statt_geraten() -> None:
    result = build_proposals(_request(), [_contract("c1", "100", unit="st")], TENANT)
    group = _group(result, "contract")

    assert group["proposals"] == []
    assert group["uncovered_quantity"] == "100"


def test_unit_factor_kennt_nur_belegte_umrechnungen() -> None:
    assert unit_factor("t", "kg") == Decimal(1000)
    assert unit_factor("kg", "t") == Decimal("0.001")
    assert unit_factor("Tonnen", "t") == Decimal(1)
    # Stueck auf Masse ist keine Umrechnung, sondern eine Annahme ueber das Gewicht.
    assert unit_factor("st", "kg") is None


# -- Kontraktseite und Zeitraum ------------------------------------------------


def test_verkaufskontrakt_nur_bei_ausgehendem_beleg() -> None:
    ausgehend = build_proposals(_request(direction="outgoing"), [_contract("c1", "100")], TENANT)
    assert _group(ausgehend, "contract")["proposals"]

    eingehend = build_proposals(_request(direction="incoming"), [_contract("c1", "100")], TENANT)
    assert _group(eingehend, "contract")["proposals"] == []


def test_einkaufskontrakt_nur_bei_eingehendem_beleg() -> None:
    einkauf = _contract("c1", "100", contract_type="EINKAUF")
    eingehend = build_proposals(_request(direction="incoming"), [einkauf], TENANT)
    assert _group(eingehend, "contract")["proposals"]

    ausgehend = build_proposals(_request(direction="outgoing"), [einkauf], TENANT)
    assert _group(ausgehend, "contract")["proposals"] == []


def test_kontrakt_ausserhalb_des_zeitraums_faellt_weg() -> None:
    abgelaufen = _contract("c1", "100", valid_to=date(2026, 8, 31))
    kuenftig = _contract("c2", "100", valid_from=date(2026, 10, 1))
    result = build_proposals(_request(), [abgelaufen, kuenftig], TENANT)

    assert _group(result, "contract")["proposals"] == []


def test_fremder_mandant_und_fremder_partner_werden_nicht_vorgeschlagen() -> None:
    fremd_mandant = _contract("c1", "100", tenant_id="t2")
    fremder_partner = _contract("c2", "100", party_id="p2")
    result = build_proposals(_request(), [fremd_mandant, fremder_partner], TENANT)

    assert _group(result, "contract")["proposals"] == []


# -- Fremdlager und Eigentum ---------------------------------------------------


def test_fremdlager_nur_bei_auslagerung() -> None:
    """Eine Einlagerung ist eine Verwahrung, keine Entnahme."""
    ausgehend = build_proposals(_request(direction="outgoing"), [_stock("s1", "50")], TENANT)
    assert _group(ausgehend, "foreign_stock")["proposals"]

    eingehend = build_proposals(_request(direction="incoming"), [_stock("s1", "50")], TENANT)
    assert all(g["kind"] != "foreign_stock" for g in eingehend["lines"][0]["groups"])


def test_kommissions_und_poolware_gilt_nicht_als_kundeneigentum() -> None:
    """Der wichtigste Filter: nur echte Fremdware gehoert dem Kunden.

    Waere er offen, wuerde Ware zur Auslagerung vorgeschlagen, die dem Haendler
    gehoert — und die Abrechnungsart „nur Leistungen" waere schlicht falsch.
    """
    kommission = _stock("s1", "50", storage_type="kommission")
    result = build_proposals(_request(), [kommission], TENANT)

    assert _group(result, "foreign_stock")["proposals"] == []


def test_fremdlager_wird_nach_lagerort_und_charge_gefiltert() -> None:
    anderes_lager = _stock("s1", "50", warehouse_id="L9")
    request = _request(warehouse_id="L1")
    assert _group(build_proposals(request, [anderes_lager], TENANT), "foreign_stock")["proposals"] == []

    andere_charge = _stock("s2", "50", charge="CH-9")
    request = _request(lines=[{"line_id": "L1", "article_id": ARTICLE, "quantity": "10", "unit": "t", "charge": "CH-1"}])
    assert _group(build_proposals(request, [andere_charge], TENANT), "foreign_stock")["proposals"] == []


def test_kundeneigene_ware_wird_nicht_nochmals_verkauft() -> None:
    """Die Abrechnungsart trennt Warenverkauf von reiner Dienstleistung."""
    result = build_proposals(_request(), [_contract("c1", "50"), _stock("s1", "50")], TENANT)

    assert _group(result, "contract")["proposals"][0]["billing"] == "goods"
    stock_proposal = _group(result, "foreign_stock")["proposals"][0]
    assert stock_proposal["billing"] == "services_only"
    # Und der Eigentuemer wird benannt, nicht nur der Bestand.
    assert stock_proposal["owner_id"] == PARTY


def test_kontrakt_und_fremdlager_bleiben_getrennte_gruppen() -> None:
    """Getrennt, damit niemand die Mengen addiert.

    Ein Kontraktabruf und ein physischer Bestand sind zwei verschiedene Dinge —
    dieselbe Tonne kann in beiden auftauchen.
    """
    result = build_proposals(_request(), [_contract("c1", "100"), _stock("s1", "100")], TENANT)
    kinds = [g["kind"] for g in result["lines"][0]["groups"]]

    assert kinds == ["contract", "foreign_stock"]
    assert _group(result, "contract")["proposals"][0]["quantity"] == "100"
    assert _group(result, "foreign_stock")["proposals"][0]["quantity"] == "100"


# -- Bevorzugung und Ehrlichkeit ----------------------------------------------


def test_genannter_kontrakt_wird_bevorzugt() -> None:
    request = _request(
        lines=[{"line_id": "L1", "article_id": ARTICLE, "quantity": "10", "unit": "t", "contract_reference": "K-c2"}]
    )
    result = build_proposals(request, [_contract("c1", "100"), _contract("c2", "100")], TENANT)

    assert _group(result, "contract")["proposals"][0]["source_id"] == "c2"


def test_vorschlag_reserviert_nichts_und_sagt_das_auch() -> None:
    """Ein Vorschlag ist eine Auskunft, keine Zusage."""
    result = build_proposals(_request(), [_contract("c1", "100")], TENANT)

    assert result["read_only"] is True
    assert result["reservation_checked"] is False
    assert "keine Reservierung" in result["notice"]
    # Die angebotene Menge stammt aus gebuchter Restmenge, und das steht dabei.
    assert "erneut pruefen" in result["notice"]


def test_jeder_vorschlag_nennt_quelle_menge_und_begruendung() -> None:
    result = build_proposals(_request(), [_contract("c1", "100"), _stock("s1", "100")], TENANT)

    for kind in ("contract", "foreign_stock"):
        proposal = _group(result, kind)["proposals"][0]
        assert proposal["reference"], "Quelle ohne Referenz ist nicht nachvollziehbar"
        assert Decimal(proposal["quantity"]) > 0
        assert proposal["reason"], "Ein Vorschlag ohne Begruendung ist eine Behauptung"
