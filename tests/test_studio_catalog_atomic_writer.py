"""A catalog refresh may not steal another writer's lock or truncate a valid file."""
import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def writer():
    path = Path(__file__).resolve().parents[1] / 'scripts/generate_studio_screen_versions.py'
    spec = importlib.util.spec_from_file_location('catalog_writer_regression', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_existing_writer_lock_is_preserved(writer, tmp_path):
    target = tmp_path / 'catalog.json'
    lock = target.with_suffix('.lock')
    lock.write_text('other writer')
    with pytest.raises(ValueError, match='busy'):
        writer.write_release(target, '1.0.0')
    assert lock.read_text() == 'other writer'
    assert not target.exists()


def test_failed_atomic_replace_keeps_previous_catalog(writer, tmp_path, monkeypatch):
    target = tmp_path / 'catalog.json'
    target.write_text('previous complete catalog')
    monkeypatch.setattr(writer, '_release_payload', lambda _: {'schemaVersion': 1, 'releaseVersion': '1.0.0', 'screens': {}})
    monkeypatch.setattr(writer, '_native_definitions', lambda: {})
    def fail(*args):
        raise PermissionError('synthetic replacement denial')
    monkeypatch.setattr(writer.os, 'replace', fail)
    with pytest.raises(PermissionError):
        writer.write_release(target, '1.0.0')
    assert target.read_text() == 'previous complete catalog'
    assert not target.with_suffix('.lock').exists()
    assert list(tmp_path.iterdir()) == [target]
