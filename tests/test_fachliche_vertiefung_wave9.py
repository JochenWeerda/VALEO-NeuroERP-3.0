"""Unit-Tests für Fachliche Vertiefung Wave 9.

Betriebsstätten/Filialen, Individuelle Artikelnummern, Versandprofile, Avise.
"""
import pytest
from datetime import date


class TestBetriebsstaetten:
    def test_create_zentrale(self):
        from app.api.v1.endpoints.betriebsstaetten import BetriebsstaetteCreate
        b = BetriebsstaetteCreate(
            filial_nr="0001",
            bezeichnung="Hauptstelle Hannover",
            ist_zentrale=True,
            plz="30159",
            ort="Hannover",
            land="DE",
        )
        assert b.ist_zentrale is True
        assert b.zentrale_filial_nr is None

    def test_create_filiale(self):
        from app.api.v1.endpoints.betriebsstaetten import BetriebsstaetteCreate
        f = BetriebsstaetteCreate(
            filial_nr="0002",
            bezeichnung="Filiale Braunschweig",
            ist_zentrale=False,
            zentrale_filial_nr="0001",
            ident_untergrenze=1000,
            ident_obergrenze=1999,
        )
        assert f.zentrale_filial_nr == "0001"
        assert f.ident_untergrenze == 1000

    def test_ident_bereich(self):
        from app.api.v1.endpoints.betriebsstaetten import BetriebsstaetteCreate
        f = BetriebsstaetteCreate(
            filial_nr="0003",
            bezeichnung="Filiale Celle",
            ident_untergrenze=2000,
            ident_obergrenze=2999,
        )
        assert f.ident_obergrenze - f.ident_untergrenze == 999


class TestIndividuelleArtikelnummern:
    def test_create_kunden_nummer(self):
        from app.api.v1.endpoints.individuelle_artikelnummern import IndivArtikelNrCreate
        ia = IndivArtikelNrCreate(
            artikel_nr="ART-001",
            partner_nr="K001",
            partner_typ="kunden",
            indiv_artikel_nr="KD-ART-001",
            indiv_bezeichnung="Artikel laut Kundenkatalog",
        )
        assert ia.partner_typ == "kunden"
        assert ia.indiv_artikel_nr == "KD-ART-001"

    def test_create_lieferanten_nummer(self):
        from app.api.v1.endpoints.individuelle_artikelnummern import IndivArtikelNrCreate
        ia = IndivArtikelNrCreate(
            artikel_nr="ART-002",
            partner_nr="L001",
            partner_typ="lieferanten",
            indiv_artikel_nr="LF-X-9900",
            gueltig_von=date(2024, 1, 1),
        )
        assert ia.partner_typ == "lieferanten"
        assert ia.gueltig_von == date(2024, 1, 1)

    def test_ungueltige_partner_typ(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.individuelle_artikelnummern import IndivArtikelNrCreate
        with pytest.raises(ValidationError):
            IndivArtikelNrCreate(
                artikel_nr="ART-003",
                partner_nr="X001",
                partner_typ="ungueltig",
                indiv_artikel_nr="X-001",
            )


class TestVersandprofile:
    def test_create_email_profil(self):
        from app.api.v1.endpoints.versandprofile import VersandprofilCreate
        p = VersandprofilCreate(
            profil_nr="VP-EMAIL-01",
            bezeichnung="Standard Email Versand",
            versandart="email",
            smtp_server="mail.example.com",
            smtp_port=587,
            absender_email="erp@example.com",
            absender_name="VALEO ERP",
            archiv_kennzeichen=True,
        )
        assert p.versandart == "email"
        assert p.smtp_port == 587

    def test_versandarten(self):
        from app.api.v1.endpoints.versandprofile import GUELTIGE_VERSANDARTEN
        assert "email" in GUELTIGE_VERSANDARTEN
        assert "fax" in GUELTIGE_VERSANDARTEN
        assert "edi" in GUELTIGE_VERSANDARTEN

    def test_create_avis(self):
        from app.api.v1.endpoints.versandprofile import LieferavisCreate
        from decimal import Decimal
        a = LieferavisCreate(
            avis_nr="AV-001",
            lieferant_nr="L001",
            avis_datum=date(2024, 6, 1),
            lieferdatum_erwartet=date(2024, 6, 5),
            artikel_nr="ART-001",
            menge=Decimal("500"),
            mengeneinheit="t",
        )
        assert a.avis_nr == "AV-001"
        assert a.menge == Decimal("500")

    def test_avis_status_workflow(self):
        from app.api.v1.endpoints.versandprofile import GUELTIGE_AVIS_STATUS
        status_offen = "offen"
        assert "bestaetigt" in GUELTIGE_AVIS_STATUS
        assert "abgeschlossen" in GUELTIGE_AVIS_STATUS
        assert "storniert" in GUELTIGE_AVIS_STATUS
        assert status_offen in GUELTIGE_AVIS_STATUS

    def test_avis_ohne_nummer_generiert(self):
        from app.api.v1.endpoints.versandprofile import LieferavisCreate
        from decimal import Decimal
        a = LieferavisCreate(
            avis_datum=date(2024, 6, 1),
            lieferant_nr="L002",
            menge=Decimal("100"),
            mengeneinheit="kg",
        )
        assert a.avis_nr is None  # wird serverseitig generiert
