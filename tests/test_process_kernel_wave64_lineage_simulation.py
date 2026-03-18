"""
Wave 64 Tests: Data Lineage Contracts + Process Simulation Contracts
130+ tests covering all classes, methods, properties, and default data.
"""
import pytest
from datetime import datetime, timedelta

from app.core.process_lineage_contracts import (
    LineageKnotenTyp,
    LineageOperationTyp,
    LineageKnoten,
    LineageKante,
    LineageGraph,
    get_default_lineage_graph,
)
from app.core.workflow_simulation_contracts_wave64 import (
    SimulationsTyp,
    SimulationsStatus,
    SimulationsParameter,
    SimulationsErgebnis,
    SimulationsLauf,
    get_default_simulations_laeufe,
)


# ─────────────────────────────────────────────
# Enum Tests
# ─────────────────────────────────────────────

class TestLineageKnotenTyp:
    def test_quelle_value(self):
        assert LineageKnotenTyp.QUELLE == "QUELLE"

    def test_transformation_value(self):
        assert LineageKnotenTyp.TRANSFORMATION == "TRANSFORMATION"

    def test_ziel_value(self):
        assert LineageKnotenTyp.ZIEL == "ZIEL"

    def test_zwischenspeicher_value(self):
        assert LineageKnotenTyp.ZWISCHENSPEICHER == "ZWISCHENSPEICHER"

    def test_all_members(self):
        members = {e.value for e in LineageKnotenTyp}
        assert members == {"QUELLE", "TRANSFORMATION", "ZIEL", "ZWISCHENSPEICHER"}


class TestLineageOperationTyp:
    def test_lesen(self):
        assert LineageOperationTyp.LESEN == "LESEN"

    def test_schreiben(self):
        assert LineageOperationTyp.SCHREIBEN == "SCHREIBEN"

    def test_transformieren(self):
        assert LineageOperationTyp.TRANSFORMIEREN == "TRANSFORMIEREN"

    def test_kopieren(self):
        assert LineageOperationTyp.KOPIEREN == "KOPIEREN"

    def test_loeschen(self):
        assert LineageOperationTyp.LOESCHEN == "LOESCHEN"

    def test_all_members(self):
        members = {e.value for e in LineageOperationTyp}
        assert members == {"LESEN", "SCHREIBEN", "TRANSFORMIEREN", "KOPIEREN", "LOESCHEN"}


class TestSimulationsTyp:
    def test_last_test(self):
        assert SimulationsTyp.LAST_TEST == "LAST_TEST"

    def test_pfad_analyse(self):
        assert SimulationsTyp.PFAD_ANALYSE == "PFAD_ANALYSE"

    def test_engpass_analyse(self):
        assert SimulationsTyp.ENGPASS_ANALYSE == "ENGPASS_ANALYSE"

    def test_what_if(self):
        assert SimulationsTyp.WHAT_IF == "WHAT_IF"


class TestSimulationsStatus:
    def test_ausstehend(self):
        assert SimulationsStatus.AUSSTEHEND == "AUSSTEHEND"

    def test_laufend(self):
        assert SimulationsStatus.LAUFEND == "LAUFEND"

    def test_abgeschlossen(self):
        assert SimulationsStatus.ABGESCHLOSSEN == "ABGESCHLOSSEN"

    def test_fehlgeschlagen(self):
        assert SimulationsStatus.FEHLGESCHLAGEN == "FEHLGESCHLAGEN"


# ─────────────────────────────────────────────
# LineageKnoten Tests
# ─────────────────────────────────────────────

class TestLineageKnoten:
    def test_creation_basic(self):
        k = LineageKnoten("K1", "Test", LineageKnotenTyp.QUELLE, "PostgreSQL", "table1")
        assert k.knoten_id == "K1"
        assert k.name == "Test"
        assert k.knoten_typ == LineageKnotenTyp.QUELLE
        assert k.system == "PostgreSQL"
        assert k.datensatz == "table1"
        assert k.tenant_id == ""

    def test_creation_with_tenant(self):
        k = LineageKnoten("K2", "Node2", LineageKnotenTyp.ZIEL, "S3", "bucket", "TENANT-X")
        assert k.tenant_id == "TENANT-X"

    def test_transformation_type(self):
        k = LineageKnoten("K3", "Transform", LineageKnotenTyp.TRANSFORMATION, "Python", "calc")
        assert k.knoten_typ == LineageKnotenTyp.TRANSFORMATION

    def test_zwischenspeicher_type(self):
        k = LineageKnoten("K4", "Cache", LineageKnotenTyp.ZWISCHENSPEICHER, "Redis", "cache_key")
        assert k.knoten_typ == LineageKnotenTyp.ZWISCHENSPEICHER

    def test_all_fields_set(self):
        k = LineageKnoten("K5", "N5", LineageKnotenTyp.QUELLE, "NATS", "topic.orders", "T1")
        assert k.knoten_id == "K5"
        assert k.name == "N5"
        assert k.system == "NATS"
        assert k.datensatz == "topic.orders"
        assert k.tenant_id == "T1"


