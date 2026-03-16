"""Wave 61: Tenant Quota Management + Workflow Pause/Resume Contracts — 130+ tests."""
import pytest
from datetime import datetime, timedelta

from app.core.process_quota_contracts import (
    QuotaTyp, QuotaStatus, QuotaAktionsBei,
    QuotaRegel, TenantQuotaVerbrauch, QuotaUebersicht,
    get_default_quota_uebersicht,
)
from app.core.workflow_pause_contracts import (
    PauseGrund, PauseStatus, ResumeAusloeser,
    WorkflowPause, PauseVerlauf,
    get_default_pause_verlaeufe,
)

NOW = datetime(2026, 3, 16, 10, 0, 0)

# ---------------------------------------------------------------------------
# QuotaTyp enum
# ---------------------------------------------------------------------------

class TestQuotaTyp:
    def test_api_anfragen_value(self):
        assert QuotaTyp.API_ANFRAGEN == "API_ANFRAGEN"

    def test_speicher_mb_value(self):
        assert QuotaTyp.SPEICHER_MB == "SPEICHER_MB"

    def test_benutzer_value(self):
        assert QuotaTyp.BENUTZER == "BENUTZER"

    def test_dokumente_value(self):
        assert QuotaTyp.DOKUMENTE == "DOKUMENTE"

    def test_workflow_instanzen_value(self):
        assert QuotaTyp.WORKFLOW_INSTANZEN == "WORKFLOW_INSTANZEN"

    def test_five_types_total(self):
        assert len(list(QuotaTyp)) == 5


# ---------------------------------------------------------------------------
# QuotaStatus enum
# ---------------------------------------------------------------------------

class TestQuotaStatus:
    def test_normal_value(self):
        assert QuotaStatus.NORMAL == "NORMAL"

    def test_warnung_value(self):
        assert QuotaStatus.WARNUNG == "WARNUNG"

    def test_kritisch_value(self):
        assert QuotaStatus.KRITISCH == "KRITISCH"

    def test_erschoepft_value(self):
        assert QuotaStatus.ERSCHOEPFT == "ERSCHOEPFT"

    def test_four_statuses_total(self):
        assert len(list(QuotaStatus)) == 4


# ---------------------------------------------------------------------------
# QuotaAktionsBei enum
# ---------------------------------------------------------------------------

class TestQuotaAktionsBei:
    def test_warnung_value(self):
        assert QuotaAktionsBei.WARNUNG == "WARNUNG"

    def test_kritisch_value(self):
        assert QuotaAktionsBei.KRITISCH == "KRITISCH"

    def test_erschoepft_value(self):
        assert QuotaAktionsBei.ERSCHOEPFT == "ERSCHOEPFT"


# ---------------------------------------------------------------------------
# QuotaRegel.berechne_status()
# ---------------------------------------------------------------------------

class TestQuotaRegelBerechneStatus:
    def _regel(self, limit=100.0, warn=80.0, krit=95.0):
        return QuotaRegel("R-TEST", QuotaTyp.API_ANFRAGEN, limit, warn, krit)

    def test_zero_percent_normal(self):
        assert self._regel().berechne_status(0.0) == QuotaStatus.NORMAL

    def test_below_warning_normal(self):
        assert self._regel().berechne_status(79.9) == QuotaStatus.NORMAL

    def test_exactly_80_warnung(self):
        assert self._regel().berechne_status(80.0) == QuotaStatus.WARNUNG

    def test_81_warnung(self):
        assert self._regel().berechne_status(81.0) == QuotaStatus.WARNUNG

    def test_94_9_warnung(self):
        assert self._regel().berechne_status(94.9) == QuotaStatus.WARNUNG

    def test_exactly_95_kritisch(self):
        assert self._regel().berechne_status(95.0) == QuotaStatus.KRITISCH

    def test_96_kritisch(self):
        assert self._regel().berechne_status(96.0) == QuotaStatus.KRITISCH

    def test_99_9_kritisch(self):
        assert self._regel().berechne_status(99.9) == QuotaStatus.KRITISCH

    def test_exactly_100_erschoepft(self):
        assert self._regel().berechne_status(100.0) == QuotaStatus.ERSCHOEPFT

    def test_150_percent_erschoepft(self):
        assert self._regel().berechne_status(150.0) == QuotaStatus.ERSCHOEPFT

    def test_200_percent_erschoepft(self):
        assert self._regel().berechne_status(200.0) == QuotaStatus.ERSCHOEPFT

    def test_limit_zero_returns_normal(self):
        regel = QuotaRegel("R-ZERO", QuotaTyp.API_ANFRAGEN, 0.0)
        assert regel.berechne_status(999.0) == QuotaStatus.NORMAL

    def test_limit_negative_returns_normal(self):
        regel = QuotaRegel("R-NEG", QuotaTyp.API_ANFRAGEN, -1.0)
        assert regel.berechne_status(50.0) == QuotaStatus.NORMAL

    def test_custom_thresholds_warn_at_50(self):
        regel = QuotaRegel("R-CUSTOM", QuotaTyp.BENUTZER, 100.0, 50.0, 70.0)
        assert regel.berechne_status(50.0) == QuotaStatus.WARNUNG

    def test_custom_thresholds_krit_at_70(self):
        regel = QuotaRegel("R-CUSTOM", QuotaTyp.BENUTZER, 100.0, 50.0, 70.0)
        assert regel.berechne_status(70.0) == QuotaStatus.KRITISCH

    def test_custom_thresholds_normal_below_50(self):
        regel = QuotaRegel("R-CUSTOM", QuotaTyp.BENUTZER, 100.0, 50.0, 70.0)
        assert regel.berechne_status(49.9) == QuotaStatus.NORMAL

    def test_real_limit_10000_75pct_normal(self):
        regel = QuotaRegel("QR-001", QuotaTyp.API_ANFRAGEN, 10000.0)
        assert regel.berechne_status(7500.0) == QuotaStatus.NORMAL

    def test_real_limit_51200_82pct_warnung(self):
        regel = QuotaRegel("QR-002", QuotaTyp.SPEICHER_MB, 51200.0)
        assert regel.berechne_status(42000.0) == QuotaStatus.WARNUNG

    def test_real_limit_50_96pct_kritisch(self):
        regel = QuotaRegel("QR-003", QuotaTyp.BENUTZER, 50.0)
        assert regel.berechne_status(48.0) == QuotaStatus.KRITISCH

    def test_real_limit_100000_over100_erschoepft(self):
        regel = QuotaRegel("QR-004", QuotaTyp.DOKUMENTE, 100000.0)
        assert regel.berechne_status(100500.0) == QuotaStatus.ERSCHOEPFT

    def test_real_limit_1000_50pct_normal(self):
        regel = QuotaRegel("QR-005", QuotaTyp.WORKFLOW_INSTANZEN, 1000.0)
        assert regel.berechne_status(500.0) == QuotaStatus.NORMAL


