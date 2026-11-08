"""Launcher-Inbox-Vertrag: Klassifikation, Konfidenz, keine Buchung.

Reine Funktionen ohne Datenbank.
"""

from __future__ import annotations

import pytest

import inspect

from app.documents.inbox_contract import (
    ARTICLE_CREATE_API,
    ARTICLE_IMAGE_ENRICH_API,
    BOOKING_BLOCKED_REASON,
    PIPELINE_GAPS,
    PREFILL_SCHEMA,
    PREFILL_STORAGE_KEY,
    SUPPLIER_CREATE_API,
    blend_confidence,
    build_master_data_proposals,
    build_queue_item,
    classify_document,
    confidence_band,
    contract_match_from_candidates,
    document_kind_from_existing,
    duplicate_hints,
    evaluate_can_open,
    extract_line_items,
    header_plausibility_uncertainties,
    partner_match_from_candidates,
    prepare_command,
    verified_linked_document_id,
)

_EINKAUF_USER = {"sub": "u1", "roles": ["EINKAUF_BEARBEITEN"]}
from app.documents import inbox_service
from app.documents.router import router

pytestmark = pytest.mark.unit


def test_inbox_routes_are_registered_before_doc_type_catchall():
    paths = [getattr(route, "path", "") for route in router.routes]
    queue_index = paths.index("/api/mcp/documents/inbox/queue")
    catchall = next(i for i, path in enumerate(paths) if path.endswith("/{doc_type}"))
    assert queue_index < catchall


def test_inbox_loaders_require_tenant_id_and_filter_sql():
    """Ohne DB: Lesepfade binden Mandant und filtern in SQL — nie Client-Query."""
    pending = inspect.getsource(inbox_service.load_pending_entries)
    entry = inspect.getsource(inbox_service.load_entry)
    assert "tenant_id" in inspect.signature(inbox_service.load_pending_entries).parameters
    assert "tenant_id" in inspect.signature(inbox_service.load_entry).parameters
    assert "tenant_id = :tenant_id" in pending
    assert "tenant_id = :tenant_id" in entry
    assert "dms_webhook_schreibt_keinen_mandant" not in PIPELINE_GAPS
    assert "dms_inbox_ohne_mandant" not in PIPELINE_GAPS
    duplicates = inspect.getsource(inbox_service.load_duplicate_candidates)
    assert "SELECT id, doc_type, doc_number" in duplicates
    contracts = inspect.getsource(inbox_service.load_contract_candidates)
    assert "domain_ops.kon_contract" in contracts
    assert "domain_inventory.agrar_contracts" in contracts
    assert "tenant_id = :tenant_id" in contracts


def test_classify_defaults_to_incoming_invoice():
    policy = classify_document({"invoice_number": "RE-1", "supplier": "Mueller GmbH"})
    assert policy["policy_id"] == "incoming-supplier-invoice"
    assert policy["target_route"] == "/einkauf/rechnung-eingang-erfassung"


def test_classify_uses_ocr_hint_for_delivery_note():
    policy = classify_document({}, "Lieferschein Nr. 12 vom Lieferanten")
    assert policy["policy_id"] == "incoming-delivery-note"
    assert policy["target_route"] == "/einkauf/lieferschein-erfassung"


def test_confidence_band_and_duplicate_penalty():
    assert confidence_band(0.9) == "high"
    assert confidence_band(0.1) == "review"
    blended = blend_confidence(0.9, 1.0, duplicate_count=1)
    assert blended < blend_confidence(0.9, 1.0, duplicate_count=0)


def test_duplicate_hints_match_document_number():
    found = duplicate_hints("RE-9", [{"doc_type": "sales_invoice", "doc_number": "RE-9"}])
    assert found == [{"doc_type": "sales_invoice", "doc_number": "RE-9"}]
    assert duplicate_hints(None, found) == []


def test_duplicate_hints_carry_verified_document_id():
    found = duplicate_hints(
        "RE-9",
        [{"id": "doc-pk-9", "doc_type": "purchase_invoice", "doc_number": "RE-9"}],
    )
    assert found == [{
        "id": "doc-pk-9",
        "doc_type": "purchase_invoice",
        "doc_number": "RE-9",
    }]
    assert verified_linked_document_id(found) == "doc-pk-9"
    assert verified_linked_document_id([{"doc_type": "x", "doc_number": "RE-9"}]) is None
    assert verified_linked_document_id([
        {"id": "a", "doc_type": "x", "doc_number": "RE-9"},
        {"id": "b", "doc_type": "y", "doc_number": "RE-9"},
    ]) is None


