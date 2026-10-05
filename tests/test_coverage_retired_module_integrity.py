"""Real Git contracts for coverage retirement; no databases or network."""
import json
import subprocess

import pytest

from scripts import check_baseline_integrity as integrity
from scripts import check_critical_backend_coverage as coverage

OLD = 'services/old.py'
NEW = 'services/new.py'


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True, stderr=subprocess.PIPE).strip()


def thresholds(root, values):
    (root / 'config/coverage_ratchet_baseline.json').write_text(json.dumps({'thresholds': values}))


def commit(root):
    git(root, 'add', '.')
    git(root, 'commit', '-qm', 'fixture')
    return git(root, 'rev-parse', 'HEAD')


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, '-c', 'init.templateDir=', 'init', '-q')
    git(tmp_path, 'config', 'user.name', 'Contract Test')
    git(tmp_path, 'config', 'user.email', 'contract@example.invalid')
    (tmp_path / 'config').mkdir()
    (tmp_path / 'scripts').mkdir()
    (tmp_path / 'scripts/check_pagination.py').write_text("EXEMPT_FILES = {'unchanged.py'}\n")
    for name, (field, _) in integrity.POLICIES.items():
        (tmp_path / name).write_text(json.dumps({field: {}, 'loc_limit': 1000}))
    source = tmp_path / 'app' / OLD
    source.parent.mkdir(parents=True)
    source.write_text('def source():\n    return "protected"\n')
    thresholds(tmp_path, {OLD: .8})
    base = commit(tmp_path)
    return tmp_path, base, source


def test_committed_deleted_module_can_retire_threshold(repo):
    root, base, source = repo
    source.unlink()
    thresholds(root, {})
    commit(root)
    assert integrity.check(root, base) == []


def test_uncommitted_deletion_does_not_prove_retirement(repo):
    root, base, source = repo
    source.unlink()
    thresholds(root, {})
    assert integrity.check(root, base)


def test_unicode_module_is_still_tracked_after_uncommitted_deletion(repo):
    root, _, source = repo
    source.rename(source.with_name('prüfen.py'))
    thresholds(root, {'services/prüfen.py': .8})
    base = commit(root)
    source.with_name('prüfen.py').unlink()
    thresholds(root, {})
    assert integrity.check(root, base)


def test_present_module_keeps_coverage_floor(repo):
    root, base, _ = repo
    thresholds(root, {})
    commit(root)
    assert integrity.check(root, base)


def test_untracked_replacement_cannot_hide_retirement(repo):
    root, base, source = repo
    source.unlink()
    thresholds(root, {})
    commit(root)
    source.write_text('untracked replacement')
    assert integrity.check(root, base)


def test_orphan_from_prior_deletion_can_be_cleaned(repo):
    root, _, source = repo
    source.unlink()
    base = commit(root)  # Old threshold still exists: real handshake condition.
    thresholds(root, {})
    commit(root)
    assert integrity.check(root, base) == []


@pytest.mark.parametrize('new_floor,allowed', [(.79, False), (None, False), (.8, True), (.9, True)])
def test_rename_transfers_at_least_the_original_floor(repo, new_floor, allowed):
    root, base, source = repo
    source.rename(root / 'app' / NEW)
    thresholds(root, {} if new_floor is None else {NEW: new_floor})
    commit(root)
    assert (integrity.check(root, base) == []) is allowed


def test_rewritten_successor_cannot_escape_git_rename_heuristic(repo):
    root, base, source = repo
    source.unlink()
    (root / 'app' / NEW).write_text('def completely_changed():\n    return 123\n')
    thresholds(root, {NEW: .1})
    commit(root)
    assert integrity.check(root, base)


def test_rename_outside_app_does_not_retire_coverage(repo):
    root, base, source = repo
    source.rename(root / 'scripts/moved.py')
    thresholds(root, {})
    commit(root)
    assert integrity.check(root, base)


