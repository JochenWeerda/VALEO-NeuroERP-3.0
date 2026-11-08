"""The existing full-suite evidence must include every Sonar Python product root."""
import configparser
from pathlib import Path
import shlex

ROOT = Path(__file__).resolve().parents[1]


def test_full_suite_coverage_and_sonar_python_sources_agree():
    config = configparser.ConfigParser()
    config.read(ROOT / 'pytest.ini', encoding='utf-8')
    options = shlex.split(config['pytest']['addopts'])
    measured = {arg.split('=', 1)[1] for arg in options if arg.startswith('--cov=')}
    sonar = (ROOT / 'sonar-project.properties').read_text(encoding='utf-8')
    source_line = next(line for line in sonar.splitlines() if line.startswith('sonar.sources='))
    declared_python = {value for value in source_line.split('=', 1)[1].split(',') if value in {'app', 'modules', 'services'}}
    assert measured == declared_python == {'app', 'modules', 'services'}
    assert '--cov-report=xml' in options
    assert '--cov-fail-under=60' in options
    assert 'sonar.python.coverage.reportPaths=coverage.xml' in sonar
