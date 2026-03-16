"""
Wave 50 — Process Archive Contracts & Workflow Metrics Contracts
70+ pytest tests covering both core modules.

No imports from app.api or app.infrastructure.
"""
from __future__ import annotations

from datetime import datetime

import pytest

from app.core.process_archive_contracts import (
    ArchivEintrag,
    ArchivierungsGrund,
    ArchivStatistik,
    ArchivStatus,
    AufbewahrungsKlasse,
    AUFBEWAHRUNGSFRISTEN,
    berechne_archiv_statistik,
    get_default_archiv_eintraege,
)
from app.core.workflow_metrics_contracts import (
    MetrikAggregation,
    MetrikMesspunkt,
    MetrikTyp,
    PerformanzBewertung,
    WorkflowKpiSummary,
    aggregiere_messpunkte,
    get_default_kpi_summaries,
)


# ---------------------------------------------------------------------------
# Fixtures — process_archive_contracts
# ---------------------------------------------------------------------------

@pytest.fixture()
def basis_datum() -> datetime:
    return datetime(2026, 1, 1, 0, 0)


@pytest.fixture()
def eintrag_klasse_a(basis_datum: datetime) -> ArchivEintrag:
    return ArchivEintrag(
        eintrag_id="AE-T-001",
        workflow_instanz_id="WF-T-001",
        tenant_id="T-001",
        grund=ArchivierungsGrund.GOBD_PFLICHT,
        status=ArchivStatus.GESPERRT,
        aufbewahrungsklasse=AufbewahrungsKlasse.KLASSE_A,
        archiviert_am=basis_datum,
        beschreibung="Fixture Klasse A",
    )


@pytest.fixture()
def eintrag_klasse_b(basis_datum: datetime) -> ArchivEintrag:
    return ArchivEintrag(
        eintrag_id="AE-T-002",
        workflow_instanz_id="WF-T-002",
        tenant_id="T-001",
        grund=ArchivierungsGrund.ABGESCHLOSSEN,
        status=ArchivStatus.ARCHIVIERT,
        aufbewahrungsklasse=AufbewahrungsKlasse.KLASSE_B,
        archiviert_am=basis_datum,
        beschreibung="Fixture Klasse B",
    )


@pytest.fixture()
def eintrag_klasse_c(basis_datum: datetime) -> ArchivEintrag:
    return ArchivEintrag(
        eintrag_id="AE-T-003",
        workflow_instanz_id="WF-T-003",
        tenant_id="T-001",
        grund=ArchivierungsGrund.INAKTIVITAET,
        status=ArchivStatus.ARCHIVIERT,
        aufbewahrungsklasse=AufbewahrungsKlasse.KLASSE_C,
        archiviert_am=basis_datum,
        beschreibung="Fixture Klasse C",
    )


@pytest.fixture()
def eintrag_klasse_d() -> ArchivEintrag:
    return ArchivEintrag(
        eintrag_id="AE-T-004",
        workflow_instanz_id="WF-T-004",
        tenant_id="T-001",
        grund=ArchivierungsGrund.MANUELL,
        status=ArchivStatus.GELOESCHT,
        aufbewahrungsklasse=AufbewahrungsKlasse.KLASSE_D,
        archiviert_am=datetime(2020, 6, 15, 0, 0),
        beschreibung="Fixture Klasse D",
    )


@pytest.fixture()
def default_eintraege() -> list[ArchivEintrag]:
    return get_default_archiv_eintraege()


# ---------------------------------------------------------------------------
# Fixtures — workflow_metrics_contracts
# ---------------------------------------------------------------------------

@pytest.fixture()
def messpunkt_fabrik():
    """Erzeugt MetrikMesspunkt-Instanzen bequem."""
    ts = datetime(2026, 3, 1, 8, 0)

    def _make(
        wert: float,
        workflow_typ: str = "wf_a",
        metrik_typ: MetrikTyp = MetrikTyp.DURCHLAUFZEIT,
        mid: str = "MP-001",
    ) -> MetrikMesspunkt:
        return MetrikMesspunkt(
            messpunkt_id=mid,
            workflow_typ=workflow_typ,
            metrik_typ=metrik_typ,
            wert=wert,
            einheit="Minuten",
            gemessen_am=ts,
            tenant_id="T-001",
        )

    return _make


@pytest.fixture()
def default_kpis() -> list[WorkflowKpiSummary]:
    return get_default_kpi_summaries()


# ===========================================================================
# Section 1: ArchivierungsGrund enum
# ===========================================================================

class TestArchivierungsGrund:
    def test_abgeschlossen_value(self):
        assert ArchivierungsGrund.ABGESCHLOSSEN == "ABGESCHLOSSEN"

    def test_gobd_pflicht_value(self):
        assert ArchivierungsGrund.GOBD_PFLICHT == "GOBD_PFLICHT"

    def test_manuell_value(self):
        assert ArchivierungsGrund.MANUELL == "MANUELL"

    def test_inaktivitaet_value(self):
        assert ArchivierungsGrund.INAKTIVITAET == "INAKTIVITAET"

    def test_all_members_count(self):
        assert len(ArchivierungsGrund) == 4


