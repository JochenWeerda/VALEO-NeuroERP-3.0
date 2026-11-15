#!/usr/bin/env python3
"""Fail-closed reuse of this event's canonical Quality Gate backend evidence."""
from __future__ import annotations

import io
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError
from urllib.parse import quote, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
import zipfile

API = 'https://api.github.com'
EXPECTED_FILES = {'coverage.xml', 'coverage.xml.evidence.json', 'backend-context.json'}
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_FILES = 64 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def get_api(path, token):
    if not path.startswith('/repos/') or '\\' in path or '..' in path:
        raise ValueError('Untrusted API path')
    request = Request(API + path, headers={'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json',
                                           'X-GitHub-Api-Version': '2022-11-28'})
    with build_opener(NoRedirect()).open(request, timeout=30) as response:
        return json.load(response)


def download(path, token):
    request = Request(API + path, headers={'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json'})
    try:
        build_opener(NoRedirect()).open(request, timeout=30)
    except HTTPError as exc:
        if exc.code not in (301, 302, 303, 307, 308):
            raise
        url = exc.headers.get('Location', '')
    else:
        raise ValueError('Expected signed artifact redirect')
    parsed = urlparse(url)
    host = (parsed.hostname or '').lower()
    if parsed.scheme != 'https' or parsed.username or parsed.password or not (
        host.endswith('.blob.core.windows.net') or host.endswith('.actions.githubusercontent.com')
        or host.endswith('.githubusercontent.com')
    ):
        raise ValueError('Untrusted artifact host')
    # No credentials on the signed URL and no subsequent redirects.
    with build_opener(NoRedirect()).open(Request(url), timeout=60) as response:
        payload = response.read(MAX_ARCHIVE + 1)
    if len(payload) > MAX_ARCHIVE:
        raise ValueError('Artifact exceeds size limit')
    return payload


def event_identity(event_name, event, checkout_sha, repository, ref):
    if event.get('repository', {}).get('full_name') != repository:
        raise ValueError('Event repository mismatch')
    sender = event.get('sender', {}).get('id')
    if type(sender) is not int or sender <= 0:
        raise ValueError('Event sender missing')
    if event_name == 'push':
        if ref not in ('refs/heads/main', 'refs/heads/develop') or event.get('after') != checkout_sha:
            raise ValueError('Unsupported or inconsistent push')
        return {'event': 'push', 'head_sha': checkout_sha, 'branch': ref.removeprefix('refs/heads/'),
                'head_repo': repository, 'pr': None, 'before': event['before'], 'sender': sender}
    if event_name == 'workflow_dispatch':
        if not ref.startswith('refs/heads/'):
            raise ValueError('Unsupported dispatch ref')
        return {'event': event_name, 'head_sha': checkout_sha, 'branch': ref.removeprefix('refs/heads/'),
                'head_repo': repository, 'pr': None, 'sender': sender}
    if event_name != 'pull_request':
        raise ValueError('Unsupported event')
    pr = event['pull_request']
    if pr['base']['repo']['full_name'] != repository or pr['base']['ref'] not in ('main', 'develop'):
        raise ValueError('Unsupported pull request base')
    if ref != f"refs/pull/{pr['number']}/merge":
        raise ValueError('Unexpected pull request ref')
    return {'event': event_name, 'head_sha': pr['head']['sha'], 'branch': pr['head']['ref'],
            'head_repo': pr['head']['repo']['full_name'], 'pr': pr['number'], 'base_sha': pr['base']['sha'],
            'base_ref': pr['base']['ref'], 'action': event['action'], 'sender': sender}


def matches(run, identity, repository, workflow_id):
    if identity['event'] == 'pull_request':
        title = f"qg:pr:{identity['pr']}:{identity['head_sha']}:{identity['base_sha']}"
    elif identity['event'] == 'push':
        title = f"qg:push:{identity['branch']}:{identity['head_sha']}"
    else:
        return False
    if (run.get('workflow_id') != workflow_id or run.get('repository', {}).get('full_name') != repository
        or run.get('event') != identity['event'] or run.get('head_sha') != identity['head_sha']
        or run.get('head_branch') != identity['branch']
        or run.get('head_repository', {}).get('full_name') != identity['head_repo']
        or run.get('display_title') != title):
        return False
    # GitHub may return an empty pull_requests array even for same-repository PRs.
    # Exact PR/base and merge commit are bound by the producer's artifact context.
    return True


