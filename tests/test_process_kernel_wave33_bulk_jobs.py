"""
Wave 33 — Tests: API-Bulk-Operationen (Gap 034) + Background-Jobs (Gap 036)

AP1/AP2: bulk_operations.py — BulkRequest/Result/Validation, Domain-Limits
AP3:     process_kernel_api.py — GET /process/bulk-limits, POST /process/bulk-operations/validate
AP4/AP5: background_jobs.py — JobQueue, Routing, Job-Katalog
AP6:     process_kernel_api.py — GET /process/jobs, POST /process/jobs/enqueue
"""
import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app, raise_server_exceptions=True)


# ---------------------------------------------------------------------------
# AP1/AP2 — bulk_operations.py
# ---------------------------------------------------------------------------

class TestBulkOperationsCore:

    def setup_method(self):
        from app.core.bulk_operations import (
            BulkItem,
            BulkItemStatus,
            BulkLimit,
            BulkOperationTyp,
            BulkRequest,
            get_default_bulk_limits,
            validate_bulk_request,
        )
        self.BulkItem = BulkItem
        self.BulkLimit = BulkLimit
        self.BulkOperationTyp = BulkOperationTyp
        self.BulkRequest = BulkRequest
        self.BulkItemStatus = BulkItemStatus
        self.get_default_bulk_limits = get_default_bulk_limits
        self.validate_bulk_request = validate_bulk_request

    def _make_items(self, n: int):
        return [
            self.BulkItem(item_id=f"item-{i}", payload={"wert": i})
            for i in range(n)
        ]

    def test_bulk_item_default_status_pending(self):
        item = self.BulkItem(item_id="x", payload={"a": 1})
        assert item.status == self.BulkItemStatus.PENDING

    def test_bulk_item_as_dict(self):
        item = self.BulkItem(item_id="x", payload={"a": 1})
        d = item.as_dict()
        assert d["item_id"] == "x"
        assert d["status"] == "PENDING"
        assert d["fehler_code"] is None

    def test_bulk_request_as_dict_contains_item_count(self):
        req = self.BulkRequest(
            operation_typ=self.BulkOperationTyp.CREATE,
            domain="agrar",
            ressource="wiegescheine",
            items=self._make_items(5),
        )
        d = req.as_dict()
        assert d["item_count"] == 5
        assert d["operation_typ"] == "CREATE"

    def test_validate_bulk_request_valid(self):
        req = self.BulkRequest(
            operation_typ=self.BulkOperationTyp.CREATE,
            domain="agrar",
            ressource="wiegescheine",
            items=self._make_items(10),
        )
        result = self.validate_bulk_request(req)
        assert result.gueltig is True
        assert result.fehler == []

    def test_validate_bulk_request_empty_items(self):
        req = self.BulkRequest(
            operation_typ=self.BulkOperationTyp.CREATE,
            domain="agrar",
            ressource="wiegescheine",
            items=[],
        )
        result = self.validate_bulk_request(req)
        assert result.gueltig is False
        assert any("keine" in f.lower() or "items" in f.lower() for f in result.fehler)

    def test_validate_bulk_request_exceeds_limit(self):
        from app.core.bulk_operations import BulkLimit
        lim = BulkLimit(
            domain="agrar",
            max_items_pro_request=5,
            max_requests_pro_minute=10,
            max_payload_bytes=1024,
            erlaubte_operationen=[self.BulkOperationTyp.CREATE],
            beschreibung="Test-Limit",
        )
        req = self.BulkRequest(
            operation_typ=self.BulkOperationTyp.CREATE,
            domain="agrar",
            ressource="test",
            items=self._make_items(10),
        )
        result = self.validate_bulk_request(req, lim)
        assert result.gueltig is False
        assert any("limit" in f.lower() or "viele" in f.lower() for f in result.fehler)

    def test_validate_bulk_request_operation_not_allowed(self):
        from app.core.bulk_operations import BulkLimit
        lim = BulkLimit(
            domain="finance",
            max_items_pro_request=200,
            max_requests_pro_minute=30,
            max_payload_bytes=1024,
            erlaubte_operationen=[self.BulkOperationTyp.CREATE],
            beschreibung="Finance-Limit ohne DELETE",
        )
        req = self.BulkRequest(
            operation_typ=self.BulkOperationTyp.DELETE,
            domain="finance",
            ressource="rechnungen",
            items=self._make_items(2),
        )
        result = self.validate_bulk_request(req, lim)
        assert result.gueltig is False
        assert any("erlaubt" in f.lower() or "operation" in f.lower() for f in result.fehler)

    def test_validate_bulk_request_missing_item_id(self):
        items = [self.BulkItem(item_id="", payload={"x": 1})]
        req = self.BulkRequest(
            operation_typ=self.BulkOperationTyp.CREATE,
            domain="agrar",
            ressource="x",
            items=items,
        )
        result = self.validate_bulk_request(req)
        assert result.gueltig is False

    def test_validate_bulk_request_empty_payload(self):
        items = [self.BulkItem(item_id="i1", payload={})]
        req = self.BulkRequest(
            operation_typ=self.BulkOperationTyp.CREATE,
            domain="agrar",
            ressource="x",
            items=items,
        )
        result = self.validate_bulk_request(req)
        assert result.gueltig is False

    def test_validate_bulk_request_warning_near_limit(self):
        from app.core.bulk_operations import BulkLimit
        lim = BulkLimit(
            domain="agrar",
            max_items_pro_request=10,
            max_requests_pro_minute=10,
            max_payload_bytes=1024,
            erlaubte_operationen=[self.BulkOperationTyp.CREATE],
            beschreibung="Test",
        )
        # 10 items, limit 10 → exactly at limit → no warning (not >90% and not exceeded)
        # 9 items of 10 → 90% exactly → no warning (strict >90%)
        # 10 items of 10 → exactly limit → limit error, not warning
        # Let's use 10 items of 11 limit → 9/10 * 11 = ~9.9 → 9 items < 90%
        # Instead test near limit: 19 of 20
        lim2 = BulkLimit(
            domain="agrar",
            max_items_pro_request=20,
            max_requests_pro_minute=10,
            max_payload_bytes=1024,
            erlaubte_operationen=[self.BulkOperationTyp.CREATE],
            beschreibung="Test",
        )
        req = self.BulkRequest(
            operation_typ=self.BulkOperationTyp.CREATE,
            domain="agrar",
            ressource="x",
            items=self._make_items(19),  # 95% of 20
        )
        result = self.validate_bulk_request(req, lim2)
        assert result.gueltig is True
        assert len(result.warnungen) > 0

    def test_default_bulk_limits_mindestens_vier(self):
        limits = self.get_default_bulk_limits()
        assert len(limits) >= 4

    def test_default_bulk_limits_domains(self):
        limits = self.get_default_bulk_limits()
        domains = {lim.domain for lim in limits}
        assert "agrar" in domains
        assert "finance" in domains
        assert "compliance" in domains
        assert "workflow" in domains

    def test_agrar_limit_hoeher_als_workflow(self):
        limits = self.get_default_bulk_limits()
        agrar = next(lim for lim in limits if lim.domain == "agrar")
        workflow = next(lim for lim in limits if lim.domain == "workflow")
        assert agrar.max_items_pro_request > workflow.max_items_pro_request

    def test_finance_kein_delete(self):
        from app.core.bulk_operations import BulkOperationTyp
        limits = self.get_default_bulk_limits()
        finance = next(lim for lim in limits if lim.domain == "finance")
        assert BulkOperationTyp.DELETE not in finance.erlaubte_operationen

    def test_bulk_limit_as_dict(self):
        limits = self.get_default_bulk_limits()
        d = limits[0].as_dict()
        assert "domain" in d
        assert "max_items_pro_request" in d
        assert "erlaubte_operationen" in d

    def test_bulk_result_success_rate(self):
        from app.core.bulk_operations import BulkResult, BulkOperationTyp
        result = BulkResult(
            operation_typ=BulkOperationTyp.CREATE,
            domain="agrar",
            ressource="x",
            total=10,
            success_count=8,
            fehler_count=2,
            skip_count=0,
        )
        assert result.success_rate == pytest.approx(0.8)

    def test_bulk_result_success_rate_zero_total(self):
        from app.core.bulk_operations import BulkResult, BulkOperationTyp
        result = BulkResult(
            operation_typ=BulkOperationTyp.CREATE,
            domain="agrar",
            ressource="x",
            total=0,
            success_count=0,
            fehler_count=0,
            skip_count=0,
        )
        assert result.success_rate == 0.0

    def test_bulk_result_as_dict(self):
        from app.core.bulk_operations import BulkResult, BulkOperationTyp
        result = BulkResult(
            operation_typ=BulkOperationTyp.CREATE,
            domain="agrar",
            ressource="x",
            total=5,
            success_count=5,
            fehler_count=0,
            skip_count=0,
        )
        d = result.as_dict()
        assert d["total"] == 5
        assert d["success_count"] == 5
        assert "success_rate" in d

    def test_get_bulk_limit_by_domain(self):
        from app.core.bulk_operations import get_bulk_limit_by_domain
        lim = get_bulk_limit_by_domain("agrar")
        assert lim is not None
        assert lim.domain == "agrar"

    def test_get_bulk_limit_by_domain_unbekannt(self):
        from app.core.bulk_operations import get_bulk_limit_by_domain
        lim = get_bulk_limit_by_domain("unbekannt_xyz")
        assert lim is None