def test_contract_match_from_candidates_exact_and_missing():
    matched, unc = contract_match_from_candidates(
        {"contractId": "13842"},
        [{
            "contract_id": "kon-1",
            "contract_number": "13842",
            "source": "kon_contract",
            "matched_by": "contract_number",
        }],
    )
    assert matched == {
        "kind": "contract",
        "status": "matched",
        "matched_by": "contract_number",
        "source": "kon_contract",
        "contract_id": "kon-1",
        "contract_number": "13842",
    }
    assert unc == []

    missing, missing_unc = contract_match_from_candidates({"contractId": "13842"}, [])
    assert missing is None
    assert missing_unc[0]["code"] == "kontrakt_nicht_gefunden"

    none_match, none_unc = contract_match_from_candidates({}, [])
    assert none_match is None
    assert none_unc == []


def test_prepare_command_never_books():
    policy = classify_document({"invoice_number": "RE-2"})
    command = prepare_command(
        item_id="INBOX-1",
        policy=policy,
        parsed_fields={"invoice_number": "RE-2", "supplier_id": "L-10"},
        confidence=0.7,
        duplicates=[],
    )
    assert command["executable"] is False
    assert command["booking"] is False
    assert command["command"] == "document.capture.open"
    prefill = command["prefill"]
    assert prefill["schema"] == PREFILL_SCHEMA
    assert prefill["documentId"] == "INBOX-1"
    assert prefill["partner"]["id"] == "L-10"
    assert prefill["partner"]["role"] == "supplier"
    assert prefill["amounts"]["currency"] == "EUR"
    assert prefill["source"]["kind"] == "dms_inbox"
    assert prefill["confidence"] == 0.7
    assert prefill["booking"] is False
    assert prefill["maskConsumesPrefill"] is True
    assert prefill["storageKey"] == PREFILL_STORAGE_KEY
    assert prefill["matchValues"]["supplierId"] == "L-10"
    assert BOOKING_BLOCKED_REASON in command["reason"]
    assert "create_from_inbox_bucht_nicht" in command["gaps"]
    assert "zielmaske_liest_prefill_nicht" not in command["gaps"]
    assert "dms_inbox_ohne_mandant" not in command["gaps"]
    assert "dms_webhook_schreibt_keinen_mandant" not in command["gaps"]


def test_queue_item_opens_existing_mask_and_lists_gaps():
    item = build_queue_item(
        entry={
            "id": "INBOX-44",
            "dms_document_id": 44,
            "status": "pending",
            "confidence": 0.5,
            "ocr_text": "Rechnung RE-44",
            "parsed_fields": {
                "invoice_number": "RE-44",
                "supplier": "Nordkorn AG",
                "total": "1280.50",
                "tax": "204.29",
            },
        },
        existing_documents=[{"doc_type": "purchase_order", "doc_number": "RE-44"}],
        partner_candidates=[{
            "partner_id": "bp-nord",
            "partner_number": "L-44",
            "name": "Nordkorn AG",
            "matched_by": "name_search",
        }],
        nutzer=_EINKAUF_USER,
    )
    assert item["booking_allowed"] is False
    assert item["can_open"] is True
    assert item["actions"][0]["enabled"] is True
    assert item["proposal"]["target_route"].startswith("/einkauf/")
    assert item["actions"][0]["key"] == "open_mask"
    assert item["actions"][0]["href"] == "/einkauf/rechnung-eingang-erfassung?inbox=INBOX-44"
    assert item["command"]["prefill"]["partner"]["name"] == "Nordkorn AG"
    assert item["command"]["prefill"]["partner"]["id"] == "bp-nord"
    assert item["command"]["prefill"]["amounts"]["total"] == "1280.50"
    assert item["command"]["prefill"]["documentId"] == "INBOX-44"
    assert item["match"]["status"] == "matched"
    assert item["duplicates"][0]["doc_number"] == "RE-44"
    assert any(blocker["code"] == "dublette" for blocker in item["blockers"])
    assert any(hint["code"] == "dublette" for hint in item["uncertainties"])
    assert item["command"]["prefill"]["duplicates"][0]["doc_number"] == "RE-44"
    assert item["proposal"]["document_kind"] is None
    assert set(PIPELINE_GAPS).issubset(set(item["command"]["gaps"]))
    assert "kontrakt_abgleich_nur_bei_kontraktnummer_im_extrakt" in PIPELINE_GAPS
    assert "linked_document_id_nur_bei_eindeutigem_documents_treffer" in PIPELINE_GAPS
    assert "kein_kontrakt_abgleich_am_eingang" not in PIPELINE_GAPS
    assert "artikel_abgleich_nur_bei_positionszeilen" in PIPELINE_GAPS
    assert "dms_parser_ohne_positionszeilen" in PIPELINE_GAPS
    assert "positionsextraktion_engine_nicht_claude" in PIPELINE_GAPS
    assert "positionsextraktion_ohne_llm_key" in PIPELINE_GAPS
    assert "positionsextraktion_regex_keine_zeilen" in PIPELINE_GAPS
    assert "kein_artikel_abgleich_am_eingang" not in PIPELINE_GAPS
    assert item["linked_document_id"] is None


