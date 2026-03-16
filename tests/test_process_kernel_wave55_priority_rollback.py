"""Wave 55: Priority Queue + Rollback Contracts — 130+ tests."""
import pytest
from datetime import datetime, timedelta

from app.core.process_priority_contracts import (
    AufgabenPrioritaet,
    WarteschlangenStatus,
    PRIORITAET_GEWICHT,
    PrioritaetsAufgabe,
    PrioritaetsWarteschlange,
    get_default_warteschlangen,
)
from app.core.workflow_rollback_contracts import (
    RollbackTyp,
    RollbackStatus,
    UmkehrbarkeitsGrad,
    RollbackSchritt,
    RollbackPlan,
    get_default_rollback_plaene,
)

NOW = datetime(2026, 3, 16, 10, 0, 0)


# ---------------------------------------------------------------------------
# Enum smoke tests
# ---------------------------------------------------------------------------

def test_aufgaben_prioritaet_values():
    assert AufgabenPrioritaet.KRITISCH == "KRITISCH"
    assert AufgabenPrioritaet.HOCH == "HOCH"
    assert AufgabenPrioritaet.MITTEL == "MITTEL"
    assert AufgabenPrioritaet.NIEDRIG == "NIEDRIG"
    assert AufgabenPrioritaet.HINTERGRUND == "HINTERGRUND"

def test_warteschlangen_status_values():
    assert WarteschlangenStatus.WARTEND == "WARTEND"
    assert WarteschlangenStatus.VERARBEITUNG == "VERARBEITUNG"
    assert WarteschlangenStatus.ABGESCHLOSSEN == "ABGESCHLOSSEN"
    assert WarteschlangenStatus.ABGEBROCHEN == "ABGEBROCHEN"

def test_rollback_typ_values():
    assert RollbackTyp.VOLLSTAENDIG == "VOLLSTAENDIG"
    assert RollbackTyp.TEILWEISE == "TEILWEISE"
    assert RollbackTyp.SCHRITT == "SCHRITT"

def test_rollback_status_values():
    assert RollbackStatus.AUSSTEHEND == "AUSSTEHEND"
    assert RollbackStatus.LAUFEND == "LAUFEND"
    assert RollbackStatus.ABGESCHLOSSEN == "ABGESCHLOSSEN"
    assert RollbackStatus.FEHLGESCHLAGEN == "FEHLGESCHLAGEN"
    assert RollbackStatus.NICHT_MOEGLICH == "NICHT_MOEGLICH"

def test_umkehrbarkeits_grad_values():
    assert UmkehrbarkeitsGrad.VOLLSTAENDIG == "VOLLSTAENDIG"
    assert UmkehrbarkeitsGrad.TEILWEISE == "TEILWEISE"
    assert UmkehrbarkeitsGrad.NICHT_UMKEHRBAR == "NICHT_UMKEHRBAR"


# ---------------------------------------------------------------------------
# PRIORITAET_GEWICHT
# ---------------------------------------------------------------------------

def test_prioritaet_gewicht_kritisch():
    assert PRIORITAET_GEWICHT[AufgabenPrioritaet.KRITISCH] == 0

def test_prioritaet_gewicht_hoch():
    assert PRIORITAET_GEWICHT[AufgabenPrioritaet.HOCH] == 1

def test_prioritaet_gewicht_mittel():
    assert PRIORITAET_GEWICHT[AufgabenPrioritaet.MITTEL] == 2

def test_prioritaet_gewicht_niedrig():
    assert PRIORITAET_GEWICHT[AufgabenPrioritaet.NIEDRIG] == 3

def test_prioritaet_gewicht_hintergrund():
    assert PRIORITAET_GEWICHT[AufgabenPrioritaet.HINTERGRUND] == 4

def test_prioritaet_gewicht_all_five_present():
    assert len(PRIORITAET_GEWICHT) == 5

def test_prioritaet_gewicht_unique_values():
    weights = list(PRIORITAET_GEWICHT.values())
    assert len(set(weights)) == 5

def test_prioritaet_gewicht_kritisch_less_than_hoch():
    assert PRIORITAET_GEWICHT[AufgabenPrioritaet.KRITISCH] < PRIORITAET_GEWICHT[AufgabenPrioritaet.HOCH]

def test_prioritaet_gewicht_hoch_less_than_mittel():
    assert PRIORITAET_GEWICHT[AufgabenPrioritaet.HOCH] < PRIORITAET_GEWICHT[AufgabenPrioritaet.MITTEL]

def test_prioritaet_gewicht_mittel_less_than_niedrig():
    assert PRIORITAET_GEWICHT[AufgabenPrioritaet.MITTEL] < PRIORITAET_GEWICHT[AufgabenPrioritaet.NIEDRIG]

def test_prioritaet_gewicht_niedrig_less_than_hintergrund():
    assert PRIORITAET_GEWICHT[AufgabenPrioritaet.NIEDRIG] < PRIORITAET_GEWICHT[AufgabenPrioritaet.HINTERGRUND]


# ---------------------------------------------------------------------------
# PrioritaetsAufgabe.sort_schluessel()
# ---------------------------------------------------------------------------