# ===========================================================================
# Section 2: ArchivStatus enum
# ===========================================================================

class TestArchivStatus:
    def test_aktiv_value(self):
        assert ArchivStatus.AKTIV == "AKTIV"

    def test_archiviert_value(self):
        assert ArchivStatus.ARCHIVIERT == "ARCHIVIERT"

    def test_gesperrt_value(self):
        assert ArchivStatus.GESPERRT == "GESPERRT"

    def test_geloescht_value(self):
        assert ArchivStatus.GELOESCHT == "GELOESCHT"

    def test_all_members_count(self):
        assert len(ArchivStatus) == 4


# ===========================================================================
# Section 3: AufbewahrungsKlasse enum
# ===========================================================================

class TestAufbewahrungsKlasse:
    def test_klasse_a_value(self):
        assert AufbewahrungsKlasse.KLASSE_A == "KLASSE_A"

    def test_klasse_b_value(self):
        assert AufbewahrungsKlasse.KLASSE_B == "KLASSE_B"

    def test_klasse_c_value(self):
        assert AufbewahrungsKlasse.KLASSE_C == "KLASSE_C"

    def test_klasse_d_value(self):
        assert AufbewahrungsKlasse.KLASSE_D == "KLASSE_D"

    def test_all_members_count(self):
        assert len(AufbewahrungsKlasse) == 4


# ===========================================================================
# Section 4: AUFBEWAHRUNGSFRISTEN dict
# ===========================================================================

class TestAufbewahrungsfristen:
    def test_klasse_a_ist_10_jahre(self):
        assert AUFBEWAHRUNGSFRISTEN[AufbewahrungsKlasse.KLASSE_A] == 10

    def test_klasse_b_ist_6_jahre(self):
        assert AUFBEWAHRUNGSFRISTEN[AufbewahrungsKlasse.KLASSE_B] == 6

    def test_klasse_c_ist_3_jahre(self):
        assert AUFBEWAHRUNGSFRISTEN[AufbewahrungsKlasse.KLASSE_C] == 3

    def test_klasse_d_ist_1_jahr(self):
        assert AUFBEWAHRUNGSFRISTEN[AufbewahrungsKlasse.KLASSE_D] == 1

    def test_alle_vier_klassen_vorhanden(self):
        assert len(AUFBEWAHRUNGSFRISTEN) == 4


# ===========================================================================
# Section 5: ArchivEintrag.aufbewahrungsfrist_jahre
# ===========================================================================

class TestArchivEintragAufbewahrungsfristJahre:
    def test_klasse_a_10_jahre(self, eintrag_klasse_a):
        assert eintrag_klasse_a.aufbewahrungsfrist_jahre == 10

    def test_klasse_b_6_jahre(self, eintrag_klasse_b):
        assert eintrag_klasse_b.aufbewahrungsfrist_jahre == 6

    def test_klasse_c_3_jahre(self, eintrag_klasse_c):
        assert eintrag_klasse_c.aufbewahrungsfrist_jahre == 3

    def test_klasse_d_1_jahr(self, eintrag_klasse_d):
        assert eintrag_klasse_d.aufbewahrungsfrist_jahre == 1


# ===========================================================================
# Section 6: ArchivEintrag.loeschen_ab
# ===========================================================================

class TestArchivEintragLoeschenAb:
    def test_klasse_a_loeschen_ab_plus_10_jahre(self, eintrag_klasse_a, basis_datum):
        erwartet = basis_datum.replace(year=basis_datum.year + 10)
        assert eintrag_klasse_a.loeschen_ab == erwartet

    def test_klasse_b_loeschen_ab_plus_6_jahre(self, eintrag_klasse_b, basis_datum):
        erwartet = basis_datum.replace(year=basis_datum.year + 6)
        assert eintrag_klasse_b.loeschen_ab == erwartet

    def test_klasse_c_loeschen_ab_plus_3_jahre(self, eintrag_klasse_c, basis_datum):
        erwartet = basis_datum.replace(year=basis_datum.year + 3)
        assert eintrag_klasse_c.loeschen_ab == erwartet

    def test_klasse_d_loeschen_ab_plus_1_jahr(self, eintrag_klasse_d):
        erwartet = datetime(2021, 6, 15, 0, 0)
        assert eintrag_klasse_d.loeschen_ab == erwartet

    def test_loeschen_ab_behaelt_uhrzeit(self, basis_datum):
        eintrag = ArchivEintrag(
            eintrag_id="X",
            workflow_instanz_id="Y",
            tenant_id="T",
            grund=ArchivierungsGrund.MANUELL,
            status=ArchivStatus.ARCHIVIERT,
            aufbewahrungsklasse=AufbewahrungsKlasse.KLASSE_C,
            archiviert_am=datetime(2026, 6, 15, 14, 30, 59),
        )
        assert eintrag.loeschen_ab == datetime(2029, 6, 15, 14, 30, 59)


