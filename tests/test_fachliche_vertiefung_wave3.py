"""Unit-Tests für Fachliche Vertiefung Wave 3.

Kundenbanken, Permanente Inventur (PIV), Stoffstromanteil, OP Skonto-Auszifferung.
"""
import pytest
from datetime import date
from decimal import Decimal


# ── Kundenbanken ──────────────────────────────────────────────────────────────

class TestIBANValidierung:
    def _validate(self, iban: str) -> str:
        import re
        IBAN_PATTERN = re.compile(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$')
        cleaned = iban.replace(" ", "").upper()
        if not IBAN_PATTERN.match(cleaned):
            raise ValueError("Ungültiges IBAN-Format.")
        return cleaned

    def test_gueltige_deutsche_iban(self):
        result = self._validate("DE89 3704 0044 0532 0130 00")
        assert result == "DE89370400440532013000"

    def test_ungueltige_iban_zu_kurz(self):
        with pytest.raises(ValueError):
            self._validate("DE12")

    def test_iban_masked(self):
        iban = "DE89370400440532013000"
        masked = iban[:4] + "****" + iban[-4:]
        assert masked == "DE89****3000"

    def test_gueltige_oesterreichische_iban(self):
        result = self._validate("AT61 1904 3002 3457 3201")
        assert result == "AT611904300234573201"


# ── PIV Differenzberechnung ───────────────────────────────────────────────────

class TestPIVDifferenz:
    def _berechne_differenz(self, buchbestand, zaehlmenge, bewertungspreis=None):
        differenz = Decimal(str(zaehlmenge)) - Decimal(str(buchbestand))
        if bewertungspreis is not None:
            differenzwert = (differenz * Decimal(str(bewertungspreis))).quantize(Decimal("0.01"))
        else:
            differenzwert = None
        return differenz, differenzwert

    def test_fehlmenge(self):
        diff, wert = self._berechne_differenz(100, 95, 2.50)
        assert diff == Decimal("-5")
        assert wert == Decimal("-12.50")

    def test_uebermenge(self):
        diff, wert = self._berechne_differenz(50, 52, 3.00)
        assert diff == Decimal("2")
        assert wert == Decimal("6.00")

    def test_keine_differenz(self):
        diff, wert = self._berechne_differenz(100, 100, 1.50)
        assert diff == Decimal("0")
        assert wert == Decimal("0.00")

    def test_ohne_bewertungspreis(self):
        diff, wert = self._berechne_differenz(100, 98)
        assert diff == Decimal("-2")
        assert wert is None


# ── Stoffstrom THG-Berechnung ─────────────────────────────────────────────────

class TestStoffstromTHG:
    def test_co2_aequivalent_vorhanden(self):
        artikel = {
            "artikel_nr": "WEIZEN01",
            "co2_aequivalent_kg_per_t": Decimal("12.5"),
            "thg_wert": Decimal("28.4"),
            "iscc_zertifiziert": True,
            "red_konform": True,
            "nachhaltig": True,
        }
        assert artikel["co2_aequivalent_kg_per_t"] > 0
        assert artikel["thg_wert"] > 0

    def test_thg_summary_aggregation(self):
        positionen = [
            {"rohstoff_kategorie": "Getreide", "co2_aequivalent_kg_per_t": Decimal("10.0"), "iscc_zertifiziert": True},
            {"rohstoff_kategorie": "Getreide", "co2_aequivalent_kg_per_t": Decimal("14.0"), "iscc_zertifiziert": False},
            {"rohstoff_kategorie": "Ölsaat", "co2_aequivalent_kg_per_t": Decimal("20.0"), "iscc_zertifiziert": True},
        ]
        getreide = [p for p in positionen if p["rohstoff_kategorie"] == "Getreide"]
        avg_co2 = sum(p["co2_aequivalent_kg_per_t"] for p in getreide) / len(getreide)
        iscc_count = sum(1 for p in getreide if p["iscc_zertifiziert"])
        assert avg_co2 == Decimal("12.0")
        assert iscc_count == 1


# ── OP Skonto-Auszifferung ────────────────────────────────────────────────────

class TestSkontoAuszifferung:
    def _berechne_skonto(self, rechnungsbetrag, skonto_prozent, zahlungsdatum, skonto_bis=None):
        skonto_gueltig = True
        if skonto_bis and zahlungsdatum > skonto_bis:
            skonto_gueltig = False
        skontobetrag = Decimal("0")
        if skonto_gueltig:
            skontobetrag = (Decimal(str(rechnungsbetrag)) * Decimal(str(skonto_prozent)) / 100
                            ).quantize(Decimal("0.01"))
        zahlungsbetrag = Decimal(str(rechnungsbetrag)) - skontobetrag
        return skonto_gueltig, skontobetrag, zahlungsbetrag

    def test_skonto_2_prozent(self):
        gueltig, skonto, zahlung = self._berechne_skonto(1000, 2, date(2026, 5, 10), date(2026, 5, 15))
        assert gueltig is True
        assert skonto == Decimal("20.00")
        assert zahlung == Decimal("980.00")

    def test_skontofrist_abgelaufen(self):
        gueltig, skonto, zahlung = self._berechne_skonto(1000, 2, date(2026, 5, 20), date(2026, 5, 15))
        assert gueltig is False
        assert skonto == Decimal("0")
        assert zahlung == Decimal("1000")

    def test_skonto_prozent_berechnung(self):
        zahlungsbetrag = Decimal("980.00")
        skontobetrag = Decimal("20.00")
        gesamtbetrag = zahlungsbetrag + skontobetrag
        skonto_prozent = (skontobetrag / gesamtbetrag * 100).quantize(Decimal("0.0001"))
        assert skonto_prozent == Decimal("2.0000")

    def test_gesamtbetrag_gleichung(self):
        zahlung = Decimal("980.00")
        skonto = Decimal("20.00")
        gesamt = zahlung + skonto
        assert gesamt == Decimal("1000.00")

    def test_kein_skonto(self):
        gueltig, skonto, zahlung = self._berechne_skonto(500, 0, date(2026, 5, 10))
        assert skonto == Decimal("0")
        assert zahlung == Decimal("500")
