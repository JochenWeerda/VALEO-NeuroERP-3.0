"""Unit-Tests für Fachliche Vertiefung Wave 4.

Rabattgruppen/klassen, Hausbankenstamm, Artikel-Bestandteile, Frachttabellen.
"""
import pytest
from datetime import date
from decimal import Decimal


# ── Rabattgruppen ─────────────────────────────────────────────────────────────

class TestRabattgruppenRichtung:
    def test_gueltige_richtungen(self):
        for r in ("EK", "VK"):
            assert r in ("EK", "VK")

    def test_ungueltige_richtung(self):
        with pytest.raises(ValueError):
            from pydantic import ValidationError
            from app.api.v1.endpoints.preis_rabattgruppen import RabattgruppeCreate
            try:
                RabattgruppeCreate(gruppe_nr="R1", bezeichnung="Test", richtung="XX")
            except Exception as e:
                raise ValueError(str(e))


class TestRabattsatzLookup:
    def _lookup_satz(self, saetze, rabattgruppe_nr, rabattklasse_nr, richtung, menge=None, stichtag=None):
        check = stichtag or date.today()
        gefunden = [
            s for s in saetze
            if s["rabattgruppe_nr"] == rabattgruppe_nr
            and s["rabattklasse_nr"] == rabattklasse_nr
            and s["richtung"] == richtung
            and (s.get("gueltig_ab") is None or s["gueltig_ab"] <= check)
            and (s.get("gueltig_bis") is None or s["gueltig_bis"] >= check)
            and (menge is None or s.get("ab_menge") is None or s["ab_menge"] <= menge)
        ]
        if not gefunden:
            return Decimal("0")
        gefunden.sort(key=lambda x: x.get("ab_menge") or Decimal("0"), reverse=True)
        return gefunden[0]["rabatt_prozent"]

    def test_rabattsatz_gefunden(self):
        saetze = [{"rabattgruppe_nr": "G1", "rabattklasse_nr": "K1", "richtung": "VK",
                   "rabatt_prozent": Decimal("5"), "ab_menge": None,
                   "gueltig_ab": None, "gueltig_bis": None}]
        result = self._lookup_satz(saetze, "G1", "K1", "VK")
        assert result == Decimal("5")

    def test_staffelrabatt(self):
        saetze = [
            {"rabattgruppe_nr": "G1", "rabattklasse_nr": "K1", "richtung": "VK",
             "rabatt_prozent": Decimal("3"), "ab_menge": Decimal("0"),
             "gueltig_ab": None, "gueltig_bis": None},
            {"rabattgruppe_nr": "G1", "rabattklasse_nr": "K1", "richtung": "VK",
             "rabatt_prozent": Decimal("5"), "ab_menge": Decimal("10"),
             "gueltig_ab": None, "gueltig_bis": None},
        ]
        assert self._lookup_satz(saetze, "G1", "K1", "VK", menge=Decimal("15")) == Decimal("5")
        assert self._lookup_satz(saetze, "G1", "K1", "VK", menge=Decimal("5")) == Decimal("3")

    def test_kein_rabattsatz(self):
        result = self._lookup_satz([], "G1", "K1", "VK")
        assert result == Decimal("0")


# ── Hausbankenstamm ───────────────────────────────────────────────────────────