# ===========================================================================
# Section 7: ArchivEintrag.ist_loeschbar_am
# ===========================================================================

class TestArchivEintragIstLoeschbarAm:
    def test_loeschbar_wenn_datum_ueberschritten_und_nicht_gesperrt(self, eintrag_klasse_b):
        # KLASSE_B archiviert 2026-01-01 → loeschen_ab = 2032-01-01
        jetzt_nach_frist = datetime(2032, 6, 1, 0, 0)
        assert eintrag_klasse_b.ist_loeschbar_am(jetzt_nach_frist) is True

    def test_nicht_loeschbar_wenn_datum_noch_nicht_erreicht(self, eintrag_klasse_b):
        jetzt_vor_frist = datetime(2028, 1, 1, 0, 0)
        assert eintrag_klasse_b.ist_loeschbar_am(jetzt_vor_frist) is False

    def test_nicht_loeschbar_wenn_gesperrt_obwohl_datum_ueberschritten(self, eintrag_klasse_a):
        # KLASSE_A GESPERRT — nie löschbar via ist_loeschbar_am auch nach 10 Jahren
        jetzt_weit_nach_frist = datetime(2040, 1, 1, 0, 0)
        assert eintrag_klasse_a.ist_loeschbar_am(jetzt_weit_nach_frist) is False

    def test_loeschbar_genau_am_loeschen_ab_datum(self, eintrag_klasse_c):
        # KLASSE_C archiviert 2026-01-01 → loeschen_ab = 2029-01-01
        genau = datetime(2029, 1, 1, 0, 0)
        assert eintrag_klasse_c.ist_loeschbar_am(genau) is True

    def test_nicht_loeschbar_eine_sekunde_vor_frist(self, eintrag_klasse_c):
        from datetime import timedelta
        knapp_davor = datetime(2029, 1, 1, 0, 0) - timedelta(seconds=1)
        assert eintrag_klasse_c.ist_loeschbar_am(knapp_davor) is False

    def test_loeschbar_fuer_geloescht_status_nach_frist(self, eintrag_klasse_d):
        # KLASSE_D archiviert 2020-06-15 → loeschen_ab = 2021-06-15; status GELOESCHT
        jetzt_nach_frist = datetime(2022, 1, 1, 0, 0)
        assert eintrag_klasse_d.ist_loeschbar_am(jetzt_nach_frist) is True

    def test_loeschbar_fuer_aktiv_status_nach_frist(self, basis_datum):
        eintrag = ArchivEintrag(
            eintrag_id="AE-X",
            workflow_instanz_id="WF-X",
            tenant_id="T-X",
            grund=ArchivierungsGrund.ABGESCHLOSSEN,
            status=ArchivStatus.AKTIV,
            aufbewahrungsklasse=AufbewahrungsKlasse.KLASSE_D,
            archiviert_am=datetime(2020, 1, 1),
        )
        # loeschen_ab = 2021-01-01
        assert eintrag.ist_loeschbar_am(datetime(2022, 1, 1)) is True


# ===========================================================================
# Section 8: ArchivEintrag.as_dict
# ===========================================================================

class TestArchivEintragAsDict:
    def test_alle_schluessel_vorhanden(self, eintrag_klasse_a):
        d = eintrag_klasse_a.as_dict()
        expected_keys = {
            "eintrag_id",
            "workflow_instanz_id",
            "tenant_id",
            "grund",
            "status",
            "aufbewahrungsklasse",
            "aufbewahrungsfrist_jahre",
            "archiviert_am",
            "loeschen_ab",
            "beschreibung",
        }
        assert expected_keys.issubset(d.keys())

    def test_grund_als_string_wert(self, eintrag_klasse_a):
        d = eintrag_klasse_a.as_dict()
        assert d["grund"] == "GOBD_PFLICHT"

    def test_status_als_string_wert(self, eintrag_klasse_a):
        d = eintrag_klasse_a.as_dict()
        assert d["status"] == "GESPERRT"

    def test_aufbewahrungsklasse_als_string_wert(self, eintrag_klasse_a):
        d = eintrag_klasse_a.as_dict()
        assert d["aufbewahrungsklasse"] == "KLASSE_A"

    def test_aufbewahrungsfrist_jahre_korrekt(self, eintrag_klasse_a):
        d = eintrag_klasse_a.as_dict()
        assert d["aufbewahrungsfrist_jahre"] == 10

    def test_loeschen_ab_als_iso_string(self, eintrag_klasse_a):
        d = eintrag_klasse_a.as_dict()
        # Muss ein ISO-String sein, der mit "2036" beginnt (2026 + 10)
        assert d["loeschen_ab"].startswith("2036")

    def test_archiviert_am_als_iso_string(self, eintrag_klasse_a):
        d = eintrag_klasse_a.as_dict()
        assert d["archiviert_am"].startswith("2026")

    def test_beschreibung_im_dict(self, eintrag_klasse_a):
        d = eintrag_klasse_a.as_dict()
        assert d["beschreibung"] == "Fixture Klasse A"


# ===========================================================================
# Section 9: ArchivStatistik
# ===========================================================================

