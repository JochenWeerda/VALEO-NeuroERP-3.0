"""MERIDIAN-BELEG-SYSTEMWEIT: Beleg-Look-and-Feel fuer alle nativen Belegmasken.

Drei Zusagen werden hier festgehalten:

1. Jede ObjectPage/Transaction laeuft als eine Seite mit Abschnittsankern,
   solange der Builder nicht ausdruecklich ``tabs`` waehlt.
2. Jede dieser Masken zeigt ihre Nummer (sonst ihren Namen) als Identitaet.
3. Kein Kopf zeigt einen technischen Schluessel. Wo ein Bezug aenderbar
   bleibt, steht daneben — in der Maske — sein Name oder seine Nummer, und die
   Einzelabfrage liefert beides mit.

Die HTTP-Vertraege laufen gegen die echte App und PostgreSQL; ohne Datenbank
wird uebersprungen, nicht gruen gewertet.
"""

from __future__ import annotations

import os
import re
import uuid

import pytest

from app.core.screen_definitions import (
    SCREEN_DEFINITION_BUILDERS,
    _with_meridian_identity,
    _with_meridian_layout,
    get_screen_definition,
    infer_identity_field,
)

DB_URL = os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp"
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

_BELEG_FLOORPLANS = {"objectPage", "transaction"}
_RAW_KEY = re.compile(r"(_id|Id)$")
_READABLE_SUFFIXES = ("_name", "_nummer", "_number", "_nr")

# Schluessel, die fachlich so heissen, aber kein technischer Bezug sind — oder
# bewusst als technische Provenienz ausgewiesen werden.
_RAW_KEY_ALLOWLIST = {
    # USt-IdNr. ist eine Steuernummer, kein Fremdschluessel.
    "ust_id",
    # Futterplan: Herkunftsnachweis, ausdruecklich als technische ID beschriftet.
    "plan_id",
    "source_ration_version_id",
    # Futteranalyse: Archivschluessel im DMS; der Kopf zeigt den Dateinamen.
    "original_document_id",
}


def _beleg_definitions() -> list[tuple[str, dict]]:
    result = []
    for mask_id in sorted(SCREEN_DEFINITION_BUILDERS):
        definition = get_screen_definition(mask_id)
        if definition and (definition.get("layout") or {}).get("floorplan") in _BELEG_FLOORPLANS:
            result.append((mask_id, definition))
    return result


def _head_fields(definition: dict) -> list[dict]:
    if definition.get("fields"):
        return list(definition["fields"])
    tabs = definition.get("tabs") or []
    return list((tabs[0].get("fields") or []) if tabs else [])


def _all_fields(definition: dict) -> list[dict]:
    fields = list(definition.get("fields") or [])
    for tab in definition.get("tabs") or []:
        fields.extend(tab.get("fields") or [])
    return fields


def _visible(fields: list[dict]) -> list[dict]:
    return [f for f in fields if f.get("key") and not f.get("hidden")]


# ---------------------------------------------------------------------------
# Kopf-Gate
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("mask_id", "definition"), _beleg_definitions(), ids=lambda v: v if isinstance(v, str) else "")
def test_kopf_zeigt_keinen_technischen_schluessel(mask_id: str, definition: dict) -> None:
    roh = [
        f["key"]
        for f in _visible(_head_fields(definition))
        if _RAW_KEY.search(f["key"]) and f["key"] not in _RAW_KEY_ALLOWLIST
    ]
    assert roh == [], f"{mask_id}: Kopf zeigt technische Schluessel {roh}"


@pytest.mark.parametrize(("mask_id", "definition"), _beleg_definitions(), ids=lambda v: v if isinstance(v, str) else "")
def test_aenderbarer_bezug_hat_lesbares_gegenstueck(mask_id: str, definition: dict) -> None:
    keys = {f["key"] for f in _visible(_all_fields(definition))}
    ohne_gegenstueck = []
    for key in sorted(keys):
        if not _RAW_KEY.search(key) or key in _RAW_KEY_ALLOWLIST:
            continue
        stamm = _RAW_KEY.sub("", key)
        if not any(stamm + suffix in keys for suffix in _READABLE_SUFFIXES):
            ohne_gegenstueck.append(key)
    assert ohne_gegenstueck == [], f"{mask_id}: Bezuege ohne Name/Nummer {ohne_gegenstueck}"


