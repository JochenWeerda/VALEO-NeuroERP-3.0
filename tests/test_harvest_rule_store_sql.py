"""Actual append-only evidence and financial effects on the existing shared probe."""
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.infrastructure.models import (Tenant, User, Customer, Article, Warehouse,
    WeighingTicket, HarvestAcceptance, HarvestAcceptancePosition, QualityProtocol)
from app.api.v1.endpoints.harvest_acceptance import HarvestAcceptanceCreate
from app.api.v1.endpoints.harvest_rules import controlled_service
from modules.agrar.contracts.harvest_control_v1 import (CalculationApproveIn, ContextCommandIn,
    FinancialReleaseIn, MeasurementAttestIn, RuleBindIn, RuleCreateIn, RuleDecisionIn)
from modules.agrar.contracts.harvest_deductions_v1 import HarvestDeductionTermsV1
from modules.agrar.services.harvest_rule_store import HarvestRuleStore, digest
from app.services import studio_process_simulation as simulation

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]


@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield


@pytest.fixture
def case():
    engine = simulation._configured_probe()
    connection = engine.connect(); outer = connection.begin()
    db = Session(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)
    tenant = str(uuid4()); editor_id = str(uuid4()); reviewer_id = str(uuid4())
    db.add(Tenant(id=tenant, name="Harvest evidence fixture", domain=tenant + ".example.invalid")); db.flush()
    for subject, role in [(editor_id, "EINKAUF_BEARBEITEN"), (reviewer_id, "FINANCE_ADMIN")]:
        db.add(User(id=subject, tenant_id=tenant, username=subject, email=subject + "@example.invalid",
                    first_name="Synthetic", last_name="Evidence", roles=[role]))
    customer = Customer(id=str(uuid4()), tenant_id=tenant, customer_number="CONTROL", company_name="Synthetic customer")
    article = Article(id=str(uuid4()), tenant_id=tenant, article_number="CONTROL", name="Synthetic grain",
                      unit="kg", category="grain", sales_price=Decimal("220"), mehrwertsteuer_prozent=Decimal("7"))
    warehouse = Warehouse(id=str(uuid4()), tenant_id=tenant, warehouse_code="CONTROL", name="Synthetic warehouse",
                          address="Synthetic", city="Synthetic", postal_code="00000")
    ticket = WeighingTicket(id=str(uuid4()), tenant_id=tenant, ticket_number="CONTROL",
                           gross_weight=27000, tare_weight=2000, net_weight=25000,
                           moisture_pct=0, impurities_pct=3)
    db.add_all([customer, article, warehouse, ticket]); db.flush()
    editor = {"sub": editor_id, "roles": ["EINKAUF_BEARBEITEN"], "raw": {"iss": "urn:valeo:synthetic", "identity_type": "human"}}
    reviewer = {"sub": reviewer_id, "roles": ["FINANCE_ADMIN"], "raw": {"iss": "urn:valeo:synthetic", "identity_type": "human"}}
    svc, store = controlled_service(db, tenant, editor)
    review_svc, review_store = controlled_service(db, tenant, reviewer)
    item = svc.create_acceptance(HarvestAcceptanceCreate(acceptance_number="CONTROL", delivery_date=date(2026, 10, 15),
        customer_id=customer.id, article_id=article.id, warehouse_id=warehouse.id, weighing_ticket_id=ticket.id), editor_id)
    acceptance = db.get(HarvestAcceptance, item["id"])
    protocol = QualityProtocol(id=str(uuid4()), tenant_id=tenant, harvest_acceptance_id=acceptance.id,
        protocol_number="CONTROL", version=1, impurities_pct=Decimal("1.5"), moisture_pct=0,
        source_type="manual", source_file_content="synthetic measurement report", created_by=editor_id)
    db.add(protocol); db.flush(); acceptance.quality_protocol_id = protocol.id; db.commit()
    terms = HarvestDeductionTermsV1(customer_id=customer.id, article_id=article.id,
        valid_from=date(2026, 1, 1), valid_until=date.max, source_reference="synthetic terms",
        measurement_method="synthetic-lab", measurement_method_version="1", impurities_free_pct=Decimal("0"),
        quality_limit_pct=Decimal("2"))
    c = SimpleNamespace(db=db, tenant=tenant, svc=svc, store=store, review_svc=review_svc, review_store=review_store,
        acceptance=acceptance, protocol=protocol, article=article, ticket=ticket, terms=terms, editor=editor, reviewer=reviewer)
    try:
        yield c
    finally:
        db.close(); assert outer.is_active; outer.rollback(); connection.close()
        with engine.connect() as verify:
            assert verify.execute(text("SELECT count(*) FROM domain_shared.tenants WHERE id=:id"), {"id": tenant}).scalar_one() == 0


