"""
Wave 51 – Process Capacity Planning + Workflow Compensation Contracts
130+ tests covering all contracts, boundary values, and edge cases.
"""
import pytest
from datetime import datetime

from app.core.process_capacity_contracts_wave51 import (
    KapazitaetsTyp,
    KapazitaetsStatus,
    SkalierungsStrategie,
    KapazitaetsRegel,
    KapazitaetsMessung,
    KapazitaetsPlan,
    get_default_kapazitaets_regeln,
)
from app.core.workflow_compensation_contracts import (
    KompensationsTyp,
    KompensationsStatus,
    SagaStatus,
    KompensationsSchritt,
    SagaInstanz,
    erstelle_kompensations_plan,
    get_default_saga_instanzen,
)


# ─────────────────────────────────────────────────────────────────────────────
# KapazitaetsTyp Enum
# ─────────────────────────────────────────────────────────────────────────────

class TestKapazitaetsTypEnum:
    def test_cpu_value(self):
        assert KapazitaetsTyp.CPU == "CPU"

    def test_speicher_value(self):
        assert KapazitaetsTyp.SPEICHER == "SPEICHER"

    def test_datenbankverbindungen_value(self):
        assert KapazitaetsTyp.DATENBANKVERBINDUNGEN == "DATENBANKVERBINDUNGEN"

    def test_nachrichtenwarteschlange_value(self):
        assert KapazitaetsTyp.NACHRICHTENWARTESCHLANGE == "NACHRICHTENWARTESCHLANGE"

    def test_externe_api_value(self):
        assert KapazitaetsTyp.EXTERNE_API == "EXTERNE_API"

    def test_all_members(self):
        assert len(KapazitaetsTyp) == 5


# ─────────────────────────────────────────────────────────────────────────────
# KapazitaetsStatus Enum
# ─────────────────────────────────────────────────────────────────────────────

class TestKapazitaetsStatusEnum:
    def test_normal_value(self):
        assert KapazitaetsStatus.NORMAL == "NORMAL"

    def test_erhoet_value(self):
        assert KapazitaetsStatus.ERHOET == "ERHOET"

    def test_kritisch_value(self):
        assert KapazitaetsStatus.KRITISCH == "KRITISCH"

    def test_ueberlastet_value(self):
        assert KapazitaetsStatus.UEBERLASTET == "UEBERLASTET"

    def test_all_members(self):
        assert len(KapazitaetsStatus) == 4


# ─────────────────────────────────────────────────────────────────────────────
# SkalierungsStrategie Enum
# ─────────────────────────────────────────────────────────────────────────────

class TestSkalierungsStrategieEnum:
    def test_manuell(self):
        assert SkalierungsStrategie.MANUELL == "MANUELL"

    def test_automatisch(self):
        assert SkalierungsStrategie.AUTOMATISCH == "AUTOMATISCH"

    def test_kein_skalieren(self):
        assert SkalierungsStrategie.KEIN_SKALIEREN == "KEIN_SKALIEREN"

    def test_all_members(self):
        assert len(SkalierungsStrategie) == 3


# ─────────────────────────────────────────────────────────────────────────────
# KapazitaetsRegel.berechne_status – standard thresholds (70/90)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def standard_regel():
    return KapazitaetsRegel(
        regel_id="KR-TEST",
        kapazitaets_typ=KapazitaetsTyp.CPU,
        max_kapazitaet=100.0,
        warnschwelle_pct=70.0,
        kritisch_schwelle_pct=90.0,
        skalierungs_strategie=SkalierungsStrategie.AUTOMATISCH,
    )