# ---------------------------------------------------------------------------
# QuotaRegel.verfuegbar()
# ---------------------------------------------------------------------------

class TestQuotaRegelVerfuegbar:
    def _regel(self, limit=100.0):
        return QuotaRegel("R-V", QuotaTyp.API_ANFRAGEN, limit)

    def test_verfuegbar_basic(self):
        assert self._regel(100.0).verfuegbar(30.0) == 70.0

    def test_verfuegbar_zero_verbrauch(self):
        assert self._regel(100.0).verfuegbar(0.0) == 100.0

    def test_verfuegbar_at_limit(self):
        assert self._regel(100.0).verfuegbar(100.0) == 0.0

    def test_verfuegbar_over_limit_no_negative(self):
        assert self._regel(100.0).verfuegbar(150.0) == 0.0

    def test_verfuegbar_far_over_limit_no_negative(self):
        assert self._regel(100.0).verfuegbar(999.0) == 0.0

    def test_verfuegbar_large_limit(self):
        r = self._regel(51200.0)
        assert r.verfuegbar(42000.0) == pytest.approx(9200.0)

    def test_verfuegbar_never_negative(self):
        r = self._regel(50.0)
        result = r.verfuegbar(1000.0)
        assert result >= 0.0


# ---------------------------------------------------------------------------
# QuotaUebersicht.status_fuer_typ()
# ---------------------------------------------------------------------------

class TestQuotaUebersichtStatusFuerTyp:
    def _build(self, regeln, verbraeuche):
        u = QuotaUebersicht("U-TEST", "T-TEST")
        u.regeln = regeln
        u.verbraeuche = verbraeuche
        return u

    def test_no_regel_returns_normal(self):
        u = self._build([], [])
        assert u.status_fuer_typ(QuotaTyp.API_ANFRAGEN) == QuotaStatus.NORMAL

    def test_no_verbrauch_returns_normal_for_regel(self):
        u = self._build(
            [QuotaRegel("R1", QuotaTyp.API_ANFRAGEN, 100.0)],
            []
        )
        assert u.status_fuer_typ(QuotaTyp.API_ANFRAGEN) == QuotaStatus.NORMAL

    def test_warnung_status_returned(self):
        u = self._build(
            [QuotaRegel("R1", QuotaTyp.SPEICHER_MB, 100.0)],
            [TenantQuotaVerbrauch("T", QuotaTyp.SPEICHER_MB, 82.0, NOW)]
        )
        assert u.status_fuer_typ(QuotaTyp.SPEICHER_MB) == QuotaStatus.WARNUNG

    def test_kritisch_status_returned(self):
        u = self._build(
            [QuotaRegel("R1", QuotaTyp.BENUTZER, 100.0)],
            [TenantQuotaVerbrauch("T", QuotaTyp.BENUTZER, 96.0, NOW)]
        )
        assert u.status_fuer_typ(QuotaTyp.BENUTZER) == QuotaStatus.KRITISCH

    def test_erschoepft_status_returned(self):
        u = self._build(
            [QuotaRegel("R1", QuotaTyp.DOKUMENTE, 100.0)],
            [TenantQuotaVerbrauch("T", QuotaTyp.DOKUMENTE, 105.0, NOW)]
        )
        assert u.status_fuer_typ(QuotaTyp.DOKUMENTE) == QuotaStatus.ERSCHOEPFT

    def test_different_type_not_mixed(self):
        u = self._build(
            [QuotaRegel("R1", QuotaTyp.SPEICHER_MB, 100.0)],
            [TenantQuotaVerbrauch("T", QuotaTyp.API_ANFRAGEN, 99.0, NOW)]
        )
        # No verbrauch for SPEICHER_MB → 0 → NORMAL
        assert u.status_fuer_typ(QuotaTyp.SPEICHER_MB) == QuotaStatus.NORMAL


