"""
Wave 41 — Process Capacity Contracts & Event Replay Contracts
60 passing deterministic tests — no database, no server, no mocking required.
"""
from __future__ import annotations

from datetime import datetime

import pytest

from app.core.process_capacity_contracts import (
    AuslastungsStatus,
    EngpassStufe,
    KapazitaetsEinheit,
    KapazitaetsTyp,
    KapazitaetsPruefungErgebnis,
    WorkloadPrognose,
    berechne_engpass_stufe,
    get_default_kapazitaets_einheiten,
    pruefe_workflow_kapazitaet,
)
from app.core.event_replay_contracts import (
    EventReplayAuftrag,
    EventSnapshot,
    ReplayCursor,
    ReplayKonsistenzPruefung,
    ReplayModus,
    ReplayStatus,
    SnapshotTyp,
    erstelle_replay_auftrag,
    get_default_replay_auftraege,
    pruefe_replay_konsistenz,
)


# ===========================================================================
# MODULE 1: process_capacity_contracts (30 tests)
# ===========================================================================

# --- KapazitaetsTyp enum ---

def test_kapazitaets_typ_values():
    assert KapazitaetsTyp.ROLLE.value == "ROLLE"
    assert KapazitaetsTyp.WORKSTATION.value == "WORKSTATION"
    assert KapazitaetsTyp.SYSTEM.value == "SYSTEM"
    assert KapazitaetsTyp.QUEUE.value == "QUEUE"


def test_kapazitaets_typ_count():
    assert len(KapazitaetsTyp) == 4


# --- AuslastungsStatus enum ---

def test_auslastungs_status_values():
    assert AuslastungsStatus.UNTERAUSGELASTET.value == "UNTERAUSGELASTET"
    assert AuslastungsStatus.NORMAL.value == "NORMAL"
    assert AuslastungsStatus.AUSGELASTET.value == "AUSGELASTET"
    assert AuslastungsStatus.UEBERLASTET.value == "UEBERLASTET"


# --- EngpassStufe enum ---

def test_engpass_stufe_values():
    assert EngpassStufe.KEIN.value == "KEIN"
    assert EngpassStufe.GERING.value == "GERING"
    assert EngpassStufe.MODERAT.value == "MODERAT"
    assert EngpassStufe.KRITISCH.value == "KRITISCH"


# --- KapazitaetsEinheit.auslastung_pct ---

def test_auslastung_pct_normal():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.ROLLE, 8.0, 4.0, "T1")
    assert ke.auslastung_pct == 50.0


def test_auslastung_pct_rounded():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.ROLLE, 3.0, 1.0, "T1")
    assert ke.auslastung_pct == round(1.0 / 3.0 * 100, 2)


def test_auslastung_pct_zero_max():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.ROLLE, 0.0, 5.0, "T1")
    assert ke.auslastung_pct == 0.0


def test_auslastung_pct_full():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.QUEUE, 100.0, 100.0, "T1")
    assert ke.auslastung_pct == 100.0


# --- KapazitaetsEinheit.auslastungs_status ---

def test_auslastungs_status_unterausgelastet():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.ROLLE, 100.0, 10.0, "T1")
    assert ke.auslastungs_status == AuslastungsStatus.UNTERAUSGELASTET


def test_auslastungs_status_normal():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.ROLLE, 100.0, 50.0, "T1")
    assert ke.auslastungs_status == AuslastungsStatus.NORMAL


def test_auslastungs_status_ausgelastet():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.WORKSTATION, 100.0, 80.0, "T1")
    assert ke.auslastungs_status == AuslastungsStatus.AUSGELASTET


def test_auslastungs_status_ueberlastet():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.SYSTEM, 100.0, 95.0, "T1")
    assert ke.auslastungs_status == AuslastungsStatus.UEBERLASTET


def test_auslastungs_status_boundary_normal_at_30():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.ROLLE, 100.0, 30.0, "T1")
    assert ke.auslastungs_status == AuslastungsStatus.NORMAL


# --- KapazitaetsEinheit.ist_engpass ---

def test_ist_engpass_false_below_90():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.ROLLE, 100.0, 89.9, "T1")
    assert ke.ist_engpass is False