# ─────────────────────────────────────────────
# LineageKante Tests
# ─────────────────────────────────────────────

class TestLineageKante:
    def test_creation_basic(self):
        now = datetime(2026, 3, 16)
        k = LineageKante("E1", "K1", "K2", LineageOperationTyp.LESEN, "WI-001", now, 100)
        assert k.kante_id == "E1"
        assert k.von_knoten_id == "K1"
        assert k.zu_knoten_id == "K2"
        assert k.operation == LineageOperationTyp.LESEN
        assert k.workflow_instanz_id == "WI-001"
        assert k.ausgefuehrt_am == now
        assert k.datenmenge_bytes == 100

    def test_default_datenmenge(self):
        k = LineageKante("E2", "K1", "K2", LineageOperationTyp.SCHREIBEN, "WI-002")
        assert k.datenmenge_bytes == 0

    def test_default_ausgefuehrt_am_is_recent(self):
        before = datetime.utcnow()
        k = LineageKante("E3", "K1", "K2", LineageOperationTyp.KOPIEREN, "WI-003")
        after = datetime.utcnow()
        assert before <= k.ausgefuehrt_am <= after

    def test_large_datenmenge(self):
        k = LineageKante("E4", "K1", "K2", LineageOperationTyp.TRANSFORMIEREN, "WI-004",
                          datenmenge_bytes=10 * 1024 * 1024)
        assert k.datenmenge_bytes == 10 * 1024 * 1024

    def test_loeschen_operation(self):
        k = LineageKante("E5", "K1", "K2", LineageOperationTyp.LOESCHEN, "WI-005")
        assert k.operation == LineageOperationTyp.LOESCHEN


# ─────────────────────────────────────────────
# LineageGraph — Empty Graph Tests
# ─────────────────────────────────────────────

class TestLineageGraphEmpty:
    def setup_method(self):
        self.g = LineageGraph("LG-EMPTY")

    def test_graph_id(self):
        assert self.g.graph_id == "LG-EMPTY"

    def test_empty_knoten(self):
        assert self.g.knoten == []

    def test_empty_kanten(self):
        assert self.g.kanten == []

    def test_quell_knoten_empty(self):
        assert self.g.quell_knoten() == []

    def test_ziel_knoten_empty(self):
        assert self.g.ziel_knoten() == []

    def test_upstream_empty(self):
        assert self.g.upstream_knoten("ANY") == []

    def test_downstream_empty(self):
        assert self.g.downstream_knoten("ANY") == []

    def test_gesamt_datenmenge_zero(self):
        assert self.g.gesamt_datenmenge_bytes() == 0


# ─────────────────────────────────────────────
# LineageGraph — Logic Tests (small custom graph)
# ─────────────────────────────────────────────