class TestArchivStatistik:
    def test_gesamt_ist_summe_aller_buckets(self):
        stat = ArchivStatistik(
            tenant_id="T",
            aktiv=5,
            archiviert=10,
            gesperrt=3,
            geloescht=2,
        )
        assert stat.gesamt == 20

    def test_archivierungsrate_pct_berechnung(self):
        stat = ArchivStatistik(
            tenant_id="T",
            aktiv=10,
            archiviert=50,
            gesperrt=20,
            geloescht=20,
        )
        # (50+20+20)/100*100 = 90.0
        assert stat.archivierungsrate_pct == 90.0

    def test_archivierungsrate_pct_zero_fuer_leere_statistik(self):
        stat = ArchivStatistik(tenant_id="T", aktiv=0, archiviert=0, gesperrt=0, geloescht=0)
        assert stat.archivierungsrate_pct == 0.0

    def test_archivierungsrate_pct_100_wenn_nichts_aktiv(self):
        stat = ArchivStatistik(tenant_id="T", aktiv=0, archiviert=10, gesperrt=5, geloescht=5)
        assert stat.archivierungsrate_pct == 100.0

    def test_as_dict_alle_schluessel(self):
        stat = ArchivStatistik(tenant_id="T", aktiv=1, archiviert=2, gesperrt=3, geloescht=4)
        d = stat.as_dict()
        for key in ("tenant_id", "aktiv", "archiviert", "gesperrt", "geloescht", "gesamt", "archivierungsrate_pct"):
            assert key in d

    def test_as_dict_gesamt_korrekt(self):
        stat = ArchivStatistik(tenant_id="T", aktiv=1, archiviert=2, gesperrt=3, geloescht=4)
        assert stat.as_dict()["gesamt"] == 10

    def test_as_dict_rate_korrekt(self):
        stat = ArchivStatistik(tenant_id="T", aktiv=25, archiviert=25, gesperrt=25, geloescht=25)
        assert stat.as_dict()["archivierungsrate_pct"] == 75.0


# ===========================================================================
# Section 10: berechne_archiv_statistik
# ===========================================================================

class TestBerechneArchivStatistik:
    def test_zaehlt_nur_passenden_tenant(self, basis_datum):
        eintraege = [
            ArchivEintrag(
                eintrag_id="X1", workflow_instanz_id="WX1", tenant_id="T-A",
                grund=ArchivierungsGrund.ABGESCHLOSSEN, status=ArchivStatus.AKTIV,
                aufbewahrungsklasse=AufbewahrungsKlasse.KLASSE_C, archiviert_am=basis_datum,
            ),
            ArchivEintrag(
                eintrag_id="X2", workflow_instanz_id="WX2", tenant_id="T-B",
                grund=ArchivierungsGrund.ABGESCHLOSSEN, status=ArchivStatus.ARCHIVIERT,
                aufbewahrungsklasse=AufbewahrungsKlasse.KLASSE_C, archiviert_am=basis_datum,
            ),
        ]
        stat = berechne_archiv_statistik(eintraege, "T-A")
        assert stat.aktiv == 1
        assert stat.archiviert == 0
        assert stat.gesamt == 1

    def test_leere_liste_ergibt_null_statistik(self):
        stat = berechne_archiv_statistik([], "T-A")
        assert stat.gesamt == 0
        assert stat.archivierungsrate_pct == 0.0

    def test_unbekannter_tenant_ergibt_null_statistik(self, default_eintraege):
        stat = berechne_archiv_statistik(default_eintraege, "UNBEKANNT")
        assert stat.gesamt == 0

    def test_bucket_counts_korrekt_fuer_default_eintraege(self, default_eintraege):
        # Default: AE-001 GESPERRT, AE-002 ARCHIVIERT, AE-003 ARCHIVIERT,
        #          AE-004 GELOESCHT, AE-005 AKTIV
        stat = berechne_archiv_statistik(default_eintraege, "TENANT-001")
        assert stat.aktiv == 1
        assert stat.archiviert == 2
        assert stat.gesperrt == 1
        assert stat.geloescht == 1

    def test_tenant_id_im_ergebnis_korrekt(self, default_eintraege):
        stat = berechne_archiv_statistik(default_eintraege, "TENANT-001")
        assert stat.tenant_id == "TENANT-001"


# ===========================================================================
# Section 11: get_default_archiv_eintraege
# ===========================================================================

