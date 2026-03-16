"""Wave 60: Process Forecasting + Workflow Handover — 130+ Tests"""
import pytest
from datetime import datetime, timedelta

from app.core.process_forecast_contracts import (
    PrognoseTyp, PrognoseMethode, KonfidenzNiveau,
    Datenpunkt, PrognoseErgebnis,
    berechne_gleitenden_durchschnitt, berechne_gewichteten_durchschnitt,
    erstelle_prognose, get_default_prognosen,
)
from app.core.workflow_handover_contracts import (
    UebergabeTyp, UebergabeStatus, DringlichkeitsStufe,
    UebergabeAnfrage, UebergabeProtokoll,
    get_default_uebergabe_protokolle,
)

# ─────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────
BASE = datetime(2026, 3, 16, 10, 0, 0)


def _punkte(werte):
    """Create Datenpunkt list from float values (hour offsets from BASE)."""
    return [Datenpunkt(BASE - timedelta(hours=len(werte) - i), float(w)) for i, w in enumerate(werte)]


# ═══════════════════════════════════════════════════════════════
# SECTION 1 — Enums
# ═══════════════════════════════════════════════════════════════

class TestPrognoseTypEnum:
    def test_last(self):
        assert PrognoseTyp.LAST == "LAST"

    def test_durchlaufzeit(self):
        assert PrognoseTyp.DURCHLAUFZEIT == "DURCHLAUFZEIT"

    def test_fehlerrate(self):
        assert PrognoseTyp.FEHLERRATE == "FEHLERRATE"

    def test_kapazitaet(self):
        assert PrognoseTyp.KAPAZITAET == "KAPAZITAET"

    def test_is_str_enum(self):
        assert isinstance(PrognoseTyp.LAST, str)


class TestPrognoseMethodeEnum:
    def test_gleitender(self):
        assert PrognoseMethode.GLEITENDER_DURCHSCHNITT == "GLEITENDER_DURCHSCHNITT"

    def test_gewichteter(self):
        assert PrognoseMethode.GEWICHTETER_DURCHSCHNITT == "GEWICHTETER_DURCHSCHNITT"

    def test_lineare_regression(self):
        assert PrognoseMethode.LINEARE_REGRESSION == "LINEARE_REGRESSION"

    def test_saisonbereinigt(self):
        assert PrognoseMethode.SAISONBEREINIGT == "SAISONBEREINIGT"


class TestKonfidenzNiveauEnum:
    def test_niedrig(self):
        assert KonfidenzNiveau.NIEDRIG == "NIEDRIG"

    def test_mittel(self):
        assert KonfidenzNiveau.MITTEL == "MITTEL"

    def test_hoch(self):
        assert KonfidenzNiveau.HOCH == "HOCH"


# ═══════════════════════════════════════════════════════════════
# SECTION 2 — berechne_gleitenden_durchschnitt
# ═══════════════════════════════════════════════════════════════

