"""Unit-Tests für Fachliche Vertiefung Wave 10.

Warengruppen (3-stufig), Erlöskennziffern [EKZS/EKZZ], Zahlungsbedingungen [ZABD].
"""
import pytest
from datetime import date


class TestWarengruppen:
    def test_hauptwarengruppe_schema(self):
        from app.api.v1.endpoints.warengruppen import HauptwarengruppeCreate
        h = HauptwarengruppeCreate(gruppe_nr="G01", bezeichnung="Getreide")
        assert h.gruppe_nr == "G01"

    def test_oberwarengruppe_schema(self):
        from app.api.v1.endpoints.warengruppen import OberwarengruppeCreate
        o = OberwarengruppeCreate(gruppe_nr="O01", bezeichnung="Brotgetreide", haupt_id="h-1")
        assert o.haupt_id == "h-1"

    def test_warengruppe_schema(self):
        from app.api.v1.endpoints.warengruppen import WarengruppeCreate
        w = WarengruppeCreate(gruppe_nr="W01", bezeichnung="Weizen A", ober_id="o-1")
        assert w.ober_id == "o-1"

    def test_hierarchie_out_schema(self):
        from app.api.v1.endpoints.warengruppen import (
            WarengruppeHierarchieOut, WarengruppeOut, OberwarengruppeOut, HauptwarengruppeOut
        )
        from datetime import datetime
        hw = HauptwarengruppeOut(id="h1", gruppe_nr="G01", bezeichnung="Getreide", aktiv=True, created_at=datetime.now())
        ow = OberwarengruppeOut(id="o1", gruppe_nr="O01", bezeichnung="Brotgetreide", haupt_id="h1", aktiv=True, created_at=datetime.now())
        wg = WarengruppeOut(id="w1", gruppe_nr="W01", bezeichnung="Weizen A", ober_id="o1", aktiv=True, created_at=datetime.now())
        hier = WarengruppeHierarchieOut(warengruppe=wg, oberwarengruppe=ow, hauptwarengruppe=hw)
        assert hier.hauptwarengruppe.gruppe_nr == "G01"
        assert hier.oberwarengruppe.gruppe_nr == "O01"
        assert hier.warengruppe.gruppe_nr == "W01"

    def test_gruppe_nr_max_length(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.warengruppen import HauptwarengruppeCreate
        with pytest.raises(ValidationError):
            HauptwarengruppeCreate(gruppe_nr="A" * 21, bezeichnung="Zu lang")


class TestErloeskennziffern:
    def test_ekz_create_schema(self):
        from app.api.v1.endpoints.erloeskennziffern import ErloeskennzifferCreate
        e = ErloeskennzifferCreate(ekz_nr="EKZ-01", bezeichnung="Standard Inland VK")
        assert e.ekz_nr == "EKZ-01"

    def test_ekz_nr_max_length(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.erloeskennziffern import ErloeskennzifferCreate
        with pytest.raises(ValidationError):
            ErloeskennzifferCreate(ekz_nr="E" * 21, bezeichnung="Zu lang")

    def test_kontenzuordnung_schema(self):
        from app.api.v1.endpoints.erloeskennziffern import ErloeskontenzuordnungCreate
        z = ErloeskontenzuordnungCreate(
            ekz_id="ekz-1",
            gueltig_ab=date(2024, 1, 1),
            steuerschluessel="19",
            konto_erloese="8400",
            konto_aufwand="3400",
            konto_umsatzsteuer="1776",
            konto_vorsteuer="1576",
        )
        assert z.konto_erloese == "8400"
        assert z.steuerschluessel == "19"

    def test_kontenzuordnung_alle_optional(self):
        from app.api.v1.endpoints.erloeskennziffern import ErloeskontenzuordnungCreate
        z = ErloeskontenzuordnungCreate(ekz_id="ekz-1", gueltig_ab=date(2024, 1, 1))
        assert z.konto_erloese is None
        assert z.steuerschluessel is None

    def test_lookup_result_schema(self):
        from app.api.v1.endpoints.erloeskennziffern import KontoLookupResult
        r = KontoLookupResult(
            ekz_nr="EKZ-01",
            konto_erloese="8400",
            konto_aufwand=None,
            konto_umsatzsteuer="1776",
            konto_vorsteuer=None,
            gueltig_ab=date(2024, 1, 1),
        )
        assert r.ekz_nr == "EKZ-01"
        assert r.gueltig_ab == date(2024, 1, 1)

    def test_gueltig_ab_zukunft(self):
        from app.api.v1.endpoints.erloeskennziffern import ErloeskontenzuordnungCreate
        z = ErloeskontenzuordnungCreate(
            ekz_id="ekz-1",
            gueltig_ab=date(2025, 1, 1),
            konto_erloese="8500",
        )
        assert z.gueltig_ab == date(2025, 1, 1)


class TestZahlungsbedingungen:
    def test_create_standard(self):
        from app.api.v1.endpoints.zahlungsbedingungen import ZahlungsbedingungCreate
        z = ZahlungsbedingungCreate(
            zabd_nr="30T",
            bezeichnung="30 Tage netto",
            zahlungsziel_tage=30,
        )
        assert z.zahlungsziel_tage == 30
        assert z.manuelles_datum is False
        assert z.zahlungsart == "ueberweisung"

    def test_create_mit_skonto(self):
        from app.api.v1.endpoints.zahlungsbedingungen import ZahlungsbedingungCreate
        z = ZahlungsbedingungCreate(
            zabd_nr="S2-10",
            bezeichnung="10 Tage 2% Skonto, 30 Tage netto",
            zahlungsziel_tage=30,
            skonto1_tage=10,
            skonto1_prozent=2.0,
            skonto2_tage=20,
            skonto2_prozent=1.0,
        )
        assert z.skonto1_prozent == 2.0
        assert z.skonto2_tage == 20

    def test_zahlungsarten(self):
        from app.api.v1.endpoints.zahlungsbedingungen import GUELTIGE_ZAHLUNGSARTEN
        assert "ueberweisung" in GUELTIGE_ZAHLUNGSARTEN
        assert "lastschrift" in GUELTIGE_ZAHLUNGSARTEN
        assert "scheck" in GUELTIGE_ZAHLUNGSARTEN
        assert "kasse" in GUELTIGE_ZAHLUNGSARTEN
        assert "vorkasse" in GUELTIGE_ZAHLUNGSARTEN

    def test_ungueltige_zahlungsart(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.zahlungsbedingungen import ZahlungsbedingungCreate
        with pytest.raises((ValueError, ValidationError)):
            ZahlungsbedingungCreate(
                zabd_nr="X",
                bezeichnung="Test",
                zahlungsart="bargeld",
            )

    def test_manuelles_datum(self):
        from app.api.v1.endpoints.zahlungsbedingungen import ZahlungsbedingungCreate
        z = ZahlungsbedingungCreate(
            zabd_nr="MAN",
            bezeichnung="Manuelles Fälligkeitsdatum",
            manuelles_datum=True,
            zahlungsart="lastschrift",
        )
        assert z.manuelles_datum is True

    def test_vorkasse(self):
        from app.api.v1.endpoints.zahlungsbedingungen import ZahlungsbedingungCreate
        z = ZahlungsbedingungCreate(
            zabd_nr="VK",
            bezeichnung="Vorkasse",
            zahlungsziel_tage=0,
            zahlungsart="vorkasse",
        )
        assert z.zahlungsziel_tage == 0
        assert z.zahlungsart == "vorkasse"
