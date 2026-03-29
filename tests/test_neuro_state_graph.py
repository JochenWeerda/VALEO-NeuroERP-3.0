"""
Tests for Lane B: Neuro State Graph + Confidence Ledger.

Covers:
  - State Graph: node creation, transition validation, snapshot building
  - Confidence Ledger: entry building, hash chain integrity, verification
  - API endpoints: CRUD + transition + ledger recording
"""

from datetime import datetime, timezone

import pytest

from app.core.neuro_state_graph import (
    EdgeRelation,
    StateEdge,
    StateGraphService,
    StateGraphValidationError,
    StateNode,
    StateNodeType,
    StatePhase,
)
from app.core.confidence_ledger import (
    ConfidenceLedgerEntry,
    ConfidenceLedgerService,
    ConfidenceSource,
    GENESIS_HASH,
    LedgerChainBroken,
    RiskLevel,
)


# ===================================================================
# State Graph -- Unit Tests
# ===================================================================

class TestStateGraphTransitions:
    """Test the allowed-transitions matrix and validation."""

    def _make_node(
        self,
        node_type: StateNodeType = StateNodeType.BESTELLUNG,
        phase: StatePhase = StatePhase.ENTWURF,
    ) -> StateNode:
        return StateNode(
            node_id="sn-test001",
            node_type=node_type,
            phase=phase,
            tenant_id="t-001",
            aggregate_id="BO-2026-0001",
            aggregate_type="SalesOrder",
            label="Bestellung 2026-0001",
        )

    def test_valid_transition_bestellung_entwurf_to_offen(self):
        node = self._make_node()
        transition = StateGraphService.build_transition(
            transition_id="st-001",
            node=node,
            to_phase=StatePhase.OFFEN,
            triggered_by="user:max",
            reason="Bestellung angelegt",
        )
        assert transition.from_phase == StatePhase.ENTWURF
        assert transition.to_phase == StatePhase.OFFEN
        assert transition.context_hash != ""
        assert len(transition.context_hash) == 64  # SHA-256

    def test_invalid_transition_raises(self):
        node = self._make_node(phase=StatePhase.ENTWURF)
        with pytest.raises(StateGraphValidationError, match="not allowed"):
            StateGraphService.build_transition(
                transition_id="st-002",
                node=node,
                to_phase=StatePhase.ABGESCHLOSSEN,
                triggered_by="user:max",
            )

    def test_rechnung_lifecycle(self):
        """Walk the full Rechnung lifecycle: Entwurf -> Offen -> Freigegeben -> Abgeschlossen."""
        node = self._make_node(node_type=StateNodeType.RECHNUNG, phase=StatePhase.ENTWURF)

        for to_phase in [StatePhase.OFFEN, StatePhase.FREIGEGEBEN, StatePhase.ABGESCHLOSSEN]:
            t = StateGraphService.build_transition(
                transition_id=f"st-{to_phase.value}",
                node=node,
                to_phase=to_phase,
                triggered_by="system:invoice-engine",
            )
            assert t.to_phase == to_phase
            node = self._make_node(node_type=StateNodeType.RECHNUNG, phase=to_phase)

    def test_stornierung_from_offen(self):
        node = self._make_node(phase=StatePhase.OFFEN)
        t = StateGraphService.build_transition(
            transition_id="st-storno",
            node=node,
            to_phase=StatePhase.STORNIERT,
            triggered_by="user:admin",
            reason="Kunde hat storniert",
        )
        assert t.to_phase == StatePhase.STORNIERT

    def test_reachable_phases_from_offen(self):
        reachable = StateGraphService.reachable_phases(
            StateNodeType.BESTELLUNG, StatePhase.OFFEN
        )
        assert "in_bearbeitung" in reachable
        assert "storniert" in reachable
        assert "abgeschlossen" not in reachable

    def test_allowed_transitions_returns_list(self):
        allowed = StateGraphService.allowed_transitions(StateNodeType.FREIGABE)
        assert isinstance(allowed, list)
        assert len(allowed) >= 3
        assert ("offen", "freigegeben") in allowed

    def test_case_run_id_propagated(self):
        node = self._make_node(phase=StatePhase.OFFEN)
        t = StateGraphService.build_transition(
            transition_id="st-case",
            node=node,
            to_phase=StatePhase.IN_BEARBEITUNG,
            triggered_by="agent:bestellvorschlag",
            case_run_id="run-abc-123",
        )
        assert t.case_run_id == "run-abc-123"