class TestGleitenderDurchschnitt:
    def test_empty_list_returns_zero(self):
        assert berechne_gleitenden_durchschnitt([], 3) == 0.0

    def test_fenster_zero_returns_zero(self):
        punkte = _punkte([10.0, 20.0])
        assert berechne_gleitenden_durchschnitt(punkte, 0) == 0.0

    def test_fenster_negative_returns_zero(self):
        punkte = _punkte([10.0, 20.0])
        assert berechne_gleitenden_durchschnitt(punkte, -1) == 0.0

    def test_fenster_equals_length(self):
        punkte = _punkte([10.0, 20.0, 30.0])
        result = berechne_gleitenden_durchschnitt(punkte, 3)
        assert result == pytest.approx(20.0)

    def test_fenster_exceeds_length_uses_all(self):
        punkte = _punkte([10.0, 20.0])
        result = berechne_gleitenden_durchschnitt(punkte, 5)
        assert result == pytest.approx(15.0)

    def test_fenster_1_returns_last_value(self):
        punkte = _punkte([10.0, 20.0, 30.0])
        result = berechne_gleitenden_durchschnitt(punkte, 1)
        assert result == pytest.approx(30.0)

    def test_fenster_3_five_points(self):
        # last 3 of [80, 95, 110, 105, 120] → [110, 105, 120] → avg=111.666...
        punkte = _punkte([80.0, 95.0, 110.0, 105.0, 120.0])
        result = berechne_gleitenden_durchschnitt(punkte, 3)
        assert result == pytest.approx((110.0 + 105.0 + 120.0) / 3)

    def test_fenster_2_five_points(self):
        punkte = _punkte([80.0, 95.0, 110.0, 105.0, 120.0])
        result = berechne_gleitenden_durchschnitt(punkte, 2)
        assert result == pytest.approx((105.0 + 120.0) / 2)

    def test_single_point_any_fenster(self):
        punkte = _punkte([42.0])
        assert berechne_gleitenden_durchschnitt(punkte, 3) == pytest.approx(42.0)
        assert berechne_gleitenden_durchschnitt(punkte, 1) == pytest.approx(42.0)

    def test_all_same_values(self):
        punkte = _punkte([5.0, 5.0, 5.0, 5.0])
        assert berechne_gleitenden_durchschnitt(punkte, 3) == pytest.approx(5.0)

    def test_returns_float(self):
        punkte = _punkte([10.0, 20.0])
        result = berechne_gleitenden_durchschnitt(punkte, 2)
        assert isinstance(result, float)

    def test_fenster_5_three_points_uses_all(self):
        punkte = _punkte([100.0, 200.0, 300.0])
        result = berechne_gleitenden_durchschnitt(punkte, 5)
        assert result == pytest.approx(200.0)

    def test_sorting_by_timestamp(self):
        # Points given in reverse order — should still pick last N chronologically
        now = BASE
        p1 = Datenpunkt(now - timedelta(hours=2), 100.0)
        p2 = Datenpunkt(now - timedelta(hours=1), 200.0)
        p3 = Datenpunkt(now, 300.0)
        punkte = [p3, p1, p2]  # shuffled
        result = berechne_gleitenden_durchschnitt(punkte, 2)
        assert result == pytest.approx(250.0)  # avg of 200, 300


# ═══════════════════════════════════════════════════════════════
# SECTION 3 — berechne_gewichteten_durchschnitt
# ═══════════════════════════════════════════════════════════════

class TestGewichteterDurchschnitt:
    def test_empty_returns_zero(self):
        assert berechne_gewichteten_durchschnitt([]) == 0.0

    def test_single_point(self):
        punkte = _punkte([42.0])
        assert berechne_gewichteten_durchschnitt(punkte) == pytest.approx(42.0)

    def test_two_points_weights_1_2(self):
        # weights: first=1, second=2; total=3
        # v1=10, v2=20 → (1*10 + 2*20)/3 = 50/3
        punkte = _punkte([10.0, 20.0])
        result = berechne_gewichteten_durchschnitt(punkte)
        assert result == pytest.approx(50.0 / 3)

    def test_later_timestamp_higher_weight(self):
        # later point dominates
        punkte = _punkte([1.0, 100.0])
        result = berechne_gewichteten_durchschnitt(punkte)
        # (1*1 + 2*100)/3 = 201/3 = 67.0
        assert result == pytest.approx(201.0 / 3)
        # Must be > simple average
        assert result > 50.5

    def test_three_points(self):
        # weights 1,2,3; values 10,20,30 → (10+40+90)/6 = 140/6
        punkte = _punkte([10.0, 20.0, 30.0])
        result = berechne_gewichteten_durchschnitt(punkte)
        assert result == pytest.approx(140.0 / 6)

    def test_returns_float(self):
        punkte = _punkte([5.0])
        assert isinstance(berechne_gewichteten_durchschnitt(punkte), float)

    def test_all_same_values(self):
        punkte = _punkte([7.0, 7.0, 7.0])
        assert berechne_gewichteten_durchschnitt(punkte) == pytest.approx(7.0)

    def test_five_points(self):
        # 80, 95, 110, 105, 120 → weights 1,2,3,4,5; total weight=15
        punkte = _punkte([80.0, 95.0, 110.0, 105.0, 120.0])
        expected = (1*80 + 2*95 + 3*110 + 4*105 + 5*120) / 15
        result = berechne_gewichteten_durchschnitt(punkte)
        assert result == pytest.approx(expected)

    def test_sorting_applied(self):
        now = BASE
        p_old = Datenpunkt(now - timedelta(hours=2), 10.0)
        p_new = Datenpunkt(now, 100.0)
        punkte = [p_new, p_old]  # reverse order
        result = berechne_gewichteten_durchschnitt(punkte)
        # sorted: p_old(w=1), p_new(w=2) → (10+200)/3 = 70
        assert result == pytest.approx(70.0)


# ═══════════════════════════════════════════════════════════════
# SECTION 4 — PrognoseErgebnis.konfidenz_niveau
# ═══════════════════════════════════════════════════════════════

