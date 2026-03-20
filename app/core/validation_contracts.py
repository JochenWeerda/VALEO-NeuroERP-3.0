"""
validation_contracts.py — Inline-Validierung mit domain-spezifischen Erklärungen (Wave 79, Gap 026)

Domain-spezifische Validierungsregeln für Landhandel-ERP-Felder:
GLN, IBAN, Menge, Preis, Datum, etc. mit deutschen Fehlermeldungen
und kontextuellen Verbesserungsvorschlägen.

Gap 026: Inline-Validierung — KPI: 35% weniger Eingabefehler
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ValidationSeverity(str, Enum):
    """Schweregrad einer Validierungsmeldung."""
    ERROR   = "ERROR"    # Eingabe ungültig, Speichern blockiert
    WARNING = "WARNING"  # Eingabe bedenklich, Speichern möglich
    INFO    = "INFO"     # Hinweis zur Verbesserung


class ValidationTrigger(str, Enum):
    """Wann wird die Validierung ausgelöst."""
    ON_CHANGE   = "ON_CHANGE"   # Bei jeder Eingabe (debounced)
    ON_BLUR     = "ON_BLUR"     # Beim Verlassen des Feldes
    ON_SUBMIT   = "ON_SUBMIT"   # Erst beim Absenden


# ---------------------------------------------------------------------------
# Validation Message
# ---------------------------------------------------------------------------

@dataclass
class ValidationMessage:
    """
    Strukturierte Validierungsmeldung mit deutschem Text und Verbesserungshinweis.

    title: Kurze Fehlerbeschreibung ("Ungültige GLN")
    detail: Ausführliche Erklärung ("Eine GLN besteht aus genau 13 Ziffern.")
    suggestion: Konkreter Verbesserungsvorschlag ("Beispiel: 4012345678901")
    """
    title: str
    detail: str
    severity: ValidationSeverity
    suggestion: str = ""
    field_name: str = ""

    def as_dict(self) -> dict:
        return {
            "title": self.title,
            "detail": self.detail,
            "severity": self.severity.value,
            "suggestion": self.suggestion,
            "field_name": self.field_name,
        }


# ---------------------------------------------------------------------------
# Validation Result
# ---------------------------------------------------------------------------

@dataclass
class DomainValidationResult:
    """Ergebnis einer Feldvalidierung."""
    field_name: str
    value: Any
    is_valid: bool
    messages: list[ValidationMessage] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(m.severity == ValidationSeverity.ERROR for m in self.messages)

    @property
    def has_warnings(self) -> bool:
        return any(m.severity == ValidationSeverity.WARNING for m in self.messages)

    @property
    def first_error(self) -> ValidationMessage | None:
        for m in self.messages:
            if m.severity == ValidationSeverity.ERROR:
                return m
        return None

    def as_dict(self) -> dict:
        return {
            "field_name": self.field_name,
            "is_valid": self.is_valid,
            "has_errors": self.has_errors,
            "has_warnings": self.has_warnings,
            "messages": [m.as_dict() for m in self.messages],
        }


# ---------------------------------------------------------------------------
# Domain-Validierungsregeln
# ---------------------------------------------------------------------------

def validate_gln(value: str, field_name: str = "gln") -> DomainValidationResult:
    """
    GLN (Global Location Number) — 13 Ziffern mit Prüfziffer.

    Standard: GS1 GLN (EAN-13-Algorithmus).
    """
    stripped = value.strip()

    if not stripped:
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title="GLN fehlt",
                detail="Eine GLN (Global Location Number) ist erforderlich.",
                severity=ValidationSeverity.ERROR,
                suggestion="Beispiel: 4012345678901",
                field_name=field_name,
            )],
        )

    if not stripped.isdigit():
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title="GLN darf nur Ziffern enthalten",
                detail=f"Die eingegebene GLN '{stripped}' enthält ungültige Zeichen.",
                severity=ValidationSeverity.ERROR,
                suggestion="Entfernen Sie alle Buchstaben, Leerzeichen und Sonderzeichen.",
                field_name=field_name,
            )],
        )

    if len(stripped) != 13:
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title=f"GLN muss 13 Ziffern haben (aktuell: {len(stripped)})",
                detail="Eine GLN besteht laut GS1-Standard aus exakt 13 Ziffern.",
                severity=ValidationSeverity.ERROR,
                suggestion="Beispiel: 4012345678901",
                field_name=field_name,
            )],
        )

    # Prüfziffer (EAN-13 Modulo-10)
    digits = [int(c) for c in stripped]
    checksum = sum(d * (3 if i % 2 else 1) for i, d in enumerate(digits[:-1]))
    expected_check = (10 - (checksum % 10)) % 10
    if digits[-1] != expected_check:
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title="GLN-Prüfziffer ungültig",
                detail=f"Die letzte Ziffer muss {expected_check} sein (EAN-13-Prüfsumme).",
                severity=ValidationSeverity.ERROR,
                suggestion="Bitte prüfen Sie die GLN in Ihrem GS1-Portal.",
                field_name=field_name,
            )],
        )

    return DomainValidationResult(field_name=field_name, value=value, is_valid=True)


def validate_menge(
    value: Any,
    field_name: str = "menge",
    einheit: str = "",
    min_wert: float = 0.0,
    max_wert: float | None = None,
    allow_zero: bool = False,
) -> DomainValidationResult:
    """
    Mengeneingabe (positiver Dezimalwert).

    Typische Einheiten im Landhandel: t, kg, l, Stück, ha.
    """
    einheit_label = f" {einheit}" if einheit else ""

    try:
        zahl = float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title="Ungültige Mengeneingabe",
                detail=f"'{value}' ist keine gültige Zahl.",
                severity=ValidationSeverity.ERROR,
                suggestion="Geben Sie eine Dezimalzahl ein, z.B. 12,5 oder 12.5",
                field_name=field_name,
            )],
        )

    if not allow_zero and zahl == 0.0:
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title=f"Menge muss größer als 0{einheit_label} sein",
                detail="Eine Menge von 0 ist in diesem Kontext nicht zulässig.",
                severity=ValidationSeverity.ERROR,
                suggestion=f"Geben Sie eine positive Menge ein, z.B. 1,0{einheit_label}",
                field_name=field_name,
            )],
        )

    if zahl < min_wert:
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title=f"Menge unter Mindestwert ({min_wert}{einheit_label})",
                detail=f"Die Menge {zahl}{einheit_label} unterschreitet den Mindestwert.",
                severity=ValidationSeverity.ERROR,
                suggestion=f"Geben Sie mindestens {min_wert}{einheit_label} ein.",
                field_name=field_name,
            )],
        )

    if max_wert is not None and zahl > max_wert:
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title=f"Menge überschreitet Maximum ({max_wert}{einheit_label})",
                detail=f"Die Menge {zahl}{einheit_label} überschreitet den Maximalwert.",
                severity=ValidationSeverity.WARNING,
                suggestion=f"Prüfen Sie ob {zahl}{einheit_label} korrekt ist.",
                field_name=field_name,
            )],
        )

    # Warnung bei ungewöhnlich hoher Menge (>10.000 t ohne expliziten max_wert)
    if einheit == "t" and max_wert is None and zahl > 10_000:
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=True,
            messages=[ValidationMessage(
                title=f"Ungewöhnlich hohe Menge: {zahl:,.0f} t",
                detail="Mengen über 10.000 t sind selten. Bitte prüfen Sie die Eingabe.",
                severity=ValidationSeverity.WARNING,
                suggestion="Haben Sie ggf. kg statt t eingegeben?",
                field_name=field_name,
            )],
        )

    return DomainValidationResult(field_name=field_name, value=value, is_valid=True)


_IBAN_LAENGEN: dict[str, int] = {
    "DE": 22, "AT": 20, "CH": 21, "FR": 27, "NL": 18, "PL": 28,
}


def validate_iban(value: str, field_name: str = "iban") -> DomainValidationResult:
    """
    IBAN-Validierung nach ISO 13616 (Ländercode + Prüfziffer + BBAN).

    Prüft: Format, Länge je Land, Mod-97-Prüfsumme.
    """
    normalized = value.replace(" ", "").upper()

    if len(normalized) < 4:
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title="IBAN zu kurz",
                detail="Eine IBAN besteht aus Ländercode, Prüfziffer und Kontonummer.",
                severity=ValidationSeverity.ERROR,
                suggestion="Beispiel (DE): DE89 3704 0044 0532 0130 00",
                field_name=field_name,
            )],
        )

    land = normalized[:2]
    if not land.isalpha():
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title="Ungültiger IBAN-Ländercode",
                detail=f"'{land}' ist kein gültiger ISO-3166-Ländercode.",
                severity=ValidationSeverity.ERROR,
                suggestion="Beginnen Sie mit dem Ländercode, z.B. DE für Deutschland.",
                field_name=field_name,
            )],
        )

    erwartet = _IBAN_LAENGEN.get(land)
    if erwartet and len(normalized) != erwartet:
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title=f"IBAN-Länge für {land} muss {erwartet} Zeichen sein",
                detail=f"Eingabe hat {len(normalized)} Zeichen.",
                severity=ValidationSeverity.ERROR,
                suggestion=f"Eine deutsche IBAN hat 22 Zeichen (ohne Leerzeichen).",
                field_name=field_name,
            )],
        )

    # Mod-97-Prüfung
    umgestellt = normalized[4:] + normalized[:4]
    numerisch = "".join(str(ord(c) - 55) if c.isalpha() else c for c in umgestellt)
    try:
        if int(numerisch) % 97 != 1:
            return DomainValidationResult(
                field_name=field_name,
                value=value,
                is_valid=False,
                messages=[ValidationMessage(
                    title="IBAN-Prüfziffer ungültig",
                    detail="Die IBAN besteht den Mod-97-Prüfsummentest nicht.",
                    severity=ValidationSeverity.ERROR,
                    suggestion="Prüfen Sie die IBAN auf Tippfehler.",
                    field_name=field_name,
                )],
            )
    except (ValueError, OverflowError):
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title="Ungültiges IBAN-Format",
                detail="Die IBAN enthält ungültige Zeichen.",
                severity=ValidationSeverity.ERROR,
                suggestion="Eine IBAN darf nur Buchstaben und Ziffern enthalten.",
                field_name=field_name,
            )],
        )

    return DomainValidationResult(field_name=field_name, value=value, is_valid=True)


def validate_preis(
    value: Any,
    field_name: str = "preis",
    waehrung: str = "EUR",
    min_preis: float = 0.0,
) -> DomainValidationResult:
    """
    Preis-/Kurseingabe für Handels- und Finanzmasken.

    Warnung bei negativen Preisen, Fehler bei nicht-numerischer Eingabe.
    """
    try:
        zahl = float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title="Ungültige Preiseingabe",
                detail=f"'{value}' ist kein gültiger {waehrung}-Betrag.",
                severity=ValidationSeverity.ERROR,
                suggestion="Geben Sie einen Dezimalwert ein, z.B. 245,50",
                field_name=field_name,
            )],
        )

    if zahl < 0:
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title=f"Negativer Preis nicht zulässig",
                detail="Ein Preis kann nicht negativ sein.",
                severity=ValidationSeverity.ERROR,
                suggestion="Für Gutschriften verwenden Sie bitte den Gutschrift-Workflow.",
                field_name=field_name,
            )],
        )

    if zahl == 0.0 and min_preis > 0:
        return DomainValidationResult(
            field_name=field_name,
            value=value,
            is_valid=False,
            messages=[ValidationMessage(
                title="Preis darf nicht 0 sein",
                detail="Ein Preis von 0 ist in diesem Kontext nicht zulässig.",
                severity=ValidationSeverity.ERROR,
                suggestion=f"Geben Sie einen Preis größer als {min_preis:.2f} {waehrung} ein.",
                field_name=field_name,
            )],
        )

    return DomainValidationResult(field_name=field_name, value=value, is_valid=True)


# ---------------------------------------------------------------------------
# Form-Level Validierung: DomainValidationContract
# ---------------------------------------------------------------------------

@dataclass
class FieldValidationRule:
    """Bindet einen Feldnamen an eine Validierungsfunktion."""
    field_name: str
    regel_name: str       # z.B. "gln", "menge_t", "iban", "preis_eur"
    pflichtfeld: bool = True
    trigger: ValidationTrigger = ValidationTrigger.ON_BLUR


@dataclass
class FormValidationContract:
    """
    Validierungsvertrag für ein ERP-Formular.

    Beschreibt welche Felder validiert werden und mit welchen Regeln.
    Wird von Frontend-Hooks und Contract-Tests genutzt.
    """
    formular_name: str
    felder: list[FieldValidationRule]
    schema_version: int = 1

    @property
    def pflichtfelder(self) -> list[str]:
        return [f.field_name for f in self.felder if f.pflichtfeld]

    @property
    def anzahl_regeln(self) -> int:
        return len(self.felder)

    def get_regel(self, field_name: str) -> FieldValidationRule | None:
        return next((f for f in self.felder if f.field_name == field_name), None)

    def as_dict(self) -> dict:
        return {
            "formular_name": self.formular_name,
            "felder": [
                {
                    "field_name": f.field_name,
                    "regel_name": f.regel_name,
                    "pflichtfeld": f.pflichtfeld,
                    "trigger": f.trigger.value,
                }
                for f in self.felder
            ],
            "pflichtfelder": self.pflichtfelder,
            "anzahl_regeln": self.anzahl_regeln,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Standard-Formular-Contracts für Landhandel-Kernmasken
# ---------------------------------------------------------------------------

def get_annahme_validation_contract() -> FormValidationContract:
    """Validierungsvertrag für die Annahme-/Waage-Maske."""
    return FormValidationContract(
        formular_name="Annahme",
        felder=[
            FieldValidationRule("lieferant_gln", "gln", pflichtfeld=True, trigger=ValidationTrigger.ON_BLUR),
            FieldValidationRule("menge_netto", "menge_t", pflichtfeld=True, trigger=ValidationTrigger.ON_CHANGE),
            FieldValidationRule("menge_brutto", "menge_t", pflichtfeld=True, trigger=ValidationTrigger.ON_CHANGE),
        ],
    )


def get_einlagerung_validation_contract() -> FormValidationContract:
    """Validierungsvertrag für die Einlagerungs-Maske."""
    return FormValidationContract(
        formular_name="Einlagerung",
        felder=[
            FieldValidationRule("menge", "menge_t", pflichtfeld=True, trigger=ValidationTrigger.ON_CHANGE),
        ],
    )


def get_bestellung_validation_contract() -> FormValidationContract:
    """Validierungsvertrag für Bestellvorschlag-Formulare."""
    return FormValidationContract(
        formular_name="Bestellung",
        felder=[
            FieldValidationRule("lieferant_gln", "gln", pflichtfeld=True, trigger=ValidationTrigger.ON_BLUR),
            FieldValidationRule("bestellmenge", "menge_t", pflichtfeld=True, trigger=ValidationTrigger.ON_CHANGE),
            FieldValidationRule("einzelpreis", "preis_eur", pflichtfeld=True, trigger=ValidationTrigger.ON_BLUR),
        ],
    )


def get_zahlung_validation_contract() -> FormValidationContract:
    """Validierungsvertrag für Zahlungs-/Überweisungsmasken."""
    return FormValidationContract(
        formular_name="Zahlung",
        felder=[
            FieldValidationRule("empfaenger_iban", "iban", pflichtfeld=True, trigger=ValidationTrigger.ON_BLUR),
            FieldValidationRule("betrag", "preis_eur", pflichtfeld=True, trigger=ValidationTrigger.ON_CHANGE),
        ],
    )
