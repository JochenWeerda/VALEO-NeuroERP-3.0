"""Build a bounded technical evidence report; absent/failed evidence fails closed."""
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


def generate(source: Path, target: Path, results: dict[str, str]) -> bool:
    lines = ['# Compliance technical evidence', '',
             'These targeted contracts do not certify complete legal compliance.',
             'Global application coverage is enforced by the full test workflow.', '']
    valid = True
    for label in ('gdpr', 'gobd'):
        try:
            tree = ET.parse(source / f'{label}-test-results' / 'pytest-report.xml')
            cases = tree.findall('.//testcase')
            failures = sum(bool(list(case.findall('failure')) + list(case.findall('error')) + list(case.findall('skipped'))) for case in cases)
            counts_valid = all(int(node.get(field, '0')) == 0
                               for node in tree.iter()
                               if node.tag in ('testsuite', 'testsuites')
                               for field in ('failures', 'errors', 'skipped'))
            passed = results.get(label) == 'success' and bool(cases) and failures == 0 and counts_valid
            lines.append(f'- {label}: {len(cases)} cases; failed/error/skipped={failures}; job={results.get(label, "missing")}; accepted={passed}')
        except (OSError, ValueError, ET.ParseError):
            passed = False
            lines.append(f'- {label}: missing or invalid evidence; accepted=False')
        valid = valid and passed
    target.write_text('\n'.join(lines) + '\n', encoding='utf8')
    return valid


if __name__ == '__main__':
    sys.exit(0 if generate(Path(sys.argv[1]), Path(sys.argv[2]),
                          {'gdpr': os.getenv('GDPR_RESULT', ''), 'gobd': os.getenv('GOBD_RESULT', '')}) else 1)