# ---------------------------------------------------------------------------
# QuotaUebersicht.kritische_quotas()
# ---------------------------------------------------------------------------

class TestQuotaUebersichtKritischeQuotas:
    def test_empty_returns_empty(self):
        u = QuotaUebersicht("U-E", "T-E")
        assert u.kritische_quotas() == []

    def test_only_normal_returns_empty(self):
        u = QuotaUebersicht("U-N", "T-N")
        u.regeln = [QuotaRegel("R1", QuotaTyp.API_ANFRAGEN, 100.0)]
        u.verbraeuche = [TenantQuotaVerbrauch("T", QuotaTyp.API_ANFRAGEN, 10.0, NOW)]
        assert u.kritische_quotas() == []

    def test_kritisch_included(self):
        u = QuotaUebersicht("U-K", "T-K")
        u.regeln = [QuotaRegel("R1", QuotaTyp.BENUTZER, 100.0)]
        u.verbraeuche = [TenantQuotaVerbrauch("T", QuotaTyp.BENUTZER, 96.0, NOW)]
        assert QuotaTyp.BENUTZER in u.kritische_quotas()

    def test_erschoepft_included(self):
        u = QuotaUebersicht("U-E2", "T-E2")
        u.regeln = [QuotaRegel("R1", QuotaTyp.DOKUMENTE, 100.0)]
        u.verbraeuche = [TenantQuotaVerbrauch("T", QuotaTyp.DOKUMENTE, 110.0, NOW)]
        assert QuotaTyp.DOKUMENTE in u.kritische_quotas()

    def test_warnung_not_included(self):
        u = QuotaUebersicht("U-W", "T-W")
        u.regeln = [QuotaRegel("R1", QuotaTyp.SPEICHER_MB, 100.0)]
        u.verbraeuche = [TenantQuotaVerbrauch("T", QuotaTyp.SPEICHER_MB, 82.0, NOW)]
        assert QuotaTyp.SPEICHER_MB not in u.kritische_quotas()


# ---------------------------------------------------------------------------
# Default QuotaUebersicht (reference values)
# ---------------------------------------------------------------------------

class TestDefaultQuotaUebersicht:
    def setup_method(self):
        self.u = get_default_quota_uebersicht()

    def test_uebersicht_id(self):
        assert self.u.uebersicht_id == "QU-001"

    def test_tenant_id(self):
        assert self.u.tenant_id == "TENANT-A"

    def test_five_regeln(self):
        assert len(self.u.regeln) == 5

    def test_five_verbraeuche(self):
        assert len(self.u.verbraeuche) == 5

    def test_api_anfragen_75pct_normal(self):
        assert self.u.status_fuer_typ(QuotaTyp.API_ANFRAGEN) == QuotaStatus.NORMAL

    def test_speicher_mb_82pct_warnung(self):
        assert self.u.status_fuer_typ(QuotaTyp.SPEICHER_MB) == QuotaStatus.WARNUNG

    def test_benutzer_96pct_kritisch(self):
        assert self.u.status_fuer_typ(QuotaTyp.BENUTZER) == QuotaStatus.KRITISCH

    def test_dokumente_over100pct_erschoepft(self):
        assert self.u.status_fuer_typ(QuotaTyp.DOKUMENTE) == QuotaStatus.ERSCHOEPFT

    def test_workflow_instanzen_50pct_normal(self):
        assert self.u.status_fuer_typ(QuotaTyp.WORKFLOW_INSTANZEN) == QuotaStatus.NORMAL

    def test_kritische_quotas_contains_benutzer(self):
        krit = self.u.kritische_quotas()
        assert QuotaTyp.BENUTZER in krit

    def test_kritische_quotas_contains_dokumente(self):
        krit = self.u.kritische_quotas()
        assert QuotaTyp.DOKUMENTE in krit

    def test_kritische_quotas_not_contains_api_anfragen(self):
        krit = self.u.kritische_quotas()
        assert QuotaTyp.API_ANFRAGEN not in krit

    def test_kritische_quotas_not_contains_speicher_mb(self):
        krit = self.u.kritische_quotas()
        assert QuotaTyp.SPEICHER_MB not in krit

    def test_kritische_quotas_not_contains_workflow_instanzen(self):
        krit = self.u.kritische_quotas()
        assert QuotaTyp.WORKFLOW_INSTANZEN not in krit

    def test_kritische_quotas_count_two(self):
        assert len(self.u.kritische_quotas()) == 2

    def test_regel_api_limit(self):
        r = next(r for r in self.u.regeln if r.quota_typ == QuotaTyp.API_ANFRAGEN)
        assert r.limit == 10000.0

    def test_regel_speicher_limit(self):
        r = next(r for r in self.u.regeln if r.quota_typ == QuotaTyp.SPEICHER_MB)
        assert r.limit == 51200.0

    def test_regel_benutzer_limit(self):
        r = next(r for r in self.u.regeln if r.quota_typ == QuotaTyp.BENUTZER)
        assert r.limit == 50.0

    def test_verfuegbar_api_anfragen(self):
        r = next(r for r in self.u.regeln if r.quota_typ == QuotaTyp.API_ANFRAGEN)
        assert r.verfuegbar(7500.0) == pytest.approx(2500.0)

    def test_verfuegbar_benutzer(self):
        r = next(r for r in self.u.regeln if r.quota_typ == QuotaTyp.BENUTZER)
        assert r.verfuegbar(48.0) == pytest.approx(2.0)

    def test_verfuegbar_dokumente_zero(self):
        r = next(r for r in self.u.regeln if r.quota_typ == QuotaTyp.DOKUMENTE)
        assert r.verfuegbar(100500.0) == 0.0