def test_ist_engpass_true_at_90():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.ROLLE, 100.0, 90.0, "T1")
    assert ke.ist_engpass is True


def test_ist_engpass_true_above_90():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.QUEUE, 100.0, 99.0, "T1")
    assert ke.ist_engpass is True


# --- KapazitaetsEinheit.as_dict ---

def test_as_dict_contains_auslastung_pct():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.ROLLE, 10.0, 5.0, "T1")
    d = ke.as_dict()
    assert "auslastung_pct" in d
    assert d["auslastung_pct"] == 50.0


def test_as_dict_auslastungs_status_is_string():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.ROLLE, 10.0, 5.0, "T1")
    d = ke.as_dict()
    assert isinstance(d["auslastungs_status"], str)
    assert d["auslastungs_status"] == AuslastungsStatus.NORMAL.value


def test_as_dict_contains_ist_engpass():
    ke = KapazitaetsEinheit("KE-X", "Test", KapazitaetsTyp.ROLLE, 10.0, 5.0, "T1")
    d = ke.as_dict()
    assert "ist_engpass" in d
    assert d["ist_engpass"] is False


# --- WorkloadPrognose.deckungsgrad_pct ---

def test_deckungsgrad_fully_covered():
    wp = WorkloadPrognose("P-1", "KE-X", 8.0, geplante_aufgaben=100.0, verfuegbare_kapazitaet=150.0)
    assert wp.deckungsgrad_pct == 100.0


def test_deckungsgrad_partial():
    wp = WorkloadPrognose("P-1", "KE-X", 8.0, geplante_aufgaben=100.0, verfuegbare_kapazitaet=75.0)
    assert wp.deckungsgrad_pct == 75.0


def test_deckungsgrad_no_tasks():
    wp = WorkloadPrognose("P-1", "KE-X", 8.0, geplante_aufgaben=0.0, verfuegbare_kapazitaet=50.0)
    assert wp.deckungsgrad_pct == 100.0


# --- berechne_engpass_stufe ---

def test_engpass_stufe_kein_below_75():
    assert berechne_engpass_stufe(74.9) == EngpassStufe.KEIN


def test_engpass_stufe_gering_at_75():
    assert berechne_engpass_stufe(75.0) == EngpassStufe.GERING


def test_engpass_stufe_moderat_at_85():
    assert berechne_engpass_stufe(85.0) == EngpassStufe.MODERAT


def test_engpass_stufe_kritisch_at_95():
    assert berechne_engpass_stufe(95.0) == EngpassStufe.KRITISCH


def test_engpass_stufe_kritisch_at_100():
    assert berechne_engpass_stufe(100.0) == EngpassStufe.KRITISCH


# --- get_default_kapazitaets_einheiten ---

def test_default_einheiten_count():
    einheiten = get_default_kapazitaets_einheiten()
    assert len(einheiten) == 6


def test_default_einheiten_ke001_normal():
    einheiten = get_default_kapazitaets_einheiten()
    ke001 = next(e for e in einheiten if e.einheit_id == "KE-001")
    assert ke001.auslastungs_status == AuslastungsStatus.NORMAL
    assert ke001.ist_engpass is False


def test_default_einheiten_ke002_engpass():
    einheiten = get_default_kapazitaets_einheiten()
    ke002 = next(e for e in einheiten if e.einheit_id == "KE-002")
    assert ke002.ist_engpass is True
    assert ke002.auslastungs_status == AuslastungsStatus.UEBERLASTET


def test_default_einheiten_ke004_engpass():
    einheiten = get_default_kapazitaets_einheiten()
    ke004 = next(e for e in einheiten if e.einheit_id == "KE-004")
    assert ke004.ist_engpass is True


def test_default_einheiten_ke006_engpass():
    einheiten = get_default_kapazitaets_einheiten()
    ke006 = next(e for e in einheiten if e.einheit_id == "KE-006")
    assert ke006.ist_engpass is True


# --- pruefe_workflow_kapazitaet ---

def _make_einheit(eid: str, aktuell: float, maxi: float, domain: str = "") -> KapazitaetsEinheit:
    return KapazitaetsEinheit(eid, f"Res-{eid}", KapazitaetsTyp.ROLLE, maxi, aktuell, "T1", domain)