def read_evidence(payload):
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        entries = archive.infolist()
        if len(entries) != len(EXPECTED_FILES) or {x.filename for x in entries} != EXPECTED_FILES:
            raise ValueError('Unexpected artifact members')
        if sum(x.file_size for x in entries) > MAX_FILES or any(
            x.is_dir() or x.file_size > MAX_FILES or x.flag_bits & 1 or
            x.filename != 'coverage.xml' and x.file_size > 64 * 1024 for x in entries
        ):
            raise ValueError('Invalid artifact member')
        files = {}
        for entry in entries:
            content = archive.read(entry)
            if len(content) != entry.file_size:
                raise ValueError('Truncated artifact')
            files[entry.filename] = content
        return files


def write_context():
    repository = os.environ['GITHUB_REPOSITORY']
    checkout_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    if checkout_sha != os.environ['GITHUB_SHA']:
        raise ValueError('Checkout differs from event commit')
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
    context = {'identity': event_identity(os.environ['GITHUB_EVENT_NAME'], event, checkout_sha, repository, os.environ['GITHUB_REF']),
               'repository': repository, 'checkout_sha': checkout_sha,
               'run_id': int(os.environ['GITHUB_RUN_ID']), 'run_attempt': int(os.environ['GITHUB_RUN_ATTEMPT'])}
    Path('backend-context.json').write_text(json.dumps(context, sort_keys=True) + '\n', encoding='utf-8')


def consume(api, fetch, identity, repository, checkout_sha, output, *, consumer_created_at, timeout=3600, interval=30, clock=time.monotonic, sleep=time.sleep):
    prefix = f'/repos/{repository}'
    workflow = api(f'{prefix}/actions/workflows/quality-gate.yml')
    if workflow.get('path') != '.github/workflows/quality-gate.yml' or workflow.get('state') != 'active':
        raise ValueError('Canonical workflow unavailable')
    workflow_id = workflow['id']
    deadline = clock() + timeout
    while clock() < deadline:
        query = f"?event={identity['event']}&head_sha={identity['head_sha']}&per_page=100"
        listed = api(f'{prefix}/actions/workflows/{workflow_id}/runs{query}')
        runs = listed['workflow_runs']
        if listed.get('total_count', len(runs)) > len(runs):
            raise ValueError('Too many matching runs to determine latest safely')
        origin_time = datetime.fromisoformat(consumer_created_at.replace('Z', '+00:00'))
        candidates = [r for r in runs if matches(r, identity, repository, workflow_id)
                      and abs((datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) - origin_time).total_seconds()) <= 300]
        if not candidates:
            sleep(interval)
            continue
        run = max(candidates, key=lambda r: (r['created_at'], r['id']))
        attempt = run['run_attempt']
        if run.get('status') != 'completed':
            sleep(interval)
            continue
        if run.get('conclusion') != 'success':
            raise ValueError('Canonical Quality Gate failed or was cancelled')
        jobs_payload = api(f"{prefix}/actions/runs/{run['id']}/jobs?filter=latest&per_page=100")
        jobs = jobs_payload['jobs']
        if jobs_payload.get('total_count', len(jobs)) > len(jobs):
            raise ValueError('Incomplete job inventory')
        backend = [job for job in jobs if job['name'] == 'Backend (pytest + Postgres)']
        if len(backend) > 1:
            raise ValueError('Ambiguous backend job')
        if not backend or backend[0]['status'] != 'completed':
            raise ValueError('Backend missing or incomplete in finished run')
        if backend[0].get('conclusion') != 'success':
            raise ValueError('Canonical backend failed or was cancelled')
        backend_attempt = backend[0].get('run_attempt')
        if type(backend_attempt) is not int or not 1 <= backend_attempt <= attempt or backend[0].get('run_id') != run['id']:
            raise ValueError('Backend attempt provenance unavailable')
        artifact_payload = api(f"{prefix}/actions/runs/{run['id']}/artifacts?per_page=100")
        artifacts = artifact_payload['artifacts']
        if artifact_payload.get('total_count', len(artifacts)) > len(artifacts):
            raise ValueError('Incomplete artifact inventory')
        evidence = [a for a in artifacts if a['name'] == 'backend-coverage-xml' and not a['expired']]
        if not evidence:
            raise ValueError('Missing backend artifact')
        expected = {'identity': identity, 'repository': repository, 'checkout_sha': checkout_sha,
                    'run_id': run['id'], 'run_attempt': backend_attempt}
        matching = []
        for artifact in evidence:
            files = read_evidence(fetch(f"{prefix}/actions/artifacts/{artifact['id']}/zip"))
            if json.loads(files['backend-context.json']) == expected:
                matching.append(files)
        if len(matching) != 1:
            raise ValueError('Missing or ambiguous run-attempt artifact')
        # A rerun or newer matching run can invalidate evidence while it is retrieved.
        current = api(f"{prefix}/actions/runs/{run['id']}")
        latest = api(f'{prefix}/actions/workflows/{workflow_id}/runs{query}')
        latest_runs = latest['workflow_runs']
        if latest.get('total_count', len(latest_runs)) > len(latest_runs):
            raise ValueError('Incomplete final run inventory')
        latest_candidates = [r for r in latest_runs if matches(r, identity, repository, workflow_id)
                             and abs((datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) - origin_time).total_seconds()) <= 300]
        newest = max(latest_candidates, key=lambda r: (r['created_at'], r['id'])) if latest_candidates else {}
        if (current.get('run_attempt') != attempt or current.get('status') != 'completed'
            or current.get('conclusion') != 'success' or not matches(current, identity, repository, workflow_id)
            or newest.get('id') != run['id'] or newest.get('run_attempt') != attempt
            or newest.get('status') != 'completed' or newest.get('conclusion') != 'success'):
            raise ValueError('Canonical run changed during verification')
        with tempfile.TemporaryDirectory(prefix='.backend-evidence-', dir=output) as temp:
            directory = Path(temp)
            for name, content in matching[0].items():
                (directory / name).write_bytes(content)
            evidence_json = json.loads((directory / 'coverage.xml.evidence.json').read_text(encoding='utf-8'))
            if evidence_json.get('sha') != checkout_sha:
                raise ValueError('Artifact does not belong to checked-out commit')
            verifier = output / 'scripts/verify_quality_evidence.py'
            subprocess.run([sys.executable, str(verifier), 'coverage.xml'], check=True, cwd=directory)
            for name in ('coverage.xml', 'coverage.xml.evidence.json'):
                os.replace(directory / name, output / name)
        return
    raise TimeoutError('Canonical backend evidence did not arrive in time')


