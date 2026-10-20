"""Parse actual slice YAML: regex-only gates cannot detect malformed prose."""
from pathlib import Path

import yaml


def test_all_slice_documents_are_valid_yaml_mappings():
    root = Path(__file__).resolve().parents[1]
    files = sorted((root / 'docs/agent-ops/slices').glob('*.yaml'))
    assert files
    errors = []
    for path in files:
        try:
            document = yaml.safe_load(path.read_text(encoding='utf-8'))
            assert isinstance(document, dict), 'expected mapping'
            assert document.get('slice_id'), 'missing slice_id'
        except (yaml.YAMLError, AssertionError) as error:
            errors.append(f'{path.name}: {error}')
    assert not errors, '\n'.join(errors)