# ===========================================================================
# PAUSE TESTS
# ===========================================================================

# ---------------------------------------------------------------------------
# PauseGrund enum
# ---------------------------------------------------------------------------

class TestPauseGrund:
    def test_benutzer_angefragt(self):
        assert PauseGrund.BENUTZER_ANGEFRAGT == "BENUTZER_ANGEFRAGT"

    def test_externe_abhaengigkeit(self):
        assert PauseGrund.EXTERNE_ABHAENGIGKEIT == "EXTERNE_ABHAENGIGKEIT"

    def test_ressource_nicht_verfuegbar(self):
        assert PauseGrund.RESSOURCE_NICHT_VERFUEGBAR == "RESSOURCE_NICHT_VERFUEGBAR"

    def test_wartung(self):
        assert PauseGrund.WARTUNG == "WARTUNG"

    def test_fehler_untersuchung(self):
        assert PauseGrund.FEHLER_UNTERSUCHUNG == "FEHLER_UNTERSUCHUNG"

    def test_genehmigung_ausstehend(self):
        assert PauseGrund.GENEHMIGUNG_AUSSTEHEND == "GENEHMIGUNG_AUSSTEHEND"

    def test_six_gruende_total(self):
        assert len(list(PauseGrund)) == 6


# ---------------------------------------------------------------------------
# PauseStatus enum
# ---------------------------------------------------------------------------

class TestPauseStatus:
    def test_aktiv(self):
        assert PauseStatus.AKTIV == "AKTIV"

    def test_fortgesetzt(self):
        assert PauseStatus.FORTGESETZT == "FORTGESETZT"

    def test_abgebrochen(self):
        assert PauseStatus.ABGEBROCHEN == "ABGEBROCHEN"

    def test_three_statuses_total(self):
        assert len(list(PauseStatus)) == 3


# ---------------------------------------------------------------------------
# ResumeAusloeser enum
# ---------------------------------------------------------------------------

class TestResumeAusloeser:
    def test_manuell(self):
        assert ResumeAusloeser.MANUELL == "MANUELL"

    def test_automatisch(self):
        assert ResumeAusloeser.AUTOMATISCH == "AUTOMATISCH"

    def test_signal(self):
        assert ResumeAusloeser.SIGNAL == "SIGNAL"

    def test_admin(self):
        assert ResumeAusloeser.ADMIN == "ADMIN"

    def test_four_ausloeser_total(self):
        assert len(list(ResumeAusloeser)) == 4


# ---------------------------------------------------------------------------
# WorkflowPause.ist_aktiv()
# ---------------------------------------------------------------------------

class TestWorkflowPauseIstAktiv:
    def test_aktiv_status_true(self):
        p = WorkflowPause("P1", "WI-1", PauseGrund.WARTUNG, PauseStatus.AKTIV, NOW)
        assert p.ist_aktiv() is True

    def test_fortgesetzt_status_false(self):
        p = WorkflowPause("P2", "WI-1", PauseGrund.WARTUNG, PauseStatus.FORTGESETZT, NOW)
        assert p.ist_aktiv() is False

    def test_abgebrochen_status_false(self):
        p = WorkflowPause("P3", "WI-1", PauseGrund.WARTUNG, PauseStatus.ABGEBROCHEN, NOW)
        assert p.ist_aktiv() is False


# ---------------------------------------------------------------------------
# WorkflowPause.ist_ueberfaellig()
# ---------------------------------------------------------------------------

