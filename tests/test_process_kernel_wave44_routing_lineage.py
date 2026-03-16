"""
Wave 44 — Process Routing Contracts & Data Lineage Contracts
60 deterministic pytest tests; no mocking, no server/DB required.
"""
from __future__ import annotations

from datetime import datetime

import pytest

# ---------------------------------------------------------------------------
# Imports — Module 1: process_routing_contracts
# ---------------------------------------------------------------------------
from app.core.process_routing_contracts import (
    RoutingBedingung,
    RoutingBedingungsTyp,
    RoutingEntscheidung,
    RoutingErgebnis,
    RoutingRegel,
    RoutingZielTyp,
    get_default_routing_regeln,
    route_nachricht,
)

# ---------------------------------------------------------------------------
# Imports — Module 2: data_lineage_contracts
# ---------------------------------------------------------------------------
from app.core.data_lineage_contracts import (
    LineageKante,
    LineageKnoten,
    LineageKnotenTyp,
    LineageStatus,
    LineageGraph,
    TransformationsTyp,
    erstelle_lineage_graph,
    get_default_lineage_graph,
)


# ===========================================================================
# MODULE 1 — process_routing_contracts (30 tests)
# ===========================================================================

# --- Enum membership tests ---

def test_routing_bedingungstyp_all_members():
    members = {m.value for m in RoutingBedingungsTyp}
    assert members == {"IMMER", "WERT_GLEICH", "WERT_GROESSER", "WERT_KLEINER",
                       "FELD_VORHANDEN", "ROLLE_ERLAUBT"}


def test_routing_zieltyp_all_members():
    members = {m.value for m in RoutingZielTyp}
    assert members == {"WORKFLOW_SCHRITT", "QUEUE", "EXTERN", "DEAD_LETTER", "ESKALATION"}


def test_routing_ergebnis_all_members():
    members = {m.value for m in RoutingErgebnis}
    assert members == {"GEROUTET", "KEIN_MATCH", "DEAD_LETTER", "FEHLER"}


# --- RoutingBedingung.pruefe ---

def test_bedingung_immer_always_true():
    b = RoutingBedingung("B1", RoutingBedingungsTyp.IMMER)
    assert b.pruefe({}) is True
    assert b.pruefe({"x": 99}) is True


def test_bedingung_feld_vorhanden_present():
    b = RoutingBedingung("B2", RoutingBedingungsTyp.FELD_VORHANDEN, feld="kostenstelle")
    assert b.pruefe({"kostenstelle": "K100"}) is True


def test_bedingung_feld_vorhanden_missing():
    b = RoutingBedingung("B3", RoutingBedingungsTyp.FELD_VORHANDEN, feld="kostenstelle")
    assert b.pruefe({}) is False


def test_bedingung_wert_gleich_match():
    b = RoutingBedingung("B4", RoutingBedingungsTyp.WERT_GLEICH,
                         feld="qualitaet_status", wert="ABGELEHNT")
    assert b.pruefe({"qualitaet_status": "ABGELEHNT"}) is True


def test_bedingung_wert_groesser_true():
    b = RoutingBedingung("B6", RoutingBedingungsTyp.WERT_GROESSER, feld="betrag_eur", wert="10000")
    assert b.pruefe({"betrag_eur": 15000}) is True


def test_bedingung_wert_groesser_false():
    b = RoutingBedingung("B7", RoutingBedingungsTyp.WERT_GROESSER, feld="betrag_eur", wert="10000")
    assert b.pruefe({"betrag_eur": 5000}) is False


def test_bedingung_wert_kleiner_true():
    b = RoutingBedingung("B9", RoutingBedingungsTyp.WERT_KLEINER, feld="menge_t", wert="100")
    assert b.pruefe({"menge_t": 50}) is True


def test_bedingung_wert_kleiner_false():
    b = RoutingBedingung("B10", RoutingBedingungsTyp.WERT_KLEINER, feld="menge_t", wert="100")
    assert b.pruefe({"menge_t": 200}) is False


def test_bedingung_rolle_erlaubt_match():
    b = RoutingBedingung("B12", RoutingBedingungsTyp.ROLLE_ERLAUBT, wert="sachbearbeiter")
    assert b.pruefe({"rolle": "sachbearbeiter"}) is True


