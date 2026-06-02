"""Unit-Tests für die Kunden↔BusinessPartner-Reconciliation (Phase 2A, DB-frei)."""

from __future__ import annotations

from app.services.kunden_merge import (
    CONFLICT,
    DUPLICATE,
    ORPHAN_BP,
    ORPHAN_KUNDE,
    STRONG,
    norm_id,
    _tokenset,
    build_bp_index,
    classify_kunde,
    reconcile_records,
)

BP1 = "11111111-1111-1111-1111-111111111111"
BP2 = "22222222-2222-2222-2222-222222222222"
BP4 = "44444444-4444-4444-4444-444444444444"


def _bp(partner_id, name_1, postal_code, **extra):
    return {"partner_id": partner_id, "name_1": name_1, "postal_code": postal_code, **extra}


def _kunde(kunden_nr, name1, plz, **extra):
    return {"kunden_nr": kunden_nr, "name1": name1, "plz": plz, "business_partner_id": None, **extra}


# ── Normalisierung ────────────────────────────────────────────────────────────


def test_norm_id_strips_format():
    assert norm_id("DE 123/456-7") == "de1234567"
    assert norm_id("") is None
    assert norm_id(None) is None


def test_tokenset_order_independent():
    assert _tokenset("Müller, Hans") == _tokenset("Hans Mueller")
    assert _tokenset("Hof Schmidt GmbH") == _tokenset("schmidt hof")


# ── Szenarien ─────────────────────────────────────────────────────────────────


def test_same_customer_in_all_silos_strong_backfill():
    bps = [_bp(BP1, "Hof Müller", "26123", farm_number="DE123", vat_id="DE111")]
    kunden = [_kunde("K1", "Müller Hof", "26123", landwirtschaftsamt_betriebsnummer="DE123")]
    crm = [{"source": "domain_crm.customers", "company_name": "Hof Müller", "tax_id": "DE111"}]
    rep = reconcile_records(kunden, bps, crm)
    c = rep["candidates"][0]
    assert c["match_class"] == STRONG
    assert c["proposed_business_partner_id"] == BP1
    assert c["match_reason"] == "betriebsnummer"
    assert c["recommended_action"] == "backfill_business_partner_id"
    assert rep["summary"]["backfillable"] == 1


def test_only_in_public_kunden_is_orphan():
    rep = reconcile_records([_kunde("K2", "Solo Bauer", "26200")], bps=[])
    c = rep["candidates"][0]
    assert c["match_class"] == ORPHAN_KUNDE
    assert c["proposed_business_partner_id"] is None
    assert c["recommended_action"] == "create_business_partner"


def test_only_in_bp_is_orphan_business_partner():
    bps = [_bp(BP2, "Nur BP GbR", "26300", farm_number="DE222")]
    rep = reconcile_records(kunden=[], bps=bps)
    assert rep["orphan_business_partner_ids"] == [BP2]
    assert rep["summary"]["counts"][ORPHAN_BP] == 1


def test_duplicate_same_name_plz():
    bps = []
    kunden = [_kunde("K3a", "Doppel Hof", "26400"), _kunde("K3b", "Doppel Hof", "26400")]
    rep = reconcile_records(kunden, bps)
    classes = {c["match_class"] for c in rep["candidates"]}
    assert classes == {DUPLICATE}
    assert all("same_name_plz" in c["conflict_fields"] for c in rep["candidates"])


def test_conflict_on_farm_number_mismatched_identity():
    # kunde teilt Betriebsnummer mit BP4, aber Name UND PLZ weichen klar ab → Konflikt
    bps = [_bp(BP4, "Ganz Anders AG", "99999", farm_number="DE999")]
    kunden = [_kunde("K4", "Hof Schmidt", "26500", landwirtschaftsamt_betriebsnummer="DE999")]
    rep = reconcile_records(kunden, bps)
    c = rep["candidates"][0]
    assert c["match_class"] == CONFLICT
    assert "name" in c["conflict_fields"]
    assert c["recommended_action"] == "manual_review"


def test_crm_record_matches_bp_by_tax_becomes_projection():
    bps = [_bp(BP1, "Hof Müller", "26123", vat_id="DE811111111")]
    crm = [{
        "source": "domain_crm.customers", "crm_id": "c1", "name": "Hof Mueller",
        "plz": "26123", "tax": "DE 811 111 111", "business_partner_id": None, "customer_number": None,
    }]
    rep = reconcile_records(kunden=[], bps=bps, crm=crm)
    cc = rep["crm_candidates"][0]
    assert cc["match_class"] == STRONG
    assert cc["match_reason"] == "vat_tax"
    assert cc["proposed_business_partner_id"] == BP1
    assert cc["recommended_action"] == "project_to_business_partner"
    # BP ist durch CRM referenziert → kein Orphan
    assert rep["orphan_business_partner_ids"] == []


def test_existing_link_marked_linked_not_backfill():
    bps = [_bp(BP1, "Hof Müller", "26123", farm_number="DE123")]
    kunde = _kunde("K5", "Hof Müller", "26123", landwirtschaftsamt_betriebsnummer="DE123")
    kunde["business_partner_id"] = BP1
    c = classify_kunde(kunde, build_bp_index(bps))
    assert c.existing_business_partner_id == BP1
    assert c.recommended_action == "linked"
