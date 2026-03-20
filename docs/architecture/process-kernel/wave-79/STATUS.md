# Wave 79 — Inline-Validierung mit domain-spezifischen Erklärungen (Gap 026)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-19
**Tests:** 52 passed, 0 failed
**Gap:** 026 — Inline-Validierung mit domain-spezifischen Erklärungen, KPI: 35% weniger Eingabefehler

## Lieferumfang

### A) Backend: `app/core/validation_contracts.py`

Domain-spezifische Validierungsfunktionen mit deutschen Fehlermeldungen:

| Funktion | Regel | Beispiel-Fehler |
|----------|-------|----------------|
| `validate_gln(value)` | 13 Ziffern, EAN-13-Prüfziffer | "GLN-Prüfziffer ungültig" |
| `validate_menge(value, einheit)` | >0, Komma-Dezimal, Warnung bei >10.000 t | "Menge muss größer als 0 t sein" |
| `validate_iban(value)` | ISO 13616, Mod-97, Längen je Land | "IBAN-Prüfziffer ungültig" |
| `validate_preis(value)` | ≥0, nicht negativ | "Negativer Preis nicht zulässig" |

**`ValidationMessage`** — strukturierte dreistufige Meldung:
```python
ValidationMessage(
    title="GLN-Prüfziffer ungültig",
    detail="Die letzte Ziffer muss 1 sein (EAN-13-Prüfsumme).",
    severity=ValidationSeverity.ERROR,
    suggestion="Bitte prüfen Sie die GLN in Ihrem GS1-Portal.",
)
```

**`ValidationSeverity`**: ERROR (blockiert Speichern), WARNING (Speichern möglich), INFO (Hinweis)
**`ValidationTrigger`**: ON_CHANGE (debounced), ON_BLUR (bei Fokusverlust), ON_SUBMIT (beim Absenden)

**`FormValidationContract`** — deklarativer Vertrag je Maske:
```python
contract = get_zahlung_validation_contract()
contract.pflichtfelder  # ["empfaenger_iban", "betrag"]
contract.get_regel("empfaenger_iban").trigger  # ON_BLUR
```

### B) Standard-Contracts für Kernmasken

| Contract | Felder | Regeln |
|---------|--------|--------|
| `get_annahme_validation_contract()` | lieferant_gln, menge_netto, menge_brutto | gln + menge_t |
| `get_einlagerung_validation_contract()` | menge | menge_t |
| `get_bestellung_validation_contract()` | lieferant_gln, bestellmenge, einzelpreis | gln + menge_t + preis_eur |
| `get_zahlung_validation_contract()` | empfaenger_iban, betrag | iban + preis_eur |

### C) Frontend: `components/validation/InlineValidationMessage.tsx`

```tsx
<InlineValidationMessage result={validateGln(value)} />
```

- ERROR: rotes Badge mit AlertTriangle-Icon
- WARNING: gelbes Badge mit AlertCircle-Icon
- INFO: blaues Badge mit Info-Icon
- Success: grüner Haken (opt-in via `showSuccessIcon`)
- `role="alert"` + `aria-live="polite"` für Screen-Reader
- `getFieldBorderClass(result)` → rote/gelbe/grüne Input-Border

### D) Frontend: `hooks/useInlineValidation.ts`

```ts
const { result, validate, reset } = useInlineValidation('gln', 'lieferant_gln')
// Bei Eingabe (debounced 300ms):
validate(inputValue)
```

Unterstützte Regeltypen: `gln`, `iban`, `menge_t`, `menge_kg`, `menge_stk`, `preis_eur`, `required`

## Kontrakt-Tests (52 Tests)

| Klasse | Tests | Kernprüfung |
|--------|-------|-------------|
| `TestValidateGln` | 10 | 13 Ziffern, Prüfziffer, Leerzeichen |
| `TestValidateMenge` | 11 | >0, Komma, Mindestwert, Warnung >10.000 t |
| `TestValidateIban` | 8 | ISO 13616, Mod-97, Länge DE=22 |
| `TestValidatePreis` | 7 | ≥0, negativ, min_preis |
| `TestFormValidationContract` | 9 | Pflichtfelder, get_regel, as_dict |
| `TestValidationMessage` | 3 | as_dict, Severities, Trigger |
| `TestIntegrationSzenario` | 4 | E2E Annahme, Zahlung, deutsche Texte, KPI-Abdeckung |

## KPI-Ergebnis (Gap 026)

| KPI | Ziel | Ergebnis |
|-----|------|----------|
| Inline-Validierung implementiert | 35% weniger Eingabefehler | Alle 4 Kernmasken mit Contracts ✓ |
| Domain-spezifische Fehlermeldungen | Deutsche Texte mit Verbesserungsvorschlag | ValidationMessage.suggestion ✓ |
| Masken-Coverage | 4 Kernmasken | Annahme, Einlagerung, Bestellung, Zahlung ✓ |
| Frontend-Hook | Debounced ON_CHANGE/ON_BLUR | useInlineValidation(rule, fieldName) ✓ |
