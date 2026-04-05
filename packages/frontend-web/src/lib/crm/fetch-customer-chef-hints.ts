import { apiClient } from '@/lib/api-client'
import {
  businessPartnerService,
  type BusinessPartnerEnvelope,
  type Instruction,
} from '@/lib/services/business-partner-service'

export type CustomerChefHints = {
  crmChefanweisung: string | null
  instructions: Instruction[]
  partnerId: string | null
}

function normalizeNum(s: string): string {
  return s.trim().replace(/\s+/g, '')
}

function instructionIsActive(inst: Instruction, ref: Date): boolean {
  const day = ref.toISOString().slice(0, 10)
  const from = inst.valid_from ? String(inst.valid_from).slice(0, 10) : null
  const to = inst.valid_to ? String(inst.valid_to).slice(0, 10) : null
  if (from && from > day) return false
  if (to && to < day) return false
  return true
}

function findPartnerForCustomerNumber(
  partners: BusinessPartnerEnvelope[],
  customerNumber: string,
): BusinessPartnerEnvelope | undefined {
  const n = normalizeNum(customerNumber)
  return partners.find((p) => {
    const core = p.business_partner.core_identity
    const fin = p.business_partner.finance as { debtor_account?: string | null } | undefined
    const pn = normalizeNum(core.partner_number || '')
    const da = fin?.debtor_account ? normalizeNum(String(fin.debtor_account)) : ''
    return pn === n || (da && da === n)
  })
}

const PRIORITY_ORDER: Record<Instruction['instruction_priority'], number> = {
  critical: 0,
  high: 1,
  normal: 2,
  low: 3,
}

function sortInstructions(list: Instruction[]): Instruction[] {
  return [...list].sort(
    (a, b) =>
      (PRIORITY_ORDER[a.instruction_priority] ?? 9) - (PRIORITY_ORDER[b.instruction_priority] ?? 9),
  )
}

/**
 * Lädt CRM-Chefanweisung und strukturierte Chef-Anweisungen (Business-Partner / Tab 21)
 * über dieselbe API wie die Kundenstamm-Maske — keine zweite Datenquelle.
 */
/**
 * Ordnet einen CRM-Kunden (ID und/oder Kundennummer) einem Business-Partner (Verkaufs-Stammdaten) zu.
 * Kein Treffer → Aufrufer kann auf die CRM-Detailmaske fallbacken.
 */
export async function resolveBusinessPartnerIdForCrmCustomer(opts: {
  crmCustomerId?: string | null
  customerNumber?: string | null
  /** Aus API GET /crm/customers/:id (Feld business_partner_id), falls gesetzt */
  businessPartnerIdHint?: string | null
}): Promise<string | null> {
  const hint = opts.businessPartnerIdHint?.trim()
  if (hint) return hint

  let cn = opts.customerNumber?.trim() ?? ''
  if (!cn && opts.crmCustomerId) {
    try {
      const res = await apiClient.get<{ customer_number?: string | null }>(
        `/api/v1/crm/customers/${opts.crmCustomerId}`,
      )
      cn = String(res.data?.customer_number ?? '').trim()
    } catch {
      return null
    }
  }
  if (!cn) return null
  const partners = await businessPartnerService.list({ search: normalizeNum(cn) })
  const match = findPartnerForCustomerNumber(partners, cn)
  return match?.business_partner.core_identity.partner_id ?? null
}

export async function fetchCustomerChefHints(opts: {
  customerNumber: string | undefined | null
  crmCustomerId: string | undefined | null
  chefanweisungFromCustomer?: string | null
}): Promise<CustomerChefHints> {
  let crmText = opts.chefanweisungFromCustomer?.trim() || null

  if (opts.crmCustomerId) {
    try {
      const res = await apiClient.get<{
        chefanweisung?: string | null
        executive_note?: string | null
      }>(`/api/v1/crm/customers/${opts.crmCustomerId}`)
      const d = res.data
      const t = (d.chefanweisung ?? d.executive_note)?.trim()
      if (t) crmText = t
    } catch {
      /* Kunde nicht ladbar — Fallback aus Selection */
    }
  }

  const cn = opts.customerNumber?.trim()
  if (!cn) {
    return { crmChefanweisung: crmText, instructions: [], partnerId: null }
  }

  const partners = await businessPartnerService.list({ search: normalizeNum(cn) })
  const match = findPartnerForCustomerNumber(partners, cn)
  const partnerId = match?.business_partner.core_identity.partner_id ?? null
  if (!partnerId) {
    return { crmChefanweisung: crmText, instructions: [], partnerId: null }
  }

  const all = await businessPartnerService.listInstructions(partnerId)
  const now = new Date()
  const active = all.filter((i) => instructionIsActive(i, now))
  return {
    crmChefanweisung: crmText,
    instructions: sortInstructions(active),
    partnerId,
  }
}
