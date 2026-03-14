"""
Wave-7 Paket A: Read-Model-Persistenz und Event-Consumer-Wiring
Tests fuer ReadModelSnapshot, ReadModelSnapshotStore, ConsumerWiringRegistry und API-Endpoints.
"""
from __future__ import annotations
import hashlib
import json
import time
from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.read_model_persistence import (
    ReadModelSnapshot,
    ReadModelSnapshotStore,
    SnapshotCursor,
)
from app.core.event_consumer_wiring import (
    ConsumerWiringRegistry,
    NatsSubjectMapping,
    WiringStatus,
    WiringHealthReport,
    build_default_wiring,
)
from app.api.v1.endpoints import read_model_snapshots as snapshot_endpoints
from app.core.database import get_db
from app.infrastructure.models.read_model_snapshots import ReadModelSnapshotRecord


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_snapshot(model_name: str = "ap-invoice-cockpit", tenant_id: str = "tenant_a", payload: dict | None = None) -> ReadModelSnapshot:
    if payload is None:
        payload = {"total": 42, "open": 5}
    return ReadModelSnapshot.build(model_name=model_name, tenant_id=tenant_id, payload=payload)


# ===========================================================================
# ReadModelSnapshot Tests (8)
# ===========================================================================

def test_snapshot_build_hat_snapshot_id():
    """build() erzeugt eine nicht-leere UUID-artige snapshot_id."""
    snap = _make_snapshot()
    assert snap.snapshot_id
    assert len(snap.snapshot_id) == 36  # Standard UUID-Format


def test_snapshot_build_hash_korrekt():
    """SHA-256 von payload_json stimmt mit payload_hash ueberein."""
    snap = _make_snapshot()
    expected = hashlib.sha256(snap.payload_json.encode()).hexdigest()
    assert snap.payload_hash == expected


def test_snapshot_verify_integrity_true():
    """Unveraenderter Snapshot besteht Integritaetspruefung."""
    snap = _make_snapshot()
    assert snap.verify_integrity() is True


def test_snapshot_verify_integrity_false_bei_tampering():
    """Veraendertes payload_json fuehrt zu False bei verify_integrity()."""
    snap = _make_snapshot()
    # Manipulate payload_json via model_copy
    tampered = snap.model_copy(update={"payload_json": snap.payload_json + " "})
    assert tampered.verify_integrity() is False


def test_snapshot_get_payload_roundtrip():
    """dict -> JSON -> dict Roundtrip liefert identische Daten."""
    original = {"invoice_count": 99, "flag": True, "name": "Test"}
    snap = ReadModelSnapshot.build("test-model", "t1", original)
    recovered = snap.get_payload()
    assert recovered == original


def test_snapshot_cursor_nicht_leer():
    """cursor-Feld ist ein 16-stelliger Hex-String."""
    snap = _make_snapshot()
    assert len(snap.cursor) == 16
    assert all(c in "0123456789abcdef" for c in snap.cursor)


def test_snapshot_schema_version():
    """schema_version ist 1."""
    snap = _make_snapshot()
    assert snap.schema_version == 1


def test_snapshot_store_save_und_get():
    """save() gefolgt von get(id) liefert dasselbe Objekt zurueck."""
    store = ReadModelSnapshotStore()
    snap = _make_snapshot()
    store.save(snap)
    retrieved = store.get(snap.snapshot_id)
    assert retrieved is not None
    assert retrieved.snapshot_id == snap.snapshot_id
    assert retrieved.model_name == snap.model_name


# ===========================================================================
# ReadModelSnapshotStore Tests (6)
# ===========================================================================

def test_store_get_latest_kein_snapshot():
    """Leerer Store liefert None fuer get_latest()."""
    store = ReadModelSnapshotStore()
    result = store.get_latest("ap-invoice-cockpit", "tenant_x")
    assert result is None


def test_store_get_latest_neuester():
    """Von zwei Snapshots wird der neuere zurueckgegeben."""
    store = ReadModelSnapshotStore()
    snap1 = ReadModelSnapshot.build("cockpit", "t1", {"v": 1})
    # Ensure snap2 is strictly newer by patching created_at
    snap2 = ReadModelSnapshot.build("cockpit", "t1", {"v": 2})
    snap2 = snap2.model_copy(update={"created_at": snap1.created_at + timedelta(seconds=1)})
    store.save(snap1)
    store.save(snap2)
    latest = store.get_latest("cockpit", "t1")
    assert latest is not None
    assert latest.snapshot_id == snap2.snapshot_id