def test_pruefe_kann_starten_no_engpass():
    einheiten = [_make_einheit("KE-A", 50.0, 100.0, "agrar")]
    ergebnis = pruefe_workflow_kapazitaet("WF-001", "agrar", einheiten)
    assert ergebnis.kann_gestartet_werden is True
    assert ergebnis.engpaesse == []
    assert ergebnis.empfehlungen == []


def test_pruefe_kann_nicht_starten_single_engpass():
    einheiten = [_make_einheit("KE-A", 95.0, 100.0, "agrar")]
    ergebnis = pruefe_workflow_kapazitaet("WF-002", "agrar", einheiten)
    assert ergebnis.kann_gestartet_werden is False
    assert "KE-A" in ergebnis.engpaesse
    assert len(ergebnis.empfehlungen) == 2


def test_pruefe_empfehlungen_single_engpass_mentions_id():
    einheiten = [_make_einheit("KE-A", 95.0, 100.0, "agrar")]
    ergebnis = pruefe_workflow_kapazitaet("WF-003", "agrar", einheiten)
    first_emp = ergebnis.empfehlungen[0]
    assert "KE-A" in first_emp


def test_pruefe_kann_nicht_starten_multi_engpass():
    einheiten = [
        _make_einheit("KE-A", 95.0, 100.0, "agrar"),
        _make_einheit("KE-B", 92.0, 100.0, "agrar"),
    ]
    ergebnis = pruefe_workflow_kapazitaet("WF-004", "agrar", einheiten)
    assert ergebnis.kann_gestartet_werden is False
    assert len(ergebnis.engpaesse) == 2
    assert len(ergebnis.empfehlungen) == 2


def test_pruefe_empfehlungen_multi_engpass_mentions_count():
    einheiten = [
        _make_einheit("KE-A", 95.0, 100.0, "agrar"),
        _make_einheit("KE-B", 92.0, 100.0, "agrar"),
    ]
    ergebnis = pruefe_workflow_kapazitaet("WF-005", "agrar", einheiten)
    first_emp = ergebnis.empfehlungen[0]
    assert "2" in first_emp


def test_pruefe_domain_filter_excludes_other_domain():
    einheiten = [
        _make_einheit("KE-A", 95.0, 100.0, "finance"),  # not included for agrar
        _make_einheit("KE-B", 50.0, 100.0, "agrar"),
    ]
    ergebnis = pruefe_workflow_kapazitaet("WF-006", "agrar", einheiten)
    assert ergebnis.kann_gestartet_werden is True


def test_pruefe_domain_filter_includes_empty_domain():
    einheiten = [
        _make_einheit("KE-GLOBAL", 95.0, 100.0, ""),  # domain="" → always included
        _make_einheit("KE-B", 50.0, 100.0, "agrar"),
    ]
    ergebnis = pruefe_workflow_kapazitaet("WF-007", "agrar", einheiten)
    assert ergebnis.kann_gestartet_werden is False
    assert "KE-GLOBAL" in ergebnis.engpaesse


def test_pruefe_geprueft_am_uses_zeitstempel():
    ts = datetime(2026, 3, 15, 10, 0, 0)
    ergebnis = pruefe_workflow_kapazitaet("WF-008", "agrar", [], zeitstempel=ts)
    assert ergebnis.geprueft_am == ts


def test_kapazitaets_pruefung_as_dict_geprueft_am_iso():
    ts = datetime(2026, 3, 15, 10, 0, 0)
    ergebnis = pruefe_workflow_kapazitaet("WF-009", "agrar", [], zeitstempel=ts)
    d = ergebnis.as_dict()
    assert d["geprueft_am"] == ts.isoformat()


def test_kapazitaets_pruefung_as_dict_empfehlung_anzahl():
    einheiten = [_make_einheit("KE-A", 95.0, 100.0, "agrar")]
    ergebnis = pruefe_workflow_kapazitaet("WF-010", "agrar", einheiten)
    d = ergebnis.as_dict()
    assert d["empfehlung_anzahl"] == 2


# ===========================================================================
# MODULE 2: event_replay_contracts (30 tests)
# ===========================================================================

# --- ReplayStatus enum ---