class TestKonfidenzNiveau:
    def _make(self, pct):
        return PrognoseErgebnis("X", PrognoseTyp.LAST, PrognoseMethode.GLEITENDER_DURCHSCHNITT, 0.0, pct, 4)

    def test_above_80_is_hoch(self):
        assert self._make(81.0).konfidenz_niveau == KonfidenzNiveau.HOCH

    def test_exactly_80_is_mittel(self):
        assert self._make(80.0).konfidenz_niveau == KonfidenzNiveau.MITTEL

    def test_75_is_mittel(self):
        assert self._make(75.0).konfidenz_niveau == KonfidenzNiveau.MITTEL

    def test_exactly_60_is_mittel(self):
        assert self._make(60.0).konfidenz_niveau == KonfidenzNiveau.MITTEL

    def test_below_60_is_niedrig(self):
        assert self._make(59.9).konfidenz_niveau == KonfidenzNiveau.NIEDRIG

    def test_zero_is_niedrig(self):
        assert self._make(0.0).konfidenz_niveau == KonfidenzNiveau.NIEDRIG

    def test_100_is_hoch(self):
        assert self._make(100.0).konfidenz_niveau == KonfidenzNiveau.HOCH

    def test_55_is_niedrig(self):
        assert self._make(55.0).konfidenz_niveau == KonfidenzNiveau.NIEDRIG

    def test_85_is_hoch(self):
        assert self._make(85.0).konfidenz_niveau == KonfidenzNiveau.HOCH


# ═══════════════════════════════════════════════════════════════
# SECTION 5 — erstelle_prognose
# ═══════════════════════════════════════════════════════════════

class TestErstelle_prognose:
    def test_returns_prognose_ergebnis(self):
        punkte = _punkte([10.0, 20.0, 30.0])
        result = erstelle_prognose("P1", PrognoseTyp.LAST, PrognoseMethode.GLEITENDER_DURCHSCHNITT, punkte, 4, 70.0)
        assert isinstance(result, PrognoseErgebnis)

    def test_prognose_id_stored(self):
        punkte = _punkte([10.0])
        result = erstelle_prognose("P-XYZ", PrognoseTyp.LAST, PrognoseMethode.GLEITENDER_DURCHSCHNITT, punkte, 4, 70.0)
        assert result.prognose_id == "P-XYZ"

    def test_methode_gleitend_uses_window_3(self):
        punkte = _punkte([80.0, 95.0, 110.0, 105.0, 120.0])
        result = erstelle_prognose("P1", PrognoseTyp.LAST, PrognoseMethode.GLEITENDER_DURCHSCHNITT, punkte, 4, 70.0)
        expected = (110.0 + 105.0 + 120.0) / 3
        assert result.prognostizierter_wert == pytest.approx(expected)

    def test_methode_gewichtet_uses_weighted(self):
        punkte = _punkte([10.0, 20.0])
        result = erstelle_prognose("P2", PrognoseTyp.LAST, PrognoseMethode.GEWICHTETER_DURCHSCHNITT, punkte, 4, 70.0)
        assert result.prognostizierter_wert == pytest.approx(50.0 / 3)

    def test_empty_data_returns_zero(self):
        result = erstelle_prognose("P3", PrognoseTyp.KAPAZITAET, PrognoseMethode.GEWICHTETER_DURCHSCHNITT, [], 12, 40.0)
        assert result.prognostizierter_wert == pytest.approx(0.0)

    def test_konfidenz_stored(self):
        result = erstelle_prognose("P4", PrognoseTyp.LAST, PrognoseMethode.GLEITENDER_DURCHSCHNITT, [], 4, 77.5)
        assert result.konfidenz_pct == pytest.approx(77.5)

    def test_zeitraum_stored(self):
        result = erstelle_prognose("P5", PrognoseTyp.LAST, PrognoseMethode.GLEITENDER_DURCHSCHNITT, [], 24, 70.0)
        assert result.prognose_zeitraum_stunden == 24

    def test_fallback_method_uses_gleitend(self):
        punkte = _punkte([10.0, 20.0, 30.0])
        result = erstelle_prognose("P6", PrognoseTyp.LAST, PrognoseMethode.LINEARE_REGRESSION, punkte, 4, 70.0)
        # fallback: all points as window
        assert result.prognostizierter_wert == pytest.approx(20.0)

    def test_typ_stored(self):
        result = erstelle_prognose("P7", PrognoseTyp.FEHLERRATE, PrognoseMethode.GLEITENDER_DURCHSCHNITT, [], 4, 70.0)
        assert result.prognose_typ == PrognoseTyp.FEHLERRATE