def _aufgabe(aufgabe_id, prioritaet, erstellt_am=None, status=WarteschlangenStatus.WARTEND):
    return PrioritaetsAufgabe(
        aufgabe_id=aufgabe_id,
        aufgabe_typ="test",
        prioritaet=prioritaet,
        tenant_id="T1",
        status=status,
        erstellt_am=erstellt_am or NOW,
    )

def test_sort_schluessel_returns_tuple():
    a = _aufgabe("A1", AufgabenPrioritaet.KRITISCH)
    result = a.sort_schluessel()
    assert isinstance(result, tuple)
    assert len(result) == 2

def test_sort_schluessel_kritisch_weight():
    a = _aufgabe("A1", AufgabenPrioritaet.KRITISCH)
    assert a.sort_schluessel()[0] == 0

def test_sort_schluessel_hoch_weight():
    a = _aufgabe("A1", AufgabenPrioritaet.HOCH)
    assert a.sort_schluessel()[0] == 1

def test_sort_schluessel_mittel_weight():
    a = _aufgabe("A1", AufgabenPrioritaet.MITTEL)
    assert a.sort_schluessel()[0] == 2

def test_sort_schluessel_niedrig_weight():
    a = _aufgabe("A1", AufgabenPrioritaet.NIEDRIG)
    assert a.sort_schluessel()[0] == 3

def test_sort_schluessel_hintergrund_weight():
    a = _aufgabe("A1", AufgabenPrioritaet.HINTERGRUND)
    assert a.sort_schluessel()[0] == 4

def test_sort_schluessel_datetime_component():
    a = _aufgabe("A1", AufgabenPrioritaet.MITTEL, NOW)
    assert a.sort_schluessel()[1] == NOW

def test_sort_schluessel_kritisch_less_than_hoch():
    a_k = _aufgabe("A1", AufgabenPrioritaet.KRITISCH, NOW)
    a_h = _aufgabe("A2", AufgabenPrioritaet.HOCH, NOW)
    assert a_k.sort_schluessel() < a_h.sort_schluessel()

def test_sort_schluessel_hoch_less_than_mittel():
    a_h = _aufgabe("A1", AufgabenPrioritaet.HOCH, NOW)
    a_m = _aufgabe("A2", AufgabenPrioritaet.MITTEL, NOW)
    assert a_h.sort_schluessel() < a_m.sort_schluessel()

def test_sort_schluessel_mittel_less_than_niedrig():
    a_m = _aufgabe("A1", AufgabenPrioritaet.MITTEL, NOW)
    a_n = _aufgabe("A2", AufgabenPrioritaet.NIEDRIG, NOW)
    assert a_m.sort_schluessel() < a_n.sort_schluessel()

def test_sort_schluessel_niedrig_less_than_hintergrund():
    a_n = _aufgabe("A1", AufgabenPrioritaet.NIEDRIG, NOW)
    a_bg = _aufgabe("A2", AufgabenPrioritaet.HINTERGRUND, NOW)
    assert a_n.sort_schluessel() < a_bg.sort_schluessel()

def test_sort_schluessel_same_priority_earlier_first():
    early = _aufgabe("A1", AufgabenPrioritaet.MITTEL, NOW)
    late = _aufgabe("A2", AufgabenPrioritaet.MITTEL, NOW + timedelta(minutes=5))
    assert early.sort_schluessel() < late.sort_schluessel()

def test_sort_schluessel_same_priority_same_time_equal():
    a1 = _aufgabe("A1", AufgabenPrioritaet.HOCH, NOW)
    a2 = _aufgabe("A2", AufgabenPrioritaet.HOCH, NOW)
    assert a1.sort_schluessel() == a2.sort_schluessel()


# ---------------------------------------------------------------------------
# PrioritaetsWarteschlange.naechste_aufgabe()
# ---------------------------------------------------------------------------

def test_naechste_aufgabe_empty_queue():
    q = PrioritaetsWarteschlange("Q1")
    assert q.naechste_aufgabe() is None

def test_naechste_aufgabe_all_abgeschlossen():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A1", AufgabenPrioritaet.MITTEL, status=WarteschlangenStatus.ABGESCHLOSSEN),
    ])
    assert q.naechste_aufgabe() is None

def test_naechste_aufgabe_all_verarbeitung():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A1", AufgabenPrioritaet.HOCH, status=WarteschlangenStatus.VERARBEITUNG),
    ])
    assert q.naechste_aufgabe() is None

def test_naechste_aufgabe_all_abgebrochen():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A1", AufgabenPrioritaet.KRITISCH, status=WarteschlangenStatus.ABGEBROCHEN),
    ])
    assert q.naechste_aufgabe() is None

def test_naechste_aufgabe_single_wartend():
    q = PrioritaetsWarteschlange("Q1", [_aufgabe("A1", AufgabenPrioritaet.MITTEL)])
    result = q.naechste_aufgabe()
    assert result is not None
    assert result.aufgabe_id == "A1"

def test_naechste_aufgabe_kritisch_before_hoch():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A-HOCH", AufgabenPrioritaet.HOCH, NOW),
        _aufgabe("A-KRIT", AufgabenPrioritaet.KRITISCH, NOW),
    ])
    assert q.naechste_aufgabe().aufgabe_id == "A-KRIT"

