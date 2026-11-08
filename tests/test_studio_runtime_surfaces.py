import pytest
from app.services.studio_runtime_surface_contracts import validate_runtime_surface


@pytest.mark.parametrize("contract", [None, {}, {"processKey": "unknown"},
    {"processKey": "order-to-cash", "endpoint": "/other"}, {"processKey": []}])
def test_process_surface_rejects_arbitrary_or_incomplete_bindings(contract):
    assert validate_runtime_surface({"id": "workflow/flow-spine-order-to-cash", "mode": "cockpit",
                                     "flowSpineWorkspace": contract})


def test_surfaces_are_bound_to_their_registered_screen_identity():
    assert not validate_runtime_surface({"id": "workflow/flow-spine-order-to-cash", "mode": "cockpit",
                                         "flowSpineWorkspace": {"processKey": "order-to-cash"}})
    assert validate_runtime_surface({"id": "other", "specialized": {"type": "intake", "id": "other"}})
    assert not validate_runtime_surface({"id": "waage/neu", "specialized": {"type": "weighing", "id": "waage/neu"}})


def test_native_draft_requires_exact_canonical_surface_and_source_hash():
    from copy import deepcopy
    from app.core.screen_definitions import get_screen_definition
    from app.core.studio_release import definition_hash
    native = get_screen_definition("waage/neu")
    draft = {**deepcopy(native), "id": "tenant/probe-scale", "baseScreenId": native["id"],
             "nativeBaseline": {"sourceHash": definition_hash(native)}}
    assert not validate_runtime_surface(draft)
    draft["specialized"]["id"] = "waage/liste"
    assert validate_runtime_surface(draft)


def test_runtime_evidence_requires_visible_exact_binding_and_actual_host(tmp_path):
    from app.core.mask_runtime_evidence import bound_domain_runtime_ids
    source = ("import { IntakeWeighingPage } from '@/components/mask-builder/specialized/intake/domain-runtime'\n"
              'export default () => <IntakeWeighingPage screenId="annahme/warteschlange" />')
    assert bound_domain_runtime_ids(source) == {"annahme/warteschlange"}
    assert not bound_domain_runtime_ids(source, root=tmp_path)
    assert not bound_domain_runtime_ids(source.replace("annahme/warteschlange", "crm/segment"))
    assert not bound_domain_runtime_ids(source.replace("intake/domain-runtime", "legacy-page"))
    hidden = source.split("export default")[0] + 'export default () => <div aria-hidden>' + source.split('=> ')[1] + '</div>'
    assert not bound_domain_runtime_ids(hidden)