def test_bedingung_as_dict_contains_typ_string():
    b = RoutingBedingung("B14", RoutingBedingungsTyp.WERT_GLEICH, feld="status", wert="OK")
    d = b.as_dict()
    assert d["typ"] == "WERT_GLEICH"
    assert d["feld"] == "status"
    assert d["wert"] == "OK"


# --- RoutingRegel ---

def test_routing_regel_pruefe_bedingungen_all_pass():
    b1 = RoutingBedingung("RB1", RoutingBedingungsTyp.IMMER)
    b2 = RoutingBedingung("RB2", RoutingBedingungsTyp.FELD_VORHANDEN, feld="x")
    regel = RoutingRegel("R1", "wf", 1, [b1, b2], RoutingZielTyp.QUEUE, "q1")
    assert regel.pruefe_bedingungen({"x": "y"}) is True


def test_routing_regel_pruefe_bedingungen_one_fails():
    b1 = RoutingBedingung("RB1", RoutingBedingungsTyp.IMMER)
    b2 = RoutingBedingung("RB2", RoutingBedingungsTyp.FELD_VORHANDEN, feld="fehlt")
    regel = RoutingRegel("R2", "wf", 1, [b1, b2], RoutingZielTyp.QUEUE, "q1")
    assert regel.pruefe_bedingungen({}) is False


def test_routing_regel_as_dict_bedingungen_anzahl():
    b = RoutingBedingung("RB1", RoutingBedingungsTyp.IMMER)
    regel = RoutingRegel("R3", "test", 5, [b], RoutingZielTyp.WORKFLOW_SCHRITT, "schritt-1")
    d = regel.as_dict()
    assert d["bedingungen_anzahl"] == 1
    assert d["ziel_typ"] == "WORKFLOW_SCHRITT"


# --- RoutingEntscheidung ---

def test_routing_entscheidung_wurde_geroutet_true():
    e = RoutingEntscheidung(
        entscheidung_id="E1", workflow_typ="wf", kontext_snapshot={},
        ergebnis=RoutingErgebnis.GEROUTET,
        ziel_typ=RoutingZielTyp.QUEUE, ziel_id="q"
    )
    assert e.wurde_geroutet is True


def test_routing_entscheidung_wurde_geroutet_false():
    e = RoutingEntscheidung(
        entscheidung_id="E2", workflow_typ="wf", kontext_snapshot={},
        ergebnis=RoutingErgebnis.DEAD_LETTER,
    )
    assert e.wurde_geroutet is False


def test_routing_entscheidung_as_dict():
    e = RoutingEntscheidung(
        entscheidung_id="E3", workflow_typ="wf", kontext_snapshot={},
        ergebnis=RoutingErgebnis.GEROUTET,
        gematchte_regel_id="RR-001",
        ziel_typ=RoutingZielTyp.ESKALATION, ziel_id="esc-queue"
    )
    d = e.as_dict()
    assert d["wurde_geroutet"] is True
    assert d["ergebnis"] == "GEROUTET"
    assert "entschieden_am" in d


# --- route_nachricht + get_default_routing_regeln ---

def test_route_nachricht_kontrakt_abgelehnt_eskalation():
    result = route_nachricht("kontrakt_annahme", {"qualitaet_status": "ABGELEHNT"})
    assert result.wurde_geroutet is True
    assert result.gematchte_regel_id == "RR-001"
    assert result.ziel_id == "eskalation-qualitaet-queue"


def test_route_nachricht_kontrakt_grossmenge_sachbearbeiter():
    result = route_nachricht("kontrakt_annahme", {"menge_t": 600, "rolle": "sachbearbeiter"})
    assert result.gematchte_regel_id == "RR-002"
    assert result.ziel_id == "schritt-leiter-freigabe"


def test_route_nachricht_kontrakt_fallback_standard():
    result = route_nachricht("kontrakt_annahme", {"menge_t": 100, "rolle": "gast"})
    assert result.gematchte_regel_id == "RR-003"
    assert result.ziel_id == "schritt-standard-freigabe"