class TestGetDefaultArchivEintraege:
    def test_gibt_5_eintraege_zurueck(self, default_eintraege):
        assert len(default_eintraege) == 5

    def test_ae001_ist_gesperrt_klasse_a(self, default_eintraege):
        ae001 = next(e for e in default_eintraege if e.eintrag_id == "AE-001")
        assert ae001.status == ArchivStatus.GESPERRT
        assert ae001.aufbewahrungsklasse == AufbewahrungsKlasse.KLASSE_A

    def test_ae002_ist_archiviert_klasse_b(self, default_eintraege):
        ae002 = next(e for e in default_eintraege if e.eintrag_id == "AE-002")
        assert ae002.status == ArchivStatus.ARCHIVIERT
        assert ae002.aufbewahrungsklasse == AufbewahrungsKlasse.KLASSE_B

    def test_ae003_ist_archiviert_klasse_c(self, default_eintraege):
        ae003 = next(e for e in default_eintraege if e.eintrag_id == "AE-003")
        assert ae003.status == ArchivStatus.ARCHIVIERT
        assert ae003.aufbewahrungsklasse == AufbewahrungsKlasse.KLASSE_C

    def test_ae004_ist_geloescht_klasse_d(self, default_eintraege):
        ae004 = next(e for e in default_eintraege if e.eintrag_id == "AE-004")
        assert ae004.status == ArchivStatus.GELOESCHT
        assert ae004.aufbewahrungsklasse == AufbewahrungsKlasse.KLASSE_D

    def test_ae005_ist_aktiv_klasse_b(self, default_eintraege):
        ae005 = next(e for e in default_eintraege if e.eintrag_id == "AE-005")
        assert ae005.status == ArchivStatus.AKTIV
        assert ae005.aufbewahrungsklasse == AufbewahrungsKlasse.KLASSE_B

    def test_custom_tenant_id_wird_gesetzt(self):
        eintraege = get_default_archiv_eintraege(tenant_id="CUSTOM-TENANT")
        assert all(e.tenant_id == "CUSTOM-TENANT" for e in eintraege)

    def test_default_tenant_id_ist_tenant_001(self, default_eintraege):
        assert all(e.tenant_id == "TENANT-001" for e in default_eintraege)

    def test_ae001_grund_ist_gobd_pflicht(self, default_eintraege):
        ae001 = next(e for e in default_eintraege if e.eintrag_id == "AE-001")
        assert ae001.grund == ArchivierungsGrund.GOBD_PFLICHT

    def test_ae004_grund_ist_manuell(self, default_eintraege):
        ae004 = next(e for e in default_eintraege if e.eintrag_id == "AE-004")
        assert ae004.grund == ArchivierungsGrund.MANUELL


# ===========================================================================
# Section 12: MetrikTyp enum
# ===========================================================================

class TestMetrikTyp:
    def test_durchlaufzeit_value(self):
        assert MetrikTyp.DURCHLAUFZEIT == "DURCHLAUFZEIT"

    def test_sla_einhaltung_value(self):
        assert MetrikTyp.SLA_EINHALTUNG == "SLA_EINHALTUNG"

    def test_fehlerrate_value(self):
        assert MetrikTyp.FEHLERRATE == "FEHLERRATE"

    def test_durchsatz_value(self):
        assert MetrikTyp.DURCHSATZ == "DURCHSATZ"

    def test_wartezeit_value(self):
        assert MetrikTyp.WARTEZEIT == "WARTEZEIT"

    def test_all_members_count(self):
        assert len(MetrikTyp) == 5


# ===========================================================================
# Section 13: MetrikAggregation enum
# ===========================================================================

class TestMetrikAggregation:
    def test_minimum_value(self):
        assert MetrikAggregation.MINIMUM == "MINIMUM"

    def test_maximum_value(self):
        assert MetrikAggregation.MAXIMUM == "MAXIMUM"

    def test_durchschnitt_value(self):
        assert MetrikAggregation.DURCHSCHNITT == "DURCHSCHNITT"

    def test_median_value(self):
        assert MetrikAggregation.MEDIAN == "MEDIAN"

    def test_summe_value(self):
        assert MetrikAggregation.SUMME == "SUMME"

    def test_all_members_count(self):
        assert len(MetrikAggregation) == 5


# ===========================================================================
# Section 14: PerformanzBewertung enum
# ===========================================================================

class TestPerformanzBewertung:
    def test_ausgezeichnet_value(self):
        assert PerformanzBewertung.AUSGEZEICHNET == "AUSGEZEICHNET"

    def test_gut_value(self):
        assert PerformanzBewertung.GUT == "GUT"

    def test_akzeptabel_value(self):
        assert PerformanzBewertung.AKZEPTABEL == "AKZEPTABEL"

    def test_kritisch_value(self):
        assert PerformanzBewertung.KRITISCH == "KRITISCH"

    def test_all_members_count(self):
        assert len(PerformanzBewertung) == 4


# ===========================================================================
# Section 15: MetrikMesspunkt.as_dict
# ===========================================================================

class TestMetrikMesspunktAsDict:
    def test_alle_schluessel_vorhanden(self, messpunkt_fabrik):
        mp = messpunkt_fabrik(42.0)
        d = mp.as_dict()
        for key in ("messpunkt_id", "workflow_typ", "metrik_typ", "wert", "einheit", "gemessen_am", "tenant_id"):
            assert key in d

    def test_metrik_typ_als_string_wert(self, messpunkt_fabrik):
        mp = messpunkt_fabrik(10.0, metrik_typ=MetrikTyp.WARTEZEIT)
        assert mp.as_dict()["metrik_typ"] == "WARTEZEIT"

    def test_wert_korrekt(self, messpunkt_fabrik):
        mp = messpunkt_fabrik(99.9)
        assert mp.as_dict()["wert"] == 99.9

    def test_gemessen_am_als_iso_string(self, messpunkt_fabrik):
        mp = messpunkt_fabrik(1.0)
        iso = mp.as_dict()["gemessen_am"]
        assert isinstance(iso, str)
        assert "2026" in iso

    def test_tenant_id_im_dict(self, messpunkt_fabrik):
        mp = messpunkt_fabrik(5.0)
        assert mp.as_dict()["tenant_id"] == "T-001"