# ---------------------------------------------------------------------------
# Navigation und Identitaet
# ---------------------------------------------------------------------------


_IDENTITAET = {
    "agrar/duenger": "artikelnummer",
    "agrar/feeding-business": "name",
    "agrar/feeding-group": "name",
    "agrar/feeding-plan": "name",
    "agrar/harvest-settlement": "settlement_number",
    # Kontrakte und Bankkonten fuehren im Kopf weder Nummer noch Namen; der
    # Titel der Maske bleibt die Ueberschrift.
    "agrar/kontrakte": None,
    "agrar/ration": "name",
    "agrar/saatgut": "artikelnummer",
    "crm/lead": "company_name",
    "crm/opportunity": "name",
    "einkauf/anfrage": "anfrageNummer",
    "einkauf/angebot": "angebotNummer",
    "einkauf/anlieferavis": "avisNummer",
    "einkauf/auftragsbestaetigung": "bestaetigungsNummer",
    "einkauf/purchase-order": "bestellnummer",
    "einkauf/supplier": "lieferantennummer",
    "finance/ap-invoice": "beleg_nr",
    "finance/ar-open-item": "rechnungsnr",
    "finance/bankkonto": None,
    "finance/debitor": "debitoren_nr",
    "finance/kreditor": "kreditoren_nr",
    "finance/payment-run": "run_number",
    "futtermittel/analyse": "probe_nr",
    "futtermittel/einzelfuttermittel": "artikel_nummer",
    "futtermittel/mischfuttermittel": "produkt_code",
    "lager/article-stock": "article_number",
    "lager/stock-movement": "movement_number",
    "qualitaet/reklamation": "reklamation_nr",
    "sales/delivery-note": "delivery_note_number",
    "sales/invoice": "invoice_number",
    "sales/sales-order": "order_number",
}


def test_identitaet_je_belegmaske() -> None:
    assert {mask_id: d.get("identityField") for mask_id, d in _beleg_definitions()} == _IDENTITAET


def test_jede_belegmaske_laeuft_mit_abschnittsankern() -> None:
    ohne_anker = [
        mask_id
        for mask_id, d in _beleg_definitions()
        if d["layout"].get("sectionNavigation") != "anchors"
    ]
    assert ohne_anker == []


def test_layout_setzt_anker_nur_fuer_einspaltige_belege() -> None:
    beleg = _with_meridian_layout({"id": "x/beleg", "domain": "x", "layout": {"floorplan": "objectPage"}})
    assert beleg["layout"]["sectionNavigation"] == "anchors"

    transaktion = _with_meridian_layout({"id": "x/tx", "domain": "x", "layout": {"floorplan": "transaction"}})
    assert transaktion["layout"]["sectionNavigation"] == "anchors"

    liste = _with_meridian_layout({
        "id": "x/liste", "domain": "x", "layout": {"floorplan": "worklist"},
        "tables": [{"key": "t", "columns": [{"key": "a"}]}],
    })
    assert "sectionNavigation" not in liste["layout"]

    spalten = _with_meridian_layout({
        "id": "x/spalten", "domain": "x",
        "layout": {"floorplan": "objectPage", "columnNavigation": "listDetail"},
    })
    assert "sectionNavigation" not in spalten["layout"]


def test_layout_respektiert_ausdrueckliche_register() -> None:
    register = _with_meridian_layout({
        "id": "x/register", "domain": "x",
        "layout": {"floorplan": "objectPage", "sectionNavigation": "tabs"},
    })
    assert register["layout"]["sectionNavigation"] == "tabs"