def test_naechste_aufgabe_hoch_before_mittel():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A-MITTEL", AufgabenPrioritaet.MITTEL, NOW),
        _aufgabe("A-HOCH", AufgabenPrioritaet.HOCH, NOW),
    ])
    assert q.naechste_aufgabe().aufgabe_id == "A-HOCH"

def test_naechste_aufgabe_mittel_before_niedrig():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A-NIEDRIG", AufgabenPrioritaet.NIEDRIG, NOW),
        _aufgabe("A-MITTEL", AufgabenPrioritaet.MITTEL, NOW),
    ])
    assert q.naechste_aufgabe().aufgabe_id == "A-MITTEL"

def test_naechste_aufgabe_niedrig_before_hintergrund():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A-HG", AufgabenPrioritaet.HINTERGRUND, NOW),
        _aufgabe("A-NIED", AufgabenPrioritaet.NIEDRIG, NOW),
    ])
    assert q.naechste_aufgabe().aufgabe_id == "A-NIED"

def test_naechste_aufgabe_same_priority_earliest_first():
    early = _aufgabe("A-EARLY", AufgabenPrioritaet.MITTEL, NOW)
    late = _aufgabe("A-LATE", AufgabenPrioritaet.MITTEL, NOW + timedelta(hours=1))
    q = PrioritaetsWarteschlange("Q1", [late, early])
    assert q.naechste_aufgabe().aufgabe_id == "A-EARLY"

def test_naechste_aufgabe_ignores_non_wartend():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A-DONE", AufgabenPrioritaet.KRITISCH, status=WarteschlangenStatus.ABGESCHLOSSEN),
        _aufgabe("A-WAIT", AufgabenPrioritaet.NIEDRIG),
    ])
    assert q.naechste_aufgabe().aufgabe_id == "A-WAIT"

def test_naechste_aufgabe_mixed_statuses():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A1", AufgabenPrioritaet.KRITISCH, status=WarteschlangenStatus.VERARBEITUNG),
        _aufgabe("A2", AufgabenPrioritaet.HOCH, status=WarteschlangenStatus.WARTEND),
        _aufgabe("A3", AufgabenPrioritaet.MITTEL, status=WarteschlangenStatus.ABGESCHLOSSEN),
    ])
    assert q.naechste_aufgabe().aufgabe_id == "A2"


# ---------------------------------------------------------------------------
# PrioritaetsWarteschlange.aufgaben_nach_prioritaet()
# ---------------------------------------------------------------------------

def test_aufgaben_nach_prioritaet_empty():
    q = PrioritaetsWarteschlange("Q1")
    assert q.aufgaben_nach_prioritaet() == []

def test_aufgaben_nach_prioritaet_only_wartend():
    done = _aufgabe("A-DONE", AufgabenPrioritaet.KRITISCH, status=WarteschlangenStatus.ABGESCHLOSSEN)
    wait = _aufgabe("A-WAIT", AufgabenPrioritaet.NIEDRIG)
    q = PrioritaetsWarteschlange("Q1", [done, wait])
    result = q.aufgaben_nach_prioritaet()
    assert len(result) == 1
    assert result[0].aufgabe_id == "A-WAIT"

def test_aufgaben_nach_prioritaet_sorted_order():
    a1 = _aufgabe("A-NIED", AufgabenPrioritaet.NIEDRIG, NOW)
    a2 = _aufgabe("A-KRIT", AufgabenPrioritaet.KRITISCH, NOW)
    a3 = _aufgabe("A-MITTEL", AufgabenPrioritaet.MITTEL, NOW)
    q = PrioritaetsWarteschlange("Q1", [a1, a2, a3])
    result = q.aufgaben_nach_prioritaet()
    assert result[0].prioritaet == AufgabenPrioritaet.KRITISCH
    assert result[1].prioritaet == AufgabenPrioritaet.MITTEL
    assert result[2].prioritaet == AufgabenPrioritaet.NIEDRIG

def test_aufgaben_nach_prioritaet_same_prio_time_order():
    early = _aufgabe("A-EARLY", AufgabenPrioritaet.HOCH, NOW)
    late = _aufgabe("A-LATE", AufgabenPrioritaet.HOCH, NOW + timedelta(hours=2))
    q = PrioritaetsWarteschlange("Q1", [late, early])
    result = q.aufgaben_nach_prioritaet()
    assert result[0].aufgabe_id == "A-EARLY"
    assert result[1].aufgabe_id == "A-LATE"

def test_aufgaben_nach_prioritaet_full_ordering():
    prios = [
        AufgabenPrioritaet.HINTERGRUND,
        AufgabenPrioritaet.NIEDRIG,
        AufgabenPrioritaet.MITTEL,
        AufgabenPrioritaet.HOCH,
        AufgabenPrioritaet.KRITISCH,
    ]
    aufgaben = [_aufgabe(f"A-{p.value}", p, NOW) for p in prios]
    q = PrioritaetsWarteschlange("Q1", aufgaben)
    result = q.aufgaben_nach_prioritaet()
    expected_order = [
        AufgabenPrioritaet.KRITISCH,
        AufgabenPrioritaet.HOCH,
        AufgabenPrioritaet.MITTEL,
        AufgabenPrioritaet.NIEDRIG,
        AufgabenPrioritaet.HINTERGRUND,
    ]
    assert [r.prioritaet for r in result] == expected_order

