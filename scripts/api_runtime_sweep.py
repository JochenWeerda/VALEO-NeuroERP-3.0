#!/usr/bin/env python3
"""API-Runtime-Sweep — Dauergate gegen 5xx auf GET-Routen (SPEC-P0-02 / RUNTIME-API-SWEEP-001).

Liest die OpenAPI-Spec einer laufenden Instanz, ruft alle parameterlosen
GET-Routen mit Dev-Token + Tenant-Header auf und klassifiziert:

  ok_2xx           — Erfolg
  expected_4xx     — 400/401/403/404/405/409/422: fachlich erwartbar ohne Testdaten
  allowed_503      — 503-by-design laut config/runtime_sweep_allowlist.yaml
  server_error_5xx — jeder nicht allowgelistete 5xx  => Exit 1

Zusaetzlich Exit 1 bei abgelaufenen Allowlist-Eintraegen (jede Ausnahme
braucht Begruendung + Ablaufdatum — fail-closed statt Dauer-Whitelist).

Lauf:    python scripts/api_runtime_sweep.py --base-url http://127.0.0.1:8000
Report:  artifacts/runtime-sweep-<datum>.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST_PATH = REPO_ROOT / "config" / "runtime_sweep_allowlist.yaml"

EXPECTED_4XX = {400, 401, 403, 404, 405, 409, 422, 428, 429}


def load_allowlist() -> tuple[dict[str, dict], set[str]]:
    """Allowlist: (pfad -> {reason, expires}, skip_paths); abgelaufene Eintraege = Fehler."""
    if not ALLOWLIST_PATH.exists():
        return {}, set()
    try:
        import yaml
    except ImportError:
        print("WARN: PyYAML fehlt — Allowlist wird ignoriert.", file=sys.stderr)
        return {}, set()
    raw = yaml.safe_load(ALLOWLIST_PATH.read_text(encoding="utf-8")) or {}
    allowed = {e["path"]: e for e in raw.get("allowed_503", [])}
    skips = set(raw.get("skip_paths", []))
    return allowed, skips


def parameterless_get_paths(spec: dict) -> list[str]:
    paths = []
    for path, ops in spec.get("paths", {}).items():
        if "{" in path:
            continue
        get_op = ops.get("get")
        if get_op is None:
            continue
        required_params = [
            p for p in get_op.get("parameters", [])
            if p.get("required") and p.get("in") in ("path", "query", "header")
            and p.get("name") not in ("tenant_id", "x-tenant-id", "X-Tenant-Id")
        ]
        if required_params:
            continue
        paths.append(path)
    return sorted(paths)


def main() -> int:
    parser = argparse.ArgumentParser(description="API runtime sweep (GET, 5xx-Gate)")
    parser.add_argument("--base-url", default=os.environ.get("SWEEP_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--token", default=os.environ.get("API_DEV_TOKEN", "dev-token"))
    parser.add_argument("--tenant", default=os.environ.get("SWEEP_TENANT_ID", "00000000-0000-0000-0000-000000000001"))
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--output", default=None, help="Report-Pfad (Default: artifacts/runtime-sweep-<datum>.json)")
    parser.add_argument("--max-failures-shown", type=int, default=50)
    args = parser.parse_args()

    today = dt.date.today()
    allowlist, skip_paths = load_allowlist()
    expired = [
        (p, e) for p, e in allowlist.items()
        if dt.date.fromisoformat(str(e.get("expires", "1970-01-01"))) < today
    ]

    headers = {
        "Authorization": f"Bearer {args.token}",
        "X-Tenant-Id": args.tenant,
    }
    limits = httpx.Limits(max_connections=8, max_keepalive_connections=8)
    with httpx.Client(base_url=args.base_url, headers=headers, timeout=args.timeout, limits=limits) as client:
        spec = client.get("/openapi.json").json()
        targets = [p for p in parameterless_get_paths(spec) if p not in skip_paths]
        print(f"Sweep: {len(targets)} parameterlose GET-Routen gegen {args.base_url} ({len(skip_paths)} geskippt)")

        results: dict[str, list[dict]] = {
            "ok_2xx": [], "expected_4xx": [], "allowed_503": [],
            "unexpected_503": [], "server_error_5xx": [], "transport_error": [],
        }
        for i, path in enumerate(targets, 1):
            try:
                r = client.get(path)
                code = r.status_code
            except httpx.HTTPError as exc:
                results["transport_error"].append({"path": path, "error": str(exc)[:200]})
                continue
            entry = {"path": path, "status": code}
            if 200 <= code < 300:
                results["ok_2xx"].append(entry)
            elif code in EXPECTED_4XX:
                results["expected_4xx"].append(entry)
            elif code == 503:
                if path in allowlist:
                    entry["reason"] = allowlist[path].get("reason")
                    results["allowed_503"].append(entry)
                else:
                    results["unexpected_503"].append(entry)
            elif code >= 500:
                detail = ""
                try:
                    detail = r.text[:300]
                except Exception:  # noqa: BLE001 — Response-Body optional, nur Diagnose
                    pass
                entry["detail"] = detail
                results["server_error_5xx"].append(entry)
            else:
                results["expected_4xx"].append(entry)
            if i % 200 == 0:
                print(f"  … {i}/{len(targets)}")

    summary = {k: len(v) for k, v in results.items()}
    report = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "base_url": args.base_url,
        "targets": len(targets),
        "summary": summary,
        "expired_allowlist_entries": [
            {"path": p, "expires": str(e.get("expires")), "reason": e.get("reason")} for p, e in expired
        ],
        "results": {k: v for k, v in results.items() if k != "ok_2xx"},
    }

    out_path = Path(args.output) if args.output else REPO_ROOT / "artifacts" / f"runtime-sweep-{today.isoformat()}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n== Runtime-Sweep-Ergebnis ==")
    for k, v in summary.items():
        print(f"  {k:18s} {v}")
    print(f"Report: {out_path}")

    failed = False
    if results["server_error_5xx"]:
        failed = True
        print(f"\nFEHLER: {len(results['server_error_5xx'])} Route(n) mit 5xx:", file=sys.stderr)
        for e in results["server_error_5xx"][: args.max_failures_shown]:
            print(f"  {e['status']} {e['path']}", file=sys.stderr)
    if results["unexpected_503"]:
        failed = True
        print(
            f"\nFEHLER: {len(results['unexpected_503'])} nicht allowgelistete 503 "
            "(config/runtime_sweep_allowlist.yaml pflegen — mit Begruendung + Ablaufdatum):",
            file=sys.stderr,
        )
        for e in results["unexpected_503"][: args.max_failures_shown]:
            print(f"  503 {e['path']}", file=sys.stderr)
    if expired:
        failed = True
        print(f"\nFEHLER: {len(expired)} abgelaufene Allowlist-Eintraege:", file=sys.stderr)
        for p, e in expired:
            print(f"  {p} (expires {e.get('expires')})", file=sys.stderr)
    if results["transport_error"]:
        failed = True
        print(f"\nFEHLER: {len(results['transport_error'])} Transportfehler (Timeout/Abbruch).", file=sys.stderr)

    if failed:
        return 1
    print("\nOK: 0x5xx, keine unerwarteten 503, Allowlist aktuell.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
