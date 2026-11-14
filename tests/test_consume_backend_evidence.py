import hashlib
import io
import json
from pathlib import Path
from urllib.error import HTTPError
import zipfile

import pytest

from scripts import consume_backend_evidence as consumer
from scripts import verify_quality_evidence

REPO = 'owner/repo'
SHA = 'a' * 40
HEAD = 'b' * 40
BASE = 'c' * 40
NOW = '2026-11-14T12:00:00Z'
IDENTITY = {'event': 'pull_request', 'head_sha': HEAD, 'branch': 'feature', 'head_repo': REPO,
            'pr': 134, 'base_sha': BASE, 'base_ref': 'main', 'action': 'synchronize', 'sender': 42}


def run_record(**updates):
    return {'id': 40, 'workflow_id': 17, 'event': 'pull_request', 'head_sha': HEAD, 'head_branch': 'feature',
            'repository': {'full_name': REPO}, 'head_repository': {'full_name': REPO}, 'pull_requests': [],
            'display_title': f'qg:pr:134:{HEAD}:{BASE}', 'created_at': NOW, 'run_attempt': 1,
            'status': 'completed', 'conclusion': 'success', **updates}


def archive(identity=IDENTITY, checkout=SHA, run_id=40, attempt=1, *, contents=b'<coverage/>', digest=None, extra=None):
    stream = io.BytesIO()
    context = {'identity': identity, 'repository': REPO, 'checkout_sha': checkout, 'run_id': run_id, 'run_attempt': attempt}
    evidence = {'sha': checkout, 'sha256': digest or hashlib.sha256(contents).hexdigest()}
    with zipfile.ZipFile(stream, 'w') as out:
        out.writestr('backend-context.json', json.dumps(context))
        out.writestr('coverage.xml', contents)
        out.writestr('coverage.xml.evidence.json', json.dumps(evidence))
        if extra:
            out.writestr(extra, b'bad')
    return stream.getvalue()


def invoke(tmp_path, monkeypatch, *, runs=None, job=None, data=None, current=None, timeout=20):
    run = run_record()
    runs = runs if runs is not None else [run]
    job = job if job is not None else {'id': 70, 'run_id': 40, 'run_attempt': 1, 'name': 'Backend (pytest + Postgres)',
                                        'status': 'completed', 'conclusion': 'success'}
    data = data if data is not None else archive()
    def api(path):
        if path.endswith('/actions/workflows/quality-gate.yml'):
            return {'id': 17, 'state': 'active', 'path': '.github/workflows/quality-gate.yml'}
        if '/actions/workflows/17/runs?' in path:
            return {'workflow_runs': runs, 'total_count': len(runs)}
        if '/jobs?' in path:
            return {'jobs': [job], 'total_count': 1}
        if path.endswith('/artifacts?per_page=100'):
            return {'artifacts': [{'id': 81, 'name': 'backend-coverage-xml', 'expired': False}], 'total_count': 1}
        if path.endswith('/actions/runs/40'):
            return current if current is not None else runs[-1]
        raise AssertionError(path)
    def verify(_args, *, check, cwd):
        verify_quality_evidence.verify(Path(cwd) / 'coverage.xml', SHA)
    monkeypatch.setattr(consumer.subprocess, 'run', verify)
    consumer.consume(api, lambda _: data, IDENTITY, REPO, SHA, tmp_path, consumer_created_at=NOW,
                     timeout=timeout, interval=0, sleep=lambda _: None)


def test_real_pr_metadata_empty_pr_list_succeeds_with_sealed_context(tmp_path, monkeypatch):
    invoke(tmp_path, monkeypatch)
    assert (tmp_path / 'coverage.xml').read_bytes() == b'<coverage/>'


@pytest.mark.parametrize('field,value', [('event', 'push'), ('head_sha', 'd' * 40), ('head_branch', 'other'),
                                          ('workflow_id', 99), ('repository', {'full_name': 'other/repo'}),
                                          ('head_repository', {'full_name': 'fork/repo'})])
def test_mismatched_api_identity_never_matches(field, value):
    assert not consumer.matches(run_record(**{field: value}), IDENTITY, REPO, 17)


@pytest.mark.parametrize('field,value', [('pr', 135), ('base_sha', 'f' * 40), ('head_repo', 'fork/repo')])
def test_wrong_pr_context_fails(tmp_path, monkeypatch, field, value):
    with pytest.raises(ValueError, match='artifact'):
        invoke(tmp_path, monkeypatch, data=archive(identity={**IDENTITY, field: value}))


@pytest.mark.parametrize('conclusion', ['failure', 'cancelled', 'timed_out', 'skipped'])
def test_whole_quality_gate_failure_blocks(tmp_path, monkeypatch, conclusion):
    with pytest.raises(ValueError, match='Quality Gate'):
        invoke(tmp_path, monkeypatch, runs=[run_record(conclusion=conclusion)])


