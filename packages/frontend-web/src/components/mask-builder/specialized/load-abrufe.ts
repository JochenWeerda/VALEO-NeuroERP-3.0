import { isAxiosError } from 'axios'
import { apiClient } from '@/lib/api-client'
import type { DispositionOrderCard } from './disposition-board'

export const KONTRAKTE_LIST_ENDPOINT = '/api/v1/kontrakte'
export const DISPOSITIONEN_PATH = (kontraktId: string) => `/api/v1/kontrakte/${encodeURIComponent(kontraktId)}/dispositionen`

const ASSIGNABLE = new Set(['OFFEN', 'FREIGEGEBEN'])

/** Gleicher Text auf Dispo-Tafel und Home-Ranking — kein Fake-Leer bei 401/ohne Sitzung. */
export const ABRUFE_AUTH_ERROR = 'Abrufe nicht lesbar: Recht oder Anmeldung fehlt.'

export type KontraktAbrufRow = {
  id: string
  kontrakt_id: string
  kontrakt_nr?: string
  kontrakt_pos_nr?: number
  disposition_nr?: number
  menge?: number
  status?: string
}

type KontraktListPayload = {
  items?: Array<{ contract_id?: string }>
}

function readError(error: unknown): string {
  if (isAxiosError(error)) {
    const status = error.response?.status
    if (status === 401 || status === 403) {
      return ABRUFE_AUTH_ERROR
    }
    if (status === 503) {
      return 'Abrufe nicht lesbar: Dienst oder Schema nicht bereit.'
    }
    if (status != null) return `Abrufe nicht lesbar (HTTP ${status}).`
  }
  return 'Abrufe nicht lesbar.'
}

function asCard(row: KontraktAbrufRow): DispositionOrderCard {
  const nr = row.kontrakt_nr || row.kontrakt_id
  const disp = row.disposition_nr != null ? ` Abruf ${row.disposition_nr}` : ''
  return {
    id: row.id,
    label: `${nr}${disp}`.trim(),
    quantity: Number(row.menge ?? 0),
    contractId: row.kontrakt_id,
    abrufId: row.id,
  }
}

/** Adapter auf den bestehenden Dispositionen-Endpunkt. Kein Mock, kein stilles []. */
export async function fetchOpenAbrufe(): Promise<DispositionOrderCard[]> {
  let list: KontraktListPayload
  try {
    const response = await apiClient.get<KontraktListPayload>(KONTRAKTE_LIST_ENDPOINT, {
      params: { status: 'OFFEN', limit: 20, include_done: false },
    })
    list = response.data ?? {}
  } catch (error) {
    throw new Error(readError(error))
  }

  const contracts = (list.items ?? []).map((item) => item.contract_id).filter((id): id is string => Boolean(id))
  const cards: DispositionOrderCard[] = []
  let lastError: string | null = null

  for (const kontraktId of contracts) {
    try {
      const response = await apiClient.get<KontraktAbrufRow[]>(DISPOSITIONEN_PATH(kontraktId))
      const rows = Array.isArray(response.data) ? response.data : []
      for (const row of rows) {
        if (!row?.id || !ASSIGNABLE.has(String(row.status ?? '').toUpperCase())) continue
        cards.push(asCard(row))
      }
    } catch (error) {
      lastError = readError(error)
    }
  }

  if (cards.length === 0 && lastError && contracts.length > 0) {
    throw new Error(lastError)
  }
  return cards
}