def ready(c, *, quality_limit=None):
    terms = c.terms if quality_limit is None else c.terms.model_copy(update={"quality_limit_pct": Decimal(quality_limit)})
    created = c.store.create_rule(RuleCreateIn(idempotency_key=uuid4(), rule_id="synthetic", expected_version=0, terms=terms))
    c.review_store.decide_rule(created["id"], RuleDecisionIn(idempotency_key=uuid4(), expected_hash=created["content_hash"],
        reason="Synthetic four-eyes verification", expires_at=datetime.now(UTC) + timedelta(days=1)))
    context = c.store.context(c.acceptance.id)
    c.store.bind_rule(c.acceptance.id, RuleBindIn(idempotency_key=uuid4(), expected_context_hash=context["context_hash"],
                                               rule_version_id=created["id"]))
    context = c.store.context(c.acceptance.id)
    c.store.attest(c.acceptance.id, MeasurementAttestIn(idempotency_key=uuid4(), expected_context_hash=context["context_hash"],
        protocol_id=c.protocol.id, expected_protocol_hash=context["protocol_hash"], measurement_method="synthetic-lab",
        measurement_method_version="1", source_reference="synthetic laboratory report"))
    return created


def calculate(c):
    return c.svc.calculate_settlement(c.acceptance.id, command=ContextCommandIn(idempotency_key=uuid4(),
        expected_context_hash=c.store.context(c.acceptance.id)["context_hash"]))


def approve(c, result, *, acknowledge=False):
    return c.review_store.approve_calculation(c.review_svc, c.acceptance.id, CalculationApproveIn(
        idempotency_key=uuid4(), expected_calculation_hash=result["calculation_hash"],
        expires_at=datetime.now(UTC) + timedelta(hours=1), reason="Synthetic financial review",
        acknowledge_quality_exception=acknowledge))


def test_real_rule_measurement_calculation_approval_and_repeat(case):
    c = case; ready(c)
    context = c.store.context(c.acceptance.id)
    body = ContextCommandIn(idempotency_key=uuid4(), expected_context_hash=context["context_hash"])
    result = c.svc.calculate_settlement(c.acceptance.id, command=body)
    assert result["total_net_amount_eur"] == 5417.5
    impurity = next(p for p in result["positions"] if p["position_number"] == 20)
    assert impurity["quantity_kg"] == 375 and impurity["quantity_pct"] == 1.5
    assert c.svc.calculate_settlement(c.acceptance.id, command=body) == result
    assert c.review_store.list_rules()["items"][0]["status"] == "approved"
    approve(c, result)
    proof = c.review_store._verified_calculation(c.review_svc, c.acceptance.id, result["calculation_hash"])[1]
    assert proof["state"]["protocol"]["id"] == c.protocol.id
    assert proof["state"]["attestation_id"]


@pytest.mark.parametrize("change", ["protocol", "ticket", "price", "position", "total"])
def test_changed_source_or_output_cannot_be_approved(case, change):
    c = case; ready(c); result = calculate(c)
    if change == "protocol": c.protocol.impurities_pct = Decimal("2")
    if change == "ticket":
        c.ticket.gross_weight = Decimal("26000")
        c.ticket.net_weight = Decimal("24000")
    if change == "price": c.article.sales_price = Decimal("230")
    if change == "position":
        p = c.db.query(HarvestAcceptancePosition).filter_by(harvest_acceptance_id=c.acceptance.id, position_number=20).one()
        p.quantity_kg = Decimal("0")
    if change == "total": c.acceptance.total_net_amount_eur = Decimal("1")
    c.db.flush()
    with pytest.raises((ConflictError, ValidationFailedError)):
        approve(c, result)
    assert c.store._latest("acceptance:" + c.acceptance.id, ["calculation.approved"]) is None