class TestLineageGraphLogic:
    def setup_method(self):
        self.g = LineageGraph("LG-TEST")
        self.g.knoten = [
            LineageKnoten("A", "Source A", LineageKnotenTyp.QUELLE, "DB", "tbl_a"),
            LineageKnoten("B", "Source B", LineageKnotenTyp.QUELLE, "API", "endpoint_b"),
            LineageKnoten("C", "Transform", LineageKnotenTyp.TRANSFORMATION, "Python", "calc_c"),
            LineageKnoten("D", "Target",    LineageKnotenTyp.ZIEL, "DWH", "fact_d"),
            LineageKnoten("E", "Cache",     LineageKnotenTyp.ZWISCHENSPEICHER, "Redis", "cache_e"),
        ]
        now = datetime(2026, 1, 1)
        self.g.kanten = [
            LineageKante("E1", "A", "C", LineageOperationTyp.LESEN, "WI-T", now, 100),
            LineageKante("E2", "B", "C", LineageOperationTyp.LESEN, "WI-T", now, 200),
            LineageKante("E3", "C", "E", LineageOperationTyp.SCHREIBEN, "WI-T", now, 50),
            LineageKante("E4", "E", "D", LineageOperationTyp.TRANSFORMIEREN, "WI-T", now, 50),
        ]

    def test_quell_knoten_returns_only_quelle(self):
        result = self.g.quell_knoten()
        ids = {k.knoten_id for k in result}
        assert ids == {"A", "B"}

    def test_quell_knoten_count(self):
        assert len(self.g.quell_knoten()) == 2

    def test_ziel_knoten_returns_only_ziel(self):
        result = self.g.ziel_knoten()
        ids = {k.knoten_id for k in result}
        assert ids == {"D"}

    def test_ziel_knoten_count(self):
        assert len(self.g.ziel_knoten()) == 1

    def test_upstream_of_c(self):
        result = self.g.upstream_knoten("C")
        ids = {k.knoten_id for k in result}
        assert ids == {"A", "B"}

    def test_upstream_of_d(self):
        result = self.g.upstream_knoten("D")
        ids = {k.knoten_id for k in result}
        assert ids == {"E"}

    def test_upstream_of_a_is_empty(self):
        assert self.g.upstream_knoten("A") == []

    def test_upstream_of_b_is_empty(self):
        assert self.g.upstream_knoten("B") == []

    def test_upstream_of_nonexistent(self):
        assert self.g.upstream_knoten("NONEXISTENT") == []

    def test_downstream_of_a(self):
        result = self.g.downstream_knoten("A")
        ids = {k.knoten_id for k in result}
        assert ids == {"C"}

    def test_downstream_of_b(self):
        result = self.g.downstream_knoten("B")
        ids = {k.knoten_id for k in result}
        assert ids == {"C"}

    def test_downstream_of_c(self):
        result = self.g.downstream_knoten("C")
        ids = {k.knoten_id for k in result}
        assert ids == {"E"}

    def test_downstream_of_e(self):
        result = self.g.downstream_knoten("E")
        ids = {k.knoten_id for k in result}
        assert ids == {"D"}

    def test_downstream_of_d_is_empty(self):
        assert self.g.downstream_knoten("D") == []

    def test_downstream_of_nonexistent(self):
        assert self.g.downstream_knoten("NONEXISTENT") == []

    def test_gesamt_datenmenge(self):
        assert self.g.gesamt_datenmenge_bytes() == 400  # 100+200+50+50

    def test_gesamt_datenmenge_single_kante(self):
        g = LineageGraph("LG-SINGLE")
        now = datetime(2026, 1, 1)
        g.kanten = [LineageKante("E1", "A", "B", LineageOperationTyp.LESEN, "WI", now, 999)]
        assert g.gesamt_datenmenge_bytes() == 999


# ─────────────────────────────────────────────
# Default Lineage Graph Tests
# ─────────────────────────────────────────────