def test_replay_status_all_values():
    values = {s.value for s in ReplayStatus}
    assert values == {
        "AUSSTEHEND", "LAUFEND", "PAUSIERT",
        "ABGESCHLOSSEN", "FEHLGESCHLAGEN", "ABGEBROCHEN",
    }


# --- ReplayModus enum ---

def test_replay_modus_values():
    assert ReplayModus.VOLLSTAENDIG.value == "VOLLSTAENDIG"
    assert ReplayModus.TEILWEISE.value == "TEILWEISE"
    assert ReplayModus.SNAPSHOT_BASIERT.value == "SNAPSHOT_BASIERT"
    assert ReplayModus.DELTA.value == "DELTA"


# --- SnapshotTyp enum ---

def test_snapshot_typ_values():
    assert SnapshotTyp.VOLL.value == "VOLL"
    assert SnapshotTyp.INKREMENTELL.value == "INKREMENTELL"
    assert SnapshotTyp.CHECKPOINT.value == "CHECKPOINT"


# --- EventReplayAuftrag.ist_abgeschlossen ---

def test_ist_abgeschlossen_abgeschlossen():
    a = EventReplayAuftrag("RA-X", "T1", "S1", ReplayModus.VOLLSTAENDIG, ReplayStatus.ABGESCHLOSSEN)
    assert a.ist_abgeschlossen is True


def test_ist_abgeschlossen_fehlgeschlagen():
    a = EventReplayAuftrag("RA-X", "T1", "S1", ReplayModus.VOLLSTAENDIG, ReplayStatus.FEHLGESCHLAGEN)
    assert a.ist_abgeschlossen is True


def test_ist_abgeschlossen_abgebrochen():
    a = EventReplayAuftrag("RA-X", "T1", "S1", ReplayModus.VOLLSTAENDIG, ReplayStatus.ABGEBROCHEN)
    assert a.ist_abgeschlossen is True


def test_ist_abgeschlossen_false_for_laufend():
    a = EventReplayAuftrag("RA-X", "T1", "S1", ReplayModus.VOLLSTAENDIG, ReplayStatus.LAUFEND)
    assert a.ist_abgeschlossen is False


def test_ist_abgeschlossen_false_for_ausstehend():
    a = EventReplayAuftrag("RA-X", "T1", "S1", ReplayModus.DELTA, ReplayStatus.AUSSTEHEND)
    assert a.ist_abgeschlossen is False


# --- EventReplayAuftrag.dauer_sekunden ---

def test_dauer_sekunden_none_if_not_started():
    a = EventReplayAuftrag("RA-X", "T1", "S1", ReplayModus.VOLLSTAENDIG, ReplayStatus.AUSSTEHEND)
    assert a.dauer_sekunden is None


def test_dauer_sekunden_none_if_not_finished():
    start = datetime(2026, 3, 15, 6, 0, 0)
    a = EventReplayAuftrag("RA-X", "T1", "S1", ReplayModus.VOLLSTAENDIG, ReplayStatus.LAUFEND,
                           gestartet_am=start)
    assert a.dauer_sekunden is None


def test_dauer_sekunden_correct():
    start = datetime(2026, 3, 15, 6, 0, 0)
    end = datetime(2026, 3, 15, 6, 1, 30)  # 90 seconds later
    a = EventReplayAuftrag("RA-X", "T1", "S1", ReplayModus.VOLLSTAENDIG, ReplayStatus.ABGESCHLOSSEN,
                           gestartet_am=start, abgeschlossen_am=end)
    assert a.dauer_sekunden == 90.0


# --- EventReplayAuftrag.durchsatz_pro_sekunde ---

def test_durchsatz_none_if_dauer_none():
    a = EventReplayAuftrag("RA-X", "T1", "S1", ReplayModus.VOLLSTAENDIG, ReplayStatus.AUSSTEHEND,
                           verarbeitete_ereignisse=100)
    assert a.durchsatz_pro_sekunde is None


def test_durchsatz_correct():
    start = datetime(2026, 3, 15, 6, 0, 0)
    end = datetime(2026, 3, 15, 6, 1, 40)  # 100 seconds
    a = EventReplayAuftrag("RA-X", "T1", "S1", ReplayModus.VOLLSTAENDIG, ReplayStatus.ABGESCHLOSSEN,
                           gestartet_am=start, abgeschlossen_am=end,
                           verarbeitete_ereignisse=500)
    assert a.durchsatz_pro_sekunde == 5.0