class TestBerechneStatus:
    def test_zero_auslastung_normal(self, standard_regel):
        assert standard_regel.berechne_status(0.0) == KapazitaetsStatus.NORMAL

    def test_below_warn_normal(self, standard_regel):
        assert standard_regel.berechne_status(50.0) == KapazitaetsStatus.NORMAL

    def test_just_below_warn_normal(self, standard_regel):
        # 69.9 → 69.9% < 70 → NORMAL
        assert standard_regel.berechne_status(69.9) == KapazitaetsStatus.NORMAL

    def test_at_warn_threshold_erhoet(self, standard_regel):
        # 70.0 → 70% >= 70 → ERHOET
        assert standard_regel.berechne_status(70.0) == KapazitaetsStatus.ERHOET

    def test_above_warn_erhoet(self, standard_regel):
        assert standard_regel.berechne_status(75.0) == KapazitaetsStatus.ERHOET

    def test_just_below_kritisch_erhoet(self, standard_regel):
        # 89.9 → 89.9% < 90 → ERHOET
        assert standard_regel.berechne_status(89.9) == KapazitaetsStatus.ERHOET

    def test_at_kritisch_threshold(self, standard_regel):
        # 90.0 → 90% >= 90 → KRITISCH
        assert standard_regel.berechne_status(90.0) == KapazitaetsStatus.KRITISCH

    def test_above_kritisch(self, standard_regel):
        assert standard_regel.berechne_status(95.0) == KapazitaetsStatus.KRITISCH

    def test_just_below_100_kritisch(self, standard_regel):
        # 99.9 → 99.9% < 100 → KRITISCH
        assert standard_regel.berechne_status(99.9) == KapazitaetsStatus.KRITISCH

    def test_at_100_ueberlastet(self, standard_regel):
        # 100.0 → 100% >= 100 → UEBERLASTET
        assert standard_regel.berechne_status(100.0) == KapazitaetsStatus.UEBERLASTET

    def test_above_100_ueberlastet(self, standard_regel):
        assert standard_regel.berechne_status(120.0) == KapazitaetsStatus.UEBERLASTET

    def test_negative_auslastung_normal(self, standard_regel):
        # negative → pct negative → NORMAL
        assert standard_regel.berechne_status(-10.0) == KapazitaetsStatus.NORMAL

    def test_max_kapazitaet_zero_returns_normal(self):
        regel = KapazitaetsRegel(
            regel_id="KR-ZERO",
            kapazitaets_typ=KapazitaetsTyp.SPEICHER,
            max_kapazitaet=0.0,
            warnschwelle_pct=70.0,
            kritisch_schwelle_pct=90.0,
            skalierungs_strategie=SkalierungsStrategie.MANUELL,
        )
        assert regel.berechne_status(500.0) == KapazitaetsStatus.NORMAL

    def test_custom_thresholds_50_80(self):
        regel = KapazitaetsRegel(
            regel_id="KR-CUSTOM",
            kapazitaets_typ=KapazitaetsTyp.DATENBANKVERBINDUNGEN,
            max_kapazitaet=200.0,
            warnschwelle_pct=50.0,
            kritisch_schwelle_pct=80.0,
            skalierungs_strategie=SkalierungsStrategie.MANUELL,
        )
        assert regel.berechne_status(90.0) == KapazitaetsStatus.NORMAL    # 45% < 50
        assert regel.berechne_status(100.0) == KapazitaetsStatus.ERHOET   # 50%
        assert regel.berechne_status(150.0) == KapazitaetsStatus.ERHOET   # 75%
        assert regel.berechne_status(160.0) == KapazitaetsStatus.KRITISCH  # 80%
        assert regel.berechne_status(200.0) == KapazitaetsStatus.UEBERLASTET  # 100%

    def test_speicher_regel_large_max(self):
        regel = KapazitaetsRegel(
            regel_id="KR-002",
            kapazitaets_typ=KapazitaetsTyp.SPEICHER,
            max_kapazitaet=16384.0,
            warnschwelle_pct=70.0,
            kritisch_schwelle_pct=90.0,
            skalierungs_strategie=SkalierungsStrategie.AUTOMATISCH,
        )
        assert regel.berechne_status(11468.8) == KapazitaetsStatus.ERHOET   # 70%
        assert regel.berechne_status(14745.6) == KapazitaetsStatus.KRITISCH  # 90%

    def test_exact_boundary_70_pct(self, standard_regel):
        # Exactly 70/100 * 100 = 70.0%
        result = standard_regel.berechne_status(70.0)
        assert result == KapazitaetsStatus.ERHOET

    def test_exact_boundary_90_pct(self, standard_regel):
        result = standard_regel.berechne_status(90.0)
        assert result == KapazitaetsStatus.KRITISCH

    def test_exact_boundary_100_pct(self, standard_regel):
        result = standard_regel.berechne_status(100.0)
        assert result == KapazitaetsStatus.UEBERLASTET


# ─────────────────────────────────────────────────────────────────────────────
# KapazitaetsRegel attributes
# ─────────────────────────────────────────────────────────────────────────────

class TestKapazitaetsRegelAttributes:
    def test_regel_id_stored(self):
        r = KapazitaetsRegel("KR-X", KapazitaetsTyp.CPU, 100.0, 70.0, 90.0, SkalierungsStrategie.MANUELL, "Test")
        assert r.regel_id == "KR-X"

    def test_beschreibung_default_empty(self):
        r = KapazitaetsRegel("KR-X", KapazitaetsTyp.CPU, 100.0, 70.0, 90.0, SkalierungsStrategie.MANUELL)
        assert r.beschreibung == ""

    def test_beschreibung_set(self):
        r = KapazitaetsRegel("KR-X", KapazitaetsTyp.CPU, 100.0, 70.0, 90.0, SkalierungsStrategie.MANUELL, "My desc")
        assert r.beschreibung == "My desc"


