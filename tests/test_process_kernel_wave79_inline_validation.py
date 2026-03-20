"""
Wave 79 — Inline-Validierung mit domain-spezifischen Erklärungen (Gap 026)

Tests für validate_gln(), validate_menge(), validate_iban(), validate_preis(),
FormValidationContract und Standard-Contracts für Landhandel-Kernmasken.

Gap 026: Inline-Validierung — KPI: 35% weniger Eingabefehler
"""
from __future__ import annotations

import pytest

from app.core.validation_contracts import (
    DomainValidationResult,
    FieldValidationRule,
    FormValidationContract,
    ValidationMessage,
    ValidationSeverity,
    ValidationTrigger,
    get_annahme_validation_contract,
    get_bestellung_validation_contract,
    get_einlagerung_validation_contract,
    get_zahlung_validation_contract,
    validate_gln,
    validate_iban,
    validate_menge,
    validate_preis,
)


# ---------------------------------------------------------------------------
# TestValidateGln
# ---------------------------------------------------------------------------

class TestValidateGln:
    """GLN-Validierung: 13 Ziffern, EAN-13-Prüfziffer."""

    def test_gueltige_gln(self):
        result = validate_gln("4012345678901")
        assert result.is_valid is True
        assert result.has_errors is False

    def test_leere_gln_ist_fehler(self):
        result = validate_gln("")
        assert result.is_valid is False
        assert result.has_errors is True
        assert "fehlt" in result.first_error.title.lower() or "fehlt" in result.first_error.title

    def test_gln_mit_buchstaben_ist_fehler(self):
        result = validate_gln("401234567890A")
        assert result.is_valid is False
        assert "Ziffern" in result.first_error.title or "Zeichen" in result.first_error.detail

    def test_gln_zu_kurz(self):
        result = validate_gln("401234")
        assert result.is_valid is False
        assert "13" in result.first_error.title

    def test_gln_zu_lang(self):
        result = validate_gln("40123456789012")  # 14 Ziffern
        assert result.is_valid is False
        assert "13" in result.first_error.title

    def test_gln_falsche_pruefziffer(self):
        result = validate_gln("4012345678900")  # Prüfziffer 0 statt 1
        assert result.is_valid is False
        assert "Prüfziffer" in result.first_error.title

    def test_gln_suggestion_enthalten(self):
        result = validate_gln("123")
        assert result.first_error.suggestion != ""

    def test_gln_field_name_gesetzt(self):
        result = validate_gln("", field_name="lieferant_gln")
        assert result.field_name == "lieferant_gln"

    def test_gln_as_dict(self):
        result = validate_gln("4012345678901")
        d = result.as_dict()
        assert d["is_valid"] is True
        assert d["has_errors"] is False
        assert "messages" in d

    def test_zweite_gueltige_gln(self):
        # Metro AG GLN aus Default-Partners
        result = validate_gln("4000260000000")
        # Prüfziffer-Check: berechnete Prüfziffer ermitteln
        digits = [int(c) for c in "4000260000000"]
        checksum = sum(d * (3 if i % 2 else 1) for i, d in enumerate(digits[:-1]))
        expected = (10 - (checksum % 10)) % 10
        if digits[-1] == expected:
            assert result.is_valid is True
        else:
            assert result.is_valid is False  # bekannte ungültige Test-GLN


# ---------------------------------------------------------------------------
# TestValidateMenge
# ---------------------------------------------------------------------------

class TestValidateMenge:
    """Mengeneingabe: positiver Dezimalwert mit Einheit."""

    def test_gueltige_menge(self):
        result = validate_menge("25.5", einheit="t")
        assert result.is_valid is True
        assert result.has_errors is False

    def test_menge_komma_als_dezimaltrenner(self):
        result = validate_menge("25,5", einheit="t")
        assert result.is_valid is True

    def test_menge_null_ist_fehler(self):
        result = validate_menge("0", einheit="t")
        assert result.is_valid is False
        assert "0" in result.first_error.title

    def test_menge_null_erlaubt(self):
        result = validate_menge("0", einheit="t", allow_zero=True)
        assert result.is_valid is True

    def test_menge_negativ_ist_fehler(self):
        result = validate_menge("-5", einheit="t")
        assert result.is_valid is False

    def test_menge_buchstaben_ist_fehler(self):
        result = validate_menge("abc", einheit="kg")
        assert result.is_valid is False
        assert "Ungültige" in result.first_error.title

    def test_menge_unter_min_wert(self):
        result = validate_menge("0.5", einheit="t", min_wert=1.0)
        assert result.is_valid is False
        assert "Mindestwert" in result.first_error.title

    def test_menge_ueber_max_wert_warnung(self):
        result = validate_menge("50000", einheit="t", max_wert=10000)
        assert result.has_warnings is True
        assert result.is_valid is False  # severity=WARNING macht is_valid=False wenn max_wert explizit

    def test_menge_t_ueber_10000_warnung(self):
        result = validate_menge("15000", einheit="t")
        assert result.has_warnings is True
        assert result.is_valid is True  # Warnung, kein Fehler

    def test_menge_suggestion_enthalten(self):
        result = validate_menge("0", einheit="kg")
        assert result.first_error.suggestion != ""

    def test_menge_field_name(self):
        result = validate_menge("10", einheit="t", field_name="menge_netto")
        assert result.field_name == "menge_netto"