# --- EventReplayAuftrag.as_dict ---

def test_as_dict_replay_contains_ist_abgeschlossen():
    a = EventReplayAuftrag("RA-X", "T1", "S1", ReplayModus.VOLLSTAENDIG, ReplayStatus.ABGESCHLOSSEN)
    d = a.as_dict()
    assert "ist_abgeschlossen" in d
    assert d["ist_abgeschlossen"] is True


def test_as_dict_replay_contains_dauer_sekunden():
    a = EventReplayAuftrag("RA-X", "T1", "S1", ReplayModus.VOLLSTAENDIG, ReplayStatus.AUSSTEHEND)
    d = a.as_dict()
    assert "dauer_sekunden" in d
    assert d["dauer_sekunden"] is None


def test_as_dict_replay_contains_durchsatz():
    a = EventReplayAuftrag("RA-X", "T1", "S1", ReplayModus.VOLLSTAENDIG, ReplayStatus.AUSSTEHEND)
    d = a.as_dict()
    assert "durchsatz_pro_sekunde" in d


# --- ReplayCursor.as_dict ---

def test_cursor_as_dict_iso_string():
    ts = datetime(2026, 3, 15, 12, 0, 0)
    c = ReplayCursor("C-1", "T1", "S1", aktuelle_position=42, letzte_aktualisierung=ts,
                     verbraucher_id="proj:settlement")
    d = c.as_dict()
    assert d["letzte_aktualisierung"] == ts.isoformat()


def test_cursor_as_dict_keys():
    ts = datetime(2026, 3, 15, 12, 0, 0)
    c = ReplayCursor("C-1", "T1", "S1", aktuelle_position=10, letzte_aktualisierung=ts,
                     verbraucher_id="agent:x")
    d = c.as_dict()
    assert "cursor_id" in d
    assert "aktuelle_position" in d
    assert d["aktuelle_position"] == 10


# --- EventSnapshot ---

def test_snapshot_as_dict_aggregat_zustand_groesse():
    ts = datetime(2026, 3, 15, 8, 0, 0)
    s = EventSnapshot("SN-1", "T1", "S1", position=100, snapshot_typ=SnapshotTyp.VOLL,
                      erstellt_am=ts, aggregat_zustand={"a": 1, "b": 2, "c": 3})
    d = s.as_dict()
    assert d["aggregat_zustand_groesse"] == 3


def test_snapshot_alter_stunden_positive():
    ts = datetime(2026, 1, 1, 0, 0, 0)  # well in the past
    s = EventSnapshot("SN-1", "T1", "S1", position=0, snapshot_typ=SnapshotTyp.CHECKPOINT,
                      erstellt_am=ts)
    assert s.alter_stunden > 0


def test_snapshot_as_dict_erstellt_am_iso():
    ts = datetime(2026, 3, 15, 8, 0, 0)
    s = EventSnapshot("SN-1", "T1", "S1", position=0, snapshot_typ=SnapshotTyp.VOLL,
                      erstellt_am=ts)
    d = s.as_dict()
    assert d["erstellt_am"] == ts.isoformat()


def test_snapshot_empty_zustand_groesse_zero():
    ts = datetime(2026, 3, 15, 8, 0, 0)
    s = EventSnapshot("SN-1", "T1", "S1", position=0, snapshot_typ=SnapshotTyp.INKREMENTELL,
                      erstellt_am=ts)
    d = s.as_dict()
    assert d["aggregat_zustand_groesse"] == 0


# --- ReplayKonsistenzPruefung.hat_probleme ---

def test_hat_probleme_false_when_all_ok():
    p = ReplayKonsistenzPruefung("P-1", "S1", 0, 3, ist_konsistent=True)
    assert p.hat_probleme is False


def test_hat_probleme_true_when_not_konsistent():
    p = ReplayKonsistenzPruefung("P-1", "S1", 0, 3, ist_konsistent=False)
    assert p.hat_probleme is True


def test_hat_probleme_true_when_luecken():
    p = ReplayKonsistenzPruefung("P-1", "S1", 0, 4, ist_konsistent=True, luecken=[2])
    assert p.hat_probleme is True


