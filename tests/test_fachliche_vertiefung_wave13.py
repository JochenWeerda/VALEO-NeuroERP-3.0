"""Unit-Tests für Fachliche Vertiefung Wave 13.

Zahlungsformulare [FIZAF], Zinsgruppen, Leergutarten [LEER].
"""
import pytest
from decimal import Decimal


class TestZahlungsformulare:
    def test_create_ausgang(self):
        from app.api.v1.endpoints.fibu_stammdaten import ZahlungsformularCreate
        f = ZahlungsformularCreate(
            formular_nr="ZF-UEBW-01",
            bezeichnung="Überweisung Volksbank",
            formularklasse="ausgang",
            bank_blz="28090012",
        )
        assert f.formularklasse == "ausgang"
        assert f.bank_blz == "28090012"

    def test_create_eingang(self):
        from app.api.v1.endpoints.fibu_stammdaten import ZahlungsformularCreate
        f = ZahlungsformularCreate(
            formular_nr="ZF-EZV-01",
            bezeichnung="Einzugsermächtigung",
            formularklasse="eingang",
        )
        assert f.formularklasse == "eingang"

    def test_formularklassen(self):
        from app.api.v1.endpoints.fibu_stammdaten import GUELTIGE_FORMULARKLASSEN
        assert "eingang" in GUELTIGE_FORMULARKLASSEN
        assert "ausgang" in GUELTIGE_FORMULARKLASSEN

    def test_ungueltige_formularklasse(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.fibu_stammdaten import ZahlungsformularCreate
        with pytest.raises((ValueError, ValidationError)):
            ZahlungsformularCreate(
                formular_nr="X",
                bezeichnung="Test",
                formularklasse="intern",
            )

    def test_ohne_bank(self):
        from app.api.v1.endpoints.fibu_stammdaten import ZahlungsformularCreate
        f = ZahlungsformularCreate(
            formular_nr="ZF-STD",
            bezeichnung="Standard",
            formularklasse="ausgang",
        )
        assert f.bank_blz is None
        assert f.bank_iban is None


class TestZinsgruppen:
    def test_create_standard(self):
        from app.api.v1.endpoints.fibu_stammdaten import ZinsgruppeCreate
        z = ZinsgruppeCreate(
            gruppe_nr="ZG-A",
            bezeichnung="Kontokorrentzinsen Standard",
            zinssatz=Decimal("8.5"),
            zinsmethode="act_360",
        )
        assert z.zinssatz == Decimal("8.5")
        assert z.zinsmethode == "act_360"

    def test_zinsmethoden(self):
        from app.api.v1.endpoints.fibu_stammdaten import GUELTIGE_ZINSMETHODEN
        assert "act_act" in GUELTIGE_ZINSMETHODEN
        assert "act_360" in GUELTIGE_ZINSMETHODEN
        assert "act_365" in GUELTIGE_ZINSMETHODEN
        assert "30_360" in GUELTIGE_ZINSMETHODEN

    def test_ungueltige_zinsmethode(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.fibu_stammdaten import ZinsgruppeCreate
        with pytest.raises((ValueError, ValidationError)):
            ZinsgruppeCreate(
                gruppe_nr="ZG-X",
                bezeichnung="Test",
                zinssatz=Decimal("5.0"),
                zinsmethode="monatlich",
            )

    def test_mit_konten(self):
        from app.api.v1.endpoints.fibu_stammdaten import ZinsgruppeCreate
        z = ZinsgruppeCreate(
            gruppe_nr="ZG-B",
            bezeichnung="Mahnzinsen",
            zinssatz=Decimal("12.0"),
            konto_zinsen="7000",
            konto_zinsabschlagsteuer="7001",
            schwellwert_tage=14,
        )
        assert z.konto_zinsen == "7000"
        assert z.schwellwert_tage == 14

    def test_zinssatz_range(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.fibu_stammdaten import ZinsgruppeCreate
        with pytest.raises(ValidationError):
            ZinsgruppeCreate(
                gruppe_nr="ZG-HIGH",
                bezeichnung="Unrealistisch",
                zinssatz=Decimal("150.0"),
            )


class TestLeergutarten:
    def test_create_palette(self):
        from app.api.v1.endpoints.fibu_stammdaten import LeergutArtCreate
        l = LeergutArtCreate(
            art_nr="LG-EUR-PAL",
            bezeichnung="EUR-Palette",
            leergut_typ="palette",
            pfandwert=Decimal("10.50"),
            konto_leergut="3200",
        )
        assert l.leergut_typ == "palette"
        assert l.pfandwert == Decimal("10.50")

    def test_create_bigbag(self):
        from app.api.v1.endpoints.fibu_stammdaten import LeergutArtCreate
        l = LeergutArtCreate(
            art_nr="LG-BIGBAG",
            bezeichnung="Big-Bag 1000kg",
            leergut_typ="bigbag",
            pfandwert=Decimal("5.00"),
        )
        assert l.leergut_typ == "bigbag"

    def test_leergut_typen(self):
        from app.api.v1.endpoints.fibu_stammdaten import GUELTIGE_LEERGUT_ARTEN
        assert "palette" in GUELTIGE_LEERGUT_ARTEN
        assert "bigbag" in GUELTIGE_LEERGUT_ARTEN
        assert "fass" in GUELTIGE_LEERGUT_ARTEN
        assert "flasche" in GUELTIGE_LEERGUT_ARTEN
        assert "behaelter" in GUELTIGE_LEERGUT_ARTEN

    def test_ungueltige_leergut_art(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.fibu_stammdaten import LeergutArtCreate
        with pytest.raises((ValueError, ValidationError)):
            LeergutArtCreate(
                art_nr="X",
                bezeichnung="Test",
                leergut_typ="kiste",
            )

    def test_ohne_pfandwert(self):
        from app.api.v1.endpoints.fibu_stammdaten import LeergutArtCreate
        l = LeergutArtCreate(
            art_nr="LG-SACK",
            bezeichnung="Jutesack",
            leergut_typ="sonstige",
        )
        assert l.pfandwert is None
