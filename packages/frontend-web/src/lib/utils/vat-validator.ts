/**
 * EU/EWR USt-ID Format-Validierung (ohne VIES-Anfrage).
 * Formate nach EU-Vorgaben; optionale Checksummen je Land ausbaubar.
 */

/** Länder-spezifische Muster (Regex); leeres Muster = kein Format-Check. */
const VAT_PATTERNS: Record<string, RegExp> = {
  DE: /^DE\d{9}$/,           // DE + 9 Ziffern
  AT: /^ATU\d{8}$/,         // ATU + 8 Ziffern
  NL: /^NL\d{9}B\d{2}$/,    // NL + 9 Ziffern + B + 2 Ziffern
  FR: /^FR[A-HJ-NP-Z0-9]{2}\d{9}$/,  // FR + 2 Zeichen (ohne O,I) + 9 Ziffern
  BE: /^BE0?\d{9}$/,        // BE + 9 Ziffern (evtl. führende 0)
  CH: /^CHE\d{9}$/,         // CH: CHE + 9 Ziffern (normalisiert ohne Punkte)
  IT: /^IT\d{11}$/,         // IT + 11 Ziffern
  ES: /^ES[A-Z0-9]\d{7}[A-Z0-9]$/i,  // ES + 1 Zeichen + 7 Ziffern + 1 Zeichen
  PL: /^PL\d{10}$/,         // PL + 10 Ziffern
  GB: /^GB(\d{9}|\d{12}|GD\d{3}|HA\d{3})$/,  // UK (historisch)
}

/**
 * Normalisiert USt-ID (Leerzeichen/ Bindestriche entfernen, Großschreibung).
 */
export function normalizeVatId(vatId: string): string {
  if (!vatId || typeof vatId !== 'string') return ''
  return vatId.replace(/\s/g, '').replace(/-/g, '').toUpperCase().trim()
}

export type VatValidationResult = {
  valid: boolean
  country?: string
  normalized?: string
  message?: string
}

/**
 * Prüft das Format einer USt-ID (EU/CH). Keine VIES-/Netzwerk-Anfrage.
 * Leeres Feld gilt als gültig (optionales Feld).
 */
export function validateVatIdFormat(vatId: string | undefined | null): VatValidationResult {
  const raw = vatId ?? ''
  const normalized = normalizeVatId(raw)
  if (normalized.length === 0) {
    return { valid: true }
  }

  const prefix2 = normalized.slice(0, 2)
  const pattern = VAT_PATTERNS[prefix2]
  if (!pattern) {
    return {
      valid: false,
      normalized,
      country: prefix2,
      message: `Unbekanntes USt-ID-Format für Länderkürzel "${prefix2}". Erlaubt: DE, AT, NL, FR, BE, CH, IT, ES, PL.`,
    }
  }

  if (!pattern.test(normalized)) {
    return {
      valid: false,
      normalized,
      country: prefix2,
      message: `USt-ID hat kein gültiges Format für ${prefix2} (z.B. DE123456789, ATU12345678).`,
    }
  }

  return { valid: true, normalized, country: prefix2 }
}
