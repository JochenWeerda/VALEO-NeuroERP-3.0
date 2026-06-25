"""
locustfile.py — PERF-MULTIUSER-001 Lasttest gegen die laufende API

Validiert das Verhalten des HTTP-Hotpaths (Middleware-Stack, Runtime) unter
echter Multi-User-Concurrency gegen einen laufenden Backend-Prozess.

Bewusst leichte Endpunkte, um Runtime/Middleware statt DB-Last zu messen:
  - GET /healthz          (kein Auth, kein DB)
  - GET /api/v1/status    (Auth + Tenant-Context + voller Middleware-Stack)

Aufruf (headless), Beispiel 100 User, 30s:
    locust -f scripts/loadtest/locustfile.py --headless \
        -u 100 -r 50 -t 30s --host http://127.0.0.1:8000 \
        --only-summary --csv reports/loadtest/perf_100

Umgebung:
    NEUROERP_URL   (optional, sonst --host)
    NEUROERP_TOKEN (Bearer-Token, Default 'dev-token')
    NEUROERP_TENANT(Tenant-ID, Default 'default')
"""
from __future__ import annotations

import os

from locust import HttpUser, between, task

_TOKEN = os.getenv("NEUROERP_TOKEN", "dev-token")
_TENANT = os.getenv("NEUROERP_TENANT", "default")

_AUTH_HEADERS = {
    "Authorization": f"Bearer {_TOKEN}",
    "X-Tenant-ID": _TENANT,
}


class ErpUser(HttpUser):
    """Simuliert einen ERP-Nutzer mit kurzem Think-Time-Fenster."""

    wait_time = between(0.1, 0.5)

    @task(3)
    def health(self) -> None:
        # Liveness — kein Auth, kein DB; misst reine Runtime/Stack-Latenz
        self.client.get("/healthz", name="GET /healthz")

    @task(5)
    def status(self) -> None:
        # Voller Middleware-Stack: Auth, Tenant-Context, Security-Header, Audit-Skip
        self.client.get("/api/v1/status", headers=_AUTH_HEADERS, name="GET /api/v1/status")
