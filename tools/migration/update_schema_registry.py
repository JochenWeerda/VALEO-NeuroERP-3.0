from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'memory-bank' / 'migration' / 'schemas'
TARGET = ROOT.parent / 'schema-registry.json'

registry: dict[str, list[str]] = defaultdict(list)

for path in sorted(ROOT.glob('*.json')):
    stem = path.stem
    if '_' in stem:
        domain, table = stem.split('_', 1)
    else:
        domain, table = 'misc', stem
    registry[domain].append(table)

payload = {
    'baseDir': str(ROOT.relative_to(Path.cwd())),
    'domains': registry,
    'count': sum(len(tables) for tables in registry.values()),
}

TARGET.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
print(f'Updated {TARGET} with {payload["count"]} table descriptors.')