"""
locustfile.py — Echter Lasttest Erntepeak mit Locust (Gap 037)

Ausführung:
    # Interaktiv im Browser (http://localhost:8089)
    python -m locust -f load-tests/locustfile.py --host http://localhost:8000

    # Headless (CI) — 500 User, 30 Minuten
    python -m locust -f load-tests/locustfile.py \\
        --host http://localhost:8000 \\
        --users 500 --spawn-rate 8 --run-time 30m --headless \\
        --csv load-tests/results/erntepeak

    # Baseline — 50 User, 3 Minuten
    python -m locust -f load-tests/locustfile.py \\
        --host http://localhost:8000 \\
        --users 50 --spawn-rate 5 --run-time 3m --headless \\
        --csv load-tests/results/baseline

SLA-Ziele (Gap 037):
    Error Rate < 1%, p95 global < 2000ms, p95 Dashboard < 250ms
"""

import os
import random
from locust import HttpUser, between, task, events

API_TOKEN = os.getenv("API_TOKEN", "dev-token")
TENANT_POOL = [
    "T-GENOSSENSCHAFT-001",
    "T-GENOSSENSCHAFT-002",
    "T-GENOSSENSCHAFT-003",
    "T-LANDHANDEL-001",
    "T-LANDHANDEL-002",
]

def _headers():
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
        "X-Tenant-ID": random.choice(TENANT_POOL),
    }

def _ok(resp):
    """Alles < 500 gilt als Erfolg (404 = nicht vorhanden aber kein Serverfehler)."""
    return resp.status_code < 500


# ---------------------------------------------------------------------------
# Disponent / Geschäftsführung — liest Dashboards & KPIs (40% der Last)
# SLA: p95 < 250ms  (Gap 033 Read-Models)
# ---------------------------------------------------------------------------
class DisponentUser(HttpUser):
    weight = 40
    wait_time = between(0.5, 2.0)

    @task(5)
    def get_dashboards(self):
        with self.client.get(
            "/api/v1/controlling/dashboards",
            headers=_headers(),
            name="[Dashboard] /controlling/dashboards",
            catch_response=True,
        ) as r:
            if _ok(r):
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")

    @task(5)
    def get_kpis(self):
        with self.client.get(
            "/api/v1/controlling/kpis",
            headers=_headers(),
            name="[Dashboard] /controlling/kpis",
            catch_response=True,
        ) as r:
            if _ok(r):
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")

    @task(3)
    def get_timeseries(self):
        kpi = random.choice(["UMSATZ", "MARGE", "LAGERBESTAND"])
        with self.client.get(
            f"/api/v1/controlling/timeseries?kpi={kpi}",
            headers=_headers(),
            name="[Dashboard] /controlling/timeseries",
            catch_response=True,
        ) as r:
            if _ok(r):
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")

    @task(2)
    def get_controlling_actions(self):
        with self.client.get(
            "/api/v1/controlling/actions?limit=20",
            headers=_headers(),
            name="[Dashboard] /controlling/actions",
            catch_response=True,
        ) as r:
            if _ok(r):
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")


# ---------------------------------------------------------------------------
# Waagen-Operator — gibt Annahmen und Qualitätsdaten ein (30% der Last)
# SLA: p95 < 1000ms
# ---------------------------------------------------------------------------
class WaagenOperatorUser(HttpUser):
    weight = 30
    wait_time = between(1.0, 3.0)

    @task(4)
    def get_harvest_acceptance(self):
        with self.client.get(
            "/api/v1/agrar/harvest-acceptance?status=offen&limit=10",
            headers=_headers(),
            name="[Annahme] /agrar/harvest-acceptance",
            catch_response=True,
        ) as r:
            if _ok(r):
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")

    @task(3)
    def get_contracts(self):
        with self.client.get(
            "/api/v1/agrar/contracts?status=aktiv&limit=20",
            headers=_headers(),
            name="[Annahme] /agrar/contracts",
            catch_response=True,
        ) as r:
            if _ok(r):
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")

    @task(2)
    def get_quality_protocols(self):
        with self.client.get(
            "/api/v1/agrar/quality-protocols?limit=5",
            headers=_headers(),
            name="[Annahme] /agrar/quality-protocols",
            catch_response=True,
        ) as r:
            if _ok(r):
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")

    @task(1)
    def get_daily_prices(self):
        with self.client.get(
            "/api/v1/agrar/daily-prices?limit=10",
            headers=_headers(),
            name="[Annahme] /agrar/daily-prices",
            catch_response=True,
        ) as r:
            if _ok(r):
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")