# ===========================================================================
# Section 16: WorkflowKpiSummary computed properties
# ===========================================================================

class TestWorkflowKpiSummaryFehlerrate:
    def test_fehlerrate_pct_berechnung(self):
        kpi = WorkflowKpiSummary(
            workflow_typ="test", tenant_id="T", periode="2026-Q1",
            instanzen_gesamt=100, instanzen_erfolgreich=90, instanzen_fehlgeschlagen=10,
            durchlaufzeit_avg_min=60.0, sla_einhaltung_pct=80.0, durchsatz_pro_stunde=5.0,
        )
        assert kpi.fehlerrate_pct == 10.0

    def test_fehlerrate_pct_null_fuer_gesamt_0(self):
        kpi = WorkflowKpiSummary(
            workflow_typ="test", tenant_id="T", periode="2026-Q1",
            instanzen_gesamt=0, instanzen_erfolgreich=0, instanzen_fehlgeschlagen=0,
            durchlaufzeit_avg_min=0.0, sla_einhaltung_pct=0.0, durchsatz_pro_stunde=0.0,
        )
        assert kpi.fehlerrate_pct == 0.0

    def test_fehlerrate_pct_rundet_auf_2_stellen(self):
        kpi = WorkflowKpiSummary(
            workflow_typ="test", tenant_id="T", periode="2026-Q1",
            instanzen_gesamt=3, instanzen_erfolgreich=2, instanzen_fehlgeschlagen=1,
            durchlaufzeit_avg_min=10.0, sla_einhaltung_pct=80.0, durchsatz_pro_stunde=1.0,
        )
        assert kpi.fehlerrate_pct == round(1 / 3 * 100, 2)


class TestWorkflowKpiSummaryErfolgsrate:
    def test_erfolgsrate_pct_berechnung(self):
        kpi = WorkflowKpiSummary(
            workflow_typ="test", tenant_id="T", periode="2026-Q1",
            instanzen_gesamt=200, instanzen_erfolgreich=180, instanzen_fehlgeschlagen=20,
            durchlaufzeit_avg_min=30.0, sla_einhaltung_pct=85.0, durchsatz_pro_stunde=3.0,
        )
        assert kpi.erfolgsrate_pct == 90.0

    def test_erfolgsrate_pct_null_fuer_gesamt_0(self):
        kpi = WorkflowKpiSummary(
            workflow_typ="test", tenant_id="T", periode="2026-Q1",
            instanzen_gesamt=0, instanzen_erfolgreich=0, instanzen_fehlgeschlagen=0,
            durchlaufzeit_avg_min=0.0, sla_einhaltung_pct=0.0, durchsatz_pro_stunde=0.0,
        )
        assert kpi.erfolgsrate_pct == 0.0


# ===========================================================================
# Section 17: WorkflowKpiSummary.performanz_bewertung
# ===========================================================================

class TestPerformanzBewertungAbleitung:
    def _kpi(self, sla: float) -> WorkflowKpiSummary:
        return WorkflowKpiSummary(
            workflow_typ="t", tenant_id="T", periode="P",
            instanzen_gesamt=100, instanzen_erfolgreich=int(sla),
            instanzen_fehlgeschlagen=100 - int(sla),
            durchlaufzeit_avg_min=10.0, sla_einhaltung_pct=sla,
            durchsatz_pro_stunde=1.0,
        )

    def test_ausgezeichnet_bei_95_prozent(self):
        assert self._kpi(95.0).performanz_bewertung == PerformanzBewertung.AUSGEZEICHNET

    def test_ausgezeichnet_bei_100_prozent(self):
        assert self._kpi(100.0).performanz_bewertung == PerformanzBewertung.AUSGEZEICHNET

    def test_gut_bei_80_prozent(self):
        assert self._kpi(80.0).performanz_bewertung == PerformanzBewertung.GUT

    def test_gut_bei_94_prozent(self):
        assert self._kpi(94.0).performanz_bewertung == PerformanzBewertung.GUT

    def test_akzeptabel_bei_60_prozent(self):
        assert self._kpi(60.0).performanz_bewertung == PerformanzBewertung.AKZEPTABEL

    def test_akzeptabel_bei_79_prozent(self):
        assert self._kpi(79.0).performanz_bewertung == PerformanzBewertung.AKZEPTABEL

    def test_kritisch_bei_59_prozent(self):
        assert self._kpi(59.0).performanz_bewertung == PerformanzBewertung.KRITISCH

    def test_kritisch_bei_0_prozent(self):
        assert self._kpi(0.0).performanz_bewertung == PerformanzBewertung.KRITISCH

    def test_grenzwert_95_ist_ausgezeichnet_nicht_gut(self):
        kpi = self._kpi(95.0)
        assert kpi.performanz_bewertung != PerformanzBewertung.GUT

    def test_grenzwert_80_ist_gut_nicht_akzeptabel(self):
        kpi = self._kpi(80.0)
        assert kpi.performanz_bewertung != PerformanzBewertung.AKZEPTABEL

    def test_grenzwert_60_ist_akzeptabel_nicht_kritisch(self):
        kpi = self._kpi(60.0)
        assert kpi.performanz_bewertung != PerformanzBewertung.KRITISCH


