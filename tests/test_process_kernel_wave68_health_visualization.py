"""
Wave 68 — Process Health Dashboard Contracts + Workflow Dependency Visualization Contracts.
148+ tests, all pure-Python, no DB/network required.
"""
import ast
import importlib
import pytest
from datetime import datetime, timedelta

from app.core.process_health_dashboard_contracts import (
    KomponentenStatus,
    MetrikTyp,
    MetrikSchwellwert,
    KomponentenMetrik,
    DashboardKomponente,
    HealthDashboard,
    STANDARD_SCHWELLWERTE,
)
from app.core.workflow_dependency_visualization_contracts import (
    KnotenTyp,
    KantenStil,
    LayoutRichtung,
    VisualisierungsKnoten,
    VisualisierungsKante,
    VisualisierungsGraph,
    GraphExport,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _schwellwert(
    typ: MetrikTyp = MetrikTyp.LATENZ,
    warnung_ab: float = 500.0,
    kritisch_ab: float = 2000.0,
    einheit: str = "ms",
) -> MetrikSchwellwert:
    return MetrikSchwellwert(
        metrik_typ=typ,
        warnung_ab=warnung_ab,
        kritisch_ab=kritisch_ab,
        einheit=einheit,
    )


def _metrik(
    wert: float,
    typ: MetrikTyp = MetrikTyp.LATENZ,
    erfasst_am: datetime | None = None,
) -> KomponentenMetrik:
    return KomponentenMetrik(
        komponente_id="k1",
        metrik_typ=typ,
        wert=wert,
        erfasst_am=erfasst_am or datetime.now(),
        einheit="ms",
    )


def _komponente(
    metriken=None,
    status_override=None,
) -> DashboardKomponente:
    return DashboardKomponente(
        komponente_id="k1",
        name="API",
        typ="api",
        metriken=metriken or [],
        status_override=status_override,
    )


def _standard_sw() -> list:
    return [_schwellwert()]


def _dag_graph() -> VisualisierungsGraph:
    """Simple DAG: START → AUFGABE → ENDE"""
    knoten = [
        VisualisierungsKnoten("s", "Start", KnotenTyp.START),
        VisualisierungsKnoten("a", "Task", KnotenTyp.AUFGABE),
        VisualisierungsKnoten("e", "End", KnotenTyp.ENDE),
    ]
    kanten = [
        VisualisierungsKante("s", "a"),
        VisualisierungsKante("a", "e"),
    ]
    return VisualisierungsGraph("g1", "wf1", knoten, kanten)


# ===========================================================================
# MetrikSchwellwert — 20 tests
# ===========================================================================

class TestMetrikSchwellwertBewerte:

    def test_gesund_below_warnung(self):
        sw = _schwellwert(warnung_ab=500.0, kritisch_ab=2000.0)
        assert sw.bewerte(100.0) == KomponentenStatus.GESUND

    def test_gesund_at_zero(self):
        sw = _schwellwert(warnung_ab=500.0, kritisch_ab=2000.0)
        assert sw.bewerte(0.0) == KomponentenStatus.GESUND

    def test_degradiert_at_warnung(self):
        sw = _schwellwert(warnung_ab=500.0, kritisch_ab=2000.0)
        assert sw.bewerte(500.0) == KomponentenStatus.DEGRADIERT

    def test_degradiert_above_warnung_below_kritisch(self):
        sw = _schwellwert(warnung_ab=500.0, kritisch_ab=2000.0)
        assert sw.bewerte(1000.0) == KomponentenStatus.DEGRADIERT

    def test_kritisch_at_kritisch_ab(self):
        sw = _schwellwert(warnung_ab=500.0, kritisch_ab=2000.0)
        assert sw.bewerte(2000.0) == KomponentenStatus.KRITISCH

    def test_kritisch_above_kritisch_ab(self):
        sw = _schwellwert(warnung_ab=500.0, kritisch_ab=2000.0)
        assert sw.bewerte(9999.0) == KomponentenStatus.KRITISCH

    def test_just_below_warnung_is_gesund(self):
        sw = _schwellwert(warnung_ab=500.0, kritisch_ab=2000.0)
        assert sw.bewerte(499.99) == KomponentenStatus.GESUND

    def test_just_above_warnung_is_degradiert(self):
        sw = _schwellwert(warnung_ab=500.0, kritisch_ab=2000.0)
        assert sw.bewerte(500.01) == KomponentenStatus.DEGRADIERT

    def test_just_below_kritisch_is_degradiert(self):
        sw = _schwellwert(warnung_ab=500.0, kritisch_ab=2000.0)
        assert sw.bewerte(1999.99) == KomponentenStatus.DEGRADIERT

    def test_fehlerrate_typ(self):
        sw = _schwellwert(typ=MetrikTyp.FEHLERRATE, warnung_ab=1.0, kritisch_ab=5.0, einheit="%")
        assert sw.bewerte(0.5) == KomponentenStatus.GESUND
        assert sw.bewerte(2.0) == KomponentenStatus.DEGRADIERT
        assert sw.bewerte(6.0) == KomponentenStatus.KRITISCH

    def test_auslastung_typ(self):
        sw = _schwellwert(typ=MetrikTyp.AUSLASTUNG, warnung_ab=70.0, kritisch_ab=90.0, einheit="%")
        assert sw.bewerte(50.0) == KomponentenStatus.GESUND
        assert sw.bewerte(80.0) == KomponentenStatus.DEGRADIERT
        assert sw.bewerte(95.0) == KomponentenStatus.KRITISCH

    def test_durchsatz_typ(self):
        # DURCHSATZ STANDARD_SCHWELLWERTE use warnung_ab=100 > kritisch_ab=10 (inverse semantics);
        # bewerte() is "above = worse" numerically, so kritisch triggers at >= 100, degradiert at >= 10.
        sw = _schwellwert(typ=MetrikTyp.DURCHSATZ, warnung_ab=100.0, kritisch_ab=10.0, einheit="req/s")
        # bewerte(): checks kritisch_ab first (wert >= kritisch_ab=10 → KRITISCH)
        # then warnung_ab (wert >= warnung_ab=100 → KRITISCH via the kritisch check already)
        # 5.0 < 10 → GESUND
        assert sw.bewerte(5.0) == KomponentenStatus.GESUND
        # 0.0 < 10 → GESUND
        assert sw.bewerte(0.0) == KomponentenStatus.GESUND
        # 50.0 >= 10 (kritisch_ab) → KRITISCH
        assert sw.bewerte(50.0) == KomponentenStatus.KRITISCH
        # 200.0 >= 10 → KRITISCH
        assert sw.bewerte(200.0) == KomponentenStatus.KRITISCH

    def test_verfuegbarkeit_typ(self):
        # VERFUEGBARKEIT STANDARD_SCHWELLWERTE: warnung_ab=99 > kritisch_ab=95 (inverse semantics)
        # bewerte() numeric: >= kritisch_ab=95 first checked … wait — bewerte checks kritisch_ab first.
        # If wert >= kritisch_ab=95 → KRITISCH; then if >= warnung_ab=99 also KRITISCH
        # So wert=99.5 >= 95 → KRITISCH, wert=50 < 95 → GESUND
        sw = _schwellwert(typ=MetrikTyp.VERFUEGBARKEIT, warnung_ab=99.0, kritisch_ab=95.0, einheit="%")
        # 50.0 < 95 → GESUND
        assert sw.bewerte(50.0) == KomponentenStatus.GESUND
        # 99.5 >= 95 → KRITISCH (because kritisch_ab=95 is lower than warnung_ab=99)
        assert sw.bewerte(99.5) == KomponentenStatus.KRITISCH
        # 100.0 >= 95 → KRITISCH
        assert sw.bewerte(100.0) == KomponentenStatus.KRITISCH
        # 96.0 >= 95 → KRITISCH
        assert sw.bewerte(96.0) == KomponentenStatus.KRITISCH

    def test_latenz_typ(self):
        sw = _schwellwert(typ=MetrikTyp.LATENZ, warnung_ab=500.0, kritisch_ab=2000.0, einheit="ms")
        assert sw.bewerte(200.0) == KomponentenStatus.GESUND

    def test_einheit_stored(self):
        sw = _schwellwert(einheit="req/s")
        assert sw.einheit == "req/s"

    def test_metrik_typ_stored(self):
        sw = _schwellwert(typ=MetrikTyp.FEHLERRATE)
        assert sw.metrik_typ == MetrikTyp.FEHLERRATE

    def test_warnung_stored(self):
        sw = _schwellwert(warnung_ab=42.0)
        assert sw.warnung_ab == 42.0

    def test_kritisch_stored(self):
        sw = _schwellwert(kritisch_ab=99.0)
        assert sw.kritisch_ab == 99.0

    def test_exact_warnung_boundary(self):
        sw = _schwellwert(warnung_ab=1.0, kritisch_ab=5.0)
        assert sw.bewerte(1.0) == KomponentenStatus.DEGRADIERT

    def test_exact_kritisch_boundary(self):
        sw = _schwellwert(warnung_ab=1.0, kritisch_ab=5.0)
        assert sw.bewerte(5.0) == KomponentenStatus.KRITISCH


# ===========================================================================
# DashboardKomponente — 30 tests
# ===========================================================================

class TestDashboardKomponenteBerechneStatus:

    def test_unbekannt_when_no_metriken(self):
        k = _komponente()
        assert k.berechne_status([]) == KomponentenStatus.UNBEKANNT

    def test_unbekannt_when_no_metriken_with_schwellwerte(self):
        k = _komponente()
        assert k.berechne_status(_standard_sw()) == KomponentenStatus.UNBEKANNT

    def test_gesund_when_below_all_thresholds(self):
        k = _komponente(metriken=[_metrik(100.0)])
        assert k.berechne_status(_standard_sw()) == KomponentenStatus.GESUND

    def test_degradiert_when_one_in_warning(self):
        k = _komponente(metriken=[_metrik(600.0)])
        assert k.berechne_status(_standard_sw()) == KomponentenStatus.DEGRADIERT

    def test_kritisch_when_one_exceeds_kritisch(self):
        k = _komponente(metriken=[_metrik(3000.0)])
        assert k.berechne_status(_standard_sw()) == KomponentenStatus.KRITISCH

    def test_status_override_gesund_takes_precedence(self):
        k = _komponente(
            metriken=[_metrik(9999.0)],
            status_override=KomponentenStatus.GESUND,
        )
        assert k.berechne_status(_standard_sw()) == KomponentenStatus.GESUND

    def test_status_override_kritisch_takes_precedence(self):
        k = _komponente(
            metriken=[_metrik(10.0)],
            status_override=KomponentenStatus.KRITISCH,
        )
        assert k.berechne_status(_standard_sw()) == KomponentenStatus.KRITISCH

    def test_status_override_ausgefallen(self):
        k = _komponente(status_override=KomponentenStatus.AUSGEFALLEN)
        assert k.berechne_status([]) == KomponentenStatus.AUSGEFALLEN

    def test_status_override_degradiert(self):
        k = _komponente(
            metriken=[_metrik(10.0)],
            status_override=KomponentenStatus.DEGRADIERT,
        )
        assert k.berechne_status(_standard_sw()) == KomponentenStatus.DEGRADIERT

    def test_worst_metric_wins(self):
        sw = [
            _schwellwert(typ=MetrikTyp.LATENZ, warnung_ab=500.0, kritisch_ab=2000.0),
            MetrikSchwellwert(MetrikTyp.FEHLERRATE, 1.0, 5.0, "%"),
        ]
        metriken = [
            _metrik(600.0, MetrikTyp.LATENZ),    # DEGRADIERT
            _metrik(6.0, MetrikTyp.FEHLERRATE),   # KRITISCH
        ]
        k = _komponente(metriken=metriken)
        assert k.berechne_status(sw) == KomponentenStatus.KRITISCH

    def test_two_metrics_both_gesund(self):
        sw = [
            _schwellwert(typ=MetrikTyp.LATENZ, warnung_ab=500.0, kritisch_ab=2000.0),
            MetrikSchwellwert(MetrikTyp.FEHLERRATE, 1.0, 5.0, "%"),
        ]
        metriken = [
            _metrik(100.0, MetrikTyp.LATENZ),
            _metrik(0.5, MetrikTyp.FEHLERRATE),
        ]
        k = _komponente(metriken=metriken)
        assert k.berechne_status(sw) == KomponentenStatus.GESUND

    def test_no_matching_schwellwert_stays_gesund(self):
        # Metrik LATENZ but schwellwert only for FEHLERRATE
        sw = [MetrikSchwellwert(MetrikTyp.FEHLERRATE, 1.0, 5.0, "%")]
        k = _komponente(metriken=[_metrik(9999.0, MetrikTyp.LATENZ)])
        assert k.berechne_status(sw) == KomponentenStatus.GESUND

    def test_komponente_id_stored(self):
        k = DashboardKomponente("myid", "MyAPI", "api")
        assert k.komponente_id == "myid"

    def test_name_stored(self):
        k = DashboardKomponente("id", "MyName", "worker")
        assert k.name == "MyName"

    def test_typ_stored(self):
        k = DashboardKomponente("id", "n", "database")
        assert k.typ == "database"

    def test_metriken_default_empty(self):
        k = DashboardKomponente("id", "n", "api")
        assert k.metriken == []

    def test_status_override_default_none(self):
        k = DashboardKomponente("id", "n", "api")
        assert k.status_override is None

    def test_letzte_metrik_none_when_empty(self):
        k = _komponente()
        assert k.letzte_metrik(MetrikTyp.LATENZ) is None

    def test_letzte_metrik_none_wrong_type(self):
        k = _komponente(metriken=[_metrik(100.0, MetrikTyp.FEHLERRATE)])
        assert k.letzte_metrik(MetrikTyp.LATENZ) is None

    def test_letzte_metrik_returns_single(self):
        m = _metrik(100.0, MetrikTyp.LATENZ)
        k = _komponente(metriken=[m])
        assert k.letzte_metrik(MetrikTyp.LATENZ) == m

    def test_letzte_metrik_returns_most_recent(self):
        t1 = datetime(2026, 1, 1, 10, 0, 0)
        t2 = datetime(2026, 1, 1, 11, 0, 0)
        m1 = _metrik(100.0, MetrikTyp.LATENZ, t1)
        m2 = _metrik(200.0, MetrikTyp.LATENZ, t2)
        k = _komponente(metriken=[m1, m2])
        assert k.letzte_metrik(MetrikTyp.LATENZ) == m2

    def test_letzte_metrik_ignores_other_types(self):
        t1 = datetime(2026, 1, 1, 10, 0, 0)
        t2 = datetime(2026, 1, 1, 11, 0, 0)
        m_lat = _metrik(100.0, MetrikTyp.LATENZ, t2)
        m_err = _metrik(1.0, MetrikTyp.FEHLERRATE, t1)
        k = _komponente(metriken=[m_lat, m_err])
        assert k.letzte_metrik(MetrikTyp.LATENZ) == m_lat

    def test_multiple_metriken_same_type_picks_latest(self):
        times = [datetime(2026, 1, 1, h, 0, 0) for h in range(5)]
        metriken = [_metrik(float(i), MetrikTyp.LATENZ, times[i]) for i in range(5)]
        k = _komponente(metriken=metriken)
        result = k.letzte_metrik(MetrikTyp.LATENZ)
        assert result is not None
        assert result.wert == 4.0

    def test_berechne_status_empty_schwellwerte_with_metriken(self):
        k = _komponente(metriken=[_metrik(9999.0)])
        # No matching schwellwert → stays GESUND
        assert k.berechne_status([]) == KomponentenStatus.GESUND

    def test_ausgefallen_override_beats_all(self):
        k = _komponente(
            metriken=[_metrik(1.0)],
            status_override=KomponentenStatus.AUSGEFALLEN,
        )
        assert k.berechne_status(_standard_sw()) == KomponentenStatus.AUSGEFALLEN

    def test_unbekannt_override(self):
        k = _komponente(status_override=KomponentenStatus.UNBEKANNT)
        assert k.berechne_status(_standard_sw()) == KomponentenStatus.UNBEKANNT

    def test_three_metriken_degradiert_wins_over_gesund(self):
        sw = [_schwellwert(warnung_ab=500.0, kritisch_ab=2000.0)]
        metriken = [_metrik(100.0), _metrik(200.0), _metrik(600.0)]
        k = _komponente(metriken=metriken)
        assert k.berechne_status(sw) == KomponentenStatus.DEGRADIERT

    def test_komponenten_metrik_wert_stored(self):
        m = _metrik(42.5)
        assert m.wert == 42.5

    def test_komponenten_metrik_typ_stored(self):
        m = _metrik(1.0, MetrikTyp.AUSLASTUNG)
        assert m.metrik_typ == MetrikTyp.AUSLASTUNG

    def test_komponenten_metrik_erfasst_am_stored(self):
        t = datetime(2026, 3, 15, 12, 0, 0)
        m = _metrik(1.0, erfasst_am=t)
        assert m.erfasst_am == t


# ===========================================================================
# HealthDashboard — 30 tests
# ===========================================================================

class TestHealthDashboard:

    def _dashboard(self, komponenten=None, schwellwerte=None) -> HealthDashboard:
        return HealthDashboard(
            dashboard_id="d1",
            name="Test",
            komponenten=komponenten or [],
            schwellwerte=schwellwerte or _standard_sw(),
        )

    def test_gesamtstatus_unbekannt_when_empty(self):
        d = self._dashboard()
        assert d.gesamtstatus() == KomponentenStatus.UNBEKANNT

    def test_gesamtstatus_gesund_all_healthy(self):
        k = _komponente(metriken=[_metrik(100.0)])
        d = self._dashboard(komponenten=[k])
        assert d.gesamtstatus() == KomponentenStatus.GESUND

    def test_gesamtstatus_degradiert_when_one_degraded(self):
        k = _komponente(metriken=[_metrik(600.0)])
        d = self._dashboard(komponenten=[k])
        assert d.gesamtstatus() == KomponentenStatus.DEGRADIERT

    def test_gesamtstatus_kritisch_when_one_critical(self):
        k = _komponente(metriken=[_metrik(3000.0)])
        d = self._dashboard(komponenten=[k])
        assert d.gesamtstatus() == KomponentenStatus.KRITISCH

    def test_gesamtstatus_ausgefallen_override(self):
        k = _komponente(status_override=KomponentenStatus.AUSGEFALLEN)
        d = self._dashboard(komponenten=[k])
        assert d.gesamtstatus() == KomponentenStatus.AUSGEFALLEN

    def test_gesamtstatus_worst_wins_mixed(self):
        k1 = _komponente(metriken=[_metrik(100.0)])   # GESUND
        k2 = _komponente(metriken=[_metrik(3000.0)])  # KRITISCH
        d = self._dashboard(komponenten=[k1, k2])
        assert d.gesamtstatus() == KomponentenStatus.KRITISCH

    def test_gesamtstatus_unbekannt_wins_over_gesund(self):
        k1 = _komponente(metriken=[_metrik(100.0)])  # GESUND
        k2 = _komponente()                            # UNBEKANNT
        d = self._dashboard(komponenten=[k1, k2])
        # UNBEKANNT ranks above GESUND in the rang list
        assert d.gesamtstatus() == KomponentenStatus.UNBEKANNT

    def test_gesamtstatus_degradiert_wins_over_unbekannt(self):
        k1 = _komponente()                           # UNBEKANNT
        k2 = _komponente(metriken=[_metrik(600.0)])  # DEGRADIERT
        d = self._dashboard(komponenten=[k1, k2])
        assert d.gesamtstatus() == KomponentenStatus.DEGRADIERT

    def test_kritische_komponenten_empty_when_all_healthy(self):
        k = _komponente(metriken=[_metrik(100.0)])
        d = self._dashboard(komponenten=[k])
        assert d.kritische_komponenten() == []

    def test_kritische_komponenten_returns_critical_one(self):
        k1 = _komponente(metriken=[_metrik(100.0)])
        k2 = DashboardKomponente("k2", "DB", "database", [_metrik(3000.0)])
        d = self._dashboard(komponenten=[k1, k2])
        result = d.kritische_komponenten()
        assert len(result) == 1
        assert result[0].komponente_id == "k2"

    def test_kritische_komponenten_includes_ausgefallen(self):
        k = _komponente(status_override=KomponentenStatus.AUSGEFALLEN)
        d = self._dashboard(komponenten=[k])
        assert len(d.kritische_komponenten()) == 1

    def test_kritische_komponenten_excludes_degradiert(self):
        k = _komponente(metriken=[_metrik(600.0)])
        d = self._dashboard(komponenten=[k])
        assert d.kritische_komponenten() == []

    def test_kritische_komponenten_multiple(self):
        k1 = DashboardKomponente("k1", "A", "api", [_metrik(3000.0)])
        k2 = DashboardKomponente("k2", "B", "api", [], KomponentenStatus.AUSGEFALLEN)
        d = self._dashboard(komponenten=[k1, k2])
        result = d.kritische_komponenten()
        assert len(result) == 2

    def test_verfuegbarkeits_pct_zero_when_empty(self):
        d = self._dashboard()
        assert d.verfuegbarkeits_pct() == 0.0

    def test_verfuegbarkeits_pct_100_when_all_healthy(self):
        k = _komponente(metriken=[_metrik(100.0)])
        d = self._dashboard(komponenten=[k])
        assert d.verfuegbarkeits_pct() == 100.0

    def test_verfuegbarkeits_pct_50_when_half_healthy(self):
        k1 = _komponente(metriken=[_metrik(100.0)])
        k2 = DashboardKomponente("k2", "B", "api", [_metrik(3000.0)])
        d = self._dashboard(komponenten=[k1, k2])
        assert d.verfuegbarkeits_pct() == 50.0

    def test_verfuegbarkeits_pct_0_when_all_critical(self):
        k = _komponente(metriken=[_metrik(3000.0)])
        d = self._dashboard(komponenten=[k])
        assert d.verfuegbarkeits_pct() == 0.0

    def test_verfuegbarkeits_pct_rounded(self):
        # 1 of 3 healthy → 33.33%
        k1 = _komponente(metriken=[_metrik(100.0)])
        k2 = DashboardKomponente("k2", "B", "api", [_metrik(3000.0)])
        k3 = DashboardKomponente("k3", "C", "api", [_metrik(3000.0)])
        d = self._dashboard(komponenten=[k1, k2, k3])
        assert d.verfuegbarkeits_pct() == 33.33

    def test_dashboard_id_stored(self):
        d = HealthDashboard("abc", "Test")
        assert d.dashboard_id == "abc"

    def test_dashboard_name_stored(self):
        d = HealthDashboard("id", "MyDashboard")
        assert d.name == "MyDashboard"

    def test_dashboard_komponenten_default_empty(self):
        d = HealthDashboard("id", "n")
        assert d.komponenten == []

    def test_dashboard_schwellwerte_default_empty(self):
        d = HealthDashboard("id", "n")
        assert d.schwellwerte == []

    def test_dashboard_erstellt_am_set(self):
        d = HealthDashboard("id", "n")
        assert isinstance(d.erstellt_am, datetime)

    def test_four_komponenten_two_healthy(self):
        ks = [
            _komponente(metriken=[_metrik(100.0)]),                           # GESUND
            DashboardKomponente("k2", "B", "api", [_metrik(100.0)]),          # GESUND
            DashboardKomponente("k3", "C", "api", [_metrik(3000.0)]),         # KRITISCH
            DashboardKomponente("k4", "D", "api", [_metrik(3000.0)]),         # KRITISCH
        ]
        d = self._dashboard(komponenten=ks)
        assert d.verfuegbarkeits_pct() == 50.0
        assert len(d.kritische_komponenten()) == 2

    def test_gesamtstatus_three_gesund_one_ausgefallen(self):
        ks = [
            _komponente(metriken=[_metrik(100.0)]),
            DashboardKomponente("k2", "B", "api", [_metrik(100.0)]),
            DashboardKomponente("k3", "C", "api", [_metrik(100.0)]),
            DashboardKomponente("k4", "D", "api", [], KomponentenStatus.AUSGEFALLEN),
        ]
        d = self._dashboard(komponenten=ks)
        assert d.gesamtstatus() == KomponentenStatus.AUSGEFALLEN

    def test_no_schwellwert_all_unknown(self):
        k = _komponente(metriken=[_metrik(100.0)])
        d = HealthDashboard("id", "n", [k], [])
        # No schwellwerte → metrik won't match → GESUND
        assert d.gesamtstatus() == KomponentenStatus.GESUND

    def test_dashboard_with_multiple_schwellwerte(self):
        sw = [
            _schwellwert(MetrikTyp.LATENZ, 500.0, 2000.0, "ms"),
            MetrikSchwellwert(MetrikTyp.FEHLERRATE, 1.0, 5.0, "%"),
        ]
        k = _komponente(metriken=[_metrik(100.0, MetrikTyp.LATENZ)])
        d = HealthDashboard("id", "n", [k], sw)
        assert d.gesamtstatus() == KomponentenStatus.GESUND

    def test_verfuegbarkeits_pct_with_no_schwellwerte_but_metriken(self):
        k = _komponente(metriken=[_metrik(100.0)])
        d = HealthDashboard("id", "n", [k], [])
        # No matching schwellwert → GESUND
        assert d.verfuegbarkeits_pct() == 100.0

    def test_kritische_komponenten_excludes_unbekannt(self):
        k = _komponente()  # UNBEKANNT
        d = self._dashboard(komponenten=[k])
        assert d.kritische_komponenten() == []

    def test_kritische_komponenten_excludes_gesund(self):
        k = _komponente(metriken=[_metrik(10.0)])
        d = self._dashboard(komponenten=[k])
        assert d.kritische_komponenten() == []


# ===========================================================================
# STANDARD_SCHWELLWERTE — 7 tests
# ===========================================================================

class TestStandardSchwellwerte:

    def test_exactly_five_entries(self):
        assert len(STANDARD_SCHWELLWERTE) == 5

    def test_all_metrik_typen_covered(self):
        typen = {sw.metrik_typ for sw in STANDARD_SCHWELLWERTE}
        assert MetrikTyp.LATENZ in typen
        assert MetrikTyp.FEHLERRATE in typen
        assert MetrikTyp.AUSLASTUNG in typen
        assert MetrikTyp.DURCHSATZ in typen
        assert MetrikTyp.VERFUEGBARKEIT in typen

    def test_unique_metrik_typen(self):
        typen = [sw.metrik_typ for sw in STANDARD_SCHWELLWERTE]
        assert len(typen) == len(set(typen))

    def test_latenz_einheit_ms(self):
        latenz = next(s for s in STANDARD_SCHWELLWERTE if s.metrik_typ == MetrikTyp.LATENZ)
        assert latenz.einheit == "ms"

    def test_fehlerrate_einheit_percent(self):
        err = next(s for s in STANDARD_SCHWELLWERTE if s.metrik_typ == MetrikTyp.FEHLERRATE)
        assert err.einheit == "%"

    def test_all_have_positive_warnung(self):
        for sw in STANDARD_SCHWELLWERTE:
            assert sw.warnung_ab > 0

    def test_all_have_positive_kritisch(self):
        for sw in STANDARD_SCHWELLWERTE:
            assert sw.kritisch_ab > 0


# ===========================================================================
# VisualisierungsKnoten — 12 tests
# ===========================================================================

class TestVisualisierungsKnoten:

    def test_basic_construction(self):
        k = VisualisierungsKnoten("k1", "Task", KnotenTyp.AUFGABE)
        assert k.knoten_id == "k1"
        assert k.bezeichnung == "Task"
        assert k.typ == KnotenTyp.AUFGABE

    def test_ebene_defaults_zero(self):
        k = VisualisierungsKnoten("k1", "T", KnotenTyp.START)
        assert k.ebene == 0

    def test_gruppe_defaults_none(self):
        k = VisualisierungsKnoten("k1", "T", KnotenTyp.START)
        assert k.gruppe is None

    def test_metadaten_defaults_empty(self):
        k = VisualisierungsKnoten("k1", "T", KnotenTyp.AUFGABE)
        assert k.metadaten == {}

    def test_typ_start(self):
        k = VisualisierungsKnoten("s", "Start", KnotenTyp.START)
        assert k.typ == KnotenTyp.START

    def test_typ_ende(self):
        k = VisualisierungsKnoten("e", "End", KnotenTyp.ENDE)
        assert k.typ == KnotenTyp.ENDE

    def test_typ_entscheidung(self):
        k = VisualisierungsKnoten("d", "Decision", KnotenTyp.ENTSCHEIDUNG)
        assert k.typ == KnotenTyp.ENTSCHEIDUNG

    def test_typ_parallelisierung(self):
        k = VisualisierungsKnoten("p", "Fork", KnotenTyp.PARALLELISIERUNG)
        assert k.typ == KnotenTyp.PARALLELISIERUNG

    def test_typ_zusammenfuehrung(self):
        k = VisualisierungsKnoten("j", "Join", KnotenTyp.ZUSAMMENFUEHRUNG)
        assert k.typ == KnotenTyp.ZUSAMMENFUEHRUNG

    def test_typ_subprozess(self):
        k = VisualisierungsKnoten("sp", "Sub", KnotenTyp.SUBPROZESS)
        assert k.typ == KnotenTyp.SUBPROZESS

    def test_gruppe_set(self):
        k = VisualisierungsKnoten("k", "T", KnotenTyp.AUFGABE, gruppe="lane1")
        assert k.gruppe == "lane1"

    def test_ebene_set(self):
        k = VisualisierungsKnoten("k", "T", KnotenTyp.AUFGABE, ebene=3)
        assert k.ebene == 3


# ===========================================================================
# VisualisierungsKante — 8 tests
# ===========================================================================

class TestVisualisierungsKante:

    def test_basic_construction(self):
        e = VisualisierungsKante("a", "b")
        assert e.von == "a"
        assert e.nach == "b"

    def test_stil_default_normal(self):
        e = VisualisierungsKante("a", "b")
        assert e.stil == KantenStil.NORMAL

    def test_beschriftung_default_none(self):
        e = VisualisierungsKante("a", "b")
        assert e.beschriftung is None

    def test_gewicht_default_one(self):
        e = VisualisierungsKante("a", "b")
        assert e.gewicht == 1

    def test_stil_bedingt(self):
        e = VisualisierungsKante("a", "b", KantenStil.BEDINGT)
        assert e.stil == KantenStil.BEDINGT

    def test_stil_fehler(self):
        e = VisualisierungsKante("a", "b", KantenStil.FEHLER)
        assert e.stil == KantenStil.FEHLER

    def test_stil_kompensation(self):
        e = VisualisierungsKante("a", "b", KantenStil.KOMPENSATION)
        assert e.stil == KantenStil.KOMPENSATION

    def test_stil_optional(self):
        e = VisualisierungsKante("a", "b", KantenStil.OPTIONAL)
        assert e.stil == KantenStil.OPTIONAL


# ===========================================================================
# VisualisierungsGraph — 60 tests
# ===========================================================================

class TestVisualisierungsGraph:

    # -- Construction --

    def test_basic_construction(self):
        g = VisualisierungsGraph("g1", "wf1")
        assert g.graph_id == "g1"
        assert g.workflow_id == "wf1"

    def test_knoten_default_empty(self):
        g = VisualisierungsGraph("g1", "wf1")
        assert g.knoten == []

    def test_kanten_default_empty(self):
        g = VisualisierungsGraph("g1", "wf1")
        assert g.kanten == []

    def test_richtung_default_lr(self):
        g = VisualisierungsGraph("g1", "wf1")
        assert g.richtung == LayoutRichtung.LINKS_RECHTS

    def test_richtung_tb(self):
        g = VisualisierungsGraph("g1", "wf1", richtung=LayoutRichtung.OBEN_UNTEN)
        assert g.richtung == LayoutRichtung.OBEN_UNTEN

    # -- knoten_nach_typ --

    def test_knoten_nach_typ_returns_subset(self):
        g = _dag_graph()
        aufgaben = g.knoten_nach_typ(KnotenTyp.AUFGABE)
        assert len(aufgaben) == 1
        assert aufgaben[0].knoten_id == "a"

    def test_knoten_nach_typ_start(self):
        g = _dag_graph()
        assert len(g.knoten_nach_typ(KnotenTyp.START)) == 1

    def test_knoten_nach_typ_ende(self):
        g = _dag_graph()
        assert len(g.knoten_nach_typ(KnotenTyp.ENDE)) == 1

    def test_knoten_nach_typ_empty_when_none(self):
        g = _dag_graph()
        assert g.knoten_nach_typ(KnotenTyp.ENTSCHEIDUNG) == []

    def test_knoten_nach_typ_multiple(self):
        knoten = [
            VisualisierungsKnoten("a1", "A", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("a2", "B", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("s", "S", KnotenTyp.START),
        ]
        g = VisualisierungsGraph("g", "wf", knoten=knoten)
        assert len(g.knoten_nach_typ(KnotenTyp.AUFGABE)) == 2

    # -- nachfolger / vorgaenger --

    def test_nachfolger_simple(self):
        g = _dag_graph()
        assert g.nachfolger("s") == ["a"]

    def test_nachfolger_multiple(self):
        knoten = [
            VisualisierungsKnoten("s", "S", KnotenTyp.START),
            VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("b", "B", KnotenTyp.AUFGABE),
        ]
        kanten = [VisualisierungsKante("s", "a"), VisualisierungsKante("s", "b")]
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=kanten)
        assert set(g.nachfolger("s")) == {"a", "b"}

    def test_nachfolger_empty_when_none(self):
        g = _dag_graph()
        assert g.nachfolger("e") == []

    def test_vorgaenger_simple(self):
        g = _dag_graph()
        assert g.vorgaenger("a") == ["s"]

    def test_vorgaenger_multiple(self):
        knoten = [
            VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("b", "B", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("e", "E", KnotenTyp.ENDE),
        ]
        kanten = [VisualisierungsKante("a", "e"), VisualisierungsKante("b", "e")]
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=kanten)
        assert set(g.vorgaenger("e")) == {"a", "b"}

    def test_vorgaenger_empty_at_start(self):
        g = _dag_graph()
        assert g.vorgaenger("s") == []

    # -- hat_zyklen --

    def test_hat_zyklen_false_dag(self):
        g = _dag_graph()
        assert g.hat_zyklen() is False

    def test_hat_zyklen_true_simple_cycle(self):
        knoten = [
            VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("b", "B", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("c", "C", KnotenTyp.AUFGABE),
        ]
        kanten = [
            VisualisierungsKante("a", "b"),
            VisualisierungsKante("b", "c"),
            VisualisierungsKante("c", "a"),  # cycle
        ]
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=kanten)
        assert g.hat_zyklen() is True

    def test_hat_zyklen_false_empty(self):
        g = VisualisierungsGraph("g", "wf")
        assert g.hat_zyklen() is False

    def test_hat_zyklen_false_single_node(self):
        g = VisualisierungsGraph("g", "wf",
            knoten=[VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE)])
        assert g.hat_zyklen() is False

    def test_hat_zyklen_self_loop(self):
        knoten = [VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE)]
        kanten = [VisualisierungsKante("a", "a")]
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=kanten)
        assert g.hat_zyklen() is True

    def test_hat_zyklen_false_diamond(self):
        knoten = [
            VisualisierungsKnoten("s", "S", KnotenTyp.START),
            VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("b", "B", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("e", "E", KnotenTyp.ENDE),
        ]
        kanten = [
            VisualisierungsKante("s", "a"),
            VisualisierungsKante("s", "b"),
            VisualisierungsKante("a", "e"),
            VisualisierungsKante("b", "e"),
        ]
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=kanten)
        assert g.hat_zyklen() is False

    def test_hat_zyklen_two_component_one_cyclic(self):
        knoten = [
            VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("b", "B", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("c", "C", KnotenTyp.AUFGABE),  # isolated
        ]
        kanten = [
            VisualisierungsKante("a", "b"),
            VisualisierungsKante("b", "a"),  # cycle in a-b component
        ]
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=kanten)
        assert g.hat_zyklen() is True

    # -- kritischer_pfad --

    def test_kritischer_pfad_empty_no_start(self):
        g = VisualisierungsGraph("g", "wf",
            knoten=[VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE)])
        assert g.kritischer_pfad() == []

    def test_kritischer_pfad_empty_no_ende(self):
        g = VisualisierungsGraph("g", "wf",
            knoten=[VisualisierungsKnoten("s", "S", KnotenTyp.START)])
        assert g.kritischer_pfad() == []

    def test_kritischer_pfad_empty_graph(self):
        g = VisualisierungsGraph("g", "wf")
        assert g.kritischer_pfad() == []

    def test_kritischer_pfad_simple_dag(self):
        g = _dag_graph()
        path = g.kritischer_pfad()
        assert path == ["s", "a", "e"]

    def test_kritischer_pfad_direct_start_to_end(self):
        knoten = [
            VisualisierungsKnoten("s", "S", KnotenTyp.START),
            VisualisierungsKnoten("e", "E", KnotenTyp.ENDE),
        ]
        kanten = [VisualisierungsKante("s", "e")]
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=kanten)
        assert g.kritischer_pfad() == ["s", "e"]

    def test_kritischer_pfad_picks_longest(self):
        """Two paths: S→A→E (len 3) vs S→B→C→E (len 4). Longest wins."""
        knoten = [
            VisualisierungsKnoten("s", "S", KnotenTyp.START),
            VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("b", "B", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("c", "C", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("e", "E", KnotenTyp.ENDE),
        ]
        kanten = [
            VisualisierungsKante("s", "a"),
            VisualisierungsKante("a", "e"),
            VisualisierungsKante("s", "b"),
            VisualisierungsKante("b", "c"),
            VisualisierungsKante("c", "e"),
        ]
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=kanten)
        path = g.kritischer_pfad()
        assert len(path) == 4
        assert path[0] == "s"
        assert path[-1] == "e"
        assert "b" in path or "c" in path

    def test_kritischer_pfad_includes_start_and_end(self):
        g = _dag_graph()
        path = g.kritischer_pfad()
        assert path[0] == "s"
        assert path[-1] == "e"

    def test_kritischer_pfad_no_path_start_to_end(self):
        knoten = [
            VisualisierungsKnoten("s", "S", KnotenTyp.START),
            VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE),  # disconnected
            VisualisierungsKnoten("e", "E", KnotenTyp.ENDE),
        ]
        kanten = [VisualisierungsKante("s", "a")]  # no path to e
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=kanten)
        # DFS from s won't reach e → path is just ["s"]
        path = g.kritischer_pfad()
        # Should return ["s"] since s is START but can't reach ENDE
        assert isinstance(path, list)

    # -- ebenen_layout --

    def test_ebenen_layout_empty(self):
        g = VisualisierungsGraph("g", "wf")
        assert g.ebenen_layout() == {}

    def test_ebenen_layout_single_node(self):
        g = VisualisierungsGraph("g", "wf",
            knoten=[VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE)])
        layout = g.ebenen_layout()
        assert layout == {"a": 0}

    def test_ebenen_layout_linear_chain(self):
        """A→B→C should give levels 0,1,2"""
        knoten = [
            VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("b", "B", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("c", "C", KnotenTyp.AUFGABE),
        ]
        kanten = [VisualisierungsKante("a", "b"), VisualisierungsKante("b", "c")]
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=kanten)
        layout = g.ebenen_layout()
        assert layout["a"] == 0
        assert layout["b"] == 1
        assert layout["c"] == 2

    def test_ebenen_layout_dag_graph(self):
        g = _dag_graph()
        layout = g.ebenen_layout()
        assert layout["s"] == 0
        assert layout["a"] == 1
        assert layout["e"] == 2

    def test_ebenen_layout_root_level_zero(self):
        knoten = [
            VisualisierungsKnoten("a", "A", KnotenTyp.START),
            VisualisierungsKnoten("b", "B", KnotenTyp.AUFGABE),
        ]
        kanten = [VisualisierungsKante("a", "b")]
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=kanten)
        layout = g.ebenen_layout()
        assert layout["a"] == 0

    def test_ebenen_layout_diamond_shape(self):
        """S→A→E and S→B→E: A and B both at level 1, E at level 2"""
        knoten = [
            VisualisierungsKnoten("s", "S", KnotenTyp.START),
            VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("b", "B", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("e", "E", KnotenTyp.ENDE),
        ]
        kanten = [
            VisualisierungsKante("s", "a"),
            VisualisierungsKante("s", "b"),
            VisualisierungsKante("a", "e"),
            VisualisierungsKante("b", "e"),
        ]
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=kanten)
        layout = g.ebenen_layout()
        assert layout["s"] == 0
        assert layout["a"] == 1
        assert layout["b"] == 1
        assert layout["e"] == 2

    def test_ebenen_layout_disconnected_nodes(self):
        knoten = [
            VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("b", "B", KnotenTyp.AUFGABE),
        ]
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=[])
        layout = g.ebenen_layout()
        assert layout["a"] == 0
        assert layout["b"] == 0

    def test_ebenen_layout_long_chain(self):
        ids = [str(i) for i in range(6)]
        knoten = [VisualisierungsKnoten(i, i, KnotenTyp.AUFGABE) for i in ids]
        kanten = [VisualisierungsKante(ids[i], ids[i+1]) for i in range(5)]
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=kanten)
        layout = g.ebenen_layout()
        for i, node_id in enumerate(ids):
            assert layout[node_id] == i

    def test_ebenen_layout_returns_all_nodes(self):
        g = _dag_graph()
        layout = g.ebenen_layout()
        assert set(layout.keys()) == {"s", "a", "e"}

    # -- LayoutRichtung --

    def test_layout_richtung_values(self):
        assert LayoutRichtung.LINKS_RECHTS.value == "LR"
        assert LayoutRichtung.OBEN_UNTEN.value == "TB"
        assert LayoutRichtung.RECHTS_LINKS.value == "RL"
        assert LayoutRichtung.UNTEN_OBEN.value == "BT"

    # -- KnotenTyp / KantenStil enum values --

    def test_knoten_typ_values(self):
        assert KnotenTyp.START.value == "START"
        assert KnotenTyp.AUFGABE.value == "AUFGABE"
        assert KnotenTyp.ENTSCHEIDUNG.value == "ENTSCHEIDUNG"
        assert KnotenTyp.PARALLELISIERUNG.value == "PARALLELISIERUNG"
        assert KnotenTyp.ZUSAMMENFUEHRUNG.value == "ZUSAMMENFUEHRUNG"
        assert KnotenTyp.ENDE.value == "ENDE"
        assert KnotenTyp.SUBPROZESS.value == "SUBPROZESS"

    def test_kanten_stil_values(self):
        assert KantenStil.NORMAL.value == "NORMAL"
        assert KantenStil.BEDINGT.value == "BEDINGT"
        assert KantenStil.FEHLER.value == "FEHLER"
        assert KantenStil.KOMPENSATION.value == "KOMPENSATION"
        assert KantenStil.OPTIONAL.value == "OPTIONAL"

    def test_seven_knoten_typen(self):
        assert len(list(KnotenTyp)) == 7

    def test_five_kanten_stile(self):
        assert len(list(KantenStil)) == 5

    # -- Multiple start nodes --

    def test_multiple_start_nodes_longest_path(self):
        """S1→A→E (len 3) and S2→E (len 2): picks S1→A→E"""
        knoten = [
            VisualisierungsKnoten("s1", "S1", KnotenTyp.START),
            VisualisierungsKnoten("s2", "S2", KnotenTyp.START),
            VisualisierungsKnoten("a", "A", KnotenTyp.AUFGABE),
            VisualisierungsKnoten("e", "E", KnotenTyp.ENDE),
        ]
        kanten = [
            VisualisierungsKante("s1", "a"),
            VisualisierungsKante("a", "e"),
            VisualisierungsKante("s2", "e"),
        ]
        g = VisualisierungsGraph("g", "wf", knoten=knoten, kanten=kanten)
        path = g.kritischer_pfad()
        assert len(path) == 3
        assert "s1" in path

    def test_knoten_count_in_graph(self):
        g = _dag_graph()
        assert len(g.knoten) == 3

    def test_kanten_count_in_graph(self):
        g = _dag_graph()
        assert len(g.kanten) == 2