class TestDefaultLineageGraph:
    def setup_method(self):
        self.g = get_default_lineage_graph()

    def test_graph_id(self):
        assert self.g.graph_id == "LG-001"

    def test_knoten_count(self):
        assert len(self.g.knoten) == 6

    def test_kanten_count(self):
        assert len(self.g.kanten) == 5

    def test_quell_knoten_ids(self):
        ids = {k.knoten_id for k in self.g.quell_knoten()}
        assert ids == {"LK-001", "LK-002"}

    def test_quell_knoten_count(self):
        assert len(self.g.quell_knoten()) == 2

    def test_ziel_knoten_ids(self):
        ids = {k.knoten_id for k in self.g.ziel_knoten()}
        assert ids == {"LK-004", "LK-005"}

    def test_ziel_knoten_count(self):
        assert len(self.g.ziel_knoten()) == 2

    def test_upstream_of_lk003(self):
        upstream = self.g.upstream_knoten("LK-003")
        ids = {k.knoten_id for k in upstream}
        assert ids == {"LK-001", "LK-002"}

    def test_upstream_of_lk003_count(self):
        assert len(self.g.upstream_knoten("LK-003")) == 2

    def test_upstream_of_lk004(self):
        upstream = self.g.upstream_knoten("LK-004")
        ids = {k.knoten_id for k in upstream}
        assert ids == {"LK-006"}

    def test_upstream_of_lk005(self):
        upstream = self.g.upstream_knoten("LK-005")
        ids = {k.knoten_id for k in upstream}
        assert ids == {"LK-004"}

    def test_upstream_of_lk001_empty(self):
        assert self.g.upstream_knoten("LK-001") == []

    def test_upstream_of_lk002_empty(self):
        assert self.g.upstream_knoten("LK-002") == []

    def test_upstream_of_lk006(self):
        upstream = self.g.upstream_knoten("LK-006")
        ids = {k.knoten_id for k in upstream}
        assert ids == {"LK-003"}

    def test_downstream_of_lk003(self):
        downstream = self.g.downstream_knoten("LK-003")
        ids = {k.knoten_id for k in downstream}
        assert ids == {"LK-006"}

    def test_downstream_of_lk001(self):
        downstream = self.g.downstream_knoten("LK-001")
        ids = {k.knoten_id for k in downstream}
        assert ids == {"LK-003"}

    def test_downstream_of_lk002(self):
        downstream = self.g.downstream_knoten("LK-002")
        ids = {k.knoten_id for k in downstream}
        assert ids == {"LK-003"}

    def test_downstream_of_lk006(self):
        downstream = self.g.downstream_knoten("LK-006")
        ids = {k.knoten_id for k in downstream}
        assert ids == {"LK-004"}

    def test_downstream_of_lk004(self):
        downstream = self.g.downstream_knoten("LK-004")
        ids = {k.knoten_id for k in downstream}
        assert ids == {"LK-005"}

    def test_downstream_of_lk005_empty(self):
        assert self.g.downstream_knoten("LK-005") == []

    def test_gesamt_datenmenge(self):
        # 1024 + 2048 + 512 + 512 + 2048 = 6144
        assert self.g.gesamt_datenmenge_bytes() == 6144

    def test_lk001_is_iot_gateway(self):
        k = next(k for k in self.g.knoten if k.knoten_id == "LK-001")
        assert k.system == "IoT-Gateway"
        assert k.knoten_typ == LineageKnotenTyp.QUELLE

    def test_lk002_is_postgresql(self):
        k = next(k for k in self.g.knoten if k.knoten_id == "LK-002")
        assert k.system == "PostgreSQL"
        assert k.datensatz == "kontrakte"

    def test_lk003_transformation(self):
        k = next(k for k in self.g.knoten if k.knoten_id == "LK-003")
        assert k.knoten_typ == LineageKnotenTyp.TRANSFORMATION

    def test_lk004_ziel(self):
        k = next(k for k in self.g.knoten if k.knoten_id == "LK-004")
        assert k.knoten_typ == LineageKnotenTyp.ZIEL

    def test_lk005_s3(self):
        k = next(k for k in self.g.knoten if k.knoten_id == "LK-005")
        assert k.system == "S3"

    def test_lk006_zwischenspeicher(self):
        k = next(k for k in self.g.knoten if k.knoten_id == "LK-006")
        assert k.knoten_typ == LineageKnotenTyp.ZWISCHENSPEICHER
        assert k.system == "Redis"

    def test_le001_operation_lesen(self):
        e = next(e for e in self.g.kanten if e.kante_id == "LE-001")
        assert e.operation == LineageOperationTyp.LESEN
        assert e.datenmenge_bytes == 1024

    def test_le003_operation_schreiben(self):
        e = next(e for e in self.g.kanten if e.kante_id == "LE-003")
        assert e.operation == LineageOperationTyp.SCHREIBEN

    def test_le004_operation_transformieren(self):
        e = next(e for e in self.g.kanten if e.kante_id == "LE-004")
        assert e.operation == LineageOperationTyp.TRANSFORMIEREN

    def test_le005_operation_kopieren(self):
        e = next(e for e in self.g.kanten if e.kante_id == "LE-005")
        assert e.operation == LineageOperationTyp.KOPIEREN

    def test_all_knoten_tenant_a(self):
        for k in self.g.knoten:
            assert k.tenant_id == "TENANT-A"

    def test_all_kanten_same_workflow(self):
        for e in self.g.kanten:
            assert e.workflow_instanz_id == "WI-S-001"


# ─────────────────────────────────────────────
# SimulationsParameter Tests
# ─────────────────────────────────────────────

class TestSimulationsParameter:
    def test_abweichung_positive(self):
        p = SimulationsParameter("P1", "Menge", 100.0, 150.0, "t")
        assert p.abweichung_pct == pytest.approx(50.0)

    def test_abweichung_negative(self):
        p = SimulationsParameter("P2", "Preis", 200.0, 190.0, "EUR/t")
        assert p.abweichung_pct == pytest.approx(-5.0)

    def test_abweichung_zero_basis(self):
        p = SimulationsParameter("P3", "X", 0.0, 100.0, "")
        assert p.abweichung_pct == 0.0

    def test_abweichung_no_change(self):
        p = SimulationsParameter("P4", "Y", 100.0, 100.0, "")
        assert p.abweichung_pct == pytest.approx(0.0)

    def test_abweichung_double(self):
        p = SimulationsParameter("P5", "Z", 50.0, 100.0, "")
        assert p.abweichung_pct == pytest.approx(100.0)

    def test_abweichung_minus_half(self):
        p = SimulationsParameter("P6", "Q", 100.0, 50.0, "")
        assert p.abweichung_pct == pytest.approx(-50.0)

    def test_einheit_default(self):
        p = SimulationsParameter("P7", "N", 10.0, 20.0)
        assert p.einheit == ""

    def test_einheit_set(self):
        p = SimulationsParameter("P8", "N", 10.0, 20.0, "kg")
        assert p.einheit == "kg"

    def test_all_fields(self):
        p = SimulationsParameter("P9", "Alpha", 300.0, 330.0, "EUR")
        assert p.parameter_id == "P9"
        assert p.name == "Alpha"
        assert p.basis_wert == 300.0
        assert p.simulierter_wert == 330.0
        assert p.einheit == "EUR"
        assert p.abweichung_pct == pytest.approx(10.0)


