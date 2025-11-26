from finance_shared.gobd import GoBDAuditTrail


def test_audit_trail_hash_chain():
    trail = GoBDAuditTrail(tenant_id="tenant-x")
    entry = trail.create_entry(
        entity_type="journal",
        entity_id="J-1",
        action="create",
        payload={"foo": "bar"},
        user_id="user-1",
    )
    trail.append_entry(entry)

    # Sollte keine Ausnahme werfen
    trail.verify_chain()