class TestWorkflowPauseIstUeberfaellig:
    def test_fortgesetzt_not_ueberfaellig(self):
        p = WorkflowPause("P1", "WI-1", PauseGrund.WARTUNG, PauseStatus.FORTGESETZT,
                          NOW - timedelta(hours=3), 60)
        assert p.ist_ueberfaellig(NOW) is False

    def test_abgebrochen_not_ueberfaellig(self):
        p = WorkflowPause("P2", "WI-1", PauseGrund.WARTUNG, PauseStatus.ABGEBROCHEN,
                          NOW - timedelta(hours=3), 60)
        assert p.ist_ueberfaellig(NOW) is False

    def test_aktiv_no_max_not_ueberfaellig(self):
        p = WorkflowPause("P3", "WI-1", PauseGrund.WARTUNG, PauseStatus.AKTIV,
                          NOW - timedelta(hours=100), None)
        assert p.ist_ueberfaellig(NOW) is False

    def test_aktiv_within_limit_not_ueberfaellig(self):
        p = WorkflowPause("P4", "WI-1", PauseGrund.WARTUNG, PauseStatus.AKTIV,
                          NOW - timedelta(minutes=30), 60)
        assert p.ist_ueberfaellig(NOW) is False

    def test_aktiv_exactly_at_limit_not_ueberfaellig(self):
        p = WorkflowPause("P5", "WI-1", PauseGrund.WARTUNG, PauseStatus.AKTIV,
                          NOW - timedelta(minutes=60), 60)
        # 60 min elapsed, max=60 → not strictly greater
        assert p.ist_ueberfaellig(NOW) is False

    def test_aktiv_exceeded_limit_ueberfaellig(self):
        p = WorkflowPause("P6", "WI-1", PauseGrund.WARTUNG, PauseStatus.AKTIV,
                          NOW - timedelta(minutes=90), 60)
        assert p.ist_ueberfaellig(NOW) is True

    def test_aktiv_far_exceeded_ueberfaellig(self):
        p = WorkflowPause("P7", "WI-1", PauseGrund.WARTUNG, PauseStatus.AKTIV,
                          NOW - timedelta(hours=5), 60)
        assert p.ist_ueberfaellig(NOW) is True


# ---------------------------------------------------------------------------
# WorkflowPause.pause_dauer_minuten()
# ---------------------------------------------------------------------------

class TestWorkflowPauseDauerMinuten:
    def test_abgebrochen_returns_zero(self):
        p = WorkflowPause("P1", "WI-1", PauseGrund.WARTUNG, PauseStatus.ABGEBROCHEN,
                          NOW - timedelta(hours=2))
        assert p.pause_dauer_minuten(NOW) == 0.0

    def test_fortgesetzt_uses_fortgesetzt_am(self):
        pausiert = NOW - timedelta(hours=2)
        fortgesetzt = NOW - timedelta(hours=1)
        p = WorkflowPause("P2", "WI-1", PauseGrund.WARTUNG, PauseStatus.FORTGESETZT,
                          pausiert, 60, fortgesetzt)
        assert p.pause_dauer_minuten(NOW) == pytest.approx(60.0)

    def test_aktiv_uses_jetzt(self):
        pausiert = NOW - timedelta(minutes=45)
        p = WorkflowPause("P3", "WI-1", PauseGrund.WARTUNG, PauseStatus.AKTIV,
                          pausiert)
        assert p.pause_dauer_minuten(NOW) == pytest.approx(45.0)

    def test_aktiv_90_minutes(self):
        pausiert = NOW - timedelta(minutes=90)
        p = WorkflowPause("P4", "WI-1", PauseGrund.EXTERNE_ABHAENGIGKEIT, PauseStatus.AKTIV,
                          pausiert, 60)
        assert p.pause_dauer_minuten(NOW) == pytest.approx(90.0)

    def test_fortgesetzt_2h_pause_equals_120_min(self):
        pausiert = NOW - timedelta(hours=3)
        fortgesetzt = NOW - timedelta(hours=1)
        p = WorkflowPause("P5", "WI-1", PauseGrund.WARTUNG, PauseStatus.FORTGESETZT,
                          pausiert, None, fortgesetzt)
        assert p.pause_dauer_minuten(NOW) == pytest.approx(120.0)

    def test_fortgesetzt_no_fortgesetzt_am_falls_back_to_jetzt(self):
        # FORTGESETZT but fortgesetzt_am is None → use jetzt
        pausiert = NOW - timedelta(minutes=30)
        p = WorkflowPause("P6", "WI-1", PauseGrund.WARTUNG, PauseStatus.FORTGESETZT,
                          pausiert, None, None)
        assert p.pause_dauer_minuten(NOW) == pytest.approx(30.0)


# ---------------------------------------------------------------------------
# PauseVerlauf.aktive_pause()
# ---------------------------------------------------------------------------