# ─────────────────────────────────────────────
# SimulationsErgebnis Tests
# ─────────────────────────────────────────────

class TestSimulationsErgebnis:
    def test_groesste_abweichung_none_if_empty(self):
        e = SimulationsErgebnis("E1", SimulationsTyp.WHAT_IF)
        assert e.groesste_abweichung is None

    def test_groesste_abweichung_single(self):
        p = SimulationsParameter("P1", "Menge", 100.0, 120.0, "t")
        e = SimulationsErgebnis("E2", SimulationsTyp.WHAT_IF, parameter=[p])
        assert e.groesste_abweichung is p

    def test_groesste_abweichung_picks_max_abs(self):
        p1 = SimulationsParameter("P1", "Menge", 100.0, 150.0, "t")   # +50%
        p2 = SimulationsParameter("P2", "Preis", 200.0, 190.0, "EUR")  # -5%
        e = SimulationsErgebnis("E3", SimulationsTyp.WHAT_IF, parameter=[p1, p2])
        assert e.groesste_abweichung is p1

    def test_groesste_abweichung_negative_wins(self):
        p1 = SimulationsParameter("P1", "A", 100.0, 130.0, "")   # +30%
        p2 = SimulationsParameter("P2", "B", 100.0, 40.0, "")    # -60%
        e = SimulationsErgebnis("E4", SimulationsTyp.WHAT_IF, parameter=[p1, p2])
        assert e.groesste_abweichung is p2

    def test_ergebnis_default_fields(self):
        e = SimulationsErgebnis("E5", SimulationsTyp.LAST_TEST)
        assert e.prognostizierte_dauer_minuten == 0.0
        assert e.engpass_schritt is None
        assert e.empfehlung == ""
        assert e.konfidenz_pct == 0.0

    def test_ergebnis_with_all_fields(self):
        e = SimulationsErgebnis(
            "E6", SimulationsTyp.ENGPASS_ANALYSE,
            prognostizierte_dauer_minuten=30.0,
            engpass_schritt="Genehmigung",
            empfehlung="Parallel verarbeiten",
            konfidenz_pct=85.0,
        )
        assert e.prognostizierte_dauer_minuten == 30.0
        assert e.engpass_schritt == "Genehmigung"
        assert e.empfehlung == "Parallel verarbeiten"
        assert e.konfidenz_pct == 85.0

    def test_groesste_abweichung_all_zero(self):
        p1 = SimulationsParameter("P1", "A", 100.0, 100.0, "")  # 0%
        p2 = SimulationsParameter("P2", "B", 100.0, 100.0, "")  # 0%
        e = SimulationsErgebnis("E7", SimulationsTyp.WHAT_IF, parameter=[p1, p2])
        # both 0%, one is returned (either)
        assert e.groesste_abweichung is not None
        assert e.groesste_abweichung.abweichung_pct == pytest.approx(0.0)


# ─────────────────────────────────────────────
# SimulationsLauf Tests
# ─────────────────────────────────────────────