class TestStateGraphSnapshot:
    """Test snapshot building for audit evidence."""

    def test_build_snapshot(self):
        root = StateNode(
            node_id="sn-root",
            node_type=StateNodeType.BESTELLUNG,
            phase=StatePhase.OFFEN,
            tenant_id="t-001",
            aggregate_id="BO-001",
            aggregate_type="SalesOrder",
            label="Bestellung 001",
        )
        related = StateNode(
            node_id="sn-ls",
            node_type=StateNodeType.LIEFERSCHEIN,
            phase=StatePhase.ENTWURF,
            tenant_id="t-001",
            aggregate_id="LS-001",
            aggregate_type="DeliveryNote",
            label="Lieferschein 001",
        )
        edge = StateEdge(
            edge_id="se-001",
            source_node_id="sn-root",
            target_node_id="sn-ls",
            relation=EdgeRelation.ERZEUGT,
            tenant_id="t-001",
        )

        snapshot = StateGraphService.build_snapshot(
            snapshot_id="snap-001",
            tenant_id="t-001",
            root_node=root,
            related_nodes=[related],
            edges=[edge],
            transitions=[],
        )
        assert snapshot.root_node_id == "sn-root"
        assert len(snapshot.nodes) == 2
        assert len(snapshot.edges) == 1


# ===================================================================
# Confidence Ledger -- Unit Tests
# ===================================================================

class TestConfidenceLedgerEntry:
    """Test ledger entry creation and hash computation."""

    def _make_entry(self, **kwargs) -> ConfidenceLedgerEntry:
        defaults = dict(
            entry_id="cl-001",
            tenant_id="t-001",
            confidence_score=0.85,
            risk_level=RiskLevel.MITTEL,
            source=ConfidenceSource.INTENT_ENGINE,
            reason="High intent match on Bestellvorschlag",
        )
        defaults.update(kwargs)
        return ConfidenceLedgerService.build_entry(**defaults)

    def test_genesis_entry_has_genesis_previous_hash(self):
        entry = self._make_entry()
        assert entry.previous_hash == GENESIS_HASH
        assert entry.chain_hash != ""
        assert entry.chain_hash != GENESIS_HASH

    def test_chain_hash_is_deterministic(self):
        e1 = self._make_entry()
        e2 = self._make_entry()
        fixed_time = datetime(2026, 3, 29, 12, 0, 0, tzinfo=timezone.utc)
        e1.recorded_at = fixed_time
        e2.recorded_at = fixed_time
        h1 = ConfidenceLedgerService.compute_chain_hash(GENESIS_HASH, e1)
        h2 = ConfidenceLedgerService.compute_chain_hash(GENESIS_HASH, e2)
        assert h1 == h2

    def test_input_hash_computed_when_input_data_provided(self):
        entry = self._make_entry(input_data={"query": "Bestellvorschlag fuer Weizen"})
        assert entry.input_hash != ""
        assert len(entry.input_hash) == 64

    def test_input_hash_empty_without_input_data(self):
        entry = self._make_entry()
        assert entry.input_hash == ""

    def test_model_metadata_stored(self):
        entry = self._make_entry(
            model_id="neuro-intent-v3",
            model_version="3.2.1",
        )
        assert entry.model_id == "neuro-intent-v3"
        assert entry.model_version == "3.2.1"