def test_aufgaben_nach_prioritaet_excludes_verarbeitung():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A1", AufgabenPrioritaet.HOCH, status=WarteschlangenStatus.VERARBEITUNG),
        _aufgabe("A2", AufgabenPrioritaet.MITTEL),
    ])
    result = q.aufgaben_nach_prioritaet()
    assert len(result) == 1
    assert result[0].aufgabe_id == "A2"

def test_aufgaben_nach_prioritaet_excludes_abgebrochen():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A1", AufgabenPrioritaet.KRITISCH, status=WarteschlangenStatus.ABGEBROCHEN),
        _aufgabe("A2", AufgabenPrioritaet.NIEDRIG),
    ])
    result = q.aufgaben_nach_prioritaet()
    assert len(result) == 1


# ---------------------------------------------------------------------------
# PrioritaetsWarteschlange.warteschlangen_tiefe()
# ---------------------------------------------------------------------------

def test_warteschlangen_tiefe_empty():
    q = PrioritaetsWarteschlange("Q1")
    tiefe = q.warteschlangen_tiefe()
    assert len(tiefe) == 5
    for p in AufgabenPrioritaet:
        assert tiefe[p] == 0

def test_warteschlangen_tiefe_all_five_keys():
    q = PrioritaetsWarteschlange("Q1")
    tiefe = q.warteschlangen_tiefe()
    for p in AufgabenPrioritaet:
        assert p in tiefe

def test_warteschlangen_tiefe_counts_only_wartend():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A1", AufgabenPrioritaet.KRITISCH),
        _aufgabe("A2", AufgabenPrioritaet.KRITISCH, status=WarteschlangenStatus.ABGESCHLOSSEN),
    ])
    tiefe = q.warteschlangen_tiefe()
    assert tiefe[AufgabenPrioritaet.KRITISCH] == 1

def test_warteschlangen_tiefe_abgeschlossen_not_counted():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A1", AufgabenPrioritaet.HOCH, status=WarteschlangenStatus.ABGESCHLOSSEN),
        _aufgabe("A2", AufgabenPrioritaet.HOCH, status=WarteschlangenStatus.ABGESCHLOSSEN),
    ])
    tiefe = q.warteschlangen_tiefe()
    assert tiefe[AufgabenPrioritaet.HOCH] == 0

def test_warteschlangen_tiefe_verarbeitung_not_counted():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A1", AufgabenPrioritaet.MITTEL, status=WarteschlangenStatus.VERARBEITUNG),
    ])
    tiefe = q.warteschlangen_tiefe()
    assert tiefe[AufgabenPrioritaet.MITTEL] == 0

def test_warteschlangen_tiefe_multiple_priorities():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A1", AufgabenPrioritaet.KRITISCH),
        _aufgabe("A2", AufgabenPrioritaet.KRITISCH),
        _aufgabe("A3", AufgabenPrioritaet.MITTEL),
    ])
    tiefe = q.warteschlangen_tiefe()
    assert tiefe[AufgabenPrioritaet.KRITISCH] == 2
    assert tiefe[AufgabenPrioritaet.MITTEL] == 1
    assert tiefe[AufgabenPrioritaet.NIEDRIG] == 0

def test_warteschlangen_tiefe_sum_equals_wartend_count():
    q = PrioritaetsWarteschlange("Q1", [
        _aufgabe("A1", AufgabenPrioritaet.KRITISCH),
        _aufgabe("A2", AufgabenPrioritaet.HOCH),
        _aufgabe("A3", AufgabenPrioritaet.HOCH, status=WarteschlangenStatus.ABGESCHLOSSEN),
    ])
    tiefe = q.warteschlangen_tiefe()
    total = sum(tiefe.values())
    assert total == 2


# ---------------------------------------------------------------------------
# get_default_warteschlangen()
# ---------------------------------------------------------------------------

def test_default_warteschlangen_returns_two():
    result = get_default_warteschlangen()
    assert len(result) == 2

def test_default_warteschlangen_ids():
    result = get_default_warteschlangen()
    ids = [q.schlange_id for q in result]
    assert "WS-001" in ids
    assert "WS-002" in ids

def test_default_ws001_has_five_tasks():
    schlangen = {q.schlange_id: q for q in get_default_warteschlangen()}
    assert len(schlangen["WS-001"].aufgaben) == 5

def test_default_ws002_is_empty():
    schlangen = {q.schlange_id: q for q in get_default_warteschlangen()}
    assert len(schlangen["WS-002"].aufgaben) == 0

def test_default_ws001_naechste_aufgabe_is_kritisch():
    schlangen = {q.schlange_id: q for q in get_default_warteschlangen()}
    naechste = schlangen["WS-001"].naechste_aufgabe()
    assert naechste is not None
    assert naechste.aufgabe_id == "AUF-001"

def test_default_ws001_naechste_prioritaet_kritisch():
    schlangen = {q.schlange_id: q for q in get_default_warteschlangen()}
    naechste = schlangen["WS-001"].naechste_aufgabe()
    assert naechste.prioritaet == AufgabenPrioritaet.KRITISCH