def test_identitaet_bevorzugt_nummer_vor_namen() -> None:
    definition = {"fields": [
        {"key": "name", "label": "Name"},
        {"key": "telefon_nr", "label": "Telefon-Nr."},
        {"key": "ust_nummer", "label": "USt-Nummer"},
        {"key": "auftrag_nr", "label": "Auftrags-Nr."},
    ]}
    assert infer_identity_field(definition) == "auftrag_nr"


def test_identitaet_erkennt_nummer_am_label() -> None:
    definition = {"tabs": [{"key": "kopf", "fields": [
        {"key": "status", "label": "Status"},
        {"key": "reklamation_nr", "label": "Reklamations-Nr."},
    ]}]}
    assert infer_identity_field(definition) == "reklamation_nr"


def test_identitaet_faellt_auf_namen_zurueck_und_ignoriert_verborgenes() -> None:
    definition = {"fields": [
        {"key": "beleg_nr", "label": "Beleg-Nr.", "hidden": True},
        {"key": "bezeichnung", "label": "Bezeichnung"},
    ]}
    assert infer_identity_field(definition) == "bezeichnung"
    assert infer_identity_field({"fields": [{"key": "status", "label": "Status"}]}) is None


def test_identitaet_ueberschreibt_keine_builder_angabe() -> None:
    erklaert = _with_meridian_identity({
        "identityField": "eigene",
        "layout": {"floorplan": "objectPage"},
        "fields": [{"key": "beleg_nr", "label": "Beleg-Nr."}],
    })
    assert erklaert["identityField"] == "eigene"

    liste = _with_meridian_identity({
        "layout": {"floorplan": "worklist"},
        "fields": [{"key": "beleg_nr", "label": "Beleg-Nr."}],
    })
    assert "identityField" not in liste


def test_readiness_meldet_aufgeloestes_layout() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness

    bericht = _check_readiness(get_screen_definition("lager/stock-movement"))
    assert bericht["resolvedLayout"] == {
        "floorplan": "transaction",
        "sectionNavigation": "anchors",
        "identityField": "movement_number",
    }


def test_readiness_akzeptiert_row_detail_opt_out() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness

    definition = get_screen_definition("einkauf/purchase-order")
    for tab in definition["tabs"]:
        for table in tab.get("tables") or []:
            table["rowDetail"] = False
    bericht = _check_readiness(definition)
    assert not [fehler for fehler in bericht["errors"] if "rowDetail" in fehler]


# ---------------------------------------------------------------------------
# Referenz-Resolver gegen PostgreSQL
# ---------------------------------------------------------------------------


def _engine():
    from sqlalchemy import create_engine, text

    engine = create_engine(DB_URL)
    try:
        with engine.connect() as verbindung:
            verbindung.execute(text("SELECT 1"))
    except Exception as fehler:  # noqa: BLE001 - jede Verbindungsart fuehrt zum Skip
        if os.environ.get("PYTEST_REQUIRE_DB_STRICT") == "1":
            pytest.fail(f"PostgreSQL nicht erreichbar: {fehler}")
        pytest.skip(f"PostgreSQL nicht erreichbar: {fehler}")
    return engine


_BP_FLAGS = (
    "is_customer", "is_supplier", "is_carrier", "is_employee", "is_service_provider",
    "blocked_for_delivery", "blocked_for_invoice", "bio_certified", "email_opt_in", "sms_opt_in",
    "whatsapp_opt_in", "newsletter_opt_in", "flyer_subscription", "privacy_policy_accepted",
    "data_processing_agreement_signed", "bank_connection_active", "wants_account_statement",
    "print_balance_on_invoice", "invoice_print_blocked", "delivery_note_print_blocked",
    "calculate_shipping_flat", "self_billing_customer", "auto_offset_enabled",
    "post_open_items_blocked", "market_price_evaluation", "webshop_customer", "fax_blocked",
    "proforma_invoice", "membership_terminated", "customer_card_flag", "edifact_invoic",
    "edifact_orders", "edifact_desadv",
)

