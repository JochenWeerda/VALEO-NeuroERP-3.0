"""A field contract must use the production export, never the test application."""
import json
import sys
from types import SimpleNamespace

import pytest
from scripts import check_field_contracts as check


def test_field_contract_uses_production_export_even_if_test_app_is_loaded(tmp_path, monkeypatch):
    spec = {'openapi': '3.1.0', 'paths': {'/production-only': {'get': {}}}}
    path = tmp_path / 'openapi.json'
    path.write_text(json.dumps(spec), encoding='utf-8')
    monkeypatch.setattr(check, 'SPEC_PATH', path)
    monkeypatch.setitem(sys.modules, 'app.main', SimpleNamespace(app=SimpleNamespace(openapi=lambda: {'paths': {}})))
    assert check._spec() == spec


@pytest.mark.parametrize('content', ['{}', '[]', '{"openapi":"3.1.0","paths":[]}'])
def test_invalid_export_never_falls_back_to_another_application(tmp_path, monkeypatch, content):
    path = tmp_path / 'openapi.json'
    path.write_text(content, encoding='utf-8')
    monkeypatch.setattr(check, 'SPEC_PATH', path)
    with pytest.raises(ValueError, match='production OpenAPI'):
        check._spec()
