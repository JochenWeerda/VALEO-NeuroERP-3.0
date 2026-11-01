"""Pure file-content metadata and Studio admission contracts; no database."""
from __future__ import annotations

from copy import deepcopy

import pytest

from app.services.studio_file_content_contracts import validate_file_content_contracts
from app.services.studio_validation import validate_studio_draft

pytestmark = pytest.mark.unit


def _field(**changes):
    field = {"key": "csv", "label": "CSV-Datei", "type": "file", "required": True,
             "fileContent": {"encoding": "utf-8", "maxBytes": 1_048_576, "accept": [".csv", ".txt"]}}
    field.update(changes)
    return field


# Deliberately express the same JSON cases as the frontend contract: byte limits
# are integers (booleans are not integers), accept is an exact extension allowlist.
@pytest.mark.parametrize(("contract", "valid"), [
    ({"encoding": "utf-8", "maxBytes": 1, "accept": [".csv"]}, True),
    ({"encoding": "utf-8", "maxBytes": 1_048_576, "accept": [".txt", ".csv"]}, True),
    (None, False),
    (False, False),
    ([], False),
    ("utf-8", False),
    ({}, False),
    ({"maxBytes": 1, "accept": [".csv"]}, False),
    ({"encoding": "utf-8", "accept": [".csv"]}, False),
    ({"encoding": "utf-8", "maxBytes": 1}, False),
    ({"encoding": "UTF-8", "maxBytes": 1, "accept": [".csv"]}, False),
    ({"encoding": "utf-16", "maxBytes": 1, "accept": [".csv"]}, False),
    ({"encoding": "utf-8", "maxBytes": 0, "accept": [".csv"]}, False),
    ({"encoding": "utf-8", "maxBytes": -1, "accept": [".csv"]}, False),
    ({"encoding": "utf-8", "maxBytes": 1_048_577, "accept": [".csv"]}, False),
    ({"encoding": "utf-8", "maxBytes": True, "accept": [".csv"]}, False),
    ({"encoding": "utf-8", "maxBytes": 1.5, "accept": [".csv"]}, False),
    ({"encoding": "utf-8", "maxBytes": "1", "accept": [".csv"]}, False),
    ({"encoding": "utf-8", "maxBytes": None, "accept": [".csv"]}, False),
    ({"encoding": "utf-8", "maxBytes": 1, "accept": []}, False),
    ({"encoding": "utf-8", "maxBytes": 1, "accept": ".csv"}, False),
    ({"encoding": "utf-8", "maxBytes": 1, "accept": [".CSV"]}, False),
    ({"encoding": "utf-8", "maxBytes": 1, "accept": ["text/csv"]}, False),
    ({"encoding": "utf-8", "maxBytes": 1, "accept": [".pdf"]}, False),
    ({"encoding": "utf-8", "maxBytes": 1, "accept": [".csv", ".csv"]}, False),
    ({"encoding": "utf-8", "maxBytes": 1, "accept": [".csv", ".txt", ".csv"]}, False),
    ({"encoding": "utf-8", "maxBytes": 1, "accept": [{}]}, False),
    ({"encoding": "utf-8", "maxBytes": 1, "accept": [None]}, False),
    ({"encoding": "utf-8", "maxBytes": 1, "accept": [".csv"], "uploadEndpoint": "/upload"}, False),
])
def test_frontend_parity_contract_cases(contract, valid):
    definition = {"fields": [_field(fileContent=contract)]}
    before = deepcopy(definition)
    assert validate_file_content_contracts(definition) == ([] if valid else ["fileContent is invalid"])
    assert definition == before


@pytest.mark.parametrize("field_type", ["text", "textarea", "table", None, 1])
def test_descriptor_is_only_valid_for_file_fields(field_type):
    assert validate_file_content_contracts({"fields": [_field(type=field_type)]}) == ["fileContent is invalid"]


def test_descriptor_requires_explicit_file_type():
    field = _field()
    del field["type"]
    assert validate_file_content_contracts(field) == ["fileContent is invalid"]


@pytest.mark.parametrize("container", [
    lambda field: {"fields": [field]},
    lambda field: {"tabs": [{"fields": [field]}]},
    lambda field: {"fields": [{"type": "table", "rowFields": [field]}]},
    lambda field: {"actions": [{"inputFields": [field]}]},
    lambda field: {"tabs": [{"tables": [{"rowActions": [{"inputFields": [field]}]}]}]},
    lambda field: {"agentContract": {"availableActions": [{"inputFields": [field]}]}},
    lambda field: {"customMetadata": [{"nested": {"declaration": field}}]},
])
def test_all_nested_metadata_locations_are_checked(container):
    assert validate_file_content_contracts(container(_field())) == []
    assert validate_file_content_contracts(container(_field(fileContent=None))) == ["fileContent is invalid"]


def test_legacy_metadata_without_descriptor_is_unchanged():
    assert validate_file_content_contracts({"fields": [
        {"key": "attachment", "type": "file"}, {"key": "text", "type": "text"},
    ]}) == []


def _draft(field):
    return {
        "schemaVersion": 1, "id": "tenant/file-input", "domain": "sales", "mode": "detail",
        "title": "Dateieingabe", "adapter": {"type": "native", "sourceId": "tenant/file-input", "temporary": True},
        "actions": [{"key": "import", "dangerLevel": "safe", "inputFields": [field]}],
    }


@pytest.mark.parametrize(("field", "errors"), [
    (_field(), []),
    (_field(fileContent=None), ["fileContent is invalid"]),
    (_field(type="text"), ["fileContent is invalid"]),
])
def test_studio_admission_applies_file_contract_to_action_inputs(field, errors, monkeypatch):
    # The unrelated harvest preview imports database models eagerly. This pure
    # unit test keeps the real Studio/catalog/file checks and replaces only that
    # semantic stage; it does not claim a business-preview or database test.
    import sys
    from types import ModuleType
    semantic = ModuleType("app.services.studio_semantic")
    semantic.semantic_violations = lambda definition: []
    monkeypatch.setitem(sys.modules, "app.services.studio_semantic", semantic)
    catalog = {"actions": {"import": {"key": "import", "dangerLevel": "safe"}},
               "data_source_endpoints": set()}
    assert validate_studio_draft(_draft(field), native_screen_ids=set(), catalog=catalog) == errors