def test_default_ws002_naechste_aufgabe_none():
    schlangen = {q.schlange_id: q for q in get_default_warteschlangen()}
    assert schlangen["WS-002"].naechste_aufgabe() is None

def test_default_ws001_four_wartend_tasks():
    schlangen = {q.schlange_id: q for q in get_default_warteschlangen()}
    q = schlangen["WS-001"]
    wartend = [a for a in q.aufgaben if a.status == WarteschlangenStatus.WARTEND]
    assert len(wartend) == 4

def test_default_ws001_auf004_is_abgeschlossen():
    schlangen = {q.schlange_id: q for q in get_default_warteschlangen()}
    aufgaben = {a.aufgabe_id: a for a in schlangen["WS-001"].aufgaben}
    assert aufgaben["AUF-004"].status == WarteschlangenStatus.ABGESCHLOSSEN

def test_default_ws001_auf001_tenant_a():
    schlangen = {q.schlange_id: q for q in get_default_warteschlangen()}
    aufgaben = {a.aufgabe_id: a for a in schlangen["WS-001"].aufgaben}
    assert aufgaben["AUF-001"].tenant_id == "TENANT-A"

def test_default_ws001_auf003_tenant_b():
    schlangen = {q.schlange_id: q for q in get_default_warteschlangen()}
    aufgaben = {a.aufgabe_id: a for a in schlangen["WS-001"].aufgaben}
    assert aufgaben["AUF-003"].tenant_id == "TENANT-B"

def test_default_ws001_sorted_first_is_kritisch():
    schlangen = {q.schlange_id: q for q in get_default_warteschlangen()}
    sortiert = schlangen["WS-001"].aufgaben_nach_prioritaet()
    assert sortiert[0].prioritaet == AufgabenPrioritaet.KRITISCH

def test_default_ws001_tiefe_has_kritisch_one():
    schlangen = {q.schlange_id: q for q in get_default_warteschlangen()}
    tiefe = schlangen["WS-001"].warteschlangen_tiefe()
    assert tiefe[AufgabenPrioritaet.KRITISCH] == 1

def test_default_ws001_tiefe_hintergrund_zero():
    # AUF-004 HINTERGRUND is ABGESCHLOSSEN, not counted
    schlangen = {q.schlange_id: q for q in get_default_warteschlangen()}
    tiefe = schlangen["WS-001"].warteschlangen_tiefe()
    assert tiefe[AufgabenPrioritaet.HINTERGRUND] == 0


# ---------------------------------------------------------------------------
# RollbackSchritt.kann_ausgefuehrt_werden()
# ---------------------------------------------------------------------------

def _schritt(schritt_id, umkehrbarkeit, status=RollbackStatus.AUSSTEHEND):
    return RollbackSchritt(
        schritt_id=schritt_id,
        workflow_schritt_id="WS-X",
        rollback_typ=RollbackTyp.SCHRITT,
        umkehrbarkeit=umkehrbarkeit,
        status=status,
    )

def test_kann_ausgefuehrt_vollstaendig_ausstehend():
    s = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG)
    assert s.kann_ausgefuehrt_werden() is True

def test_kann_ausgefuehrt_teilweise_ausstehend():
    s = _schritt("S1", UmkehrbarkeitsGrad.TEILWEISE)
    assert s.kann_ausgefuehrt_werden() is True

def test_kann_ausgefuehrt_nicht_umkehrbar_ausstehend():
    s = _schritt("S1", UmkehrbarkeitsGrad.NICHT_UMKEHRBAR)
    assert s.kann_ausgefuehrt_werden() is False

def test_kann_ausgefuehrt_vollstaendig_abgeschlossen():
    s = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.ABGESCHLOSSEN)
    assert s.kann_ausgefuehrt_werden() is False

def test_kann_ausgefuehrt_vollstaendig_laufend():
    s = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.LAUFEND)
    assert s.kann_ausgefuehrt_werden() is False

def test_kann_ausgefuehrt_vollstaendig_fehlgeschlagen():
    s = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.FEHLGESCHLAGEN)
    assert s.kann_ausgefuehrt_werden() is False

def test_kann_ausgefuehrt_vollstaendig_nicht_moeglich():
    s = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.NICHT_MOEGLICH)
    assert s.kann_ausgefuehrt_werden() is False

def test_kann_ausgefuehrt_nicht_umkehrbar_abgeschlossen():
    s = _schritt("S1", UmkehrbarkeitsGrad.NICHT_UMKEHRBAR, RollbackStatus.ABGESCHLOSSEN)
    assert s.kann_ausgefuehrt_werden() is False

def test_kann_ausgefuehrt_teilweise_laufend():
    s = _schritt("S1", UmkehrbarkeitsGrad.TEILWEISE, RollbackStatus.LAUFEND)
    assert s.kann_ausgefuehrt_werden() is False

def test_kann_ausgefuehrt_nicht_umkehrbar_nicht_moeglich():
    s = _schritt("S1", UmkehrbarkeitsGrad.NICHT_UMKEHRBAR, RollbackStatus.NICHT_MOEGLICH)
    assert s.kann_ausgefuehrt_werden() is False


