"""Merge lineage must not reset or weaken established quality ratchets."""
import json
import subprocess

import pytest

from scripts.check_baseline_integrity import compare
from scripts.resolve_quality_baseline_base import select_base


@pytest.fixture
def history(tmp_path):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(tmp_path), *args], text=True).strip()
    git('init', '-q', '--initial-branch=seed')
    git('config', 'user.name', 'Contract')
    git('config', 'user.email', 'contract@example.invalid')
    (tmp_path / 'root.txt').write_text('root')
    git('add', '.')
    git('commit', '-qm', 'root')
    root = git('rev-parse', 'HEAD')
    git('checkout', '-qb', 'main')
    (tmp_path / 'baseline.json').write_text(json.dumps({'debt': 1}))
    git('add', '.')
    git('commit', '-qm', 'established ratchet')
    incoming = git('rev-parse', 'HEAD')
    git('update-ref', 'refs/remotes/origin/main', incoming)
    git('checkout', '-qb', 'develop', root)
    (tmp_path / 'develop.txt').write_text('preserved')
    git('add', '.')
    git('commit', '-qm', 'develop work')
    before = git('rev-parse', 'HEAD')
    git('merge', '--no-ff', '-m', 'import main', 'main')
    merged = git('rev-parse', 'HEAD')
    return tmp_path, git, root, before, incoming, merged


def test_import_uses_established_main_lineage(history):
    root, _, _, before, incoming, merged = history
    assert select_base(root, before, merged, 'push', 'develop') == incoming


@pytest.mark.parametrize('event,branch', [('pull_request', 'develop'), ('push', 'main'), ('push', 'topic')])
def test_other_events_keep_original_protection(history, event, branch):
    root, _, _, before, _, merged = history
    assert select_base(root, before, merged, event, branch) == before


def test_unestablished_incoming_branch_keeps_old_base(history):
    root, git, oldest, before, _, merged = history
    git('update-ref', 'refs/remotes/origin/main', oldest)
    assert select_base(root, before, merged, 'push', 'develop') == before


def test_direct_push_does_not_change_lineage(history):
    root, _, oldest, before, _, _ = history
    assert select_base(root, oldest, before, 'push', 'develop') == oldest


def test_push_range_must_match_first_merge_parent(history):
    root, _, oldest, _, _, merged = history
    assert select_base(root, oldest, merged, 'push', 'develop') == oldest


def test_new_debt_in_merge_result_is_still_rejected(history):
    root, git, _, before, incoming, _ = history
    # Amend the merge result with increased debt, keeping both parents.
    (root / 'baseline.json').write_text(json.dumps({'debt': 2}))
    git('add', '.')
    git('commit', '--amend', '-qm', 'bad merge resolution')
    target = git('rev-parse', 'HEAD')
    selected = select_base(root, before, target, 'push', 'develop')
    assert selected == incoming
    established = json.loads(git('show', selected + ':baseline.json'))
    assert compare(established, json.loads((root / 'baseline.json').read_text()), 'down')