# Reihenfolge = Loeschreihenfolge: Belege vor den Stammdaten, auf die sie zeigen.
_MANDANTEN_TABELLEN = (
    ("domain_inventory.agrar_settlements", "tenant_id"),
    ("domain_inventory.inventory_stock_movements", "tenant_id"),
    ("domain_ops.reklamationen", "tenant_id"),
    ("domain_einkauf.bestellungen", "tenant_id"),
    ("domain_sales.delivery_notes", "tenant_id"),
    ("domain_einkauf.kontrakte", "tenant_id"),
    ("domain_einkauf.lieferanten", "tenant_id"),
    ("domain_inventory.agrar_contracts", "tenant_id"),
    ("domain_inventory.warehouses", "tenant_id"),
    ("domain_inventory.articles", "tenant_id"),
    ("domain_agrar.ernte_kampagnen", "tenant_id"),
    ("domain_crm.sales_orders", "tenant_id"),
    ("domain_crm.business_partners", "tenant_id"),
    ("domain_crm.customers", "tenant_id"),
    ("domain_shared.branches", "tenant_id"),
    ("domain_shared.tenants", "id"),
)


@pytest.fixture()
def stamm():
    """Ein frischer Mandant mit je einem Stammsatz pro Referenzart."""
    from sqlalchemy import text

    engine = _engine()
    mandant = f"test-{uuid.uuid4().hex[:8]}"
    ids = {
        "lieferant": str(uuid.uuid4()),
        "kontrakt": str(uuid.uuid4()),
        "niederlassung": f"br-{uuid.uuid4().hex[:8]}",
        "lager": f"wh-{uuid.uuid4().hex[:8]}",
        "artikel": f"art-{uuid.uuid4().hex[:8]}",
        "auftrag": f"so-{uuid.uuid4().hex[:8]}",
        "kampagne": f"kamp-{uuid.uuid4().hex[:8]}",
        "erzeuger": f"bp-{uuid.uuid4().hex[:8]}",
        "agrarkontrakt": f"ac-{uuid.uuid4().hex[:8]}",
        # UUID, weil die Opportunity customer_id als UUID fuehrt.
        "kunde": str(uuid.uuid4()),
    }
    bp_spalten = ", ".join(_BP_FLAGS)
    bp_werte = ", ".join("false" for _ in _BP_FLAGS)
    with engine.begin() as v:
        v.execute(text(
            "INSERT INTO domain_shared.tenants (id, name, domain, is_active) VALUES (:t, :t, :d, true)"
        ), {"t": mandant, "d": f"{mandant}.test"})
        v.execute(text(
            "INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname) "
            "VALUES (:id, :t, 'LF-4711', 'Agrarhandel Nord GmbH')"
        ), {"id": ids["lieferant"], "t": mandant})
        v.execute(text(
            "INSERT INTO domain_einkauf.kontrakte (id, tenant_id, kontraktnummer, lieferant_id, bezeichnung) "
            "VALUES (:id, :t, 'EK-K-2026-07', :lf, 'Weizen Ernte 2026')"
        ), {"id": ids["kontrakt"], "t": mandant, "lf": ids["lieferant"]})
        v.execute(text(
            "INSERT INTO domain_shared.branches (id, tenant_id, branch_number, name) "
            "VALUES (:id, :t, 12, 'Niederlassung Suedheide')"
        ), {"id": ids["niederlassung"], "t": mandant})
        v.execute(text(
            "INSERT INTO domain_inventory.warehouses (id, tenant_id, warehouse_code, name, address, city, postal_code) "
            "VALUES (:id, :t, 'L-03', 'Getreidelager Hafen', 'Kai 3', 'Bremen', '28195')"
        ), {"id": ids["lager"], "t": mandant})
        v.execute(text(
            "INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, mhd_erforderlich, "
            "lagerartikel, lagerorte, chargenpflicht, qs_pruefung_erforderlich, bio_kennzeichnung, "
            "gmp_plus_relevanz, unit, category, sales_price) "
            "VALUES (:id, :t, '10001', 'Weizen A', false, true, '[]'::jsonb, false, false, false, false, "
            "'t', 'Getreide', 0)"
        ), {"id": ids["artikel"], "t": mandant})
        v.execute(text(
            "INSERT INTO domain_crm.sales_orders (id, tenant_id, order_number) VALUES (:id, :t, 'VA-2026-0815')"
        ), {"id": ids["auftrag"], "t": mandant})
        v.execute(text(
            "INSERT INTO domain_agrar.ernte_kampagnen (id, kampagne_id, tenant_id, wirtschaftsjahr, ernte_art, bezeichnung) "
            "VALUES (:id, :kid, :t, 2026, 'getreide', 'Getreideernte 2026')"
        ), {"id": str(uuid.uuid4()), "kid": ids["kampagne"], "t": mandant})
        v.execute(text(
            f"INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name_1, status, {bp_spalten}) "  # nosec B608
            f"VALUES (:id, :t, 'E-2001', 'Hof Meyer GbR', 'active', {bp_werte})"
        ), {"id": ids["erzeuger"], "t": mandant})
        v.execute(text(
            "INSERT INTO domain_inventory.agrar_contracts (id, tenant_id, contract_number, contract_type, harvest_year, "
            "partner_id, article_id, pricing_model, total_quantity_kg, remaining_quantity_kg) "
            "VALUES (:id, :t, 'AK-2026-031', 'purchase', 2026, :bp, :art, 'fixed', 100000, 100000)"
        ), {"id": ids["agrarkontrakt"], "t": mandant, "bp": ids["erzeuger"], "art": ids["artikel"]})
        v.execute(text(
            "INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
            "VALUES (:id, :t, 'K-3300', 'Raiffeisen Markt Ost eG')"
        ), {"id": ids["kunde"], "t": mandant})
    try:
        yield {"mandant": mandant, "engine": engine, **ids}
    finally:
        with engine.begin() as v:
            for tabelle, spalte in _MANDANTEN_TABELLEN:
                v.execute(text(f"DELETE FROM {tabelle} WHERE {spalte} = :t"), {"t": mandant})  # nosec B608