# ---------------------------------------------------------------------------
# RollbackPlan.ausfuehrbare_schritte()
# ---------------------------------------------------------------------------

def _plan(plan_id, schritte):
    p = RollbackPlan(plan_id, "WI-X", RollbackTyp.VOLLSTAENDIG, erstellt_am=NOW)
    p.schritte = schritte
    return p

def test_ausfuehrbare_schritte_empty_plan():
    p = _plan("P1", [])
    assert p.ausfuehrbare_schritte() == []

def test_ausfuehrbare_schritte_all_ausfuehrbar():
    s1 = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG)
    s2 = _schritt("S2", UmkehrbarkeitsGrad.TEILWEISE)
    p = _plan("P1", [s1, s2])
    assert len(p.ausfuehrbare_schritte()) == 2

def test_ausfuehrbare_schritte_filters_nicht_umkehrbar():
    s1 = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG)
    s2 = _schritt("S2", UmkehrbarkeitsGrad.NICHT_UMKEHRBAR)
    p = _plan("P1", [s1, s2])
    result = p.ausfuehrbare_schritte()
    assert len(result) == 1
    assert result[0].schritt_id == "S1"

def test_ausfuehrbare_schritte_filters_abgeschlossen():
    s1 = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.ABGESCHLOSSEN)
    s2 = _schritt("S2", UmkehrbarkeitsGrad.VOLLSTAENDIG)
    p = _plan("P1", [s1, s2])
    result = p.ausfuehrbare_schritte()
    assert len(result) == 1
    assert result[0].schritt_id == "S2"

def test_ausfuehrbare_schritte_none_ausfuehrbar():
    s1 = _schritt("S1", UmkehrbarkeitsGrad.NICHT_UMKEHRBAR)
    s2 = _schritt("S2", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.ABGESCHLOSSEN)
    p = _plan("P1", [s1, s2])
    assert p.ausfuehrbare_schritte() == []


# ---------------------------------------------------------------------------
# RollbackPlan.ist_vollstaendig_ausfuehrbar()
# ---------------------------------------------------------------------------

def test_ist_vollstaendig_ausfuehrbar_empty():
    p = _plan("P1", [])
    assert p.ist_vollstaendig_ausfuehrbar() is True

def test_ist_vollstaendig_ausfuehrbar_all_vollstaendig():
    s1 = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG)
    s2 = _schritt("S2", UmkehrbarkeitsGrad.VOLLSTAENDIG)
    p = _plan("P1", [s1, s2])
    assert p.ist_vollstaendig_ausfuehrbar() is True

def test_ist_vollstaendig_ausfuehrbar_all_teilweise():
    s1 = _schritt("S1", UmkehrbarkeitsGrad.TEILWEISE)
    p = _plan("P1", [s1])
    assert p.ist_vollstaendig_ausfuehrbar() is True

def test_ist_vollstaendig_ausfuehrbar_one_nicht_umkehrbar():
    s1 = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG)
    s2 = _schritt("S2", UmkehrbarkeitsGrad.NICHT_UMKEHRBAR)
    p = _plan("P1", [s1, s2])
    assert p.ist_vollstaendig_ausfuehrbar() is False

def test_ist_vollstaendig_ausfuehrbar_all_nicht_umkehrbar():
    s1 = _schritt("S1", UmkehrbarkeitsGrad.NICHT_UMKEHRBAR)
    s2 = _schritt("S2", UmkehrbarkeitsGrad.NICHT_UMKEHRBAR)
    p = _plan("P1", [s1, s2])
    assert p.ist_vollstaendig_ausfuehrbar() is False

def test_ist_vollstaendig_ausfuehrbar_mixed_vollstaendig_teilweise():
    s1 = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG)
    s2 = _schritt("S2", UmkehrbarkeitsGrad.TEILWEISE)
    p = _plan("P1", [s1, s2])
    assert p.ist_vollstaendig_ausfuehrbar() is True


# ---------------------------------------------------------------------------
# RollbackPlan.rollback_fortschritt_pct()
# ---------------------------------------------------------------------------

def test_rollback_fortschritt_empty():
    p = _plan("P1", [])
    assert p.rollback_fortschritt_pct() == 0.0

def test_rollback_fortschritt_none_done():
    s1 = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.AUSSTEHEND)
    s2 = _schritt("S2", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.AUSSTEHEND)
    s3 = _schritt("S3", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.AUSSTEHEND)
    p = _plan("P1", [s1, s2, s3])
    assert p.rollback_fortschritt_pct() == 0.0

def test_rollback_fortschritt_two_of_three():
    s1 = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.ABGESCHLOSSEN)
    s2 = _schritt("S2", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.ABGESCHLOSSEN)
    s3 = _schritt("S3", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.AUSSTEHEND)
    p = _plan("P1", [s1, s2, s3])
    assert abs(p.rollback_fortschritt_pct() - 66.6667) < 0.001

def test_rollback_fortschritt_all_done():
    s1 = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.ABGESCHLOSSEN)
    s2 = _schritt("S2", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.ABGESCHLOSSEN)
    s3 = _schritt("S3", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.ABGESCHLOSSEN)
    p = _plan("P1", [s1, s2, s3])
    assert p.rollback_fortschritt_pct() == 100.0

