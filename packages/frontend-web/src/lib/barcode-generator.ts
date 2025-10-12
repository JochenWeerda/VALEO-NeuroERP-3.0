/**
 * Barcode-Generator für VALERO NeuroERP
 * 
 * Unterstützt:
 * - EAN-13 (Europa-Standard)
 * - Prüfziffer-Berechnung nach GS1
 * - Barcode-Rendering (Canvas/SVG via JsBarcode später)
 */

// EAN-13 Präfix für Deutschland: 400-440
const VALERO_COMPANY_CODE = '12345' // 5-stellig (später: offizielle GS1-Nummer)
const COUNTRY_PREFIX = '400' // Deutschland

export type BarcodeFormat = 'EAN13' | 'EAN8' | 'CODE128'

/**
 * Generiert EAN-13 aus Artikelnummer
 * @param artikelnr - Artikelnummer (max. 5 Stellen)
 * @returns EAN-13 mit Prüfziffer (13 Stellen)
 */
export function generateEAN13(artikelnr: string): string {
  // Artikelnummer auf 5 Stellen normalisieren
  const productCode = artikelnr.toString().padStart(4, '0').slice(0, 4)
  
  // Basis-Code: 400 (Land) + 12345 (Firma) + XXXX (Artikel) = 12 Stellen
  const baseCode = COUNTRY_PREFIX + VALERO_COMPANY_CODE + productCode
  
  // Prüfziffer berechnen
  const checkDigit = calculateEAN13CheckDigit(baseCode)
  
  return baseCode + checkDigit
}

/**
 * Berechnet EAN-13 Prüfziffer nach GS1-Standard
 * @param code - 12-stelliger Basis-Code
 * @returns Prüfziffer (0-9)
 */
export function calculateEAN13CheckDigit(code: string): number {
  let sum = 0
  
  // Abwechselnd mit 1 und 3 multiplizieren (von rechts nach links)
  for (let i = 0; i < 12; i++) {
    const digit = parseInt(code[i], 10)
    const multiplier = i % 2 === 0 ? 1 : 3
    sum += digit * multiplier
  }
  
  // Nächstes Vielfaches von 10 minus Summe
  const checkDigit = (10 - (sum % 10)) % 10
  
  return checkDigit
}

/**
 * Validiert einen EAN-13 Barcode
 * @param ean - 13-stelliger EAN-Code
 * @returns true wenn gültig
 */
export function validateEAN13(ean: string): boolean {
  if (!/^\d{13}$/.test(ean)) return false
  
  const baseCode = ean.slice(0, 12)
  const providedCheckDigit = parseInt(ean[12], 10)
  const calculatedCheckDigit = calculateEAN13CheckDigit(baseCode)
  
  return providedCheckDigit === calculatedCheckDigit
}

/**
 * Formatiert EAN-13 mit Leerzeichen für bessere Lesbarkeit
 * @param ean - 13-stelliger EAN-Code
 * @returns Formatierter String (z.B. "400 12345 12345 6")
 */
export function formatEAN13(ean: string): string {
  if (ean.length !== 13) return ean
  
  return `${ean.slice(0, 3)} ${ean.slice(3, 8)} ${ean.slice(8, 12)} ${ean.slice(12)}`
}

/**
 * Extrahiert Artikelnummer aus EAN-13
 * @param ean - 13-stelliger EAN-Code
 * @returns Artikelnummer (4 Stellen) oder null wenn nicht VALERO-Code
 */
export function extractArticleNumber(ean: string): string | null {
  if (!validateEAN13(ean)) return null
  
  // Prüfe ob VALERO-Code
  const countryCode = ean.slice(0, 3)
  const companyCode = ean.slice(3, 8)
  
  if (countryCode !== COUNTRY_PREFIX || companyCode !== VALERO_COMPANY_CODE) {
    return null
  }
  
  // Extrahiere Artikel-Code
  return ean.slice(8, 12)
}

/**
 * Barcode-Metadata für Artikel
 */
export type BarcodeMetadata = {
  ean: string
  format: BarcodeFormat
  countryCode: string
  companyCode: string
  productCode: string
  checkDigit: number
  isValid: boolean
  isValeroCode: boolean
}

/**
 * Analysiert einen Barcode und gibt Metadata zurück
 * @param barcode - Barcode-String
 * @returns Barcode-Metadata
 */
export function analyzeBarcod(barcode: string): BarcodeMetadata | null {
  if (barcode.length !== 13) return null
  
  const isValid = validateEAN13(barcode)
  const countryCode = barcode.slice(0, 3)
  const companyCode = barcode.slice(3, 8)
  const productCode = barcode.slice(8, 12)
  const checkDigit = parseInt(barcode[12], 10)
  
  return {
    ean: barcode,
    format: 'EAN13',
    countryCode,
    companyCode,
    productCode,
    checkDigit,
    isValid,
    isValeroCode: countryCode === COUNTRY_PREFIX && companyCode === VALERO_COMPANY_CODE,
  }
}

/**
 * Batch-Generierung von EAN-13 Codes für mehrere Artikel
 * @param startArtikelnr - Start-Artikelnummer
 * @param count - Anzahl zu generierender Codes
 * @returns Array von EAN-13 Codes
 */
export function batchGenerateEAN13(startArtikelnr: number, count: number): string[] {
  const codes: string[] = []
  
  for (let i = 0; i < count; i++) {
    const artikelnr = (startArtikelnr + i).toString()
    codes.push(generateEAN13(artikelnr))
  }
  
  return codes
}

/**
 * Generiert Test-Barcodes für Development
 * @returns Array von Test-EAN-Codes mit Beschreibung
 */
export function generateTestBarcodes(): Array<{ ean: string; description: string }> {
  return [
    { ean: generateEAN13('1'), description: 'Artikel 1' },
    { ean: generateEAN13('100'), description: 'Artikel 100' },
    { ean: generateEAN13('1000'), description: 'Artikel 1000' },
    { ean: generateEAN13('9999'), description: 'Artikel 9999' },
  ]
}