def test_store_get_page_leer():
    """Leerer Store liefert leere Liste fuer get_page()."""
    store = ReadModelSnapshotStore()
    cursor = SnapshotCursor()
    result = store.get_page("cockpit", "t1", cursor)
    assert result == []


def test_store_get_page_mit_limit():
    """5 gespeicherte Snapshots mit limit=3 ergeben 3 Eintraege."""
    store = ReadModelSnapshotStore()
    base_time = datetime(2026, 1, 1, 12, 0, 0)
    for i in range(5):
        snap = ReadModelSnapshot.build("cockpit", "t1", {"i": i})
        snap = snap.model_copy(update={"created_at": base_time + timedelta(seconds=i)})
        store.save(snap)
    cursor = SnapshotCursor(limit=3)
    page = store.get_page("cockpit", "t1", cursor)
    assert len(page) == 3


def test_store_get_page_cursor():
    """Cursor nach dem 2. Element liefert ab dem 3. Element weiter."""
    store = ReadModelSnapshotStore()
    base_time = datetime(2026, 1, 1, 12, 0, 0)
    snaps = []
    for i in range(5):
        snap = ReadModelSnapshot.build("cockpit", "t1", {"i": i})
        snap = snap.model_copy(update={"created_at": base_time + timedelta(seconds=i)})
        store.save(snap)
        snaps.append(snap)
    # Cursor nach dem 2. Element (Index 1)
    cursor = SnapshotCursor(last_snapshot_id=snaps[1].snapshot_id, limit=10)
    page = store.get_page("cockpit", "t1", cursor)
    assert len(page) == 3
    assert page[0].snapshot_id == snaps[2].snapshot_id


def test_store_count():
    """count() zaehlt korrekt nach model_name und tenant_id."""
    store = ReadModelSnapshotStore()
    for i in range(3):
        store.save(ReadModelSnapshot.build("model-a", "t1", {"i": i}))
    for i in range(2):
        store.save(ReadModelSnapshot.build("model-b", "t1", {"i": i}))
    store.save(ReadModelSnapshot.build("model-a", "t2", {"i": 0}))

    assert store.count("model-a", "t1") == 3
    assert store.count("model-b", "t1") == 2
    assert store.count("model-a", "t2") == 1
    assert store.count("model-c", "t1") == 0


def test_store_db_save_und_get_latest(sqlite_snapshot_db: Session):
    """DB-Store speichert Snapshots und liefert den neuesten Eintrag zurueck."""
    store = ReadModelSnapshotStore(db_session=sqlite_snapshot_db)
    snap1 = ReadModelSnapshot.build("cockpit", "tenant-db", {"v": 1})
    snap2 = ReadModelSnapshot.build("cockpit", "tenant-db", {"v": 2})
    snap2 = snap2.model_copy(update={"created_at": snap1.created_at + timedelta(seconds=1)})

    store.save(snap1)
    store.save(snap2)

    latest = store.get_latest("cockpit", "tenant-db")
    assert latest is not None
    assert latest.snapshot_id == snap2.snapshot_id
    assert store.count("cockpit", "tenant-db") == 2


def test_store_db_get_page_cursor(sqlite_snapshot_db: Session):
    """DB-Store paginiert deterministisch ueber last_snapshot_id."""
    store = ReadModelSnapshotStore(db_session=sqlite_snapshot_db)
    base_time = datetime(2026, 1, 1, 12, 0, 0)
    snapshots = []
    for i in range(4):
        snap = ReadModelSnapshot.build("cockpit", "tenant-db", {"i": i})
        snap = snap.model_copy(update={"created_at": base_time + timedelta(seconds=i)})
        store.save(snap)
        snapshots.append(snap)

    page = store.get_page(
        "cockpit",
        "tenant-db",
        SnapshotCursor(last_snapshot_id=snapshots[1].snapshot_id, limit=10),
    )

    assert [item.snapshot_id for item in page] == [snapshots[2].snapshot_id, snapshots[3].snapshot_id]


# ===========================================================================
# ConsumerWiringRegistry Tests (8)
# ===========================================================================

def test_wiring_is_wired_true():
    """Bekanntes Subject mit Status WIRED liefert True."""
    registry = build_default_wiring()
    assert registry.is_wired("tenant.*.ap_invoice.approved") is True


def test_wiring_is_wired_false():
    """Unbekanntes Subject liefert False."""
    registry = build_default_wiring()
    assert registry.is_wired("tenant.*.nonexistent.event") is False


def test_wiring_get_consumer_id():
    """get_consumer_id() liefert die korrekte consumer_id."""
    registry = build_default_wiring()
    cid = registry.get_consumer_id("tenant.*.ap_invoice.approved")
    assert cid == "ap_invoice_cockpit_consumer"