def test_route_nachricht_ap_approval_high_amount():
    result = route_nachricht("ap_approval", {"betrag_eur": 25000})
    assert result.gematchte_regel_id == "RR-004"
    assert result.ziel_id == "schritt-4-augen-pruefung"


def test_route_nachricht_ap_approval_kostenstelle():
    result = route_nachricht("ap_approval", {"betrag_eur": 500, "kostenstelle": "K200"})
    assert result.gematchte_regel_id == "RR-005"
    assert result.ziel_id == "schritt-kostenstellen-freigabe"


def test_route_nachricht_ap_approval_fallback_queue():
    result = route_nachricht("ap_approval", {"betrag_eur": 50})
    assert result.gematchte_regel_id == "RR-006"
    assert result.ziel_typ == RoutingZielTyp.QUEUE
    assert result.ziel_id == "ap-standard-approval-queue"


def test_route_nachricht_unknown_workflow_dead_letter():
    result = route_nachricht("unbekannter_typ", {"x": 1})
    assert result.ergebnis == RoutingErgebnis.DEAD_LETTER
    assert result.ziel_id == "dead-letter-queue"


def test_route_nachricht_auto_entscheidung_id():
    result = route_nachricht("ap_approval", {"betrag_eur": 50})
    assert result.entscheidung_id.startswith("RE-")


def test_route_nachricht_custom_entscheidung_id():
    result = route_nachricht("ap_approval", {"betrag_eur": 50},
                             entscheidung_id="CUSTOM-ID-99")
    assert result.entscheidung_id == "CUSTOM-ID-99"


def test_get_default_routing_regeln_count_and_ids():
    regeln = get_default_routing_regeln()
    assert len(regeln) == 6
    ids = {r.regel_id for r in regeln}
    assert ids == {"RR-001", "RR-002", "RR-003", "RR-004", "RR-005", "RR-006"}


def test_get_default_routing_regeln_workflow_split():
    regeln = get_default_routing_regeln()
    assert len([r for r in regeln if r.workflow_typ == "kontrakt_annahme"]) == 3
    assert len([r for r in regeln if r.workflow_typ == "ap_approval"]) == 3


def test_kontext_snapshot_is_copy():
    kontext = {"betrag_eur": 50}
    result = route_nachricht("ap_approval", kontext)
    kontext["betrag_eur"] = 99999
    assert result.kontext_snapshot["betrag_eur"] == 50


# ===========================================================================
# MODULE 2 — data_lineage_contracts (30 tests)
# ===========================================================================

# --- Enum membership tests ---

def test_lineage_knoten_typ_all_members():
    members = {m.value for m in LineageKnotenTyp}
    assert members == {"QUELLE", "TRANSFORMATION", "AGGREGATION", "SENKE", "ZWISCHENSPEICHER"}


def test_transformations_typ_all_members():
    members = {m.value for m in TransformationsTyp}
    assert members == {"FILTER", "PROJEKTION", "ANREICHERUNG", "BERECHNUNG",
                       "NORMALISIERUNG", "ZUSAMMENFUEHRUNG"}


def test_lineage_status_all_members():
    members = {m.value for m in LineageStatus}
    assert members == {"AKTIV", "VERALTET", "ARCHIVIERT"}


# --- LineageKnoten ---

def test_lineage_knoten_ist_quelle_true():
    k = LineageKnoten("K1", "Quelle", LineageKnotenTyp.QUELLE, "T1", datetime(2026, 1, 1))
    assert k.ist_quelle is True
    assert k.ist_senke is False


def test_lineage_knoten_ist_senke_true():
    k = LineageKnoten("K2", "Senke", LineageKnotenTyp.SENKE, "T1", datetime(2026, 1, 1))
    assert k.ist_senke is True
    assert k.ist_quelle is False


def test_lineage_knoten_default_status_aktiv():
    k = LineageKnoten("K4", "Test", LineageKnotenTyp.AGGREGATION, "T1", datetime(2026, 1, 1))
    assert k.status == LineageStatus.AKTIV


def test_lineage_knoten_as_dict_fields():
    k = LineageKnoten("K5", "MyKnoten", LineageKnotenTyp.QUELLE, "T99",
                      datetime(2026, 3, 1), schema_id="ES-001")
    d = k.as_dict()
    assert d["knoten_id"] == "K5"
    assert d["knoten_typ"] == "QUELLE"
    assert d["ist_quelle"] is True
    assert d["ist_senke"] is False
    assert d["status"] == "AKTIV"
    assert d["schema_id"] == "ES-001"


