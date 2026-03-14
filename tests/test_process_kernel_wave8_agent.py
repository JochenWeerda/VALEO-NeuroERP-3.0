"""Wave 8 Paket B - Multi-Kontext-Agent und Betriebskennzahlen-Benchmark Tests."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.betriebskennzahlen import (
    DEFAULT_KZ_KATALOG,
    BenchmarkReport,
    BetriebsKennzahl,
    KennzahlEinheit,
)
from app.core.multi_context_agent import (
    AgentContext,
    AgentContextStatus,
    AgentContextStore,
    MultiContextAgentManifest,
    tenantbewusst_dispatch,
)
from app.core.tenant_isolation_guard import TenantIsolationGuard, VerbundSharingPolicy


def make_context(
    tenant_id: str = "tenant-a",
    expires_delta: timedelta = timedelta(hours=1),
    roles: list[str] | None = None,
    status: AgentContextStatus = AgentContextStatus.AKTIV,
) -> AgentContext:
    now = datetime.utcnow()
    return AgentContext(
        context_id=str(uuid.uuid4()),
        agent_id="agent-001",
        tenant_id=tenant_id,
        delegated_roles=roles or ["agent", "reader"],
        context_expires_at=now + expires_delta,
        erstellt_am=now,
        status=status,
    )


def make_kennzahl(
    tenant_id: str,
    kz_name: str = "umsatz_eur_t",
    wert: float = 100.0,
    periode: str = "2025",
    einheit: KennzahlEinheit = KennzahlEinheit.EUR_JE_T,
) -> BetriebsKennzahl:
    from datetime import date

    return BetriebsKennzahl(
        kz_id=str(uuid.uuid4()),
        kz_name=kz_name,
        einheit=einheit,
        wert=wert,
        tenant_id=tenant_id,
        periode=periode,
        berechnet_am=date.today(),
    )


def test_agent_context_ist_aktiv():
    ctx = make_context(expires_delta=timedelta(hours=1))
    assert ctx.ist_aktiv() is True


def test_agent_context_abgelaufen():
    ctx = make_context(expires_delta=timedelta(hours=-1))
    assert ctx.ist_aktiv() is False


def test_agent_context_widerrufen():
    ctx = make_context(expires_delta=timedelta(hours=1))
    ctx.widerrufen()
    assert ctx.ist_aktiv() is False
    assert ctx.status == AgentContextStatus.WIDERRUFEN


def test_agent_context_verbleibende_sekunden_positiv():
    ctx = make_context(expires_delta=timedelta(hours=1))
    assert ctx.verbleibende_sekunden() > 0


def test_agent_context_verbleibende_sekunden_null():
    ctx = make_context(expires_delta=timedelta(hours=-1))
    assert ctx.verbleibende_sekunden() == 0.0


def test_context_store_get_active_gueltig():
    store = AgentContextStore()
    ctx = make_context(expires_delta=timedelta(hours=1))
    store.add(ctx)
    assert store.get_active(ctx.context_id) is not None


def test_context_store_get_active_abgelaufen():
    store = AgentContextStore()
    ctx = make_context(expires_delta=timedelta(hours=-1))
    store.add(ctx)
    assert store.get_active(ctx.context_id) is None


def test_context_store_bereinige_abgelaufene():
    store = AgentContextStore()
    expired = make_context(expires_delta=timedelta(hours=-1))
    active = make_context(expires_delta=timedelta(hours=1))
    store.add(expired)
    store.add(active)
    count = store.bereinige_abgelaufene()
    assert count == 1
    assert store.kontexte[expired.context_id].status == AgentContextStatus.ABGELAUFEN
    assert store.kontexte[active.context_id].status == AgentContextStatus.AKTIV


def test_dispatch_accepted():
    ctx = make_context(tenant_id="tenant-a", roles=["agent"])
    result = tenantbewusst_dispatch(
        ctx,
        "FreigebeRechnung",
        "tenant-a",
        resource_type="ap_invoice",
        issuer_role="agent",
        isolation_guard=TenantIsolationGuard(),
    )
    assert result.entscheidung == "ACCEPTED"


def test_dispatch_kontext_abgelaufen():
    ctx = make_context(expires_delta=timedelta(hours=-1))
    result = tenantbewusst_dispatch(
        ctx,
        "FreigebeRechnung",
        ctx.tenant_id,
        resource_type="ap_invoice",
        issuer_role="agent",
        isolation_guard=TenantIsolationGuard(),
    )
    assert result.entscheidung == "DENIED_KONTEXT_ABGELAUFEN"


def test_dispatch_tenant_isolation():
    ctx = make_context(tenant_id="tenant-a", roles=["agent"])
    result = tenantbewusst_dispatch(
        ctx,
        "FreigebeRechnung",
        "tenant-b",
        resource_type="ap_invoice",
        issuer_role="agent",
        isolation_guard=TenantIsolationGuard(),
    )
    assert result.entscheidung == "DENIED_TENANT_ISOLATION"


def test_dispatch_rolle_fehlt():
    ctx = make_context(tenant_id="tenant-a", roles=["reader"])
    result = tenantbewusst_dispatch(
        ctx,
        "FreigebeRechnung",
        "tenant-a",
        resource_type="ap_invoice",
        issuer_role="approver",
        isolation_guard=TenantIsolationGuard(),
    )
    assert result.entscheidung == "REJECTED"


def test_dispatch_verbund_allowed():
    ctx = make_context(tenant_id="tenant-a", roles=["agent"])
    guard = TenantIsolationGuard(
        verbund_policies=[
            VerbundSharingPolicy(
                verbund_id="verbund-1",
                mitglieder_tenant_ids=["tenant-a", "tenant-b"],
                erlaubte_ressourcentypen=["feldbuch_schlag"],
            )
        ]
    )
    result = tenantbewusst_dispatch(
        ctx,
        "LeseSchlag",
        "tenant-b",
        resource_type="feldbuch_schlag",
        issuer_role="agent",
        isolation_guard=guard,
    )
    assert result.entscheidung == "ACCEPTED_VERBUND"


def test_dispatch_schema_version():
    ctx = make_context(tenant_id="tenant-a", roles=["agent"])
    result = tenantbewusst_dispatch(
        ctx,
        "TestCommand",
        "tenant-a",
        resource_type="ap_invoice",
        issuer_role="agent",
        isolation_guard=TenantIsolationGuard(),
    )
    assert result.schema_version == 1


def test_multi_context_manifest_schema_version():
    manifest = MultiContextAgentManifest(
        manifest_id=str(uuid.uuid4()),
        tenant_id="tenant-a",
        erlaubte_command_names=["FreigebeRechnung"],
        gesperrte_command_names=["AusfuehreZahlung"],
    )
    assert manifest.schema_version == 1


def test_kennzahl_schema_version():
    kz = make_kennzahl("tenant-a")
    assert kz.schema_version == 1


def test_benchmark_report_build_leer():
    report = BenchmarkReport.build(
        verbund_id="verbund-1",
        periode="2025",
        kennzahlen_je_tenant={},
    )
    assert report.verbund_id == "verbund-1"
    assert len(report.gruppen) == 1
    assert report.gruppen[0].kennzahlen == []


def test_benchmark_report_build_ein_tenant():
    kz = make_kennzahl("tenant-a", wert=200.0, periode="2025")
    report = BenchmarkReport.build(
        verbund_id="verbund-1",
        periode="2025",
        kennzahlen_je_tenant={"tenant-a": [kz]},
    )
    bkz = report.gruppen[0].kennzahlen[0]
    assert bkz.n_teilnehmer == 1
    assert bkz.durchschnitt == 200.0


def test_benchmark_report_build_drei_tenants():
    kzs = {
        "t1": [make_kennzahl("t1", wert=100.0, periode="2025")],
        "t2": [make_kennzahl("t2", wert=200.0, periode="2025")],
        "t3": [make_kennzahl("t3", wert=300.0, periode="2025")],
    }
    report = BenchmarkReport.build(verbund_id="v1", periode="2025", kennzahlen_je_tenant=kzs)
    bkz = report.gruppen[0].kennzahlen[0]
    assert bkz.n_teilnehmer == 3
    assert abs(bkz.durchschnitt - 200.0) < 0.01


def test_benchmark_report_anonymisiert():
    kzs = {
        "tenant-geheim-123": [make_kennzahl("tenant-geheim-123", wert=150.0, periode="2025")],
    }
    report = BenchmarkReport.build(verbund_id="v1", periode="2025", kennzahlen_je_tenant=kzs)
    assert "tenant-geheim-123" not in report.model_dump_json()


def test_benchmark_report_quartile():
    kzs = {
        "t1": [make_kennzahl("t1", wert=10.0, periode="2025")],
        "t2": [make_kennzahl("t2", wert=20.0, periode="2025")],
        "t3": [make_kennzahl("t3", wert=30.0, periode="2025")],
        "t4": [make_kennzahl("t4", wert=40.0, periode="2025")],
    }
    report = BenchmarkReport.build(verbund_id="v1", periode="2025", kennzahlen_je_tenant=kzs)
    bkz = report.gruppen[0].kennzahlen[0]
    assert bkz.p25 <= bkz.median <= bkz.p75


def test_benchmark_default_kz_katalog_mindestens_4():
    assert len(DEFAULT_KZ_KATALOG) >= 4


def test_benchmark_report_schema_version():
    report = BenchmarkReport.build(
        verbund_id="v1",
        periode="2025",
        kennzahlen_je_tenant={},
    )
    assert report.schema_version == 1


def test_api_agent_context_post():
    from app.api.v1.endpoints.agent_context_api import router as agent_context_router

    app = FastAPI()
    app.include_router(agent_context_router, prefix="/api/v1")
    client = TestClient(app, raise_server_exceptions=True)
    resp = client.post(
        "/api/v1/agent-context",
        json={
            "agent_id": "agent-test-001",
            "tenant_id": "tenant-api-test",
            "delegated_roles": ["agent", "reader"],
            "ttl_sekunden": 3600,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "context_id" in data
    assert data["tenant_id"] == "tenant-api-test"
    assert data["schema_version"] == 1


def test_api_agent_context_dispatch_post():
    from app.api.v1.endpoints.agent_context_api import router as agent_context_router

    app = FastAPI()
    app.include_router(agent_context_router, prefix="/api/v1")
    client = TestClient(app, raise_server_exceptions=True)

    create_resp = client.post(
        "/api/v1/agent-context",
        json={
            "agent_id": "agent-test-001",
            "tenant_id": "tenant-api-test",
            "delegated_roles": ["agent", "reader"],
            "ttl_sekunden": 3600,
        },
    )
    context_id = create_resp.json()["context_id"]

    dispatch_resp = client.post(
        f"/api/v1/agent-context/{context_id}/dispatch",
        json={
            "command_name": "FreigebeRechnung",
            "resource_tenant_id": "tenant-api-test",
            "resource_type": "ap_invoice",
            "issuer_role": "agent",
        },
    )
    assert dispatch_resp.status_code == 200
    assert dispatch_resp.json()["entscheidung"] == "ACCEPTED"


def test_api_benchmark_katalog_get():
    from app.api.v1.endpoints.benchmark_api import router as benchmark_router

    app = FastAPI()
    app.include_router(benchmark_router, prefix="/api/v1")
    client = TestClient(app, raise_server_exceptions=True)
    resp = client.get("/api/v1/benchmark/katalog")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 4
    assert len(data["katalog"]) >= 4
