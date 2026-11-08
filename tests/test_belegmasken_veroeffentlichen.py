"""Native document definitions are code-owned and visible only in the approved tenant."""
import importlib.util
from pathlib import Path
import pytest
from app.core.belegvertrag import BELEGARTEN
from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
from app.core.screen_definitions_beleg import NATIVE_BELEG_TENANTS, screen_id

TENANT = next(iter(NATIVE_BELEG_TENANTS))


def script():
    spec = importlib.util.spec_from_file_location("check_native_documents", Path(__file__).resolve().parents[1] / "scripts/belegmasken_veroeffentlichen.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_native_documents_are_not_global_or_editable_studio_definitions(monkeypatch):
    from app.services import studio_draft_store
    def forbidden(*args, **kwargs):
        raise AssertionError("Native definitions must not read or write Studio publication state")
    for name in ["save_draft", "set_status", "get_published_definition"]:
        monkeypatch.setattr(studio_draft_store, name, forbidden)
    assert not [key for key in SCREEN_DEFINITION_BUILDERS if key.startswith("beleg/")]
    for art in BELEGARTEN:
        key = screen_id(art)
        assert get_screen_definition(key, tenant_id=TENANT)["title"] == BELEGARTEN[art].bezeichnung
        assert get_screen_definition(key, tenant_id="foreign") is None
        assert get_screen_definition(key) is None


def test_check_rejects_unapproved_tenant():
    with pytest.raises(PermissionError):
        script().pruefe_native_definitionen("foreign")


def test_all_nine_native_document_variants_pass_governance():
    result = script().pruefe_native_definitionen(TENANT)
    assert result == {screen_id(art): "native_definition_geprueft" for art in BELEGARTEN}


def test_repeated_checks_do_not_create_drafts_or_release_proof():
    checker = script()
    first = checker.pruefe_native_definitionen(TENANT)
    assert checker.pruefe_native_definitionen(TENANT) == first
    for key in first:
        assert "studioRelease" not in get_screen_definition(key, tenant_id=TENANT)