class TestConfidenceLedgerChain:
    """Test hash-chain integrity verification."""

    def _build_chain(self, n: int = 5) -> list[ConfidenceLedgerEntry]:
        chain: list[ConfidenceLedgerEntry] = []
        for i in range(n):
            prev_hash = chain[-1].chain_hash if chain else GENESIS_HASH
            entry = ConfidenceLedgerService.build_entry(
                entry_id=f"cl-{i:03d}",
                tenant_id="t-001",
                confidence_score=round(0.5 + i * 0.1, 2),
                risk_level=RiskLevel.MITTEL,
                source=ConfidenceSource.PLANNER,
                reason=f"Step {i} confidence",
                previous_hash=prev_hash,
            )
            chain.append(entry)
        return chain

    def test_valid_chain_passes_verification(self):
        chain = self._build_chain(5)
        assert ConfidenceLedgerService.verify_chain(chain) is True

    def test_empty_chain_passes(self):
        assert ConfidenceLedgerService.verify_chain([]) is True

    def test_single_entry_chain_passes(self):
        chain = self._build_chain(1)
        assert ConfidenceLedgerService.verify_chain(chain) is True

    def test_tampered_chain_hash_raises(self):
        chain = self._build_chain(3)
        chain[1].chain_hash = "deadbeef" * 8
        with pytest.raises(LedgerChainBroken, match="chain_hash mismatch"):
            ConfidenceLedgerService.verify_chain(chain)

    def test_tampered_previous_hash_raises(self):
        chain = self._build_chain(3)
        chain[2].previous_hash = "cafebabe" * 8
        with pytest.raises(LedgerChainBroken, match="previous_hash mismatch"):
            ConfidenceLedgerService.verify_chain(chain)

    def test_reordered_chain_breaks(self):
        chain = self._build_chain(3)
        chain[1], chain[2] = chain[2], chain[1]
        with pytest.raises(LedgerChainBroken):
            ConfidenceLedgerService.verify_chain(chain)


class TestConfidenceLedgerAnalytics:
    """Test risk_summary and latest_confidence helpers."""

    def _build_entries(self) -> list[ConfidenceLedgerEntry]:
        entries = []
        specs = [
            ("cl-a", 0.9, RiskLevel.NIEDRIG, ConfidenceSource.INTENT_ENGINE),
            ("cl-b", 0.7, RiskLevel.MITTEL, ConfidenceSource.PLANNER),
            ("cl-c", 0.4, RiskLevel.HOCH, ConfidenceSource.POLICY_GATE),
            ("cl-d", 0.2, RiskLevel.KRITISCH, ConfidenceSource.APPROVAL_GATE),
        ]
        prev = GENESIS_HASH
        for eid, score, risk, source in specs:
            e = ConfidenceLedgerService.build_entry(
                entry_id=eid,
                tenant_id="t-001",
                confidence_score=score,
                risk_level=risk,
                source=source,
                reason=f"Test entry {eid}",
                previous_hash=prev,
            )
            entries.append(e)
            prev = e.chain_hash
        return entries

    def test_risk_summary(self):
        entries = self._build_entries()
        summary = ConfidenceLedgerService.risk_summary(entries)
        assert summary["count"] == 4
        assert summary["max_risk"] == "KRITISCH"
        assert summary["min_confidence"] == 0.2
        assert summary["max_confidence"] == 0.9
        assert len(summary["sources"]) == 4

    def test_risk_summary_empty(self):
        summary = ConfidenceLedgerService.risk_summary([])
        assert summary["count"] == 0

    def test_latest_confidence(self):
        entries = self._build_entries()
        latest = ConfidenceLedgerService.latest_confidence(entries)
        assert latest is not None
        assert latest.entry_id == "cl-d"

    def test_latest_confidence_filtered_by_source(self):
        entries = self._build_entries()
        latest = ConfidenceLedgerService.latest_confidence(entries, source=ConfidenceSource.PLANNER)
        assert latest is not None
        assert latest.entry_id == "cl-b"

    def test_latest_confidence_none_for_missing_source(self):
        entries = self._build_entries()
        latest = ConfidenceLedgerService.latest_confidence(entries, source=ConfidenceSource.DQ_GATE)
        assert latest is None


