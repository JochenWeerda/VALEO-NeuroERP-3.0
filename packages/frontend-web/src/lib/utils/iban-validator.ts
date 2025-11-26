/**
 * IBAN Validator
 * Validates IBAN (International Bank Account Number) according to ISO 13616
 */

/**
 * Validates an IBAN using the mod-97-10 algorithm
 * @param iban - The IBAN to validate
 * @returns true if valid, false otherwise
 */
export function validateIBAN(iban: string): boolean {
  if (!iban) return false

  // Remove spaces and convert to uppercase
  const normalized = iban.replace(/\s/g, '').toUpperCase()

  // Basic format check: 2 letters + 2 digits + up to 30 alphanumeric characters
  if (!/^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$/.test(normalized)) {
    return false
  }

  // Move first 4 characters to end
  const rearranged = normalized.slice(4) + normalized.slice(0, 4)

  // Replace letters with numbers (A=10, B=11, ..., Z=35)
  const numeric = rearranged.replace(/[A-Z]/g, (char) => {
    return (char.charCodeAt(0) - 55).toString()
  })

  // Calculate mod 97
  let remainder = ''
  for (let i = 0; i < numeric.length; i++) {
    remainder = (remainder + numeric[i]).replace(/^0+/, '')
    if (remainder.length >= 9) {
      remainder = (parseInt(remainder.slice(0, 9)) % 97).toString() + remainder.slice(9)
    }
  }
  const mod97 = parseInt(remainder) % 97

  // Valid IBAN has mod 97 = 1
  return mod97 === 1
}

/**
 * Formats an IBAN with spaces every 4 characters
 * @param iban - The IBAN to format
 * @returns Formatted IBAN
 */
export function formatIBAN(iban: string): string {
  if (!iban) return ''
  const normalized = iban.replace(/\s/g, '').toUpperCase()
  return normalized.replace(/(.{4})/g, '$1 ').trim()
}

/**
 * Gets the country code from an IBAN
 * @param iban - The IBAN
 * @returns Country code (2 letters) or null
 */
export function getIBANCountryCode(iban: string): string | null {
  if (!iban) return null
  const normalized = iban.replace(/\s/g, '').toUpperCase()
  const match = normalized.match(/^([A-Z]{2})/)
  return match ? match[1] : null
}

/**
 * Gets the check digits from an IBAN
 * @param iban - The IBAN
 * @returns Check digits (2 digits) or null
 */
export function getIBANCheckDigits(iban: string): string | null {
  if (!iban) return null
  const normalized = iban.replace(/\s/g, '').toUpperCase()
  const match = normalized.match(/^[A-Z]{2}(\d{2})/)
  return match ? match[1] : null
}

/**
 * IBAN Lookup Response from backend
 */
export interface IBANLookupResponse {
  valid: boolean
  iban: string
  bank_name?: string | null
  bic?: string | null
  bank_code?: string | null
  city?: string | null
  zip?: string | null
  country?: string | null
  message?: string | null
}

/**
 * Lookup IBAN and retrieve bank information from backend
 * @param iban - The IBAN to lookup
 * @returns IBANLookupResponse with validation result and bank information
 */
export async function lookupIBAN(iban: string): Promise<IBANLookupResponse> {
  if (!iban) {
    throw new Error('IBAN is required')
  }

  const normalized = iban.replace(/\s/g, '').replace(/-/g, '').toUpperCase()
  
  try {
    const response = await fetch(
      `/api/v1/finance/iban-lookup/validate/${encodeURIComponent(normalized)}?get_bic=true&validate_bank_code=true`
    )
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to lookup IBAN' }))
      throw new Error(error.detail || 'Failed to lookup IBAN')
    }
    
    return await response.json()
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Failed to lookup IBAN')
  }
}

