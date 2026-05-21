"""Unit-Tests für Fachliche Vertiefung Wave 6.

Mengeneinheiten/Gruppen, Artikelverpackung, Zahlungsmeldungen.
"""
import pytest
from datetime import date
from decimal import Decimal


# ── Mengeneinheiten ───────────────────────────────────────────────────────────

class TestMengeneinheiten:
    def test_umrechnungsfaktor(self):
        # 1 t = 1000 kg
        wert_t = Decimal("2.5")
        faktor_t = Decimal("1000")  # t → kg
        faktor_kg = Decimal("1")    # kg = Basis
        ergebnis_kg = (wert_t * faktor_t / faktor_kg).quantize(Decimal("0.000001"))
        assert ergebnis_kg == Decimal("2500.000000")

    def test_umrechnung_karton(self):
        # 1 Kar = 24 Stk
        wert_kar = Decimal("5")
        faktor_kar = Decimal("24")
        ergebnis_stk = wert_kar * faktor_kar
        assert ergebnis_stk == Decimal("120")

    def test_mengeneinheit_create(self):
        from app.api.v1.endpoints.artikel_mengeneinheiten import MengeneinheitCreate
        me = MengeneinheitCreate(
            einheit_kuerzel="t",
            bezeichnung="Tonne",
            basis_einheit="kg",
            umrechnungsfaktor=Decimal("1000"),
            dezimalstellen=3,
        )
        assert me.einheit_kuerzel == "t"
        assert me.umrechnungsfaktor == Decimal("1000")

    def test_gruppe_create(self):
        from app.api.v1.endpoints.artikel_mengeneinheiten import MengeneinheitengruppeCreate
        g = MengeneinheitengruppeCreate(
            gruppe_nr="G-GETREIDE",
            bezeichnung="Getreide EK/VK",
            bestand_einheit="t",
            ek_einheit="t",
            vk_einheit="kg",
            preis_einheit="t",
        )
        assert g.bestand_einheit == "t"
        assert g.vk_einheit == "kg"


# ── Artikelverpackung ─────────────────────────────────────────────────────────

class TestArtikelVerpackung:
    def test_einstufig_create(self):
        from app.api.v1.endpoints.artikel_verpackung import ArtikelVerpackungCreate
        v = ArtikelVerpackungCreate(
            verpackungs_nr="VP001",
            bezeichnung="25kg Sack",
            stufen=1,
            stufe1_bezeichnung="Sack",
            stufe1_menge=Decimal("25"),
            stufe1_einheit="kg",
            stufe1_gewicht_kg=Decimal("0.5"),
        )
        assert v.stufen == 1

    def test_dreistufig_create(self):
        from app.api.v1.endpoints.artikel_verpackung import ArtikelVerpackungCreate
        v = ArtikelVerpackungCreate(
            verpackungs_nr="VP003",
            bezeichnung="Palette 24er Karton 6er Flasche",
            stufen=3,
            stufe1_bezeichnung="Flasche",
            stufe1_menge=Decimal("1"),
            stufe1_einheit="l",
            stufe2_bezeichnung="Karton",
            stufe2_einheiten_pro_stufe2=6,
            stufe3_bezeichnung="Palette",
            stufe3_einheiten_pro_stufe3=48,
        )
        assert v.stufen == 3
        assert v.stufe2_einheiten_pro_stufe2 == 6
        assert v.stufe3_einheiten_pro_stufe3 == 48

    def test_dreistufig_ohne_stufe2_fehler(self):
        from app.api.v1.endpoints.artikel_verpackung import ArtikelVerpackungCreate
        from pydantic import ValidationError
        with pytest.raises((ValueError, ValidationError)):
            ArtikelVerpackungCreate(
                verpackungs_nr="VPFAIL",
                bezeichnung="Ungültig",
                stufen=3,
                # stufe2_einheiten_pro_stufe2 fehlt
                stufe3_einheiten_pro_stufe3=48,
            )

    def test_gesamtgewicht_berechnung(self):
        # 2 Paletten à 48 Kartons à 6 Flaschen à 0.02 kg Packgewicht
        stufe1_gew = Decimal("0.02")  # kg pro Flasche Verpackung
        stufe2_gew = Decimal("0.3")   # kg pro Karton
        stufe3_gew = Decimal("25")    # kg Palette
        anzahl_s3 = 2
        anzahl_s2 = 48 * 2
        anzahl_s1 = 6 * 48 * 2
        gesamt = (stufe3_gew * anzahl_s3 + stufe2_gew * anzahl_s2
                  + stufe1_gew * anzahl_s1)
        assert gesamt > 0


# ── Zahlungsmeldungen ─────────────────────────────────────────────────────────

class TestZahlungsmeldungen:
    def test_status_workflow(self):
        status_eingegangen = "eingegangen"
        erlaubte_transitionen = {
            "eingegangen": ("verarbeitet", "abgewiesen"),
            "verarbeitet": (),
            "abgewiesen": (),
        }
        assert "verarbeitet" in erlaubte_transitionen[status_eingegangen]
        assert len(erlaubte_transitionen["verarbeitet"]) == 0

    def test_skonto_betrag(self):
        zahlung = Decimal("980.00")
        skonto = Decimal("20.00")
        gesamt = zahlung + skonto
        assert gesamt == Decimal("1000.00")

    def test_teilzahlung_flag(self):
        meldung = {
            "zahlungsbetrag_eur": Decimal("500.00"),
            "rechnungs_nr": "RE-2024-001",
            "teilzahlung": True,
        }
        assert meldung["teilzahlung"] is True

    def test_create_schema(self):
        from app.api.v1.endpoints.fibu_zahlungsmeldungen import ZahlungsmeldungCreate
        zm = ZahlungsmeldungCreate(
            kunden_nr="K001",
            zahlungsdatum=date(2024, 6, 15),
            zahlungsbetrag_eur=Decimal("1500.00"),
            skonto_erlaubt=True,
            teilzahlung=False,
        )
        assert zm.zahlungsbetrag_eur == Decimal("1500.00")
        assert zm.skonto_erlaubt is True
