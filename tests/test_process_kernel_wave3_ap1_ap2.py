"""
Wave-3 Contract-Tests: AP1 Maskenklassifizierung + AP2 Audit-Evidence-Modell
"""
from __future__ import annotations

from app.core.mask_classification import (
    MaskClass,
    MaskDomain,
    MaskClassification,
    MaskRegistry,
    ExplainabilityRequirement,
    build_mask_registry,
)
from app.core.audit_evidence import (
    AuditEvidenceEntry,
    EvidenceReference,
    EvidenceSourceSystem,
    EvidenceType,
    DocumentEvidencePolicy,
    build_default_evidence_policy,
)


# ---------------------------------------------------------------------------
# AP1: UI-Maskenklassifizierung
# ---------------------------------------------------------------------------

def test_mask_registry_has_class_a_masks():
    registry = build_mask_registry()
    class_a = registry.get_by_class(MaskClass.A)
    assert len(class_a) > 0


def test_ap_invoice_form_is_class_a_with_wave1_contract():
    registry = build_mask_registry()
    mask = registry.get("finance/ap-invoice-form")
    assert mask is not None
    assert mask.mask_class == MaskClass.A
    assert mask.wave1_contract is True
    assert mask.requires_approval_ui is True
    assert mask.gobd_relevant is True


def test_class_a_masks_require_explainability():
    registry = build_mask_registry()
    class_a = registry.get_by_class(MaskClass.A)
    non_required = [m for m in class_a if m.explainability != ExplainabilityRequirement.REQUIRED]
    assert non_required == [], f"Class-A masks without REQUIRED explainability: {[m.mask_id for m in non_required]}"


def test_mask_registry_get_by_domain_finance():
    registry = build_mask_registry()
    finance_masks = registry.get_by_domain(MaskDomain.FINANCE)
    assert len(finance_masks) >= 5


def test_mask_registry_gap_report_all_a_have_contract():
    registry = build_mask_registry()
    gaps = registry.class_a_without_wave1_contract()
    # All class-A masks in the registry should have wave1_contract=True
    assert gaps == [], f"Class-A masks missing Wave-1 contract: {[m.mask_id for m in gaps]}"


def test_mask_classification_schema_version():
    mask = MaskClassification(
        mask_id="test/mask",
        route="/test",
        label="Test",
        domain=MaskDomain.FINANCE,
        mask_class=MaskClass.C,
    )
    assert mask.schema_version == 1


def test_mask_registry_schema_version():
    registry = MaskRegistry()
    assert registry.schema_version == 1


def test_mask_registry_contains_agrar_masks():
    registry = build_mask_registry()
    agrar = registry.get_by_domain(MaskDomain.AGRAR)
    assert any(m.mask_id == "annahme/abrechnung" for m in agrar)
    assert any(m.mask_id == "annahme/qualitaets-check" for m in agrar)


# ---------------------------------------------------------------------------
# AP2: Audit-Evidence-Modell
# ---------------------------------------------------------------------------

def test_evidence_reference_schema_version():
    ref = EvidenceReference(
        evidence_id="ev-1",
        source_system=EvidenceSourceSystem.PAPERLESS_NGX,
        evidence_type=EvidenceType.INVOICE_SCAN,
        external_id="doc-42",
    )
    assert ref.schema_version == 1
    assert ref.verified is False


def test_audit_evidence_entry_add_evidence_updates_gobd():
    entry = AuditEvidenceEntry(
        audit_entry_id="ae-1",
        tenant_id="t1",
        aggregate_type="ap_invoice",
        aggregate_id="inv-1",
        action="approved",
    )
    assert entry.gobd_compliant is False

    ref = EvidenceReference(
        evidence_id="ev-1",
        source_system=EvidenceSourceSystem.PAPERLESS_NGX,
        evidence_type=EvidenceType.INVOICE_SCAN,
        external_id="doc-42",
        verified=True,
    )
    entry.add_evidence(ref)
    assert entry.gobd_compliant is True
    assert len(entry.evidence_refs) == 1


def test_audit_evidence_entry_primary_evidence_prefers_verified():
    entry = AuditEvidenceEntry(
        audit_entry_id="ae-2",
        tenant_id="t1",
        aggregate_type="ap_invoice",
        aggregate_id="inv-2",
        action="posted",
    )
    unverified = EvidenceReference(
        evidence_id="ev-1",
        source_system=EvidenceSourceSystem.UPLOAD,
        evidence_type=EvidenceType.INVOICE_SCAN,
        external_id="doc-1",
        verified=False,
    )
    verified = EvidenceReference(
        evidence_id="ev-2",
        source_system=EvidenceSourceSystem.PAPERLESS_NGX,
        evidence_type=EvidenceType.INVOICE_SCAN,
        external_id="doc-2",
        verified=True,
    )
    entry.evidence_refs = [unverified, verified]
    primary = entry.primary_evidence()
    assert primary is not None
    assert primary.evidence_id == "ev-2"


def test_document_evidence_policy_requires_evidence_for_ap_invoice_approved():
    policy = build_default_evidence_policy("t1")
    assert policy.requires_evidence("ap_invoice", "approved") is True
    assert policy.requires_evidence("ap_invoice", "created") is False


def test_document_evidence_policy_gobd_retention_check_default():
    policy = build_default_evidence_policy("t1")
    assert policy.gobd_retention_check is True
    assert policy.ocr_min_confidence == 0.75


def test_document_evidence_policy_schema_version():
    policy = build_default_evidence_policy("t1")
    assert policy.schema_version == 1
