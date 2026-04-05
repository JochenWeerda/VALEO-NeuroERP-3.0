/**
 * useInlineValidation — Debounced Inline-Validierung für ERP-Felder
 *
 * Gap 026: Inline-Validierung mit domain-spezifischen Erklärungen
 *
 * Unterstützte Regeltypen:
 *   'gln'      — GLN (13 Ziffern + Prüfziffer)
 *   'iban'     — IBAN (Ländercode + Mod-97)
 *   'menge_t'  — Menge in Tonnen (>0, Warnung >10.000 t)
 *   'menge_kg' — Menge in kg (>0)
 *   'preis_eur'— Preis EUR (>=0, nicht negativ)
 *   'required' — Pflichtfeld (nicht leer)
 *
 * Verwendung:
 *   const { result, validate, reset } = useInlineValidation('gln')
 *   // Bei Eingabe:
 *   validate(inputValue)
 *   // Im JSX:
 *   <InlineValidationMessage result={result} />
 */

import { useState, useCallback, useRef } from 'react'
import { ValidationResultData, ValidationMessageData } from '@/components/validation/InlineValidationMessage'

type ValidationRuleId =
  | 'gln'
  | 'iban'
  | 'menge_t'
  | 'menge_kg'
  | 'menge_stk'
  | 'preis_eur'
  | 'required'

// ---------------------------------------------------------------------------
// Client-side Validierungslogik (spiegelt app/core/validation_contracts.py)
// ---------------------------------------------------------------------------

function _makeError(
  title: string,
  detail: string,
  suggestion = '',
  fieldName = '',
): ValidationResultData {
  const msg: ValidationMessageData = {
    title,
    detail,
    severity: 'ERROR',
    suggestion,
    field_name: fieldName,
  }
  return {
    field_name: fieldName,
    is_valid: false,
    has_errors: true,
    has_warnings: false,
    messages: [msg],
  }
}

function _makeWarning(
  title: string,
  detail: string,
  suggestion = '',
  fieldName = '',
): ValidationResultData {
  const msg: ValidationMessageData = {
    title,
    detail,
    severity: 'WARNING',
    suggestion,
    field_name: fieldName,
  }
  return {
    field_name: fieldName,
    is_valid: true,
    has_errors: false,
    has_warnings: true,
    messages: [msg],
  }
}

function _makeOk(fieldName: string): ValidationResultData {
  return { field_name: fieldName, is_valid: true, has_errors: false, has_warnings: false, messages: [] }
}

function _validateGln(value: string, fieldName: string): ValidationResultData {
  const s = value.trim()
  if (!s) return _makeError('GLN fehlt', 'Eine GLN ist erforderlich.', 'Beispiel: 4012345678901', fieldName)
  if (!/^\d+$/.test(s)) return _makeError('GLN darf nur Ziffern enthalten', `'${s}' enthält ungültige Zeichen.`, 'Entfernen Sie Buchstaben und Sonderzeichen.', fieldName)
  if (s.length !== 13) return _makeError(`GLN muss 13 Ziffern haben (aktuell: ${s.length})`, 'Eine GLN besteht laut GS1 aus exakt 13 Ziffern.', 'Beispiel: 4012345678901', fieldName)
  const digits = s.split('').map(Number)
  const checksum = digits.slice(0, 12).reduce((sum, d, i) => sum + d * (i % 2 === 0 ? 1 : 3), 0)
  const expected = (10 - (checksum % 10)) % 10
  if (digits[12] !== expected) return _makeError('GLN-Prüfziffer ungültig', `Die letzte Ziffer muss ${expected} sein.`, 'Prüfen Sie die GLN in Ihrem GS1-Portal.', fieldName)
  return _makeOk(fieldName)
}

const _IBAN_LENGTHS: Record<string, number> = {
  DE: 22, AT: 20, CH: 21, FR: 27, NL: 18, PL: 28,
}

