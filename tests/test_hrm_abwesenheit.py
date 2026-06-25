"""HRM-ABWESENHEIT-ANTRAG-001 — Unit Tests fuer HrmAbwesenheitService."""
from __future__ import annotations

from datetime import date

import pytest

from app.services.hrm_abwesenheit_service import (
    AbwesenheitKonfliktError,
    AbwesenheitStatus,
    AbwesenheitTyp,
    AntragNichtGefundenError,
    HrmAbwesenheitService,
    UngueltigerStatusUebergangError,
)


@pytest.fixture()
def svc() -> HrmAbwesenheitService:
    s = HrmAbwesenheitService(tenant_id="test")
    s.reset()
    return s


def _antrag(svc: HrmAbwesenheitService, *, von: str = "2026-07-01", bis: str = "2026-07-05"):
    return svc.antrag_stellen(
        mitarbeiter_nr="MA-001",
        typ=AbwesenheitTyp.URLAUB,
        von_datum=date.fromisoformat(von),
        bis_datum=date.fromisoformat(bis),
        beantragt_von="MA-001",
    )


class TestAntragStellen:
    def test_erstellt_antrag_mit_status_beantragt(self, svc):
        a = _antrag(svc)
        assert a.status == AbwesenheitStatus.BEANTRAGT
        assert a.antrag_id

    def test_arbeitstage_werden_berechnet(self, svc):
        # Mo 2026-07-06 bis Fr 2026-07-10 = 5 Werktage
        a = svc.antrag_stellen(
            mitarbeiter_nr="MA-001",
            typ=AbwesenheitTyp.URLAUB,
            von_datum=date(2026, 7, 6),
            bis_datum=date(2026, 7, 10),
            beantragt_von="MA-001",
        )
        assert a.arbeitstage == 5

    def test_wochenende_wird_nicht_gezaehlt(self, svc):
        # Sa-So = 0 Werktage
        a = svc.antrag_stellen(
            mitarbeiter_nr="MA-002",
            typ=AbwesenheitTyp.URLAUB,
            von_datum=date(2026, 7, 4),  # Samstag
            bis_datum=date(2026, 7, 5),  # Sonntag
            beantragt_von="MA-002",
        )
        assert a.arbeitstage == 0

    def test_bis_vor_von_raises(self, svc):
        with pytest.raises(ValueError):
            svc.antrag_stellen(
                mitarbeiter_nr="MA-001",
                typ=AbwesenheitTyp.URLAUB,
                von_datum=date(2026, 7, 10),
                bis_datum=date(2026, 7, 5),
                beantragt_von="MA-001",
            )

    def test_konflikt_mit_bestehendem_antrag_raises(self, svc):
        _antrag(svc, von="2026-07-01", bis="2026-07-05")
        with pytest.raises(AbwesenheitKonfliktError):
            _antrag(svc, von="2026-07-03", bis="2026-07-08")

    def test_kein_konflikt_bei_anderem_mitarbeiter(self, svc):
        _antrag(svc)
        a2 = svc.antrag_stellen(
            mitarbeiter_nr="MA-002",
            typ=AbwesenheitTyp.URLAUB,
            von_datum=date(2026, 7, 1),
            bis_datum=date(2026, 7, 5),
            beantragt_von="MA-002",
        )
        assert a2.status == AbwesenheitStatus.BEANTRAGT

    def test_to_dict_enthaelt_pflichtfelder(self, svc):
        a = _antrag(svc)
        d = a.to_dict()
        for k in ("antrag_id", "mitarbeiter_nr", "typ", "status", "arbeitstage",
                  "von_datum", "bis_datum", "eau_pflicht", "abgeschlossen"):
            assert k in d

    def test_krank_hat_eau_pflicht(self, svc):
        a = svc.antrag_stellen(
            mitarbeiter_nr="MA-001",
            typ=AbwesenheitTyp.KRANK,
            von_datum=date(2026, 7, 1),
            bis_datum=date(2026, 7, 3),
            beantragt_von="MA-001",
        )
        assert a.to_dict()["eau_pflicht"] is True

    def test_urlaub_keine_eau_pflicht(self, svc):
        a = _antrag(svc)
        assert a.to_dict()["eau_pflicht"] is False


