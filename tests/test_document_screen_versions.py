"""Real builder projection, immutable historical references and fail-closed hashes."""
from copy import deepcopy
import json

import pytest

from app.core.document_screen_versions import (
    REGISTRY_PATH, check_registry, document_definition, extend_registry, resolve_variant,
)
from app.core.screen_definitions_beleg import BELEGARTEN, build_beleg_screen_definition
from app.core.studio_release import definition_hash
from scripts.generate_document_screen_versions import current_matches, write_release


def definitions():
    return {key: build_beleg_screen_definition(key) for key in BELEGARTEN}


@pytest.mark.parametrize("variant_id", BELEGARTEN)
def test_every_registered_variant_materializes_the_canonical_builder(variant_id):
    definition = document_definition(variant_id)
    binding = definition.pop("documentVariant")
    assert definition == build_beleg_screen_definition(variant_id)
    assert binding["materializedHash"] == definition_hash(definition)
    assert binding["variantId"] == variant_id
    assert document_definition(variant_id, binding["variantVersion"], expected=binding)["documentVariant"] == binding


def test_registry_is_synchronized_with_all_real_document_variants():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    assert current_matches(registry, definitions())


def test_appending_a_release_preserves_the_complete_old_history_and_pinned_resolution():
    original = definitions()
    first = extend_registry(original, "1.0.0")
    before = deepcopy(first)
    old = resolve_variant(first, "sales_invoice")
    changed = deepcopy(original)
    changed["sales_invoice"]["title"] = "New invoice title"
    second = extend_registry(changed, "2.0.0", first)
    assert first == before
    assert second["bases"]["1.0.0"] == first["bases"]["1.0.0"]
    for key in original:
        assert second["variants"][key]["1.0.0"] == first["variants"][key]["1.0.0"]
    assert resolve_variant(second, "sales_invoice")["title"] == "New invoice title"
    assert resolve_variant(second, "sales_invoice", "1.0.0", expected=old["documentVariant"]) == old


@pytest.mark.parametrize("change", ["base", "patch", "materialization", "alias"])
def test_content_or_alias_changes_cannot_silently_change_an_existing_binding(change):
    registry = extend_registry(definitions(), "1.0.0")
    reference = resolve_variant(registry, "sales_invoice")["documentVariant"]
    row = registry["variants"]["sales_invoice"]["1.0.0"]
    if change == "base":
        registry["bases"]["1.0.0"]["definition"]["mode"] = "list"
    elif change == "patch":
        row["patch"]["title"] = "Unapproved change"
    elif change == "materialization":
        row["definitionHash"] = "0" * 64
    else:
        registry["current"]["sales_invoice"] = "9.0.0"
    with pytest.raises(ValueError):
        resolve_variant(registry, "sales_invoice", expected=reference)


def test_even_rehashed_modified_history_is_rejected_by_its_preexisting_reference():
    registry = extend_registry(definitions(), "1.0.0")
    reference = resolve_variant(registry, "sales_invoice")["documentVariant"]
    row = registry["variants"]["sales_invoice"]["1.0.0"]
    row["patch"]["title"] = "Rehashed history"
    row["patchHash"] = definition_hash(row["patch"])
    row["definitionHash"] = definition_hash({**registry["bases"]["1.0.0"]["definition"], **row["patch"]})
    with pytest.raises(ValueError, match="binding_changed"):
        resolve_variant(registry, "sales_invoice", "1.0.0", expected=reference)


def test_release_numbers_cannot_overwrite_any_existing_record():
    registry = extend_registry(definitions(), "1.0.0")
    with pytest.raises(ValueError, match="already_exists"):
        extend_registry(definitions(), "1.0.0", registry)


def test_a_new_release_cannot_move_the_version_timeline_backwards():
    registry = extend_registry(definitions(), "2.0.0")
    with pytest.raises(ValueError, match="must_advance"):
        extend_registry(definitions(), "1.0.0", registry)


def test_unreferenced_historical_bases_are_also_checked():
    registry = extend_registry(definitions(), "1.0.0")
    registry['bases']['2.0.0'] = {'definition': {}, 'hash': '0' * 64}
    with pytest.raises(ValueError, match="base_changed"):
        check_registry(registry)