def _resolve(stamm: dict, kind: str, reference: object):
    from sqlalchemy.orm import Session

    from app.services.customer_reference import resolve_reference

    with Session(stamm["engine"]) as db:
        return resolve_reference(db, stamm["mandant"], kind, reference)


@pytest.mark.integration
def test_resolver_findet_ueber_id_und_ueber_nummer(stamm: dict) -> None:
    ueber_id = _resolve(stamm, "supplier", stamm["lieferant"])
    assert (ueber_id.name, ueber_id.number, ueber_id.found) == ("Agrarhandel Nord GmbH", "LF-4711", True)

    ueber_nummer = _resolve(stamm, "supplier", "LF-4711")
    assert (ueber_nummer.name, ueber_nummer.number) == ("Agrarhandel Nord GmbH", "LF-4711")

    # Ganzzahlige Nummern werden als Text verglichen.
    assert _resolve(stamm, "branch", "12").name == "Niederlassung Suedheide"
    assert _resolve(stamm, "warehouse", stamm["lager"]).name == "Getreidelager Hafen"


@pytest.mark.integration
def test_resolver_kennt_arten_ohne_namen_oder_ohne_nummer(stamm: dict) -> None:
    auftrag = _resolve(stamm, "sales_order", stamm["auftrag"])
    assert (auftrag.name, auftrag.number) == (None, "VA-2026-0815")

    kampagne = _resolve(stamm, "harvest_campaign", stamm["kampagne"])
    assert (kampagne.name, kampagne.number, kampagne.found) == ("Getreideernte 2026", None, True)