class TestSimulationsLauf:
    def test_laufzeit_none_if_no_start(self):
        l = SimulationsLauf("SL-T1", "wf", SimulationsTyp.LAST_TEST)
        assert l.laufzeit_sekunden() is None

    def test_laufzeit_none_if_no_end(self):
        l = SimulationsLauf("SL-T2", "wf", SimulationsTyp.LAST_TEST,
                             gestartet_am=datetime(2026, 3, 16, 10, 0, 0))
        assert l.laufzeit_sekunden() is None

    def test_laufzeit_correct_seconds(self):
        start = datetime(2026, 3, 16, 10, 0, 0)
        end = start + timedelta(minutes=2)
        l = SimulationsLauf("SL-T3", "wf", SimulationsTyp.WHAT_IF,
                             SimulationsStatus.ABGESCHLOSSEN,
                             gestartet_am=start, beendet_am=end)
        assert l.laufzeit_sekunden() == pytest.approx(120.0)

    def test_laufzeit_one_hour(self):
        start = datetime(2026, 3, 16, 8, 0, 0)
        end = datetime(2026, 3, 16, 9, 0, 0)
        l = SimulationsLauf("SL-T4", "wf", SimulationsTyp.PFAD_ANALYSE,
                             SimulationsStatus.ABGESCHLOSSEN,
                             gestartet_am=start, beendet_am=end)
        assert l.laufzeit_sekunden() == pytest.approx(3600.0)

    def test_default_status(self):
        l = SimulationsLauf("SL-T5", "wf", SimulationsTyp.LAST_TEST)
        assert l.status == SimulationsStatus.AUSSTEHEND

    def test_default_ergebnis_none(self):
        l = SimulationsLauf("SL-T6", "wf", SimulationsTyp.LAST_TEST)
        assert l.ergebnis is None

    def test_all_fields(self):
        now = datetime(2026, 3, 16, 10, 0, 0)
        l = SimulationsLauf("SL-T7", "ap_rechnung", SimulationsTyp.ENGPASS_ANALYSE,
                             SimulationsStatus.LAUFEND, gestartet_am=now)
        assert l.lauf_id == "SL-T7"
        assert l.workflow_typ == "ap_rechnung"
        assert l.simulations_typ == SimulationsTyp.ENGPASS_ANALYSE
        assert l.status == SimulationsStatus.LAUFEND
        assert l.gestartet_am == now

    def test_laufzeit_30s(self):
        start = datetime(2026, 3, 16, 10, 0, 0)
        end = start + timedelta(seconds=30)
        l = SimulationsLauf("SL-T8", "wf", SimulationsTyp.WHAT_IF,
                             SimulationsStatus.ABGESCHLOSSEN,
                             gestartet_am=start, beendet_am=end)
        assert l.laufzeit_sekunden() == pytest.approx(30.0)


# ─────────────────────────────────────────────
# Default Simulations Laeufe Tests
# ─────────────────────────────────────────────

class TestDefaultSimulationsLaeufe:
    def setup_method(self):
        self.laeufe = get_default_simulations_laeufe()
        self.by_id = {l.lauf_id: l for l in self.laeufe}

    def test_count(self):
        assert len(self.laeufe) == 3

    def test_sl001_exists(self):
        assert "SL-001" in self.by_id

    def test_sl002_exists(self):
        assert "SL-002" in self.by_id

    def test_sl003_exists(self):
        assert "SL-003" in self.by_id

    def test_sl001_status_abgeschlossen(self):
        assert self.by_id["SL-001"].status == SimulationsStatus.ABGESCHLOSSEN

    def test_sl002_status_laufend(self):
        assert self.by_id["SL-002"].status == SimulationsStatus.LAUFEND

    def test_sl003_status_ausstehend(self):
        assert self.by_id["SL-003"].status == SimulationsStatus.AUSSTEHEND

    def test_sl001_laufzeit_120s(self):
        # 10min → 8min = 2min = 120s
        assert self.by_id["SL-001"].laufzeit_sekunden() == pytest.approx(120.0)

    def test_sl002_laufzeit_none(self):
        assert self.by_id["SL-002"].laufzeit_sekunden() is None

    def test_sl003_laufzeit_none(self):
        assert self.by_id["SL-003"].laufzeit_sekunden() is None

    def test_sl001_has_ergebnis(self):
        assert self.by_id["SL-001"].ergebnis is not None

    def test_sl002_ergebnis_none(self):
        assert self.by_id["SL-002"].ergebnis is None

    def test_sl003_ergebnis_none(self):
        assert self.by_id["SL-003"].ergebnis is None

    def test_sl001_simulations_typ_what_if(self):
        assert self.by_id["SL-001"].simulations_typ == SimulationsTyp.WHAT_IF

    def test_sl002_simulations_typ_engpass(self):
        assert self.by_id["SL-002"].simulations_typ == SimulationsTyp.ENGPASS_ANALYSE

    def test_sl003_simulations_typ_last_test(self):
        assert self.by_id["SL-003"].simulations_typ == SimulationsTyp.LAST_TEST

    def test_sl001_workflow_typ(self):
        assert self.by_id["SL-001"].workflow_typ == "kontrakt_freigabe"

    def test_sl002_workflow_typ(self):
        assert self.by_id["SL-002"].workflow_typ == "settlement_ausfuehren"

    def test_sl003_workflow_typ(self):
        assert self.by_id["SL-003"].workflow_typ == "ap_rechnung"

    def test_sl001_ergebnis_dauer(self):
        assert self.by_id["SL-001"].ergebnis.prognostizierte_dauer_minuten == pytest.approx(45.0)

    def test_sl001_ergebnis_engpass(self):
        assert self.by_id["SL-001"].ergebnis.engpass_schritt == "Preisfreigabe"

    def test_sl001_ergebnis_konfidenz(self):
        assert self.by_id["SL-001"].ergebnis.konfidenz_pct == pytest.approx(78.0)

    def test_sl001_ergebnis_parameter_count(self):
        assert len(self.by_id["SL-001"].ergebnis.parameter) == 2

    def test_sl001_sp001_abweichung_plus50(self):
        params = {p.parameter_id: p for p in self.by_id["SL-001"].ergebnis.parameter}
        assert params["SP-001"].abweichung_pct == pytest.approx(50.0)

    def test_sl001_sp002_abweichung_minus5(self):
        params = {p.parameter_id: p for p in self.by_id["SL-001"].ergebnis.parameter}
        assert params["SP-002"].abweichung_pct == pytest.approx(-5.0)

    def test_sl001_groesste_abweichung_sp001(self):
        ergebnis = self.by_id["SL-001"].ergebnis
        g = ergebnis.groesste_abweichung
        assert g is not None
        assert g.parameter_id == "SP-001"

    def test_sl001_groesste_abweichung_name(self):
        ergebnis = self.by_id["SL-001"].ergebnis
        assert ergebnis.groesste_abweichung.name == "Menge"

    def test_sl001_sp001_menge(self):
        params = {p.parameter_id: p for p in self.by_id["SL-001"].ergebnis.parameter}
        sp1 = params["SP-001"]
        assert sp1.name == "Menge"
        assert sp1.basis_wert == 100.0
        assert sp1.simulierter_wert == 150.0
        assert sp1.einheit == "t"

    def test_sl001_sp002_preis(self):
        params = {p.parameter_id: p for p in self.by_id["SL-001"].ergebnis.parameter}
        sp2 = params["SP-002"]
        assert sp2.name == "Preis"
        assert sp2.basis_wert == 200.0
        assert sp2.simulierter_wert == 190.0
        assert sp2.einheit == "EUR/t"

    def test_sl001_gestartet_am_set(self):
        assert self.by_id["SL-001"].gestartet_am is not None

    def test_sl001_beendet_am_set(self):
        assert self.by_id["SL-001"].beendet_am is not None

    def test_sl002_gestartet_am_set(self):
        assert self.by_id["SL-002"].gestartet_am is not None

    def test_sl002_beendet_am_none(self):
        assert self.by_id["SL-002"].beendet_am is None

    def test_sl003_gestartet_am_none(self):
        assert self.by_id["SL-003"].gestartet_am is None

    def test_sl001_ergebnis_typ_what_if(self):
        assert self.by_id["SL-001"].ergebnis.simulations_typ == SimulationsTyp.WHAT_IF

    def test_sl001_ergebnis_id(self):
        assert self.by_id["SL-001"].ergebnis.ergebnis_id == "SE-001"

    def test_sl001_empfehlung_not_empty(self):
        assert len(self.by_id["SL-001"].ergebnis.empfehlung) > 0