def test_rollback_fortschritt_one_of_one():
    s1 = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.ABGESCHLOSSEN)
    p = _plan("P1", [s1])
    assert p.rollback_fortschritt_pct() == 100.0

def test_rollback_fortschritt_zero_of_one():
    s1 = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.AUSSTEHEND)
    p = _plan("P1", [s1])
    assert p.rollback_fortschritt_pct() == 0.0

def test_rollback_fortschritt_counts_only_abgeschlossen():
    # LAUFEND and FEHLGESCHLAGEN don't count
    s1 = _schritt("S1", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.LAUFEND)
    s2 = _schritt("S2", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.FEHLGESCHLAGEN)
    s3 = _schritt("S3", UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.ABGESCHLOSSEN)
    p = _plan("P1", [s1, s2, s3])
    assert abs(p.rollback_fortschritt_pct() - 33.3333) < 0.001


# ---------------------------------------------------------------------------
# get_default_rollback_plaene()
# ---------------------------------------------------------------------------

def test_default_rollback_plaene_returns_three():
    result = get_default_rollback_plaene()
    assert len(result) == 3

def test_default_rollback_plaene_ids():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert "RP-001" in plaene
    assert "RP-002" in plaene
    assert "RP-003" in plaene

def test_rp001_workflow_instanz():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert plaene["RP-001"].workflow_instanz_id == "WI-K-001"

def test_rp001_typ_vollstaendig():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert plaene["RP-001"].rollback_typ == RollbackTyp.VOLLSTAENDIG

def test_rp001_has_three_schritte():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert len(plaene["RP-001"].schritte) == 3

def test_rp001_two_abgeschlossen():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    p = plaene["RP-001"]
    done = [s for s in p.schritte if s.status == RollbackStatus.ABGESCHLOSSEN]
    assert len(done) == 2

def test_rp001_one_ausstehend():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    p = plaene["RP-001"]
    ausstehend = [s for s in p.schritte if s.status == RollbackStatus.AUSSTEHEND]
    assert len(ausstehend) == 1

def test_rp001_fortschritt_pct():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    pct = plaene["RP-001"].rollback_fortschritt_pct()
    assert abs(pct - 66.6667) < 0.001

def test_rp001_ist_vollstaendig_ausfuehrbar():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert plaene["RP-001"].ist_vollstaendig_ausfuehrbar() is True

def test_rp001_ausfuehrbare_schritte_count():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    # RS-003 is AUSSTEHEND + VOLLSTAENDIG
    assert len(plaene["RP-001"].ausfuehrbare_schritte()) == 1

def test_rp001_erstellt_von_system():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert plaene["RP-001"].erstellt_von == "system"

def test_rp002_typ_teilweise():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert plaene["RP-002"].rollback_typ == RollbackTyp.TEILWEISE

def test_rp002_has_two_schritte():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert len(plaene["RP-002"].schritte) == 2

def test_rp002_has_nicht_umkehrbar():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    p = plaene["RP-002"]
    nicht_umk = [s for s in p.schritte if s.umkehrbarkeit == UmkehrbarkeitsGrad.NICHT_UMKEHRBAR]
    assert len(nicht_umk) == 1

def test_rp002_ist_nicht_vollstaendig_ausfuehrbar():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert plaene["RP-002"].ist_vollstaendig_ausfuehrbar() is False

def test_rp002_ausfuehrbare_schritte_one():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    # RS-004 VOLLSTAENDIG + AUSSTEHEND is executable
    assert len(plaene["RP-002"].ausfuehrbare_schritte()) == 1

def test_rp002_rs005_nicht_moeglich_status():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    schritte = {s.schritt_id: s for s in plaene["RP-002"].schritte}
    assert schritte["RS-005"].status == RollbackStatus.NICHT_MOEGLICH

def test_rp002_erstellt_von_user():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert plaene["RP-002"].erstellt_von == "user-001"

def test_rp003_empty_schritte():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert len(plaene["RP-003"].schritte) == 0

def test_rp003_fortschritt_pct_zero():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert plaene["RP-003"].rollback_fortschritt_pct() == 0.0

def test_rp003_ausfuehrbare_schritte_zero():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert len(plaene["RP-003"].ausfuehrbare_schritte()) == 0

def test_rp003_ist_vollstaendig_ausfuehrbar_true():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert plaene["RP-003"].ist_vollstaendig_ausfuehrbar() is True

def test_rp003_typ_schritt():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert plaene["RP-003"].rollback_typ == RollbackTyp.SCHRITT

def test_rp003_workflow_instanz():
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    assert plaene["RP-003"].workflow_instanz_id == "WI-LEER-003"


# ---------------------------------------------------------------------------
# FastAPI endpoint integration tests
# ---------------------------------------------------------------------------

from fastapi.testclient import TestClient
from app.api.v1.endpoints.process_kernel_api import router
from fastapi import FastAPI

_app = FastAPI()
_app.include_router(router)
_client = TestClient(_app)

# router has prefix="/process", so endpoints are at /process/prioritaet/... etc.

def test_endpoint_warteschlangen_status_200():
    r = _client.get("/process/prioritaet/warteschlangen")
    assert r.status_code == 200

