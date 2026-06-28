import type { Kontrakt } from '@/lib/api/kontrakte'

export function mapKontraktToMask(kontrakt: Kontrakt | null | undefined): Record<string, unknown> {
  if (!kontrakt) return {}
  return {
    contract: {
      contract_no: kontrakt.contract_no,
      party_id: kontrakt.party_id,
      contract_type: kontrakt.contract_type,
      status: kontrakt.status,
      valid_from: kontrakt.valid_from ?? '',
      valid_to: kontrakt.valid_to ?? '',
      total_quantity: kontrakt.total_quantity,
      rest_quantity: kontrakt.rest_quantity,
      unit: kontrakt.unit,
      payment_terms: kontrakt.payment_terms ?? '',
      notes: kontrakt.notes ?? '',
    },
  }
}