@pytest.mark.integration
def test_resolver_ohne_treffer_zeigt_keine_uuid(stamm: dict) -> None:
    fremde_uuid = _resolve(stamm, "supplier", str(uuid.uuid4()))
    assert (fremde_uuid.name, fremde_uuid.number, fremde_uuid.found) == (None, None, False)

    # Eine fachliche Nummer ohne Stammsatz bleibt sichtbar, statt zu verschwinden.
    altnummer = _resolve(stamm, "supplier", "LF-ALT-9")
    assert (altnummer.name, altnummer.number, altnummer.found) == (None, "LF-ALT-9", False)

    leer = _resolve(stamm, "supplier", None)
    assert (leer.name, leer.number) == (None, None)


@pytest.mark.integration
def test_resolver_bleibt_im_mandanten(stamm: dict) -> None:
    from sqlalchemy.orm import Session

    from app.services.customer_reference import resolve_reference

    with Session(stamm["engine"]) as db:
        fremd = resolve_reference(db, "anderer-mandant", "supplier", stamm["lieferant"])
    assert fremd.found is False
    assert fremd.name is None


# ---------------------------------------------------------------------------
# HTTP-Vertraege: die entity-Datenquelle jeder Maske liefert ihren Kopf
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def _kopf(mandant: str) -> dict[str, str]:
    return {"Authorization": "Bearer dev-token", "X-Tenant-ID": mandant, "X-Tenant-Id": mandant}


def _entity_url(mask_id: str, entity_id: str) -> str:
    definition = get_screen_definition(mask_id)
    quelle = next(ds for ds in definition["dataSources"] if ds["key"] == "entity")
    return quelle["endpoint"].replace("{entity_id}", entity_id)


def _kopf_keys(mask_id: str) -> set[str]:
    return {f["key"] for f in _visible(_head_fields(get_screen_definition(mask_id)))}


@pytest.mark.integration
def test_lieferschein_nennt_die_niederlassung(client, stamm: dict) -> None:
    kopf = _kopf(stamm["mandant"])
    angelegt = client.post("/api/v1/sales/delivery-notes", headers=kopf, json={
        "customer_id": stamm["kunde"],
        "branch_id": stamm["niederlassung"],
        "delivery_date": "2026-09-29",
        "positionen": [],
    })
    assert angelegt.status_code == 201, angelegt.text

    gelesen = client.get(_entity_url("sales/delivery-note", angelegt.json()["id"]), headers=kopf)
    assert gelesen.status_code == 200, gelesen.text
    assert gelesen.json()["branch_name"] == "Niederlassung Suedheide"
    assert "branch_name" in _kopf_keys("sales/delivery-note")


@pytest.mark.integration
def test_lagerbewegung_nennt_das_lager(client, stamm: dict, monkeypatch) -> None:
    from sqlalchemy import text

    from app.core import security
    from app.main import app

    # Die Lager-API prueft die Claims des Dev-Tokens selbst; die globale
    # Bearer-Abkuerzung der Suite liesse sie leer.
    monkeypatch.delitem(app.dependency_overrides, security.require_bearer_token, raising=False)
    bewegung = f"mv-{uuid.uuid4().hex[:8]}"
    with stamm["engine"].begin() as v:
        v.execute(text(
            "INSERT INTO domain_inventory.inventory_stock_movements (id, tenant_id, article_id, warehouse_id, "
            "movement_type, quantity, auto_created, ownership_type, storage_fee_relevant, previous_stock, "
            "new_stock, movement_number) "
            "VALUES (:id, :t, :art, :wh, 'in', 12.5, false, 'owned', false, 0, 12.5, 'LB-2026-0001')"
        ), {"id": bewegung, "t": stamm["mandant"], "art": stamm["artikel"], "wh": stamm["lager"]})

    # Die Lager-API liest den Mandanten aus dem Query-Parameter, nicht aus dem Header.
    gelesen = client.get(
        _entity_url("lager/stock-movement", bewegung),
        params={"tenant_id": stamm["mandant"]},
        headers=_kopf(stamm["mandant"]),
    )
    assert gelesen.status_code == 200, gelesen.text
    assert gelesen.json()["warehouse_name"] == "Getreidelager Hafen"
    assert "warehouse_name" in _kopf_keys("lager/stock-movement")


