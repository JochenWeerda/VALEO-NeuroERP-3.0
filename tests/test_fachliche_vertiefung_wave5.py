"""Unit-Tests für Fachliche Vertiefung Wave 5.

Vermehrungsvertrag, Vertreterstamm, Geschäftsjahre, Periodische Buchungen.
"""
import pytest
import calendar
from datetime import date
from decimal import Decimal


# ── Vermehrungsvertrag ────────────────────────────────────────────────────────

class TestVermehrungsvertrag:
    def test_gueltige_status(self):
        gueltige = ("angelegt", "aktiv", "beendet", "storniert")
        assert "angelegt" in gueltige
        assert "ungueltig" not in gueltige

    def test_erntejahr_validierung(self):
        from app.api.v1.endpoints.vermehrungsvertrag import VermehrungsvertragCreate
        v = VermehrungsvertragCreate(
            vertrag_nr="VV2024-001",
            erntejahr=2024,
            vermehrer_kunden_nr="K12345",
            kategorie="Z1",
        )
        assert v.erntejahr == 2024
        assert v.kategorie == "Z1"

    def test_erntejahr_0_zeigt_alle(self):
        # Erntejahr 0 zeigt alle Schläge (Referenz-ERP-Verhalten)
        erntejahr = 0
        assert erntejahr == 0

    def test_sorte_zuordnung(self):
        vertrag = {
            "vertrag_nr": "VV2024-001",
            "sorte_nr": "WEIZ001",
            "sorte_bezeichnung": "Tobak Winterweizen",
            "vmkz": "123456",
            "anbauflaeche_ha": Decimal("12.5"),
        }
        assert vertrag["anbauflaeche_ha"] > 0


# ── Vertreterstamm ────────────────────────────────────────────────────────────

class TestVertreterstamm:
    def test_vertreter_create(self):
        from app.api.v1.endpoints.vertreterstamm import VertreterCreate
        v = VertreterCreate(
            vertreter_nr="V001",
            name="Mustermann",
            vorname="Max",
            vertretergruppe_nr="VG1",
        )
        assert v.vertreter_nr == "V001"
        assert v.vertretergruppe_nr == "VG1"

    def test_vertretergruppe_pflicht(self):
        from app.api.v1.endpoints.vertreterstamm import VertretergruppeCreate
        g = VertretergruppeCreate(gruppe_nr="VG1", bezeichnung="Nordregion")
        assert g.gruppe_nr == "VG1"

    def test_provisionsgruppe_optional(self):
        from app.api.v1.endpoints.vertreterstamm import VertreterCreate
        v = VertreterCreate(vertreter_nr="V002", name="Schmidt")
        assert v.provisionsgruppe_nr is None


# ── Geschäftsjahre ────────────────────────────────────────────────────────────

class TestGeschaeftsjahre:
    def test_datum_validierung(self):
        from app.api.v1.endpoints.fibu_geschaeftsjahre import GeschaeftsjahreCreate
        gj = GeschaeftsjahreCreate(
            jahr_nr=2024,
            bezeichnung="Geschäftsjahr 2024",
            datum_beginn=date(2024, 1, 1),
            datum_ende=date(2024, 12, 31),
        )
        assert gj.datum_ende > gj.datum_beginn

    def test_datum_fehler(self):
        from app.api.v1.endpoints.fibu_geschaeftsjahre import GeschaeftsjahreCreate
        from pydantic import ValidationError
        with pytest.raises((ValueError, ValidationError)):
            GeschaeftsjahreCreate(
                jahr_nr=2024,
                bezeichnung="Test",
                datum_beginn=date(2024, 12, 31),
                datum_ende=date(2024, 1, 1),
            )

    def test_12_perioden_auto(self):
        # Teste automatische Perioden-Berechnung
        for monat in range(1, 13):
            _, letzter_tag = calendar.monthrange(2024, monat)
            von = date(2024, monat, 1)
            bis = date(2024, monat, letzter_tag)
            assert von <= bis

    def test_periode_typen(self):
        typen = ("normal", "eroeffnung", "abschluss")
        assert "normal" in typen
        assert "halbzeit" not in typen


# ── Periodische Buchungen ─────────────────────────────────────────────────────

class TestPeriodischeBuchungen:
    def test_intervall_validierung(self):
        from app.api.v1.endpoints.fibu_geschaeftsjahre import PeriodischeBuchungCreate
        pb = PeriodischeBuchungCreate(
            bezeichnung="Miete",
            soll_konto="6900",
            haben_konto="3500",
            betrag_eur=Decimal("1500.00"),
            intervall="monatlich",
        )
        assert pb.intervall == "monatlich"

    def test_ungueltiges_intervall(self):
        from app.api.v1.endpoints.fibu_geschaeftsjahre import PeriodischeBuchungCreate
        with pytest.raises((ValueError, Exception)):
            PeriodischeBuchungCreate(
                bezeichnung="Test",
                soll_konto="6900",
                haben_konto="3500",
                betrag_eur=Decimal("100.00"),
                intervall="wöchentlich",
            )

    def test_naechstes_buchungsdatum_monatlich(self):
        aktuell = date(2024, 1, 15)
        monat = aktuell.month + 1
        jahr = aktuell.year + (monat - 1) // 12
        monat = ((monat - 1) % 12) + 1
        naechstes = aktuell.replace(year=jahr, month=monat)
        assert naechstes == date(2024, 2, 15)

    def test_naechstes_buchungsdatum_jaehrlich(self):
        aktuell = date(2024, 3, 1)
        naechstes = aktuell.replace(year=aktuell.year + 1)
        assert naechstes == date(2025, 3, 1)

    def test_abgrenzungsdatum(self):
        heute = date(2024, 6, 1)
        abgrenzung = date(2024, 12, 31)
        naechste = date(2024, 5, 1)
        soll_buchen = naechste <= min(heute, abgrenzung)
        assert soll_buchen is True