# ═══════════════════════════════════════════════════════════════
# SECTION 6 — Default Prognosen
# ═══════════════════════════════════════════════════════════════

class TestDefaultPrognosen:
    def setup_method(self):
        self.prognosen = get_default_prognosen()
        self.by_id = {p.prognose_id: p for p in self.prognosen}

    def test_count_is_4(self):
        assert len(self.prognosen) == 4

    def test_pg001_exists(self):
        assert "PG-001" in self.by_id

    def test_pg002_exists(self):
        assert "PG-002" in self.by_id

    def test_pg003_exists(self):
        assert "PG-003" in self.by_id

    def test_pg004_exists(self):
        assert "PG-004" in self.by_id

    def test_pg001_typ_last(self):
        assert self.by_id["PG-001"].prognose_typ == PrognoseTyp.LAST

    def test_pg001_methode_gleitend(self):
        assert self.by_id["PG-001"].methode == PrognoseMethode.GLEITENDER_DURCHSCHNITT

    def test_pg001_konfidenz_75(self):
        assert self.by_id["PG-001"].konfidenz_pct == pytest.approx(75.0)

    def test_pg001_konfidenz_niveau_mittel(self):
        assert self.by_id["PG-001"].konfidenz_niveau == KonfidenzNiveau.MITTEL

    def test_pg002_methode_gewichtet(self):
        assert self.by_id["PG-002"].methode == PrognoseMethode.GEWICHTETER_DURCHSCHNITT

    def test_pg002_konfidenz_85(self):
        assert self.by_id["PG-002"].konfidenz_pct == pytest.approx(85.0)

    def test_pg002_konfidenz_niveau_hoch(self):
        assert self.by_id["PG-002"].konfidenz_niveau == KonfidenzNiveau.HOCH

    def test_pg002_typ_durchlaufzeit(self):
        assert self.by_id["PG-002"].prognose_typ == PrognoseTyp.DURCHLAUFZEIT

    def test_pg003_konfidenz_55(self):
        assert self.by_id["PG-003"].konfidenz_pct == pytest.approx(55.0)

    def test_pg003_konfidenz_niveau_niedrig(self):
        assert self.by_id["PG-003"].konfidenz_niveau == KonfidenzNiveau.NIEDRIG

    def test_pg003_typ_fehlerrate(self):
        assert self.by_id["PG-003"].prognose_typ == PrognoseTyp.FEHLERRATE

    def test_pg004_empty_data_value_zero(self):
        assert self.by_id["PG-004"].prognostizierter_wert == pytest.approx(0.0)

    def test_pg004_konfidenz_40(self):
        assert self.by_id["PG-004"].konfidenz_pct == pytest.approx(40.0)

    def test_pg004_konfidenz_niveau_niedrig(self):
        assert self.by_id["PG-004"].konfidenz_niveau == KonfidenzNiveau.NIEDRIG

    def test_pg004_typ_kapazitaet(self):
        assert self.by_id["PG-004"].prognose_typ == PrognoseTyp.KAPAZITAET

    def test_pg001_zeitraum_4(self):
        assert self.by_id["PG-001"].prognose_zeitraum_stunden == 4

    def test_pg002_zeitraum_8(self):
        assert self.by_id["PG-002"].prognose_zeitraum_stunden == 8

    def test_pg003_zeitraum_24(self):
        assert self.by_id["PG-003"].prognose_zeitraum_stunden == 24

    def test_pg004_zeitraum_12(self):
        assert self.by_id["PG-004"].prognose_zeitraum_stunden == 12

    def test_pg001_value_is_avg_last_3_of_5(self):
        # last 3: 110, 105, 120
        expected = (110.0 + 105.0 + 120.0) / 3
        assert self.by_id["PG-001"].prognostizierter_wert == pytest.approx(expected)

    def test_pg003_two_points_used(self):
        # punkte[:2] = [80, 95], fenster=3 > len → avg of both
        expected = (80.0 + 95.0) / 2
        assert self.by_id["PG-003"].prognostizierter_wert == pytest.approx(expected)

    def test_erstellt_am_is_datetime(self):
        for p in self.prognosen:
            assert isinstance(p.erstellt_am, datetime)


# ═══════════════════════════════════════════════════════════════
# SECTION 7 — Handover Enums
# ═══════════════════════════════════════════════════════════════

