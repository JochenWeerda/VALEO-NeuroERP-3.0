"""
benchmark_middleware_stack.py — PERF-MULTIUSER-001

Isolierter Micro-Benchmark fuer den HTTP-Request-Hotpath.

Misst den reinen Overhead der vier Response-/Context-Middleware
(Prometheus, Correlation, SecurityHeaders, Audit) gegen eine identische
App ohne Middleware — ohne DB, Auth oder Lifespan.

Vergleicht damit BaseHTTPMiddleware (vorher) vs. reine ASGI-Middleware
(nachher). Ausgabe: req/s und mittlere Latenz fuer "bare" vs "stacked"
sowie der relative Overhead.

Aufruf:
    python scripts/benchmark_middleware_stack.py
    python scripts/benchmark_middleware_stack.py --requests 5000 --concurrency 64
"""
from __future__ import annotations

import argparse
import asyncio
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from fastapi import FastAPI

from app.middleware.metrics import PrometheusMiddleware
from app.middleware.correlation import CorrelationMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.audit_middleware import AuditMiddleware


def _build_app(*, with_stack: bool) -> FastAPI:
    app = FastAPI()

    @app.get("/ping")
    async def ping() -> dict[str, bool]:
        return {"ok": True}

    @app.post("/echo")
    async def echo() -> dict[str, bool]:
        return {"ok": True}

    if with_stack:
        # Gleiche Reihenfolge wie main.py (innen → aussen)
        app.add_middleware(PrometheusMiddleware)
        app.add_middleware(CorrelationMiddleware)
        app.add_middleware(SecurityHeadersMiddleware)
        app.add_middleware(AuditMiddleware)

    return app


async def _run(app: FastAPI, *, method: str, path: str, requests: int, concurrency: int) -> dict[str, float]:
    transport = httpx.ASGITransport(app=app)
    latencies: list[float] = []

    async with httpx.AsyncClient(transport=transport, base_url="http://bench") as client:
        # Warmup
        for _ in range(50):
            await client.request(method, path, headers={"X-Tenant-ID": "bench"})

        sem = asyncio.Semaphore(concurrency)

        async def _one() -> None:
            async with sem:
                t0 = time.perf_counter()
                await client.request(method, path, headers={"X-Tenant-ID": "bench"})
                latencies.append((time.perf_counter() - t0) * 1000.0)

        start = time.perf_counter()
        await asyncio.gather(*[_one() for _ in range(requests)])
        wall = time.perf_counter() - start

    latencies.sort()
    return {
        "rps": requests / wall,
        "mean_ms": statistics.fmean(latencies),
        "p50_ms": latencies[len(latencies) // 2],
        "p99_ms": latencies[min(len(latencies) - 1, int(len(latencies) * 0.99))],
    }


def _fmt(label: str, r: dict[str, float]) -> str:
    return (
        f"{label:<18} rps={r['rps']:>9.0f}  "
        f"mean={r['mean_ms']:>6.3f}ms  p50={r['p50_ms']:>6.3f}ms  p99={r['p99_ms']:>6.3f}ms"
    )


async def _main_async(requests: int, concurrency: int) -> None:
    bare = _build_app(with_stack=False)
    stacked = _build_app(with_stack=True)

    print(f"# Benchmark: {requests} requests, concurrency={concurrency}\n")

    for method, path in (("GET", "/ping"), ("POST", "/echo")):
        bare_r = await _run(bare, method=method, path=path, requests=requests, concurrency=concurrency)
        stacked_r = await _run(stacked, method=method, path=path, requests=requests, concurrency=concurrency)
        overhead_ms = stacked_r["mean_ms"] - bare_r["mean_ms"]
        overhead_pct = (overhead_ms / bare_r["mean_ms"] * 100.0) if bare_r["mean_ms"] else 0.0

        print(f"## {method} {path}")
        print(_fmt("bare", bare_r))
        print(_fmt("stacked", stacked_r))
        print(f"{'overhead':<18} +{overhead_ms:.3f}ms/req  (+{overhead_pct:.1f}%)\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Middleware-Stack Micro-Benchmark (PERF-MULTIUSER-001)")
    parser.add_argument("--requests", type=int, default=3000)
    parser.add_argument("--concurrency", type=int, default=32)
    args = parser.parse_args()
    asyncio.run(_main_async(args.requests, args.concurrency))


if __name__ == "__main__":
    main()