class TestPauseVerlaufAktivePause:
    def test_none_when_no_pausen(self):
        v = PauseVerlauf("V1", "WI-1")
        assert v.aktive_pause() is None

    def test_none_when_all_fortgesetzt(self):
        v = PauseVerlauf("V2", "WI-1")
        v.pausen = [
            WorkflowPause("P1", "WI-1", PauseGrund.WARTUNG, PauseStatus.FORTGESETZT, NOW),
        ]
        assert v.aktive_pause() is None

    def test_none_when_all_abgebrochen(self):
        v = PauseVerlauf("V3", "WI-1")
        v.pausen = [
            WorkflowPause("P1", "WI-1", PauseGrund.WARTUNG, PauseStatus.ABGEBROCHEN, NOW),
        ]
        assert v.aktive_pause() is None

    def test_returns_first_aktiv(self):
        v = PauseVerlauf("V4", "WI-1")
        p1 = WorkflowPause("P1", "WI-1", PauseGrund.WARTUNG, PauseStatus.AKTIV, NOW)
        p2 = WorkflowPause("P2", "WI-1", PauseGrund.WARTUNG, PauseStatus.AKTIV, NOW)
        v.pausen = [p1, p2]
        assert v.aktive_pause() is p1

    def test_returns_aktiv_among_mixed(self):
        v = PauseVerlauf("V5", "WI-1")
        p1 = WorkflowPause("P1", "WI-1", PauseGrund.WARTUNG, PauseStatus.FORTGESETZT, NOW)
        p2 = WorkflowPause("P2", "WI-1", PauseGrund.WARTUNG, PauseStatus.AKTIV, NOW)
        v.pausen = [p1, p2]
        assert v.aktive_pause() is p2


# ---------------------------------------------------------------------------
# PauseVerlauf.gesamt_pause_minuten()
# ---------------------------------------------------------------------------

class TestPauseVerlaufGesamtPauseMinuten:
    def test_empty_returns_zero(self):
        v = PauseVerlauf("V1", "WI-1")
        assert v.gesamt_pause_minuten(NOW) == 0.0

    def test_abgebrochen_excluded(self):
        v = PauseVerlauf("V2", "WI-1")
        v.pausen = [
            WorkflowPause("P1", "WI-1", PauseGrund.WARTUNG, PauseStatus.ABGEBROCHEN,
                          NOW - timedelta(hours=2)),
        ]
        assert v.gesamt_pause_minuten(NOW) == 0.0

    def test_fortgesetzt_included(self):
        pausiert = NOW - timedelta(hours=2)
        fortgesetzt = NOW - timedelta(hours=1)
        v = PauseVerlauf("V3", "WI-1")
        v.pausen = [
            WorkflowPause("P1", "WI-1", PauseGrund.WARTUNG, PauseStatus.FORTGESETZT,
                          pausiert, None, fortgesetzt),
        ]
        assert v.gesamt_pause_minuten(NOW) == pytest.approx(60.0)

    def test_aktiv_included(self):
        v = PauseVerlauf("V4", "WI-1")
        v.pausen = [
            WorkflowPause("P1", "WI-1", PauseGrund.WARTUNG, PauseStatus.AKTIV,
                          NOW - timedelta(minutes=45)),
        ]
        assert v.gesamt_pause_minuten(NOW) == pytest.approx(45.0)

    def test_mixed_sum_excludes_abgebrochen(self):
        v = PauseVerlauf("V5", "WI-1")
        # 60 min fortgesetzt + 45 min aktiv + 0 abgebrochen = 105
        v.pausen = [
            WorkflowPause("P1", "WI-1", PauseGrund.WARTUNG, PauseStatus.FORTGESETZT,
                          NOW - timedelta(hours=2), None, NOW - timedelta(hours=1)),
            WorkflowPause("P2", "WI-1", PauseGrund.WARTUNG, PauseStatus.AKTIV,
                          NOW - timedelta(minutes=45)),
            WorkflowPause("P3", "WI-1", PauseGrund.WARTUNG, PauseStatus.ABGEBROCHEN,
                          NOW - timedelta(hours=5)),
        ]
        assert v.gesamt_pause_minuten(NOW) == pytest.approx(105.0)


# ---------------------------------------------------------------------------
# PauseVerlauf.ueberfaellige_pausen()
# ---------------------------------------------------------------------------

class TestPauseVerlaufUeberfaelligePausen:
    def test_empty_returns_empty(self):
        v = PauseVerlauf("V1", "WI-1")
        assert v.ueberfaellige_pausen(NOW) == []

    def test_no_ueberfaellige(self):
        v = PauseVerlauf("V2", "WI-1")
        v.pausen = [
            WorkflowPause("P1", "WI-1", PauseGrund.WARTUNG, PauseStatus.AKTIV,
                          NOW - timedelta(minutes=30), 60),
        ]
        assert v.ueberfaellige_pausen(NOW) == []

    def test_one_ueberfaellig(self):
        v = PauseVerlauf("V3", "WI-1")
        p = WorkflowPause("P1", "WI-1", PauseGrund.WARTUNG, PauseStatus.AKTIV,
                          NOW - timedelta(minutes=90), 60)
        v.pausen = [p]
        result = v.ueberfaellige_pausen(NOW)
        assert len(result) == 1
        assert result[0] is p


# ---------------------------------------------------------------------------
# Default PauseVerlaeufe (reference values)
# ---------------------------------------------------------------------------