class TestHandoverEnums:
    def test_uebergabe_typ_eskalation(self):
        assert UebergabeTyp.ESKALATION == "ESKALATION"

    def test_uebergabe_typ_delegation(self):
        assert UebergabeTyp.DELEGATION == "DELEGATION"

    def test_uebergabe_typ_stellvertretung(self):
        assert UebergabeTyp.STELLVERTRETUNG == "STELLVERTRETUNG"

    def test_uebergabe_typ_abschluss(self):
        assert UebergabeTyp.ABSCHLUSS == "ABSCHLUSS"

    def test_status_angefragt(self):
        assert UebergabeStatus.ANGEFRAGT == "ANGEFRAGT"

    def test_status_angenommen(self):
        assert UebergabeStatus.ANGENOMMEN == "ANGENOMMEN"

    def test_status_abgelehnt(self):
        assert UebergabeStatus.ABGELEHNT == "ABGELEHNT"

    def test_status_abgeschlossen(self):
        assert UebergabeStatus.ABGESCHLOSSEN == "ABGESCHLOSSEN"

    def test_status_zurueckgezogen(self):
        assert UebergabeStatus.ZURUECKGEZOGEN == "ZURUECKGEZOGEN"

    def test_dringlichkeit_normal(self):
        assert DringlichkeitsStufe.NORMAL == "NORMAL"

    def test_dringlichkeit_dringend(self):
        assert DringlichkeitsStufe.DRINGEND == "DRINGEND"

    def test_dringlichkeit_sofort(self):
        assert DringlichkeitsStufe.SOFORT == "SOFORT"


# ═══════════════════════════════════════════════════════════════
# SECTION 8 — UebergabeAnfrage.ist_offen
# ═══════════════════════════════════════════════════════════════

class TestIstOffen:
    def _make(self, status):
        return UebergabeAnfrage("A1", "W1", UebergabeTyp.ESKALATION, "R1", "R2",
                                DringlichkeitsStufe.NORMAL, status)

    def test_angefragt_is_open(self):
        assert self._make(UebergabeStatus.ANGEFRAGT).ist_offen() is True

    def test_angenommen_not_open(self):
        assert self._make(UebergabeStatus.ANGENOMMEN).ist_offen() is False

    def test_abgelehnt_not_open(self):
        assert self._make(UebergabeStatus.ABGELEHNT).ist_offen() is False

    def test_abgeschlossen_not_open(self):
        assert self._make(UebergabeStatus.ABGESCHLOSSEN).ist_offen() is False

    def test_zurueckgezogen_not_open(self):
        assert self._make(UebergabeStatus.ZURUECKGEZOGEN).ist_offen() is False

    def test_default_status_is_angefragt(self):
        a = UebergabeAnfrage("A1", "W1", UebergabeTyp.ESKALATION, "R1", "R2")
        assert a.ist_offen() is True


# ═══════════════════════════════════════════════════════════════
# SECTION 9 — UebergabeAnfrage.reaktionszeit_minuten
# ═══════════════════════════════════════════════════════════════

class TestReaktionszeit:
    def test_none_if_not_answered(self):
        a = UebergabeAnfrage("A1", "W1", UebergabeTyp.ESKALATION, "R1", "R2",
                             angefragt_am=BASE, beantwortet_am=None)
        assert a.reaktionszeit_minuten() is None

    def test_15_minutes(self):
        a = UebergabeAnfrage("A1", "W1", UebergabeTyp.ESKALATION, "R1", "R2",
                             angefragt_am=BASE - timedelta(hours=2),
                             beantwortet_am=BASE - timedelta(hours=1, minutes=45))
        assert a.reaktionszeit_minuten() == pytest.approx(15.0)

    def test_10_minutes(self):
        a = UebergabeAnfrage("A2", "W1", UebergabeTyp.DELEGATION, "R1", "R2",
                             angefragt_am=BASE - timedelta(hours=1),
                             beantwortet_am=BASE - timedelta(minutes=50))
        assert a.reaktionszeit_minuten() == pytest.approx(10.0)

    def test_5_minutes(self):
        a = UebergabeAnfrage("A3", "W1", UebergabeTyp.DELEGATION, "R1", "R2",
                             angefragt_am=BASE,
                             beantwortet_am=BASE + timedelta(minutes=5))
        assert a.reaktionszeit_minuten() == pytest.approx(5.0)

    def test_returns_float(self):
        a = UebergabeAnfrage("A4", "W1", UebergabeTyp.ESKALATION, "R1", "R2",
                             angefragt_am=BASE,
                             beantwortet_am=BASE + timedelta(minutes=30))
        assert isinstance(a.reaktionszeit_minuten(), float)

    def test_ua004_reaktionszeit(self):
        # UA-004: angefragt 3h ago, beantwortet 2h55m ago → 5 min
        a = UebergabeAnfrage("UA-004", "WI-S-002", UebergabeTyp.STELLVERTRETUNG, "B-A", "B-B",
                             angefragt_am=BASE - timedelta(hours=3),
                             beantwortet_am=BASE - timedelta(hours=2, minutes=55))
        assert a.reaktionszeit_minuten() == pytest.approx(5.0)