# ─────────────────────────────────────────────
# FastAPI Endpoint Tests
# ─────────────────────────────────────────────

class TestLineageEndpoints:
    def setup_method(self):
        from fastapi.testclient import TestClient
        from app.api.v1.endpoints.process_kernel_api import router
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)
        # Router prefix is /process, W64 paths use /lineage/w64/... and /simulation/w64/...
        self.base = "/process"

    def test_lineage_graph_status_200(self):
        r = self.client.get(f"{self.base}/lineage/w64/graph")
        assert r.status_code == 200

    def test_lineage_graph_graph_id(self):
        r = self.client.get(f"{self.base}/lineage/w64/graph")
        assert r.json()["graph_id"] == "LG-001"

    def test_lineage_graph_knoten_anzahl(self):
        r = self.client.get(f"{self.base}/lineage/w64/graph")
        assert r.json()["knoten_anzahl"] == 6

    def test_lineage_graph_kanten_anzahl(self):
        r = self.client.get(f"{self.base}/lineage/w64/graph")
        assert r.json()["kanten_anzahl"] == 5

    def test_lineage_graph_quell_knoten(self):
        r = self.client.get(f"{self.base}/lineage/w64/graph")
        assert set(r.json()["quell_knoten"]) == {"LK-001", "LK-002"}

    def test_lineage_graph_ziel_knoten(self):
        r = self.client.get(f"{self.base}/lineage/w64/graph")
        assert set(r.json()["ziel_knoten"]) == {"LK-004", "LK-005"}

    def test_lineage_graph_gesamt_datenmenge(self):
        r = self.client.get(f"{self.base}/lineage/w64/graph")
        assert r.json()["gesamt_datenmenge_bytes"] == 6144

    def test_lineage_upstream_lk003(self):
        r = self.client.post(f"{self.base}/lineage/w64/upstream", json={"knoten_id": "LK-003"})
        assert r.status_code == 200
        data = r.json()
        assert data["knoten_id"] == "LK-003"
        assert set(data["upstream"]) == {"LK-001", "LK-002"}

    def test_lineage_upstream_lk001_empty(self):
        r = self.client.post(f"{self.base}/lineage/w64/upstream", json={"knoten_id": "LK-001"})
        assert r.json()["upstream"] == []

    def test_lineage_upstream_missing_id(self):
        r = self.client.post(f"{self.base}/lineage/w64/upstream", json={})
        assert r.status_code == 200
        assert r.json()["upstream"] == []

    def test_lineage_upstream_lk004(self):
        r = self.client.post(f"{self.base}/lineage/w64/upstream", json={"knoten_id": "LK-004"})
        assert set(r.json()["upstream"]) == {"LK-006"}