@pytest.mark.parametrize('path', ['../outside.py', '/absolute.py', 'C:/outside.py', 'services\\old.py'])
def test_invalid_coverage_paths_are_not_retired(repo, path):
    root, _, _ = repo
    thresholds(root, {path: .8})
    base = commit(root)
    thresholds(root, {})
    commit(root)
    assert integrity.check(root, base)


def test_coverage_gate_rejects_live_missing_source_even_with_xml(tmp_path, monkeypatch):
    (tmp_path / 'config').mkdir()
    thresholds(tmp_path, {OLD: .8})
    xml = tmp_path / 'coverage.xml'
    xml.write_text(f'<coverage><class filename="{OLD}" line-rate="1"/></coverage>')
    monkeypatch.setattr(coverage, 'PROJECT_ROOT', tmp_path)
    monkeypatch.setattr(coverage, 'COVERAGE_XML', xml)
    monkeypatch.setattr(coverage, 'CRITICAL_THRESHOLDS', {OLD: .8})
    with pytest.raises(SystemExit):
        coverage.main()


def test_coverage_gate_accepts_present_module_with_preserved_floor(tmp_path, monkeypatch):
    (tmp_path / 'config').mkdir()
    thresholds(tmp_path, {OLD: .8})
    source = tmp_path / 'app' / OLD
    source.parent.mkdir(parents=True)
    source.write_text('def source():\n    return 1\n')
    xml = tmp_path / 'coverage.xml'
    xml.write_text(f'<coverage><class filename="{OLD}" line-rate="0.8"/></coverage>')
    monkeypatch.setattr(coverage, 'PROJECT_ROOT', tmp_path)
    monkeypatch.setattr(coverage, 'COVERAGE_XML', xml)
    monkeypatch.setattr(coverage, 'CRITICAL_THRESHOLDS', {OLD: .8})
    coverage.main()


def test_project_thresholds_match_baseline_and_live_sources():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    new = json.loads((root / 'config/coverage_ratchet_baseline.json').read_text(encoding='utf-8'))['thresholds']
    assert coverage.CRITICAL_THRESHOLDS == new
    assert all(integrity.coverage_source(root, name).is_file() for name in new)


@pytest.mark.parametrize('rate', ['NaN', 'Infinity', '-0.1', '1.1', 'invalid'])
def test_invalid_measurement_never_passes_coverage_gate(tmp_path, monkeypatch, rate):
    (tmp_path / 'config').mkdir()
    thresholds(tmp_path, {OLD: .8})
    source = tmp_path / 'app' / OLD
    source.parent.mkdir(parents=True)
    source.write_text('def source():\n    return 1\n')
    xml = tmp_path / 'coverage.xml'
    xml.write_text(f'<coverage><class filename="{OLD}" line-rate="{rate}"/></coverage>')
    monkeypatch.setattr(coverage, 'PROJECT_ROOT', tmp_path)
    monkeypatch.setattr(coverage, 'COVERAGE_XML', xml)
    monkeypatch.setattr(coverage, 'CRITICAL_THRESHOLDS', {OLD: .8})
    with pytest.raises(SystemExit):
        coverage.main()


@pytest.mark.parametrize('rate', [float('nan'), float('inf'), -.1, 1.1, True, '.8'])
def test_invalid_threshold_never_passes_coverage_gate(tmp_path, monkeypatch, rate):
    (tmp_path / 'config').mkdir()
    thresholds(tmp_path, {OLD: .8})
    source = tmp_path / 'app' / OLD
    source.parent.mkdir(parents=True)
    source.write_text('def source():\n    return 1\n')
    xml = tmp_path / 'coverage.xml'
    xml.write_text(f'<coverage><class filename="{OLD}" line-rate="1"/></coverage>')
    monkeypatch.setattr(coverage, 'PROJECT_ROOT', tmp_path)
    monkeypatch.setattr(coverage, 'COVERAGE_XML', xml)
    monkeypatch.setattr(coverage, 'CRITICAL_THRESHOLDS', {OLD: rate})
    with pytest.raises(SystemExit):
        coverage.main()
