import type { PriceList, PriceListItem } from './api/price-lists'

export type ProfessionalDocumentRecord = {
  id: string
  name: string
  category: string
  type: string
  date: string
  sizeLabel: string
  owner: string
  source: string
  objectRef: string
  objectKind: string
  status: 'neu' | 'vorgangsbelegt' | 'nachweisrelevant' | 'wiedervorlage' | 'archiv'
  followUp: string
}

export type ProfessionalDocumentWorkspace = {
  total: number
  evidenceCount: number
  workflowCount: number
  followUpCount: number
  latestDate?: string
  nextAction: string
}

export type ProfessionalPriceAgreement = {
  partnerName: string
  priceNet: number
  validFrom?: string | null
  validTo?: string | null
}

export type ProfessionalPriceWorkspace = {
  activeAgreements: number
  expiredAgreements: number
  bestCustomerPrice?: number
  marginPerUnit: number
  tierBreakCount: number
  nextAction: string
  pricePressure: 'niedrig' | 'mittel' | 'hoch'
}

export type TierBreak = {
  minQuantity: number
  maxQuantity?: number
  price: number
  discountPercent: number
  sourceLabel: string
}

function daysUntil(dateValue?: string | null): number | null {
  if (!dateValue) return null
  const target = new Date(dateValue)
  if (Number.isNaN(target.getTime())) return null
  return Math.ceil((target.getTime() - Date.now()) / 86_400_000)
}

function normalizeObjectRef(name: string): { objectRef: string; objectKind: string } {
  const patterns: Array<{ regex: RegExp; kind: string }> = [
    { regex: /(LS[-\s]?\d[\w-]*)/i, kind: 'Lieferschein' },
    { regex: /(RE[-\s]?\d[\w-]*)/i, kind: 'Rechnung' },
    { regex: /(KON[-\s]?\d[\w-]*)/i, kind: 'Kontrakt' },
    { regex: /(PO[-\s]?\d[\w-]*)/i, kind: 'Bestellung' },
    { regex: /(AV[-\s]?\d[\w-]*)/i, kind: 'Avis' },
  ]
  for (const pattern of patterns) {
    const match = name.match(pattern.regex)
    if (match?.[1]) {
      return { objectRef: match[1].replace(/\s+/g, ''), objectKind: pattern.kind }
    }
  }
  return { objectRef: 'nicht zugeordnet', objectKind: 'Allgemein' }
}

export function buildDocumentRecord(input: {
  id: string
  name: string
  category: string
  type: string
  date: string
  sizeLabel: string
  owner: string
  source: string
}): ProfessionalDocumentRecord {
  const base = normalizeObjectRef(`${input.name} ${input.category}`)
  const text = `${input.name} ${input.category}`.toLowerCase()
  const dueInDays = daysUntil(input.date)
  let status: ProfessionalDocumentRecord['status'] = 'vorgangsbelegt'
  let followUp = 'Im Vorgang verfuegbar halten'

  if (text.includes('analyse') || text.includes('deklaration') || text.includes('naehrstoff') || text.includes('zertifikat')) {
    status = 'nachweisrelevant'
    followUp = 'Nachweis aktuell halten'
  }
  if ((text.includes('vertrag') || text.includes('compliance') || text.includes('sds') || text.includes('sachkunde')) && dueInDays !== null && dueInDays <= 30) {
    status = 'wiedervorlage'
    followUp = 'Wiedervorlage vor Ablauf pruefen'
  } else if (new Date(input.date).getTime() < Date.now() - 365 * 86_400_000) {
    status = 'archiv'
    followUp = 'Archiviert, nur bei Rueckfragen oeffnen'
  } else if (new Date(input.date).getTime() >= Date.now() - 14 * 86_400_000) {
    status = 'neu'
    followUp = 'Neu eingegangen, Zuordnung pruefen'
  }

  return {
    ...input,
    ...base,
    status,
    followUp,
  }
}

export function buildDocumentWorkspace(records: ProfessionalDocumentRecord[]): ProfessionalDocumentWorkspace {
  const evidenceCount = records.filter((record) => record.status === 'nachweisrelevant').length
  const workflowCount = records.filter((record) => record.status === 'vorgangsbelegt' || record.status === 'neu').length
  const followUpCount = records.filter((record) => record.status === 'wiedervorlage').length
  const latestDate = records
    .map((record) => record.date)
    .filter(Boolean)
    .sort((left, right) => new Date(right).getTime() - new Date(left).getTime())[0]

  let nextAction = 'Dokumentenlage stabil'
  if (followUpCount > 0) nextAction = 'Wiedervorlagen und Ablaufdaten pruefen'
  else if (evidenceCount > workflowCount) nextAction = 'Nachweisdokumente den operativen Vorgaengen zuordnen'
  else if (records.some((record) => record.objectRef === 'nicht zugeordnet')) nextAction = 'Objektbezug fuer unzugeordnete Dokumente nachziehen'

  return {
    total: records.length,
    evidenceCount,
    workflowCount,
    followUpCount,
    latestDate,
    nextAction,
  }
}

function isCurrentlyActive(validFrom?: string | null, validTo?: string | null): boolean {
  const now = Date.now()
  const fromOk = !validFrom || new Date(validFrom).getTime() <= now
  const toOk = !validTo || new Date(validTo).getTime() >= now
  return fromOk && toOk
}