# ─────────────────────────────────────────────────────────────────────────────
# KapazitaetsMessung
# ─────────────────────────────────────────────────────────────────────────────

class TestKapazitaetsMessung:
    def test_create_messung(self):
        now = datetime(2026, 3, 16, 8, 0, 0)
        m = KapazitaetsMessung("M-001", "KR-001", KapazitaetsTyp.CPU, 75.0, now, KapazitaetsStatus.ERHOET)
        assert m.messung_id == "M-001"
        assert m.regel_id == "KR-001"
        assert m.kapazitaets_typ == KapazitaetsTyp.CPU
        assert m.aktuelle_auslastung == 75.0
        assert m.status == KapazitaetsStatus.ERHOET

    def test_default_status_normal(self):
        now = datetime.utcnow()
        m = KapazitaetsMessung("M-002", "KR-001", KapazitaetsTyp.SPEICHER, 50.0, now)
        assert m.status == KapazitaetsStatus.NORMAL


# ─────────────────────────────────────────────────────────────────────────────
# KapazitaetsPlan
# ─────────────────────────────────────────────────────────────────────────────

class TestKapazitaetsPlan:
    @pytest.fixture
    def plan_with_messungen(self):
        now = datetime(2026, 3, 16, 8, 0, 0)
        plan = KapazitaetsPlan("P-001", "TENANT-A")
        plan.messungen = [
            KapazitaetsMessung("M-001", "KR-001", KapazitaetsTyp.CPU, 50.0, now, KapazitaetsStatus.NORMAL),
            KapazitaetsMessung("M-002", "KR-002", KapazitaetsTyp.SPEICHER, 75.0, now, KapazitaetsStatus.ERHOET),
            KapazitaetsMessung("M-003", "KR-003", KapazitaetsTyp.DATENBANKVERBINDUNGEN, 92.0, now, KapazitaetsStatus.KRITISCH),
            KapazitaetsMessung("M-004", "KR-004", KapazitaetsTyp.NACHRICHTENWARTESCHLANGE, 105.0, now, KapazitaetsStatus.UEBERLASTET),
        ]
        return plan

    def test_kritische_messungen_returns_kritisch_and_ueberlastet(self, plan_with_messungen):
        krit = plan_with_messungen.kritische_messungen()
        assert len(krit) == 2
        statuses = {m.status for m in krit}
        assert KapazitaetsStatus.KRITISCH in statuses
        assert KapazitaetsStatus.UEBERLASTET in statuses

    def test_kritische_messungen_excludes_normal_erhoet(self, plan_with_messungen):
        krit = plan_with_messungen.kritische_messungen()
        for m in krit:
            assert m.status not in (KapazitaetsStatus.NORMAL, KapazitaetsStatus.ERHOET)

    def test_kritische_messungen_empty_plan(self):
        plan = KapazitaetsPlan("P-EMPTY", "TENANT-B")
        assert plan.kritische_messungen() == []

    def test_auslastungs_zusammenfassung_counts(self, plan_with_messungen):
        summary = plan_with_messungen.auslastungs_zusammenfassung()
        assert summary[KapazitaetsStatus.NORMAL] == 1
        assert summary[KapazitaetsStatus.ERHOET] == 1
        assert summary[KapazitaetsStatus.KRITISCH] == 1
        assert summary[KapazitaetsStatus.UEBERLASTET] == 1

    def test_auslastungs_zusammenfassung_zeros_for_missing(self):
        now = datetime.utcnow()
        plan = KapazitaetsPlan("P-002", "TENANT-C")
        plan.messungen = [
            KapazitaetsMessung("M-001", "KR-001", KapazitaetsTyp.CPU, 50.0, now, KapazitaetsStatus.NORMAL),
        ]
        summary = plan.auslastungs_zusammenfassung()
        assert summary[KapazitaetsStatus.ERHOET] == 0
        assert summary[KapazitaetsStatus.KRITISCH] == 0
        assert summary[KapazitaetsStatus.UEBERLASTET] == 0

    def test_auslastungs_zusammenfassung_all_keys_present(self, plan_with_messungen):
        summary = plan_with_messungen.auslastungs_zusammenfassung()
        for status in KapazitaetsStatus:
            assert status in summary

    def test_auslastungs_zusammenfassung_empty_plan(self):
        plan = KapazitaetsPlan("P-EMPTY", "TENANT-D")
        summary = plan.auslastungs_zusammenfassung()
        assert all(v == 0 for v in summary.values())

    def test_plan_default_messungen_empty(self):
        plan = KapazitaetsPlan("P-003", "TENANT-E")
        assert plan.messungen == []

    def test_plan_erstellt_am_set(self):
        plan = KapazitaetsPlan("P-004", "TENANT-F")
        assert isinstance(plan.erstellt_am, datetime)


