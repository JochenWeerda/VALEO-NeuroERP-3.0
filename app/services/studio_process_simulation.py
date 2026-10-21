"""Real domain-service simulation on the shared probe, always rolled back.

No scenario descriptions are accepted as proof. No user-supplied handler,
URL, SQL, Python or external delivery is executed.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

_REQUIRED = ("receipt", "quality", "self_billing", "tax", "ledger", "stock",
             "tenancy", "permissions", "reversal", "correction", "idempotency", "numbering", "rollback")


def simulation_artifact_hash():
    root = Path(__file__).resolve().parents[2]
    files = ["app/services/studio_process_simulation.py", "app/services/harvest_acceptance_service.py",
             "app/services/finance_transaction_service.py", "app/core/studio_release.py",
             "modules/agrar/services/harvest_calculator.py", "modules/agrar/services/self_billing_service.py",
             "modules/agrar/contracts/harvest_deductions_v1.py",
             "modules/agrar/contracts/harvest_control_v1.py", "modules/agrar/services/harvest_rule_store.py",
             "app/auth/finance_roles.py", "config/studio_data_sources.yaml", "app/core/mcp_tool_contracts.py",
             "app/finance/steuerschluessel.py", "app/services/finance_eingangsrechnung_buchung.py",
             "modules/agrar/repositories/self_billing_repo.py", "modules/agrar/services/partie_service.py",
             "modules/agrar/services/tax_profile_service.py", "modules/agrar/services/weighing_domain.py",
             "app/api/v1/endpoints/studio_drafts.py", "app/services/studio_draft_store.py",
             "app/api/v1/endpoints/studio_native_import.py", "app/services/studio_native_import.py",
             "app/core/document_screen_versions.py", "config/document_screen_versions.json",
             "app/core/screen_definitions.py", "app/core/screen_definitions_beleg.py",
             "app/core/belegkommandos.py", "app/core/belegvertrag.py",
             "app/services/studio_validation.py", "app/services/number_range_service.py", "config/mcp_erp_tools.yaml",
             "app/core/agent_tool_contract_manifest.py", "app/core/mcp_rest_binding.py",
             "app/api/v1/schemas/advisory_input.py", "app/core/screen_definitions_studio_history.py",
             "app/services/studio_semantic.py", "app/services/studio_semantic_model.py",
             "app/services/llm_gateway.py", "app/services/studio_migration.py",
             "app/services/studio_migration_store.py", "app/api/v1/schemas/studio_migration.py",
             "app/services/mcp_studio_plans.py"]
    digest = hashlib.sha256()
    for name in files:
        path = root / name
        if not path.is_file():
            raise RuntimeError("simulation_artifact_missing")
        digest.update(name.encode()); digest.update(path.read_bytes())
    return digest.hexdigest()


@lru_cache(maxsize=1)
def _probe_engine(url):
    return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 5})


def _configured_probe():
    from app.core.config import settings
    url = os.environ.get("TEST_DATABASE_URL") or (os.environ.get("DATABASE_URL") if os.environ.get("CI", "").lower() == "true" else None)
    if not url and settings.APP_ENV == "development":
        from dotenv import dotenv_values
        url = dotenv_values(Path(__file__).resolve().parents[2] / ".env").get("TEST_DATABASE_URL")
    if not url: raise RuntimeError("simulation_probe_not_configured")
    parsed = make_url(url)
    development = make_url(str(settings.DATABASE_URL))
    ci = os.environ.get("CI", "").lower() == "true"
    if not ci and (parsed.database != "valeo_probe" or parsed.database == development.database):
        raise RuntimeError("simulation_database_not_authorized")
    if ci and parsed != make_url(os.environ.get("DATABASE_URL", "")):
        raise RuntimeError("simulation_ci_database_not_authorized")
    return _probe_engine(url)


def _grain_chain(db, seed, checks):
    from app.infrastructure.models import Tenant, User, Customer, Article, Warehouse, WeighingTicket, Account, StockMovement, JournalEntry, JournalEntryLine
    from app.services.harvest_acceptance_service import HarvestAcceptanceService
    from app.api.v1.endpoints.harvest_acceptance import HarvestAcceptanceCreate
    from modules.agrar.services.weighing_domain import validate_and_compute_weights
    from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl
    from modules.agrar.services.self_billing_service import issue_invoice
    from app.services.finance_transaction_service import FinanceTransactionService
    from app.core.exceptions import EntityNotFoundError, ValidationFailedError, ConflictError
    from app.auth.finance_roles import finance_write
    from fastapi import HTTPException

    suffix = seed.replace("-", "")[:16]
    db.add(Tenant(id=seed, name="Simulation", domain=f"{suffix}.simulation.invalid")); db.flush()
    actor = User(id=str(uuid4()), tenant_id=seed, username=f"sim-{suffix}", email=f"sim-{suffix}@example.invalid",
                 first_name="Simulation", last_name="Fixture", roles=["FINANCE_BEARBEITEN"])
    customer = Customer(id=str(uuid4()), tenant_id=seed, customer_number=f"SIM-{suffix}", company_name="Simulation customer")
    article = Article(id=str(uuid4()), tenant_id=seed, article_number=f"SIM-{suffix}", name="Simulation grain", unit="kg",
                      category="grain", sales_price=Decimal("200"), mehrwertsteuer_prozent=Decimal("7"))
    warehouse = Warehouse(id=str(uuid4()), tenant_id=seed, warehouse_code=f"S{suffix}", name="Simulation warehouse",
                          address="Simulation", city="Simulation", postal_code="00000")
    db.add_all([actor, customer, article, warehouse]); db.flush()
    from app.finance.steuerschluessel import richte_skr03_ein
    richte_skr03_ein(db, seed)
    from app.services.number_range_service import NumberRangeService
    NumberRangeService(db).configure(seed, "self_billing", "GS", 1, 6)
    db.execute(text("INSERT INTO domain_shared.system_properties "
                    "(id,tenant_id,property_key,property_value,property_type,category) "
                    "VALUES (:id,:tenant,'agrar.self_billing.tax_code','8','string','agrar')"),
               {"id": str(uuid4()), "tenant": seed})
    net = validate_and_compute_weights(12000, 2000, None)
    ticket = WeighingTicket(id=str(uuid4()), tenant_id=seed, ticket_number=f"SIM-{suffix}", gross_weight=12000,
                           tare_weight=2000, net_weight=net, moisture_pct=14, impurities_pct=3)
    db.add(ticket); db.flush()
    db.refresh(ticket); db.refresh(article)
    checks["receipt"] = net == 10000
    from modules.agrar.contracts.harvest_deductions_v1 import HarvestDeductionTermsV1
    from modules.agrar.contracts.harvest_control_v1 import (RuleCreateIn, RuleDecisionIn, RuleBindIn,
        MeasurementAttestIn, ContextCommandIn, CalculationApproveIn, FinancialReleaseIn)
    from app.api.v1.endpoints.harvest_rules import controlled_service
    from app.infrastructure.models import QualityProtocol, HarvestAcceptance
    reviewer = User(id=str(uuid4()), tenant_id=seed, username=f"review-{suffix}",
                    email=f"review-{suffix}@example.invalid", first_name="Synthetic", last_name="Reviewer", roles=["FINANCE_ADMIN"])
    db.add(reviewer); db.flush()
    issuer = {"iss": "urn:valeo:synthetic-grain-simulation", "identity_type": "human"}
    editor_principal = {"sub": actor.id, "roles": ["FINANCE_BEARBEITEN"], "raw": issuer}
    review_principal = {"sub": reviewer.id, "roles": ["FINANCE_ADMIN"], "raw": issuer}
    svc, control = controlled_service(db, seed, editor_principal)
    review_svc, review_control = controlled_service(db, seed, review_principal)
    rule_record = control.create_rule(RuleCreateIn(idempotency_key=uuid4(), rule_id="grain.v1.synthetic-terms",
        expected_version=0, terms=HarvestDeductionTermsV1(customer_id=customer.id, article_id=article.id,
            valid_from=date(2026, 1, 1), valid_until=date.max, source_reference="Studio isolated synthetic fixture",
            measurement_method="synthetic-laboratory", measurement_method_version="1",
            impurities_free_pct=Decimal("2"), quality_limit_pct=Decimal("2"))))
    review_control.decide_rule(rule_record["id"], RuleDecisionIn(idempotency_key=uuid4(),
        expected_hash=rule_record["content_hash"], reason="Synthetic four-eyes rule verification",
        expires_at=datetime.now(UTC)+timedelta(days=1)))

    def controlled_calculation(acceptance_id):
        acceptance = db.get(HarvestAcceptance, acceptance_id)
        protocol = QualityProtocol(id=str(uuid4()), tenant_id=seed, harvest_acceptance_id=acceptance_id,
            protocol_number="SIM-"+acceptance_id[:12], version=1, impurities_pct=3, moisture_pct=14,
            source_type="manual", source_file_content="Synthetic laboratory fixture", created_by=actor.id)
        db.add(protocol); db.flush(); acceptance.quality_protocol_id=protocol.id; db.commit()
        context = control.context(acceptance_id)
        control.bind_rule(acceptance_id, RuleBindIn(idempotency_key=uuid4(),
            expected_context_hash=context["context_hash"], rule_version_id=rule_record["id"]))
        context = control.context(acceptance_id)
        control.attest(acceptance_id, MeasurementAttestIn(idempotency_key=uuid4(),
            expected_context_hash=context["context_hash"], protocol_id=protocol.id,
            expected_protocol_hash=context["protocol_hash"], measurement_method="synthetic-laboratory",
            measurement_method_version="1", source_reference="Synthetic laboratory fixture"))
        result = svc.calculate_settlement(acceptance_id, command=ContextCommandIn(idempotency_key=uuid4(),
            expected_context_hash=control.context(acceptance_id)["context_hash"]))
        review_control.approve_calculation(review_svc, acceptance_id, CalculationApproveIn(idempotency_key=uuid4(),
            expected_calculation_hash=result["calculation_hash"], expires_at=datetime.now(UTC)+timedelta(hours=1),
            reason="Synthetic financial review including quality exception", acknowledge_quality_exception=True))
        return result

    item = svc.create_acceptance(HarvestAcceptanceCreate(acceptance_number=f"SIM-{suffix}", delivery_date=date(2026, 1, 15),
             customer_id=customer.id, article_id=article.id, warehouse_id=warehouse.id, weighing_ticket_id=ticket.id), actor.id)
    acceptance_id = str(item["id"])
    calculation = controlled_calculation(acceptance_id)
    from app.infrastructure.models import HarvestAcceptance
    acceptance = db.get(HarvestAcceptance, acceptance_id)
    impurity = next(p for p in calculation["positions"] if p["position_number"] == 20)
    checks["quality"] = (acceptance.total_net_amount_eur > 0 and impurity["quantity_kg"] == 100
                         and rule_record["content_hash"] in impurity["calculation_formula"]
                         and any("Qualitaetsgrenze" in warning for warning in calculation["warnings"]))
    release_body = FinancialReleaseIn(idempotency_key=uuid4(), expected_calculation_hash=calculation["calculation_hash"])
    svc.release_acceptance(acceptance_id, "final", True, True, actor.id, command=release_body)
    acceptance = db.get(HarvestAcceptance, acceptance_id)
    invoice = SelfBillingRepositoryImpl(db).get_invoice_by_id(acceptance.invoice_id)
    checks["self_billing"] = invoice is not None and invoice.harvest_acceptance_id == acceptance_id
    issued = issue_invoice(SelfBillingRepositoryImpl(db), invoice.id, actor.id)
    checks["self_billing"] &= issued.status == "issued"
    checks["tax"] = invoice.total_vat_amount_eur == (invoice.total_net_amount_eur * Decimal("0.07")).quantize(Decimal("0.01"))
    stock = db.get(StockMovement, acceptance.stock_movement_id)
    checks["stock"] = stock.quantity == Decimal("10000") and stock.new_stock - stock.previous_stock == stock.quantity
    fin = FinanceTransactionService(db, seed)
    journal = db.query(JournalEntry).filter_by(tenant_id=seed, reference=invoice.invoice_number).one_or_none()
    checks["ledger"] = journal is not None
    if journal is not None:
        fin.post(journal.id, actor.id)
        lines = db.query(JournalEntryLine).filter_by(journal_entry_id=journal.id).all()
        checks["ledger"] &= journal.status == "posted" and sum(line.debit_amount for line in lines) == sum(line.credit_amount for line in lines)
        tax_id = fin.account_id_for_number("1571")
        checks["tax"] &= any(line.account_id == tax_id and line.debit_amount == invoice.total_vat_amount_eur for line in lines)
        original, reverse = fin.reverse(journal.id, "Simulation reversal")
        checks["reversal"] = original.status == "reversed" and reverse.status == "posted" and reverse.reversed_entry_id == original.id
    try:
        HarvestAcceptanceService(db, str(uuid4())).get_acceptance(acceptance_id)
        checks["tenancy"] = False
    except EntityNotFoundError:
        checks["tenancy"] = True
    try:
        finance_write(user={"sub": "simulation-reader", "roles": ["EINKAUF_LESEN"]})
        checks["permissions"] = False
    except HTTPException as error:
        checks["permissions"] = error.status_code == 403
    finance_write(user={"sub": "simulation-bookkeeper", "roles": ["FINANCE_BEARBEITEN"]})
    # Negative correction runs in its own savepoint, so even a bad command is contained.
    nested = db.begin_nested()
    try:
        svc.cancel(acceptance_id, "Simulation immutable-document check")
        checks["correction"] = False
    except (ValidationFailedError, ConflictError):
        checks["correction"] = True
    except Exception:
        checks["correction"] = False
    finally:
        if nested.is_active:
            nested.rollback()
    before = db.query(StockMovement).filter_by(tenant_id=seed).count()
    nested = db.begin_nested()
    try:
        svc.release_acceptance(acceptance_id, "final", True, True, actor.id, command=release_body)
        checks["idempotency"] = (db.query(StockMovement).filter_by(tenant_id=seed).count() == before
                                   and db.get(HarvestAcceptance, acceptance_id).invoice_id == invoice.id)
    except (ValidationFailedError, ConflictError):
        checks["idempotency"] = True
    finally:
        if nested.is_active:
            nested.rollback()
    # A second real receipt in the same tenant/day catches timestamp-prefix collisions.
    second_ticket = WeighingTicket(id=str(uuid4()), tenant_id=seed, ticket_number=f"SB-{suffix}",
                                  gross_weight=12000, tare_weight=2000, net_weight=net,
                                  moisture_pct=14, impurities_pct=3)
    db.add(second_ticket); db.flush(); db.refresh(second_ticket)
    second = svc.create_acceptance(HarvestAcceptanceCreate(acceptance_number=f"SB-{suffix}",
             delivery_date=date(2026, 1, 15), customer_id=customer.id, article_id=article.id,
             warehouse_id=warehouse.id, weighing_ticket_id=second_ticket.id), actor.id)
    second_calculation = controlled_calculation(second["id"])
    svc.release_acceptance(second["id"], "final", True, True, actor.id, command=FinancialReleaseIn(
        idempotency_key=uuid4(), expected_calculation_hash=second_calculation["calculation_hash"]))
    second_acceptance = db.get(HarvestAcceptance, second["id"])
    second_invoice = SelfBillingRepositoryImpl(db).get_invoice_by_id(second_acceptance.invoice_id)
    checks["numbering"] = (invoice.id != second_invoice.id and invoice.invoice_number != second_invoice.invoice_number
                            and len(second_invoice.invoice_number) <= 10
                            and db.query(JournalEntry).filter_by(tenant_id=seed, reference=second_invoice.invoice_number).count() == 1)


def simulate_process(definition, *, engine=None):
    """Return complete positive evidence only when every real invariant passed."""
    from app.core.studio_release import SimulationBusy
    stamp = simulation_artifact_hash()
    requested = definition.get("processSimulation") or {}
    profile = requested.get("profile") or ("grain.v1" if definition.get("domain") == "agrar" else None)
    checks = {name: False for name in _REQUIRED}
    report = {"profile": profile, "artifact_hash": stamp, "checks": checks, "passed": False,
              "business_effect": "none", "external_effect": "none"}
    if profile != "grain.v1" or set(requested) - {"profile"}:
        report["error"] = "simulation_profile_not_supported"
        return report
    if stamp != _LOADED_ARTIFACT_HASH:
        report["error"] = "simulation_runtime_requires_restart"
        report["failed_checks"] = list(_REQUIRED)
        return report
    seed = str(uuid4())
    try:
        engine = engine or _configured_probe()
        if engine.url.database != "valeo_probe" and os.environ.get("CI", "").lower() != "true":
            raise RuntimeError("simulation_database_not_authorized")
        with engine.connect() as connection:
            outer = connection.begin()
            if not connection.execute(text("SELECT pg_try_advisory_xact_lock(hashtextextended('valeo.studio.simulation.grain.v1', 0))")).scalar_one():
                outer.rollback()
                raise SimulationBusy("shared_simulation_busy")
            db = Session(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)
            try:
                _grain_chain(db, seed, checks)
                if not outer.is_active: raise RuntimeError("simulation_transaction_escaped")
            finally:
                db.close()
                if outer.is_active: outer.rollback()
        with engine.connect() as verify:
            checks["rollback"] = verify.execute(text("SELECT count(*) FROM domain_shared.tenants WHERE id=:id"), {"id": seed}).scalar_one() == 0
    except SimulationBusy:
        raise
    except Exception as error:
        report["error"] = type(error).__name__
        import traceback
        frame = traceback.extract_tb(error.__traceback__)[-1]
        report["error_location"] = f"{Path(frame.filename).name}:{frame.lineno}:{frame.name}"
        if engine is not None:
            with engine.connect() as verify:
                checks["rollback"] = verify.execute(text("SELECT count(*) FROM domain_shared.tenants WHERE id=:id"), {"id": seed}).scalar_one() == 0
    report["passed"] = all(checks.values()) and simulation_artifact_hash() == stamp
    report["failed_checks"] = [name for name, passed in checks.items() if not passed]
    return report


# Runtime source changes invalidate evidence until the process loads a coherent release.
_LOADED_ARTIFACT_HASH = simulation_artifact_hash()