def test_lineage_knoten_as_dict_erstellt_am_iso():
    k = LineageKnoten("K6", "Test", LineageKnotenTyp.SENKE, "T1", datetime(2026, 3, 15))
    d = k.as_dict()
    assert d["erstellt_am"].startswith("2026-03-15")


# --- LineageKante ---

def test_lineage_kante_as_dict_transformations_typ():
    kante = LineageKante("KT1", "K1", "K2", TransformationsTyp.FILTER,
                         "Filterschritt", datetime(2026, 3, 1))
    d = kante.as_dict()
    assert d["transformations_typ"] == "FILTER"
    assert d["von_knoten_id"] == "K1"
    assert d["zu_knoten_id"] == "K2"


def test_lineage_kante_erstellt_am_iso():
    kante = LineageKante("KT2", "A", "B", TransformationsTyp.BERECHNUNG,
                         erstellt_am=datetime(2026, 3, 5))
    assert "2026-03-05" in kante.as_dict()["erstellt_am"]


# --- LineageGraph ---

def test_erstelle_lineage_graph_returns_graph():
    k = LineageKnoten("K1", "Q", LineageKnotenTyp.QUELLE, "T1", datetime(2026, 1, 1))
    g = erstelle_lineage_graph("G1", "T1", [k], [])
    assert isinstance(g, LineageGraph)
    assert g.graph_id == "G1"
    assert len(g.knoten) == 1


def test_lineage_graph_quellen_filtered():
    k1 = LineageKnoten("K1", "Q", LineageKnotenTyp.QUELLE, "T1", datetime(2026, 1, 1))
    k2 = LineageKnoten("K2", "T", LineageKnotenTyp.TRANSFORMATION, "T1", datetime(2026, 1, 2))
    g = LineageGraph("G2", "T1", [k1, k2])
    assert len(g.quellen) == 1
    assert g.quellen[0].knoten_id == "K1"


def test_lineage_graph_hat_zyklus_false_for_dag():
    k1 = LineageKnoten("K1", "A", LineageKnotenTyp.QUELLE, "T1", datetime(2026, 1, 1))
    k2 = LineageKnoten("K2", "B", LineageKnotenTyp.SENKE, "T1", datetime(2026, 1, 1))
    kante = LineageKante("KT1", "K1", "K2", TransformationsTyp.FILTER)
    g = LineageGraph("G4", "T1", [k1, k2], [kante])
    assert g.hat_zyklus is False


def test_lineage_graph_hat_zyklus_true_for_cycle():
    k1 = LineageKnoten("K1", "A", LineageKnotenTyp.QUELLE, "T1", datetime(2026, 1, 1))
    k2 = LineageKnoten("K2", "B", LineageKnotenTyp.TRANSFORMATION, "T1", datetime(2026, 1, 1))
    k3 = LineageKnoten("K3", "C", LineageKnotenTyp.AGGREGATION, "T1", datetime(2026, 1, 1))
    kanten = [
        LineageKante("KT1", "K1", "K2", TransformationsTyp.FILTER),
        LineageKante("KT2", "K2", "K3", TransformationsTyp.BERECHNUNG),
        LineageKante("KT3", "K3", "K1", TransformationsTyp.PROJEKTION),
    ]
    g = LineageGraph("G5", "T1", [k1, k2, k3], kanten)
    assert g.hat_zyklus is True


def test_lineage_graph_finde_pfad_same_node():
    k1 = LineageKnoten("K1", "A", LineageKnotenTyp.QUELLE, "T1", datetime(2026, 1, 1))
    g = LineageGraph("G6", "T1", [k1], [])
    assert g.finde_pfad("K1", "K1") == ["K1"]


def test_lineage_graph_finde_pfad_direct_edge():
    k1 = LineageKnoten("K1", "A", LineageKnotenTyp.QUELLE, "T1", datetime(2026, 1, 1))
    k2 = LineageKnoten("K2", "B", LineageKnotenTyp.SENKE, "T1", datetime(2026, 1, 1))
    kante = LineageKante("KT1", "K1", "K2", TransformationsTyp.FILTER)
    g = LineageGraph("G7", "T1", [k1, k2], [kante])
    assert g.finde_pfad("K1", "K2") == ["K1", "K2"]