# ===================================================================
# API Endpoint Tests (FastAPI TestClient)
# ===================================================================

@pytest.fixture
def client():
    """Create a FastAPI test client with the neuro router mounted."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints.neuro_state_graph_api import router, _nodes, _edges, _transitions, _ledger
    from app.core.database import get_db

    _nodes.clear()
    _edges.clear()
    _transitions.clear()
    _ledger.clear()

    app = FastAPI()
    app.include_router(router, prefix="/api/v1/neuro")
    app.dependency_overrides[get_db] = lambda: None
    return TestClient(app)


class TestStateGraphAPI:
    """Test State Graph REST endpoints."""

    def test_create_and_get_node(self, client):
        resp = client.post("/api/v1/neuro/state-graph/nodes", json={
            "node_type": "bestellung",
            "phase": "entwurf",
            "tenant_id": "t-001",
            "aggregate_id": "BO-001",
            "aggregate_type": "SalesOrder",
            "label": "Bestellung 001",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["node_type"] == "bestellung"
        assert data["phase"] == "entwurf"

        node_id = data["node_id"]
        resp2 = client.get(f"/api/v1/neuro/state-graph/nodes/{node_id}")
        assert resp2.status_code == 200
        assert resp2.json()["node_id"] == node_id

    def test_create_node_invalid_type(self, client):
        resp = client.post("/api/v1/neuro/state-graph/nodes", json={
            "node_type": "ungueltig",
            "tenant_id": "t-001",
            "aggregate_id": "X",
            "aggregate_type": "X",
            "label": "X",
        })
        assert resp.status_code == 400

    def test_transition_valid(self, client):
        resp = client.post("/api/v1/neuro/state-graph/nodes", json={
            "node_type": "bestellung",
            "phase": "entwurf",
            "tenant_id": "t-001",
            "aggregate_id": "BO-002",
            "aggregate_type": "SalesOrder",
            "label": "Test",
        })
        node_id = resp.json()["node_id"]

        resp2 = client.post(f"/api/v1/neuro/state-graph/nodes/{node_id}/transitions", json={
            "to_phase": "offen",
            "triggered_by": "user:test",
            "reason": "Erstellt",
        })
        assert resp2.status_code == 200
        assert resp2.json()["to_phase"] == "offen"

    def test_transition_invalid_rejected(self, client):
        resp = client.post("/api/v1/neuro/state-graph/nodes", json={
            "node_type": "bestellung",
            "phase": "entwurf",
            "tenant_id": "t-001",
            "aggregate_id": "BO-003",
            "aggregate_type": "SalesOrder",
            "label": "Test",
        })
        node_id = resp.json()["node_id"]

        resp2 = client.post(f"/api/v1/neuro/state-graph/nodes/{node_id}/transitions", json={
            "to_phase": "abgeschlossen",
            "triggered_by": "user:test",
        })
        assert resp2.status_code == 422

    def test_list_nodes_filtered(self, client):
        for i in range(3):
            client.post("/api/v1/neuro/state-graph/nodes", json={
                "node_type": "rechnung",
                "phase": "entwurf",
                "tenant_id": "t-001",
                "aggregate_id": f"RE-{i}",
                "aggregate_type": "Invoice",
                "label": f"Rechnung {i}",
            })
        resp = client.get("/api/v1/neuro/state-graph/nodes?tenant_id=t-001&node_type=rechnung")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_reachable_phases(self, client):
        resp = client.post("/api/v1/neuro/state-graph/nodes", json={
            "node_type": "bestellung",
            "phase": "offen",
            "tenant_id": "t-001",
            "aggregate_id": "BO-R",
            "aggregate_type": "SalesOrder",
            "label": "Test",
        })
        node_id = resp.json()["node_id"]

        resp2 = client.get(f"/api/v1/neuro/state-graph/nodes/{node_id}/reachable")
        assert resp2.status_code == 200
        data = resp2.json()
        assert "in_bearbeitung" in data["reachable"]
        assert "storniert" in data["reachable"]

    def test_create_edge(self, client):
        r1 = client.post("/api/v1/neuro/state-graph/nodes", json={
            "node_type": "bestellung", "tenant_id": "t-001",
            "aggregate_id": "BO-E1", "aggregate_type": "SalesOrder", "label": "A",
        })
        r2 = client.post("/api/v1/neuro/state-graph/nodes", json={
            "node_type": "lieferschein", "tenant_id": "t-001",
            "aggregate_id": "LS-E1", "aggregate_type": "DeliveryNote", "label": "B",
        })
        n1 = r1.json()["node_id"]
        n2 = r2.json()["node_id"]

        resp = client.post("/api/v1/neuro/state-graph/edges", json={
            "source_node_id": n1,
            "target_node_id": n2,
            "relation": "erzeugt",
            "tenant_id": "t-001",
        })
        assert resp.status_code == 200
        assert resp.json()["relation"] == "erzeugt"

    def test_node_types_meta(self, client):
        resp = client.get("/api/v1/neuro/state-graph/meta/node-types")
        assert resp.status_code == 200
        data = resp.json()
        assert "bestellung" in data
        assert len(data["bestellung"]) >= 5


class TestConfidenceLedgerAPI:
    """Test Confidence Ledger REST endpoints."""

    def test_record_and_get_entry(self, client):
        resp = client.post("/api/v1/neuro/confidence-ledger/entries", json={
            "tenant_id": "t-001",
            "confidence_score": 0.87,
            "risk_level": "MITTEL",
            "source": "intent_engine",
            "reason": "High intent match",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["confidence_score"] == 0.87
        assert data["chain_hash"] != ""

        entry_id = data["entry_id"]
        resp2 = client.get(f"/api/v1/neuro/confidence-ledger/entries/{entry_id}")
        assert resp2.status_code == 200

    def test_chain_integrity_after_multiple_entries(self, client):
        for i in range(5):
            client.post("/api/v1/neuro/confidence-ledger/entries", json={
                "tenant_id": "t-001",
                "confidence_score": 0.5 + i * 0.1,
                "risk_level": "NIEDRIG",
                "source": "planner",
                "reason": f"Step {i}",
            })

        resp = client.post("/api/v1/neuro/confidence-ledger/verify?tenant_id=t-001")
        assert resp.status_code == 200
        assert resp.json()["status"] == "intact"
        assert resp.json()["entries_verified"] == 5

    def test_invalid_risk_level_rejected(self, client):
        resp = client.post("/api/v1/neuro/confidence-ledger/entries", json={
            "tenant_id": "t-001",
            "confidence_score": 0.5,
            "risk_level": "UNGUELTIG",
            "source": "planner",
            "reason": "Test",
        })
        assert resp.status_code == 400

    def test_summary_endpoint(self, client):
        for score, risk in [(0.9, "NIEDRIG"), (0.4, "HOCH"), (0.1, "KRITISCH")]:
            client.post("/api/v1/neuro/confidence-ledger/entries", json={
                "tenant_id": "t-001",
                "confidence_score": score,
                "risk_level": risk,
                "source": "policy_gate",
                "reason": "Test",
            })

        resp = client.get("/api/v1/neuro/confidence-ledger/summary?tenant_id=t-001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 3
        assert data["max_risk"] == "KRITISCH"

    def test_list_filtered_by_source(self, client):
        client.post("/api/v1/neuro/confidence-ledger/entries", json={
            "tenant_id": "t-001", "confidence_score": 0.8,
            "risk_level": "NIEDRIG", "source": "intent_engine", "reason": "A",
        })
        client.post("/api/v1/neuro/confidence-ledger/entries", json={
            "tenant_id": "t-001", "confidence_score": 0.5,
            "risk_level": "MITTEL", "source": "planner", "reason": "B",
        })

        resp = client.get("/api/v1/neuro/confidence-ledger/entries?tenant_id=t-001&source=intent_engine")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["source"] == "intent_engine"
