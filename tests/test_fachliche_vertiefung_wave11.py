"""Unit-Tests für Fachliche Vertiefung Wave 11.

Partiestamm [PAR/PGR], Forderungsgruppen [FORG], Periodische Buchungen [WZA].
"""
import pytest
from datetime import date
from decimal import Decimal


class TestPartiegruppen:
    def test_create_schema(self):
        from app.api.v1.endpoints.partiestamm import PartiegruppeCreate
        g = PartiegruppeCreate(gruppe_nr="PG-GETREIDE", bezeichnung="Getreide-Partien")
        assert g.gruppe_nr == "PG-GETREIDE"

    def test_gruppe_nr_max_length(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.partiestamm import PartiegruppeCreate
        with pytest.raises(ValidationError):
            PartiegruppeCreate(gruppe_nr="P" * 21, bezeichnung="Zu lang")


class TestPartiestamm:
    def test_create_artikelstamm_typ(self):
        from app.api.v1.endpoints.partiestamm import PartiestammCreate
        p = PartiestammCreate(
            partie_nr="PAR-2024-001",
            artikel_nr="WEIZEN-A",
            partie_typ="artikelstamm",
            erntejahr=2024,
            herkunftsland="DE",
        )
        assert p.partie_typ == "artikelstamm"
        assert p.erntejahr == 2024

    def test_create_artikel_lager_typ(self):
        from app.api.v1.endpoints.partiestamm import PartiestammCreate
        p = PartiestammCreate(
            artikel_nr="GERSTE",
            partie_typ="artikel_lager",
            lager_nr="SILO-01",
        )
        assert p.lager_nr == "SILO-01"

    def test_artikel_lager_ohne_lager_fehler(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.partiestamm import PartiestammCreate
        with pytest.raises((ValueError, ValidationError)):
            PartiestammCreate(
                artikel_nr="GERSTE",
                partie_typ="artikel_lager",
                # lager_nr fehlt
            )

    def test_ungueltige_typ_fehler(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.partiestamm import PartiestammCreate
        with pytest.raises((ValueError, ValidationError)):
            PartiestammCreate(
                artikel_nr="GERSTE",
                partie_typ="ungueltig",
            )

    def test_status_werte(self):
        from app.api.v1.endpoints.partiestamm import GUELTIGE_STATUS
        assert "aktiv" in GUELTIGE_STATUS
        assert "gesperrt" in GUELTIGE_STATUS
        assert "abgeschlossen" in GUELTIGE_STATUS

    def test_automatische_nummer_none(self):
        from app.api.v1.endpoints.partiestamm import PartiestammCreate
        p = PartiestammCreate(artikel_nr="WEIZEN", partie_typ="artikelstamm")
        assert p.partie_nr is None  # wird serverseitig generiert

    def test_umbuchung_schema(self):
        from app.api.v1.endpoints.partiestamm import PartieUmbuchungCreate
        u = PartieUmbuchungCreate(
            ziel_lager_nr="SILO-02",
            menge=500.0,
            bemerkung="Umlagerung nach Siloumbau",
        )
        assert u.ziel_lager_nr == "SILO-02"
        assert u.menge == 500.0

    def test_herkunftsland_max_3(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.partiestamm import PartiestammCreate
        with pytest.raises(ValidationError):
            PartiestammCreate(
                artikel_nr="WEIZEN",
                partie_typ="artikelstamm",
                herkunftsland="DEUR",  # 4 Zeichen, max 3
            )


class TestForderungsgruppen:
    def test_create_mit_konten(self):
        from app.api.v1.endpoints.forderungsgruppen import ForderungsgruppeCreate
        f = ForderungsgruppeCreate(
            gruppe_nr="GK",
            bezeichnung="Großkunden",
            konto_forderungen="1400",
            konto_verbindlichkeiten="1600",
            konto_sammel_1="1401",
        )
        assert f.konto_forderungen == "1400"
        assert f.konto_sammel_1 == "1401"

    def test_create_nur_pflichtfelder(self):
        from app.api.v1.endpoints.forderungsgruppen import ForderungsgruppeCreate
        f = ForderungsgruppeCreate(gruppe_nr="LW", bezeichnung="Landwirte")
        assert f.konto_forderungen is None
        assert f.konto_sammel_1 is None

    def test_verschiedene_gruppen(self):
        from app.api.v1.endpoints.forderungsgruppen import ForderungsgruppeCreate
        gruppen = [
            ForderungsgruppeCreate(gruppe_nr="GK", bezeichnung="Großkunden", konto_forderungen="1400"),
            ForderungsgruppeCreate(gruppe_nr="LW", bezeichnung="Landwirte", konto_forderungen="1410"),
            ForderungsgruppeCreate(gruppe_nr="BH", bezeichnung="Baustoffhändler", konto_forderungen="1420"),
        ]
        assert len(gruppen) == 3
        assert all(g.konto_forderungen is not None for g in gruppen)


class TestPeriodischeBuchungen:
    def test_create_monatlich(self):
        from app.api.v1.endpoints.periodische_buchungen import PeriodischeBuchungCreate
        b = PeriodischeBuchungCreate(
            bezeichnung="Miete Büro",
            konto="4210",
            gegenkonto="1200",
            betrag=Decimal("1500.00"),
            turnus="monatlich",
            gueltig_ab=date(2024, 1, 1),
        )
        assert b.betrag == Decimal("1500.00")
        assert b.turnus == "monatlich"
        assert b.gesperrt is False

    def test_turnus_werte(self):
        from app.api.v1.endpoints.periodische_buchungen import GUELTIGE_TURNUS
        assert "monatlich" in GUELTIGE_TURNUS
        assert "quartalsweise" in GUELTIGE_TURNUS
        assert "halbjaehrlich" in GUELTIGE_TURNUS
        assert "jaehrlich" in GUELTIGE_TURNUS
        assert "einmalig" in GUELTIGE_TURNUS

    def test_vorgangsklassen(self):
        from app.api.v1.endpoints.periodische_buchungen import GUELTIGE_VORGANGSKLASSEN
        assert "ZA" in GUELTIGE_VORGANGSKLASSEN
        assert "ER" in GUELTIGE_VORGANGSKLASSEN
        assert "AR" in GUELTIGE_VORGANGSKLASSEN

    def test_ungueltige_turnus(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.periodische_buchungen import PeriodischeBuchungCreate
        with pytest.raises((ValueError, ValidationError)):
            PeriodischeBuchungCreate(
                bezeichnung="Test",
                konto="4210",
                gegenkonto="1200",
                betrag=Decimal("100"),
                turnus="taeglich",
                gueltig_ab=date(2024, 1, 1),
            )

    def test_gesperrt_flag(self):
        from app.api.v1.endpoints.periodische_buchungen import PeriodischeBuchungCreate
        b = PeriodischeBuchungCreate(
            bezeichnung="AfA PKW",
            konto="4830",
            gegenkonto="0320",
            betrag=Decimal("250.00"),
            turnus="monatlich",
            gueltig_ab=date(2024, 1, 1),
            gesperrt=True,
        )
        assert b.gesperrt is True

    def test_gueltig_bis_optional(self):
        from app.api.v1.endpoints.periodische_buchungen import PeriodischeBuchungCreate
        b = PeriodischeBuchungCreate(
            bezeichnung="Dauerauftrag unbefristet",
            konto="4200",
            gegenkonto="1200",
            betrag=Decimal("800"),
            turnus="monatlich",
            gueltig_ab=date(2024, 1, 1),
        )
        assert b.gueltig_bis is None

    def test_mit_laufzeit(self):
        from app.api.v1.endpoints.periodische_buchungen import PeriodischeBuchungCreate
        b = PeriodischeBuchungCreate(
            bezeichnung="Leasing 24 Monate",
            konto="4570",
            gegenkonto="1200",
            betrag=Decimal("650.00"),
            turnus="monatlich",
            gueltig_ab=date(2024, 1, 1),
            gueltig_bis=date(2025, 12, 31),
        )
        assert b.gueltig_bis == date(2025, 12, 31)
