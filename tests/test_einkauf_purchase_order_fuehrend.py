"""Fuehrende Einkaufsbestellung: Maske und Endpunkt sprechen dieselben Schluessel."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.core.screen_definitions import get_screen_definition
from app.services.procurement_service import bestellung_to_mask, position_to_mask
from app.api.v1.schemas.mask_entity_contracts import (
    EinkaufBestellungOut,
    purchase_order_position_aliases,
)

pytestmark = pytest.mark.unit

L3_KOPF = (
    "bestellfall",
    "ansprechpartner",
    "ladetermin",
    "ladetermin_ab",
    "kostenstelle",
    "kommission",
    "anfrage_nr",
    "angebot_nr",
    "skonto1_tage",
    "skonto1_prozent",
    "fremdwaehrung",
    "abverkauf_horizont",
    "mindestbestellmenge",
    "maximalbestellmenge",
    "opportunitaetskostensatz",
    "direktlieferung",
    "ueberschlag_lager",
    "neuer_artikel",
)

L3_POS = (
    "lieferanten_artnr",
    "gebinde_menge",
    "preis_einheit",
    "gewicht_kg",
    "kontrakt_nr",
    "lager",
    "lagerhalle",
    "lagerfach",
)


def test_purchase_order_sd_ist_object_page_mit_bestellfall() -> None:
    sd = get_screen_definition("einkauf/purchase-order")
    assert sd is not None
    assert sd["layout"]["floorplan"] == "objectPage"
    assert sd["layout"]["density"] == "compact"
    assert sd["layout"]["contextRail"] == "workflow"
    assert sd["layout"]["tableProfile"] == "inventory"
    tabs = {tab["key"]: tab for tab in sd["tabs"]}
    assert set(tabs) >= {"kopf", "positionen", "kette", "zahlung", "fall", "kommunikation"}
    kopf_keys = {field["key"] for field in tabs["kopf"]["fields"]}
    for key in L3_KOPF:
        assert key in kopf_keys or key in {field["key"] for tab in ("kette", "zahlung", "fall") for field in tabs[tab]["fields"]}
    fall = {field["key"] for field in tabs["fall"]["fields"]}
    assert "abverkauf_horizont" in fall
    assert "opportunitaetskostensatz" in fall
    assert "neuer_artikel" in fall
    kette = {field["key"] for field in tabs["kette"]["fields"]}
    assert "direktlieferung" in kette
    assert "ueberschlag_lager" in kette
    pos_cols = {col["key"] for col in tabs["positionen"]["tables"][0]["columns"]}
    for key in L3_POS:
        assert key in pos_cols
    bestellfall = next(field for field in tabs["kopf"]["fields"] if field["key"] == "bestellfall")
    assert {opt["value"] for opt in bestellfall["options"]} == {
        "bestand_abgleich",
        "direktlieferung",
        "innovation",
    }
    assert sd["processChain"] == {"chainId": "k3_einkauf", "stepKey": "bestellung"}
    action_keys = {action["key"] for action in sd["actions"]}
    assert {"edit", "speichern", "versenden"} <= action_keys


def test_einkauf_bestellung_out_deckt_maskenfelder() -> None:
    declared = set(EinkaufBestellungOut.model_fields)
    sd = get_screen_definition("einkauf/purchase-order")
    assert sd is not None
    for tab in sd["tabs"]:
        if tab.get("dataSourceKey") != "entity":
            continue
        for field in tab.get("fields") or []:
            assert field["key"] in declared, field["key"]


def test_position_alias_spricht_orm_und_l3() -> None:
    aliased = purchase_order_position_aliases(
        {
            "pos_nr": 1,
            "artikel_bezeichnung": "Weizen",
            "lagerort": "Silo-2",
            "netto_betrag": 80.0,
            "menge": 10,
            "menge_geliefert": 4,
        }
    )
    assert aliased["bezeichnung"] == "Weizen"
    assert aliased["lager"] == "Silo-2"
    assert aliased["betrag"] == 80.0
    assert aliased["menge_offen"] == 6.0


def test_bestellung_to_mask_setzt_bestellfall_und_ladetermin() -> None:
    pos = SimpleNamespace(
        id="p1", pos_nr=1, article_id=None, artikel_nr="A-1",
        artikel_bezeichnung="Soja", lieferanten_artnr="L-9", menge=2,
        menge_geliefert=0, menge_offen=2, einheit="t", einzelpreis=12.5,
        preis_einheit="t", netto_betrag=25.0, status="offen", lagerort="Silo-1",
        gebinde_menge=1, gebinde_einheit="BigBag", gebinde_schluessel=None,
        gewicht_kg=2000, kontrakt_nr="K-1", lagerhalle="H1", lagerfach="F2",
        mindestmenge=1, maximalmenge=20, lieferdatum=None, notiz=None,
    )
    bestellung = SimpleNamespace(
        id="b1", bestellnummer="EK-1", lieferant_id="l1", lieferant=SimpleNamespace(firmenname="Nord"),
        bestelldatum=None, lieferdatum_wunsch=None, lieferdatum_zugesagt=None,
        lieferdatum_ist=None, status="entwurf", versand_art="email",
        netto_summe=25, mwst_betrag=None, brutto_summe=25, waehrung="EUR",
        zahlungsziel_tage=14, skonto_prozent=2, skonto_frist_tage=7,
        unsere_referenz=None, ihre_referenz=None, kontrakt_id=None,
        freitext_kopf=None, freitext_fuss=None, notiz=None, niederlassung_id="NL1",
        bestellfall="direktlieferung", ansprechpartner="Mara", kreditor_konto="70001",
        lieferant_nr="L-12", kostenstelle="4000", kommission=None,
        ladetermin=None, ladetermin_ab=None, lade_datum=None, incoterms="DAP",
        lieferadresse="Hof Tor 2", zahlungsbedingung="skonto",
        skonto1_tage=8, skonto1_prozent=2, skonto2_tage=None, skonto2_prozent=None,
        netto_tage=30, fremdwaehrung=None, umrechnungsfaktor=None,
        anfrage_nr="AN-1", angebot_nr=None, auftrag_nr="VK-9",
        abverkauf_horizont="woechentlich", bedarfsmenge=None,
        mindestbestellmenge=1, maximalbestellmenge=40, artikelgruppe="Schrot",
        lagerplatz_opt=True, fracht_opt=True, opportunitaetskostensatz=1.5,
        palettenstellplatz_kosten=8, lagerkosten_satz=0.4,
        verkaufsbeleg_id="VK-9", kunden_id="K-1", direktlieferung=True,
        ueberschlag_lager=True, neuer_artikel=False, innovationshinweis=None,
        erstellt_von="jochen", positionen=[pos],
    )
    payload = bestellung_to_mask(bestellung)
    assert payload["bestellfall"] == "direktlieferung"
    assert payload["ansprechpartner"] == "Mara"
    assert payload["direktlieferung"] is True
    assert payload["ueberschlag_lager"] is True
    assert payload["positionen"][0]["lieferanten_artnr"] == "L-9"
    assert payload["positionen"][0]["lager"] == "Silo-1"
    assert position_to_mask(pos)["betrag"] == 25.0