# ═══════════════════════════════════════════════════════════════
# SECTION 10 — UebergabeProtokoll methods
# ═══════════════════════════════════════════════════════════════

class TestProtokollMethods:
    def _empty_protokoll(self):
        return UebergabeProtokoll("P1", "W1")

    def _make_anfrage(self, anfrage_id, typ=UebergabeTyp.ESKALATION, status=UebergabeStatus.ANGEFRAGT,
                      angefragt=None, beantwortet=None):
        return UebergabeAnfrage(anfrage_id, "W1", typ, "R1", "R2",
                                DringlichkeitsStufe.NORMAL, status,
                                angefragt_am=angefragt or BASE,
                                beantwortet_am=beantwortet)

    # offene_anfragen
    def test_offene_empty(self):
        p = self._empty_protokoll()
        assert p.offene_anfragen() == []

    def test_offene_only_angefragt(self):
        p = self._empty_protokoll()
        p.anfragen = [
            self._make_anfrage("A1", status=UebergabeStatus.ANGEFRAGT),
            self._make_anfrage("A2", status=UebergabeStatus.ANGENOMMEN),
            self._make_anfrage("A3", status=UebergabeStatus.ABGELEHNT),
        ]
        offene = p.offene_anfragen()
        assert len(offene) == 1
        assert offene[0].anfrage_id == "A1"

    def test_offene_multiple(self):
        p = self._empty_protokoll()
        p.anfragen = [
            self._make_anfrage("A1", status=UebergabeStatus.ANGEFRAGT),
            self._make_anfrage("A2", status=UebergabeStatus.ANGEFRAGT),
        ]
        assert len(p.offene_anfragen()) == 2

    # angenommene_anfragen
    def test_angenommene_empty(self):
        p = self._empty_protokoll()
        assert p.angenommene_anfragen() == []

    def test_angenommene_filters_correctly(self):
        p = self._empty_protokoll()
        p.anfragen = [
            self._make_anfrage("A1", status=UebergabeStatus.ANGENOMMEN),
            self._make_anfrage("A2", status=UebergabeStatus.ANGENOMMEN),
            self._make_anfrage("A3", status=UebergabeStatus.ABGELEHNT),
        ]
        assert len(p.angenommene_anfragen()) == 2

    # durchschnittliche_reaktionszeit_minuten
    def test_reaktionszeit_none_no_answered(self):
        p = self._empty_protokoll()
        p.anfragen = [self._make_anfrage("A1")]  # no beantwortet_am
        assert p.durchschnittliche_reaktionszeit_minuten() is None

    def test_reaktionszeit_empty(self):
        p = self._empty_protokoll()
        assert p.durchschnittliche_reaktionszeit_minuten() is None

    def test_reaktionszeit_average_of_answered(self):
        p = self._empty_protokoll()
        p.anfragen = [
            self._make_anfrage("A1", angefragt=BASE - timedelta(minutes=20), beantwortet=BASE),
            self._make_anfrage("A2", angefragt=BASE - timedelta(minutes=10), beantwortet=BASE),
        ]
        # 20 min + 10 min → avg 15 min
        assert p.durchschnittliche_reaktionszeit_minuten() == pytest.approx(15.0)

    def test_reaktionszeit_skips_unanswered(self):
        p = self._empty_protokoll()
        p.anfragen = [
            self._make_anfrage("A1", angefragt=BASE - timedelta(minutes=30), beantwortet=BASE),
            self._make_anfrage("A2"),  # no answer
        ]
        assert p.durchschnittliche_reaktionszeit_minuten() == pytest.approx(30.0)

    # eskalations_quote_pct
    def test_eskalation_quote_empty(self):
        p = self._empty_protokoll()
        assert p.eskalations_quote_pct() == pytest.approx(0.0)

    def test_eskalation_quote_zero_when_no_eskalation(self):
        p = self._empty_protokoll()
        p.anfragen = [self._make_anfrage("A1", typ=UebergabeTyp.DELEGATION)]
        assert p.eskalations_quote_pct() == pytest.approx(0.0)

    def test_eskalation_quote_100_when_all_eskalation(self):
        p = self._empty_protokoll()
        p.anfragen = [
            self._make_anfrage("A1", typ=UebergabeTyp.ESKALATION),
            self._make_anfrage("A2", typ=UebergabeTyp.ESKALATION),
        ]
        assert p.eskalations_quote_pct() == pytest.approx(100.0)

    def test_eskalation_quote_1_of_3(self):
        p = self._empty_protokoll()
        p.anfragen = [
            self._make_anfrage("A1", typ=UebergabeTyp.ESKALATION),
            self._make_anfrage("A2", typ=UebergabeTyp.DELEGATION),
            self._make_anfrage("A3", typ=UebergabeTyp.ABSCHLUSS),
        ]
        assert p.eskalations_quote_pct() == pytest.approx(100.0 / 3)

    def test_eskalation_quote_returns_float(self):
        p = self._empty_protokoll()
        assert isinstance(p.eskalations_quote_pct(), float)