function _validateIban(value: string, fieldName: string): ValidationResultData {
  const s = value.replace(/\s/g, '').toUpperCase()
  if (s.length < 4) return _makeError('IBAN zu kurz', 'Eine IBAN besteht aus Ländercode, Prüfziffer und Kontonummer.', 'Beispiel (DE): DE89370400440532013000', fieldName)
  const country = s.slice(0, 2)
  if (!/^[A-Z]{2}$/.test(country)) return _makeError('Ungültiger IBAN-Ländercode', `'${country}' ist kein gültiger ISO-Ländercode.`, 'Beginnen Sie mit dem Ländercode, z.B. DE.', fieldName)
  const expected = _IBAN_LENGTHS[country]
  if (expected && s.length !== expected) return _makeError(`IBAN-Länge für ${country} muss ${expected} Zeichen sein`, `Eingabe hat ${s.length} Zeichen.`, 'Eine deutsche IBAN hat 22 Zeichen.', fieldName)
  const rearranged = s.slice(4) + s.slice(0, 4)
  const numeric = rearranged.split('').map(c => /[A-Z]/.test(c) ? String(c.charCodeAt(0) - 55) : c).join('')
  try {
    const remainder = [...numeric].reduce((acc, d) => (Number(acc + d) % 97).toString(), '0')
    if (Number(remainder) !== 1) return _makeError('IBAN-Prüfziffer ungültig', 'Die IBAN besteht den Mod-97-Test nicht.', 'Prüfen Sie die IBAN auf Tippfehler.', fieldName)
  } catch {
    return _makeError('Ungültiges IBAN-Format', 'Die IBAN enthält ungültige Zeichen.', '', fieldName)
  }
  return _makeOk(fieldName)
}

function _validateMenge(
  value: string,
  fieldName: string,
  einheit: string,
  maxWarning?: number,
): ValidationResultData {
  const s = value.replace(',', '.')
  const n = parseFloat(s)
  if (isNaN(n)) return _makeError('Ungültige Mengeneingabe', `'${value}' ist keine gültige Zahl.`, 'Geben Sie z.B. 12,5 ein.', fieldName)
  if (n <= 0) return _makeError(`Menge muss größer als 0 ${einheit} sein`, 'Eine Menge von 0 oder weniger ist nicht zulässig.', `Geben Sie einen positiven Wert ein, z.B. 1,0 ${einheit}.`, fieldName)
  if (maxWarning !== undefined && n > maxWarning) return _makeWarning(`Ungewöhnlich hohe Menge: ${n.toLocaleString('de')} ${einheit}`, `Mengen über ${maxWarning.toLocaleString('de')} ${einheit} sind selten.`, `Haben Sie ggf. eine andere Einheit eingegeben?`, fieldName)
  return _makeOk(fieldName)
}

function _validatePreis(value: string, fieldName: string): ValidationResultData {
  const s = value.replace(',', '.')
  const n = parseFloat(s)
  if (isNaN(n)) return _makeError('Ungültige Preiseingabe', `'${value}' ist kein gültiger Betrag.`, 'Geben Sie z.B. 245,50 ein.', fieldName)
  if (n < 0) return _makeError('Negativer Preis nicht zulässig', 'Ein Preis kann nicht negativ sein.', 'Für Gutschriften nutzen Sie den Gutschrift-Workflow.', fieldName)
  return _makeOk(fieldName)
}

function _validateRequired(value: string, fieldName: string): ValidationResultData {
  if (!value || value.trim() === '') {
    return _makeError('Pflichtfeld', 'Dieses Feld muss ausgefüllt werden.', '', fieldName)
  }
  return _makeOk(fieldName)
}

function _runRule(rule: ValidationRuleId, value: string, fieldName: string): ValidationResultData {
  switch (rule) {
    case 'gln':      return _validateGln(value, fieldName)
    case 'iban':     return _validateIban(value, fieldName)
    case 'menge_t':  return _validateMenge(value, fieldName, 't', 10_000)
    case 'menge_kg': return _validateMenge(value, fieldName, 'kg', 100_000)
    case 'menge_stk': return _validateMenge(value, fieldName, 'Stk')
    case 'preis_eur': return _validatePreis(value, fieldName)
    case 'required': return _validateRequired(value, fieldName)
    default:         return _makeOk(fieldName)
  }
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

interface UseInlineValidationReturn {
  result: ValidationResultData | null
  validate: (value: string) => ValidationResultData
  reset: () => void
  isValid: boolean
  hasError: boolean
}

export function useInlineValidation(
  rule: ValidationRuleId,
  fieldName: string = rule,
  debounceMs = 300,
): UseInlineValidationReturn {
  const [result, setResult] = useState<ValidationResultData | null>(null)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const validate = useCallback(
    (value: string): ValidationResultData => {
      if (timerRef.current) clearTimeout(timerRef.current)
      const res = _runRule(rule, value, fieldName)
      timerRef.current = setTimeout(() => setResult(res), debounceMs)
      return res
    },
    [rule, fieldName, debounceMs],
  )

  const reset = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current)
    setResult(null)
  }, [])

  return {
    result,
    validate,
    reset,
    isValid: result?.is_valid ?? true,
    hasError: result?.has_errors ?? false,
  }
}
