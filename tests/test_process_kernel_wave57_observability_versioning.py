"""
Wave 57 — Process Observability + Workflow Versioning Contracts
130+ tests covering spans, traces, health checks, schema versions, migration guards.
"""
import pytest
from datetime import datetime, timedelta

from app.core.process_observability_contracts import (
    SpanStatus, HealthStatus, MetrikEinheit,
    ObservabilitySpan, Trace, HealthCheck, SystemHealthReport,
    get_default_traces, get_default_health_report,
)
from app.core.workflow_versioning_contracts_wave57 import (
    VersionsStatus, MigrationsTyp, KompatibilitaetsTyp,
    WorkflowSchemaVersion, MigrationsSchritt, MigrationsGuard,
    get_default_migrations_guards,
)


# ---------------------------------------------------------------------------
# SpanStatus Enum
# ---------------------------------------------------------------------------

class TestSpanStatus:
    def test_laufend(self):
        assert SpanStatus.LAUFEND == "LAUFEND"

    def test_erfolgreich(self):
        assert SpanStatus.ERFOLGREICH == "ERFOLGREICH"

    def test_fehler(self):
        assert SpanStatus.FEHLER == "FEHLER"

    def test_abgebrochen(self):
        assert SpanStatus.ABGEBROCHEN == "ABGEBROCHEN"

    def test_all_values(self):
        values = {s.value for s in SpanStatus}
        assert values == {"LAUFEND", "ERFOLGREICH", "FEHLER", "ABGEBROCHEN"}


# ---------------------------------------------------------------------------
# HealthStatus Enum
# ---------------------------------------------------------------------------

class TestHealthStatus:
    def test_gesund(self):
        assert HealthStatus.GESUND == "GESUND"

    def test_degradiert(self):
        assert HealthStatus.DEGRADIERT == "DEGRADIERT"

    def test_krank(self):
        assert HealthStatus.KRANK == "KRANK"

    def test_unbekannt(self):
        assert HealthStatus.UNBEKANNT == "UNBEKANNT"


# ---------------------------------------------------------------------------
# MetrikEinheit Enum
# ---------------------------------------------------------------------------

class TestMetrikEinheit:
    def test_millisekunden(self):
        assert MetrikEinheit.MILLISEKUNDEN == "MILLISEKUNDEN"

    def test_anfragen_pro_sekunde(self):
        assert MetrikEinheit.ANFRAGEN_PRO_SEKUNDE == "ANFRAGEN_PRO_SEKUNDE"

    def test_prozent(self):
        assert MetrikEinheit.PROZENT == "PROZENT"

    def test_bytes(self):
        assert MetrikEinheit.BYTES == "BYTES"

    def test_anzahl(self):
        assert MetrikEinheit.ANZAHL == "ANZAHL"


# ---------------------------------------------------------------------------
# ObservabilitySpan
# ---------------------------------------------------------------------------