# ---------------------------------------------------------------------------
# AP4/AP5 — background_jobs.py
# ---------------------------------------------------------------------------

class TestBackgroundJobsCore:

    def setup_method(self):
        from app.core.background_jobs import (
            BackgroundJob,
            JobEnqueueRequest,
            JobPrioritaet,
            JobQueue,
            JobRoutingResult,
            JobStatus,
            JobTyp,
            WorkerKlasse,
            create_job_from_request,
            evaluate_job_routing,
            get_default_job_types,
        )
        self.BackgroundJob = BackgroundJob
        self.JobEnqueueRequest = JobEnqueueRequest
        self.JobPrioritaet = JobPrioritaet
        self.JobQueue = JobQueue
        self.JobStatus = JobStatus
        self.JobTyp = JobTyp
        self.WorkerKlasse = WorkerKlasse
        self.create_job_from_request = create_job_from_request
        self.evaluate_job_routing = evaluate_job_routing
        self.get_default_job_types = get_default_job_types

    def _make_job(self, typ=None, prio=None):
        from datetime import datetime, timezone
        return self.BackgroundJob(
            job_id="job-001",
            typ=typ or self.JobTyp.REPORT_GENERATION,
            status=self.JobStatus.PENDING,
            prioritaet=prio or self.JobPrioritaet.MITTEL,
            angefordert_von="system",
            erstellt_am=datetime.now(timezone.utc),
        )

    def test_background_job_as_dict(self):
        job = self._make_job()
        d = job.as_dict()
        assert d["status"] == "PENDING"
        assert d["typ"] == "REPORT_GENERATION"
        assert d["laufzeit_sekunden"] is None

    def test_job_ist_abgeschlossen_completed(self):
        from datetime import datetime, timezone
        job = self.BackgroundJob(
            job_id="x",
            typ=self.JobTyp.EDI_EXPORT,
            status=self.JobStatus.COMPLETED,
            prioritaet=self.JobPrioritaet.HOCH,
            angefordert_von="user",
            erstellt_am=datetime.now(timezone.utc),
        )
        assert job.ist_abgeschlossen is True

    def test_job_ist_abgeschlossen_pending(self):
        job = self._make_job()
        assert job.ist_abgeschlossen is False

    def test_laufzeit_sekunden_wenn_abgeschlossen(self):
        from datetime import datetime, timezone, timedelta
        start = datetime.now(timezone.utc)
        end = start + timedelta(seconds=42)
        job = self.BackgroundJob(
            job_id="x",
            typ=self.JobTyp.REPORT_GENERATION,
            status=self.JobStatus.COMPLETED,
            prioritaet=self.JobPrioritaet.MITTEL,
            angefordert_von="u",
            erstellt_am=start,
            gestartet_am=start,
            abgeschlossen_am=end,
        )
        assert job.laufzeit_sekunden == pytest.approx(42.0)

    def test_job_queue_enqueue_dequeue(self):
        q = self.JobQueue()
        job = self._make_job()
        job_id = q.enqueue(job)
        assert job_id == job.job_id
        assert q.pending_count() == 1
        dequeued = q.dequeue()
        assert dequeued is not None
        assert dequeued.status == self.JobStatus.RUNNING
        assert q.pending_count() == 0

    def test_job_queue_prioritaet_reihenfolge(self):
        q = self.JobQueue()
        low = self._make_job(prio=self.JobPrioritaet.NIEDRIG)
        low.job_id = "low"
        high = self._make_job(prio=self.JobPrioritaet.KRITISCH)
        high.job_id = "high"
        q.enqueue(low)
        q.enqueue(high)
        first = q.dequeue()
        assert first.job_id == "high"

    def test_job_queue_dequeue_leer(self):
        q = self.JobQueue()
        assert q.dequeue() is None

    def test_job_queue_cancel(self):
        q = self.JobQueue()
        job = self._make_job()
        q.enqueue(job)
        result = q.cancel(job.job_id)
        assert result is True
        assert q.pending_count() == 0

    def test_job_queue_cancel_nicht_gefunden(self):
        q = self.JobQueue()
        result = q.cancel("ghost-id")
        assert result is False

    def test_job_queue_by_typ(self):
        q = self.JobQueue()
        j1 = self._make_job(typ=self.JobTyp.REPORT_GENERATION)
        j1.job_id = "r1"
        j2 = self._make_job(typ=self.JobTyp.EDI_EXPORT)
        j2.job_id = "e1"
        q.enqueue(j1)
        q.enqueue(j2)
        reports = q.by_typ(self.JobTyp.REPORT_GENERATION)
        assert len(reports) == 1
        assert reports[0].job_id == "r1"

    def test_evaluate_job_routing_settlement_finance(self):
        result = self.evaluate_job_routing(self.JobTyp.SETTLEMENT_BATCH)
        assert result.worker_klasse == self.WorkerKlasse.FINANCE
        assert result.prioritaet == self.JobPrioritaet.HOCH
        assert result.timeout_sekunden > 0

    def test_evaluate_job_routing_preis_kritisch(self):
        result = self.evaluate_job_routing(self.JobTyp.PREIS_AKTUALISIERUNG)
        assert result.prioritaet == self.JobPrioritaet.KRITISCH

    def test_evaluate_job_routing_as_dict(self):
        result = self.evaluate_job_routing(self.JobTyp.SNAPSHOT_REBUILD)
        d = result.as_dict()
        assert "worker_klasse" in d
        assert "timeout_sekunden" in d
        assert d["schema_version"] == 1

    def test_get_default_job_types_count(self):
        job_types = self.get_default_job_types()
        assert len(job_types) >= 8

    def test_get_default_job_types_alle_idempotent_check(self):
        job_types = self.get_default_job_types()
        # Settlement und Snapshot sind idempotent
        settlement = next(j for j in job_types if j.typ == self.JobTyp.SETTLEMENT_BATCH)
        assert settlement.idempotent is True
        # E-Mail-Kampagne ist NICHT idempotent
        email = next(j for j in job_types if j.typ == self.JobTyp.EMAIL_KAMPAGNE)
        assert email.idempotent is False

    def test_job_definition_as_dict(self):
        job_types = self.get_default_job_types()
        d = job_types[0].as_dict()
        assert "typ" in d
        assert "worker_klasse" in d
        assert "idempotent" in d

    def test_create_job_from_request(self):
        req = self.JobEnqueueRequest(
            typ=self.JobTyp.REPORT_GENERATION,
            angefordert_von="user-42",
            parameter={"report_typ": "INTRASTAT"},
        )
        job, routing = self.create_job_from_request(req)
        assert job.status == self.JobStatus.PENDING
        assert job.typ == self.JobTyp.REPORT_GENERATION
        assert job.job_id != ""
        assert routing.worker_klasse == self.WorkerKlasse.REPORTING

    def test_create_job_prioritaet_override(self):
        req = self.JobEnqueueRequest(
            typ=self.JobTyp.EMAIL_KAMPAGNE,
            angefordert_von="u",
            prioritaet_override=self.JobPrioritaet.KRITISCH,
        )
        job, _ = self.create_job_from_request(req)
        assert job.prioritaet == self.JobPrioritaet.KRITISCH

    def test_create_job_uuid_einzigartig(self):
        req = self.JobEnqueueRequest(
            typ=self.JobTyp.SNAPSHOT_REBUILD,
            angefordert_von="u",
        )
        job1, _ = self.create_job_from_request(req)
        job2, _ = self.create_job_from_request(req)
        assert job1.job_id != job2.job_id


