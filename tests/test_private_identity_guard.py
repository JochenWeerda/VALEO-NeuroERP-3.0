"""No actual personal account data is used by the publication-guard test."""
import subprocess
import hashlib
import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_known_private_values_block_without_logging_them():
    script = r'''
    const {containsPrivateIdentity} = require('./scripts/private-identity-guard.cjs');
    const crypto = require('node:crypto');
    const salt='test-only-random-prefix';
    const hash=v=>crypto.createHash('sha256').update(salt+v.toLowerCase()).digest('hex');
    const manifest={salt, emails:[hash('person@example.invalid')], usernames:[hash('private-test-user')]};
    if (!containsPrivateIdentity('Email: person@example.invalid',manifest)) process.exit(1);
    if (!containsPrivateIdentity('"username": "private-test-user"',manifest)) process.exit(2);
    if (containsPrivateIdentity('A generic admin role',manifest)) process.exit(3);
    if (containsPrivateIdentity('"username": "example-user"',manifest)) process.exit(4);
    '''
    result=subprocess.run(['node','-e',script],capture_output=True,text=True)
    assert result.returncode == 0
    assert result.stdout == result.stderr == ''


@pytest.mark.parametrize('kind', ['removed_content', 'merge_content', 'metadata', 'private_path', 'clean'])
def test_push_checks_history_and_merge_changes_without_disclosing_values(tmp_path, kind):
    repo = tmp_path / 'repo'
    repo.mkdir()
    env = os.environ.copy()
    # No real fingerprints, account information, hooks or network in this fixture.
    for name in ('GIT_INDEX_FILE', 'GIT_DIR', 'GIT_WORK_TREE'):
        env.pop(name, None)
    salt = 'synthetic-fingerprint-salt'
    private_email = 'person@example.invalid'
    digest = lambda value: hashlib.sha256((salt + value.lower()).encode()).hexdigest()
    manifest = tmp_path / 'fingerprints.json'
    manifest.write_text(json.dumps({'salt': salt, 'emails': [digest(private_email)], 'usernames': []}))
    env['VALEO_PRIVATE_IDENTITY_MANIFEST'] = str(manifest)

    def git(*args):
        return subprocess.check_output(['git', *args], cwd=repo, env=env, stderr=subprocess.PIPE).decode().strip()

    def commit(message='fixture'):
        git('add', '.')
        git('commit', '-m', message)
        return git('rev-parse', 'HEAD')

    git('init', '-b', 'main')
    git('config', 'user.name', 'Synthetic fixture')
    git('config', 'user.email', 'fixture@example.invalid')
    git('config', 'core.hooksPath', str(tmp_path / 'no-hooks'))
    (repo / 'note.txt').write_text('public data')
    base = commit()
    if kind == 'merge_content':
        git('checkout', '-b', 'other')
        (repo / 'other.txt').write_text('public branch')
        commit()
        git('checkout', 'main')
        (repo / 'main.txt').write_text('public main')
        commit()
        git('merge', '--no-ff', '--no-commit', 'other')
        (repo / 'note.txt').write_text(private_email)
        commit('merge fixture')
    elif kind == 'private_path':
        private = repo / 'identity-private' / 'record.json'
        private.parent.mkdir()
        private.write_text('{}')
        commit()
    elif kind == 'metadata':
        (repo / 'note.txt').write_text('still public')
        commit('Email: ' + private_email)
    elif kind == 'removed_content':
        (repo / 'note.txt').write_text(private_email)
        commit()
        (repo / 'note.txt').write_text('public again')
        commit()
    else:
        (repo / 'note.txt').write_text('another public value')
        commit()
    tip = git('rev-parse', 'HEAD')
    result = subprocess.run(['node', str(ROOT / 'scripts/private-identity-push-guard.cjs')],
        cwd=repo, env=env, input=f'refs/heads/main {tip} refs/heads/main {base}\n',
        capture_output=True, text=True)
    assert result.returncode == (0 if kind == 'clean' else 1)
    assert private_email not in result.stdout + result.stderr
    assert ('Push blocked:' in result.stderr) == (kind != 'clean')