def test_author_cannot_self_approve_and_quality_exception_is_bound(case):
    c = case; ready(c, quality_limit="1"); result = calculate(c)
    with pytest.raises(ValidationFailedError): approve(c, result)
    approve(c, result, acknowledge=True)
    c.store.principal["roles"] = ["FINANCE_ADMIN"]
    with pytest.raises(ValidationFailedError, match="eigene"):
        c.store.approve_calculation(c.svc, c.acceptance.id, CalculationApproveIn(idempotency_key=uuid4(),
            expected_calculation_hash=result["calculation_hash"], expires_at=datetime.now(UTC)+timedelta(hours=1),
            reason="Synthetic self-approval", acknowledge_quality_exception=True))


def test_foreign_context_and_revoked_rule_are_blocked(case):
    c = case; rule = ready(c); result = calculate(c)
    other = HarvestRuleStore(c.db, str(uuid4()), c.editor)
    with pytest.raises(EntityNotFoundError): other.context(c.acceptance.id)
    with pytest.raises(EntityNotFoundError): other._rule(rule["id"])
    c.review_store.decide_rule(rule["id"], RuleDecisionIn(idempotency_key=uuid4(), expected_hash=rule["content_hash"],
        reason="Synthetic revocation"), revoke=True)
    with pytest.raises((ConflictError, ValidationFailedError)): approve(c, result)


def test_append_only_and_idempotency_key_conflict(case):
    c = case; body = RuleCreateIn(idempotency_key=uuid4(), rule_id="synthetic", expected_version=0, terms=c.terms)
    first = c.store.create_rule(body)
    assert c.store.create_rule(body) == first
    with pytest.raises(ConflictError):
        c.store.create_rule(body.model_copy(update={"rule_id": "changed"}))
    for operation in ["UPDATE domain_inventory.harvest_control_events SET actor='forged' WHERE tenant_id=:tenant",
                      "DELETE FROM domain_inventory.harvest_control_events WHERE tenant_id=:tenant"]:
        with pytest.raises(Exception, match="append-only"):
            with c.db.begin_nested(): c.db.execute(text(operation), {"tenant": c.tenant})


def test_failed_proof_insert_rolls_back_business_changes(case, monkeypatch):
    c = case; ready(c); original = c.db.execute
    def reject(statement, *args, **kwargs):
        if "INSERT INTO domain_inventory.harvest_control_events" in str(statement):
            raise RuntimeError("synthetic persistence failure")
        return original(statement, *args, **kwargs)
    monkeypatch.setattr(c.db, "execute", reject)
    with pytest.raises(RuntimeError, match="synthetic persistence failure"): calculate(c)
    c.db.refresh(c.acceptance)
    assert c.acceptance.total_net_amount_eur is None


def financial_ready(c):
    from app.finance.steuerschluessel import richte_skr03_ein
    from app.services.number_range_service import NumberRangeService
    richte_skr03_ein(c.db, c.tenant)
    NumberRangeService(c.db).configure(c.tenant, "self_billing", "GS", 1, 6)
    c.db.execute(text("INSERT INTO domain_shared.system_properties "
        "(id,tenant_id,property_key,property_value,property_type,category) "
        "VALUES (:id,:tenant,'agrar.self_billing.tax_code','8','string','agrar')"),
        {"id": str(uuid4()), "tenant": c.tenant})
    c.db.commit()
    ready(c); result = calculate(c); approve(c, result)
    return FinancialReleaseIn(idempotency_key=uuid4(), expected_calculation_hash=result["calculation_hash"])


def test_real_financial_release_is_atomic_and_replay_has_no_second_effect(case):
    c = case; body = financial_ready(c)
    result = c.svc.release_acceptance(c.acceptance.id, "final", True, True, c.editor["sub"], command=body)
    repeated = c.svc.release_acceptance(c.acceptance.id, "final", True, True, c.editor["sub"], command=body)
    assert result == repeated and result["invoice_id"] and result["stock_movement_id"]
    from app.infrastructure.models import StockMovement, JournalEntry, JournalEntryLine
    assert c.db.query(StockMovement).filter_by(tenant_id=c.tenant).count() == 1
    entries = c.db.query(JournalEntry).filter_by(tenant_id=c.tenant).all()
    assert len(entries) == 1
    lines = c.db.query(JournalEntryLine).filter_by(journal_entry_id=entries[0].id).all()
    assert sum(p.debit_amount for p in lines) == sum(p.credit_amount for p in lines)
    assert c.store._latest("acceptance:" + c.acceptance.id, ["release.completed"])