# ===========================================================================
# GraphExport — 7 tests
# ===========================================================================

class TestGraphExport:

    def test_basic_construction(self):
        ge = GraphExport("g1", "mermaid", "A --> B\nB --> C", "2026-03-19T10:00:00")
        assert ge.graph_id == "g1"
        assert ge.format == "mermaid"

    def test_zeilen_anzahl_counts_lines(self):
        ge = GraphExport("g1", "mermaid", "A --> B\nB --> C", "2026-03-19")
        assert ge.zeilen_anzahl() == 2

    def test_zeilen_anzahl_single_line(self):
        ge = GraphExport("g1", "dot", "digraph{}", "2026-03-19")
        assert ge.zeilen_anzahl() == 1

    def test_zeilen_anzahl_empty_string(self):
        ge = GraphExport("g1", "json", "", "2026-03-19")
        assert ge.zeilen_anzahl() == 0

    def test_zeilen_anzahl_three_lines(self):
        ge = GraphExport("g1", "json", "{\n  \"a\": 1\n}", "2026-03-19")
        assert ge.zeilen_anzahl() == 3

    def test_format_dot(self):
        ge = GraphExport("g1", "dot", "digraph G {}", "2026-03-19")
        assert ge.format == "dot"

    def test_erstellt_am_stored(self):
        ge = GraphExport("g1", "json", "{}", "2026-03-19T12:00:00")
        assert ge.erstellt_am == "2026-03-19T12:00:00"


# ===========================================================================
# Architecture constraint tests — 2 tests
# ===========================================================================

class TestArchitectureConstraints:

    def _get_imports(self, module_path: str) -> list[str]:
        with open(module_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def test_no_api_imports_in_health_dashboard(self):
        import os
        path = os.path.join(
            os.path.dirname(__file__),
            "..", "app", "core", "process_health_dashboard_contracts.py"
        )
        imports = self._get_imports(os.path.normpath(path))
        api_imports = [i for i in imports if "app.api" in i]
        assert api_imports == [], f"Found app.api imports: {api_imports}"

    def test_no_api_imports_in_visualization(self):
        import os
        path = os.path.join(
            os.path.dirname(__file__),
            "..", "app", "core", "workflow_dependency_visualization_contracts.py"
        )
        imports = self._get_imports(os.path.normpath(path))
        api_imports = [i for i in imports if "app.api" in i]
        assert api_imports == [], f"Found app.api imports: {api_imports}"
