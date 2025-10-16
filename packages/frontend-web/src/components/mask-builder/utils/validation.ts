// VALEO Mask Builder Validation Utilities

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/
  return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''))
}

export function isValidDate(dateString: string): boolean {
  const date = new Date(dateString)
  return date instanceof Date && !isNaN(date.getTime())
}

export function isValidNumber(value: any, min?: number, max?: number): boolean {
  const num = Number(value)
  if (isNaN(num)) return false
  if (min !== undefined && num < min) return false
  if (max !== undefined && num > max) return false
  return true
}

export function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

export function isValidPostalCode(code: string, country = 'DE'): boolean {
  const patterns = {
    DE: /^\d{5}$/,
    AT: /^\d{4}$/,
    CH: /^\d{4}$/,
  }

  const pattern = patterns[country as keyof typeof patterns] || patterns.DE
  return pattern.test(code)
}

export function isValidTaxId(taxId: string, country = 'DE'): boolean {
  // German tax ID validation (simplified)
  if (country === 'DE') {
    return /^\d{11}$/.test(taxId.replace(/\s/g, ''))
  }
  return taxId.length > 0
}

export function isValidIBAN(iban: string): boolean {
  const ibanRegex = /^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$/
  return ibanRegex.test(iban.replace(/\s/g, '').toUpperCase())
}

export function isValidVATId(vatId: string, country = 'DE'): boolean {
  // German VAT ID validation (simplified)
  if (country === 'DE') {
    return /^DE\d{9}$/.test(vatId.toUpperCase())
  }
  return vatId.length > 0
}

export function validatePasswordStrength(password: string): {
  isValid: boolean
  score: number
  feedback: string[]
} {
  const feedback: string[] = []
  let score = 0

  if (password.length >= 8) {
    score += 1
  } else {
    feedback.push('Mindestens 8 Zeichen')
  }

  if (/[a-z]/.test(password)) {
    score += 1
  } else {
    feedback.push('Kleinbuchstaben erforderlich')
  }

  if (/[A-Z]/.test(password)) {
    score += 1
  } else {
    feedback.push('Großbuchstaben erforderlich')
  }

  if (/\d/.test(password)) {
    score += 1
  } else {
    feedback.push('Zahlen erforderlich')
  }

  if (/[^a-zA-Z\d]/.test(password)) {
    score += 1
  } else {
    feedback.push('Sonderzeichen erforderlich')
  }

  return {
    isValid: score >= 4,
    score,
    feedback
  }
}

export function validateBusinessRules(data: any, rules: Record<string, (value: any) => boolean>): Record<string, string> {
  const errors: Record<string, string> = {}

  Object.entries(rules).forEach(([field, validator]) => {
    if (!validator(data[field])) {
      errors[field] = `Ungültiger Wert für ${field}`
    }
  })

  return errors
}