def test_endpoint_warteschlangen_returns_two():
    r = _client.get("/process/prioritaet/warteschlangen")
    data = r.json()
    assert len(data) == 2

def test_endpoint_warteschlangen_ws001_present():
    r = _client.get("/process/prioritaet/warteschlangen")
    ids = [q["schlange_id"] for q in r.json()]
    assert "WS-001" in ids

def test_endpoint_warteschlangen_ws001_naechste():
    r = _client.get("/process/prioritaet/warteschlangen")
    ws001 = next(q for q in r.json() if q["schlange_id"] == "WS-001")
    assert ws001["naechste_aufgabe_id"] == "AUF-001"

def test_endpoint_warteschlangen_ws002_naechste_none():
    r = _client.get("/process/prioritaet/warteschlangen")
    ws002 = next(q for q in r.json() if q["schlange_id"] == "WS-002")
    assert ws002["naechste_aufgabe_id"] is None

def test_endpoint_warteschlangen_tiefe_keys():
    r = _client.get("/process/prioritaet/warteschlangen")
    ws001 = next(q for q in r.json() if q["schlange_id"] == "WS-001")
    tiefe = ws001["tiefe"]
    assert "KRITISCH" in tiefe
    assert "HOCH" in tiefe
    assert "MITTEL" in tiefe
    assert "NIEDRIG" in tiefe
    assert "HINTERGRUND" in tiefe

def test_endpoint_sortiere_empty_payload():
    r = _client.post("/process/prioritaet/sortiere", json={"aufgaben": []})
    assert r.status_code == 200
    assert r.json() == []

def test_endpoint_sortiere_single_aufgabe():
    r = _client.post("/process/prioritaet/sortiere", json={"aufgaben": [
        {"aufgabe_id": "X1", "prioritaet": "HOCH", "erstellt_am": "2026-01-01T00:00:00"}
    ]})
    assert r.status_code == 200
    assert len(r.json()) == 1

def test_endpoint_sortiere_order():
    r = _client.post("/process/prioritaet/sortiere", json={"aufgaben": [
        {"aufgabe_id": "A-NIEDRIG", "prioritaet": "NIEDRIG", "erstellt_am": "2026-01-01T00:00:00"},
        {"aufgabe_id": "A-KRITISCH", "prioritaet": "KRITISCH", "erstellt_am": "2026-01-01T00:00:00"},
    ]})
    result = r.json()
    assert result[0]["aufgabe_id"] == "A-KRITISCH"
    assert result[1]["aufgabe_id"] == "A-NIEDRIG"

def test_endpoint_rollback_plaene_status_200():
    r = _client.get("/process/rollback/plaene")
    assert r.status_code == 200

def test_endpoint_rollback_plaene_returns_three():
    r = _client.get("/process/rollback/plaene")
    assert len(r.json()) == 3

def test_endpoint_rollback_plaene_rp001_fields():
    r = _client.get("/process/rollback/plaene")
    rp001 = next(p for p in r.json() if p["plan_id"] == "RP-001")
    assert rp001["schritte_gesamt"] == 3
    assert rp001["ist_vollstaendig_ausfuehrbar"] is True
    assert abs(rp001["fortschritt_pct"] - 66.6667) < 0.001

def test_endpoint_rollback_plaene_rp002_nicht_vollstaendig():
    r = _client.get("/process/rollback/plaene")
    rp002 = next(p for p in r.json() if p["plan_id"] == "RP-002")
    assert rp002["ist_vollstaendig_ausfuehrbar"] is False

def test_endpoint_rollback_plaene_rp003_empty():
    r = _client.get("/process/rollback/plaene")
    rp003 = next(p for p in r.json() if p["plan_id"] == "RP-003")
    assert rp003["schritte_gesamt"] == 0
    assert rp003["fortschritt_pct"] == 0.0

def test_endpoint_pruefe_ausfuehrbarkeit_rp001():
    r = _client.post("/process/rollback/pruefe-ausfuehrbarkeit", json={"plan_id": "RP-001"})
    assert r.status_code == 200
    data = r.json()
    assert data["plan_id"] == "RP-001"
    assert data["ist_vollstaendig_ausfuehrbar"] is True

def test_endpoint_pruefe_ausfuehrbarkeit_rp002():
    r = _client.post("/process/rollback/pruefe-ausfuehrbarkeit", json={"plan_id": "RP-002"})
    data = r.json()
    assert data["ist_vollstaendig_ausfuehrbar"] is False
    assert data["ausfuehrbare_schritte"] == 1

def test_endpoint_pruefe_ausfuehrbarkeit_unknown_plan():
    r = _client.post("/process/rollback/pruefe-ausfuehrbarkeit", json={"plan_id": "RP-UNBEKANNT"})
    assert r.status_code == 200
    data = r.json()
    assert "fehler" in data

def test_endpoint_pruefe_ausfuehrbarkeit_rp003():
    r = _client.post("/process/rollback/pruefe-ausfuehrbarkeit", json={"plan_id": "RP-003"})
    data = r.json()
    assert data["ausfuehrbare_schritte"] == 0
    assert data["fortschritt_pct"] == 0.0