class TestObservabilitySpan:
    def _make_span(self, status=SpanStatus.ERFOLGREICH, ende_am=None,
                   parent_span_id=None, fehler_nachricht=""):
        now = datetime(2026, 3, 16, 10, 0, 0)
        return ObservabilitySpan(
            span_id="SP-TEST",
            trace_id="TRACE-TEST",
            operation_name="test.op",
            status=status,
            beginn_am=now,
            ende_am=ende_am,
            parent_span_id=parent_span_id,
            tags={},
            fehler_nachricht=fehler_nachricht,
        )

    def test_dauer_ms_none_if_running(self):
        span = self._make_span()
        assert span.dauer_ms() is None

    def test_dauer_ms_correct_calculation(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        span = ObservabilitySpan(
            "SP-T", "TR-T", "op", SpanStatus.ERFOLGREICH,
            now, now + timedelta(milliseconds=150),
        )
        assert span.dauer_ms() == pytest.approx(150.0)

    def test_dauer_ms_zero_if_same_time(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        span = ObservabilitySpan("SP-T", "TR-T", "op", SpanStatus.ERFOLGREICH, now, now)
        assert span.dauer_ms() == pytest.approx(0.0)

    def test_dauer_ms_one_second(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        span = ObservabilitySpan(
            "SP-T", "TR-T", "op", SpanStatus.ERFOLGREICH,
            now, now + timedelta(seconds=1),
        )
        assert span.dauer_ms() == pytest.approx(1000.0)

    def test_dauer_ms_fractional(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        span = ObservabilitySpan(
            "SP-T", "TR-T", "op", SpanStatus.ERFOLGREICH,
            now, now + timedelta(milliseconds=42, microseconds=500),
        )
        # 42.5 ms
        assert span.dauer_ms() == pytest.approx(42.5)

    def test_ist_root_span_true_when_no_parent(self):
        span = self._make_span(parent_span_id=None)
        assert span.ist_root_span() is True

    def test_ist_root_span_false_when_has_parent(self):
        span = self._make_span(parent_span_id="SP-PARENT")
        assert span.ist_root_span() is False

    def test_default_status_laufend(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        span = ObservabilitySpan("SP-T", "TR-T", "op")
        assert span.status == SpanStatus.LAUFEND

    def test_fehler_nachricht_default_empty(self):
        span = self._make_span()
        assert span.fehler_nachricht == ""

    def test_tags_default_empty(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        span = ObservabilitySpan("SP-T", "TR-T", "op")
        assert span.tags == {}

    def test_fehler_span_status(self):
        span = self._make_span(status=SpanStatus.FEHLER, fehler_nachricht="DB error")
        assert span.status == SpanStatus.FEHLER
        assert span.fehler_nachricht == "DB error"

    def test_span_with_tags(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        span = ObservabilitySpan(
            "SP-T", "TR-T", "op", SpanStatus.ERFOLGREICH,
            now, now + timedelta(ms=10) if False else now + timedelta(milliseconds=10),
            None, {"tenant": "X", "env": "prod"}
        )
        assert span.tags["tenant"] == "X"


# ---------------------------------------------------------------------------
# Trace
# ---------------------------------------------------------------------------

class TestTrace:
    def _make_finished_span(self, span_id, trace_id, status, parent_id=None,
                             start_ms=0, end_ms=100, fehler=""):
        base = datetime(2026, 3, 16, 10, 0, 0)
        return ObservabilitySpan(
            span_id, trace_id, "op", status,
            base + timedelta(milliseconds=start_ms),
            base + timedelta(milliseconds=end_ms),
            parent_id, {}, fehler,
        )

    def _make_running_span(self, span_id, trace_id, parent_id=None):
        base = datetime(2026, 3, 16, 10, 0, 0)
        return ObservabilitySpan(span_id, trace_id, "op", SpanStatus.LAUFEND,
                                 base, None, parent_id)

    def test_root_span_returns_span_with_no_parent(self):
        t = Trace("T-001")
        root = self._make_finished_span("SP-R", "T-001", SpanStatus.ERFOLGREICH, None, 0, 50)
        child = self._make_finished_span("SP-C", "T-001", SpanStatus.ERFOLGREICH, "SP-R", 50, 100)
        t.spans = [root, child]
        assert t.root_span().span_id == "SP-R"

    def test_root_span_none_if_all_have_parents(self):
        t = Trace("T-001")
        s1 = self._make_finished_span("SP-1", "T-001", SpanStatus.ERFOLGREICH, "SOME-PARENT")
        s2 = self._make_finished_span("SP-2", "T-001", SpanStatus.ERFOLGREICH, "OTHER")
        t.spans = [s1, s2]
        assert t.root_span() is None

    def test_root_span_none_for_empty_trace(self):
        t = Trace("T-001")
        assert t.root_span() is None

    def test_gesamtdauer_ms_sum_of_all(self):
        t = Trace("T-001")
        s1 = self._make_finished_span("SP-1", "T-001", SpanStatus.ERFOLGREICH, None, 0, 100)
        s2 = self._make_finished_span("SP-2", "T-001", SpanStatus.ERFOLGREICH, "SP-1", 100, 250)
        t.spans = [s1, s2]
        # s1 = 100ms, s2 = 150ms → 250ms
        assert t.gesamtdauer_ms() == pytest.approx(250.0)

    def test_gesamtdauer_ms_none_if_any_running(self):
        t = Trace("T-001")
        s1 = self._make_finished_span("SP-1", "T-001", SpanStatus.ERFOLGREICH, None, 0, 100)
        s2 = self._make_running_span("SP-2", "T-001", "SP-1")
        t.spans = [s1, s2]
        assert t.gesamtdauer_ms() is None

    def test_gesamtdauer_ms_none_for_single_running(self):
        t = Trace("T-001")
        t.spans = [self._make_running_span("SP-1", "T-001")]
        assert t.gesamtdauer_ms() is None

    def test_gesamtdauer_ms_zero_for_empty(self):
        t = Trace("T-001")
        assert t.gesamtdauer_ms() == pytest.approx(0.0)

    def test_fehlerhafte_spans_only_fehler(self):
        t = Trace("T-001")
        s1 = self._make_finished_span("SP-1", "T-001", SpanStatus.ERFOLGREICH, None, 0, 50)
        s2 = self._make_finished_span("SP-2", "T-001", SpanStatus.FEHLER, "SP-1", 50, 100, "err")
        s3 = self._make_finished_span("SP-3", "T-001", SpanStatus.ABGEBROCHEN, "SP-1", 50, 80)
        t.spans = [s1, s2, s3]
        fehler = t.fehlerhafte_spans()
        assert len(fehler) == 1
        assert fehler[0].span_id == "SP-2"

    def test_fehlerhafte_spans_empty_for_all_ok(self):
        t = Trace("T-001")
        s1 = self._make_finished_span("SP-1", "T-001", SpanStatus.ERFOLGREICH, None, 0, 50)
        t.spans = [s1]
        assert t.fehlerhafte_spans() == []

    def test_fehlerhafte_spans_empty_trace(self):
        t = Trace("T-001")
        assert t.fehlerhafte_spans() == []

    def test_erfolgsrate_pct_100_for_empty(self):
        t = Trace("T-001")
        assert t.erfolgsrate_pct() == pytest.approx(100.0)

    def test_erfolgsrate_pct_100_all_erfolgreich(self):
        t = Trace("T-001")
        s1 = self._make_finished_span("SP-1", "T-001", SpanStatus.ERFOLGREICH, None, 0, 50)
        s2 = self._make_finished_span("SP-2", "T-001", SpanStatus.ERFOLGREICH, "SP-1", 50, 100)
        t.spans = [s1, s2]
        assert t.erfolgsrate_pct() == pytest.approx(100.0)

    def test_erfolgsrate_pct_0_none_erfolgreich(self):
        t = Trace("T-001")
        s1 = self._make_finished_span("SP-1", "T-001", SpanStatus.FEHLER, None, 0, 50, "err")
        t.spans = [s1]
        assert t.erfolgsrate_pct() == pytest.approx(0.0)

    def test_erfolgsrate_pct_50(self):
        t = Trace("T-001")
        s1 = self._make_finished_span("SP-1", "T-001", SpanStatus.ERFOLGREICH, None, 0, 50)
        s2 = self._make_finished_span("SP-2", "T-001", SpanStatus.FEHLER, "SP-1", 50, 100, "err")
        t.spans = [s1, s2]
        assert t.erfolgsrate_pct() == pytest.approx(50.0)

    def test_erfolgsrate_pct_two_thirds(self):
        t = Trace("T-001")
        s1 = self._make_finished_span("SP-1", "T-001", SpanStatus.ERFOLGREICH, None, 0, 30)
        s2 = self._make_finished_span("SP-2", "T-001", SpanStatus.ERFOLGREICH, "SP-1", 30, 60)
        s3 = self._make_finished_span("SP-3", "T-001", SpanStatus.FEHLER, "SP-1", 60, 90, "e")
        t.spans = [s1, s2, s3]
        assert t.erfolgsrate_pct() == pytest.approx(200 / 3)

    def test_multiple_fehler_spans(self):
        t = Trace("T-001")
        s1 = self._make_finished_span("SP-1", "T-001", SpanStatus.FEHLER, None, 0, 50, "e1")
        s2 = self._make_finished_span("SP-2", "T-001", SpanStatus.FEHLER, None, 50, 100, "e2")
        s3 = self._make_finished_span("SP-3", "T-001", SpanStatus.ERFOLGREICH, None, 100, 150)
        t.spans = [s1, s2, s3]
        assert len(t.fehlerhafte_spans()) == 2

    def test_default_spans_field_is_list(self):
        t = Trace("T-001")
        assert isinstance(t.spans, list)


# ---------------------------------------------------------------------------
# HealthCheck
# ---------------------------------------------------------------------------

class TestHealthCheck:
    def test_basic_creation(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        hc = HealthCheck("HC-T", "TestComp", HealthStatus.GESUND, "OK", now, 10.0)
        assert hc.check_id == "HC-T"
        assert hc.komponente == "TestComp"
        assert hc.status == HealthStatus.GESUND
        assert hc.antwortzeit_ms == pytest.approx(10.0)

    def test_degradiert_check(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        hc = HealthCheck("HC-D", "Comp", HealthStatus.DEGRADIERT, "Slow", now, 999.0)
        assert hc.status == HealthStatus.DEGRADIERT

    def test_krank_check(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        hc = HealthCheck("HC-K", "Comp", HealthStatus.KRANK, "Down", now, 0.0)
        assert hc.status == HealthStatus.KRANK

    def test_default_nachricht_empty(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        hc = HealthCheck("HC-T", "C", HealthStatus.GESUND)
        assert hc.nachricht == ""

    def test_default_antwortzeit_zero(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        hc = HealthCheck("HC-T", "C", HealthStatus.GESUND)
        assert hc.antwortzeit_ms == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# SystemHealthReport
# ---------------------------------------------------------------------------

class TestSystemHealthReport:
    def _make_check(self, check_id, status):
        now = datetime(2026, 3, 16, 10, 0, 0)
        return HealthCheck(check_id, f"Comp-{check_id}", status, "msg", now, 1.0)

    def test_gesamtstatus_empty_is_gesund(self):
        report = SystemHealthReport("R-T")
        assert report.gesamtstatus() == HealthStatus.GESUND

    def test_gesamtstatus_all_gesund(self):
        report = SystemHealthReport("R-T")
        report.checks = [
            self._make_check("C1", HealthStatus.GESUND),
            self._make_check("C2", HealthStatus.GESUND),
        ]
        assert report.gesamtstatus() == HealthStatus.GESUND

    def test_gesamtstatus_any_krank_wins(self):
        report = SystemHealthReport("R-T")
        report.checks = [
            self._make_check("C1", HealthStatus.GESUND),
            self._make_check("C2", HealthStatus.KRANK),
            self._make_check("C3", HealthStatus.GESUND),
        ]
        assert report.gesamtstatus() == HealthStatus.KRANK

    def test_gesamtstatus_krank_beats_degradiert(self):
        report = SystemHealthReport("R-T")
        report.checks = [
            self._make_check("C1", HealthStatus.DEGRADIERT),
            self._make_check("C2", HealthStatus.KRANK),
        ]
        assert report.gesamtstatus() == HealthStatus.KRANK

    def test_gesamtstatus_degradiert_beats_unbekannt(self):
        report = SystemHealthReport("R-T")
        report.checks = [
            self._make_check("C1", HealthStatus.UNBEKANNT),
            self._make_check("C2", HealthStatus.DEGRADIERT),
        ]
        assert report.gesamtstatus() == HealthStatus.DEGRADIERT

    def test_gesamtstatus_unbekannt_if_no_krank_degradiert(self):
        report = SystemHealthReport("R-T")
        report.checks = [
            self._make_check("C1", HealthStatus.GESUND),
            self._make_check("C2", HealthStatus.UNBEKANNT),
        ]
        assert report.gesamtstatus() == HealthStatus.UNBEKANNT

    def test_gesamtstatus_krank_beats_all(self):
        report = SystemHealthReport("R-T")
        report.checks = [
            self._make_check("C1", HealthStatus.GESUND),
            self._make_check("C2", HealthStatus.DEGRADIERT),
            self._make_check("C3", HealthStatus.UNBEKANNT),
            self._make_check("C4", HealthStatus.KRANK),
        ]
        assert report.gesamtstatus() == HealthStatus.KRANK

    def test_gesunde_komponenten_only_gesund(self):
        report = SystemHealthReport("R-T")
        report.checks = [
            self._make_check("C1", HealthStatus.GESUND),
            self._make_check("C2", HealthStatus.DEGRADIERT),
            self._make_check("C3", HealthStatus.GESUND),
            self._make_check("C4", HealthStatus.KRANK),
        ]
        gesunde = report.gesunde_komponenten()
        assert len(gesunde) == 2
        ids = {c.check_id for c in gesunde}
        assert ids == {"C1", "C3"}

    def test_gesunde_komponenten_empty_if_none_gesund(self):
        report = SystemHealthReport("R-T")
        report.checks = [
            self._make_check("C1", HealthStatus.KRANK),
        ]
        assert report.gesunde_komponenten() == []

    def test_gesunde_komponenten_empty_report(self):
        report = SystemHealthReport("R-T")
        assert report.gesunde_komponenten() == []

    def test_single_krank(self):
        report = SystemHealthReport("R-T")
        report.checks = [self._make_check("C1", HealthStatus.KRANK)]
        assert report.gesamtstatus() == HealthStatus.KRANK

    def test_single_degradiert(self):
        report = SystemHealthReport("R-T")
        report.checks = [self._make_check("C1", HealthStatus.DEGRADIERT)]
        assert report.gesamtstatus() == HealthStatus.DEGRADIERT

    def test_single_unbekannt(self):
        report = SystemHealthReport("R-T")
        report.checks = [self._make_check("C1", HealthStatus.UNBEKANNT)]
        assert report.gesamtstatus() == HealthStatus.UNBEKANNT


# ---------------------------------------------------------------------------
# Default Traces (integration)
# ---------------------------------------------------------------------------

class TestDefaultTraces:
    def setup_method(self):
        self.traces = get_default_traces()
        self.t1 = next(t for t in self.traces if t.trace_id == "TRACE-001")
        self.t2 = next(t for t in self.traces if t.trace_id == "TRACE-002")

    def test_two_traces(self):
        assert len(self.traces) == 2

    def test_trace1_id(self):
        assert self.t1.trace_id == "TRACE-001"

    def test_trace1_three_spans(self):
        assert len(self.t1.spans) == 3

    def test_trace1_erfolgsrate_100(self):
        assert self.t1.erfolgsrate_pct() == pytest.approx(100.0)

    def test_trace1_no_fehlerhafte_spans(self):
        assert len(self.t1.fehlerhafte_spans()) == 0

    def test_trace1_root_span_is_sp001(self):
        root = self.t1.root_span()
        assert root is not None
        assert root.span_id == "SP-001"

    def test_trace1_gesamtdauer_400ms(self):
        # SP-001: 120ms, SP-002: 130ms, SP-003: 150ms → 400ms
        assert self.t1.gesamtdauer_ms() == pytest.approx(400.0)

    def test_trace1_all_spans_erfolgreich(self):
        for span in self.t1.spans:
            assert span.status == SpanStatus.ERFOLGREICH

    def test_trace2_id(self):
        assert self.t2.trace_id == "TRACE-002"

    def test_trace2_two_spans(self):
        assert len(self.t2.spans) == 2

    def test_trace2_one_fehlerhafter_span(self):
        assert len(self.t2.fehlerhafte_spans()) == 1

    def test_trace2_fehlerhafter_span_is_sp005(self):
        assert self.t2.fehlerhafte_spans()[0].span_id == "SP-005"

    def test_trace2_erfolgsrate_50pct(self):
        assert self.t2.erfolgsrate_pct() == pytest.approx(50.0)

    def test_trace2_root_span_is_sp004(self):
        root = self.t2.root_span()
        assert root is not None
        assert root.span_id == "SP-004"

    def test_trace2_gesamtdauer_280ms(self):
        # SP-004: 80ms, SP-005: 120ms → 200ms
        assert self.t2.gesamtdauer_ms() == pytest.approx(200.0)

    def test_trace2_fehler_has_nachricht(self):
        fehler_span = self.t2.fehlerhafte_spans()[0]
        assert "DB" in fehler_span.fehler_nachricht or len(fehler_span.fehler_nachricht) > 0


# ---------------------------------------------------------------------------
# Default Health Report (integration)
# ---------------------------------------------------------------------------

class TestDefaultHealthReport:
    def setup_method(self):
        self.report = get_default_health_report()

    def test_report_id(self):
        assert self.report.report_id == "HR-001"

    def test_five_checks(self):
        assert len(self.report.checks) == 5

    def test_gesamtstatus_degradiert(self):
        # Has DEGRADIERT (NATS) and UNBEKANNT (EDI), no KRANK → DEGRADIERT
        assert self.report.gesamtstatus() == HealthStatus.DEGRADIERT

    def test_drei_gesunde_komponenten(self):
        assert len(self.report.gesunde_komponenten()) == 3

    def test_gesunde_komponenten_ids(self):
        ids = {c.check_id for c in self.report.gesunde_komponenten()}
        assert ids == {"HC-001", "HC-002", "HC-005"}

    def test_datenbank_gesund(self):
        db = next(c for c in self.report.checks if c.check_id == "HC-001")
        assert db.status == HealthStatus.GESUND
        assert db.komponente == "Datenbank"

    def test_nats_degradiert(self):
        nats = next(c for c in self.report.checks if c.check_id == "HC-003")
        assert nats.status == HealthStatus.DEGRADIERT

    def test_edi_unbekannt(self):
        edi = next(c for c in self.report.checks if c.check_id == "HC-004")
        assert edi.status == HealthStatus.UNBEKANNT

    def test_keycloak_gesund(self):
        kc = next(c for c in self.report.checks if c.check_id == "HC-005")
        assert kc.status == HealthStatus.GESUND

    def test_redis_gesund(self):
        redis = next(c for c in self.report.checks if c.check_id == "HC-002")
        assert redis.status == HealthStatus.GESUND

    def test_nats_hohe_antwortzeit(self):
        nats = next(c for c in self.report.checks if c.check_id == "HC-003")
        assert nats.antwortzeit_ms > 100.0

    def test_edi_sehr_hohe_antwortzeit(self):
        edi = next(c for c in self.report.checks if c.check_id == "HC-004")
        assert edi.antwortzeit_ms >= 5000.0


# ---------------------------------------------------------------------------
# VersionsStatus Enum
# ---------------------------------------------------------------------------

class TestVersionsStatus:
    def test_entwurf(self):
        assert VersionsStatus.ENTWURF == "ENTWURF"

    def test_aktiv(self):
        assert VersionsStatus.AKTIV == "AKTIV"

    def test_veraltet(self):
        assert VersionsStatus.VERALTET == "VERALTET"

    def test_zurueckgezogen(self):
        assert VersionsStatus.ZURUECKGEZOGEN == "ZURUECKGEZOGEN"


# ---------------------------------------------------------------------------
# MigrationsTyp Enum
# ---------------------------------------------------------------------------

class TestMigrationsTyp:
    def test_vorwaerts(self):
        assert MigrationsTyp.VORWAERTS == "VORWAERTS"

    def test_rueckwaerts(self):
        assert MigrationsTyp.RUECKWAERTS == "RUECKWAERTS"

    def test_datenmigration(self):
        assert MigrationsTyp.DATENMIGRATION == "DATENMIGRATION"


# ---------------------------------------------------------------------------
# KompatibilitaetsTyp Enum
# ---------------------------------------------------------------------------

class TestKompatibilitaetsTyp:
    def test_vollstaendig(self):
        assert KompatibilitaetsTyp.VOLLSTAENDIG == "VOLLSTAENDIG"

    def test_rueckwaerts(self):
        assert KompatibilitaetsTyp.RUECKWAERTS == "RUECKWAERTS"

    def test_brechend(self):
        assert KompatibilitaetsTyp.BRECHEND == "BRECHEND"


# ---------------------------------------------------------------------------
# WorkflowSchemaVersion
# ---------------------------------------------------------------------------

class TestWorkflowSchemaVersion:
    def _make_version(self, version="1.0.0", status=VersionsStatus.ENTWURF,
                       komp=KompatibilitaetsTyp.VOLLSTAENDIG):
        now = datetime(2026, 3, 16, 10, 0, 0)
        return WorkflowSchemaVersion(
            schema_id="WSV-T",
            workflow_typ="test_workflow",
            version=version,
            status=status,
            kompatibilitaet=komp,
            erstellt_am=now,
        )

    def test_ist_produktiv_true_for_aktiv(self):
        v = self._make_version(status=VersionsStatus.AKTIV)
        assert v.ist_produktiv() is True

    def test_ist_produktiv_false_for_entwurf(self):
        v = self._make_version(status=VersionsStatus.ENTWURF)
        assert v.ist_produktiv() is False

    def test_ist_produktiv_false_for_veraltet(self):
        v = self._make_version(status=VersionsStatus.VERALTET)
        assert v.ist_produktiv() is False

    def test_ist_produktiv_false_for_zurueckgezogen(self):
        v = self._make_version(status=VersionsStatus.ZURUECKGEZOGEN)
        assert v.ist_produktiv() is False

    def test_version_tuple_100(self):
        v = self._make_version("1.0.0")
        assert v.version_tuple() == (1, 0, 0)

    def test_version_tuple_110(self):
        v = self._make_version("1.1.0")
        assert v.version_tuple() == (1, 1, 0)

    def test_version_tuple_200(self):
        v = self._make_version("2.0.0")
        assert v.version_tuple() == (2, 0, 0)

    def test_version_tuple_123(self):
        v = self._make_version("1.2.3")
        assert v.version_tuple() == (1, 2, 3)

    def test_version_tuple_large(self):
        v = self._make_version("10.20.30")
        assert v.version_tuple() == (10, 20, 30)

    def test_version_tuple_invalid_returns_000(self):
        v = self._make_version("invalid")
        assert v.version_tuple() == (0, 0, 0)

    def test_version_tuple_empty_returns_000(self):
        v = self._make_version("")
        assert v.version_tuple() == (0, 0, 0)

    def test_version_tuple_partial_invalid(self):
        v = self._make_version("1.x.0")
        assert v.version_tuple() == (0, 0, 0)

    def test_default_status_entwurf(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        v = WorkflowSchemaVersion("WSV-T", "wf", "1.0.0")
        assert v.status == VersionsStatus.ENTWURF

    def test_default_kompatibilitaet_vollstaendig(self):
        v = WorkflowSchemaVersion("WSV-T", "wf", "1.0.0")
        assert v.kompatibilitaet == KompatibilitaetsTyp.VOLLSTAENDIG

    def test_aktiviert_am_optional_none(self):
        v = WorkflowSchemaVersion("WSV-T", "wf", "1.0.0")
        assert v.aktiviert_am is None


# ---------------------------------------------------------------------------
# MigrationsSchritt
# ---------------------------------------------------------------------------

class TestMigrationsSchritt:
    def test_basic(self):
        ms = MigrationsSchritt("MS-T", MigrationsTyp.VORWAERTS, "1.0.0", "1.1.0", "desc", True)
        assert ms.schritt_id == "MS-T"
        assert ms.migrations_typ == MigrationsTyp.VORWAERTS
        assert ms.von_version == "1.0.0"
        assert ms.zu_version == "1.1.0"
        assert ms.ist_rueckwaerts_kompatibel is True

    def test_breaking_migration(self):
        ms = MigrationsSchritt("MS-T", MigrationsTyp.VORWAERTS, "1.1.0", "2.0.0",
                               "Breaking", False)
        assert ms.ist_rueckwaerts_kompatibel is False

    def test_default_rueckwaerts_kompatibel_true(self):
        ms = MigrationsSchritt("MS-T", MigrationsTyp.VORWAERTS, "1.0.0", "1.1.0")
        assert ms.ist_rueckwaerts_kompatibel is True


# ---------------------------------------------------------------------------
# MigrationsGuard
# ---------------------------------------------------------------------------

class TestMigrationsGuard:
    def _make_guard_with_versions(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        g = MigrationsGuard("MG-T", "test_wf")
        g.versionen = [
            WorkflowSchemaVersion("V1", "test_wf", "1.0.0", VersionsStatus.VERALTET,
                                  KompatibilitaetsTyp.VOLLSTAENDIG, "", now),
            WorkflowSchemaVersion("V2", "test_wf", "1.1.0", VersionsStatus.AKTIV,
                                  KompatibilitaetsTyp.RUECKWAERTS, "", now),
            WorkflowSchemaVersion("V3", "test_wf", "2.0.0", VersionsStatus.ENTWURF,
                                  KompatibilitaetsTyp.BRECHEND, "", now),
        ]
        g.migrationen = [
            MigrationsSchritt("MS-1", MigrationsTyp.VORWAERTS, "1.0.0", "1.1.0", "", True),
            MigrationsSchritt("MS-2", MigrationsTyp.VORWAERTS, "1.1.0", "2.0.0", "", False),
        ]
        return g

    def test_aktive_version_returns_aktiv(self):
        g = self._make_guard_with_versions()
        av = g.aktive_version()
        assert av is not None
        assert av.version == "1.1.0"
        assert av.status == VersionsStatus.AKTIV

    def test_aktive_version_none_if_none_aktiv(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        g = MigrationsGuard("MG-T", "test_wf")
        g.versionen = [
            WorkflowSchemaVersion("V1", "test_wf", "1.0.0", VersionsStatus.VERALTET),
        ]
        assert g.aktive_version() is None

    def test_aktive_version_none_for_empty(self):
        g = MigrationsGuard("MG-T", "test_wf")
        assert g.aktive_version() is None

    def test_neueste_version_max_by_tuple(self):
        g = self._make_guard_with_versions()
        nv = g.neueste_version()
        assert nv is not None
        assert nv.version == "2.0.0"

    def test_neueste_version_none_for_empty(self):
        g = MigrationsGuard("MG-T", "test_wf")
        assert g.neueste_version() is None

    def test_neueste_version_single(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        g = MigrationsGuard("MG-T", "test_wf")
        g.versionen = [WorkflowSchemaVersion("V1", "test_wf", "1.0.0", VersionsStatus.AKTIV)]
        assert g.neueste_version().version == "1.0.0"

    def test_hat_brechende_aenderung_false_if_kompatibel(self):
        g = self._make_guard_with_versions()
        # MS-1: 1.0.0 → 1.1.0, ist_rueckwaerts_kompatibel=True, target RUECKWAERTS (not BRECHEND)
        assert g.hat_brechende_aenderung("1.0.0", "1.1.0") is False

    def test_hat_brechende_aenderung_true_if_not_kompatibel(self):
        g = self._make_guard_with_versions()
        # MS-2: 1.1.0 → 2.0.0, ist_rueckwaerts_kompatibel=False
        assert g.hat_brechende_aenderung("1.1.0", "2.0.0") is True

    def test_hat_brechende_aenderung_true_if_target_brechend(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        g = MigrationsGuard("MG-T", "test_wf")
        g.versionen = [
            WorkflowSchemaVersion("V1", "test_wf", "1.0.0", VersionsStatus.AKTIV,
                                  KompatibilitaetsTyp.BRECHEND),
        ]
        g.migrationen = []
        # No matching migration, but target version is BRECHEND
        assert g.hat_brechende_aenderung("0.9.0", "1.0.0") is True

    def test_hat_brechende_aenderung_false_unknown_path_non_brechend_target(self):
        g = self._make_guard_with_versions()
        # No migration 0.9.0 → 1.0.0, target 1.0.0 is VOLLSTAENDIG
        assert g.hat_brechende_aenderung("0.9.0", "1.0.0") is False

    def test_hat_brechende_aenderung_empty_migrationen(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        g = MigrationsGuard("MG-T", "test_wf")
        g.versionen = [
            WorkflowSchemaVersion("V1", "test_wf", "1.0.0", VersionsStatus.AKTIV,
                                  KompatibilitaetsTyp.VOLLSTAENDIG),
        ]
        g.migrationen = []
        assert g.hat_brechende_aenderung("1.0.0", "1.0.0") is False


# ---------------------------------------------------------------------------
# Default MigrationsGuards (integration)
# ---------------------------------------------------------------------------

class TestDefaultMigrationsGuards:
    def setup_method(self):
        self.guards = get_default_migrations_guards()
        self.g1 = next(g for g in self.guards if g.guard_id == "MG-001")
        self.g2 = next(g for g in self.guards if g.guard_id == "MG-002")

    def test_two_guards(self):
        assert len(self.guards) == 2

    def test_mg001_workflow_typ(self):
        assert self.g1.workflow_typ == "kontrakt_freigabe"

    def test_mg001_drei_versionen(self):
        assert len(self.g1.versionen) == 3

    def test_mg001_zwei_migrationen(self):
        assert len(self.g1.migrationen) == 2

    def test_mg001_aktive_version_200(self):
        av = self.g1.aktive_version()
        assert av is not None
        assert av.version == "2.0.0"

    def test_mg001_neueste_version_200(self):
        nv = self.g1.neueste_version()
        assert nv is not None
        assert nv.version == "2.0.0"

    def test_mg001_v100_veraltet(self):
        v = next(v for v in self.g1.versionen if v.version == "1.0.0")
        assert v.status == VersionsStatus.VERALTET

    def test_mg001_v110_veraltet(self):
        v = next(v for v in self.g1.versionen if v.version == "1.1.0")
        assert v.status == VersionsStatus.VERALTET

    def test_mg001_v200_aktiv(self):
        v = next(v for v in self.g1.versionen if v.version == "2.0.0")
        assert v.status == VersionsStatus.AKTIV

    def test_mg001_v200_brechend(self):
        v = next(v for v in self.g1.versionen if v.version == "2.0.0")
        assert v.kompatibilitaet == KompatibilitaetsTyp.BRECHEND

    def test_mg001_v200_ist_produktiv(self):
        v = next(v for v in self.g1.versionen if v.version == "2.0.0")
        assert v.ist_produktiv() is True

    def test_mg001_v100_nicht_produktiv(self):
        v = next(v for v in self.g1.versionen if v.version == "1.0.0")
        assert v.ist_produktiv() is False

    def test_mg001_ms002_nicht_kompatibel(self):
        ms = next(m for m in self.g1.migrationen if m.schritt_id == "MS-002")
        assert ms.ist_rueckwaerts_kompatibel is False

    def test_mg001_ms001_kompatibel(self):
        ms = next(m for m in self.g1.migrationen if m.schritt_id == "MS-001")
        assert ms.ist_rueckwaerts_kompatibel is True

    def test_mg001_hat_brechend_110_200_true(self):
        assert self.g1.hat_brechende_aenderung("1.1.0", "2.0.0") is True

    def test_mg001_hat_brechend_100_110_false(self):
        assert self.g1.hat_brechende_aenderung("1.0.0", "1.1.0") is False

    def test_mg002_workflow_typ(self):
        assert self.g2.workflow_typ == "ap_rechnung"

    def test_mg002_aktive_version_100(self):
        av = self.g2.aktive_version()
        assert av is not None
        assert av.version == "1.0.0"

    def test_mg002_neueste_version_100(self):
        nv = self.g2.neueste_version()
        assert nv is not None
        assert nv.version == "1.0.0"

    def test_mg002_keine_migrationen(self):
        assert len(self.g2.migrationen) == 0

    def test_mg002_eine_version(self):
        assert len(self.g2.versionen) == 1

    def test_mg001_v100_version_tuple(self):
        v = next(v for v in self.g1.versionen if v.version == "1.0.0")
        assert v.version_tuple() == (1, 0, 0)

    def test_mg001_v200_version_tuple(self):
        v = next(v for v in self.g1.versionen if v.version == "2.0.0")
        assert v.version_tuple() == (2, 0, 0)