class TestSimulationEndpoints:
    def setup_method(self):
        from fastapi.testclient import TestClient
        from app.api.v1.endpoints.process_kernel_api import router
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)
        self.base = "/process"

    def test_simulation_laeufe_status_200(self):
        r = self.client.get(f"{self.base}/simulation/w64/laeufe")
        assert r.status_code == 200

    def test_simulation_laeufe_count(self):
        r = self.client.get(f"{self.base}/simulation/w64/laeufe")
        assert len(r.json()) == 3

    def test_simulation_laeufe_sl001_status(self):
        data = {l["lauf_id"]: l for l in self.client.get(f"{self.base}/simulation/w64/laeufe").json()}
        assert data["SL-001"]["status"] == "ABGESCHLOSSEN"

    def test_simulation_laeufe_sl002_status(self):
        data = {l["lauf_id"]: l for l in self.client.get(f"{self.base}/simulation/w64/laeufe").json()}
        assert data["SL-002"]["status"] == "LAUFEND"

    def test_simulation_laeufe_sl003_status(self):
        data = {l["lauf_id"]: l for l in self.client.get(f"{self.base}/simulation/w64/laeufe").json()}
        assert data["SL-003"]["status"] == "AUSSTEHEND"

    def test_simulation_laeufe_sl001_hat_ergebnis(self):
        data = {l["lauf_id"]: l for l in self.client.get(f"{self.base}/simulation/w64/laeufe").json()}
        assert data["SL-001"]["hat_ergebnis"] is True

    def test_simulation_laeufe_sl002_kein_ergebnis(self):
        data = {l["lauf_id"]: l for l in self.client.get(f"{self.base}/simulation/w64/laeufe").json()}
        assert data["SL-002"]["hat_ergebnis"] is False

    def test_simulation_laeufe_sl001_laufzeit(self):
        data = {l["lauf_id"]: l for l in self.client.get(f"{self.base}/simulation/w64/laeufe").json()}
        assert data["SL-001"]["laufzeit_sekunden"] == pytest.approx(120.0)

    def test_simulation_laeufe_sl002_laufzeit_null(self):
        data = {l["lauf_id"]: l for l in self.client.get(f"{self.base}/simulation/w64/laeufe").json()}
        assert data["SL-002"]["laufzeit_sekunden"] is None

    def test_simulation_ergebnis_sl001(self):
        r = self.client.post(f"{self.base}/simulation/w64/ergebnis", json={"lauf_id": "SL-001"})
        assert r.status_code == 200
        d = r.json()
        assert d["lauf_id"] == "SL-001"
        assert d["prognostizierte_dauer_minuten"] == pytest.approx(45.0)
        assert d["engpass_schritt"] == "Preisfreigabe"
        assert d["konfidenz_pct"] == pytest.approx(78.0)

    def test_simulation_ergebnis_sl001_groesste_abweichung(self):
        r = self.client.post(f"{self.base}/simulation/w64/ergebnis", json={"lauf_id": "SL-001"})
        d = r.json()
        assert d["groesste_abweichung_parameter"] == "Menge"
        assert d["groesste_abweichung_pct"] == pytest.approx(50.0)

    def test_simulation_ergebnis_sl002_kein_ergebnis(self):
        r = self.client.post(f"{self.base}/simulation/w64/ergebnis", json={"lauf_id": "SL-002"})
        d = r.json()
        assert d["lauf_id"] == "SL-002"
        assert d["ergebnis"] is None

    def test_simulation_ergebnis_not_found(self):
        r = self.client.post(f"{self.base}/simulation/w64/ergebnis", json={"lauf_id": "SL-UNKNOWN"})
        d = r.json()
        assert "fehler" in d

    def test_simulation_ergebnis_sl001_empfehlung(self):
        r = self.client.post(f"{self.base}/simulation/w64/ergebnis", json={"lauf_id": "SL-001"})
        d = r.json()
        assert len(d["empfehlung"]) > 0