@pytest.mark.integration
def test_reklamation_nennt_lieferant_kontrakt_und_nummer(client, stamm: dict) -> None:
    kopf = _kopf(stamm["mandant"])
    angelegt = client.post("/api/v1/reklamationen", headers=kopf, json={
        "lieferant_id": "LF-4711",
        "kontrakt_id": stamm["kontrakt"],
        "typ": "qualitaet",
        "positionen": [],
        "zustaendiger": "qs-team",
        "frist_datum": "2026-10-15",
    })
    assert angelegt.status_code in (200, 201), angelegt.text

    gelesen = client.get(_entity_url("qualitaet/reklamation", angelegt.json()["reklamation_id"]), headers=kopf)
    assert gelesen.status_code == 200, gelesen.text
    body = gelesen.json()
    assert body["lieferant_name"] == "Agrarhandel Nord GmbH"
    assert body["lieferant_nummer"] == "LF-4711"
    assert body["kontrakt_nummer"] == "EK-K-2026-07"
    assert re.fullmatch(r"REK-[0-9A-F]{8}", body["reklamation_nr"])


@pytest.mark.integration
def test_reklamation_faellt_auf_agrarkontrakt_zurueck(client, stamm: dict) -> None:
    kopf = _kopf(stamm["mandant"])
    angelegt = client.post("/api/v1/reklamationen", headers=kopf, json={
        "lieferant_id": stamm["lieferant"],
        "kontrakt_id": stamm["agrarkontrakt"],
        "typ": "qualitaet",
        "positionen": [],
        "zustaendiger": "qs-team",
        "frist_datum": "2026-10-15",
    })
    assert angelegt.status_code in (200, 201), angelegt.text

    body = client.get(_entity_url("qualitaet/reklamation", angelegt.json()["reklamation_id"]), headers=kopf).json()
    assert body["kontrakt_nummer"] == "AK-2026-031"
    assert body["lieferant_nummer"] == "LF-4711"


@pytest.mark.integration
def test_ernteabrechnung_nennt_erzeuger_kampagne_artikel_kontrakt(client, stamm: dict) -> None:
    from sqlalchemy import text

    abrechnung = f"set-{uuid.uuid4().hex[:8]}"
    with stamm["engine"].begin() as v:
        v.execute(text(
            "INSERT INTO domain_inventory.agrar_settlements (id, tenant_id, settlement_number, supplier_id, "
            "campaign_id, article_id, contract_id, gross_quantity_kg, billing_quantity_kg, "
            "unit_price_eur_per_ton, gross_amount_eur, total_deductions_eur, net_amount_eur, currency, status) "
            "VALUES (:id, :t, 'EA-2026-0042', :bp, :kamp, :art, :ak, 25000, 24500, 210, 5145, 0, 5145, 'EUR', 'draft')"
        ), {
            "id": abrechnung, "t": stamm["mandant"], "bp": stamm["erzeuger"], "kamp": stamm["kampagne"],
            "art": stamm["artikel"], "ak": stamm["agrarkontrakt"],
        })

    gelesen = client.get(_entity_url("agrar/harvest-settlement", abrechnung), headers=_kopf(stamm["mandant"]))
    assert gelesen.status_code == 200, gelesen.text
    body = gelesen.json()
    assert body["supplier_name"] == "Hof Meyer GbR"
    assert body["supplier_number"] == "E-2001"
    assert body["campaign_name"] == "Getreideernte 2026"
    assert body["article_name"] == "Weizen A"
    assert body["contract_number"] == "AK-2026-031"
    assert {"supplier_name", "campaign_name", "article_name", "contract_number"} <= _kopf_keys("agrar/harvest-settlement")