# ===========================================================================
# Section 18: WorkflowKpiSummary.as_dict
# ===========================================================================

class TestWorkflowKpiSummaryAsDict:
    def test_alle_schluessel_vorhanden(self):
        kpi = WorkflowKpiSummary(
            workflow_typ="wf", tenant_id="T", periode="2026-Q1",
            instanzen_gesamt=100, instanzen_erfolgreich=90, instanzen_fehlgeschlagen=10,
            durchlaufzeit_avg_min=60.0, sla_einhaltung_pct=90.0, durchsatz_pro_stunde=2.0,
            berechnet_am=datetime(2026, 3, 15, 0, 0),
        )
        d = kpi.as_dict()
        for key in (
            "workflow_typ", "tenant_id", "periode", "instanzen_gesamt",
            "instanzen_erfolgreich", "instanzen_fehlgeschlagen", "durchlaufzeit_avg_min",
            "sla_einhaltung_pct", "durchsatz_pro_stunde", "fehlerrate_pct",
            "erfolgsrate_pct", "performanz_bewertung", "berechnet_am",
        ):
            assert key in d, f"Schluessel fehlt: {key}"

    def test_performanz_bewertung_als_string_wert(self):
        kpi = WorkflowKpiSummary(
            workflow_typ="wf", tenant_id="T", periode="P",
            instanzen_gesamt=100, instanzen_erfolgreich=96, instanzen_fehlgeschlagen=4,
            durchlaufzeit_avg_min=10.0, sla_einhaltung_pct=96.0, durchsatz_pro_stunde=1.0,
        )
        assert kpi.as_dict()["performanz_bewertung"] == "AUSGEZEICHNET"

    def test_berechnet_am_als_iso_string(self):
        ts = datetime(2026, 3, 15, 12, 0)
        kpi = WorkflowKpiSummary(
            workflow_typ="wf", tenant_id="T", periode="P",
            instanzen_gesamt=10, instanzen_erfolgreich=9, instanzen_fehlgeschlagen=1,
            durchlaufzeit_avg_min=10.0, sla_einhaltung_pct=90.0, durchsatz_pro_stunde=1.0,
            berechnet_am=ts,
        )
        assert kpi.as_dict()["berechnet_am"] == ts.isoformat()


# ===========================================================================
# Section 19: aggregiere_messpunkte
# ===========================================================================

