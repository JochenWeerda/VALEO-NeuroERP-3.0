"""Wave 56: Process Step Dependencies (DAG) + Workflow Signal Contracts — 130+ Tests"""
import pytest
from datetime import datetime, timedelta

from app.core.process_dependency_contracts import (
    AbhaengigkeitsTyp, SchrittStatus,
    AbhaengigkeitsKante, ProzessSchritt, ProzessGraph,
    get_default_prozess_graphen,
)
from app.core.workflow_signal_contracts import (
    SignalTyp, SignalStatus, TriggerAktion,
    WorkflowSignal, SignalRegel, SignalVerarbeitungsErgebnis,
    verarbeite_signal, get_default_signal_regeln, get_default_signale,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
NOW = datetime(2026, 3, 16, 10, 0, 0)

def make_schritt(sid, status=SchrittStatus.AUSSTEHEND, name=None):
    return ProzessSchritt(sid, name or sid, status)

def make_kante(von, zu, typ=AbhaengigkeitsTyp.SEQUENZIELL):
    return AbhaengigkeitsKante(von, zu, typ)

def make_graph(schritte, kanten):
    g = ProzessGraph("TEST")
    g.schritte = schritte
    g.kanten = kanten
    return g

def make_signal(sid, wid, typ=SignalTyp.EXTERN, status=SignalStatus.AUSSTEHEND,
                ablauf_am=None, zugestellt_am=None, quelle="test"):
    return WorkflowSignal(sid, wid, typ, {}, status, NOW, zugestellt_am, ablauf_am, quelle)

def make_regel(rid, typ=SignalTyp.EXTERN, aktion=TriggerAktion.FORTSETZEN,
               workflow_typ="test", aktiv=True):
    return SignalRegel(rid, typ, aktion, workflow_typ, ist_aktiv=aktiv)

# ===========================================================================
# SECTION 1: AbhaengigkeitsTyp Enum
# ===========================================================================

def test_enum_sequenziell():
    assert AbhaengigkeitsTyp.SEQUENZIELL == "SEQUENZIELL"

def test_enum_parallel():
    assert AbhaengigkeitsTyp.PARALLEL == "PARALLEL"

def test_enum_optional():
    assert AbhaengigkeitsTyp.OPTIONAL == "OPTIONAL"

def test_enum_blockierend():
    assert AbhaengigkeitsTyp.BLOCKIEREND == "BLOCKIEREND"

def test_enum_from_string():
    assert AbhaengigkeitsTyp("SEQUENZIELL") == AbhaengigkeitsTyp.SEQUENZIELL

# ===========================================================================
# SECTION 2: SchrittStatus Enum
# ===========================================================================

def test_status_ausstehend():
    assert SchrittStatus.AUSSTEHEND == "AUSSTEHEND"

def test_status_bereit():
    assert SchrittStatus.BEREIT == "BEREIT"

def test_status_laufend():
    assert SchrittStatus.LAUFEND == "LAUFEND"

def test_status_abgeschlossen():
    assert SchrittStatus.ABGESCHLOSSEN == "ABGESCHLOSSEN"

def test_status_fehlgeschlagen():
    assert SchrittStatus.FEHLGESCHLAGEN == "FEHLGESCHLAGEN"

def test_status_uebersprungen():
    assert SchrittStatus.UEBERSPRUNGEN == "UEBERSPRUNGEN"

# ===========================================================================
# SECTION 3: AbhaengigkeitsKante
# ===========================================================================

def test_kante_attributes():
    k = AbhaengigkeitsKante("A", "B", AbhaengigkeitsTyp.SEQUENZIELL)
    assert k.von_schritt_id == "A"
    assert k.zu_schritt_id == "B"
    assert k.typ == AbhaengigkeitsTyp.SEQUENZIELL

def test_kante_blockierend():
    k = AbhaengigkeitsKante("X", "Y", AbhaengigkeitsTyp.BLOCKIEREND)
    assert k.typ == AbhaengigkeitsTyp.BLOCKIEREND

def test_kante_parallel():
    k = AbhaengigkeitsKante("X", "Y", AbhaengigkeitsTyp.PARALLEL)
    assert k.typ == AbhaengigkeitsTyp.PARALLEL

# ===========================================================================
# SECTION 4: ProzessSchritt
# ===========================================================================

def test_schritt_default_status():
    s = ProzessSchritt("S1", "Test")
    assert s.status == SchrittStatus.AUSSTEHEND

def test_schritt_custom_status():
    s = ProzessSchritt("S1", "Test", SchrittStatus.ABGESCHLOSSEN)
    assert s.status == SchrittStatus.ABGESCHLOSSEN

def test_schritt_abhaengigkeiten_default_empty():
    s = ProzessSchritt("S1", "Test")
    assert s.abhaengigkeiten == []

def test_schritt_id_and_name():
    s = ProzessSchritt("MY-STEP", "Mein Schritt")
    assert s.schritt_id == "MY-STEP"
    assert s.name == "Mein Schritt"

# ===========================================================================
# SECTION 5: ProzessGraph — bereite_schritte (no edges)
# ===========================================================================

def test_bereite_schritte_no_edges_single_ausstehend():
    g = make_graph([make_schritt("S1")], [])
    result = g.bereite_schritte()
    assert len(result) == 1
    assert result[0].schritt_id == "S1"

def test_bereite_schritte_no_edges_multiple_ausstehend():
    g = make_graph([make_schritt("S1"), make_schritt("S2"), make_schritt("S3")], [])
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "S1" in ids
    assert "S2" in ids
    assert "S3" in ids

def test_bereite_schritte_excludes_non_ausstehend():
    g = make_graph([
        make_schritt("S1", SchrittStatus.LAUFEND),
        make_schritt("S2", SchrittStatus.ABGESCHLOSSEN),
        make_schritt("S3", SchrittStatus.AUSSTEHEND),
    ], [])
    result = g.bereite_schritte()
    assert len(result) == 1
    assert result[0].schritt_id == "S3"

def test_bereite_schritte_empty_graph():
    g = make_graph([], [])
    assert g.bereite_schritte() == []

def test_bereite_schritte_all_abgeschlossen():
    g = make_graph([
        make_schritt("S1", SchrittStatus.ABGESCHLOSSEN),
        make_schritt("S2", SchrittStatus.ABGESCHLOSSEN),
    ], [])
    assert g.bereite_schritte() == []

# ===========================================================================
# SECTION 6: ProzessGraph — bereite_schritte (SEQUENZIELL)
# ===========================================================================

def test_sequenziell_blocked_when_predecessor_ausstehend():
    g = make_graph(
        [make_schritt("A"), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.SEQUENZIELL)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "A" in ids
    assert "B" not in ids

def test_sequenziell_blocked_when_predecessor_laufend():
    g = make_graph(
        [make_schritt("A", SchrittStatus.LAUFEND), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.SEQUENZIELL)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "B" not in ids

def test_sequenziell_ready_when_predecessor_abgeschlossen():
    g = make_graph(
        [make_schritt("A", SchrittStatus.ABGESCHLOSSEN), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.SEQUENZIELL)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "B" in ids

def test_sequenziell_blocked_when_predecessor_fehlgeschlagen():
    g = make_graph(
        [make_schritt("A", SchrittStatus.FEHLGESCHLAGEN), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.SEQUENZIELL)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "B" not in ids

def test_sequenziell_chain_only_first_ready():
    g = make_graph(
        [make_schritt("S1"), make_schritt("S2"), make_schritt("S3")],
        [
            make_kante("S1", "S2"),
            make_kante("S2", "S3"),
        ]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "S1" in ids
    assert "S2" not in ids
    assert "S3" not in ids

def test_sequenziell_chain_middle_ready():
    g = make_graph(
        [
            make_schritt("S1", SchrittStatus.ABGESCHLOSSEN),
            make_schritt("S2"),
            make_schritt("S3"),
        ],
        [
            make_kante("S1", "S2"),
            make_kante("S2", "S3"),
        ]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "S2" in ids
    assert "S3" not in ids

def test_sequenziell_chain_last_ready():
    g = make_graph(
        [
            make_schritt("S1", SchrittStatus.ABGESCHLOSSEN),
            make_schritt("S2", SchrittStatus.ABGESCHLOSSEN),
            make_schritt("S3"),
        ],
        [
            make_kante("S1", "S2"),
            make_kante("S2", "S3"),
        ]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "S3" in ids

# ===========================================================================
# SECTION 7: ProzessGraph — bereite_schritte (BLOCKIEREND)
# ===========================================================================

def test_blockierend_blocked_when_predecessor_fehlgeschlagen():
    g = make_graph(
        [make_schritt("A", SchrittStatus.FEHLGESCHLAGEN), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.BLOCKIEREND)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "B" not in ids

def test_blockierend_ready_when_predecessor_abgeschlossen():
    g = make_graph(
        [make_schritt("A", SchrittStatus.ABGESCHLOSSEN), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.BLOCKIEREND)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "B" in ids

def test_blockierend_blocked_when_predecessor_ausstehend():
    g = make_graph(
        [make_schritt("A"), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.BLOCKIEREND)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "B" not in ids

def test_blockierend_blocked_when_predecessor_laufend():
    g = make_graph(
        [make_schritt("A", SchrittStatus.LAUFEND), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.BLOCKIEREND)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "B" not in ids

# ===========================================================================
# SECTION 8: ProzessGraph — bereite_schritte (PARALLEL and OPTIONAL)
# ===========================================================================

def test_parallel_never_blocks_when_predecessor_ausstehend():
    g = make_graph(
        [make_schritt("A"), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.PARALLEL)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "B" in ids

def test_parallel_never_blocks_when_predecessor_fehlgeschlagen():
    g = make_graph(
        [make_schritt("A", SchrittStatus.FEHLGESCHLAGEN), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.PARALLEL)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "B" in ids

def test_parallel_never_blocks_when_predecessor_laufend():
    g = make_graph(
        [make_schritt("A", SchrittStatus.LAUFEND), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.PARALLEL)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "B" in ids

def test_optional_never_blocks_when_predecessor_ausstehend():
    g = make_graph(
        [make_schritt("A"), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.OPTIONAL)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "B" in ids

def test_optional_never_blocks_when_predecessor_fehlgeschlagen():
    g = make_graph(
        [make_schritt("A", SchrittStatus.FEHLGESCHLAGEN), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.OPTIONAL)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "B" in ids

def test_optional_never_blocks_when_predecessor_laufend():
    g = make_graph(
        [make_schritt("A", SchrittStatus.LAUFEND), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.OPTIONAL)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "B" in ids

# ===========================================================================
# SECTION 9: ProzessGraph — bereite_schritte (fork-join)
# ===========================================================================

def test_fork_join_both_blocked_initially():
    """S1→S2a, S1→S2b (SEQ), S2a→S3, S2b→S3 — all ausstehend"""
    g = make_graph(
        [make_schritt("S1"), make_schritt("S2a"), make_schritt("S2b"), make_schritt("S3")],
        [
            make_kante("S1", "S2a"),
            make_kante("S1", "S2b"),
            make_kante("S2a", "S3"),
            make_kante("S2b", "S3"),
        ]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "S1" in ids
    assert "S2a" not in ids
    assert "S2b" not in ids
    assert "S3" not in ids

def test_fork_join_both_fork_ready_when_S1_done():
    g = make_graph(
        [make_schritt("S1", SchrittStatus.ABGESCHLOSSEN), make_schritt("S2a"), make_schritt("S2b"), make_schritt("S3")],
        [
            make_kante("S1", "S2a"),
            make_kante("S1", "S2b"),
            make_kante("S2a", "S3"),
            make_kante("S2b", "S3"),
        ]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "S2a" in ids
    assert "S2b" in ids
    assert "S3" not in ids

def test_fork_join_S3_blocked_when_only_S2a_done():
    g = make_graph(
        [
            make_schritt("S1", SchrittStatus.ABGESCHLOSSEN),
            make_schritt("S2a", SchrittStatus.ABGESCHLOSSEN),
            make_schritt("S2b"),
            make_schritt("S3"),
        ],
        [
            make_kante("S1", "S2a"),
            make_kante("S1", "S2b"),
            make_kante("S2a", "S3"),
            make_kante("S2b", "S3"),
        ]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "S3" not in ids
    assert "S2b" in ids

def test_fork_join_S3_ready_when_both_done():
    g = make_graph(
        [
            make_schritt("S1", SchrittStatus.ABGESCHLOSSEN),
            make_schritt("S2a", SchrittStatus.ABGESCHLOSSEN),
            make_schritt("S2b", SchrittStatus.ABGESCHLOSSEN),
            make_schritt("S3"),
        ],
        [
            make_kante("S1", "S2a"),
            make_kante("S1", "S2b"),
            make_kante("S2a", "S3"),
            make_kante("S2b", "S3"),
        ]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "S3" in ids

# ===========================================================================
# SECTION 10: ProzessGraph — topologische_reihenfolge
# ===========================================================================

def test_topo_empty_graph():
    g = make_graph([], [])
    assert g.topologische_reihenfolge() == []

def test_topo_single_node():
    g = make_graph([make_schritt("S1")], [])
    assert g.topologische_reihenfolge() == ["S1"]

def test_topo_linear_s1_s2_s3():
    g = make_graph(
        [make_schritt("S1"), make_schritt("S2"), make_schritt("S3")],
        [make_kante("S1", "S2"), make_kante("S2", "S3")]
    )
    result = g.topologische_reihenfolge()
    assert result == ["S1", "S2", "S3"]

def test_topo_linear_reversed_order_in_list():
    """Even if schritte listed in reverse, topo order should be correct."""
    g = make_graph(
        [make_schritt("S3"), make_schritt("S2"), make_schritt("S1")],
        [make_kante("S1", "S2"), make_kante("S2", "S3")]
    )
    result = g.topologische_reihenfolge()
    # S1 must come before S2, S2 before S3
    assert result.index("S1") < result.index("S2")
    assert result.index("S2") < result.index("S3")

def test_topo_cycle_returns_empty():
    g = make_graph(
        [make_schritt("A"), make_schritt("B"), make_schritt("C")],
        [
            make_kante("A", "B"),
            make_kante("B", "C"),
            make_kante("C", "A"),
        ]
    )
    assert g.topologische_reihenfolge() == []

def test_topo_two_node_cycle():
    g = make_graph(
        [make_schritt("A"), make_schritt("B")],
        [make_kante("A", "B"), make_kante("B", "A")]
    )
    assert g.topologische_reihenfolge() == []

def test_topo_fork_join_s1_first_s3_last():
    g = make_graph(
        [make_schritt("S1"), make_schritt("S2a"), make_schritt("S2b"), make_schritt("S3")],
        [
            make_kante("S1", "S2a"),
            make_kante("S1", "S2b"),
            make_kante("S2a", "S3"),
            make_kante("S2b", "S3"),
        ]
    )
    result = g.topologische_reihenfolge()
    assert len(result) == 4
    assert result[0] == "S1"
    assert result[-1] == "S3"
    assert "S2a" in result
    assert "S2b" in result

def test_topo_parallel_edges_not_used_for_ordering():
    """PARALLEL edges should not affect topological order."""
    g = make_graph(
        [make_schritt("A"), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.PARALLEL)]
    )
    result = g.topologische_reihenfolge()
    # No SEQUENZIELL/BLOCKIEREND edges => both have in-degree 0 => just 2 nodes
    assert set(result) == {"A", "B"}

def test_topo_optional_edges_not_used_for_ordering():
    g = make_graph(
        [make_schritt("A"), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.OPTIONAL)]
    )
    result = g.topologische_reihenfolge()
    assert set(result) == {"A", "B"}

def test_topo_blockierend_used_for_ordering():
    g = make_graph(
        [make_schritt("A"), make_schritt("B")],
        [make_kante("A", "B", AbhaengigkeitsTyp.BLOCKIEREND)]
    )
    result = g.topologische_reihenfolge()
    assert result == ["A", "B"]

def test_topo_returns_all_nodes_no_cycle():
    g = make_graph(
        [make_schritt("S1"), make_schritt("S2"), make_schritt("S3"), make_schritt("S4")],
        [
            make_kante("S1", "S2"),
            make_kante("S2", "S3"),
            make_kante("S3", "S4"),
        ]
    )
    result = g.topologische_reihenfolge()
    assert len(result) == 4
    assert set(result) == {"S1", "S2", "S3", "S4"}

# ===========================================================================
# SECTION 11: get_default_prozess_graphen
# ===========================================================================

def test_default_graphen_returns_two():
    graphen = get_default_prozess_graphen()
    assert len(graphen) == 2

def test_default_graph_pg001_id():
    g = get_default_prozess_graphen()[0]
    assert g.graph_id == "PG-001"

def test_default_graph_pg002_id():
    g = get_default_prozess_graphen()[1]
    assert g.graph_id == "PG-002"

def test_default_pg001_has_four_schritte():
    g = get_default_prozess_graphen()[0]
    assert len(g.schritte) == 4

def test_default_pg001_has_three_kanten():
    g = get_default_prozess_graphen()[0]
    assert len(g.kanten) == 3

def test_default_pg001_bereite_schritte_is_s3():
    g = get_default_prozess_graphen()[0]
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert ids == ["S3"]

def test_default_pg001_s4_blocked():
    g = get_default_prozess_graphen()[0]
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "S4" not in ids

def test_default_pg002_has_four_schritte():
    g = get_default_prozess_graphen()[1]
    assert len(g.schritte) == 4

def test_default_pg002_has_four_kanten():
    g = get_default_prozess_graphen()[1]
    assert len(g.kanten) == 4

def test_default_pg002_bereite_schritte_s2a_s2b():
    g = get_default_prozess_graphen()[1]
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "S2a" in ids
    assert "S2b" in ids

def test_default_pg002_s3_blocked():
    g = get_default_prozess_graphen()[1]
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "S3" not in ids

def test_default_pg001_topo_order_correct():
    g = get_default_prozess_graphen()[0]
    result = g.topologische_reihenfolge()
    assert result.index("S1") < result.index("S2")
    assert result.index("S2") < result.index("S3")
    assert result.index("S3") < result.index("S4")

def test_default_pg002_topo_s1_first():
    g = get_default_prozess_graphen()[1]
    result = g.topologische_reihenfolge()
    assert result[0] == "S1"

def test_default_pg002_topo_s3_last():
    g = get_default_prozess_graphen()[1]
    result = g.topologische_reihenfolge()
    assert result[-1] == "S3"

def test_default_pg002_topo_all_four_nodes():
    g = get_default_prozess_graphen()[1]
    result = g.topologische_reihenfolge()
    assert set(result) == {"S1", "S2a", "S2b", "S3"}

# ===========================================================================
# SECTION 12: SignalTyp Enum
# ===========================================================================

def test_signal_typ_extern():
    assert SignalTyp.EXTERN == "EXTERN"

def test_signal_typ_intern():
    assert SignalTyp.INTERN == "INTERN"

def test_signal_typ_zeitplan():
    assert SignalTyp.ZEITPLAN == "ZEITPLAN"

def test_signal_typ_benutzer():
    assert SignalTyp.BENUTZER == "BENUTZER"

def test_signal_typ_system():
    assert SignalTyp.SYSTEM == "SYSTEM"

# ===========================================================================
# SECTION 13: SignalStatus Enum
# ===========================================================================

def test_signal_status_ausstehend():
    assert SignalStatus.AUSSTEHEND == "AUSSTEHEND"

def test_signal_status_zugestellt():
    assert SignalStatus.ZUGESTELLT == "ZUGESTELLT"

def test_signal_status_verarbeitet():
    assert SignalStatus.VERARBEITET == "VERARBEITET"

def test_signal_status_abgelaufen():
    assert SignalStatus.ABGELAUFEN == "ABGELAUFEN"

def test_signal_status_abgewiesen():
    assert SignalStatus.ABGEWIESEN == "ABGEWIESEN"

# ===========================================================================
# SECTION 14: TriggerAktion Enum
# ===========================================================================

def test_trigger_fortsetzen():
    assert TriggerAktion.FORTSETZEN == "FORTSETZEN"

def test_trigger_abbrechen():
    assert TriggerAktion.ABBRECHEN == "ABBRECHEN"

def test_trigger_eskalieren():
    assert TriggerAktion.ESKALIEREN == "ESKALIEREN"

def test_trigger_benachrichtigen():
    assert TriggerAktion.BENACHRICHTIGEN == "BENACHRICHTIGEN"

# ===========================================================================
# SECTION 15: WorkflowSignal — ist_abgelaufen
# ===========================================================================

def test_ist_abgelaufen_none_ablauf():
    s = make_signal("S1", "WI-1")
    assert s.ist_abgelaufen(NOW) is False

def test_ist_abgelaufen_future_ablauf():
    s = make_signal("S1", "WI-1", ablauf_am=NOW + timedelta(hours=1))
    assert s.ist_abgelaufen(NOW) is False

def test_ist_abgelaufen_past_ablauf():
    s = make_signal("S1", "WI-1", ablauf_am=NOW - timedelta(seconds=1))
    assert s.ist_abgelaufen(NOW) is True

def test_ist_abgelaufen_exact_moment():
    s = make_signal("S1", "WI-1", ablauf_am=NOW)
    assert s.ist_abgelaufen(NOW) is True

def test_ist_abgelaufen_far_future():
    s = make_signal("S1", "WI-1", ablauf_am=NOW + timedelta(days=365))
    assert s.ist_abgelaufen(NOW) is False

def test_ist_abgelaufen_far_past():
    s = make_signal("S1", "WI-1", ablauf_am=NOW - timedelta(days=30))
    assert s.ist_abgelaufen(NOW) is True

# ===========================================================================
# SECTION 16: WorkflowSignal — aktueller_status
# ===========================================================================

def test_aktueller_status_ausstehend_not_expired():
    s = make_signal("S1", "WI-1", ablauf_am=NOW + timedelta(hours=1))
    assert s.aktueller_status(NOW) == SignalStatus.AUSSTEHEND

def test_aktueller_status_ausstehend_expired():
    s = make_signal("S1", "WI-1", ablauf_am=NOW - timedelta(seconds=1))
    assert s.aktueller_status(NOW) == SignalStatus.ABGELAUFEN

def test_aktueller_status_verarbeitet_unchanged_even_if_past():
    s = make_signal("S1", "WI-1", status=SignalStatus.VERARBEITET, ablauf_am=NOW - timedelta(hours=1))
    assert s.aktueller_status(NOW) == SignalStatus.VERARBEITET

def test_aktueller_status_zugestellt_unchanged():
    s = make_signal("S1", "WI-1", status=SignalStatus.ZUGESTELLT, ablauf_am=NOW - timedelta(hours=1))
    assert s.aktueller_status(NOW) == SignalStatus.ZUGESTELLT

def test_aktueller_status_abgewiesen_unchanged():
    s = make_signal("S1", "WI-1", status=SignalStatus.ABGEWIESEN)
    assert s.aktueller_status(NOW) == SignalStatus.ABGEWIESEN

def test_aktueller_status_no_ablauf_stays_ausstehend():
    s = make_signal("S1", "WI-1")
    assert s.aktueller_status(NOW) == SignalStatus.AUSSTEHEND

# ===========================================================================
# SECTION 17: verarbeite_signal
# ===========================================================================

def test_verarbeite_expired_signal():
    s = make_signal("S1", "WI-1", ablauf_am=NOW - timedelta(hours=1))
    regeln = [make_regel("R1", SignalTyp.EXTERN, TriggerAktion.FORTSETZEN)]
    ergebnis = verarbeite_signal(s, regeln, NOW)
    assert ergebnis.erfolgreich is False
    assert "abgelaufen" in ergebnis.nachricht

def test_verarbeite_no_matching_rule():
    s = make_signal("S1", "WI-1", typ=SignalTyp.EXTERN)
    regeln = [make_regel("R1", SignalTyp.BENUTZER, TriggerAktion.FORTSETZEN)]
    ergebnis = verarbeite_signal(s, regeln, NOW)
    assert ergebnis.erfolgreich is False
    assert "Keine passende Regel" in ergebnis.nachricht

def test_verarbeite_matching_extern_rule():
    s = make_signal("S1", "WI-1", typ=SignalTyp.EXTERN)
    regeln = [make_regel("R1", SignalTyp.EXTERN, TriggerAktion.FORTSETZEN)]
    ergebnis = verarbeite_signal(s, regeln, NOW)
    assert ergebnis.erfolgreich is True
    assert ergebnis.trigger_aktion == TriggerAktion.FORTSETZEN

def test_verarbeite_matching_benutzer_rule():
    s = make_signal("S1", "WI-1", typ=SignalTyp.BENUTZER)
    regeln = [make_regel("R1", SignalTyp.BENUTZER, TriggerAktion.FORTSETZEN)]
    ergebnis = verarbeite_signal(s, regeln, NOW)
    assert ergebnis.erfolgreich is True
    assert ergebnis.trigger_aktion == TriggerAktion.FORTSETZEN

def test_verarbeite_matching_zeitplan_eskalieren():
    s = make_signal("S1", "WI-1", typ=SignalTyp.ZEITPLAN)
    regeln = [make_regel("R1", SignalTyp.ZEITPLAN, TriggerAktion.ESKALIEREN)]
    ergebnis = verarbeite_signal(s, regeln, NOW)
    assert ergebnis.erfolgreich is True
    assert ergebnis.trigger_aktion == TriggerAktion.ESKALIEREN

def test_verarbeite_matching_system_abbrechen():
    s = make_signal("S1", "WI-1", typ=SignalTyp.SYSTEM)
    regeln = [make_regel("R1", SignalTyp.SYSTEM, TriggerAktion.ABBRECHEN)]
    ergebnis = verarbeite_signal(s, regeln, NOW)
    assert ergebnis.erfolgreich is True
    assert ergebnis.trigger_aktion == TriggerAktion.ABBRECHEN

def test_verarbeite_inactive_rule_not_matched():
    s = make_signal("S1", "WI-1", typ=SignalTyp.EXTERN)
    regeln = [make_regel("R1", SignalTyp.EXTERN, TriggerAktion.FORTSETZEN, aktiv=False)]
    ergebnis = verarbeite_signal(s, regeln, NOW)
    assert ergebnis.erfolgreich is False

def test_verarbeite_first_matching_rule_wins():
    s = make_signal("S1", "WI-1", typ=SignalTyp.EXTERN)
    regeln = [
        make_regel("R1", SignalTyp.EXTERN, TriggerAktion.FORTSETZEN),
        make_regel("R2", SignalTyp.EXTERN, TriggerAktion.ABBRECHEN),
    ]
    ergebnis = verarbeite_signal(s, regeln, NOW)
    assert ergebnis.trigger_aktion == TriggerAktion.FORTSETZEN

def test_verarbeite_second_rule_used_when_first_inactive():
    s = make_signal("S1", "WI-1", typ=SignalTyp.EXTERN)
    regeln = [
        make_regel("R1", SignalTyp.EXTERN, TriggerAktion.FORTSETZEN, aktiv=False),
        make_regel("R2", SignalTyp.EXTERN, TriggerAktion.ABBRECHEN),
    ]
    ergebnis = verarbeite_signal(s, regeln, NOW)
    assert ergebnis.erfolgreich is True
    assert ergebnis.trigger_aktion == TriggerAktion.ABBRECHEN

def test_verarbeite_result_has_correct_signal_id():
    s = make_signal("MY-SIG", "WI-X", typ=SignalTyp.INTERN)
    regeln = [make_regel("R1", SignalTyp.INTERN, TriggerAktion.FORTSETZEN)]
    ergebnis = verarbeite_signal(s, regeln, NOW)
    assert ergebnis.signal_id == "MY-SIG"

def test_verarbeite_result_has_correct_workflow_instanz_id():
    s = make_signal("SIG-1", "WI-SPECIAL", typ=SignalTyp.INTERN)
    regeln = [make_regel("R1", SignalTyp.INTERN, TriggerAktion.FORTSETZEN)]
    ergebnis = verarbeite_signal(s, regeln, NOW)
    assert ergebnis.workflow_instanz_id == "WI-SPECIAL"

def test_verarbeite_result_nachricht_contains_regel_id():
    s = make_signal("S1", "WI-1", typ=SignalTyp.EXTERN)
    regeln = [make_regel("MY-RULE", SignalTyp.EXTERN, TriggerAktion.FORTSETZEN)]
    ergebnis = verarbeite_signal(s, regeln, NOW)
    assert "MY-RULE" in ergebnis.nachricht

def test_verarbeite_expired_uses_benachrichtigen():
    s = make_signal("S1", "WI-1", ablauf_am=NOW - timedelta(hours=1))
    ergebnis = verarbeite_signal(s, [], NOW)
    assert ergebnis.trigger_aktion == TriggerAktion.BENACHRICHTIGEN

# ===========================================================================
# SECTION 18: get_default_signal_regeln
# ===========================================================================

def test_default_regeln_count():
    regeln = get_default_signal_regeln()
    assert len(regeln) == 5

def test_default_regel_sr001():
    r = get_default_signal_regeln()[0]
    assert r.regel_id == "SR-001"
    assert r.signal_typ == SignalTyp.EXTERN
    assert r.trigger_aktion == TriggerAktion.FORTSETZEN

def test_default_regel_sr002():
    r = get_default_signal_regeln()[1]
    assert r.regel_id == "SR-002"
    assert r.signal_typ == SignalTyp.BENUTZER
    assert r.trigger_aktion == TriggerAktion.FORTSETZEN

def test_default_regel_sr003():
    r = get_default_signal_regeln()[2]
    assert r.regel_id == "SR-003"
    assert r.signal_typ == SignalTyp.ZEITPLAN
    assert r.trigger_aktion == TriggerAktion.ESKALIEREN

def test_default_regel_sr004():
    r = get_default_signal_regeln()[3]
    assert r.regel_id == "SR-004"
    assert r.signal_typ == SignalTyp.INTERN
    assert r.trigger_aktion == TriggerAktion.FORTSETZEN

def test_default_regel_sr005():
    r = get_default_signal_regeln()[4]
    assert r.regel_id == "SR-005"
    assert r.signal_typ == SignalTyp.SYSTEM
    assert r.trigger_aktion == TriggerAktion.ABBRECHEN

def test_default_regeln_all_aktiv():
    regeln = get_default_signal_regeln()
    assert all(r.ist_aktiv for r in regeln)

def test_default_regeln_all_have_workflow_typ():
    regeln = get_default_signal_regeln()
    assert all(r.workflow_typ for r in regeln)

# ===========================================================================
# SECTION 19: get_default_signale
# ===========================================================================

def test_default_signale_count():
    signale = get_default_signale()
    assert len(signale) == 4

def test_default_sig001_id():
    s = get_default_signale()[0]
    assert s.signal_id == "SIG-001"

def test_default_sig001_typ():
    s = get_default_signale()[0]
    assert s.signal_typ == SignalTyp.EXTERN

def test_default_sig001_not_expired():
    s = get_default_signale()[0]
    assert s.ist_abgelaufen(NOW) is False

def test_default_sig001_aktueller_status_ausstehend():
    s = get_default_signale()[0]
    assert s.aktueller_status(NOW) == SignalStatus.AUSSTEHEND

def test_default_sig002_status_verarbeitet():
    s = get_default_signale()[1]
    assert s.status == SignalStatus.VERARBEITET

def test_default_sig002_aktueller_status_verarbeitet():
    s = get_default_signale()[1]
    assert s.aktueller_status(NOW) == SignalStatus.VERARBEITET

def test_default_sig003_expired():
    s = get_default_signale()[2]
    assert s.ist_abgelaufen(NOW) is True

def test_default_sig003_aktueller_status_abgelaufen():
    s = get_default_signale()[2]
    assert s.aktueller_status(NOW) == SignalStatus.ABGELAUFEN

def test_default_sig003_typ_zeitplan():
    s = get_default_signale()[2]
    assert s.signal_typ == SignalTyp.ZEITPLAN

def test_default_sig004_typ_intern():
    s = get_default_signale()[3]
    assert s.signal_typ == SignalTyp.INTERN

def test_default_sig004_status_zugestellt():
    s = get_default_signale()[3]
    assert s.status == SignalStatus.ZUGESTELLT

def test_default_sig001_quelle():
    s = get_default_signale()[0]
    assert s.quelle == "EDI-Gateway"

def test_default_sig002_quelle():
    s = get_default_signale()[1]
    assert s.quelle == "user-001"

def test_default_sig003_quelle():
    s = get_default_signale()[2]
    assert s.quelle == "scheduler"

def test_default_sig004_workflow_instanz():
    s = get_default_signale()[3]
    assert s.workflow_instanz_id == "WI-Q-004"

def test_default_sig001_workflow_instanz():
    s = get_default_signale()[0]
    assert s.workflow_instanz_id == "WI-K-001"

# ===========================================================================
# SECTION 20: SignalVerarbeitungsErgebnis dataclass
# ===========================================================================

def test_signal_ergebnis_attributes():
    e = SignalVerarbeitungsErgebnis("S1", "WI-1", TriggerAktion.FORTSETZEN, True, "OK")
    assert e.signal_id == "S1"
    assert e.workflow_instanz_id == "WI-1"
    assert e.trigger_aktion == TriggerAktion.FORTSETZEN
    assert e.erfolgreich is True
    assert e.nachricht == "OK"

def test_signal_ergebnis_default_nachricht():
    e = SignalVerarbeitungsErgebnis("S1", "WI-1", TriggerAktion.FORTSETZEN, True)
    assert e.nachricht == ""

# ===========================================================================
# SECTION 21: SignalRegel dataclass
# ===========================================================================

def test_signal_regel_default_aktiv():
    r = SignalRegel("R1", SignalTyp.EXTERN, TriggerAktion.FORTSETZEN, "test")
    assert r.ist_aktiv is True

def test_signal_regel_default_bedingung_empty():
    r = SignalRegel("R1", SignalTyp.EXTERN, TriggerAktion.FORTSETZEN, "test")
    assert r.bedingung == ""

def test_signal_regel_inaktiv():
    r = SignalRegel("R1", SignalTyp.EXTERN, TriggerAktion.FORTSETZEN, "test", ist_aktiv=False)
    assert r.ist_aktiv is False

# ===========================================================================
# SECTION 22: Integration — verarbeite_signal with default data
# ===========================================================================

def test_integration_sig001_with_default_rules():
    """SIG-001 is EXTERN + not expired => SR-001 matches => FORTSETZEN"""
    signale = {s.signal_id: s for s in get_default_signale()}
    regeln = get_default_signal_regeln()
    ergebnis = verarbeite_signal(signale["SIG-001"], regeln, NOW)
    assert ergebnis.erfolgreich is True
    assert ergebnis.trigger_aktion == TriggerAktion.FORTSETZEN

def test_integration_sig002_verarbeitet_still_matches_rules():
    """SIG-002 status=VERARBEITET but not expired => BENUTZER => SR-002 => FORTSETZEN"""
    signale = {s.signal_id: s for s in get_default_signale()}
    regeln = get_default_signal_regeln()
    ergebnis = verarbeite_signal(signale["SIG-002"], regeln, NOW)
    # status=VERARBEITET, but ist_abgelaufen checks ablauf_am which is None => not expired
    assert ergebnis.erfolgreich is True
    assert ergebnis.trigger_aktion == TriggerAktion.FORTSETZEN

def test_integration_sig003_expired_result():
    """SIG-003 is expired => erfolgreich=False"""
    signale = {s.signal_id: s for s in get_default_signale()}
    regeln = get_default_signal_regeln()
    ergebnis = verarbeite_signal(signale["SIG-003"], regeln, NOW)
    assert ergebnis.erfolgreich is False

def test_integration_sig004_intern_with_default_rules():
    """SIG-004 is INTERN => SR-004 matches => FORTSETZEN"""
    signale = {s.signal_id: s for s in get_default_signale()}
    regeln = get_default_signal_regeln()
    ergebnis = verarbeite_signal(signale["SIG-004"], regeln, NOW)
    assert ergebnis.erfolgreich is True
    assert ergebnis.trigger_aktion == TriggerAktion.FORTSETZEN

# ===========================================================================
# SECTION 23: ProzessGraph — _schritt_map
# ===========================================================================

def test_schritt_map_correct():
    s1 = make_schritt("A")
    s2 = make_schritt("B")
    g = make_graph([s1, s2], [])
    m = g._schritt_map()
    assert m["A"] is s1
    assert m["B"] is s2

def test_schritt_map_empty():
    g = make_graph([], [])
    assert g._schritt_map() == {}

# ===========================================================================
# SECTION 24: ProzessGraph — graph_id and attributes
# ===========================================================================

def test_graph_id_set():
    g = ProzessGraph("MY-GRAPH")
    assert g.graph_id == "MY-GRAPH"

def test_graph_default_empty_schritte():
    g = ProzessGraph("G1")
    assert g.schritte == []

def test_graph_default_empty_kanten():
    g = ProzessGraph("G1")
    assert g.kanten == []

# ===========================================================================
# SECTION 25: Edge cases
# ===========================================================================

def test_bereite_schritte_unknown_von_schritt_id_skipped():
    """Kante references non-existent von_schritt_id — should be skipped (no block)."""
    g = make_graph(
        [make_schritt("B")],
        [make_kante("NONEXISTENT", "B", AbhaengigkeitsTyp.SEQUENZIELL)]
    )
    ids = [s.schritt_id for s in g.bereite_schritte()]
    assert "B" in ids

def test_verarbeite_empty_regeln_list():
    s = make_signal("S1", "WI-1", typ=SignalTyp.EXTERN)
    ergebnis = verarbeite_signal(s, [], NOW)
    assert ergebnis.erfolgreich is False
    assert "Keine passende Regel" in ergebnis.nachricht

def test_topo_disconnected_graph():
    """Two unconnected components."""
    g = make_graph(
        [make_schritt("A"), make_schritt("B"), make_schritt("C"), make_schritt("D")],
        [make_kante("A", "B"), make_kante("C", "D")]
    )
    result = g.topologische_reihenfolge()
    assert len(result) == 4
    assert result.index("A") < result.index("B")
    assert result.index("C") < result.index("D")

def test_bereite_schritte_uebersprungen_excluded():
    """UEBERSPRUNGEN step should not appear in bereite_schritte."""
    g = make_graph([make_schritt("S1", SchrittStatus.UEBERSPRUNGEN)], [])
    assert g.bereite_schritte() == []

def test_bereite_schritte_bereit_excluded():
    """Already BEREIT step should not appear again in bereite_schritte."""
    g = make_graph([make_schritt("S1", SchrittStatus.BEREIT)], [])
    assert g.bereite_schritte() == []