# ─────────────────────────────────────────────────────────────────────────────
# get_default_kapazitaets_regeln
# ─────────────────────────────────────────────────────────────────────────────

class TestGetDefaultKapazitaetsRegeln:
    @pytest.fixture
    def regeln(self):
        return get_default_kapazitaets_regeln()

    def test_returns_5_regeln(self, regeln):
        assert len(regeln) == 5

    def test_all_are_kapazitaets_regel(self, regeln):
        for r in regeln:
            assert isinstance(r, KapazitaetsRegel)

    def test_regel_ids(self, regeln):
        ids = [r.regel_id for r in regeln]
        assert "KR-001" in ids
        assert "KR-002" in ids
        assert "KR-003" in ids
        assert "KR-004" in ids
        assert "KR-005" in ids

    def test_kr001_is_cpu(self, regeln):
        kr1 = next(r for r in regeln if r.regel_id == "KR-001")
        assert kr1.kapazitaets_typ == KapazitaetsTyp.CPU

    def test_kr002_is_speicher(self, regeln):
        kr2 = next(r for r in regeln if r.regel_id == "KR-002")
        assert kr2.kapazitaets_typ == KapazitaetsTyp.SPEICHER

    def test_kr003_is_db_verbindungen(self, regeln):
        kr3 = next(r for r in regeln if r.regel_id == "KR-003")
        assert kr3.kapazitaets_typ == KapazitaetsTyp.DATENBANKVERBINDUNGEN

    def test_kr004_is_nachrichtenwarteschlange(self, regeln):
        kr4 = next(r for r in regeln if r.regel_id == "KR-004")
        assert kr4.kapazitaets_typ == KapazitaetsTyp.NACHRICHTENWARTESCHLANGE

    def test_kr005_is_externe_api(self, regeln):
        kr5 = next(r for r in regeln if r.regel_id == "KR-005")
        assert kr5.kapazitaets_typ == KapazitaetsTyp.EXTERNE_API

    def test_kr001_automatisch(self, regeln):
        kr1 = next(r for r in regeln if r.regel_id == "KR-001")
        assert kr1.skalierungs_strategie == SkalierungsStrategie.AUTOMATISCH

    def test_kr003_manuell(self, regeln):
        kr3 = next(r for r in regeln if r.regel_id == "KR-003")
        assert kr3.skalierungs_strategie == SkalierungsStrategie.MANUELL

    def test_kr005_kein_skalieren(self, regeln):
        kr5 = next(r for r in regeln if r.regel_id == "KR-005")
        assert kr5.skalierungs_strategie == SkalierungsStrategie.KEIN_SKALIEREN

    def test_kr002_max_kapazitaet_16384(self, regeln):
        kr2 = next(r for r in regeln if r.regel_id == "KR-002")
        assert kr2.max_kapazitaet == 16384.0

    def test_kr004_max_kapazitaet_10000(self, regeln):
        kr4 = next(r for r in regeln if r.regel_id == "KR-004")
        assert kr4.max_kapazitaet == 10000.0

    def test_all_warnschwelle_70(self, regeln):
        for r in regeln:
            assert r.warnschwelle_pct == 70.0

    def test_all_kritisch_schwelle_90(self, regeln):
        for r in regeln:
            assert r.kritisch_schwelle_pct == 90.0

    def test_all_have_beschreibung(self, regeln):
        for r in regeln:
            assert r.beschreibung != ""


# ─────────────────────────────────────────────────────────────────────────────
# KompensationsTyp Enum
# ─────────────────────────────────────────────────────────────────────────────

class TestKompensationsTypEnum:
    def test_rueckgaengig(self):
        assert KompensationsTyp.RUECKGAENGIG == "RUECKGAENGIG"

    def test_ausgleich(self):
        assert KompensationsTyp.AUSGLEICH == "AUSGLEICH"

    def test_neustart(self):
        assert KompensationsTyp.NEUSTART == "NEUSTART"

    def test_ueberspringen(self):
        assert KompensationsTyp.UEBERSPRINGEN == "UEBERSPRINGEN"

    def test_abbrechen(self):
        assert KompensationsTyp.ABBRECHEN == "ABBRECHEN"

    def test_all_members(self):
        assert len(KompensationsTyp) == 5


# ─────────────────────────────────────────────────────────────────────────────
# KompensationsStatus Enum
# ─────────────────────────────────────────────────────────────────────────────