# ═══════════════════════════════════════════════════════════════
# SECTION 11 — Default Protokolle
# ═══════════════════════════════════════════════════════════════

class TestDefaultProtokolle:
    def setup_method(self):
        self.protokolle = get_default_uebergabe_protokolle()
        self.by_id = {p.protokoll_id: p for p in self.protokolle}

    def test_count_is_2(self):
        assert len(self.protokolle) == 2

    def test_up001_exists(self):
        assert "UP-001" in self.by_id

    def test_up002_exists(self):
        assert "UP-002" in self.by_id

    def test_up001_workflow_instanz(self):
        assert self.by_id["UP-001"].workflow_instanz_id == "WI-K-001"

    def test_up002_workflow_instanz(self):
        assert self.by_id["UP-002"].workflow_instanz_id == "WI-S-002"

    def test_up001_three_anfragen(self):
        assert len(self.by_id["UP-001"].anfragen) == 3

    def test_up002_one_anfrage(self):
        assert len(self.by_id["UP-002"].anfragen) == 1

    def test_up001_one_offen(self):
        assert len(self.by_id["UP-001"].offene_anfragen()) == 1

    def test_up001_offen_is_ua003(self):
        offene = self.by_id["UP-001"].offene_anfragen()
        assert offene[0].anfrage_id == "UA-003"

    def test_up001_two_angenommen(self):
        assert len(self.by_id["UP-001"].angenommene_anfragen()) == 2

    def test_up001_eskalation_quote_33pct(self):
        # 1 ESKALATION out of 3
        assert self.by_id["UP-001"].eskalations_quote_pct() == pytest.approx(100.0 / 3)

    def test_up001_reaktionszeit_avg(self):
        # UA-001: 15 min, UA-002: 10 min; UA-003 unanswered → avg = 12.5
        result = self.by_id["UP-001"].durchschnittliche_reaktionszeit_minuten()
        assert result == pytest.approx(12.5)

    def test_up002_zero_offen(self):
        assert len(self.by_id["UP-002"].offene_anfragen()) == 0

    def test_up002_eskalation_quote_zero(self):
        # STELLVERTRETUNG is not ESKALATION
        assert self.by_id["UP-002"].eskalations_quote_pct() == pytest.approx(0.0)

    def test_up002_ua004_abgelehnt(self):
        a = self.by_id["UP-002"].anfragen[0]
        assert a.status == UebergabeStatus.ABGELEHNT

    def test_up002_ua004_typ_stellvertretung(self):
        a = self.by_id["UP-002"].anfragen[0]
        assert a.uebergabe_typ == UebergabeTyp.STELLVERTRETUNG

    def test_up002_ua004_dringlichkeit_sofort(self):
        a = self.by_id["UP-002"].anfragen[0]
        assert a.dringlichkeit == DringlichkeitsStufe.SOFORT

    def test_up001_ua001_von_sachbearbeiter(self):
        a = next(x for x in self.by_id["UP-001"].anfragen if x.anfrage_id == "UA-001")
        assert a.von_rolle == "SACHBEARBEITER"

    def test_up001_ua001_zu_abteilungsleiter(self):
        a = next(x for x in self.by_id["UP-001"].anfragen if x.anfrage_id == "UA-001")
        assert a.zu_rolle == "ABTEILUNGSLEITER"

    def test_up001_ua001_typ_eskalation(self):
        a = next(x for x in self.by_id["UP-001"].anfragen if x.anfrage_id == "UA-001")
        assert a.uebergabe_typ == UebergabeTyp.ESKALATION

    def test_up001_ua002_typ_delegation(self):
        a = next(x for x in self.by_id["UP-001"].anfragen if x.anfrage_id == "UA-002")
        assert a.uebergabe_typ == UebergabeTyp.DELEGATION

    def test_up001_ua003_typ_abschluss(self):
        a = next(x for x in self.by_id["UP-001"].anfragen if x.anfrage_id == "UA-003")
        assert a.uebergabe_typ == UebergabeTyp.ABSCHLUSS

    def test_up001_ua003_beantwortet_am_none(self):
        a = next(x for x in self.by_id["UP-001"].anfragen if x.anfrage_id == "UA-003")
        assert a.beantwortet_am is None

    def test_up002_reaktionszeit_5min(self):
        result = self.by_id["UP-002"].durchschnittliche_reaktionszeit_minuten()
        assert result == pytest.approx(5.0)