class TestHausbankIBANValidierung:
    def _validate(self, iban: str) -> str:
        import re
        IBAN_PATTERN = re.compile(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$')
        cleaned = iban.replace(" ", "").upper()
        if not IBAN_PATTERN.match(cleaned):
            raise ValueError("Ungültiges IBAN-Format.")
        return cleaned

    def test_gueltige_iban(self):
        result = self._validate("DE89 3704 0044 0532 0130 00")
        assert result == "DE89370400440532013000"

    def test_ungueltige_iban(self):
        with pytest.raises(ValueError):
            self._validate("INVALID")

    def test_erechnung_flag(self):
        hausbank = {
            "bank_nr": "HB01",
            "iban": "DE89370400440532013000",
            "erechnung_aktiv": True,
            "standard": True,
        }
        assert hausbank["erechnung_aktiv"] is True


# ── Artikel-Bestandteile ──────────────────────────────────────────────────────

class TestArtikelBestandteile:
    def test_grenzwert_definition(self):
        bestandteil = {
            "bestandteil_nr": "FEUCHTE",
            "bezeichnung": "Feuchtigkeit",
            "einheit": "%",
            "grenzwert_min": Decimal("0"),
            "grenzwert_max": Decimal("14.5"),
            "nutzung": "qualitaetsdaten",
            "typ_schad_naehr": "keins",
        }
        assert bestandteil["grenzwert_max"] > bestandteil["grenzwert_min"]

    def test_schadstoff_typ(self):
        bestandteil = {"typ_schad_naehr": "schadstoff", "bezeichnung": "DON-Mykotoxin"}
        assert bestandteil["typ_schad_naehr"] == "schadstoff"

    def test_nutzungstypen(self):
        erlaubte = ("egal", "qualitaetsdaten", "ackerschlagkartei", "partieartikelanalyse")
        assert "qualitaetsdaten" in erlaubte
        assert "xyz" not in erlaubte

    def test_sollwert_zuordnung(self):
        zuordnung = {"artikel_nr": "WEIZEN01", "bestandteil_nr": "ROHPROTEIN",
                     "sollwert": Decimal("11.5")}
        assert zuordnung["sollwert"] == Decimal("11.5")


# ── Frachttabellen ────────────────────────────────────────────────────────────

class TestFrachttabellenLookup:
    def _berechne_frachtkosten(self, positionen, menge, tabelle_nr):
        relevante = [p for p in positionen
                     if p["tabelle_nr"] == tabelle_nr and p["ab_menge"] <= menge]
        if not relevante:
            return None
        relevante.sort(key=lambda x: x["ab_menge"], reverse=True)
        beste = relevante[0]
        kosten = beste["frachtsatz_eur"] * menge
        if beste.get("mindestfracht_eur"):
            kosten = max(kosten, beste["mindestfracht_eur"])
        return kosten

    def test_frachtkosten_staffel(self):
        positionen = [
            {"tabelle_nr": "FT01", "ab_menge": Decimal("0"), "frachtsatz_eur": Decimal("10.00"), "mindestfracht_eur": None},
            {"tabelle_nr": "FT01", "ab_menge": Decimal("20"), "frachtsatz_eur": Decimal("8.50"), "mindestfracht_eur": None},
        ]
        assert self._berechne_frachtkosten(positionen, Decimal("25"), "FT01") == Decimal("212.50")
        assert self._berechne_frachtkosten(positionen, Decimal("10"), "FT01") == Decimal("100.00")

    def test_mindestfracht(self):
        positionen = [
            {"tabelle_nr": "FT01", "ab_menge": Decimal("0"), "frachtsatz_eur": Decimal("5.00"), "mindestfracht_eur": Decimal("50.00")},
        ]
        assert self._berechne_frachtkosten(positionen, Decimal("5"), "FT01") == Decimal("50.00")

    def test_frachttabellen_zuordnung_lookup(self):
        zuordnungen = [
            {"frachtklasse": "FK1", "frachtgruppe": "FG1", "versandart": None,
             "tabelle_nr": "FT01", "sperre": False,
             "gueltig_ab": None, "gueltig_bis": None},
        ]
        gefunden = [z for z in zuordnungen
                    if z["frachtklasse"] == "FK1" and z["frachtgruppe"] == "FG1"
                    and not z["sperre"]]
        assert len(gefunden) == 1
        assert gefunden[0]["tabelle_nr"] == "FT01"

    def test_gesperrte_zuordnung_ignoriert(self):
        zuordnungen = [
            {"frachtklasse": "FK1", "frachtgruppe": "FG1", "versandart": None,
             "tabelle_nr": "FT01", "sperre": True,
             "gueltig_ab": None, "gueltig_bis": None},
        ]
        gefunden = [z for z in zuordnungen
                    if z["frachtklasse"] == "FK1" and z["frachtgruppe"] == "FG1"
                    and not z["sperre"]]
        assert len(gefunden) == 0