def test_newer_failed_run_wins_over_older_success(tmp_path, monkeypatch):
    later = run_record(id=41, created_at='2026-11-14T12:00:10Z', conclusion='failure')
    with pytest.raises(ValueError, match='Quality Gate'):
        invoke(tmp_path, monkeypatch, runs=[run_record(), later])


def test_newer_other_pr_same_head_does_not_shadow_own_provider(tmp_path, monkeypatch):
    other = run_record(id=41, created_at='2026-11-14T12:00:10Z', conclusion='failure',
                       display_title=f'qg:pr:135:{HEAD}:{"d" * 40}')
    invoke(tmp_path, monkeypatch, runs=[other, run_record()])
    assert (tmp_path / 'coverage.xml').exists()


def test_other_pr_success_cannot_hide_own_provider_failure(tmp_path, monkeypatch):
    other = run_record(id=41, created_at='2026-11-14T12:00:10Z',
                       display_title=f'qg:pr:135:{HEAD}:{"d" * 40}')
    with pytest.raises(ValueError, match='Quality Gate'):
        invoke(tmp_path, monkeypatch, runs=[other, run_record(conclusion='failure')])


def test_rerun_only_sonar_accepts_successful_original_backend_attempt(tmp_path, monkeypatch):
    rerun = run_record(run_attempt=2)
    invoke(tmp_path, monkeypatch, runs=[rerun], job={'id': 70, 'run_id': 40, 'run_attempt': 1,
           'name': 'Backend (pytest + Postgres)', 'status': 'completed', 'conclusion': 'success'}, data=archive(attempt=1))


def test_rerun_backend_requires_new_backend_attempt(tmp_path, monkeypatch):
    rerun = run_record(run_attempt=2)
    job = {'id': 71, 'run_id': 40, 'run_attempt': 2, 'name': 'Backend (pytest + Postgres)',
           'status': 'completed', 'conclusion': 'success'}
    with pytest.raises(ValueError, match='artifact'):
        invoke(tmp_path, monkeypatch, runs=[rerun], job=job, data=archive(attempt=1))
    invoke(tmp_path, monkeypatch, runs=[rerun], job=job, data=archive(attempt=2))


@pytest.mark.parametrize('change', [{'conclusion': 'failure'}, {'conclusion': 'cancelled'}, {'run_attempt': None}, {'run_id': 41}])
def test_bad_latest_backend_blocks(tmp_path, monkeypatch, change):
    job = {'id': 70, 'run_id': 40, 'run_attempt': 1, 'name': 'Backend (pytest + Postgres)',
           'status': 'completed', 'conclusion': 'success', **change}
    with pytest.raises(ValueError):
        invoke(tmp_path, monkeypatch, job=job)


def test_tampered_sha_hash_and_zip_traversal_block(tmp_path, monkeypatch):
    for data in (archive(checkout='d' * 40), archive(digest='0' * 64), archive(extra='../escape')):
        with pytest.raises(ValueError):
            invoke(tmp_path, monkeypatch, data=data)
    assert not (tmp_path.parent / 'escape').exists()


def test_timeout_and_stale_runs_fail_closed(tmp_path, monkeypatch):
    with pytest.raises(TimeoutError):
        invoke(tmp_path, monkeypatch, runs=[], timeout=0)
    with pytest.raises(TimeoutError):
        invoke(tmp_path, monkeypatch, runs=[run_record(created_at='2026-11-13T12:00:00Z')], timeout=0)


def test_pr_merge_sha_is_distinct_from_head_sha():
    event = {'repository': {'full_name': REPO}, 'sender': {'id': 42}, 'action': 'synchronize', 'pull_request': {'number': 134,
             'head': {'sha': HEAD, 'ref': 'feature', 'repo': {'full_name': REPO}},
             'base': {'sha': BASE, 'ref': 'main', 'repo': {'full_name': REPO}}}}
    assert consumer.event_identity('pull_request', event, SHA, REPO, 'refs/pull/134/merge') == IDENTITY
    with pytest.raises(ValueError):
        consumer.event_identity('pull_request', event, SHA, REPO, 'refs/pull/135/merge')


def test_push_identity_is_branch_and_event_specific():
    event = {'repository': {'full_name': REPO}, 'sender': {'id': 42}, 'before': BASE, 'after': SHA}
    result = consumer.event_identity('push', event, SHA, REPO, 'refs/heads/develop')
    assert result == {'event': 'push', 'head_sha': SHA, 'branch': 'develop', 'head_repo': REPO, 'pr': None, 'before': BASE, 'sender': 42}
    push_run = run_record(event='push', head_sha=SHA, head_branch='develop', display_title=f'qg:push:develop:{SHA}')
    assert consumer.matches(push_run, result, REPO, 17)
    assert not consumer.matches({**push_run, 'display_title': f'qg:push:main:{SHA}'}, result, REPO, 17)
    with pytest.raises(ValueError):
        consumer.event_identity('push', event, SHA, REPO, 'refs/heads/feature')


