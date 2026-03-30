"""
Audit Hash-Chain Regression-Tests — NC-D5
Testet die Integritaet der Append-Only-Audit-Kette
ohne Datenbank (Unit-Tests auf Logik-Ebene).
"""

import hashlib
import json
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from app.services.audit_hardening import _compute_hash, validate_hash_chain


class TestComputeHash:
    def test_deterministic(self):
        payload = {"action": "create", "entity_type": "order", "entity_id": "ORD-001"}
        h1 = _compute_hash("genesis", payload)
        h2 = _compute_hash("genesis", payload)
        assert h1 == h2

    def test_different_prev_hash_different_result(self):
        payload = {"action": "create"}
        h1 = _compute_hash("genesis", payload)
        h2 = _compute_hash("abc123", payload)
        assert h1 != h2

    def test_different_payload_different_result(self):
        h1 = _compute_hash("genesis", {"action": "create"})
        h2 = _compute_hash("genesis", {"action": "delete"})
        assert h1 != h2

    def test_hash_is_sha256(self):
        h = _compute_hash("genesis", {"x": 1})
        assert len(h) == 64
        int(h, 16)

    def test_key_order_irrelevant(self):
        """JSON-Sortierung stellt sicher, dass Reihenfolge egal ist."""
        h1 = _compute_hash("genesis", {"a": 1, "b": 2})
        h2 = _compute_hash("genesis", {"b": 2, "a": 1})
        assert h1 == h2

    def test_empty_payload(self):
        h = _compute_hash("genesis", {})
        assert isinstance(h, str)
        assert len(h) == 64


class TestHashChainIntegrity:
    """Simuliert eine Hash-Chain und prueft Konsistenz."""

    def _build_chain(self, entries: list[dict]) -> list[dict]:
        chain = []
        prev_hash = "genesis"
        for entry in entries:
            h = _compute_hash(prev_hash, entry)
            chain.append({**entry, "prev_hash": prev_hash, "hash": h})
            prev_hash = h
        return chain

    def test_valid_chain(self):
        entries = [
            {"id": "1", "tenant_id": "t1", "action": "create", "entity_type": "order",
             "entity_id": "O1", "user_id": "u1", "timestamp": "2026-03-30T10:00:00", "changes": {}},
            {"id": "2", "tenant_id": "t1", "action": "update", "entity_type": "order",
             "entity_id": "O1", "user_id": "u1", "timestamp": "2026-03-30T10:01:00", "changes": {"status": "approved"}},
            {"id": "3", "tenant_id": "t1", "action": "delete", "entity_type": "order",
             "entity_id": "O1", "user_id": "u2", "timestamp": "2026-03-30T10:02:00", "changes": {}},
        ]
        chain = self._build_chain(entries)
        assert chain[0]["prev_hash"] == "genesis"
        assert chain[1]["prev_hash"] == chain[0]["hash"]
        assert chain[2]["prev_hash"] == chain[1]["hash"]

    def test_tampered_entry_detected(self):
        entries = [
            {"id": "1", "tenant_id": "t1", "action": "create", "entity_type": "order",
             "entity_id": "O1", "user_id": "u1", "timestamp": "2026-03-30T10:00:00", "changes": {}},
            {"id": "2", "tenant_id": "t1", "action": "update", "entity_type": "order",
             "entity_id": "O1", "user_id": "u1", "timestamp": "2026-03-30T10:01:00", "changes": {"status": "approved"}},
        ]
        chain = self._build_chain(entries)
        original_hash = chain[0]["hash"]
        chain[0]["action"] = "TAMPERED"
        recomputed = _compute_hash(chain[0]["prev_hash"], {
            k: v for k, v in chain[0].items() if k not in ("prev_hash", "hash")
        })
        assert recomputed != original_hash

    def test_inserted_entry_breaks_chain(self):
        entries = [
            {"id": "1", "tenant_id": "t1", "action": "create", "entity_type": "order",
             "entity_id": "O1", "user_id": "u1", "timestamp": "2026-03-30T10:00:00", "changes": {}},
            {"id": "3", "tenant_id": "t1", "action": "delete", "entity_type": "order",
             "entity_id": "O1", "user_id": "u2", "timestamp": "2026-03-30T10:02:00", "changes": {}},
        ]
        chain = self._build_chain(entries)
        # Inject an entry between 1 and 3
        injected = {"id": "2", "tenant_id": "t1", "action": "injected", "entity_type": "order",
                     "entity_id": "O1", "user_id": "hacker", "timestamp": "2026-03-30T10:01:00", "changes": {}}
        injected_hash = _compute_hash(chain[0]["hash"], injected)
        # chain[1] still has prev_hash pointing to chain[0]'s hash, not injected_hash
        # So inserting this would mean chain[1]'s prev_hash doesn't match injected_hash
        assert injected_hash != chain[1]["prev_hash"]

    def test_genesis_is_first_prev(self):
        chain = self._build_chain([
            {"id": "1", "tenant_id": "t1", "action": "create", "entity_type": "x",
             "entity_id": "1", "user_id": "u", "timestamp": "2026-01-01T00:00:00", "changes": {}},
        ])
        assert chain[0]["prev_hash"] == "genesis"

    def test_long_chain_consistency(self):
        entries = []
        for i in range(100):
            entries.append({
                "id": str(i), "tenant_id": "t1", "action": f"action_{i}",
                "entity_type": "test", "entity_id": f"E-{i}",
                "user_id": "u1", "timestamp": f"2026-03-30T{10+i//60:02d}:{i%60:02d}:00",
                "changes": {"index": i},
            })
        chain = self._build_chain(entries)
        for i in range(1, len(chain)):
            assert chain[i]["prev_hash"] == chain[i - 1]["hash"], f"Break at index {i}"


