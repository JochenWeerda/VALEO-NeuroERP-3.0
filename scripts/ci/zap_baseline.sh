#!/usr/bin/env bash
set -eu

# The scanner runs as a non-root user; never grant it write access to the checkout.
workdir=$(mktemp -d)
trap 'rm -rf "$workdir"' EXIT
chmod 777 "$workdir"
cp .zap/rules.tsv "$workdir/rules.tsv"
rm -f report_json.json
status=0
docker run --rm --network host -v "$workdir:/zap/wrk:rw" \
  ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
  -t http://localhost:8000 -c rules.tsv -a -J report_json.json || status=$?
if [ -f "$workdir/report_json.json" ]; then
  cp "$workdir/report_json.json" report_json.json
fi
if [ "$status" -ne 0 ] && [ "$status" -ne 2 ]; then
  echo "::error::ZAP scanner failed with exit code $status"
  exit 1
fi
python - <<'PY'
import json
from pathlib import Path

try:
    report = json.loads(Path('report_json.json').read_text(encoding='utf-8'))
    sites = report['site']
    if not isinstance(sites, list) or not sites:
        raise ValueError('site must be a nonempty list')
    count = 0
    for site in sites:
        alerts = site['alerts']
        if not isinstance(alerts, list):
            raise ValueError('alerts must be a list')
        for alert in alerts:
            risk = alert['riskcode']
            if isinstance(risk, bool) or str(risk) not in ('0', '1', '2', '3'):
                raise ValueError('invalid riskcode')
            count += int(risk) >= 2
    print(f'ZAP medium/high findings: {count}')
    if count:
        raise ValueError('medium/high findings detected')
except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
    raise SystemExit(f'::error::Invalid or unsafe ZAP report: {exc}')
PY