def test_queue_item_sets_linked_document_id_from_documents_join():
    item = build_queue_item(
        entry={
            "id": "INBOX-LINK",
            "status": "pending",
            "confidence": 0.8,
            "ocr_text": "Rechnung RE-LINK",
            "parsed_fields": {"invoice_number": "RE-LINK", "supplier": "Nordkorn AG"},
        },
        existing_documents=[{
            "id": "erp-doc-77",
            "doc_type": "purchase_invoice",
            "doc_number": "RE-LINK",
        }],
        partner_candidates=[{
            "partner_id": "bp-1",
            "partner_number": "L-1",
            "name": "Nordkorn AG",
            "matched_by": "name_search",
        }],
        nutzer=_EINKAUF_USER,
    )
    assert item["linked_document_id"] == "erp-doc-77"
    assert item["duplicates"][0]["id"] == "erp-doc-77"


def test_queue_item_contract_match_from_candidates():
    item = build_queue_item(
        entry={
            "id": "INBOX-KON",
            "status": "pending",
            "confidence": 0.8,
            "ocr_text": "Rechnung KontraktNr. 13842",
            "parsed_fields": {
                "invoice_number": "227627",
                "supplier": "Kurt Birkhoff KG",
                "contract_id": "13842",
            },
        },
        contract_candidates=[{
            "contract_id": "kon-13842",
            "contract_number": "13842",
            "source": "kon_contract",
            "matched_by": "contract_number",
        }],
        nutzer=_EINKAUF_USER,
    )
    assert item["contract_match"]["status"] == "matched"
    assert item["contract_match"]["contract_number"] == "13842"
    assert item["match_values"]["contractId"] == "13842"
    assert item["command"]["prefill"]["contractMatch"]["contract_id"] == "kon-13842"
    assert item["command"]["prefill"]["matchValues"]["contractId"] == "13842"


def test_document_kind_maps_existing_classifier_ohne_routing():
    """Ist-Wert aus klassifiziere_dokument; Policy und can_open bleiben unveraendert."""
    assert document_kind_from_existing(
        "Rechnung Rechnungsnummer MwSt Zahlungsziel",
        "INBOX-kind",
    ) == "EINGANGSRECHNUNG"
    item = build_queue_item(
        entry={
            "id": "INBOX-kind",
            "status": "pending",
            "confidence": 0.9,
            "ocr_text": "Rechnung Rechnungsnummer MwSt Zahlungsziel",
            "parsed_fields": {
                "invoice_number": "RE-K",
                "date": "2026-10-01",
                "supplier": "Nordkorn",
                "total": "10.00",
                "tax": "1.00",
            },
        },
        nutzer=_EINKAUF_USER,
    )
    assert item["proposal"]["document_kind"] == "EINGANGSRECHNUNG"
    assert item["proposal"]["document_type"] == "supplier_invoice"
    assert item["can_open"] is True
    assert item["command"]["prefill"]["maskConsumesPrefill"] is True

    weigh = build_queue_item(
        entry={
            "id": "INBOX-waage",
            "status": "pending",
            "confidence": 0.9,
            "ocr_text": "Wiegeschein Waage Bruttogewicht Nettogewicht Tara",
            "parsed_fields": {
                "invoice_number": "WS-1",
                "date": "2026-10-01",
                "supplier": "Nordkorn",
                "total": "10.00",
                "tax": "1.00",
            },
        },
        nutzer=_EINKAUF_USER,
    )
    assert weigh["proposal"]["document_kind"] == "WIEGESCHEIN"
    assert weigh["proposal"]["document_type"] == "supplier_invoice"
    assert weigh["can_open"] is True