# ═══════════════════════════════════════════════════════════════
# SECTION 12 — FastAPI Endpoints (via TestClient)
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints.process_kernel_api import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestPrognoseEndpoints:
    def test_get_prognose_ergebnisse_200(self, client):
        resp = client.get("/process/prognose/ergebnisse")
        assert resp.status_code == 200

    def test_get_prognose_ergebnisse_returns_list(self, client):
        data = client.get("/process/prognose/ergebnisse").json()
        assert isinstance(data, list)

    def test_get_prognose_ergebnisse_count(self, client):
        data = client.get("/process/prognose/ergebnisse").json()
        assert len(data) == 4

    def test_get_prognose_ergebnisse_has_fields(self, client):
        item = client.get("/process/prognose/ergebnisse").json()[0]
        assert "prognose_id" in item
        assert "konfidenz_niveau" in item
        assert "prognostizierter_wert" in item

    def test_berechne_gleitend(self, client):
        resp = client.post("/process/prognose/berechne", json={"methode": "GLEITENDER_DURCHSCHNITT", "werte": [10, 20, 30], "fenster": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert data["ergebnis"] == pytest.approx(25.0)

    def test_berechne_gewichtet(self, client):
        resp = client.post("/process/prognose/berechne", json={"methode": "GEWICHTETER_DURCHSCHNITT", "werte": [10, 20], "fenster": 3})
        assert resp.status_code == 200
        data = resp.json()
        assert data["ergebnis"] == pytest.approx(50.0 / 3)

    def test_berechne_empty_werte(self, client):
        resp = client.post("/process/prognose/berechne", json={"methode": "GLEITENDER_DURCHSCHNITT", "werte": [], "fenster": 3})
        assert resp.status_code == 200
        assert resp.json()["ergebnis"] == pytest.approx(0.0)

    def test_berechne_datenpunkte_count(self, client):
        resp = client.post("/process/prognose/berechne", json={"methode": "GLEITENDER_DURCHSCHNITT", "werte": [1, 2, 3, 4, 5], "fenster": 3})
        assert resp.json()["datenpunkte"] == 5


class TestHandoverEndpoints:
    def test_get_protokolle_200(self, client):
        resp = client.get("/process/handover/protokolle")
        assert resp.status_code == 200

    def test_get_protokolle_returns_list(self, client):
        data = client.get("/process/handover/protokolle").json()
        assert isinstance(data, list)

    def test_get_protokolle_count(self, client):
        data = client.get("/process/handover/protokolle").json()
        assert len(data) == 2

    def test_get_protokolle_has_fields(self, client):
        item = client.get("/process/handover/protokolle").json()[0]
        assert "protokoll_id" in item
        assert "offene_anfragen" in item
        assert "eskalations_quote_pct" in item

    def test_pruefe_offen_up001(self, client):
        resp = client.post("/process/handover/pruefe-offen", json={"protokoll_id": "UP-001"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["protokoll_id"] == "UP-001"
        assert len(data["offene_anfragen"]) == 1

    def test_pruefe_offen_up002_no_open(self, client):
        resp = client.post("/process/handover/pruefe-offen", json={"protokoll_id": "UP-002"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["offene_anfragen"]) == 0

    def test_pruefe_offen_not_found(self, client):
        resp = client.post("/process/handover/pruefe-offen", json={"protokoll_id": "UNKNOWN"})
        assert resp.status_code == 200
        assert "fehler" in resp.json()

    def test_pruefe_offen_up001_eskalation_quote(self, client):
        resp = client.post("/process/handover/pruefe-offen", json={"protokoll_id": "UP-001"})
        data = resp.json()
        assert data["eskalations_quote_pct"] == pytest.approx(100.0 / 3)
