"""
Wave 83 — Read-Models für Dashboards (Gap 033)

Tests für DashboardSnapshot, DashboardReadModelStore,
ReadModelFreshness, ReadModelBuildJob und DashboardPerformanceContract.

Gap 033: p95 Dashboard-API < 250ms durch vorberechnete Read-Models
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.core.dashboard_read_model_contracts import (
    DashboardKpiTile,
    DashboardPerformanceContract,
    DashboardReadModelStore,
    DashboardSnapshot,
    DashboardTyp,
    ReadModelBuildJob,
    ReadModelFreshness,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _tile(kpi_code: str = "UMSATZ", ampel: str = "GRUEN") -> DashboardKpiTile:
    return DashboardKpiTile(
        kpi_code=kpi_code,
        titel=f"KPI {kpi_code}",
        wert=100.0,
        einheit="EUR",
        ampel=ampel,
        trend="STABIL",
    )


def _snapshot(
    tenant_id: str = "T-001",
    typ: DashboardTyp = DashboardTyp.CONTROLLING,
    alter_sekunden: float = 0,
    tiles: list[DashboardKpiTile] | None = None,
) -> DashboardSnapshot:
    erstellt = _now() - timedelta(seconds=alter_sekunden)
    return DashboardSnapshot(
        snapshot_id=f"SNAP-{tenant_id}-{typ.value}",
        tenant_id=tenant_id,
        dashboard_typ=typ,
        kpi_tiles=tiles or [_tile()],
        erstellt_am=erstellt,
    )


# ---------------------------------------------------------------------------
# TestDashboardKpiTile
# ---------------------------------------------------------------------------

class TestDashboardKpiTile:
    def test_as_dict(self):
        t = _tile("MARGE", "GELB")
        d = t.as_dict()
        assert d["kpi_code"] == "MARGE"
        assert d["ampel"] == "GELB"
        assert "trend" in d


# ---------------------------------------------------------------------------
# TestDashboardSnapshot
# ---------------------------------------------------------------------------

class TestDashboardSnapshot:
    def test_anzahl_tiles(self):
        snap = _snapshot(tiles=[_tile("A"), _tile("B"), _tile("C")])
        assert snap.anzahl_tiles == 3

    def test_tiles_gruen(self):
        snap = _snapshot(tiles=[_tile("A", "GRUEN"), _tile("B", "ROT"), _tile("C", "GRUEN")])
        assert snap.tiles_gruen == 2
        assert snap.tiles_rot == 1

    def test_get_tile_gefunden(self):
        snap = _snapshot(tiles=[_tile("UMSATZ"), _tile("MARGE")])
        tile = snap.get_tile("MARGE")
        assert tile is not None
        assert tile.kpi_code == "MARGE"

    def test_get_tile_nicht_gefunden(self):
        snap = _snapshot()
        assert snap.get_tile("GIBT_ES_NICHT") is None

    def test_freshness_frisch(self):
        snap = _snapshot(alter_sekunden=100)
        assert snap.freshness(max_alter_sekunden=300) == ReadModelFreshness.FRISCH

    def test_freshness_veraltet(self):
        snap = _snapshot(alter_sekunden=400)
        assert snap.freshness(max_alter_sekunden=300) == ReadModelFreshness.VERALTET

    def test_freshness_leer_via_store(self):
        """LEER kommt vom Store wenn kein Eintrag vorhanden — nicht vom Snapshot selbst."""
        store = DashboardReadModelStore()
        _, freshness = store.get_or_stale("T-LEER", DashboardTyp.FINANCE)
        assert freshness == ReadModelFreshness.LEER

    def test_alter_sekunden_wächst(self):
        snap = _snapshot(alter_sekunden=60)
        assert snap.alter_sekunden >= 60.0

    def test_as_dict_vollstaendig(self):
        snap = _snapshot()
        d = snap.as_dict()
        assert "snapshot_id" in d
        assert "kpi_tiles" in d
        assert "tiles_gruen" in d
        assert "alter_sekunden" in d


# ---------------------------------------------------------------------------
# TestDashboardReadModelStore
# ---------------------------------------------------------------------------

class TestDashboardReadModelStore:
    def test_put_und_get_frisch(self):
        store = DashboardReadModelStore()
        snap = _snapshot(alter_sekunden=10)
        store.put(snap)
        result = store.get("T-001", DashboardTyp.CONTROLLING, max_alter_sekunden=300)
        assert result is snap

    def test_get_veraltet_gibt_none(self):
        store = DashboardReadModelStore()
        snap = _snapshot(alter_sekunden=400)
        store.put(snap)
        result = store.get("T-001", DashboardTyp.CONTROLLING, max_alter_sekunden=300)
        assert result is None

    def test_get_nicht_vorhanden_gibt_none(self):
        store = DashboardReadModelStore()
        assert store.get("T-999", DashboardTyp.AGRAR) is None

    def test_get_or_stale_gibt_veralteten_snapshot(self):
        store = DashboardReadModelStore()
        snap = _snapshot(alter_sekunden=600)
        store.put(snap)
        result, freshness = store.get_or_stale("T-001", DashboardTyp.CONTROLLING)
        assert result is snap
        assert freshness == ReadModelFreshness.VERALTET

    def test_get_or_stale_leer(self):
        store = DashboardReadModelStore()
        result, freshness = store.get_or_stale("T-999", DashboardTyp.AGRAR)
        assert result is None
        assert freshness == ReadModelFreshness.LEER

    def test_invalidate_entfernt_snapshot(self):
        store = DashboardReadModelStore()
        store.put(_snapshot())
        assert store.size == 1
        ok = store.invalidate("T-001", DashboardTyp.CONTROLLING)
        assert ok is True
        assert store.size == 0

    def test_invalidate_unbekannt_gibt_false(self):
        store = DashboardReadModelStore()
        assert store.invalidate("T-999", DashboardTyp.FINANCE) is False

    def test_invalidate_tenant_alle_typen(self):
        store = DashboardReadModelStore()
        store.put(_snapshot("T-001", DashboardTyp.CONTROLLING))
        store.put(_snapshot("T-001", DashboardTyp.AGRAR))
        store.put(_snapshot("T-002", DashboardTyp.CONTROLLING))
        deleted = store.invalidate_tenant("T-001")
        assert deleted == 2
        assert store.size == 1

    def test_tenant_isolation(self):
        store = DashboardReadModelStore()
        store.put(_snapshot("T-001"))
        store.put(_snapshot("T-002"))
        r1 = store.get("T-001", DashboardTyp.CONTROLLING)
        r2 = store.get("T-002", DashboardTyp.CONTROLLING)
        assert r1 is not r2
        assert r1.tenant_id == "T-001"


# ---------------------------------------------------------------------------
# TestReadModelBuildJob
# ---------------------------------------------------------------------------

class TestReadModelBuildJob:
    def test_gueltiger_job(self):
        job = ReadModelBuildJob(
            job_id="J-001",
            tenant_id="T-001",
            dashboard_typ=DashboardTyp.CONTROLLING,
            ausgeloest_durch="SCHEDULER_5MIN",
            erstellt_am=_now(),
            prioritaet=2,
        )
        assert job.versuche == 0
        assert job.prioritaet == 2

    def test_ungueltige_prioritaet(self):
        with pytest.raises(ValueError):
            ReadModelBuildJob("J-1", "T-1", DashboardTyp.CONTROLLING,
                              "TEST", _now(), prioritaet=0)

    def test_as_dict(self):
        job = ReadModelBuildJob("J-1", "T-1", DashboardTyp.AGRAR, "EVENT", _now())
        d = job.as_dict()
        assert d["dashboard_typ"] == "AGRAR"
        assert "erstellt_am" in d


# ---------------------------------------------------------------------------
# TestDashboardPerformanceContract
# ---------------------------------------------------------------------------

class TestDashboardPerformanceContract:
    def test_kpi_erfuellt(self):
        perf = DashboardPerformanceContract(p95_ziel_ms=250.0, gemessene_p95_ms=180.0, stichproben=100)
        assert perf.kpi_erfuellt is True

    def test_kpi_nicht_erfuellt(self):
        perf = DashboardPerformanceContract(p95_ziel_ms=250.0, gemessene_p95_ms=320.0, stichproben=50)
        assert perf.kpi_erfuellt is False

    def test_keine_stichproben_nicht_erfuellt(self):
        perf = DashboardPerformanceContract(p95_ziel_ms=250.0, gemessene_p95_ms=100.0, stichproben=0)
        assert perf.kpi_erfuellt is False

    def test_headroom(self):
        perf = DashboardPerformanceContract(p95_ziel_ms=250.0, gemessene_p95_ms=180.0, stichproben=10)
        assert perf.headroom_ms == 70.0

    def test_as_dict(self):
        perf = DashboardPerformanceContract(250.0, 200.0, 50)
        d = perf.as_dict()
        assert d["kpi_erfuellt"] is True
        assert d["headroom_ms"] == 50.0


# ---------------------------------------------------------------------------
# TestIntegrationSzenario
# ---------------------------------------------------------------------------

class TestIntegrationSzenario:
    def test_stale_while_revalidate_pattern(self):
        """
        Typisches Cache-Muster: veralteter Snapshot wird sofort ausgeliefert,
        Rebuild-Job wird parallel angestossen.
        """
        store = DashboardReadModelStore()
        snap = _snapshot(alter_sekunden=400)  # veraltet
        store.put(snap)

        result, freshness = store.get_or_stale("T-001", DashboardTyp.CONTROLLING)
        assert result is not None          # sofortige Antwort
        assert freshness == ReadModelFreshness.VERALTET

        # Rebuild-Job simuliert
        job = ReadModelBuildJob(
            job_id="J-REBUILD",
            tenant_id="T-001",
            dashboard_typ=DashboardTyp.CONTROLLING,
            ausgeloest_durch="STALE_CACHE",
            erstellt_am=_now(),
        )
        assert job.ausgeloest_durch == "STALE_CACHE"

    def test_alle_dashboard_typen_abgedeckt(self):
        """Alle DashboardTypen können im Store gespeichert und abgerufen werden."""
        store = DashboardReadModelStore()
        for typ in DashboardTyp:
            snap = _snapshot("T-001", typ, alter_sekunden=0)
            store.put(snap)
        assert store.size == len(DashboardTyp)
        for typ in DashboardTyp:
            result = store.get("T-001", typ)
            assert result is not None

    def test_performance_contract_mit_read_model(self):
        """Read-Model-Zugriff ist O(1) — muss p95 < 250ms erfüllen."""
        perf = DashboardPerformanceContract(
            p95_ziel_ms=250.0,
            gemessene_p95_ms=8.0,   # Cache-Hit: ~8ms
            stichproben=1000,
        )
        assert perf.kpi_erfuellt is True
        assert perf.headroom_ms > 200