class TestCaseManagement:
    """Tests fuer den Case Management Service (NC-08)."""

    def test_create_case(self):
        from app.services.case_management import (
            create_case, _CASE_STORE, CaseStatus, CasePriority,
        )
        from app.core.human_approval_gate import (
            HumanApprovalRequirement, ApprovalRisikostufe, ApprovalAusloserTyp,
        )

        _CASE_STORE.clear()
        req = HumanApprovalRequirement(
            aktions_typ="SETTLEMENT_FREIGABE",
            risiko_stufe=ApprovalRisikostufe.HOCH,
            requires_human_approval=True,
            ausgeloeste_regel_id="AG-H-001",
            ausloser_typ=ApprovalAusloserTyp.BETRAG_SCHWELLE,
            begruendung="Settlement > 50k EUR",
            freigabe_rolle="teamleiter",
        )
        case = create_case(req, "SET-001", "agent-1", {"betrag_eur": 75000})
        assert case.status == CaseStatus.OPEN
        assert case.priority == CasePriority.HIGH
        assert case.due_at is not None
        _CASE_STORE.clear()

    def test_assign_and_decide_case(self):
        from app.services.case_management import (
            create_case, assign_case, decide_case, _CASE_STORE, CaseStatus,
        )
        from app.core.human_approval_gate import (
            HumanApprovalRequirement, ApprovalDecision, ApprovalRisikostufe, ApprovalAusloserTyp,
        )

        _CASE_STORE.clear()
        req = HumanApprovalRequirement(
            aktions_typ="BESTELLUNG_ANLEGEN",
            risiko_stufe=ApprovalRisikostufe.MITTEL,
            requires_human_approval=True,
            ausgeloeste_regel_id="AG-M-003",
            ausloser_typ=ApprovalAusloserTyp.BETRAG_SCHWELLE,
            begruendung="Bestellung",
            freigabe_rolle="sachbearbeiter",
        )
        case = create_case(req, "ORD-001", "agent-2", {"betrag_eur": 5000})
        assigned = assign_case(case.case_id, "user@example.com")
        assert assigned.status == CaseStatus.ASSIGNED
        assert assigned.assigned_to == "user@example.com"

        decided = decide_case(case.case_id, ApprovalDecision.GENEHMIGT, "user@example.com", "Sieht gut aus")
        assert decided.status == CaseStatus.DECIDED
        assert decided.decision == "GENEHMIGT"
        _CASE_STORE.clear()

    def test_escalate_case(self):
        from app.services.case_management import (
            create_case, escalate_case, _CASE_STORE, CaseStatus, CasePriority,
        )
        from app.core.human_approval_gate import (
            HumanApprovalRequirement, ApprovalRisikostufe, ApprovalAusloserTyp,
        )

        _CASE_STORE.clear()
        req = HumanApprovalRequirement(
            aktions_typ="ZAHLUNG_AUSLOESEN",
            risiko_stufe=ApprovalRisikostufe.KRITISCH,
            requires_human_approval=True,
            ausgeloeste_regel_id="AG-K-002",
            ausloser_typ=ApprovalAusloserTyp.BETRAG_SCHWELLE,
            begruendung="Zahlung > 500k",
            freigabe_rolle="geschaeftsfuehrung",
        )
        case = create_case(req, "PAY-001", "agent-3", {"betrag_eur": 600000})
        escalated = escalate_case(case.case_id, "ceo@example.com", "Dringend")
        assert escalated.status == CaseStatus.ESCALATED
        assert escalated.escalated_to == "ceo@example.com"
        assert escalated.priority == CasePriority.CRITICAL
        _CASE_STORE.clear()

    def test_dashboard_stats(self):
        from app.services.case_management import (
            create_case, get_dashboard_stats, _CASE_STORE,
        )
        from app.core.human_approval_gate import (
            HumanApprovalRequirement, ApprovalRisikostufe, ApprovalAusloserTyp,
        )

        _CASE_STORE.clear()
        for risiko in [ApprovalRisikostufe.MITTEL, ApprovalRisikostufe.HOCH, ApprovalRisikostufe.KRITISCH]:
            req = HumanApprovalRequirement(
                aktions_typ="TEST", risiko_stufe=risiko, requires_human_approval=True,
                ausgeloeste_regel_id="T", ausloser_typ=ApprovalAusloserTyp.STANDARD,
                begruendung="Test", freigabe_rolle="tester",
            )
            create_case(req, f"I-{risiko.value}", "agent", {}, tenant_id="t1")

        stats = get_dashboard_stats("t1")
        assert stats["total"] == 3
        assert stats["open"] == 3
        _CASE_STORE.clear()