# ---------------------------------------------------------------------------
# TestValidateIban
# ---------------------------------------------------------------------------

class TestValidateIban:
    """IBAN-Validierung: ISO 13616, Mod-97-Prüfung."""

    def test_gueltige_de_iban(self):
        # Bekannte gültige Test-IBAN
        result = validate_iban("DE89370400440532013000")
        assert result.is_valid is True

    def test_iban_mit_leerzeichen(self):
        result = validate_iban("DE89 3704 0044 0532 0130 00")
        assert result.is_valid is True

    def test_zu_kurze_iban(self):
        result = validate_iban("DE")
        assert result.is_valid is False
        assert "kurz" in result.first_error.title.lower()

    def test_ungültiger_laendercode(self):
        result = validate_iban("123456789")
        assert result.is_valid is False
        assert "Ländercode" in result.first_error.title

    def test_falsche_laenge_de(self):
        result = validate_iban("DE893704004405320130")  # nur 20 Zeichen
        assert result.is_valid is False
        assert "22" in result.first_error.title

    def test_falsche_pruefziffer(self):
        # Korrekte Struktur aber falsche Prüfziffer
        result = validate_iban("DE00370400440532013000")
        assert result.is_valid is False
        assert "Prüfziffer" in result.first_error.title

    def test_iban_suggestion_vorhanden(self):
        result = validate_iban("DE")
        assert result.first_error.suggestion != ""

    def test_iban_field_name(self):
        result = validate_iban("DE89370400440532013000", field_name="empfaenger_iban")
        assert result.field_name == "empfaenger_iban"


# ---------------------------------------------------------------------------
# TestValidatePreis
# ---------------------------------------------------------------------------

class TestValidatePreis:
    """Preis-Validierung: nicht-negativer Dezimalwert."""

    def test_gueltiger_preis(self):
        result = validate_preis("245.50")
        assert result.is_valid is True

    def test_preis_komma(self):
        result = validate_preis("245,50")
        assert result.is_valid is True

    def test_preis_null_erlaubt(self):
        result = validate_preis("0")
        assert result.is_valid is True

    def test_preis_null_mit_min_preis(self):
        result = validate_preis("0", min_preis=0.01)
        assert result.is_valid is False
        assert "0" in result.first_error.title

    def test_negativer_preis_ist_fehler(self):
        result = validate_preis("-10")
        assert result.is_valid is False
        assert "negativ" in result.first_error.title.lower()

    def test_buchstaben_ist_fehler(self):
        result = validate_preis("EUR245")
        assert result.is_valid is False
        assert "Ungültige" in result.first_error.title

    def test_preis_suggestion_vorhanden(self):
        result = validate_preis("abc")
        assert result.first_error.suggestion != ""


# ---------------------------------------------------------------------------
# TestFormValidationContract
# ---------------------------------------------------------------------------