@pytest.mark.parametrize('version', ['', 'latest', '9.0.0'])
def test_an_explicit_unknown_version_never_falls_back_to_the_current_alias(version):
    with pytest.raises(ValueError):
        document_definition('sales_invoice', version)


def test_materialized_results_do_not_mutate_the_cached_base_or_other_callers():
    result = document_definition("sales_invoice")
    result["tabs"].clear()
    result["documentVariant"]["baseHash"] = "bad"
    assert document_definition("sales_invoice")["tabs"]
    assert document_definition("sales_invoice")["documentVariant"]["baseHash"] != "bad"


def test_all_historical_versions_are_verified_even_when_a_later_release_is_current():
    registry = extend_registry(definitions(), "2.0.0", extend_registry(definitions(), "1.0.0"))
    registry["variants"]["sales_invoice"]["1.0.0"]["patch"]["title"] = "Tampered old version"
    with pytest.raises(ValueError):
        check_registry(registry)


@pytest.mark.parametrize("value", ["", "latest", "1", "0.1.0", "1.0.0/../../", "1.0.0\n"])
def test_release_version_is_explicit_and_not_an_alias_or_path(value):
    with pytest.raises(ValueError):
        extend_registry(definitions(), value)


def test_studio_rejects_a_forged_origin_reference_without_relaxing_other_gates():
    from app.services.studio_validation import validate_studio_draft
    definition = document_definition("sales_invoice")
    definition.update(id="tenant/version-check", adapter={"type": "native", "sourceId": "tenant/version-check", "temporary": True})
    valid = validate_studio_draft(definition, native_screen_ids=set())
    assert "belegvariantenbindung_ungueltig" not in valid
    assert valid  # Document command/source release gates still apply.
    definition["documentVariant"]["baseHash"] = "0" * 64
    assert "belegvariantenbindung_ungueltig" in validate_studio_draft(definition, native_screen_ids=set())


def test_releasing_a_file_keeps_old_references_resolvable_and_never_exposes_partial_json(tmp_path, monkeypatch):
    from scripts import generate_document_screen_versions as generator
    path = tmp_path / 'versions.json'
    write_release(path, definitions(), '1.0.0')
    old_bytes = path.read_bytes()
    reference = resolve_variant(json.loads(old_bytes), 'sales_invoice')['documentVariant']
    real_replace = generator.os.replace
    observed = []
    def replace_complete(source, target):
        observed.append((json.loads(target.read_bytes()), json.loads(source.read_bytes())))
        real_replace(source, target)
    monkeypatch.setattr(generator.os, 'replace', replace_complete)
    write_release(path, definitions(), '2.0.0')
    assert observed[0][0]['current']['sales_invoice'] == '1.0.0'
    assert observed[0][1]['current']['sales_invoice'] == '2.0.0'
    assert resolve_variant(json.loads(path.read_bytes()), 'sales_invoice', '1.0.0', expected=reference)
    assert not path.with_suffix('.lock').exists()


def test_an_interrupted_file_release_keeps_the_previous_complete_registry(tmp_path, monkeypatch):
    from scripts import generate_document_screen_versions as generator
    path = tmp_path / 'versions.json'
    write_release(path, definitions(), '1.0.0')
    before = path.read_bytes()
    def interrupted(*args):
        raise OSError('simulated replacement failure')
    monkeypatch.setattr(generator.os, 'replace', interrupted)
    with pytest.raises(OSError):
        write_release(path, definitions(), '2.0.0')
    assert path.read_bytes() == before
    assert not path.with_suffix('.lock').exists()
    assert list(tmp_path.glob('*.tmp')) == []


def test_an_existing_writer_lock_is_preserved_and_no_release_is_lost(tmp_path):
    path = tmp_path / 'versions.json'
    write_release(path, definitions(), '1.0.0')
    before = path.read_bytes()
    lock = path.with_suffix('.lock')
    lock.write_text('other writer', encoding='utf-8')
    with pytest.raises(ValueError, match='release_busy'):
        write_release(path, definitions(), '2.0.0')
    assert path.read_bytes() == before
    assert lock.read_text(encoding='utf-8') == 'other writer'