class TestSecretsVault:
    """Tests fuer den Secrets Vault Service (NC-15)."""

    def test_store_and_retrieve(self):
        from app.services.secrets_vault import (
            store_secret, get_secret, delete_secret, _VAULT_STORE,
        )
        _VAULT_STORE.clear()
        store_secret("TEST_API_KEY", "sk-12345")
        value = get_secret("TEST_API_KEY")
        assert value == "sk-12345"
        delete_secret("TEST_API_KEY")
        _VAULT_STORE.clear()

    def test_obfuscation_roundtrip(self):
        from app.services.secrets_vault import _obfuscate, _deobfuscate
        original = "super-secret-password-with-special-chars-äöü-!@#$%"
        obfuscated = _obfuscate(original)
        assert obfuscated != original
        restored = _deobfuscate(obfuscated)
        assert restored == original

    def test_rotate_secret(self):
        from app.services.secrets_vault import (
            store_secret, get_secret, rotate_secret, _VAULT_STORE,
        )
        _VAULT_STORE.clear()
        store_secret("ROTATE_KEY", "old-value")
        rotate_secret("ROTATE_KEY", "new-value")
        assert get_secret("ROTATE_KEY") == "new-value"
        metadata = _VAULT_STORE["ROTATE_KEY"][0]
        assert metadata.rotated_at is not None
        _VAULT_STORE.clear()

    def test_delete_secret(self):
        from app.services.secrets_vault import (
            store_secret, delete_secret, get_secret, _VAULT_STORE,
        )
        _VAULT_STORE.clear()
        store_secret("DEL_KEY", "val")
        assert delete_secret("DEL_KEY") is True
        assert get_secret("DEL_KEY") is None
        assert delete_secret("NONEXISTENT") is False
        _VAULT_STORE.clear()

    def test_list_secrets(self):
        from app.services.secrets_vault import (
            store_secret, list_secrets, SecretType, _VAULT_STORE,
        )
        _VAULT_STORE.clear()
        store_secret("K1", "v1", SecretType.API_KEY)
        store_secret("K2", "v2", SecretType.DATABASE_CREDENTIAL)
        secrets = list_secrets()
        assert len(secrets) == 2
        keys = {s.key for s in secrets}
        assert keys == {"K1", "K2"}
        _VAULT_STORE.clear()

    def test_health_check(self):
        from app.services.secrets_vault import (
            store_secret, check_health, _VAULT_STORE,
        )
        _VAULT_STORE.clear()
        store_secret("H1", "v1")
        health = check_health()
        assert health["status"] == "healthy"
        assert health["total_secrets"] == 1
        _VAULT_STORE.clear()

    def test_access_log(self):
        from app.services.secrets_vault import (
            store_secret, get_secret, get_access_log, _VAULT_STORE, _ACCESS_LOG,
        )
        _VAULT_STORE.clear()
        _ACCESS_LOG.clear()
        store_secret("LOG_KEY", "val")
        get_secret("LOG_KEY", accessor="test-user")
        log = get_access_log()
        assert any(e["key"] == "LOG_KEY" and e["accessor"] == "test-user" for e in log)
        _VAULT_STORE.clear()
        _ACCESS_LOG.clear()