# ---------------------------------------------------------------------------
# Buchhalter — liest OP-Listen und Zahlungsläufe (20% der Last)
# SLA: p95 < 500ms
# ---------------------------------------------------------------------------
class BuchhaltungUser(HttpUser):
    weight = 20
    wait_time = between(1.0, 4.0)

    @task(4)
    def get_open_items_kreditor(self):
        with self.client.get(
            "/api/v1/finance/open-items?typ=kreditor&limit=50",
            headers=_headers(),
            name="[Finance] /finance/open-items?typ=kreditor",
            catch_response=True,
        ) as r:
            if _ok(r):
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")

    @task(3)
    def get_payment_runs(self):
        with self.client.get(
            "/api/v1/finance/payment-runs?limit=20",
            headers=_headers(),
            name="[Finance] /finance/payment-runs",
            catch_response=True,
        ) as r:
            if _ok(r):
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")

    @task(2)
    def get_open_items_debitor(self):
        with self.client.get(
            "/api/v1/finance/open-items?typ=debitor&limit=50",
            headers=_headers(),
            name="[Finance] /finance/open-items?typ=debitor",
            catch_response=True,
        ) as r:
            if _ok(r):
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")


# ---------------------------------------------------------------------------
# Abrechnungssachbearbeiter — Settlements (10% der Last)
# SLA: p95 < 2000ms
# ---------------------------------------------------------------------------
class AbrechnungUser(HttpUser):
    weight = 10
    wait_time = between(2.0, 5.0)

    @task(3)
    def get_settlements(self):
        with self.client.get(
            "/api/v1/agrar/settlements/?limit=20",
            headers=_headers(),
            name="[Settlement] /agrar/settlements",
            catch_response=True,
        ) as r:
            if _ok(r):
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")

    @task(2)
    def get_self_billing(self):
        with self.client.get(
            "/api/v1/agrar/self-billing?limit=10",
            headers=_headers(),
            name="[Settlement] /agrar/self-billing",
            catch_response=True,
        ) as r:
            if _ok(r):
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")

    @task(1)
    def get_drying_rules(self):
        with self.client.get(
            "/api/v1/agrar/settlements/drying-rules?limit=10",
            headers=_headers(),
            name="[Settlement] /agrar/settlements/drying-rules",
            catch_response=True,
        ) as r:
            if _ok(r):
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")


# ---------------------------------------------------------------------------
# SLA-Auswertung nach Testende
# ---------------------------------------------------------------------------
@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    stats = environment.stats
    total = stats.total

    if total.num_requests == 0:
        print("\n[WARN] Keine Requests gemessen — Test korrekt konfiguriert?\n")
        return

    p95_ms   = total.get_response_time_percentile(0.95) or 0
    err_rate = total.fail_ratio * 100

    print("\n" + "="*60)
    print("VALEO ERNTEPEAK-LASTTEST — SLA-AUSWERTUNG (Gap 037)")
    print("="*60)
    print(f"  Requests gesamt : {total.num_requests:>8,}")
    print(f"  Fehler gesamt   : {total.num_failures:>8,}")
    print(f"  Error Rate      : {err_rate:>7.2f}%   Ziel: < 1.0%")
    print(f"  p95 global      : {p95_ms:>7.0f}ms  Ziel: < 2000ms")
    print(f"  Throughput      : {total.current_rps:>7.1f} req/s")
    print()

    # Dashboard-Endpunkte (Gap 033)
    dashboard_p95_max = 0.0
    for key, entry in stats.entries.items():
        name = key[0] if isinstance(key, tuple) else str(key)
        if "[Dashboard]" in name:
            p95 = entry.get_response_time_percentile(0.95) or 0
            dashboard_p95_max = max(dashboard_p95_max, p95)
            marker = "OK  " if p95 <= 250 else "FAIL"
            print(f"  [{marker}] {name:<50} p95={p95:.0f}ms")

    print()
    violations = []
    if err_rate > 1.0:
        violations.append(f"Error Rate {err_rate:.2f}% > 1.0%")
    if p95_ms > 2000:
        violations.append(f"p95 global {p95_ms:.0f}ms > 2000ms")
    if dashboard_p95_max > 250:
        violations.append(f"Dashboard p95 {dashboard_p95_max:.0f}ms > 250ms (Gap 033)")

    if violations:
        for v in violations:
            print(f"  [FAIL] {v}")
        print("\n  Gap 037 NICHT erfuellt.")
        environment.process_exit_code = 1
    else:
        print("  [PASS] Alle SLA-Ziele eingehalten.")
        print("\n  Gap 037 erfuellt: Stack stabil unter Last.")
    print("="*60 + "\n")
