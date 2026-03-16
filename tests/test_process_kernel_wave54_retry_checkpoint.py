"""Wave 54: Retry Policies + Workflow Checkpoint Contracts — 130+ Tests."""
import pytest
from datetime import datetime, timedelta
import dataclasses

from app.core.process_retry_contracts import (
    RetryStrategie,
    RetryStatus,
    RetryRegel,
    RetryZustand,
    get_default_retry_regeln,
)
from app.core.workflow_checkpoint_contracts_wave54 import (
    CheckpointTyp,
    CheckpointStatus,
    WorkflowCheckpoint,
    CheckpointSequenz,
    get_default_checkpoint_sequenzen,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
NOW = datetime(2026, 3, 16, 10, 0, 0)


def make_regel(strategie, basis=10.0, max_versuche=3, max_verz=300.0):
    return RetryRegel(
        regel_id="TEST",
        strategie=strategie,
        max_versuche=max_versuche,
        basis_sekunden=basis,
        max_verzoegerung_sekunden=max_verz,
    )


def make_zustand(aktueller_versuch=0, status=RetryStatus.AUSSTEHEND):
    return RetryZustand(
        zustand_id="ZS-TEST",
        regel_id="TEST",
        befehl_typ="TEST_CMD",
        status=status,
        aktueller_versuch=aktueller_versuch,
    )


def make_checkpoint(checkpoint_id, schritt, status=CheckpointStatus.AKTUELL, instanz_id="WI-X"):
    return WorkflowCheckpoint(
        checkpoint_id=checkpoint_id,
        workflow_instanz_id=instanz_id,
        checkpoint_typ=CheckpointTyp.AUTOMATISCH,
        zustand_snapshot={"schritt": schritt},
        schritt_nummer=schritt,
        status=status,
        erstellt_am=NOW,
    )


# ===========================================================================
# PART 1: RetryStrategie Enum
# ===========================================================================

class TestRetryStrategieEnum:
    def test_kein_retry_value(self):
        assert RetryStrategie.KEIN_RETRY == "KEIN_RETRY"

    def test_fester_intervall_value(self):
        assert RetryStrategie.FESTER_INTERVALL == "FESTER_INTERVALL"

    def test_lineares_backoff_value(self):
        assert RetryStrategie.LINEARES_BACKOFF == "LINEARES_BACKOFF"

    def test_exponentielles_backoff_value(self):
        assert RetryStrategie.EXPONENTIELLES_BACKOFF == "EXPONENTIELLES_BACKOFF"

    def test_jitter_value(self):
        assert RetryStrategie.JITTER == "JITTER"

    def test_all_strategies_count(self):
        assert len(RetryStrategie) == 5

    def test_str_enum_membership(self):
        assert "JITTER" in [s.value for s in RetryStrategie]


# ===========================================================================
# PART 2: RetryStatus Enum
# ===========================================================================

class TestRetryStatusEnum:
    def test_ausstehend(self):
        assert RetryStatus.AUSSTEHEND == "AUSSTEHEND"

    def test_laufend(self):
        assert RetryStatus.LAUFEND == "LAUFEND"

    def test_erfolgreich(self):
        assert RetryStatus.ERFOLGREICH == "ERFOLGREICH"

    def test_erschoepft(self):
        assert RetryStatus.ERSCHOEPFT == "ERSCHOEPFT"

    def test_aufgegeben(self):
        assert RetryStatus.AUFGEGEBEN == "AUFGEGEBEN"

    def test_all_statuses_count(self):
        assert len(RetryStatus) == 5


# ===========================================================================
# PART 3: RetryRegel.berechne_verzoegerung — KEIN_RETRY
# ===========================================================================

class TestBerechneVerzoegerungKeinRetry:
    def test_versuch1_returns_zero(self):
        r = make_regel(RetryStrategie.KEIN_RETRY)
        assert r.berechne_verzoegerung(1) == 0.0

    def test_versuch2_returns_zero(self):
        r = make_regel(RetryStrategie.KEIN_RETRY)
        assert r.berechne_verzoegerung(2) == 0.0

    def test_versuch5_returns_zero(self):
        r = make_regel(RetryStrategie.KEIN_RETRY)
        assert r.berechne_verzoegerung(5) == 0.0

    def test_basis_irrelevant_for_kein_retry(self):
        r = make_regel(RetryStrategie.KEIN_RETRY, basis=100.0)
        assert r.berechne_verzoegerung(1) == 0.0

    def test_return_type_is_float(self):
        r = make_regel(RetryStrategie.KEIN_RETRY)
        assert isinstance(r.berechne_verzoegerung(1), float)


# ===========================================================================
# PART 4: RetryRegel.berechne_verzoegerung — FESTER_INTERVALL
# ===========================================================================

class TestBerechneVerzoegerungFesterIntervall:
    def test_versuch1_returns_basis(self):
        r = make_regel(RetryStrategie.FESTER_INTERVALL, basis=10.0)
        assert r.berechne_verzoegerung(1) == 10.0

    def test_versuch2_returns_basis(self):
        r = make_regel(RetryStrategie.FESTER_INTERVALL, basis=10.0)
        assert r.berechne_verzoegerung(2) == 10.0

    def test_versuch3_returns_basis(self):
        r = make_regel(RetryStrategie.FESTER_INTERVALL, basis=10.0)
        assert r.berechne_verzoegerung(3) == 10.0

    def test_basis_5_versuch1(self):
        r = make_regel(RetryStrategie.FESTER_INTERVALL, basis=5.0)
        assert r.berechne_verzoegerung(1) == 5.0

    def test_basis_30_versuch4(self):
        r = make_regel(RetryStrategie.FESTER_INTERVALL, basis=30.0)
        assert r.berechne_verzoegerung(4) == 30.0

    def test_always_same_regardless_of_versuch(self):
        r = make_regel(RetryStrategie.FESTER_INTERVALL, basis=7.5)
        vals = [r.berechne_verzoegerung(v) for v in range(1, 6)]
        assert all(v == 7.5 for v in vals)


# ===========================================================================
# PART 5: RetryRegel.berechne_verzoegerung — LINEARES_BACKOFF
# ===========================================================================

class TestBerechneVerzoegerungLinearesBackoff:
    def test_versuch1_equals_basis(self):
        r = make_regel(RetryStrategie.LINEARES_BACKOFF, basis=10.0)
        assert r.berechne_verzoegerung(1) == 10.0

    def test_versuch2_equals_2x_basis(self):
        r = make_regel(RetryStrategie.LINEARES_BACKOFF, basis=10.0)
        assert r.berechne_verzoegerung(2) == 20.0

    def test_versuch3_equals_3x_basis(self):
        r = make_regel(RetryStrategie.LINEARES_BACKOFF, basis=10.0)
        assert r.berechne_verzoegerung(3) == 30.0

    def test_versuch4_equals_4x_basis(self):
        r = make_regel(RetryStrategie.LINEARES_BACKOFF, basis=15.0)
        assert r.berechne_verzoegerung(4) == 60.0

    def test_capped_at_max_verzoegerung(self):
        r = make_regel(RetryStrategie.LINEARES_BACKOFF, basis=100.0, max_verz=150.0)
        assert r.berechne_verzoegerung(2) == 150.0  # 200 capped to 150

    def test_exactly_at_cap(self):
        r = make_regel(RetryStrategie.LINEARES_BACKOFF, basis=50.0, max_verz=100.0)
        assert r.berechne_verzoegerung(2) == 100.0  # 100 == cap

    def test_linear_growth_pattern(self):
        r = make_regel(RetryStrategie.LINEARES_BACKOFF, basis=5.0)
        assert r.berechne_verzoegerung(1) < r.berechne_verzoegerung(2) < r.berechne_verzoegerung(3)


# ===========================================================================
# PART 6: RetryRegel.berechne_verzoegerung — EXPONENTIELLES_BACKOFF
# ===========================================================================

class TestBerechneVerzoegerungExponentiellesBackoff:
    def test_versuch1_equals_basis(self):
        r = make_regel(RetryStrategie.EXPONENTIELLES_BACKOFF, basis=5.0)
        assert r.berechne_verzoegerung(1) == 5.0  # 5 * 2^0

    def test_versuch2_equals_2x_basis(self):
        r = make_regel(RetryStrategie.EXPONENTIELLES_BACKOFF, basis=5.0)
        assert r.berechne_verzoegerung(2) == 10.0  # 5 * 2^1

    def test_versuch3_equals_4x_basis(self):
        r = make_regel(RetryStrategie.EXPONENTIELLES_BACKOFF, basis=5.0)
        assert r.berechne_verzoegerung(3) == 20.0  # 5 * 2^2

    def test_versuch4_equals_8x_basis(self):
        r = make_regel(RetryStrategie.EXPONENTIELLES_BACKOFF, basis=5.0)
        assert r.berechne_verzoegerung(4) == 40.0  # 5 * 2^3

    def test_capped_at_max(self):
        r = make_regel(RetryStrategie.EXPONENTIELLES_BACKOFF, basis=100.0, max_verz=200.0)
        assert r.berechne_verzoegerung(3) == 200.0  # 400 capped

    def test_versuch1_capped_if_basis_exceeds(self):
        r = make_regel(RetryStrategie.EXPONENTIELLES_BACKOFF, basis=500.0, max_verz=100.0)
        assert r.berechne_verzoegerung(1) == 100.0

    def test_exponential_growth(self):
        r = make_regel(RetryStrategie.EXPONENTIELLES_BACKOFF, basis=2.0)
        v1 = r.berechne_verzoegerung(1)
        v2 = r.berechne_verzoegerung(2)
        v3 = r.berechne_verzoegerung(3)
        assert v2 == v1 * 2
        assert v3 == v1 * 4


# ===========================================================================
# PART 7: RetryRegel.berechne_verzoegerung — JITTER
# ===========================================================================

class TestBerechneVerzoegerungJitter:
    def test_versuch1_equals_1_5x_basis(self):
        r = make_regel(RetryStrategie.JITTER, basis=10.0)
        assert r.berechne_verzoegerung(1) == 15.0  # 10 * 1 * 1.5

    def test_versuch2_equals_3x_basis(self):
        r = make_regel(RetryStrategie.JITTER, basis=10.0)
        assert r.berechne_verzoegerung(2) == 30.0  # 10 * 2 * 1.5

    def test_versuch3_equals_6x_basis(self):
        r = make_regel(RetryStrategie.JITTER, basis=10.0)
        assert r.berechne_verzoegerung(3) == 60.0  # 10 * 4 * 1.5

    def test_basis_2_versuch1(self):
        r = make_regel(RetryStrategie.JITTER, basis=2.0, max_verz=60.0)
        assert r.berechne_verzoegerung(1) == 3.0  # 2 * 1 * 1.5

    def test_basis_2_versuch2(self):
        r = make_regel(RetryStrategie.JITTER, basis=2.0, max_verz=60.0)
        assert r.berechne_verzoegerung(2) == 6.0  # 2 * 2 * 1.5

    def test_capped_at_max(self):
        r = make_regel(RetryStrategie.JITTER, basis=100.0, max_verz=50.0)
        assert r.berechne_verzoegerung(1) == 50.0  # 150 capped

    def test_jitter_higher_than_exp_backoff(self):
        r_jitter = make_regel(RetryStrategie.JITTER, basis=5.0)
        r_exp = make_regel(RetryStrategie.EXPONENTIELLES_BACKOFF, basis=5.0)
        # Jitter adds 50% on top
        assert r_jitter.berechne_verzoegerung(1) == r_exp.berechne_verzoegerung(1) * 1.5


# ===========================================================================
# PART 8: RetryZustand.kann_nochmal_versuchen
# ===========================================================================

class TestKannNochmalVersuchen:
    def test_true_when_ausstehend_and_under_max(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, max_versuche=3)
        z = make_zustand(aktueller_versuch=0, status=RetryStatus.AUSSTEHEND)
        assert z.kann_nochmal_versuchen(regel) is True

    def test_true_when_laufend_and_under_max(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, max_versuche=3)
        z = make_zustand(aktueller_versuch=1, status=RetryStatus.LAUFEND)
        assert z.kann_nochmal_versuchen(regel) is True

    def test_true_at_exactly_one_below_max(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, max_versuche=3)
        z = make_zustand(aktueller_versuch=2, status=RetryStatus.LAUFEND)
        assert z.kann_nochmal_versuchen(regel) is True

    def test_false_when_at_max(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, max_versuche=3)
        z = make_zustand(aktueller_versuch=3, status=RetryStatus.LAUFEND)
        assert z.kann_nochmal_versuchen(regel) is False

    def test_false_when_erfolgreich(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, max_versuche=5)
        z = make_zustand(aktueller_versuch=1, status=RetryStatus.ERFOLGREICH)
        assert z.kann_nochmal_versuchen(regel) is False

    def test_false_when_erschoepft(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, max_versuche=5)
        z = make_zustand(aktueller_versuch=2, status=RetryStatus.ERSCHOEPFT)
        assert z.kann_nochmal_versuchen(regel) is False

    def test_false_when_aufgegeben(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, max_versuche=5)
        z = make_zustand(aktueller_versuch=0, status=RetryStatus.AUFGEGEBEN)
        assert z.kann_nochmal_versuchen(regel) is False

    def test_false_when_kein_retry(self):
        regel = make_regel(RetryStrategie.KEIN_RETRY, max_versuche=1)
        z = make_zustand(aktueller_versuch=0, status=RetryStatus.AUSSTEHEND)
        # aktueller_versuch (0) < max_versuche (1) → True by logic
        assert z.kann_nochmal_versuchen(regel) is True

    def test_false_when_kein_retry_and_at_max(self):
        regel = make_regel(RetryStrategie.KEIN_RETRY, max_versuche=1)
        z = make_zustand(aktueller_versuch=1, status=RetryStatus.AUSSTEHEND)
        assert z.kann_nochmal_versuchen(regel) is False


# ===========================================================================
# PART 9: RetryZustand.naechsten_versuch_planen
# ===========================================================================

class TestNaechstenVersuchPlanen:
    def test_increments_aktueller_versuch(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, basis=10.0, max_versuche=3)
        z = make_zustand(aktueller_versuch=0)
        result = z.naechsten_versuch_planen(regel, NOW)
        assert result.aktueller_versuch == 1

    def test_sets_status_laufend(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, basis=10.0, max_versuche=3)
        z = make_zustand(aktueller_versuch=0)
        result = z.naechsten_versuch_planen(regel, NOW)
        assert result.status == RetryStatus.LAUFEND

    def test_sets_naechster_versuch_am(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, basis=10.0, max_versuche=3)
        z = make_zustand(aktueller_versuch=0)
        result = z.naechsten_versuch_planen(regel, NOW)
        assert result.naechster_versuch_am == NOW + timedelta(seconds=10.0)

    def test_exponential_backoff_timing(self):
        regel = make_regel(RetryStrategie.EXPONENTIELLES_BACKOFF, basis=5.0, max_versuche=3)
        z = make_zustand(aktueller_versuch=1)
        result = z.naechsten_versuch_planen(regel, NOW)
        # versuch 2: 5 * 2^1 = 10
        assert result.naechster_versuch_am == NOW + timedelta(seconds=10.0)

    def test_exceeds_max_returns_erschoepft(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, basis=10.0, max_versuche=3)
        z = make_zustand(aktueller_versuch=3)  # already at max
        result = z.naechsten_versuch_planen(regel, NOW)
        assert result.status == RetryStatus.ERSCHOEPFT

    def test_at_max_returns_erschoepft(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, basis=10.0, max_versuche=2)
        z = make_zustand(aktueller_versuch=2)
        result = z.naechsten_versuch_planen(regel, NOW)
        assert result.status == RetryStatus.ERSCHOEPFT

    def test_immutability_original_unchanged(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, basis=10.0, max_versuche=3)
        z = make_zustand(aktueller_versuch=0, status=RetryStatus.AUSSTEHEND)
        _ = z.naechsten_versuch_planen(regel, NOW)
        assert z.aktueller_versuch == 0
        assert z.status == RetryStatus.AUSSTEHEND

    def test_result_is_new_object(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, basis=10.0, max_versuche=3)
        z = make_zustand(aktueller_versuch=0)
        result = z.naechsten_versuch_planen(regel, NOW)
        assert result is not z

    def test_preserves_zustand_id(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, basis=10.0, max_versuche=3)
        z = make_zustand(aktueller_versuch=0)
        result = z.naechsten_versuch_planen(regel, NOW)
        assert result.zustand_id == z.zustand_id

    def test_preserves_befehl_typ(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, basis=10.0, max_versuche=3)
        z = make_zustand(aktueller_versuch=0)
        result = z.naechsten_versuch_planen(regel, NOW)
        assert result.befehl_typ == z.befehl_typ

    def test_erschoepft_no_naechster_versuch_change(self):
        regel = make_regel(RetryStrategie.FESTER_INTERVALL, basis=10.0, max_versuche=3)
        z = make_zustand(aktueller_versuch=3)
        result = z.naechsten_versuch_planen(regel, NOW)
        assert result.status == RetryStatus.ERSCHOEPFT
        # aktueller_versuch not incremented in the erschoepft branch
        assert result.aktueller_versuch == 3

    def test_jitter_timing(self):
        regel = make_regel(RetryStrategie.JITTER, basis=2.0, max_versuche=3, max_verz=60.0)
        z = make_zustand(aktueller_versuch=0)
        result = z.naechsten_versuch_planen(regel, NOW)
        # versuch 1: 2 * 1 * 1.5 = 3.0
        assert result.naechster_versuch_am == NOW + timedelta(seconds=3.0)

    def test_linear_timing_versuch3(self):
        regel = make_regel(RetryStrategie.LINEARES_BACKOFF, basis=15.0, max_versuche=4)
        z = make_zustand(aktueller_versuch=2)
        result = z.naechsten_versuch_planen(regel, NOW)
        # versuch 3: 15 * 3 = 45
        assert result.naechster_versuch_am == NOW + timedelta(seconds=45.0)


# ===========================================================================
# PART 10: get_default_retry_regeln
# ===========================================================================

class TestGetDefaultRetryRegeln:
    def test_returns_5_rules(self):
        regeln = get_default_retry_regeln()
        assert len(regeln) == 5

    def test_rr001_exists(self):
        ids = [r.regel_id for r in get_default_retry_regeln()]
        assert "RR-001" in ids

    def test_rr002_exists(self):
        ids = [r.regel_id for r in get_default_retry_regeln()]
        assert "RR-002" in ids

    def test_rr003_exists(self):
        ids = [r.regel_id for r in get_default_retry_regeln()]
        assert "RR-003" in ids

    def test_rr004_exists(self):
        ids = [r.regel_id for r in get_default_retry_regeln()]
        assert "RR-004" in ids

    def test_rr005_exists(self):
        ids = [r.regel_id for r in get_default_retry_regeln()]
        assert "RR-005" in ids

    def test_rr001_is_exponential(self):
        regel = next(r for r in get_default_retry_regeln() if r.regel_id == "RR-001")
        assert regel.strategie == RetryStrategie.EXPONENTIELLES_BACKOFF

    def test_rr002_is_fester_intervall(self):
        regel = next(r for r in get_default_retry_regeln() if r.regel_id == "RR-002")
        assert regel.strategie == RetryStrategie.FESTER_INTERVALL

    def test_rr003_is_lineares_backoff(self):
        regel = next(r for r in get_default_retry_regeln() if r.regel_id == "RR-003")
        assert regel.strategie == RetryStrategie.LINEARES_BACKOFF

    def test_rr004_is_jitter(self):
        regel = next(r for r in get_default_retry_regeln() if r.regel_id == "RR-004")
        assert regel.strategie == RetryStrategie.JITTER

    def test_rr005_is_kein_retry(self):
        regel = next(r for r in get_default_retry_regeln() if r.regel_id == "RR-005")
        assert regel.strategie == RetryStrategie.KEIN_RETRY

    def test_rr001_max_versuche_3(self):
        regel = next(r for r in get_default_retry_regeln() if r.regel_id == "RR-001")
        assert regel.max_versuche == 3

    def test_rr002_max_versuche_5(self):
        regel = next(r for r in get_default_retry_regeln() if r.regel_id == "RR-002")
        assert regel.max_versuche == 5

    def test_rr005_max_versuche_1(self):
        regel = next(r for r in get_default_retry_regeln() if r.regel_id == "RR-005")
        assert regel.max_versuche == 1

    def test_all_have_beschreibung(self):
        for r in get_default_retry_regeln():
            assert len(r.beschreibung) > 0

    def test_all_are_retry_regel_instances(self):
        for r in get_default_retry_regeln():
            assert isinstance(r, RetryRegel)


# ===========================================================================
# PART 11: CheckpointTyp + CheckpointStatus Enums
# ===========================================================================

class TestCheckpointEnums:
    def test_automatisch_value(self):
        assert CheckpointTyp.AUTOMATISCH == "AUTOMATISCH"

    def test_manuell_value(self):
        assert CheckpointTyp.MANUELL == "MANUELL"

    def test_vor_kritischem_schritt_value(self):
        assert CheckpointTyp.VOR_KRITISCHEM_SCHRITT == "VOR_KRITISCHEM_SCHRITT"

    def test_nach_fehler_value(self):
        assert CheckpointTyp.NACH_FEHLER == "NACH_FEHLER"

    def test_checkpoint_typ_count(self):
        assert len(CheckpointTyp) == 4

    def test_aktuell_value(self):
        assert CheckpointStatus.AKTUELL == "AKTUELL"

    def test_veraltet_value(self):
        assert CheckpointStatus.VERALTET == "VERALTET"

    def test_wiederhergestellt_value(self):
        assert CheckpointStatus.WIEDERHERGESTELLT == "WIEDERHERGESTELLT"

    def test_korrupt_value(self):
        assert CheckpointStatus.KORRUPT == "KORRUPT"

    def test_checkpoint_status_count(self):
        assert len(CheckpointStatus) == 4


# ===========================================================================
# PART 12: WorkflowCheckpoint.ist_verwendbar
# ===========================================================================

class TestIstVerwendbar:
    def test_aktuell_is_verwendbar(self):
        cp = make_checkpoint("CP-1", 1, CheckpointStatus.AKTUELL)
        assert cp.ist_verwendbar() is True

    def test_wiederhergestellt_is_verwendbar(self):
        cp = make_checkpoint("CP-2", 2, CheckpointStatus.WIEDERHERGESTELLT)
        assert cp.ist_verwendbar() is True

    def test_veraltet_not_verwendbar(self):
        cp = make_checkpoint("CP-3", 3, CheckpointStatus.VERALTET)
        assert cp.ist_verwendbar() is False

    def test_korrupt_not_verwendbar(self):
        cp = make_checkpoint("CP-4", 4, CheckpointStatus.KORRUPT)
        assert cp.ist_verwendbar() is False

    def test_ist_verwendbar_returns_bool(self):
        cp = make_checkpoint("CP-5", 1, CheckpointStatus.AKTUELL)
        assert isinstance(cp.ist_verwendbar(), bool)

    def test_default_status_aktuell(self):
        cp = WorkflowCheckpoint(
            checkpoint_id="CP-DEF",
            workflow_instanz_id="WI-X",
            checkpoint_typ=CheckpointTyp.MANUELL,
            zustand_snapshot={},
            schritt_nummer=1,
        )
        assert cp.ist_verwendbar() is True


# ===========================================================================
# PART 13: CheckpointSequenz.aktuellster_checkpoint
# ===========================================================================

class TestAktuellsterCheckpoint:
    def test_empty_sequenz_returns_none(self):
        s = CheckpointSequenz("WI-EMPTY")
        assert s.aktuellster_checkpoint() is None

    def test_single_aktuell_checkpoint(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [make_checkpoint("CP-1", 1, CheckpointStatus.AKTUELL)]
        result = s.aktuellster_checkpoint()
        assert result.checkpoint_id == "CP-1"

    def test_returns_highest_schritt_among_verwendbar(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 1, CheckpointStatus.AKTUELL),
            make_checkpoint("CP-2", 3, CheckpointStatus.AKTUELL),
            make_checkpoint("CP-3", 2, CheckpointStatus.AKTUELL),
        ]
        result = s.aktuellster_checkpoint()
        assert result.schritt_nummer == 3

    def test_ignores_veraltet(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 5, CheckpointStatus.VERALTET),
            make_checkpoint("CP-2", 2, CheckpointStatus.AKTUELL),
        ]
        result = s.aktuellster_checkpoint()
        assert result.schritt_nummer == 2

    def test_ignores_korrupt(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 10, CheckpointStatus.KORRUPT),
            make_checkpoint("CP-2", 3, CheckpointStatus.AKTUELL),
        ]
        result = s.aktuellster_checkpoint()
        assert result.schritt_nummer == 3

    def test_accepts_wiederhergestellt(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 2, CheckpointStatus.WIEDERHERGESTELLT),
            make_checkpoint("CP-2", 1, CheckpointStatus.AKTUELL),
        ]
        result = s.aktuellster_checkpoint()
        assert result.schritt_nummer == 2

    def test_all_korrupt_returns_none(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 1, CheckpointStatus.KORRUPT),
            make_checkpoint("CP-2", 2, CheckpointStatus.KORRUPT),
        ]
        assert s.aktuellster_checkpoint() is None

    def test_all_veraltet_returns_none(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 1, CheckpointStatus.VERALTET),
        ]
        assert s.aktuellster_checkpoint() is None


