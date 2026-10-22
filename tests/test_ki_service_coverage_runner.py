"""Real child pytest/coverage: namespace separation, preservation and fail-closed publishing."""
import hashlib
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from coverage import Coverage, CoverageData
import pytest

from scripts.run_ki_service_coverage import minimum, run


def project(root: Path, *, branch=False, failure=False):
    for name in ('app', 'modules', 'services/ki-usability/app', 'services/ki-usability/tests'):
        path = root / name
        path.mkdir(parents=True, exist_ok=True)
        (path / '__init__.py').write_text('')
    (root / 'pytest.ini').write_text('[pytest]\naddopts = --cov-fail-under=60\n')
    core = root / 'app/shared.py'
    core.write_text('def marker():\n    return "core"\n')
    (root / 'app/never.py').write_text('UNEXECUTED = 42\n')
    child = root / 'services/ki-usability/app/shared.py'
    child.write_text('def marker():\n    return "service"\n')
    assertion = 'assert False' if failure else 'assert marker() == "service"'
    (root / 'services/ki-usability/tests/test_service.py').write_text(
        'from app.shared import marker\ndef test_own_namespace():\n    ' + assertion + '\n')
    coverage = Coverage(data_file=str(root / '.coverage'), source=[str(root / 'app')], branch=branch, config_file=False)
    coverage.start()
    namespace = {}
    exec(compile(core.read_text(), str(core), 'exec'), namespace)
    assert namespace['marker']() == 'core'
    coverage.stop()
    coverage.save()
    return core, child


@pytest.mark.parametrize('branch', [False, True])
def test_real_service_suite_has_own_app_and_preserves_core_including_zero_hits(tmp_path, branch):
    core, child = project(tmp_path, branch=branch)
    percentage = run(tmp_path)
    assert percentage >= 60
    merged = CoverageData(basename=str(tmp_path / '.coverage'))
    merged.read()
    assert merged.has_arcs() == branch
    assert merged.lines(str(core)) == [1, 2]
    assert merged.lines(str(child)) == [1, 2]
    assert str(tmp_path / 'app/never.py') in merged.measured_files()
    assert merged.lines(str(tmp_path / 'app/never.py')) == []
    classes = ET.parse(tmp_path / 'coverage.xml').getroot().findall('.//class')
    unexecuted = next(item for item in classes if item.attrib['filename'].endswith('never.py'))
    assert unexecuted.find('lines/line').attrib['hits'] == '0'


def test_failed_service_suite_cannot_replace_verified_core_or_xml(tmp_path):
    project(tmp_path, failure=True)
    original = (tmp_path / '.coverage').read_bytes()
    xml = tmp_path / 'coverage.xml'
    xml.write_text('existing core XML')
    with pytest.raises(subprocess.CalledProcessError):
        run(tmp_path)
    assert hashlib.sha256((tmp_path / '.coverage').read_bytes()).digest() == hashlib.sha256(original).digest()
    assert xml.read_text() == 'existing core XML'


@pytest.mark.parametrize('value', ['0', '101', 'nan', 'invalid'])
def test_missing_or_invalid_coverage_minimum_is_never_assumed(tmp_path, value):
    (tmp_path / 'pytest.ini').write_text('[pytest]\naddopts = --cov-fail-under=' + value + '\n')
    with pytest.raises(ValueError):
        minimum(tmp_path)


def test_service_suite_requires_real_core_measurement_first(tmp_path):
    (tmp_path / 'pytest.ini').write_text('[pytest]\naddopts = --cov-fail-under=60\n')
    with pytest.raises(ValueError, match='Full core suite coverage'):
        run(tmp_path)