def test_hat_probleme_true_when_duplikate():
    p = ReplayKonsistenzPruefung("P-1", "S1", 0, 2, ist_konsistent=True, duplikate=[1])
    assert p.hat_probleme is True


# --- pruefe_replay_konsistenz ---

def test_konsistenz_empty_list():
    result = pruefe_replay_konsistenz("PR-1", "S1", [])
    assert result.ist_konsistent is True
    assert result.luecken == []
    assert result.duplikate == []
    assert result.von_position == 0
    assert result.bis_position == 0


def test_konsistenz_consecutive():
    result = pruefe_replay_konsistenz("PR-2", "S1", [0, 1, 2, 3])
    assert result.ist_konsistent is True
    assert result.luecken == []
    assert result.duplikate == []


def test_konsistenz_gap_detected():
    result = pruefe_replay_konsistenz("PR-3", "S1", [0, 1, 3, 4])
    assert result.ist_konsistent is False
    assert 2 in result.luecken


def test_konsistenz_duplicate_detected():
    result = pruefe_replay_konsistenz("PR-4", "S1", [0, 1, 1, 2])
    assert result.ist_konsistent is False
    assert 1 in result.duplikate


def test_konsistenz_multiple_gaps():
    result = pruefe_replay_konsistenz("PR-5", "S1", [0, 2, 4])
    assert result.ist_konsistent is False
    assert sorted(result.luecken) == [1, 3]


def test_konsistenz_von_bis_set_to_min_max():
    result = pruefe_replay_konsistenz("PR-6", "S1", [3, 4, 5, 6])
    assert result.von_position == 3
    assert result.bis_position == 6


# --- erstelle_replay_auftrag ---

def test_erstelle_replay_auftrag_status_ausstehend():
    a = erstelle_replay_auftrag("RA-NEW", "T1", "S1", ReplayModus.VOLLSTAENDIG)
    assert a.status == ReplayStatus.AUSSTEHEND


def test_erstelle_replay_auftrag_not_started():
    a = erstelle_replay_auftrag("RA-NEW", "T1", "S1", ReplayModus.DELTA)
    assert a.gestartet_am is None
    assert a.abgeschlossen_am is None
    assert a.verarbeitete_ereignisse == 0


def test_erstelle_replay_auftrag_mit_positionen():
    a = erstelle_replay_auftrag("RA-NEW", "T1", "S1", ReplayModus.TEILWEISE,
                                von_position=100, bis_position=200)
    assert a.von_position == 100
    assert a.bis_position == 200


def test_erstelle_replay_auftrag_erstellt_am_custom():
    ts = datetime(2026, 3, 15, 9, 0, 0)
    a = erstelle_replay_auftrag("RA-NEW", "T1", "S1", ReplayModus.DELTA, erstellt_am=ts)
    assert a.erstellt_am == ts


# --- get_default_replay_auftraege ---

def test_default_auftraege_count():
    auftraege = get_default_replay_auftraege()
    assert len(auftraege) == 3


def test_default_ra001_abgeschlossen():
    auftraege = get_default_replay_auftraege()
    ra001 = next(a for a in auftraege if a.auftrag_id == "RA-001")
    assert ra001.status == ReplayStatus.ABGESCHLOSSEN
    assert ra001.modus == ReplayModus.VOLLSTAENDIG
    assert ra001.verarbeitete_ereignisse == 3820
    assert ra001.dauer_sekunden is not None
    assert ra001.dauer_sekunden > 0


def test_default_ra002_laufend():
    auftraege = get_default_replay_auftraege()
    ra002 = next(a for a in auftraege if a.auftrag_id == "RA-002")
    assert ra002.status == ReplayStatus.LAUFEND
    assert ra002.modus == ReplayModus.SNAPSHOT_BASIERT
    assert ra002.verarbeitete_ereignisse == 240
    assert ra002.dauer_sekunden is None


def test_default_ra003_ausstehend():
    auftraege = get_default_replay_auftraege()
    ra003 = next(a for a in auftraege if a.auftrag_id == "RA-003")
    assert ra003.status == ReplayStatus.AUSSTEHEND
    assert ra003.modus == ReplayModus.DELTA
    assert ra003.verarbeitete_ereignisse == 0
    assert ra003.gestartet_am is None