class TestKompensationsStatusEnum:
    def test_ausstehend(self):
        assert KompensationsStatus.AUSSTEHEND == "AUSSTEHEND"

    def test_laufend(self):
        assert KompensationsStatus.LAUFEND == "LAUFEND"

    def test_abgeschlossen(self):
        assert KompensationsStatus.ABGESCHLOSSEN == "ABGESCHLOSSEN"

    def test_fehlgeschlagen(self):
        assert KompensationsStatus.FEHLGESCHLAGEN == "FEHLGESCHLAGEN"

    def test_nicht_notwendig(self):
        assert KompensationsStatus.NICHT_NOTWENDIG == "NICHT_NOTWENDIG"

    def test_all_members(self):
        assert len(KompensationsStatus) == 5


# ─────────────────────────────────────────────────────────────────────────────
# SagaStatus Enum
# ─────────────────────────────────────────────────────────────────────────────

class TestSagaStatusEnum:
    def test_laufend(self):
        assert SagaStatus.LAUFEND == "LAUFEND"

    def test_abgeschlossen(self):
        assert SagaStatus.ABGESCHLOSSEN == "ABGESCHLOSSEN"

    def test_kompensiert(self):
        assert SagaStatus.KOMPENSIERT == "KOMPENSIERT"

    def test_fehlgeschlagen(self):
        assert SagaStatus.FEHLGESCHLAGEN == "FEHLGESCHLAGEN"

    def test_all_members(self):
        assert len(SagaStatus) == 4


# ─────────────────────────────────────────────────────────────────────────────
# KompensationsSchritt.ist_abgeschlossen
# ─────────────────────────────────────────────────────────────────────────────

class TestKompensationsSchrittIstAbgeschlossen:
    def _make(self, status: KompensationsStatus) -> KompensationsSchritt:
        return KompensationsSchritt(
            schritt_id="SK-TEST",
            saga_id="SI-TEST",
            schritt_name="Test",
            kompensations_typ=KompensationsTyp.RUECKGAENGIG,
            status=status,
        )

    def test_abgeschlossen_is_true(self):
        assert self._make(KompensationsStatus.ABGESCHLOSSEN).ist_abgeschlossen is True

    def test_fehlgeschlagen_is_true(self):
        assert self._make(KompensationsStatus.FEHLGESCHLAGEN).ist_abgeschlossen is True

    def test_nicht_notwendig_is_true(self):
        assert self._make(KompensationsStatus.NICHT_NOTWENDIG).ist_abgeschlossen is True

    def test_ausstehend_is_false(self):
        assert self._make(KompensationsStatus.AUSSTEHEND).ist_abgeschlossen is False

    def test_laufend_is_false(self):
        assert self._make(KompensationsStatus.LAUFEND).ist_abgeschlossen is False

    def test_default_status_ausstehend(self):
        s = KompensationsSchritt("SK-D", "SI-D", "Name", KompensationsTyp.AUSGLEICH)
        assert s.status == KompensationsStatus.AUSSTEHEND
        assert s.ist_abgeschlossen is False

    def test_fehler_nachricht_default_empty(self):
        s = KompensationsSchritt("SK-D", "SI-D", "Name", KompensationsTyp.AUSGLEICH)
        assert s.fehler_nachricht == ""

    def test_fehler_nachricht_set(self):
        s = KompensationsSchritt(
            "SK-D", "SI-D", "Name", KompensationsTyp.ABBRECHEN,
            KompensationsStatus.FEHLGESCHLAGEN, fehler_nachricht="Timeout"
        )
        assert s.fehler_nachricht == "Timeout"


# ─────────────────────────────────────────────────────────────────────────────
# SagaInstanz.offene_kompensationen
# ─────────────────────────────────────────────────────────────────────────────

class TestSagaInstanzOffeneKompensationen:
    def test_returns_only_ausstehend(self):
        saga = SagaInstanz("SI-T", "test", "TENANT-X")
        saga.schritte = [
            KompensationsSchritt("SK-1", "SI-T", "S1", KompensationsTyp.RUECKGAENGIG, KompensationsStatus.AUSSTEHEND),
            KompensationsSchritt("SK-2", "SI-T", "S2", KompensationsTyp.AUSGLEICH, KompensationsStatus.LAUFEND),
            KompensationsSchritt("SK-3", "SI-T", "S3", KompensationsTyp.NEUSTART, KompensationsStatus.AUSSTEHEND),
        ]
        offen = saga.offene_kompensationen()
        assert len(offen) == 2
        for s in offen:
            assert s.status == KompensationsStatus.AUSSTEHEND

    def test_no_open_if_all_done(self):
        saga = SagaInstanz("SI-T", "test", "TENANT-X")
        saga.schritte = [
            KompensationsSchritt("SK-1", "SI-T", "S1", KompensationsTyp.RUECKGAENGIG, KompensationsStatus.ABGESCHLOSSEN),
            KompensationsSchritt("SK-2", "SI-T", "S2", KompensationsTyp.AUSGLEICH, KompensationsStatus.NICHT_NOTWENDIG),
        ]
        assert saga.offene_kompensationen() == []

    def test_empty_schritte(self):
        saga = SagaInstanz("SI-T", "test", "TENANT-X")
        assert saga.offene_kompensationen() == []


