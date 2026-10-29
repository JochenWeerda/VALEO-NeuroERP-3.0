"""Scope regression: tests are tests, production coverage remains required."""
from pathlib import Path
from fnmatch import fnmatchcase

ROOT=Path(__file__).resolve().parents[1]


def properties():
    source=(ROOT/'sonar-project.properties').read_text(encoding='utf-8')
    joined=source.replace('\\\n','')
    return {key.strip():value.strip() for line in joined.splitlines()
            if line.strip() and not line.lstrip().startswith('#') and '=' in line
            for key,value in [line.split('=',1)]}


def test_actual_frontend_and_backend_tests_are_classified_as_tests():
    config=properties()
    assert 'sonar.test.exclusions' not in config
    roots=config['sonar.tests'].split(',')
    patterns=[p.strip() for p in config['sonar.test.inclusions'].split(',')]
    paths=['tests/test_studio_entity_channels.py',
        'packages/frontend-web/src/__tests__/pages/service-annahme-feldservice-uix.test.ts',
        'packages/frontend-web/src/components/example.test.tsx',
        'services/ki-usability/tests/test_intent_resolver.py']
    for path in paths:
        assert any(path.startswith(root+'/') for root in roots),path
        assert any(fnmatchcase(path,p) for p in patterns),path


def test_business_sources_and_coverage_requirements_are_not_excluded():
    config=properties()
    patterns=[p.strip() for p in config['sonar.test.inclusions'].split(',')]
    for path in ['app/services/studio_entity_commands.py',
        'app/services/mcp_execution_service.py',
        'packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx',
        'packages/frontend-web/src/pages/lager/materialfluss.tsx',
        'services/ki-usability/app/services/intent_resolver.py']:
        assert not any(fnmatchcase(path,p) for p in patterns),path
        assert not any(fnmatchcase(path,p.strip()) for p in config['sonar.exclusions'].split(',')),path
        assert not any(fnmatchcase(path,p.strip()) for p in config['sonar.coverage.exclusions'].split(',')),path
    assert config['sonar.python.coverage.reportPaths']=='coverage.xml'
    assert config['sonar.javascript.lcov.reportPaths']=='packages/frontend-web/coverage/lcov.info'