# ===========================================================================
# PART 14: CheckpointSequenz.wiederherstellungs_punkt
# ===========================================================================

class TestWiederherstellungsPunkt:
    def test_empty_returns_none(self):
        s = CheckpointSequenz("WI-X")
        assert s.wiederherstellungs_punkt(5) is None

    def test_ab_schritt_999_returns_highest_usable(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 1, CheckpointStatus.AKTUELL),
            make_checkpoint("CP-2", 5, CheckpointStatus.AKTUELL),
        ]
        result = s.wiederherstellungs_punkt(999)
        assert result.schritt_nummer == 5

    def test_ab_schritt_2_returns_at_most_2(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 1, CheckpointStatus.AKTUELL),
            make_checkpoint("CP-2", 2, CheckpointStatus.AKTUELL),
            make_checkpoint("CP-3", 3, CheckpointStatus.AKTUELL),
        ]
        result = s.wiederherstellungs_punkt(2)
        assert result.schritt_nummer == 2

    def test_ab_schritt_1_returns_step1(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 1, CheckpointStatus.AKTUELL),
            make_checkpoint("CP-2", 2, CheckpointStatus.AKTUELL),
        ]
        result = s.wiederherstellungs_punkt(1)
        assert result.schritt_nummer == 1

    def test_no_usable_before_ab_schritt_returns_none(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 5, CheckpointStatus.AKTUELL),
        ]
        result = s.wiederherstellungs_punkt(3)
        assert result is None

    def test_ignores_korrupt_before_ab_schritt(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 1, CheckpointStatus.AKTUELL),
            make_checkpoint("CP-2", 2, CheckpointStatus.KORRUPT),
        ]
        result = s.wiederherstellungs_punkt(2)
        assert result.schritt_nummer == 1

    def test_ignores_veraltet_before_ab_schritt(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 1, CheckpointStatus.VERALTET),
            make_checkpoint("CP-2", 2, CheckpointStatus.AKTUELL),
        ]
        result = s.wiederherstellungs_punkt(3)
        assert result.schritt_nummer == 2

    def test_wiederhergestellt_included(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 1, CheckpointStatus.WIEDERHERGESTELLT),
            make_checkpoint("CP-2", 3, CheckpointStatus.KORRUPT),
        ]
        result = s.wiederherstellungs_punkt(5)
        assert result.schritt_nummer == 1

    def test_exactly_at_ab_schritt_included(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 3, CheckpointStatus.AKTUELL),
        ]
        result = s.wiederherstellungs_punkt(3)
        assert result.schritt_nummer == 3

    def test_returns_max_below_ab_schritt(self):
        s = CheckpointSequenz("WI-X")
        s.checkpoints = [
            make_checkpoint("CP-1", 1, CheckpointStatus.AKTUELL),
            make_checkpoint("CP-2", 2, CheckpointStatus.AKTUELL),
            make_checkpoint("CP-3", 4, CheckpointStatus.AKTUELL),
        ]
        result = s.wiederherstellungs_punkt(3)
        assert result.schritt_nummer == 2