def test_newer_attempt_or_provider_failure_during_download_blocks(tmp_path, monkeypatch):
    for current in (run_record(run_attempt=2), run_record(conclusion='failure'), run_record(status='in_progress')):
        with pytest.raises(ValueError, match='changed'):
            invoke(tmp_path, monkeypatch, current=current)


def test_no_redirect_credentials_and_untrusted_hosts(monkeypatch):
    requests = []
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, _size): return b'zip'
    class Opener:
        def open(self, request, timeout):
            requests.append(request)
            if len(requests) == 1:
                raise HTTPError(request.full_url, 302, 'redirect',
                                {'Location': 'https://safe.blob.core.windows.net/artifact?sig=secret'}, None)
            return Response()
    monkeypatch.setattr(consumer, 'build_opener', lambda *_: Opener())
    assert consumer.download('/repos/owner/repo/actions/artifacts/1/zip', 'token') == b'zip'
    assert requests[0].get_header('Authorization') == 'Bearer token'
    assert requests[1].get_header('Authorization') is None
    class UnsafeOpener:
        def open(self, request, timeout):
            raise HTTPError(request.full_url, 302, 'redirect', {'Location': 'https://evil.invalid/path'}, None)
    monkeypatch.setattr(consumer, 'build_opener', lambda *_: UnsafeOpener())
    with pytest.raises(ValueError, match='Untrusted artifact host'):
        consumer.download('/repos/owner/repo/actions/artifacts/1/zip', 'token')


def test_workflow_wiring_preserves_existing_gates():
    root = Path(__file__).resolve().parents[1]
    ci = (root / '.github/workflows/ci.yml').read_text(encoding='utf-8')
    quality = (root / '.github/workflows/quality-gate.yml').read_text(encoding='utf-8')
    assert "format('qg:pr:{0}:{1}:{2}'" in quality
    assert "format('qg:push:{0}:{1}'" in quality
    job = ci.split('  test:\n', 1)[1].split('  frontend-test:', 1)[0]
    assert 'python scripts/consume_backend_evidence.py' in job
    assert 'actions: read' in job and 'contents: read' in job
    assert 'services:' not in job and 'pytest --cov=' not in job
    assert all(item in job for item in ('Validate L3 mapping definitions', 'Upload coverage', 'Bandit security scan', 'Safety dependency check'))
    backend = quality.split('  backend:\n', 1)[1].split('  frontend:\n', 1)[0]
    assert 'PYTEST_REQUIRE_DB_STRICT: "1"' in backend and 'python -m app.seeds.inventory_seed' in backend
    assert all(item in backend for item in ('pytest -q --deselect', 'run_ki_service_coverage.py',
                                           'check_critical_backend_coverage.py', 'verify_quality_evidence.py --write',
                                           'consume_backend_evidence.py --write-context', 'backend-context.json', 'overwrite: true'))
    assert 'needs: [test, frontend-test,' in ci


def test_producer_context_supports_dispatch_without_consumer_fallback(tmp_path, monkeypatch):
    event = {'repository': {'full_name': REPO}, 'sender': {'id': 42}}
    assert consumer.event_identity('workflow_dispatch', event, SHA, REPO, 'refs/heads/feature') == {
        'event': 'workflow_dispatch', 'head_sha': SHA, 'branch': 'feature', 'head_repo': REPO, 'pr': None, 'sender': 42}
    with pytest.raises(ValueError):
        consumer.event_identity('workflow_dispatch', event, SHA, REPO, 'refs/tags/v1')


def test_api_errors_and_missing_artifact_fail_closed(tmp_path, monkeypatch):
    def fail_api(_path):
        raise HTTPError('https://api.github.com/', 401, 'unauthorized', {}, None)
    with pytest.raises(HTTPError):
        consumer.consume(fail_api, lambda _: b'', IDENTITY, REPO, SHA, tmp_path, consumer_created_at=NOW)
    calls = []
    def no_artifact(path):
        calls.append(path)
        if path.endswith('/actions/workflows/quality-gate.yml'):
            return {'id': 17, 'state': 'active', 'path': '.github/workflows/quality-gate.yml'}
        if '/actions/workflows/17/runs?' in path:
            return {'workflow_runs': [run_record()], 'total_count': 1}
        if '/jobs?' in path:
            return {'jobs': [{'id': 70, 'run_id': 40, 'run_attempt': 1, 'name': 'Backend (pytest + Postgres)',
                              'status': 'completed', 'conclusion': 'success'}], 'total_count': 1}
        return {'artifacts': [], 'total_count': 0}
    with pytest.raises(ValueError, match='Missing backend artifact'):
        consumer.consume(no_artifact, lambda _: b'', IDENTITY, REPO, SHA, tmp_path, consumer_created_at=NOW)


def test_bounded_archive_members_and_size():
    with pytest.raises(ValueError, match='Unexpected artifact'):
        consumer.read_evidence(archive(extra='../escape'))
    with pytest.raises(ValueError, match='Invalid artifact'):
        monkey = consumer.MAX_FILES
        try:
            consumer.MAX_FILES = 4
            consumer.read_evidence(archive())
        finally:
            consumer.MAX_FILES = monkey