def test_document_kind_absent_when_classifier_has_no_kind():
    assert document_kind_from_existing(None) is None
    assert document_kind_from_existing("") is None
    assert document_kind_from_existing("irgendetwas unbekanntes xyz") is None
    item = build_queue_item(
        entry={
            "id": "INBOX-nokind",
            "status": "pending",
            "confidence": 0.9,
            "parsed_fields": {
                "invoice_number": "RE-N",
                "date": "2026-10-01",
                "supplier": "Nord",
                "total": "10.00",
                "tax": "1.00",
            },
        },
        nutzer=_EINKAUF_USER,
    )
    assert item["proposal"]["document_kind"] is None
    assert item["can_open"] is True
    assert item["command"]["prefill"]["maskConsumesPrefill"] is True


def test_header_plausibility_missing_and_amounts():
    missing = header_plausibility_uncertainties({})
    codes = {row["code"] for row in missing}
    assert "pflicht_invoice_number" in codes
    assert "pflicht_date" in codes
    assert "pflicht_supplier" in codes
    assert "pflicht_total" in codes
    assert "pflicht_tax" in codes

    bad = header_plausibility_uncertainties({
        "invoice_number": "RE-1",
        "date": "2026-10-01",
        "supplier": "Nordkorn",
        "total": "abc",
        "tax": "12,5x",
    })
    assert any(row["code"] == "plausi_total_nicht_numerisch" for row in bad)
    assert any(row["code"] == "plausi_tax_nicht_numerisch" for row in bad)

    skewed = header_plausibility_uncertainties({
        "invoice_number": "RE-2",
        "date": "2026-10-01",
        "supplier_id": "L-1",
        "total": "100.00",
        "tax": "120.00",
    })
    assert any(row["code"] == "plausi_tax_groesser_total" for row in skewed)

    ok = header_plausibility_uncertainties({
        "invoice_number": "RE-3",
        "date": "2026-10-01",
        "supplier": "Nordkorn",
        "total": "1280.50",
        "tax": "204.29",
    })
    assert ok == []


def test_queue_item_surfaces_header_uncertainties_in_prefill():
    item = build_queue_item(
        entry={
            "id": "INBOX-plausi",
            "status": "pending",
            "confidence": 0.9,
            "parsed_fields": {
                "invoice_number": "RE-P",
                "date": "2026-10-01",
                "supplier": "Nordkorn",
                "total": "50.00",
                "tax": "80.00",
            },
        },
        partner_candidates=[{
            "partner_id": "bp-1",
            "partner_number": "L-1",
            "name": "Nordkorn",
            "matched_by": "name_search",
        }],
        nutzer=_EINKAUF_USER,
    )
    assert any(row["code"] == "plausi_tax_groesser_total" for row in item["uncertainties"])
    assert any(
        row["code"] == "plausi_tax_groesser_total"
        for row in item["command"]["prefill"]["uncertainties"]
    )
    assert item["booking_allowed"] is False


def test_evaluate_can_open_uses_beleg_roles_not_body():
    policy = classify_document({"invoice_number": "RE-1"})
    allowed, unclear, belegart = evaluate_can_open(policy, _EINKAUF_USER)
    assert allowed is True
    assert belegart == "purchase_invoice"
    assert unclear == []

    denied, denied_unclear, _art = evaluate_can_open(
        policy,
        {"sub": "u2", "roles": ["SALES_LESEN"]},
    )
    assert denied is False
    assert any(row["code"] == "keine_berechtigung_maske" for row in denied_unclear)