class TestLiveChatChannel:
    """Tests fuer den Live-Chat-Kanal (NC-12)."""

    def test_create_session(self):
        from app.channels.livechat_channel import create_session, _SESSIONS
        _SESSIONS.clear()
        session = create_session("user-1", "tenant-1")
        assert session.user_id == "user-1"
        assert session.status == "active"
        assert session.message_count == 0
        _SESSIONS.clear()

    def test_add_message(self):
        from app.channels.livechat_channel import (
            create_session, add_message, get_history, ChatMessage, _SESSIONS,
        )
        _SESSIONS.clear()
        session = create_session("user-2")
        msg = ChatMessage(content="Hallo", sender_type="user", sender_id="user-2")
        result = add_message(session.session_id, msg)
        assert result is not None
        history = get_history(session.session_id)
        assert len(history) == 1
        assert history[0].content == "Hallo"
        _SESSIONS.clear()

    def test_close_session(self):
        from app.channels.livechat_channel import (
            create_session, close_session, add_message, ChatMessage, _SESSIONS,
        )
        _SESSIONS.clear()
        session = create_session("user-3")
        close_session(session.session_id)
        msg = ChatMessage(content="Test")
        result = add_message(session.session_id, msg)
        assert result is None
        _SESSIONS.clear()

    def test_session_to_dict(self):
        from app.channels.livechat_channel import create_session, _SESSIONS
        _SESSIONS.clear()
        session = create_session("user-4", "t1")
        d = session.to_dict()
        assert d["user_id"] == "user-4"
        assert d["tenant_id"] == "t1"
        assert d["message_count"] == 0
        _SESSIONS.clear()

    def test_list_active_sessions(self):
        from app.channels.livechat_channel import (
            create_session, close_session, list_active_sessions, _SESSIONS,
        )
        _SESSIONS.clear()
        s1 = create_session("u1", "t1")
        s2 = create_session("u2", "t1")
        s3 = create_session("u3", "t2")
        close_session(s1.session_id)
        active_t1 = list_active_sessions("t1")
        assert len(active_t1) == 1
        assert active_t1[0].user_id == "u2"
        _SESSIONS.clear()

    def test_format_response(self):
        from app.channels.livechat_channel import _format_response
        assert "Fehler" in _format_response({"status": "error", "message": "kaputt"})
        assert "Schritt" in _format_response({
            "intent": {"intent": "bestellung_anlegen", "confidence_score": 0.9, "explanation": ""},
            "plan": {"steps": [{"action": "create"}]},
        })
