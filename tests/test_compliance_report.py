"""A report must never turn absent, partial or failed evidence into success."""
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('compliance_report', Path(__file__).resolve().parents[1] / 'scripts/compliance_report.py')
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


@pytest.mark.parametrize('problem', ['missing', 'invalid', 'empty', 'failure', 'error', 'skipped', 'suite_error', 'invalid_count', 'job_failed', 'job_missing', 'none'])
def test_evidence_is_fail_closed(tmp_path, problem):
    for label in ('gdpr', 'gobd'):
        folder = tmp_path / f'{label}-test-results'
        folder.mkdir()
        (folder / 'pytest-report.xml').write_text('<testsuites><testsuite><testcase name="actual"/></testsuite></testsuites>')
    path = tmp_path / 'gobd-test-results/pytest-report.xml'
    results = {'gdpr': 'success', 'gobd': 'success'}
    if problem == 'missing': path.unlink()
    elif problem == 'invalid': path.write_text('<broken')
    elif problem == 'empty': path.write_text('<testsuites/>')
    elif problem in ('failure', 'error', 'skipped'):
        path.write_text(f'<testsuites><testsuite><testcase><{problem}/></testcase></testsuite></testsuites>')
    elif problem in ('suite_error', 'invalid_count'):
        count = '1' if problem == 'suite_error' else 'invalid'
        path.write_text(f'<testsuites errors="{count}"><testsuite><testcase/></testsuite></testsuites>')
    elif problem == 'job_failed': results['gobd'] = 'failure'
    elif problem == 'job_missing': results.pop('gobd')
    target = tmp_path / 'report.md'
    assert report.generate(tmp_path, target, results) is (problem == 'none')
    assert target.is_file()
