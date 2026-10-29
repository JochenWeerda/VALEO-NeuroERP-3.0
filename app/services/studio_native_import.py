"""Version native masks through the existing Studio store, without activation."""
from copy import deepcopy
from hashlib import sha256

from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
from app.core.screen_definitions_beleg import BELEGARTEN, NATIVE_BELEG_TENANTS, screen_id
from app.core.studio_release import definition_hash
from app.services import studio_draft_store
from app.services.studio_validation import validate_studio_draft


def source_ids(tenant_id):
    ids = set(SCREEN_DEFINITION_BUILDERS)
    if tenant_id in NATIVE_BELEG_TENANTS:
        ids.update(screen_id(art) for art in BELEGARTEN)
    return sorted(ids)


def source_definition(tenant_id, source_id):
    if source_id not in source_ids(tenant_id):
        raise KeyError(source_id)
    definition = get_screen_definition(source_id, tenant_id=tenant_id)
    if not definition:
        raise KeyError(source_id)
    return definition


def native_release_metadata(source_id: str) -> dict:
    """Release-Nachweis fuer native ScreenDefinitions (Beleg ueber document_screen_versions)."""
    if source_id.startswith("beleg/"):
        from app.core.document_screen_versions import document_definition

        binding = document_definition(source_id.split("/", 1)[1].replace("-", "_"))["documentVariant"]
        return {
            "version": binding["variantVersion"],
            "definition_hash": binding["materializedHash"],
            "gates_passed": ["A", "B", "C", "E"],
            "studio_draft_clean": True,
            "family": "beleg",
        }
    from app.core.studio_screen_versions import release_entry

    return release_entry(source_id)


def list_sources(tenant_id, query="", skip=0, limit=50):
    rows = []
    for source_id in source_ids(tenant_id):
        definition = source_definition(tenant_id, source_id)
        title = str(definition.get("title") or source_id)
        if query.casefold() not in f"{source_id} {title}".casefold():
            continue
        rows.append({"screen_id": source_id, "title": title,
                     "source_hash": definition_hash(definition)})
    return {"items": rows[skip:skip + limit], "total": len(rows)}


def import_source(tenant_id, actor, source_id, expected_hash, idempotency_key):
    definition = deepcopy(source_definition(tenant_id, source_id))
    source_snapshot = deepcopy(definition)
    stamp = definition_hash(definition)
    if stamp != expected_hash:
        raise ValueError("native_quelle_seit_anzeige_geaendert")
    target_id = "tenant/native-" + sha256(source_id.encode()).hexdigest()
    definition.update({"id": target_id, "baseScreenId": source_id,
                       "adapter": {"type": "native", "sourceId": target_id, "temporary": True},
                       "nativeBaseline": {"sourceId": source_id, "sourceHash": stamp, "version": 1}})
    violations = validate_studio_draft(definition, native_screen_ids=set(SCREEN_DEFINITION_BUILDERS))
    # Import is an auditable starting point, never proof of process compatibility.
    readiness = {"migration": {"stage": "baseline", "source_id": source_id,
                               "source_hash": stamp, "source_definition": source_snapshot,
                               "activation": "unchanged"},
                 "eligible_for_release": False, "violations": violations}
    return studio_draft_store.save_draft(tenant_id, actor, definition, readiness=readiness,
                                        idempotency_key=idempotency_key)