@pytest.mark.integration
def test_bestellung_nennt_niederlassung_und_belegkette(client, stamm: dict) -> None:
    kopf = _kopf(stamm["mandant"])
    angelegt = client.post("/api/v1/einkauf/bestellungen", headers=kopf, json={
        "lieferant_id": stamm["lieferant"],
        "bestelldatum": "2026-09-29",
        "niederlassung_id": stamm["niederlassung"],
        "kontrakt_id": stamm["kontrakt"],
        "verkaufsbeleg_id": stamm["auftrag"],
        "kunden_id": "K-3300",
        "bestellfall": "direktlieferung",
    })
    assert angelegt.status_code in (200, 201), angelegt.text

    gelesen = client.get(_entity_url("einkauf/purchase-order", angelegt.json()["id"]), headers=kopf)
    assert gelesen.status_code == 200, gelesen.text
    body = gelesen.json()
    assert body["niederlassung_name"] == "Niederlassung Suedheide"
    assert body["kontrakt_nummer"] == "EK-K-2026-07"
    assert body["verkaufsbeleg_nummer"] == "VA-2026-0815"
    assert body["kunden_name"] == "Raiffeisen Markt Ost eG"
    # Die Bezuege bleiben aenderbar und kommen weiter mit.
    assert body["niederlassung_id"] == stamm["niederlassung"]
    assert "niederlassung_name" in _kopf_keys("einkauf/purchase-order")


@pytest.mark.integration
def test_futteranalyse_nennt_den_originalbeleg(client) -> None:
    _engine()
    mandant = "00000000-0000-0000-0000-000000000001"
    kopf = {"Authorization": "Bearer dev-token", "X-Tenant-Id": mandant}
    suffix = uuid.uuid4().hex[:8]
    futter = client.post("/api/v1/agrar/rations-optimization/feed-catalog/feeds", headers=kopf, json={
        "artikel_nummer": f"MBS-{suffix}", "name": f"Maissilage {suffix}", "art": "Grundfutter",
        "feed_kind": "forage", "approval_status": "approved", "trockensubstanz": "35",
    })
    assert futter.status_code == 201, futter.text
    analyse = client.post("/api/v1/agrar/rations-optimization/feed-analyses", headers=kopf, json={
        "feed_id": futter.json()["id"], "bezeichnung": f"Maissilage Probe {suffix}",
        "probe_nr": f"P-{suffix}", "labor": "Testlabor", "status": "draft",
        "quelle_datei": f"laborbefund-{suffix}.pdf", "values": [],
    })
    assert analyse.status_code == 201, analyse.text

    gelesen = client.get(_entity_url("futtermittel/analyse", analyse.json()["id"]), headers=kopf)
    assert gelesen.status_code == 200, gelesen.text
    assert gelesen.json()["quelle_datei"] == f"laborbefund-{suffix}.pdf"
    assert "quelle_datei" in _kopf_keys("futtermittel/analyse")


@pytest.mark.integration
def test_verkaufschance_nennt_den_kunden(client, stamm: dict, monkeypatch) -> None:
    """Die Opportunity kommt aus crm-sales; ersetzt wird nur dieser externe Dienst, nicht die DB."""
    from app.api.v1.endpoints import opportunities

    chance_id = str(uuid.uuid4())

    async def _crm_sales(opportunity_id: str) -> dict:
        assert opportunity_id == chance_id
        return {
            "id": chance_id, "tenant_id": stamm["mandant"], "name": "Frühjahrsdüngung 2027",
            "status": "prospecting", "stage": "initial_contact", "customer_id": stamm["kunde"],
            "created_at": "2026-09-29T08:00:00Z", "updated_at": "2026-09-29T08:00:00Z",
        }

    monkeypatch.setattr(opportunities, "crm_get_opportunity", _crm_sales)
    gelesen = client.get(_entity_url("crm/opportunity", chance_id), headers=_kopf(stamm["mandant"]))
    assert gelesen.status_code == 200, gelesen.text
    body = gelesen.json()
    assert body["customer_name"] == "Raiffeisen Markt Ost eG"
    assert body["customer_number"] == "K-3300"
    assert {"customer_name", "customer_number"} <= _kopf_keys("crm/opportunity")