def test_evaluate_can_open_maps_supplier_delivery_note_to_goods_receipt():
    """Lieferschein-Eingang: vorhandene Belegart goods_receipt, keine neue Rolle."""
    ocr = "Lieferschein Lieferung delivery versand Empfangsbestaetigung"
    policy = classify_document({}, ocr)
    assert policy["document_type"] == "supplier_delivery_note"
    allowed, unclear, belegart = evaluate_can_open(policy, _EINKAUF_USER)
    assert allowed is True
    assert belegart == "goods_receipt"
    assert unclear == []

    item = build_queue_item(
        entry={
            "id": "INBOX-LS",
            "status": "pending",
            "confidence": 0.85,
            "parsed_fields": {},
            "ocr_text": ocr,
        },
        nutzer=_EINKAUF_USER,
    )
    assert item["proposal"]["document_kind"] == "LIEFERSCHEIN"
    assert item["proposal"]["belegart"] == "goods_receipt"
    assert item["can_open"] is True
    assert item["actions"][0]["enabled"] is True
    assert item["actions"][0]["href"] is not None

    item = build_queue_item(
        entry={
            "id": "INBOX-auth",
            "status": "pending",
            "confidence": 0.9,
            "parsed_fields": {
                "invoice_number": "RE-A",
                "date": "2026-10-01",
                "supplier": "Nord",
                "total": "10.00",
                "tax": "1.00",
            },
        },
        nutzer={"sub": "u3", "roles": ["CRM_LESEN"]},
    )
    assert item["can_open"] is False
    assert item["actions"][0]["enabled"] is False
    assert item["actions"][0]["href"] is None
    assert any(row["code"] == "keine_berechtigung_maske" for row in item["uncertainties"])


def test_supplier_create_proposal_when_partner_not_found_keeps_header_without_inventing_lines():
    item = build_queue_item(
        entry={
            "id": "INBOX-LS-NEW",
            "status": "pending",
            "confidence": 0.8,
            "ocr_text": "Lieferschein Lieferung delivery versand Empfangsbestaetigung",
            "parsed_fields": {
                "supplier": "Neue Muehle GmbH",
                "supplier_id": "L-NEU-9",
                "strasse": "Hofweg 1",
                "plz": "26789",
                "ort": "Leer",
            },
        },
        partner_candidates=[],
        nutzer=_EINKAUF_USER,
    )
    md = item["master_data_proposals"]
    assert md["booking"] is False
    assert md["executable"] is False
    assert md["line_item_count"] == 0
    supplier = md["supplier"]
    assert supplier is not None
    assert supplier["status"] == "propose"
    assert supplier["domain_api"] == SUPPLIER_CREATE_API
    assert supplier["payload"]["firmenname"] == "Neue Muehle GmbH"
    assert supplier["payload"]["lieferantennummer"] == "L-NEU-9"
    assert supplier["payload"]["strasse"] == "Hofweg 1"
    supplier_action = next(a for a in item["actions"] if a["key"] == "propose_supplier_create")
    assert supplier_action["label"] == "Lieferant anlegen"
    assert supplier_action["domain_api"] == SUPPLIER_CREATE_API
    assert supplier_action["booking"] is False
    assert all(a.get("booking") is False for a in item["actions"])

    articles = md["articles"]
    assert len(articles) == 1
    assert articles[0]["status"] == "blocked"
    assert articles[0]["code"] == "keine_positionszeilen_im_extrakt"
    assert any(u["code"] == "keine_positionszeilen_im_extrakt" for u in item["uncertainties"])
    assert any(u["code"] == "partner_nicht_gefunden" for u in item["uncertainties"])


