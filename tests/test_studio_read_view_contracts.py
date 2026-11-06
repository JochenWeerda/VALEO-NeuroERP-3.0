"""Contracts for related-row reads; no live services or database."""
from copy import deepcopy

from app.services.studio_read_view_contracts import validate_read_view


def example():
    return {"key": "history", "localEffect": "view", "readView": {
        "endpoint": "/api/v1/webhooks/{id}/zustellversuche",
        "columns": [{"key": "versucht_am", "label": "Zeit", "renderKind": "datetime"},
                    {"key": "erfolgreich", "label": "Erfolg", "renderKind": "boolean"}]}}


def test_registered_get_and_actual_response_columns():
    assert validate_read_view(example()) == []


def test_untrusted_sources_and_fields_fail_closed():
    for endpoint in ("https://example.org/api/v1/x", "/api/v1/webhooks/{tenant_id}/zustellversuche",
                     "/api/v1/webhooks/{id}/zustellversuche?x=1", "/api/v1/no-such-route"):
        action = example()
        action["readView"]["endpoint"] = endpoint
        assert validate_read_view(action)
    for change in (lambda a: a["readView"]["columns"].append(deepcopy(a["readView"]["columns"][0])),
                   lambda a: a["readView"]["columns"][0].update(key="secret"),
                   lambda a: a.update(commandEndpoint="/api/v1/x"),
                   lambda a: a.update(localEffect="edit"),
                   lambda a: a["readView"]["columns"][0].update(renderKind=[])):
        action = example()
        change(action)
        assert validate_read_view(action)


def test_native_studio_import_preserves_and_pins_read_view():
    from hashlib import sha256
    from app.core.screen_definitions import get_screen_definition, SCREEN_DEFINITION_BUILDERS
    from app.core.studio_release import definition_hash
    from app.services.studio_validation import validate_studio_draft
    source = get_screen_definition("admin/webhooks-liste")
    draft = deepcopy(source)
    target = "tenant/native-" + sha256(b"admin/webhooks-liste").hexdigest()
    draft.update(id=target, baseScreenId=source["id"],
                 adapter={"type": "native", "sourceId": target, "temporary": True},
                 nativeBaseline={"sourceId": source["id"], "sourceHash": definition_hash(source), "version": 1})
    assert validate_studio_draft(draft, native_screen_ids=set(SCREEN_DEFINITION_BUILDERS)) == []
    history = next(a for a in draft["tables"][0]["rowActions"] if a["key"] == "history")
    history["readView"]["columns"] = [{"key": "erfolgreich", "label": "Geaendert"}]
    assert any("readView" in error for error in validate_studio_draft(draft, native_screen_ids=set(SCREEN_DEFINITION_BUILDERS)))