# ---------------------------------------------------------------------------
# AP3 — GET /process/bulk-limits + POST /process/bulk-operations/validate
# ---------------------------------------------------------------------------

class TestBulkLimitsEndpoints:

    def test_get_bulk_limits_alle(self, client):
        resp = client.get("/api/v1/process/bulk-limits")
        assert resp.status_code == 200
        data = resp.json()
        assert "limit_count" in data
        assert data["limit_count"] >= 4
        assert "domains" in data
        assert "limits" in data

    def test_get_bulk_limits_agrar(self, client):
        resp = client.get("/api/v1/process/bulk-limits?domain=agrar")
        assert resp.status_code == 200
        data = resp.json()
        assert data["domain"] == "agrar"
        assert "limit" in data

    def test_get_bulk_limits_unbekannte_domain(self, client):
        resp = client.get("/api/v1/process/bulk-limits?domain=unbekannt_xyz")
        assert resp.status_code == 404

    def test_post_bulk_validate_valid(self, client):
        payload = {
            "operation_typ": "CREATE",
            "domain": "agrar",
            "ressource": "wiegescheine",
            "items": [
                {"item_id": f"ws-{i}", "payload": {"gewicht": i * 1000}}
                for i in range(5)
            ],
        }
        resp = client.post("/api/v1/process/bulk-operations/validate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["gueltig"] is True
        assert data["item_count"] == 5

    def test_post_bulk_validate_fehlende_pflichtfelder(self, client):
        resp = client.post(
            "/api/v1/process/bulk-operations/validate",
            json={"operation_typ": "CREATE"},
        )
        assert resp.status_code == 422

    def test_post_bulk_validate_ungueltige_operation(self, client):
        payload = {
            "operation_typ": "UNGUELTIG",
            "domain": "agrar",
            "ressource": "x",
            "items": [{"item_id": "i1", "payload": {"x": 1}}],
        }
        resp = client.post("/api/v1/process/bulk-operations/validate", json=payload)
        assert resp.status_code == 422

    def test_post_bulk_validate_finance_no_delete(self, client):
        payload = {
            "operation_typ": "DELETE",
            "domain": "finance",
            "ressource": "rechnungen",
            "items": [{"item_id": "r1", "payload": {"id": "r1"}}],
        }
        resp = client.post("/api/v1/process/bulk-operations/validate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        # Finance-Limit verbietet DELETE -> ungueltig
        assert data["gueltig"] is False

    def test_post_bulk_validate_too_many_items_finance(self, client):
        # Finance limit: 200 items max
        items = [{"item_id": f"i-{i}", "payload": {"x": i}} for i in range(250)]
        payload = {
            "operation_typ": "CREATE",
            "domain": "finance",
            "ressource": "buchungen",
            "items": items,
        }
        resp = client.post("/api/v1/process/bulk-operations/validate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["gueltig"] is False


# ---------------------------------------------------------------------------
# AP6 — GET /process/jobs + POST /process/jobs/enqueue
# ---------------------------------------------------------------------------

class TestJobsEndpoints:

    def test_get_jobs_alle(self, client):
        resp = client.get("/api/v1/process/jobs")
        assert resp.status_code == 200
        data = resp.json()
        assert "job_type_count" in data
        assert data["job_type_count"] >= 8
        assert "definitions" in data

    def test_get_jobs_filter_settlement(self, client):
        resp = client.get("/api/v1/process/jobs?typ=SETTLEMENT_BATCH")
        assert resp.status_code == 200
        data = resp.json()
        assert data["typ"] == "SETTLEMENT_BATCH"
        assert "routing" in data
        assert "definition" in data

    def test_get_jobs_unbekannter_typ(self, client):
        resp = client.get("/api/v1/process/jobs?typ=GHOST_JOB")
        assert resp.status_code == 404

    def test_post_jobs_enqueue_valid(self, client):
        payload = {
            "typ": "REPORT_GENERATION",
            "angefordert_von": "user-123",
            "parameter": {"report_typ": "INTRASTAT", "periode": "2025-03"},
        }
        resp = client.post("/api/v1/process/jobs/enqueue", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "job_id" in data
        assert data["typ"] == "REPORT_GENERATION"
        assert data["status"] == "PENDING"
        assert "worker_klasse" in data
        assert data["schema_version"] == 1

    def test_post_jobs_enqueue_job_id_nicht_leer(self, client):
        payload = {
            "typ": "SNAPSHOT_REBUILD",
            "angefordert_von": "system",
        }
        resp = client.post("/api/v1/process/jobs/enqueue", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["job_id"]) > 0

    def test_post_jobs_enqueue_zwei_calls_unterschiedliche_ids(self, client):
        payload = {"typ": "EDI_EXPORT", "angefordert_von": "user"}
        r1 = client.post("/api/v1/process/jobs/enqueue", json=payload)
        r2 = client.post("/api/v1/process/jobs/enqueue", json=payload)
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json()["job_id"] != r2.json()["job_id"]

    def test_post_jobs_enqueue_fehlende_pflichtfelder(self, client):
        resp = client.post("/api/v1/process/jobs/enqueue", json={"typ": "EDI_EXPORT"})
        assert resp.status_code == 422

    def test_post_jobs_enqueue_unbekannter_typ(self, client):
        payload = {"typ": "GHOST_JOB", "angefordert_von": "u"}
        resp = client.post("/api/v1/process/jobs/enqueue", json=payload)
        assert resp.status_code == 422

    def test_post_jobs_enqueue_prioritaet_override(self, client):
        payload = {
            "typ": "EMAIL_KAMPAGNE",
            "angefordert_von": "u",
            "prioritaet_override": "KRITISCH",
        }
        resp = client.post("/api/v1/process/jobs/enqueue", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["prioritaet"] == "KRITISCH"

    def test_post_jobs_enqueue_ungueltige_prioritaet(self, client):
        payload = {
            "typ": "REPORT_GENERATION",
            "angefordert_von": "u",
            "prioritaet_override": "SUPER_KRITISCH",
        }
        resp = client.post("/api/v1/process/jobs/enqueue", json=payload)
        assert resp.status_code == 422

    def test_post_jobs_enqueue_preis_aktualisierung_kritisch(self, client):
        payload = {
            "typ": "PREIS_AKTUALISIERUNG",
            "angefordert_von": "markt-feed",
            "parameter": {"markt": "MATIF"},
        }
        resp = client.post("/api/v1/process/jobs/enqueue", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["prioritaet"] == "KRITISCH"

    def test_get_jobs_settlement_routing_finance_worker(self, client):
        resp = client.get("/api/v1/process/jobs?typ=SETTLEMENT_BATCH")
        assert resp.status_code == 200
        data = resp.json()
        assert data["routing"]["worker_klasse"] == "FINANCE"

    def test_get_jobs_heartbeat(self, client):
        resp = client.get("/api/v1/process/jobs/heartbeat")
        assert resp.status_code == 200
        data = resp.json()
        assert "scheduler_id" in data
        assert "worker_id" in data
        assert "heartbeat" in data
        assert data["heartbeat"]["status"] in {"ACTIVE", "DEGRADED", "STALE"}
        assert data["schema_version"] == 1

    def test_get_jobs_heartbeat_recovery(self, client):
        resp = client.get("/api/v1/process/jobs/heartbeat/recovery")
        assert resp.status_code == 200
        data = resp.json()
        assert data["heartbeat_status"] in {"ACTIVE", "DEGRADED", "STALE"}
        assert "recovery_plan" in data
        assert "notification_preview" in data
        assert data["recovery_plan"]["scheduler_id"] == data["scheduler_id"]
        assert data["recovery_plan"]["actions"]
        assert data["notification_preview"]["ausloeser"] == "ESKALATION"