def test_article_create_proposal_from_real_positions_and_image_slot():
    assert extract_line_items({}) == []
    assert extract_line_items({"ocr_blob": "Weizen 10 t"}) == []
    lines = extract_line_items({
        "positionen": [
            {"artikel": "Winterweizen A", "artikel_nr": "WW-1", "ean": "4006381333931", "menge": "10", "einheit": "t"},
        ],
    })
    assert len(lines) == 1
    assert lines[0]["name"] == "Winterweizen A"
    # ocr_invoice-Feldalias: wenn positionen mit artikel_name im Extrakt landen, nutzen.
    ocr_shaped = extract_line_items({
        "positionen": [{"artikel_name": "Musterartikel A", "menge": 10}],
    })
    assert len(ocr_shaped) == 1
    assert ocr_shaped[0]["name"] == "Musterartikel A"

    item = build_queue_item(
        entry={
            "id": "INBOX-POS",
            "status": "pending",
            "confidence": 0.85,
            "parsed_fields": {
                "supplier": "Bekannter Lieferant",
                "positionen": [
                    {"artikel": "Winterweizen A", "artikel_nr": "WW-1", "ean": "4006381333931"},
                ],
            },
        },
        partner_candidates=[{
            "partner_id": "bp-1",
            "partner_number": "L-1",
            "name": "Bekannter Lieferant",
            "matched_by": "name_search",
        }],
        article_candidates_by_index={0: []},
        nutzer=_EINKAUF_USER,
    )
    md = item["master_data_proposals"]
    assert md["supplier"] is None
    assert md["line_item_count"] == 1
    art = md["articles"][0]
    assert art["kind"] == "article_create"
    assert art["status"] == "propose"
    assert art["domain_api"] == ARTICLE_CREATE_API
    assert art["payload"]["name"] == "Winterweizen A"
    assert art["payload"]["article_number"] == "WW-1"
    assert art["image_research"]["status"] == "propose"
    assert art["image_research"]["executed"] is False
    assert art["image_research"]["api"] == ARTICLE_IMAGE_ENRICH_API
    assert any(a["key"] == "propose_article_create" for a in item["actions"])
    assert item["booking_allowed"] is False
    assert item["command"]["executable"] is False


def test_master_data_proposals_helper_is_non_executable():
    md = build_master_data_proposals(
        values={"supplierName": "X"},
        partner_uncertainties=[{"code": "partner_nicht_gefunden", "detail": "fehlt"}],
        parsed_fields={"supplier": "X"},
    )
    assert md["executable"] is False
    assert md["booking"] is False
    assert md["supplier"]["executable"] is False


def test_evaluate_can_open_maps_delivery_advice_to_goods_receipt():
    """Anlieferavis: gleiche Wareneingangs-Belegart wie Lieferschein; keine neue Rolle."""
    policy = classify_document({"document_type": "delivery_advice"}, None)
    assert policy["policy_id"] == "incoming-delivery-advice"
    assert policy["document_type"] == "delivery_advice"
    allowed, unclear, belegart = evaluate_can_open(policy, _EINKAUF_USER)
    assert allowed is True
    assert belegart == "goods_receipt"
    assert unclear == []

    item = build_queue_item(
        entry={
            "id": "INBOX-AVIS",
            "status": "pending",
            "confidence": 0.8,
            "parsed_fields": {"document_type": "anlieferavis"},
            "ocr_text": "Anlieferavis Avis Lieferavis",
        },
        nutzer=_EINKAUF_USER,
    )
    assert item["proposal"]["document_type"] == "delivery_advice"
    assert item["proposal"]["belegart"] == "goods_receipt"
    assert item["can_open"] is True
    assert item["actions"][0]["enabled"] is True
    assert "/einkauf/anlieferavis" in (item["actions"][0]["href"] or "")


def test_partner_match_exact_and_ambiguous():
    match, unclear = partner_match_from_candidates(
        {"supplierId": "L-10", "supplierName": "Nordkorn"},
        [{
            "partner_id": "bp-1",
            "partner_number": "L-10",
            "name": "Nordkorn AG",
            "matched_by": "partner_number",
        }],
    )
    assert match is not None
    assert match["status"] == "matched"
    assert match["partner_id"] == "bp-1"
    assert unclear == []

    ambiguous, unclear_many = partner_match_from_candidates(
        {"supplierName": "Nord"},
        [
            {"partner_id": "a", "partner_number": "1", "name": "Nord A"},
            {"partner_id": "b", "partner_number": "2", "name": "Nord B"},
        ],
    )
    assert ambiguous is not None
    assert ambiguous["status"] == "ambiguous"
    assert any(row["code"] == "partner_mehrdeutig" for row in unclear_many)