def test_wiring_health_alle_wired():
    """build_default_wiring() liefert health_pct=100.0 (alle Eintraege WIRED)."""
    registry = build_default_wiring()
    report = registry.health_check()
    assert report.health_pct == 100.0
    assert report.unwired_count == 0
    assert report.schema_version == 1


def test_wiring_health_mit_unwired():
    """Ein UNWIRED-Eintrag senkt wired_count und erhoert unwired_count auf 1."""
    registry = build_default_wiring()
    registry.add(NatsSubjectMapping(
        subject_pattern="tenant.*.some.orphaned_event",
        consumer_id="orphan_consumer",
        status=WiringStatus.UNWIRED,
    ))
    report = registry.health_check()
    assert report.unwired_count == 1
    assert "tenant.*.some.orphaned_event" in report.unwired_subjects


def test_wiring_default_deckt_ap_invoice():
    """AP-Invoice.approved ist in build_default_wiring() enthalten."""
    registry = build_default_wiring()
    subjects = [m.subject_pattern for m in registry.mappings]
    assert "tenant.*.ap_invoice.approved" in subjects


def test_wiring_default_deckt_workflow():
    """workflow.started ist in build_default_wiring() enthalten."""
    registry = build_default_wiring()
    subjects = [m.subject_pattern for m in registry.mappings]
    assert "tenant.*.workflow.started" in subjects


def test_wiring_default_deckt_silo():
    """silo.transfer ist in build_default_wiring() enthalten."""
    registry = build_default_wiring()
    subjects = [m.subject_pattern for m in registry.mappings]
    assert "tenant.*.silo.transfer" in subjects


# ===========================================================================
# API Tests (2)
# ===========================================================================

AUTH_HEADERS = {"Authorization": "Bearer dev-token"}


@pytest.fixture()
def sqlite_snapshot_db() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    ReadModelSnapshotRecord.__table__.create(bind=engine)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        ReadModelSnapshotRecord.__table__.drop(bind=engine)
        engine.dispose()


@pytest.fixture(scope="module")
def client():
    from main import app
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture()
def snapshot_client(sqlite_snapshot_db: Session):
    app = FastAPI()
    app.include_router(snapshot_endpoints.router, prefix="/api/v1")

    def _override_get_db():
        try:
            yield sqlite_snapshot_db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


def test_api_wiring_health_get(client):
    """GET /api/v1/read-models/wiring-health gibt ein WiringHealthReport zurueck."""
    response = client.get("/api/v1/read-models/wiring-health", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "health_pct" in data
    assert data["health_pct"] == 100.0
    assert "schema_version" in data


def test_api_wiring_subjects_get(client):
    """GET /api/v1/read-models/wiring-subjects gibt mappings und total zurueck."""
    response = client.get("/api/v1/read-models/wiring-subjects", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "mappings" in data
    assert "total" in data
    assert data["total"] > 0
    assert data["schema_version"] == 1


def test_api_snapshot_roundtrip_db(snapshot_client: TestClient):
    """Snapshot-API schreibt in den DB-Store und liest den Datensatz wieder aus."""
    create_response = snapshot_client.post(
        "/api/v1/read-models/snapshots",
        params={"model_name": "ap-invoice-cockpit", "tenant_id": "tenant-db"},
        json={"open": 4, "total": 9},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["model_name"] == "ap-invoice-cockpit"

    latest_response = snapshot_client.get(
        "/api/v1/read-models/snapshots/latest",
        params={"model_name": "ap-invoice-cockpit", "tenant_id": "tenant-db"},
    )
    assert latest_response.status_code == 200
    latest = latest_response.json()
    assert latest["snapshot_id"] == created["snapshot_id"]


def test_api_snapshot_page_db(snapshot_client: TestClient):
    """Paging-Endpoint liefert DB-persistierte Snapshots samt count."""
    for index in range(3):
        response = snapshot_client.post(
            "/api/v1/read-models/snapshots",
            params={"model_name": "payment-run-cockpit", "tenant_id": "tenant-db"},
            json={"index": index},
        )
        assert response.status_code == 201

    page_response = snapshot_client.get(
        "/api/v1/read-models/snapshots/page",
        params={"model_name": "payment-run-cockpit", "tenant_id": "tenant-db", "limit": 2},
    )
    assert page_response.status_code == 200
    page = page_response.json()
    assert page["count"] == 2
    assert len(page["items"]) == 2
    assert page["schema_version"] == 1