# ─────────────────────────────────────────────────────────────────────────────
# SagaInstanz.berechne_saga_status
# ─────────────────────────────────────────────────────────────────────────────

class TestBerecheSagaStatus:
    def test_empty_schritte_returns_abgeschlossen(self):
        saga = SagaInstanz("SI-T", "test", "T")
        assert saga.berechne_saga_status() == SagaStatus.ABGESCHLOSSEN

    def test_any_laufend_returns_laufend(self):
        saga = SagaInstanz("SI-T", "test", "T")
        saga.schritte = [
            KompensationsSchritt("SK-1", "SI-T", "S1", KompensationsTyp.RUECKGAENGIG, KompensationsStatus.LAUFEND),
            KompensationsSchritt("SK-2", "SI-T", "S2", KompensationsTyp.AUSGLEICH, KompensationsStatus.AUSSTEHEND),
        ]
        assert saga.berechne_saga_status() == SagaStatus.LAUFEND

    def test_laufend_priority_over_fehlgeschlagen(self):
        saga = SagaInstanz("SI-T", "test", "T")
        saga.schritte = [
            KompensationsSchritt("SK-1", "SI-T", "S1", KompensationsTyp.RUECKGAENGIG, KompensationsStatus.LAUFEND),
            KompensationsSchritt("SK-2", "SI-T", "S2", KompensationsTyp.AUSGLEICH, KompensationsStatus.FEHLGESCHLAGEN),
        ]
        assert saga.berechne_saga_status() == SagaStatus.LAUFEND

    def test_any_fehlgeschlagen_returns_fehlgeschlagen(self):
        saga = SagaInstanz("SI-T", "test", "T")
        saga.schritte = [
            KompensationsSchritt("SK-1", "SI-T", "S1", KompensationsTyp.RUECKGAENGIG, KompensationsStatus.FEHLGESCHLAGEN),
            KompensationsSchritt("SK-2", "SI-T", "S2", KompensationsTyp.AUSGLEICH, KompensationsStatus.ABGESCHLOSSEN),
        ]
        assert saga.berechne_saga_status() == SagaStatus.FEHLGESCHLAGEN

    def test_all_nicht_notwendig_returns_abgeschlossen(self):
        saga = SagaInstanz("SI-T", "test", "T")
        saga.schritte = [
            KompensationsSchritt("SK-1", "SI-T", "S1", KompensationsTyp.RUECKGAENGIG, KompensationsStatus.NICHT_NOTWENDIG),
            KompensationsSchritt("SK-2", "SI-T", "S2", KompensationsTyp.AUSGLEICH, KompensationsStatus.NICHT_NOTWENDIG),
        ]
        assert saga.berechne_saga_status() == SagaStatus.ABGESCHLOSSEN

    def test_mix_abgeschlossen_nicht_notwendig_returns_kompensiert(self):
        saga = SagaInstanz("SI-T", "test", "T")
        saga.schritte = [
            KompensationsSchritt("SK-1", "SI-T", "S1", KompensationsTyp.RUECKGAENGIG, KompensationsStatus.ABGESCHLOSSEN),
            KompensationsSchritt("SK-2", "SI-T", "S2", KompensationsTyp.AUSGLEICH, KompensationsStatus.NICHT_NOTWENDIG),
        ]
        assert saga.berechne_saga_status() == SagaStatus.KOMPENSIERT

    def test_all_abgeschlossen_returns_kompensiert(self):
        saga = SagaInstanz("SI-T", "test", "T")
        saga.schritte = [
            KompensationsSchritt("SK-1", "SI-T", "S1", KompensationsTyp.RUECKGAENGIG, KompensationsStatus.ABGESCHLOSSEN),
            KompensationsSchritt("SK-2", "SI-T", "S2", KompensationsTyp.AUSGLEICH, KompensationsStatus.ABGESCHLOSSEN),
        ]
        assert saga.berechne_saga_status() == SagaStatus.KOMPENSIERT

    def test_single_abgeschlossen_returns_kompensiert(self):
        saga = SagaInstanz("SI-T", "test", "T")
        saga.schritte = [
            KompensationsSchritt("SK-1", "SI-T", "S1", KompensationsTyp.RUECKGAENGIG, KompensationsStatus.ABGESCHLOSSEN),
        ]
        assert saga.berechne_saga_status() == SagaStatus.KOMPENSIERT

    def test_ausstehend_only_returns_kompensiert(self):
        # all steps are AUSSTEHEND (not LAUFEND/FEHLGESCHLAGEN/NICHT_NOTWENDIG) → falls through to KOMPENSIERT
        saga = SagaInstanz("SI-T", "test", "T")
        saga.schritte = [
            KompensationsSchritt("SK-1", "SI-T", "S1", KompensationsTyp.RUECKGAENGIG, KompensationsStatus.AUSSTEHEND),
        ]
        # AUSSTEHEND is not LAUFEND, not FEHLGESCHLAGEN, not all NICHT_NOTWENDIG → KOMPENSIERT
        assert saga.berechne_saga_status() == SagaStatus.KOMPENSIERT


