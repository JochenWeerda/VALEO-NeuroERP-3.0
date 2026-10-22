"""A renamed/lazy-loaded old UI is not evidence of a native runtime migration."""
import importlib.util
from pathlib import Path

import pytest

from app.services.made_by_studio_gates import _source_has_runtime_marker, _endpoint_in_openapi


@pytest.fixture
def inventory_module():
    path = Path(__file__).resolve().parents[1] / "scripts/mask_route_migration_inventory.py"
    spec = importlib.util.spec_from_file_location("route_migration_evidence", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_lazy_wrapper_is_reported_as_legacy_not_native(inventory_module):
    source = "import { createLegacyMaskPage } from '@/components/mask-builder';\nexport default createLegacyMaskPage(() => import('./security-legacy'))"
    assert inventory_module.classify_source(source, filename="security.tsx") == "legacy_wrapper"
    assert not _source_has_runtime_marker(source)


def test_suffix_cannot_hide_legacy_implementation(inventory_module):
    assert inventory_module.classify_source("return <ObjectPage />", filename="security-legacy.tsx") == "legacy_mask_pattern"
    assert inventory_module.classify_source("return <form><input /></form>", filename="create-legacy.tsx") == "hand_built"


def test_native_route_still_has_positive_runtime_evidence(inventory_module):
    source = 'return <NativeListPage screenId="finance/datev-export" />'
    assert inventory_module.classify_source(source) == "runtime_wired"
    assert _source_has_runtime_marker(source)


@pytest.mark.parametrize('source', [
    "import { NativeListPage } from '@/components/mask-builder'",
    '// return <NativeListPage screenId="fake" />',
    '/* return <NativeListPage screenId="fake" /> */',
    'return <div className="sr-only" aria-hidden><NativeListPage screenId="fake" /></div>',
])
def test_import_comment_or_hidden_decoy_is_not_runtime_evidence(inventory_module, source):
    assert inventory_module.classify_source(source) != 'runtime_wired'
    assert not _source_has_runtime_marker(source)


def test_unrelated_collection_or_parameter_route_cannot_prove_an_endpoint_exists():
    assert not _endpoint_in_openapi('/api/v1/finance/datev-export', {'/api/v1/finance/{}'})
    assert not _endpoint_in_openapi('/api/v1/customers/{entity_id}', {'/api/v1/customers'})
    assert not _endpoint_in_openapi('/api/v1/customers', set())
    assert _endpoint_in_openapi('/api/v1/customers/{entity_id}', {'/api/v1/customers/{}'})