def main():
    repository = os.environ['GITHUB_REPOSITORY']
    if not __import__('re').fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Invalid repository')
    checkout_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    if checkout_sha != os.environ['GITHUB_SHA']:
        raise ValueError('Checkout differs from event commit')
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
    if os.environ['GITHUB_EVENT_NAME'] not in ('push', 'pull_request'):
        raise ValueError('Unsupported consumer event')
    identity = event_identity(os.environ['GITHUB_EVENT_NAME'], event, checkout_sha, repository, os.environ['GITHUB_REF'])
    token = os.environ['GH_TOKEN']
    own_run = get_api(f"/repos/{repository}/actions/runs/{int(os.environ['GITHUB_RUN_ID'])}", token)
    if (own_run.get('event') != identity['event'] or own_run.get('head_sha') != identity['head_sha']
            or own_run.get('head_branch') != identity['branch'] or own_run.get('repository', {}).get('full_name') != repository
            or own_run.get('head_repository', {}).get('full_name') != identity['head_repo']):
        raise ValueError('Consumer run identity mismatch')
    consume(lambda path: get_api(path, token), lambda path: download(path, token), identity, repository, checkout_sha, Path.cwd(),
            consumer_created_at=own_run['created_at'])
    print('Canonical backend evidence verified for this checkout.')


if __name__ == '__main__':
    try:
        write_context() if sys.argv[1:] == ['--write-context'] else main()
    except Exception as error:
        detail = f': {error}' if isinstance(error, (ValueError, TimeoutError)) else ''
        print(f'Backend evidence unavailable: {type(error).__name__}{detail}', file=sys.stderr)
        sys.exit(1)