# ─────────────────────────────────────────────────────────────────────────────
# erstelle_kompensations_plan
# ─────────────────────────────────────────────────────────────────────────────

class TestErstelle_KompensationsPlan:
    @pytest.fixture
    def standard_definitionen(self):
        return [
            {"schritt_id": "SK-A", "schritt_name": "Schritt A", "kompensations_typ": "RUECKGAENGIG"},
            {"schritt_id": "SK-B", "schritt_name": "Schritt B", "kompensations_typ": "AUSGLEICH"},
            {"schritt_id": "SK-C", "schritt_name": "Schritt C", "kompensations_typ": "ABBRECHEN"},
        ]

    def test_returns_saga_instanz(self, standard_definitionen):
        saga = erstelle_kompensations_plan("SI-NEW", "test_typ", "TENANT-X", standard_definitionen)
        assert isinstance(saga, SagaInstanz)

    def test_saga_id_set(self, standard_definitionen):
        saga = erstelle_kompensations_plan("SI-NEW", "test_typ", "TENANT-X", standard_definitionen)
        assert saga.saga_id == "SI-NEW"

    def test_saga_typ_set(self, standard_definitionen):
        saga = erstelle_kompensations_plan("SI-NEW", "test_typ", "TENANT-X", standard_definitionen)
        assert saga.saga_typ == "test_typ"

    def test_tenant_id_set(self, standard_definitionen):
        saga = erstelle_kompensations_plan("SI-NEW", "test_typ", "TENANT-X", standard_definitionen)
        assert saga.tenant_id == "TENANT-X"

    def test_schritte_count(self, standard_definitionen):
        saga = erstelle_kompensations_plan("SI-NEW", "test_typ", "TENANT-X", standard_definitionen)
        assert len(saga.schritte) == 3

    def test_all_schritte_ausstehend(self, standard_definitionen):
        saga = erstelle_kompensations_plan("SI-NEW", "test_typ", "TENANT-X", standard_definitionen)
        for s in saga.schritte:
            assert s.status == KompensationsStatus.AUSSTEHEND

    def test_saga_status_laufend_by_default(self, standard_definitionen):
        saga = erstelle_kompensations_plan("SI-NEW", "test_typ", "TENANT-X", standard_definitionen)
        assert saga.status == SagaStatus.LAUFEND

    def test_schritt_ids_correct(self, standard_definitionen):
        saga = erstelle_kompensations_plan("SI-NEW", "test_typ", "TENANT-X", standard_definitionen)
        ids = [s.schritt_id for s in saga.schritte]
        assert "SK-A" in ids
        assert "SK-B" in ids
        assert "SK-C" in ids

    def test_schritt_saga_id_set(self, standard_definitionen):
        saga = erstelle_kompensations_plan("SI-NEW", "test_typ", "TENANT-X", standard_definitionen)
        for s in saga.schritte:
            assert s.saga_id == "SI-NEW"

    def test_kompensations_typ_parsed(self, standard_definitionen):
        saga = erstelle_kompensations_plan("SI-NEW", "test_typ", "TENANT-X", standard_definitionen)
        sk_a = next(s for s in saga.schritte if s.schritt_id == "SK-A")
        assert sk_a.kompensations_typ == KompensationsTyp.RUECKGAENGIG

    def test_empty_definitionen(self):
        saga = erstelle_kompensations_plan("SI-EMPTY", "typ", "TENANT-Y", [])
        assert saga.schritte == []
        assert saga.status == SagaStatus.LAUFEND


# ─────────────────────────────────────────────────────────────────────────────
# get_default_saga_instanzen
# ─────────────────────────────────────────────────────────────────────────────