class TestDefaultPauseVerlaeufe:
    def setup_method(self):
        self.verlaeufe = get_default_pause_verlaeufe()
        self.v1 = next(v for v in self.verlaeufe if v.verlauf_id == "PV-001")
        self.v2 = next(v for v in self.verlaeufe if v.verlauf_id == "PV-002")

    def test_two_verlaeufe_returned(self):
        assert len(self.verlaeufe) == 2

    def test_pv001_workflow_instanz(self):
        assert self.v1.workflow_instanz_id == "WI-K-001"

    def test_pv002_workflow_instanz(self):
        assert self.v2.workflow_instanz_id == "WI-S-002"

    def test_pv001_has_two_pausen(self):
        assert len(self.v1.pausen) == 2

    def test_pv002_has_one_pause(self):
        assert len(self.v2.pausen) == 1

    def test_pv001_aktive_pause_is_pa002(self):
        aktiv = self.v1.aktive_pause()
        assert aktiv is not None
        assert aktiv.pause_id == "PA-002"

    def test_pv002_no_aktive_pause(self):
        assert self.v2.aktive_pause() is None

    def test_pa001_status_fortgesetzt(self):
        pa001 = next(p for p in self.v1.pausen if p.pause_id == "PA-001")
        assert pa001.status == PauseStatus.FORTGESETZT

    def test_pa002_status_aktiv(self):
        pa002 = next(p for p in self.v1.pausen if p.pause_id == "PA-002")
        assert pa002.status == PauseStatus.AKTIV

    def test_pa003_status_abgebrochen(self):
        pa003 = self.v2.pausen[0]
        assert pa003.status == PauseStatus.ABGEBROCHEN

    def test_pa001_dauer_60_minutes(self):
        pa001 = next(p for p in self.v1.pausen if p.pause_id == "PA-001")
        # pausiert 2h before NOW, fortgesetzt 1h before NOW → 60 min
        assert pa001.pause_dauer_minuten(NOW) == pytest.approx(60.0)

    def test_pa002_dauer_90_minutes(self):
        pa002 = next(p for p in self.v1.pausen if p.pause_id == "PA-002")
        # pausiert 90 min before NOW, AKTIV → 90 min
        assert pa002.pause_dauer_minuten(NOW) == pytest.approx(90.0)

    def test_pa003_dauer_zero(self):
        pa003 = self.v2.pausen[0]
        assert pa003.pause_dauer_minuten(NOW) == 0.0

    def test_pa002_ist_ueberfaellig(self):
        pa002 = next(p for p in self.v1.pausen if p.pause_id == "PA-002")
        # 90 min elapsed, max=60 → ueberfaellig
        assert pa002.ist_ueberfaellig(NOW) is True

    def test_pa001_not_ueberfaellig(self):
        pa001 = next(p for p in self.v1.pausen if p.pause_id == "PA-001")
        # FORTGESETZT → not active → not ueberfaellig
        assert pa001.ist_ueberfaellig(NOW) is False

    def test_pv001_gesamt_pause_minuten_150(self):
        # PA-001: 60 min + PA-002: 90 min = 150 min
        assert self.v1.gesamt_pause_minuten(NOW) == pytest.approx(150.0)

    def test_pv002_gesamt_pause_minuten_zero(self):
        # PA-003: ABGEBROCHEN → excluded → 0.0
        assert self.v2.gesamt_pause_minuten(NOW) == 0.0

    def test_pv001_ueberfaellige_pausen_one(self):
        result = self.v1.ueberfaellige_pausen(NOW)
        assert len(result) == 1
        assert result[0].pause_id == "PA-002"

    def test_pv002_ueberfaellige_pausen_empty(self):
        assert self.v2.ueberfaellige_pausen(NOW) == []

    def test_pa001_grund_genehmigung_ausstehend(self):
        pa001 = next(p for p in self.v1.pausen if p.pause_id == "PA-001")
        assert pa001.grund == PauseGrund.GENEHMIGUNG_AUSSTEHEND

    def test_pa002_grund_externe_abhaengigkeit(self):
        pa002 = next(p for p in self.v1.pausen if p.pause_id == "PA-002")
        assert pa002.grund == PauseGrund.EXTERNE_ABHAENGIGKEIT

    def test_pa003_grund_wartung(self):
        pa003 = self.v2.pausen[0]
        assert pa003.grund == PauseGrund.WARTUNG

    def test_pa001_resume_ausloeser_manuell(self):
        pa001 = next(p for p in self.v1.pausen if p.pause_id == "PA-001")
        assert pa001.resume_ausloeser == ResumeAusloeser.MANUELL

    def test_pa002_max_pause_60(self):
        pa002 = next(p for p in self.v1.pausen if p.pause_id == "PA-002")
        assert pa002.max_pause_minuten == 60

    def test_pa001_notiz_not_empty(self):
        pa001 = next(p for p in self.v1.pausen if p.pause_id == "PA-001")
        assert pa001.notiz != ""

    def test_pa003_is_not_active(self):
        pa003 = self.v2.pausen[0]
        assert pa003.ist_aktiv() is False


# ---------------------------------------------------------------------------
# API Endpoints (TestClient)
# ---------------------------------------------------------------------------

