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
        except yaml.YAMLError as error:
            errors.append(f'{path.name}: {error}')
            continue
        if not isinstance(document, dict):
            errors.append(f'{path.name}: expected mapping')
        elif not document.get('slice_id'):
            errors.append(f'{path.name}: missing slice_id')
    assert not errors, '\n'.join(errors)