class TestGetDefaultSagaInstanzen:
    @pytest.fixture
    def sagas(self):
        return get_default_saga_instanzen()

    def test_returns_4_instanzen(self, sagas):
        assert len(sagas) == 4

    def test_all_are_saga_instanz(self, sagas):
        for s in sagas:
            assert isinstance(s, SagaInstanz)

    def test_si001_exists(self, sagas):
        ids = [s.saga_id for s in sagas]
        assert "SI-001" in ids

    def test_si002_exists(self, sagas):
        ids = [s.saga_id for s in sagas]
        assert "SI-002" in ids

    def test_si003_exists(self, sagas):
        ids = [s.saga_id for s in sagas]
        assert "SI-003" in ids

    def test_si004_exists(self, sagas):
        ids = [s.saga_id for s in sagas]
        assert "SI-004" in ids

    def test_si001_status_abgeschlossen(self, sagas):
        si1 = next(s for s in sagas if s.saga_id == "SI-001")
        assert si1.status == SagaStatus.ABGESCHLOSSEN

    def test_si002_status_kompensiert(self, sagas):
        si2 = next(s for s in sagas if s.saga_id == "SI-002")
        assert si2.status == SagaStatus.KOMPENSIERT

    def test_si003_status_laufend(self, sagas):
        si3 = next(s for s in sagas if s.saga_id == "SI-003")
        assert si3.status == SagaStatus.LAUFEND

    def test_si004_status_fehlgeschlagen(self, sagas):
        si4 = next(s for s in sagas if s.saga_id == "SI-004")
        assert si4.status == SagaStatus.FEHLGESCHLAGEN

    def test_si001_tenant_a(self, sagas):
        si1 = next(s for s in sagas if s.saga_id == "SI-001")
        assert si1.tenant_id == "TENANT-A"

    def test_si003_tenant_b(self, sagas):
        si3 = next(s for s in sagas if s.saga_id == "SI-003")
        assert si3.tenant_id == "TENANT-B"

    def test_si001_has_2_schritte(self, sagas):
        si1 = next(s for s in sagas if s.saga_id == "SI-001")
        assert len(si1.schritte) == 2

    def test_si002_has_2_schritte(self, sagas):
        si2 = next(s for s in sagas if s.saga_id == "SI-002")
        assert len(si2.schritte) == 2

    def test_si001_offene_kompensationen_zero(self, sagas):
        si1 = next(s for s in sagas if s.saga_id == "SI-001")
        assert len(si1.offene_kompensationen()) == 0

    def test_si003_offene_kompensationen_one(self, sagas):
        si3 = next(s for s in sagas if s.saga_id == "SI-003")
        assert len(si3.offene_kompensationen()) == 1

    def test_si002_all_schritte_abgeschlossen(self, sagas):
        si2 = next(s for s in sagas if s.saga_id == "SI-002")
        for s in si2.schritte:
            assert s.ist_abgeschlossen

    def test_si004_sk007_fehlgeschlagen_with_message(self, sagas):
        si4 = next(s for s in sagas if s.saga_id == "SI-004")
        sk7 = next(s for s in si4.schritte if s.schritt_id == "SK-007")
        assert sk7.status == KompensationsStatus.FEHLGESCHLAGEN
        assert sk7.fehler_nachricht != ""

    def test_si003_sk005_laufend(self, sagas):
        si3 = next(s for s in sagas if s.saga_id == "SI-003")
        sk5 = next(s for s in si3.schritte if s.schritt_id == "SK-005")
        assert sk5.status == KompensationsStatus.LAUFEND

    def test_si003_sk006_ausstehend(self, sagas):
        si3 = next(s for s in sagas if s.saga_id == "SI-003")
        sk6 = next(s for s in si3.schritte if s.schritt_id == "SK-006")
        assert sk6.status == KompensationsStatus.AUSSTEHEND

    def test_si001_berechne_saga_status_abgeschlossen(self, sagas):
        si1 = next(s for s in sagas if s.saga_id == "SI-001")
        assert si1.berechne_saga_status() == SagaStatus.ABGESCHLOSSEN

    def test_si002_berechne_saga_status_kompensiert(self, sagas):
        si2 = next(s for s in sagas if s.saga_id == "SI-002")
        assert si2.berechne_saga_status() == SagaStatus.KOMPENSIERT

    def test_si003_berechne_saga_status_laufend(self, sagas):
        si3 = next(s for s in sagas if s.saga_id == "SI-003")
        assert si3.berechne_saga_status() == SagaStatus.LAUFEND

    def test_si004_berechne_saga_status_fehlgeschlagen(self, sagas):
        si4 = next(s for s in sagas if s.saga_id == "SI-004")
        assert si4.berechne_saga_status() == SagaStatus.FEHLGESCHLAGEN