def test_lineage_graph_finde_pfad_no_path_reverse():
    k1 = LineageKnoten("K1", "A", LineageKnotenTyp.QUELLE, "T1", datetime(2026, 1, 1))
    k2 = LineageKnoten("K2", "B", LineageKnotenTyp.SENKE, "T1", datetime(2026, 1, 1))
    kante = LineageKante("KT1", "K1", "K2", TransformationsTyp.FILTER)
    g = LineageGraph("G8", "T1", [k1, k2], [kante])
    assert g.finde_pfad("K2", "K1") == []


def test_lineage_graph_as_dict_counts():
    k1 = LineageKnoten("K1", "Q", LineageKnotenTyp.QUELLE, "T1", datetime(2026, 1, 1))
    k2 = LineageKnoten("K2", "S", LineageKnotenTyp.SENKE, "T1", datetime(2026, 1, 1))
    kante = LineageKante("KT1", "K1", "K2", TransformationsTyp.BERECHNUNG)
    g = LineageGraph("G9", "T1", [k1, k2], [kante])
    d = g.as_dict()
    assert d["knoten_anzahl"] == 2
    assert d["kanten_anzahl"] == 1
    assert d["quellen_anzahl"] == 1
    assert d["senken_anzahl"] == 1
    assert d["hat_zyklus"] is False


# --- get_default_lineage_graph ---

def test_get_default_lineage_graph_five_knoten():
    g = get_default_lineage_graph()
    assert len(g.knoten) == 5


def test_get_default_lineage_graph_five_kanten():
    g = get_default_lineage_graph()
    assert len(g.kanten) == 5


def test_get_default_lineage_graph_no_cycle():
    g = get_default_lineage_graph()
    assert g.hat_zyklus is False


def test_get_default_lineage_graph_one_quelle_lk001():
    g = get_default_lineage_graph()
    assert len(g.quellen) == 1
    assert g.quellen[0].knoten_id == "LK-001"


def test_get_default_lineage_graph_one_senke_lk004():
    g = get_default_lineage_graph()
    assert len(g.senken) == 1
    assert g.senken[0].knoten_id == "LK-004"


def test_get_default_lineage_graph_pfad_quelle_to_senke():
    g = get_default_lineage_graph()
    path = g.finde_pfad("LK-001", "LK-004")
    assert len(path) > 0
    assert path[0] == "LK-001"
    assert path[-1] == "LK-004"


def test_get_default_lineage_graph_no_reverse_pfad():
    g = get_default_lineage_graph()
    assert g.finde_pfad("LK-004", "LK-001") == []


def test_get_default_lineage_graph_knoten_ids():
    g = get_default_lineage_graph()
    ids = {k.knoten_id for k in g.knoten}
    assert ids == {"LK-001", "LK-002", "LK-003", "LK-004", "LK-005"}


def test_get_default_lineage_graph_lkt001_normalisierung():
    g = get_default_lineage_graph()
    kante = next(k for k in g.kanten if k.kante_id == "LKT-001")
    assert kante.von_knoten_id == "LK-001"
    assert kante.zu_knoten_id == "LK-002"
    assert kante.transformations_typ == TransformationsTyp.NORMALISIERUNG


def test_get_default_lineage_graph_lkt005_filter():
    g = get_default_lineage_graph()
    kante = next(k for k in g.kanten if k.kante_id == "LKT-005")
    assert kante.von_knoten_id == "LK-001"
    assert kante.zu_knoten_id == "LK-003"
    assert kante.transformations_typ == TransformationsTyp.FILTER


def test_get_default_lineage_graph_as_dict_structure():
    g = get_default_lineage_graph()
    d = g.as_dict()
    assert d["knoten_anzahl"] == 5
    assert d["kanten_anzahl"] == 5
    assert d["quellen_anzahl"] == 1
    assert d["senken_anzahl"] == 1
    assert d["hat_zyklus"] is False
    assert "knoten" in d
    assert "kanten" in d