export function extractTierBreaks(priceLists: PriceList[], matcher: {
  articleId?: string
  articleNumber?: string
  articleGroup?: string
}): TierBreak[] {
  const matches: TierBreak[] = []
  for (const priceList of priceLists.filter((entry) => entry.is_active)) {
    for (const item of priceList.items ?? []) {
      const articleMatch =
        (matcher.articleId && item.article_id === matcher.articleId) ||
        (matcher.articleNumber && item.article_number === matcher.articleNumber) ||
        false
      const groupMatch = matcher.articleGroup ? priceList.name.toLowerCase().includes(matcher.articleGroup.toLowerCase()) : false
      if (!articleMatch && !groupMatch) continue
      if (!isCurrentlyActive(item.valid_from, item.valid_until)) continue
      matches.push({
        minQuantity: Number(item.min_quantity ?? 0),
        maxQuantity: item.max_quantity == null ? undefined : Number(item.max_quantity),
        price: Number(item.unit_price ?? 0),
        discountPercent: Number(item.discount_percent ?? 0),
        sourceLabel: priceList.name,
      })
    }
  }
  return matches.sort((left, right) => right.minQuantity - left.minQuantity)
}

export function fallbackTierBreaks(category: string, basePrice: number): TierBreak[] {
  const normalized = category.toLowerCase()
  if (normalized.includes('futter')) {
    return [
      { minQuantity: 240, price: basePrice, discountPercent: 0, sourceLabel: 'Standardstaffel' },
      { minQuantity: 120, price: basePrice + 0.5, discountPercent: 0, sourceLabel: 'Standardstaffel' },
      { minQuantity: 50, price: basePrice + 1, discountPercent: 0, sourceLabel: 'Standardstaffel' },
      { minQuantity: 1, price: basePrice + 2, discountPercent: 0, sourceLabel: 'Standardstaffel' },
    ]
  }
  if (normalized.includes('duenger')) {
    return [
      { minQuantity: 240, price: basePrice, discountPercent: 0, sourceLabel: 'Standardstaffel' },
      { minQuantity: 100, price: basePrice + 0.8, discountPercent: 0, sourceLabel: 'Standardstaffel' },
      { minQuantity: 25, price: basePrice + 1.5, discountPercent: 0, sourceLabel: 'Standardstaffel' },
      { minQuantity: 1, price: basePrice + 2.5, discountPercent: 0, sourceLabel: 'Standardstaffel' },
    ]
  }
  return [{ minQuantity: 1, price: basePrice, discountPercent: 0, sourceLabel: 'Listenpreis' }]
}

export function getTierInfo(tierBreaks: TierBreak[], quantity: number, fallbackPrice: number): {
  currentPrice: number
  surcharge: number
  nextTier?: { minQuantity: number; savings: number }
} {
  const sorted = [...tierBreaks].sort((left, right) => right.minQuantity - left.minQuantity)
  const current = sorted.find((tier) => quantity >= tier.minQuantity) ?? sorted.at(-1)
  if (!current) return { currentPrice: fallbackPrice, surcharge: 0 }
  const currentPrice = current.price
  const surcharge = Math.max(0, currentPrice - fallbackPrice)
  const nextBetter = sorted.find((tier) => tier.minQuantity > quantity && tier.price < currentPrice)
  return {
    currentPrice,
    surcharge,
    nextTier: nextBetter
      ? { minQuantity: nextBetter.minQuantity, savings: Math.max(0, currentPrice - nextBetter.price) }
      : undefined,
  }
}

export function buildPriceWorkspace(input: {
  listPrice: number
  purchasePrice: number
  agreements: ProfessionalPriceAgreement[]
  tierBreaks: TierBreak[]
}): ProfessionalPriceWorkspace {
  const activeAgreements = input.agreements.filter((agreement) => isCurrentlyActive(agreement.validFrom, agreement.validTo)).length
  const expiredAgreements = input.agreements.length - activeAgreements
  const bestCustomerPrice = input.agreements.length > 0
    ? Math.min(...input.agreements.map((agreement) => agreement.priceNet))
    : undefined
  const marginPerUnit = input.listPrice - input.purchasePrice
  let pricePressure: ProfessionalPriceWorkspace['pricePressure'] = 'niedrig'
  if (marginPerUnit <= 0 || (bestCustomerPrice !== undefined && bestCustomerPrice < input.purchasePrice)) {
    pricePressure = 'hoch'
  } else if (marginPerUnit < input.listPrice * 0.12 || activeAgreements > 3) {
    pricePressure = 'mittel'
  }

  let nextAction = 'Preisbild stabil'
  if (pricePressure === 'hoch') nextAction = 'Marge und Sonderkonditionen sofort pruefen'
  else if (expiredAgreements > 0) nextAction = 'Abgelaufene Vereinbarungen verlaengern oder bereinigen'
  else if (input.tierBreaks.length === 0) nextAction = 'Staffel- oder Listenlogik hinterlegen'

  return {
    activeAgreements,
    expiredAgreements,
    bestCustomerPrice,
    marginPerUnit,
    tierBreakCount: input.tierBreaks.length,
    nextAction,
    pricePressure,
  }
}

export function formatCurrency(value: number, maximumFractionDigits = 2): string {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits,
  }).format(value)
}