class TestGenehmigung:
    def test_genehmigen_setzt_status(self, svc):
        a = _antrag(svc)
        g = svc.genehmigen(a.antrag_id, genehmigt_von="HR-LEITER")
        assert g.status == AbwesenheitStatus.GENEHMIGT
        assert g.genehmigt_von == "HR-LEITER"

    def test_doppeltes_genehmigen_raises(self, svc):
        a = _antrag(svc)
        svc.genehmigen(a.antrag_id, genehmigt_von="HR")
        with pytest.raises(UngueltigerStatusUebergangError):
            svc.genehmigen(a.antrag_id, genehmigt_von="HR")

    def test_ablehnen_setzt_status_und_grund(self, svc):
        a = _antrag(svc)
        ab = svc.ablehnen(a.antrag_id, abgelehnt_von="HR", grund="Kein Vertreter verfuegbar")
        assert ab.status == AbwesenheitStatus.ABGELEHNT
        assert ab.ablehnung_grund == "Kein Vertreter verfuegbar"

    def test_ablehnen_ohne_grund_raises(self, svc):
        a = _antrag(svc)
        with pytest.raises(ValueError):
            svc.ablehnen(a.antrag_id, abgelehnt_von="HR", grund="  ")

    def test_ablehnen_nach_genehmigung_raises(self, svc):
        a = _antrag(svc)
        svc.genehmigen(a.antrag_id, genehmigt_von="HR")
        with pytest.raises(UngueltigerStatusUebergangError):
            svc.ablehnen(a.antrag_id, abgelehnt_von="HR", grund="Zu spaet")


class TestZurueckziehen:
    def test_zurueckziehen_eigener_antrag(self, svc):
        a = _antrag(svc)
        z = svc.zurueckziehen(a.antrag_id, mitarbeiter_nr="MA-001")
        assert z.status == AbwesenheitStatus.ZURUECKGEZOGEN

    def test_zurueckziehen_fremder_antrag_raises(self, svc):
        a = _antrag(svc)
        with pytest.raises(PermissionError):
            svc.zurueckziehen(a.antrag_id, mitarbeiter_nr="MA-999")

    def test_zurueckziehen_nach_genehmigung_raises(self, svc):
        a = _antrag(svc)
        svc.genehmigen(a.antrag_id, genehmigt_von="HR")
        with pytest.raises(UngueltigerStatusUebergangError):
            svc.zurueckziehen(a.antrag_id, mitarbeiter_nr="MA-001")


class TestListUndGet:
    def test_not_found_raises(self, svc):
        with pytest.raises(AntragNichtGefundenError):
            svc.get("nicht-vorhanden")

    def test_list_alle(self, svc):
        _antrag(svc, von="2026-07-01", bis="2026-07-05")
        svc.antrag_stellen(
            mitarbeiter_nr="MA-002",
            typ=AbwesenheitTyp.KRANK,
            von_datum=date(2026, 8, 1),
            bis_datum=date(2026, 8, 3),
            beantragt_von="MA-002",
        )
        result = svc.list_antraege()
        assert len(result) == 2

    def test_list_filter_mitarbeiter(self, svc):
        _antrag(svc)
        svc.antrag_stellen(
            mitarbeiter_nr="MA-002",
            typ=AbwesenheitTyp.URLAUB,
            von_datum=date(2026, 8, 1),
            bis_datum=date(2026, 8, 5),
            beantragt_von="MA-002",
        )
        result = svc.list_antraege(mitarbeiter_nr="MA-001")
        assert all(a.mitarbeiter_nr == "MA-001" for a in result)

    def test_list_filter_status(self, svc):
        a = _antrag(svc)
        svc.genehmigen(a.antrag_id, genehmigt_von="HR")
        result = svc.list_antraege(status=AbwesenheitStatus.GENEHMIGT)
        assert all(a.status == AbwesenheitStatus.GENEHMIGT for a in result)

    def test_tenant_isolation(self, svc):
        _antrag(svc)
        andere = HrmAbwesenheitService(tenant_id="other-tenant")
        assert len(andere.list_antraege()) == 0


class TestUrlaubskonto:
    def test_urlaubskonto_leer(self, svc):
        konto = svc.urlaubskonto("MA-001", 2026)
        assert konto["verbraucht_tage"] == 0
        assert konto["resturlaub_tage"] == 30

    def test_urlaubskonto_mit_genehmigtem_urlaub(self, svc):
        a = svc.antrag_stellen(
            mitarbeiter_nr="MA-001",
            typ=AbwesenheitTyp.URLAUB,
            von_datum=date(2026, 7, 6),
            bis_datum=date(2026, 7, 10),
            beantragt_von="MA-001",
        )
        svc.genehmigen(a.antrag_id, genehmigt_von="HR")
        konto = svc.urlaubskonto("MA-001", 2026)
        assert konto["verbraucht_tage"] == 5
        assert konto["resturlaub_tage"] == 25

    def test_abgelehnter_urlaub_zaehlt_nicht(self, svc):
        a = svc.antrag_stellen(
            mitarbeiter_nr="MA-001",
            typ=AbwesenheitTyp.URLAUB,
            von_datum=date(2026, 7, 6),
            bis_datum=date(2026, 7, 10),
            beantragt_von="MA-001",
        )
        svc.ablehnen(a.antrag_id, abgelehnt_von="HR", grund="Kein Vertreter")
        konto = svc.urlaubskonto("MA-001", 2026)
        assert konto["verbraucht_tage"] == 0