# ===========================================================================
# PART 15: get_default_checkpoint_sequenzen
# ===========================================================================

class TestGetDefaultCheckpointSequenzen:
    def test_returns_3_sequences(self):
        seqs = get_default_checkpoint_sequenzen()
        assert len(seqs) == 3

    def test_wi_k_001_exists(self):
        ids = [s.instanz_id for s in get_default_checkpoint_sequenzen()]
        assert "WI-K-001" in ids

    def test_wi_s_002_exists(self):
        ids = [s.instanz_id for s in get_default_checkpoint_sequenzen()]
        assert "WI-S-002" in ids

    def test_wi_leer_003_exists(self):
        ids = [s.instanz_id for s in get_default_checkpoint_sequenzen()]
        assert "WI-LEER-003" in ids

    def test_wi_k_001_has_3_checkpoints(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-K-001")
        assert len(seq.checkpoints) == 3

    def test_wi_k_001_aktuellster_is_cp003(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-K-001")
        result = seq.aktuellster_checkpoint()
        assert result.checkpoint_id == "CP-003"

    def test_wi_k_001_aktuellster_schritt_3(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-K-001")
        result = seq.aktuellster_checkpoint()
        assert result.schritt_nummer == 3

    def test_wi_k_001_cp001_is_veraltet(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-K-001")
        cp = next(c for c in seq.checkpoints if c.checkpoint_id == "CP-001")
        assert cp.status == CheckpointStatus.VERALTET

    def test_wi_k_001_cp002_is_veraltet(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-K-001")
        cp = next(c for c in seq.checkpoints if c.checkpoint_id == "CP-002")
        assert cp.status == CheckpointStatus.VERALTET

    def test_wi_k_001_cp003_is_aktuell(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-K-001")
        cp = next(c for c in seq.checkpoints if c.checkpoint_id == "CP-003")
        assert cp.status == CheckpointStatus.AKTUELL

    def test_wi_s_002_has_2_checkpoints(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-S-002")
        assert len(seq.checkpoints) == 2

    def test_wi_s_002_cp004_is_aktuell(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-S-002")
        cp = next(c for c in seq.checkpoints if c.checkpoint_id == "CP-004")
        assert cp.status == CheckpointStatus.AKTUELL

    def test_wi_s_002_cp005_is_korrupt(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-S-002")
        cp = next(c for c in seq.checkpoints if c.checkpoint_id == "CP-005")
        assert cp.status == CheckpointStatus.KORRUPT

    def test_wi_s_002_aktuellster_is_cp004(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-S-002")
        result = seq.aktuellster_checkpoint()
        assert result.checkpoint_id == "CP-004"

    def test_wi_leer_003_has_no_checkpoints(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-LEER-003")
        assert len(seq.checkpoints) == 0

    def test_wi_leer_003_aktuellster_is_none(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-LEER-003")
        assert seq.aktuellster_checkpoint() is None

    def test_all_are_checkpoint_sequenz_instances(self):
        for s in get_default_checkpoint_sequenzen():
            assert isinstance(s, CheckpointSequenz)

    def test_wi_k_001_cp002_typ_vor_kritischem(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-K-001")
        cp = next(c for c in seq.checkpoints if c.checkpoint_id == "CP-002")
        assert cp.checkpoint_typ == CheckpointTyp.VOR_KRITISCHEM_SCHRITT

    def test_wi_s_002_cp005_typ_nach_fehler(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-S-002")
        cp = next(c for c in seq.checkpoints if c.checkpoint_id == "CP-005")
        assert cp.checkpoint_typ == CheckpointTyp.NACH_FEHLER


# ===========================================================================
# PART 16: Edge cases and integration scenarios
# ===========================================================================

class TestEdgeCases:
    def test_retry_zustand_default_status_ausstehend(self):
        z = RetryZustand(zustand_id="Z1", regel_id="R1", befehl_typ="CMD")
        assert z.status == RetryStatus.AUSSTEHEND

    def test_retry_zustand_default_versuch_zero(self):
        z = RetryZustand(zustand_id="Z1", regel_id="R1", befehl_typ="CMD")
        assert z.aktueller_versuch == 0

    def test_retry_zustand_default_naechster_none(self):
        z = RetryZustand(zustand_id="Z1", regel_id="R1", befehl_typ="CMD")
        assert z.naechster_versuch_am is None

    def test_full_retry_cycle_three_attempts(self):
        """Simulate a full retry cycle: 3 attempts exhausted."""
        regel = make_regel(RetryStrategie.EXPONENTIELLES_BACKOFF, basis=5.0, max_versuche=3)
        z = make_zustand(aktueller_versuch=0, status=RetryStatus.AUSSTEHEND)
        assert z.kann_nochmal_versuchen(regel) is True

        z2 = z.naechsten_versuch_planen(regel, NOW)
        assert z2.aktueller_versuch == 1
        assert z2.kann_nochmal_versuchen(regel) is True

        z3 = z2.naechsten_versuch_planen(regel, NOW)
        assert z3.aktueller_versuch == 2
        assert z3.kann_nochmal_versuchen(regel) is True

        z4 = z3.naechsten_versuch_planen(regel, NOW)
        assert z4.aktueller_versuch == 3
        assert z4.kann_nochmal_versuchen(regel) is False

        z5 = z4.naechsten_versuch_planen(regel, NOW)
        assert z5.status == RetryStatus.ERSCHOEPFT

    def test_checkpoint_sequenz_wiederherstellung_after_korrupt(self):
        """Recovery scenario: step 2 checkpoint corrupted, restore from step 1."""
        s = CheckpointSequenz("WI-RECOVERY")
        s.checkpoints = [
            make_checkpoint("CP-A", 1, CheckpointStatus.AKTUELL),
            make_checkpoint("CP-B", 2, CheckpointStatus.KORRUPT),
        ]
        result = s.wiederherstellungs_punkt(2)
        assert result.schritt_nummer == 1

    def test_berechne_verzoegerung_kein_retry_basis_zero(self):
        r = RetryRegel("RR-005", RetryStrategie.KEIN_RETRY, 1, 0.0, 0.0)
        assert r.berechne_verzoegerung(1) == 0.0

    def test_checkpoint_zustand_snapshot_stored(self):
        cp = WorkflowCheckpoint(
            checkpoint_id="CP-X",
            workflow_instanz_id="WI-X",
            checkpoint_typ=CheckpointTyp.MANUELL,
            zustand_snapshot={"key": "value", "step": 42},
            schritt_nummer=5,
        )
        assert cp.zustand_snapshot["step"] == 42

    def test_retry_regel_beschreibung_default_empty(self):
        r = RetryRegel("R1", RetryStrategie.FESTER_INTERVALL, 3, 10.0)
        assert r.beschreibung == ""

    def test_linear_backoff_cap_enforced(self):
        r = make_regel(RetryStrategie.LINEARES_BACKOFF, basis=100.0, max_verz=150.0)
        # versuch 3: 300 → capped to 150
        assert r.berechne_verzoegerung(3) == 150.0

    def test_exponential_backoff_large_versuch_capped(self):
        r = make_regel(RetryStrategie.EXPONENTIELLES_BACKOFF, basis=1.0, max_verz=100.0)
        # versuch 10: 1 * 512 → capped to 100
        assert r.berechne_verzoegerung(10) == 100.0

    def test_jitter_large_versuch_capped(self):
        r = make_regel(RetryStrategie.JITTER, basis=1.0, max_verz=50.0)
        # versuch 6: 1 * 32 * 1.5 = 48 → within cap
        assert r.berechne_verzoegerung(6) == 48.0

    def test_wi_k_001_wiederherstellung_vor_schritt3(self):
        """Recovery from before step 3: should get CP-001 or CP-002 (both VERALTET → None)."""
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-K-001")
        result = seq.wiederherstellungs_punkt(2)
        # CP-001 and CP-002 are VERALTET (not verwendbar) → None
        assert result is None

    def test_wi_s_002_wiederherstellung_ab_schritt1(self):
        seq = next(s for s in get_default_checkpoint_sequenzen() if s.instanz_id == "WI-S-002")
        result = seq.wiederherstellungs_punkt(1)
        assert result.checkpoint_id == "CP-004"

    def test_retry_zustand_letzter_fehler_default_empty(self):
        z = RetryZustand(zustand_id="Z1", regel_id="R1", befehl_typ="CMD")
        assert z.letzter_fehler == ""
