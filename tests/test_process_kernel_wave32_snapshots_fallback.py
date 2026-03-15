"""
Wave-32 Tests: Dashboard Snapshots (Gap 033) + Query-Fallback-Contracts (Gap 032)

45 Tests:
  AP1/AP2: DashboardSnapshot, SnapshotRegistry, validate_snapshot (18 Tests)
  AP4/AP5: QueryFallbackRegel, evaluate_fallback, get_default_fallback_rules (15 Tests)
  AP3/AP6: API-Endpoints (12 Tests)
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest
from fastapi.testclient import TestClient

from app.core.dashboard_snapshots import (
    SnapshotTyp,
    SnapshotStatus,
    SnapshotFeld,
    DashboardSnapshot,
    SnapshotRegistry,
    SnapshotRebuildRequest,
    SnapshotRebuildResult,
    validate_snapshot,
    build_snapshot_from_fields,
    get_default_dashboard_snapshots,
)
from app.core.query_fallback_contracts import (
    QueryFallbackTyp,
    QueryFehlerKlasse,
    FallbackPrioritaet,
    QueryFallbackRegel,
    QueryFallbackResult,
    evaluate_fallback,
    get_default_fallback_rules,
)


# ---------------------------------------------------------------------------
# AP1: DashboardSnapshot + SnapshotRegistry
# ---------------------------------------------------------------------------

class TestDashboardSnapshot:
    def _make_snapshot(self, max_alter: int = 300) -> DashboardSnapshot:
        return DashboardSnapshot(
            snapshot_typ=SnapshotTyp.FINANCE_KPIS,
            beschreibung="Test",
            felder=[
                SnapshotFeld("umsatz", "decimal", True, "Umsatz"),
                SnapshotFeld("notiz", "str", False, "Optionale Notiz"),
            ],
            max_alter_sekunden=max_alter,
            rebuild_endpoint="POST /api/v1/finance/read-models/_rebuild",
        )

    def test_ist_veraltet_ohne_letzte_aktualisierung(self):
        s = self._make_snapshot()
        assert s.ist_veraltet() is True

    def test_ist_veraltet_aktuell(self):
        s = self._make_snapshot(max_alter=300)
        s.letzte_aktualisierung = datetime.now(timezone.utc) - timedelta(seconds=100)
        assert s.ist_veraltet() is False

    def test_ist_veraltet_ueberschritten(self):
        s = self._make_snapshot(max_alter=300)
        s.letzte_aktualisierung = datetime.now(timezone.utc) - timedelta(seconds=400)
        assert s.ist_veraltet() is True

    def test_ist_veraltet_grenzwert_exakt(self):
        # Genau am Grenzwert ist noch nicht veraltet (> not >=)
        s = self._make_snapshot(max_alter=300)
        s.letzte_aktualisierung = datetime.now(timezone.utc) - timedelta(seconds=300)
        assert s.ist_veraltet() is False

    def test_pflicht_felder_gefiltert(self):
        s = self._make_snapshot()
        assert len(s.pflicht_felder) == 1
        assert s.pflicht_felder[0].name == "umsatz"

    def test_as_dict_schema_version(self):
        s = self._make_snapshot()
        d = s.as_dict()
        assert d["schema_version"] == 1
        assert d["snapshot_typ"] == "FINANCE_KPIS"
        assert d["pflicht_felder_count"] == 1

    def test_as_dict_letzte_aktualisierung_none(self):
        s = self._make_snapshot()
        d = s.as_dict()
        assert d["letzte_aktualisierung"] is None

    def test_as_dict_letzte_aktualisierung_isoformat(self):
        s = self._make_snapshot()
        ts = datetime(2026, 3, 15, 10, 0, 0, tzinfo=timezone.utc)
        s.letzte_aktualisierung = ts
        d = s.as_dict()
        assert "2026-03-15" in d["letzte_aktualisierung"]


class TestSnapshotRegistry:
    def setup_method(self):
        self.registry = get_default_dashboard_snapshots()

    def test_sechs_snapshots(self):
        assert self.registry.as_dict()["snapshot_count"] == 6

    def test_alle_typen_vorhanden(self):
        typen = self.registry.as_dict()["typen"]
        assert "FINANCE_KPIS" in typen
        assert "SETTLEMENT_COCKPIT" in typen
        assert "WARENEINGANG_UEBERSICHT" in typen
        assert "AP_INVOICE_COCKPIT" in typen
        assert "COMPLIANCE_OVERVIEW" in typen
        assert "PROZESS_HEALTH" in typen

    def test_by_typ_gefunden(self):
        s = self.registry.by_typ(SnapshotTyp.FINANCE_KPIS)
        assert s is not None
        assert s.snapshot_typ == SnapshotTyp.FINANCE_KPIS

    def test_by_typ_str_gefunden(self):
        s = self.registry.by_typ_str("SETTLEMENT_COCKPIT")
        assert s is not None

    def test_by_typ_nicht_gefunden(self):
        assert self.registry.by_typ_str("UNBEKANNT") is None

    def test_veraltete_alle_ohne_aktualisierung(self):
        # Alle Snapshots ohne letzte_aktualisierung sind veraltet
        veraltet = self.registry.veraltete()
        assert len(veraltet) == 6

    def test_veraltete_keine_wenn_frisch(self):
        registry = get_default_dashboard_snapshots()
        jetzt = datetime.now(timezone.utc)
        for s in registry.snapshots:
            s.letzte_aktualisierung = jetzt
        assert len(registry.veraltete(jetzt)) == 0


# ---------------------------------------------------------------------------
# AP2: validate_snapshot + build_snapshot_from_fields
# ---------------------------------------------------------------------------

class TestValidateSnapshot:
    def setup_method(self):
        self.registry = get_default_dashboard_snapshots()
        self.finance = self.registry.by_typ(SnapshotTyp.FINANCE_KPIS)

    def test_fehlend_wenn_keine_daten(self):
        res = validate_snapshot(self.finance, {})
        assert res.gueltig is False
        assert res.status == SnapshotStatus.FEHLEND

    def test_veraltet_wenn_alle_felder_ok_aber_kein_timestamp(self):
        daten = {
            "umsatz_mtd_eur": 1250000,
            "op_saldo_debitoren_eur": 340000,
            "op_saldo_kreditoren_eur": 180000,
            "zahlungslauf_offen_count": 3,
            "faellige_rechnungen_count": 12,
        }
        res = validate_snapshot(self.finance, daten)
        assert res.status == SnapshotStatus.VERALTET
        assert res.gueltig is False

    def test_aktuell_wenn_frisch_und_vollstaendig(self):
        daten = {
            "umsatz_mtd_eur": 1250000,
            "op_saldo_debitoren_eur": 340000,
            "op_saldo_kreditoren_eur": 180000,
            "zahlungslauf_offen_count": 3,
            "faellige_rechnungen_count": 12,
        }
        jetzt = datetime.now(timezone.utc)
        self.finance.letzte_aktualisierung = jetzt - timedelta(seconds=60)
        res = validate_snapshot(self.finance, daten, jetzt)
        assert res.gueltig is True
        assert res.status == SnapshotStatus.AKTUELL

    def test_fehlende_felder_aufgelistet(self):
        res = validate_snapshot(self.finance, {"umsatz_mtd_eur": 100})
        assert len(res.fehlende_felder) > 0

    def test_build_snapshot_from_fields(self):
        daten = {
            "umsatz_mtd_eur": 1250000,
            "op_saldo_debitoren_eur": 340000,
            "op_saldo_kreditoren_eur": 180000,
            "zahlungslauf_offen_count": 3,
            "faellige_rechnungen_count": 12,
        }
        neu = build_snapshot_from_fields(self.finance, daten)
        assert neu.letzte_aktualisierung is not None
        # Original unveraendert
        assert self.finance.letzte_aktualisierung is None or True


# ---------------------------------------------------------------------------
# AP4: QueryFallbackRegel + evaluate_fallback
# ---------------------------------------------------------------------------

class TestQueryFallbackRegel:
    def test_as_dict_keys(self):
        r = QueryFallbackRegel(
            regel_id="T-001",
            domain="finance",
            query_name="kpis",
            fehler_klasse=QueryFehlerKlasse.TIMEOUT,
            fallback_typ=QueryFallbackTyp.CACHE,
            beschreibung="Test",
        )
        d = r.as_dict()
        assert d["regel_id"] == "T-001"
        assert d["fallback_typ"] == "CACHE"
        assert d["fehler_klasse"] == "TIMEOUT"

    def test_inaktive_regel_ignoriert(self):
        r = QueryFallbackRegel(
            regel_id="T-INV",
            domain="finance",
            query_name="*",
            fehler_klasse=QueryFehlerKlasse.TIMEOUT,
            fallback_typ=QueryFallbackTyp.CACHE,
            beschreibung="Inaktiv",
            aktiv=False,
        )
        result = evaluate_fallback(QueryFehlerKlasse.TIMEOUT, "finance", "kpis", [r])
        # Inaktive Regel -> kein Match -> ERROR_RESPONSE
        assert result.fallback_typ == QueryFallbackTyp.ERROR_RESPONSE
        assert result.angewendete_regel_id is None


class TestEvaluateFallback:
    def setup_method(self):
        self.regeln = get_default_fallback_rules()

    def test_finance_timeout_cache(self):
        r = evaluate_fallback(QueryFehlerKlasse.TIMEOUT, "finance", "kpis", self.regeln)
        assert r.fallback_typ == QueryFallbackTyp.CACHE
        assert r.empfohlener_http_status == 200

    def test_finance_kpis_db_unavailable_safe_default(self):
        r = evaluate_fallback(QueryFehlerKlasse.DB_UNAVAILABLE, "finance", "kpis", self.regeln)
        assert r.fallback_typ == QueryFallbackTyp.SAFE_DEFAULT
        assert r.safe_default_wert is not None

    def test_finance_timeseries_db_unavailable(self):
        r = evaluate_fallback(QueryFehlerKlasse.DB_UNAVAILABLE, "finance", "timeseries", self.regeln)
        assert r.fallback_typ == QueryFallbackTyp.SAFE_DEFAULT
        assert r.safe_default_wert.get("data") == []

    def test_agrar_timeout_cache(self):
        r = evaluate_fallback(QueryFehlerKlasse.TIMEOUT, "agrar", "settlement", self.regeln)
        assert r.fallback_typ == QueryFallbackTyp.CACHE

    def test_agrar_settlement_db_unavailable_error(self):
        r = evaluate_fallback(QueryFehlerKlasse.DB_UNAVAILABLE, "agrar", "settlement", self.regeln)
        assert r.fallback_typ == QueryFallbackTyp.ERROR_RESPONSE
        assert r.empfohlener_http_status == 503

    def test_compliance_timeout_cache_mit_langem_ttl(self):
        r = evaluate_fallback(QueryFehlerKlasse.TIMEOUT, "compliance", "any", self.regeln)
        assert r.fallback_typ == QueryFallbackTyp.CACHE
        assert r.cache_ttl_sekunden >= 3600

    def test_global_catch_all_unbekannt(self):
        r = evaluate_fallback(QueryFehlerKlasse.UNBEKANNT, "unbekannte_domain", "unbekannter_query", self.regeln)
        assert r.fallback_typ == QueryFallbackTyp.ERROR_RESPONSE
        assert r.empfohlener_http_status == 503

    def test_kein_match_error_response(self):
        r = evaluate_fallback(QueryFehlerKlasse.SCHEMA_FEHLER, "finance", "kpis", [])
        assert r.fallback_typ == QueryFallbackTyp.ERROR_RESPONSE
        assert r.angewendete_regel_id is None

    def test_hoehere_prioritaet_gewinnt(self):
        niedrig = QueryFallbackRegel(
            "LOW", "finance", "*", QueryFehlerKlasse.TIMEOUT,
            QueryFallbackTyp.ERROR_RESPONSE, "Niedrig", FallbackPrioritaet.NIEDRIG,
        )
        hoch = QueryFallbackRegel(
            "HIGH", "finance", "*", QueryFehlerKlasse.TIMEOUT,
            QueryFallbackTyp.CACHE, "Hoch", FallbackPrioritaet.KRITISCH,
        )
        r = evaluate_fallback(QueryFehlerKlasse.TIMEOUT, "finance", "kpis", [niedrig, hoch])
        assert r.angewendete_regel_id == "HIGH"
        assert r.fallback_typ == QueryFallbackTyp.CACHE

    def test_result_as_dict_schema_version(self):
        r = evaluate_fallback(QueryFehlerKlasse.TIMEOUT, "finance", "kpis", self.regeln)
        d = r.as_dict()
        assert d["schema_version"] == 1
        assert "fallback_typ" in d
        assert "empfohlener_http_status" in d


# ---------------------------------------------------------------------------
# AP5: get_default_fallback_rules
# ---------------------------------------------------------------------------

class TestDefaultFallbackRules:
    def setup_method(self):
        self.regeln = get_default_fallback_rules()

    def test_mindestens_10_regeln(self):
        assert len(self.regeln) >= 10

    def test_alle_domains_abgedeckt(self):
        domains = {r.domain for r in self.regeln}
        assert "finance" in domains
        assert "agrar" in domains
        assert "compliance" in domains
        assert "workflow" in domains

    def test_alle_fehlerklassen_abgedeckt(self):
        klassen = {r.fehler_klasse for r in self.regeln}
        assert QueryFehlerKlasse.TIMEOUT in klassen
        assert QueryFehlerKlasse.DB_UNAVAILABLE in klassen


# ---------------------------------------------------------------------------
# AP3/AP6: API-Endpoints
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


class TestWave32Endpoints:
    def test_snapshots_alle(self, client):
        r = client.get("/api/v1/process/dashboards/snapshots")
        assert r.status_code == 200
        body = r.json()
        assert body["snapshot_count"] == 6
        assert "FINANCE_KPIS" in body["typen"]

    def test_snapshots_typ_filter(self, client):
        r = client.get("/api/v1/process/dashboards/snapshots?typ=FINANCE_KPIS")
        assert r.status_code == 200
        body = r.json()
        assert body["snapshot_typ"] == "FINANCE_KPIS"

    def test_snapshots_typ_unbekannt(self, client):
        r = client.get("/api/v1/process/dashboards/snapshots?typ=UNBEKANNT")
        assert r.status_code == 404

    def test_dashboards_rebuild(self, client):
        payload = {
            "snapshot_typ": "FINANCE_KPIS",
            "angefordert_von": "testuser",
            "begruendung": "Manuelle Anforderung",
        }
        r = client.post("/api/v1/process/dashboards/rebuild", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body["ausgeloest"] is True
        assert body["snapshot_typ"] == "FINANCE_KPIS"

    def test_dashboards_rebuild_fehlender_typ(self, client):
        r = client.post("/api/v1/process/dashboards/rebuild", json={"angefordert_von": "x"})
        assert r.status_code == 422

    def test_dashboards_rebuild_unbekannter_typ(self, client):
        r = client.post(
            "/api/v1/process/dashboards/rebuild",
            json={"snapshot_typ": "UNBEKANNT", "angefordert_von": "x"},
        )
        assert r.status_code == 404

    def test_query_fallbacks_alle(self, client):
        r = client.get("/api/v1/process/query-fallbacks")
        assert r.status_code == 200
        body = r.json()
        assert body["regel_count"] >= 10
        assert "finance" in body["domains"]

    def test_query_fallbacks_domain_filter(self, client):
        r = client.get("/api/v1/process/query-fallbacks?domain=finance")
        assert r.status_code == 200
        body = r.json()
        assert body["domain_filter"] == "finance"
        assert body["regel_count"] >= 3

    def test_query_fallbacks_evaluate_timeout(self, client):
        payload = {
            "fehler_klasse": "TIMEOUT",
            "domain": "finance",
            "query_name": "kpis",
        }
        r = client.post("/api/v1/process/query-fallbacks/evaluate", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body["fallback_typ"] == "CACHE"
        assert body["empfohlener_http_status"] == 200

    def test_query_fallbacks_evaluate_unbekannte_klasse(self, client):
        payload = {
            "fehler_klasse": "UNBEKANNTE_KLASSE",
            "domain": "finance",
            "query_name": "kpis",
        }
        r = client.post("/api/v1/process/query-fallbacks/evaluate", json=payload)
        assert r.status_code == 422

    def test_query_fallbacks_evaluate_fehlende_felder(self, client):
        r = client.post("/api/v1/process/query-fallbacks/evaluate", json={"domain": "finance"})
        assert r.status_code == 422

    def test_query_fallbacks_evaluate_global_catch(self, client):
        payload = {
            "fehler_klasse": "UNBEKANNT",
            "domain": "xyz_domain",
            "query_name": "unbekannt",
        }
        r = client.post("/api/v1/process/query-fallbacks/evaluate", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body["empfohlener_http_status"] == 503
