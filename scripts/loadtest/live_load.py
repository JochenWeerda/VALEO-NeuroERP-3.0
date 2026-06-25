"""
live_load.py — PERF-MULTIUSER-001 Live-Lasttest (httpx, Windows-tauglich)

Erzeugt echte Concurrency gegen eine laufende API und misst RPS + Latenz-
Perzentile pro Endpunkt. Zuverlaessige Alternative zu locust/gevent unter
Windows.

Beispiel:
    python scripts/loadtest/live_load.py --url http://127.0.0.1:8000 \
        --concurrency 100 --duration 20

Umgebung:
    NEUROERP_TOKEN  (Default 'dev-token')
    NEUROERP_TENANT (Default 'default')
"""
from __future__ import annotations

import argparse
import asyncio
import os
import statistics
import sys
import time

import httpx

# Windows: Selector-Loop vermeidet langes Proactor-Teardown nach dem Lauf
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

_TOKEN = os.getenv("NEUROERP_TOKEN", "dev-token")
_TENANT = os.getenv("NEUROERP_TENANT", "default")

# (Name, Methode, Pfad, Auth?)
_ENDPOINTS = [
    ("GET /healthz", "GET", "/healthz", False),
    ("GET /api/v1/status", "GET", "/api/v1/status", True),
]


def _percentile(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = min(len(sorted_vals) - 1, int(len(sorted_vals) * pct))
    return sorted_vals[idx]


async def _worker(
    client: httpx.AsyncClient,
    deadline: float,
    auth_headers: dict[str, str],
    stats: dict[str, list[float]],
    fails: dict[str, int],
) -> None:
    i = 0
    while time.perf_counter() < deadline:
        name, method, path, needs_auth = _ENDPOINTS[i % len(_ENDPOINTS)]
        i += 1
        headers = auth_headers if needs_auth else None
        t0 = time.perf_counter()
        try:
            resp = await client.request(method, path, headers=headers)
            dt = (time.perf_counter() - t0) * 1000.0
            stats[name].append(dt)
            if resp.status_code >= 400:
                fails[name] += 1
        except Exception:
            fails[name] += 1


async def _run(url: str, concurrency: int, duration: float) -> None:
    auth_headers = {"Authorization": f"Bearer {_TOKEN}", "X-Tenant-ID": _TENANT}
    stats: dict[str, list[float]] = {name: [] for name, *_ in _ENDPOINTS}
    fails: dict[str, int] = {name: 0 for name, *_ in _ENDPOINTS}

    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)
    timeout = httpx.Timeout(30.0)

    async with httpx.AsyncClient(base_url=url, limits=limits, timeout=timeout) as client:
        # Warmup
        for _, method, path, needs_auth in _ENDPOINTS:
            try:
                await client.request(method, path, headers=auth_headers if needs_auth else None)
            except Exception:
                pass

        start = time.perf_counter()
        deadline = start + duration
        await asyncio.gather(
            *[_worker(client, deadline, auth_headers, stats, fails) for _ in range(concurrency)]
        )
        wall = time.perf_counter() - start

    total = sum(len(v) for v in stats.values())
    total_fails = sum(fails.values())
    print(f"# Live-Load: url={url} concurrency={concurrency} duration={duration:.0f}s")
    print(f"# total_ok={total}  total_fail={total_fails}  aggregate_rps={total / wall:,.0f}\n")
    print(f"{'endpoint':<22}{'reqs':>8}{'fails':>7}{'rps':>9}{'mean':>9}{'p50':>9}{'p95':>9}{'p99':>9}")
    for name, *_ in _ENDPOINTS:
        vals = sorted(stats[name])
        if not vals:
            print(f"{name:<22}{0:>8}{fails[name]:>7}{'-':>9}")
            continue
        print(
            f"{name:<22}{len(vals):>8}{fails[name]:>7}{len(vals) / wall:>9,.0f}"
            f"{statistics.fmean(vals):>8.1f}ms{_percentile(vals, 0.50):>7.1f}ms"
            f"{_percentile(vals, 0.95):>7.1f}ms{_percentile(vals, 0.99):>7.1f}ms"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Live-Lasttest (PERF-MULTIUSER-001)")
    parser.add_argument("--url", default=os.getenv("NEUROERP_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--concurrency", type=int, default=100)
    parser.add_argument("--duration", type=float, default=20.0)
    args = parser.parse_args()
    asyncio.run(_run(args.url, args.concurrency, args.duration))


if __name__ == "__main__":
    main()