def test_demo_nwf_positions_match_article_and_partner_gap_keeps_supplier_propose():
    """DEMO-Kette ohne DB: NWF Position→Artikel-Match; GAP Propose-Payload fuer Create."""
    position = {
        "artikel_name": "Demo-Schrot Weizen",
        "artikel_nr": "DEMO-NWF-WHEAT",
        "menge": 10,
        "einheit": "t",
    }
    nwf = build_queue_item(
        entry={
            "id": "INBOX-DEMO-LF-NWF",
            "status": "pending",
            "confidence": 0.85,
            "ocr_text": "Nordwestdeutsche Futtermittel Rechnung DEMO",
            "parsed_fields": {
                "invoice_number": "DEMO-NWF-RE-001",
                "supplier": "Nordwestdeutsche Futtermittel GmbH & Co. KG",
                "supplier_id": "DEMO-LF-NWF",
                "domain": "purchase",
                "document_type": "supplier_invoice",
                "positionen": [position],
            },
        },
        partner_candidates=[],
        article_candidates_by_index={
            0: [{"article_number": "DEMO-NWF-WHEAT", "name": "Demo-Schrot Weizen"}],
        },
        nutzer=_EINKAUF_USER,
    )
    assert any(u["code"] == "partner_nicht_gefunden" for u in nwf["uncertainties"])
    supplier = nwf["master_data_proposals"]["supplier"]
    assert supplier["status"] == "propose"
    assert supplier["kind"] == "supplier_create"
    assert supplier["payload"]["lieferantennummer"] == "DEMO-LF-NWF"
    assert supplier["payload"]["firmenname"] == "Nordwestdeutsche Futtermittel GmbH & Co. KG"
    assert supplier["domain_api"] == SUPPLIER_CREATE_API
    articles = nwf["master_data_proposals"]["articles"]
    assert len(articles) == 1
    assert articles[0]["kind"] == "article_match"
    assert articles[0]["status"] == "matched"
    assert articles[0]["match"]["article_number"] == "DEMO-NWF-WHEAT"
    assert nwf["command"]["prefill"]["documentId"] == "INBOX-DEMO-LF-NWF"
    assert nwf["command"]["prefill"]["schema"] == PREFILL_SCHEMA
    assert nwf["command"]["prefill"]["storageKey"] == PREFILL_STORAGE_KEY
    assert nwf["command"]["prefill"]["maskConsumesPrefill"] is True
    assert nwf["command"]["prefill"]["booking"] is False
    assert nwf["command"]["executable"] is False
    assert "/einkauf/rechnung-eingang-erfassung" in (nwf["actions"][0]["href"] or "")

    gap = build_queue_item(
        entry={
            "id": "INBOX-DEMO-LF-GAP",
            "status": "pending",
            "confidence": 0.85,
            "parsed_fields": {
                "invoice_number": "DEMO-GAP-LS-001",
                "supplier": "Nordkorn Handelsgesellschaft Demo OHG",
                "supplier_id": "DEMO-LF-GAP",
                "domain": "purchase",
                "document_type": "supplier_invoice",
                "positionen": [position],
            },
        },
        partner_candidates=[],
        article_candidates_by_index={
            0: [{"article_number": "DEMO-NWF-WHEAT", "name": "Demo-Schrot Weizen"}],
        },
        nutzer=_EINKAUF_USER,
    )
    assert any(u["code"] == "partner_nicht_gefunden" for u in gap["uncertainties"])
    gap_supplier = gap["master_data_proposals"]["supplier"]
    assert gap_supplier["status"] == "propose"
    assert gap_supplier["payload"]["lieferantennummer"] == "DEMO-LF-GAP"
    assert gap_supplier["payload"]["firmenname"] == "Nordkorn Handelsgesellschaft Demo OHG"
    assert next(a for a in gap["actions"] if a["key"] == "propose_supplier_create")["label"] == (
        "Lieferant anlegen"
    )
    assert gap["master_data_proposals"]["articles"][0]["status"] == "matched"
    assert gap["command"]["prefill"]["documentId"] == "INBOX-DEMO-LF-GAP"
    assert gap["command"]["prefill"]["matchValues"]["supplierId"] == "DEMO-LF-GAP"
    assert gap["booking_allowed"] is False