class TestFormValidationContract:
    """FormValidationContract: Struktur, Pflichtfelder, Regelzuordnung."""

    def test_annahme_contract_hat_felder(self):
        contract = get_annahme_validation_contract()
        assert contract.anzahl_regeln >= 2
        assert "lieferant_gln" in contract.pflichtfelder

    def test_einlagerung_contract(self):
        contract = get_einlagerung_validation_contract()
        assert "menge" in contract.pflichtfelder

    def test_bestellung_contract(self):
        contract = get_bestellung_validation_contract()
        assert "lieferant_gln" in contract.pflichtfelder
        assert "bestellmenge" in contract.pflichtfelder
        assert "einzelpreis" in contract.pflichtfelder

    def test_zahlung_contract(self):
        contract = get_zahlung_validation_contract()
        assert "empfaenger_iban" in contract.pflichtfelder
        assert "betrag" in contract.pflichtfelder

    def test_get_regel_findet_eintrag(self):
        contract = get_annahme_validation_contract()
        regel = contract.get_regel("lieferant_gln")
        assert regel is not None
        assert regel.regel_name == "gln"

    def test_get_regel_unbekannt_ist_none(self):
        contract = get_annahme_validation_contract()
        assert contract.get_regel("unbekannt") is None

    def test_as_dict_vollstaendig(self):
        contract = get_zahlung_validation_contract()
        d = contract.as_dict()
        assert d["formular_name"] == "Zahlung"
        assert "felder" in d
        assert "pflichtfelder" in d
        assert d["schema_version"] == 1

    def test_trigger_on_blur_standard(self):
        contract = get_annahme_validation_contract()
        regel = contract.get_regel("lieferant_gln")
        assert regel.trigger == ValidationTrigger.ON_BLUR

    def test_trigger_on_change_fuer_menge(self):
        contract = get_annahme_validation_contract()
        regel = contract.get_regel("menge_netto")
        assert regel is not None
        assert regel.trigger == ValidationTrigger.ON_CHANGE


# ---------------------------------------------------------------------------
# TestValidationMessage
# ---------------------------------------------------------------------------

class TestValidationMessage:
    """ValidationMessage: Struktur und as_dict()."""

    def test_message_as_dict(self):
        msg = ValidationMessage(
            title="Testfehler",
            detail="Detailbeschreibung",
            severity=ValidationSeverity.ERROR,
            suggestion="Verbesserungsvorschlag",
            field_name="feld_a",
        )
        d = msg.as_dict()
        assert d["title"] == "Testfehler"
        assert d["severity"] == "ERROR"
        assert d["suggestion"] == "Verbesserungsvorschlag"
        assert d["field_name"] == "feld_a"

    def test_alle_severities_vorhanden(self):
        for s in ValidationSeverity:
            assert s.value in ("ERROR", "WARNING", "INFO")

    def test_alle_trigger_vorhanden(self):
        for t in ValidationTrigger:
            assert t.value in ("ON_CHANGE", "ON_BLUR", "ON_SUBMIT")


# ---------------------------------------------------------------------------
# TestIntegrationSzenario
# ---------------------------------------------------------------------------

class TestIntegrationSzenario:
    """End-to-End Validierungsszenarien für Landhandel-Kernmasken."""

    def test_annahme_vollstaendig_gueltig(self):
        """Annahme: GLN + Mengen alle gültig."""
        contract = get_annahme_validation_contract()
        daten = {
            "lieferant_gln": "4012345678901",
            "menge_netto": "24.5",
            "menge_brutto": "25.0",
        }
        ergebnisse = {}
        for f in contract.felder:
            wert = daten.get(f.field_name, "")
            if f.regel_name == "gln":
                ergebnisse[f.field_name] = validate_gln(wert, f.field_name)
            elif f.regel_name == "menge_t":
                ergebnisse[f.field_name] = validate_menge(wert, einheit="t", field_name=f.field_name)

        alle_gueltig = all(r.is_valid for r in ergebnisse.values())
        assert alle_gueltig is True

    def test_zahlung_iban_fehler_blockiert(self):
        """Zahlung: ungültige IBAN → Formular nicht absendbar."""
        ergebnis = validate_iban("DE00000000000000000000")
        assert ergebnis.is_valid is False
        assert ergebnis.has_errors is True

    def test_domain_nachrichten_sind_deutsch(self):
        """Alle Fehlermeldungen müssen auf Deutsch sein."""
        fehlermeldungen = [
            validate_gln("").first_error.title,
            validate_menge("0", einheit="t").first_error.title,
            validate_preis("-1").first_error.title,
        ]
        for msg in fehlermeldungen:
            # Typisch deutsche Wörter / kein reines Englisch
            assert msg != ""
            # Keine typisch englischen Fehlermuster
            assert "invalid" not in msg.lower()
            assert "required" not in msg.lower()

    def test_kpi_abdeckung_alle_vier_contracts(self):
        """Alle 4 Standard-Contracts sind definiert und haben Felder."""
        contracts = [
            get_annahme_validation_contract(),
            get_einlagerung_validation_contract(),
            get_bestellung_validation_contract(),
            get_zahlung_validation_contract(),
        ]
        for contract in contracts:
            assert contract.anzahl_regeln >= 1
            assert len(contract.pflichtfelder) >= 1
            assert contract.formular_name != ""