class TestAggregiereMesspunkte:
    def _mp(self, wert: float, wf: str = "wf_a", mt: MetrikTyp = MetrikTyp.DURCHLAUFZEIT) -> MetrikMesspunkt:
        return MetrikMesspunkt(
            messpunkt_id=f"MP-{wert}",
            workflow_typ=wf,
            metrik_typ=mt,
            wert=wert,
            einheit="Min",
            gemessen_am=datetime(2026, 1, 1),
            tenant_id="T",
        )

    def test_leere_liste_ergibt_null(self):
        assert aggregiere_messpunkte([], "wf_a", MetrikTyp.DURCHLAUFZEIT, MetrikAggregation.DURCHSCHNITT) == 0.0

    def test_falscher_workflow_typ_ergibt_null(self):
        mps = [self._mp(100.0)]
        result = aggregiere_messpunkte(mps, "wf_x", MetrikTyp.DURCHLAUFZEIT, MetrikAggregation.DURCHSCHNITT)
        assert result == 0.0

    def test_falscher_metrik_typ_ergibt_null(self):
        mps = [self._mp(100.0)]
        result = aggregiere_messpunkte(mps, "wf_a", MetrikTyp.FEHLERRATE, MetrikAggregation.DURCHSCHNITT)
        assert result == 0.0

    def test_minimum_mit_bekannten_werten(self):
        mps = [self._mp(10.0), self._mp(20.0), self._mp(5.0), self._mp(15.0)]
        result = aggregiere_messpunkte(mps, "wf_a", MetrikTyp.DURCHLAUFZEIT, MetrikAggregation.MINIMUM)
        assert result == 5.0

    def test_maximum_mit_bekannten_werten(self):
        mps = [self._mp(10.0), self._mp(20.0), self._mp(5.0), self._mp(15.0)]
        result = aggregiere_messpunkte(mps, "wf_a", MetrikTyp.DURCHLAUFZEIT, MetrikAggregation.MAXIMUM)
        assert result == 20.0

    def test_summe_mit_bekannten_werten(self):
        mps = [self._mp(10.0), self._mp(20.0), self._mp(30.0)]
        result = aggregiere_messpunkte(mps, "wf_a", MetrikTyp.DURCHLAUFZEIT, MetrikAggregation.SUMME)
        assert result == 60.0

    def test_durchschnitt_mit_bekannten_werten(self):
        mps = [self._mp(10.0), self._mp(20.0), self._mp(30.0)]
        result = aggregiere_messpunkte(mps, "wf_a", MetrikTyp.DURCHLAUFZEIT, MetrikAggregation.DURCHSCHNITT)
        assert result == 20.0

    def test_median_ungerade_anzahl(self):
        # Werte: 10, 30, 20 → sortiert: 10, 20, 30 → Median = 20
        mps = [self._mp(10.0), self._mp(30.0), self._mp(20.0)]
        result = aggregiere_messpunkte(mps, "wf_a", MetrikTyp.DURCHLAUFZEIT, MetrikAggregation.MEDIAN)
        assert result == 20.0

    def test_median_gerade_anzahl(self):
        # Werte: 10, 20, 30, 40 → sortiert: 10, 20, 30, 40 → Median = (20+30)/2 = 25
        mps = [self._mp(10.0), self._mp(40.0), self._mp(20.0), self._mp(30.0)]
        result = aggregiere_messpunkte(mps, "wf_a", MetrikTyp.DURCHLAUFZEIT, MetrikAggregation.MEDIAN)
        assert result == 25.0

    def test_median_einzelner_wert(self):
        mps = [self._mp(42.0)]
        result = aggregiere_messpunkte(mps, "wf_a", MetrikTyp.DURCHLAUFZEIT, MetrikAggregation.MEDIAN)
        assert result == 42.0

    def test_filtert_nach_metrik_typ(self):
        mps = [
            self._mp(100.0, mt=MetrikTyp.DURCHLAUFZEIT),
            self._mp(999.0, mt=MetrikTyp.WARTEZEIT),
        ]
        result = aggregiere_messpunkte(mps, "wf_a", MetrikTyp.DURCHLAUFZEIT, MetrikAggregation.MAXIMUM)
        assert result == 100.0

    def test_filtert_nach_workflow_typ(self):
        mps = [
            self._mp(50.0, wf="wf_a"),
            self._mp(999.0, wf="wf_b"),
        ]
        result = aggregiere_messpunkte(mps, "wf_a", MetrikTyp.DURCHLAUFZEIT, MetrikAggregation.SUMME)
        assert result == 50.0


# ===========================================================================
# Section 20: get_default_kpi_summaries
# ===========================================================================

class TestGetDefaultKpiSummaries:
    def test_gibt_4_summaries_zurueck(self, default_kpis):
        assert len(default_kpis) == 4

    def test_kontrakt_freigabe_ausgezeichnet(self, default_kpis):
        kpi = next(k for k in default_kpis if k.workflow_typ == "kontrakt_freigabe")
        assert kpi.performanz_bewertung == PerformanzBewertung.AUSGEZEICHNET
        assert kpi.sla_einhaltung_pct == 95.0

    def test_settlement_abrechnung_gut(self, default_kpis):
        kpi = next(k for k in default_kpis if k.workflow_typ == "settlement_abrechnung")
        assert kpi.performanz_bewertung == PerformanzBewertung.GUT
        assert kpi.sla_einhaltung_pct == 82.0

    def test_ap_rechnungseingang_kritisch(self, default_kpis):
        kpi = next(k for k in default_kpis if k.workflow_typ == "ap_rechnungseingang")
        assert kpi.performanz_bewertung == PerformanzBewertung.KRITISCH
        assert kpi.sla_einhaltung_pct == 58.0

    def test_qualitaets_freigabe_gut(self, default_kpis):
        kpi = next(k for k in default_kpis if k.workflow_typ == "qualitaets_freigabe")
        assert kpi.performanz_bewertung == PerformanzBewertung.GUT
        assert kpi.sla_einhaltung_pct == 88.0

    def test_custom_tenant_id_wird_gesetzt(self):
        kpis = get_default_kpi_summaries(tenant_id="MEIN-TENANT")
        assert all(k.tenant_id == "MEIN-TENANT" for k in kpis)

    def test_default_tenant_id_ist_tenant_001(self, default_kpis):
        assert all(k.tenant_id == "TENANT-001" for k in default_kpis)

    def test_alle_summaries_haben_periode_2026_q1(self, default_kpis):
        assert all(k.periode == "2026-Q1" for k in default_kpis)

    def test_kontrakt_freigabe_instanzen_gesamt(self, default_kpis):
        kpi = next(k for k in default_kpis if k.workflow_typ == "kontrakt_freigabe")
        assert kpi.instanzen_gesamt == 320

    def test_ap_rechnungseingang_instanzen_gesamt(self, default_kpis):
        kpi = next(k for k in default_kpis if k.workflow_typ == "ap_rechnungseingang")
        assert kpi.instanzen_gesamt == 500