class TestProcessKernelApiWave61:
    def setup_method(self):
        from fastapi.testclient import TestClient
        from app.api.v1.endpoints.process_kernel_api import router
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    def test_quota_uebersicht_200(self):
        r = self.client.get("/process/quota/uebersicht")
        assert r.status_code == 200

    def test_quota_uebersicht_has_uebersicht_id(self):
        r = self.client.get("/process/quota/uebersicht")
        assert r.json()["uebersicht_id"] == "QU-001"

    def test_quota_uebersicht_has_tenant_id(self):
        r = self.client.get("/process/quota/uebersicht")
        assert r.json()["tenant_id"] == "TENANT-A"

    def test_quota_uebersicht_kritische_quotas_two(self):
        r = self.client.get("/process/quota/uebersicht")
        assert len(r.json()["kritische_quotas"]) == 2

    def test_quota_uebersicht_status_api_anfragen_normal(self):
        r = self.client.get("/process/quota/uebersicht")
        assert r.json()["status_pro_typ"]["API_ANFRAGEN"] == "NORMAL"

    def test_quota_uebersicht_status_speicher_warnung(self):
        r = self.client.get("/process/quota/uebersicht")
        assert r.json()["status_pro_typ"]["SPEICHER_MB"] == "WARNUNG"

    def test_quota_pruefe_verbrauch_normal(self):
        r = self.client.post("/process/quota/pruefe-verbrauch",
                             json={"limit": 100.0, "verbrauch": 50.0})
        assert r.status_code == 200
        assert r.json()["status"] == "NORMAL"

    def test_quota_pruefe_verbrauch_erschoepft(self):
        r = self.client.post("/process/quota/pruefe-verbrauch",
                             json={"limit": 100.0, "verbrauch": 101.0})
        assert r.json()["status"] == "ERSCHOEPFT"

    def test_quota_pruefe_verbrauch_verfuegbar(self):
        r = self.client.post("/process/quota/pruefe-verbrauch",
                             json={"limit": 100.0, "verbrauch": 30.0})
        assert r.json()["verfuegbar"] == pytest.approx(70.0)

    def test_quota_pruefe_verbrauch_verfuegbar_zero_when_exceeded(self):
        r = self.client.post("/process/quota/pruefe-verbrauch",
                             json={"limit": 100.0, "verbrauch": 200.0})
        assert r.json()["verfuegbar"] == 0.0

    def test_pause_verlaeufe_200(self):
        r = self.client.get("/process/pause/verlaeufe")
        assert r.status_code == 200

    def test_pause_verlaeufe_two_items(self):
        r = self.client.get("/process/pause/verlaeufe")
        assert len(r.json()) == 2

    def test_pause_verlaeufe_pv001_aktive_pause_pa002(self):
        r = self.client.get("/process/pause/verlaeufe")
        pv001 = next(v for v in r.json() if v["verlauf_id"] == "PV-001")
        assert pv001["aktive_pause_id"] == "PA-002"

    def test_pause_verlaeufe_pv002_no_aktive_pause(self):
        r = self.client.get("/process/pause/verlaeufe")
        pv002 = next(v for v in r.json() if v["verlauf_id"] == "PV-002")
        assert pv002["aktive_pause_id"] is None

    def test_pause_verlaeufe_pv001_gesamt_150(self):
        r = self.client.get("/process/pause/verlaeufe")
        pv001 = next(v for v in r.json() if v["verlauf_id"] == "PV-001")
        assert pv001["gesamt_pause_minuten"] == pytest.approx(150.0)

    def test_pause_verlaeufe_pv002_gesamt_zero(self):
        r = self.client.get("/process/pause/verlaeufe")
        pv002 = next(v for v in r.json() if v["verlauf_id"] == "PV-002")
        assert pv002["gesamt_pause_minuten"] == 0.0

    def test_pause_verlaeufe_pv001_one_ueberfaellig(self):
        r = self.client.get("/process/pause/verlaeufe")
        pv001 = next(v for v in r.json() if v["verlauf_id"] == "PV-001")
        assert pv001["ueberfaellige_pausen"] == 1

    def test_pruefe_ueberfaellig_pv001(self):
        r = self.client.post("/process/pause/pruefe-ueberfaellig",
                             json={"verlauf_id": "PV-001"})
        assert r.status_code == 200
        assert r.json()["verlauf_id"] == "PV-001"

    def test_pruefe_ueberfaellig_pv001_has_pa002(self):
        r = self.client.post("/process/pause/pruefe-ueberfaellig",
                             json={"verlauf_id": "PV-001"})
        ids = [p["pause_id"] for p in r.json()["ueberfaellige_pausen"]]
        assert "PA-002" in ids

    def test_pruefe_ueberfaellig_pv002_empty(self):
        r = self.client.post("/process/pause/pruefe-ueberfaellig",
                             json={"verlauf_id": "PV-002"})
        assert r.json()["ueberfaellige_pausen"] == []

    def test_pruefe_ueberfaellig_unknown_verlauf_fehler(self):
        r = self.client.post("/process/pause/pruefe-ueberfaellig",
                             json={"verlauf_id": "NONEXISTENT"})
        assert "fehler" in r.json()