def test_financial_failure_rolls_back_stock_invoice_and_control_receipt(case, monkeypatch):
    c = case; body = financial_ready(c)
    from app.services.finance_transaction_service import FinanceTransactionService
    from app.infrastructure.models import StockMovement
    def fail(*args, **kwargs):
        raise RuntimeError("synthetic ledger failure")
    monkeypatch.setattr(FinanceTransactionService, "create", fail)
    with pytest.raises(RuntimeError, match="synthetic ledger failure"):
        c.svc.release_acceptance(c.acceptance.id, "final", True, True, c.editor["sub"], command=body)
    c.db.refresh(c.acceptance)
    assert c.acceptance.release_status == "draft" and c.acceptance.invoice_id is None
    assert c.db.query(StockMovement).filter_by(tenant_id=c.tenant).count() == 0
    assert c.store._latest("acceptance:" + c.acceptance.id, ["release.completed"]) is None


@pytest.mark.parametrize("hours", [2, 48])
def test_expired_financial_or_rule_approval_cannot_release(case, monkeypatch, hours):
    c = case; body = financial_ready(c)
    from modules.agrar.services import harvest_rule_store as module
    class Later(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.now(tz) + timedelta(hours=hours)
    monkeypatch.setattr(module, "datetime", Later)
    with pytest.raises(ValidationFailedError):
        c.svc.release_acceptance(c.acceptance.id, "final", True, True, c.editor["sub"], command=body)
    assert c.acceptance.invoice_id is None


def test_nonhuman_cannot_grant_approval_and_provider_identity_binds_replay(case):
    c = case; body = RuleCreateIn(idempotency_key=uuid4(), rule_id="synthetic", expected_version=0, terms=c.terms)
    result = c.store.create_rule(body)
    principal = dict(c.reviewer, raw={"iss": "urn:valeo:synthetic", "identity_type": "agent"})
    agent = HarvestRuleStore(c.db, c.tenant, principal)
    with pytest.raises(ValidationFailedError, match="menschliche"):
        agent.decide_rule(result["id"], RuleDecisionIn(idempotency_key=uuid4(), expected_hash=result["content_hash"],
            reason="Synthetic rejected agent approval", expires_at=datetime.now(UTC)+timedelta(hours=1)))
    other_issuer = HarvestRuleStore(c.db, c.tenant, dict(c.editor, raw={"iss": "urn:valeo:other", "identity_type": "human"}))
    with pytest.raises(ConflictError): other_issuer.create_rule(body)


def test_expected_version_and_stale_context_are_enforced(case):
    c = case; ready(c)
    with pytest.raises(ConflictError):
        c.store.create_rule(RuleCreateIn(idempotency_key=uuid4(), rule_id="synthetic", expected_version=0, terms=c.terms))
    before = c.store.context(c.acceptance.id)
    c.article.sales_price = Decimal("221"); c.db.flush()
    with pytest.raises(ConflictError):
        c.svc.calculate_settlement(c.acceptance.id, command=ContextCommandIn(
            idempotency_key=uuid4(), expected_context_hash=before["context_hash"]))


def test_idempotency_lock_is_tenant_scoped_and_visible_to_concurrent_sessions(case):
    c = case; key = "request:" + str(uuid4())
    c.store._lock(key)
    with simulation._configured_probe().connect() as other:
        assert other.execute(text("SELECT pg_try_advisory_xact_lock(hashtextextended(:key,0))"),
            {"key": "harvest-control:" + c.tenant + ":" + key}).scalar_one() is False
        assert other.execute(text("SELECT pg_try_advisory_xact_lock(hashtextextended(:key,0))"),
            {"key": "harvest-control:" + str(uuid4()) + ":" + key}).scalar_one() is True
