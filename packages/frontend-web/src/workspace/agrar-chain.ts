import { isAxiosError } from 'axios'
import { apiClient } from '@/lib/api-client'
import type { TypedFachaktion, WorkspaceSignal } from './types'

/** GET /api/v1/workspace/agrar-chain — Read-Model, keine Buchung. Mandant serverseitig. */
export const AGRAR_CHAIN_PATH = '/api/v1/workspace/agrar-chain'

/** KonContract-Index. `status` filtert nur OFFEN|ERLEDIGT|STORNIERT — ohne Filter, clientseitig. */
export const OPEN_KONTRAKTE_PATH = '/api/v1/kontrakte'
export const OPEN_KONTRAKTE_PARAMS = { limit: 20, include_done: true } as const

/** AgrarContract-Index — nicht /api/v1/kontrakte. */
export const AGRAR_CONTRACTS_PATH = '/api/v1/agrar/contracts'
export const AGRAR_CONTRACTS_PARAMS = { limit: 20 } as const

export function dispositionenPath(kontraktId: string): string {
  return `${OPEN_KONTRAKTE_PATH}/${encodeURIComponent(kontraktId)}/dispositionen`
}

const KON_CONTRACT_STATUSES = new Set(['OFFEN', 'ERLEDIGT', 'STORNIERT'])
const AGRAR_CONTRACT_STATUSES = new Set([
  'open',
  'partially_allocated',
  'fulfilled',
  'cancelled',
  'closed',
])
const KON_ABRUF_RANK: Record<string, number> = {
  STORNIERT: 0,
  OFFEN: 1,
  FREIGEGEBEN: 2,
  GELIEFERT: 3,
}

export type AgrarSourceModel = 'kon' | 'agrar'

export type AgrarNextStep =
  | 'disposition'
  | 'waage'
  | 'qualitaet'
  | 'abrechnung'
  | 'done'
  | 'blocked'

export type AgrarChainHint = {
  contract_ref: string
  source_model: AgrarSourceModel
  next_step: AgrarNextStep
  reason: string
}

export type AgrarChainQuery = {
  contract_ref: string
  source_model: AgrarSourceModel
  contract_status?: string
  disposition_status?: string
  weighing_present?: boolean
  weighing_status?: string
  quality_is_final?: boolean
  settlement_status?: string
  allocation_status?: string
  harvest_release_status?: string
  quality_status?: string
}

export type AgrarChainLink = {
  route: string | null
  label: string
  clickable: boolean
}

export type AgrarChainViewState =
  | { status: 'pending' }
  | { status: 'hidden' }
  | { status: 'empty' }
  | { status: 'error'; message: string }
  | { status: 'ready'; hints: AgrarChainHint[]; warning?: string }

export const EMPTY_AGRAR_CHAIN_QUERIES: AgrarChainQuery[] = []

const NEXT_STEPS = new Set<AgrarNextStep>([
  'disposition',
  'waage',
  'qualitaet',
  'abrechnung',
  'done',
  'blocked',
])

/** Echte Maskenrouten — done/blocked bleiben Status ohne Buchungs-Klick. */
export const AGRAR_NEXT_STEP_LINKS: Record<AgrarNextStep, AgrarChainLink> = {
  disposition: {
    route: '/disposition/touren-disposition',
    label: 'Disposition',
    clickable: true,
  },
  waage: {
    route: '/waage/wiegungen',
    label: 'Waage',
    clickable: true,
  },
  qualitaet: {
    route: '/annahme/qualitaets-check',
    label: 'Qualitaet',
    clickable: true,
  },
  abrechnung: {
    route: '/annahme/abrechnung',
    label: 'Abrechnung',
    clickable: true,
  },
  done: {
    route: null,
    label: 'Abgeschlossen',
    clickable: false,
  },
  blocked: {
    route: null,
    label: 'Blockiert',
    clickable: false,
  },
}

function nonempty(value: string | undefined): value is string {
  return typeof value === 'string' && value.trim().length > 0
}

/** Ohne Status-Projektion liefert der GET nur den Default-Fallback — das ist keine Kette. */
export function hasChainProjection(query: AgrarChainQuery): boolean {
  if (!nonempty(query.contract_ref)) {
    return false
  }
  if (query.source_model !== 'kon' && query.source_model !== 'agrar') {
    return false
  }
  return (
    nonempty(query.contract_status)
    || nonempty(query.disposition_status)
    || nonempty(query.weighing_status)
    || nonempty(query.settlement_status)
    || nonempty(query.allocation_status)
    || nonempty(query.harvest_release_status)
    || nonempty(query.quality_status)
    || query.weighing_present === true
    || query.quality_is_final === true
  )
}

export function agrarChainLinkFor(step: AgrarNextStep): AgrarChainLink {
  return AGRAR_NEXT_STEP_LINKS[step]
}

/**
 * Home zeigt den Server-`next_step` 1:1. `fulfilled` wird nicht lokal
 * auf Qualitaet zurueckgebogen, auch nicht bei source_model=agrar.
 */
export function agrarChainLinkForHint(
  hint: Pick<AgrarChainHint, 'next_step'>,
): AgrarChainLink {
  return agrarChainLinkFor(hint.next_step)
}

/**
 * Naechste Schritte, die der Client schon als Klick anbietet.
 * done/blocked bleiben Status und werden nicht in den Rang geschoben.
 */
const HANDLUNGSBEDARF_STEPS = new Set<AgrarNextStep>([
  'disposition',
  'waage',
  'qualitaet',
  'abrechnung',
])

/**
 * Dieselben geladenen Hinweise als situative Signale fuer rankWorkspaceItems.
 * Route nur ueber agrarChainLinkForHint. Leere Liste, 401 (hidden) und Fehler
 * liefern nichts. quality_is_final setzt diese Funktion nicht.
 */
export function situationalItemsFromAgrarChain(state: AgrarChainViewState): {
  actions: TypedFachaktion[]
  signals: WorkspaceSignal[]
} {
  if (state.status !== 'ready') {
    return { actions: [], signals: [] }
  }

  const actions: TypedFachaktion[] = []
  const signals: WorkspaceSignal[] = []
  const seen = new Set<string>()
  for (const hint of state.hints) {
    if (!HANDLUNGSBEDARF_STEPS.has(hint.next_step)) {
      continue
    }
    const link = agrarChainLinkForHint(hint)
    if (!link.clickable || link.route == null) {
      continue
    }
    const id = `agrar.chain.${hint.source_model}.${hint.contract_ref}.${hint.next_step}`
    if (seen.has(id)) {
      continue
    }
    seen.add(id)
    actions.push({
      id,
      label: `${hint.contract_ref}: ${link.label}`,
      kind: 'navigate',
      layer: 'situational',
      keywords: [hint.contract_ref, hint.next_step, link.label],
      requiredScopes: [],
      businessDomain: 'agrar',
      target: { route: link.route },
      mcpIntent: 'navigate',
      reasonTemplate: hint.reason || link.label,
    })
    signals.push({
      id: `agrar-chain:${hint.source_model}:${hint.contract_ref}:${hint.next_step}`,
      kind: 'open-task',
      layer: 'situational',
      relatedActionIds: [id],
      severity: 3,
      source: 'agrar-chain',
    })
  }
  return { actions, signals }
}

/** Server-Antwort 1:1. Kein lokales Umschreiben von next_step. */
export function parseAgrarChainHint(payload: unknown): AgrarChainHint | null {
  if (!payload || typeof payload !== 'object') {
    return null
  }
  const raw = payload as Record<string, unknown>
  const contractRef = typeof raw.contract_ref === 'string' ? raw.contract_ref.trim() : ''
  const source = raw.source_model
  const step = raw.next_step
  const reason = typeof raw.reason === 'string' ? raw.reason : ''
  if (!contractRef) {
    return null
  }
  if (source !== 'kon' && source !== 'agrar') {
    return null
  }
  if (typeof step !== 'string' || !NEXT_STEPS.has(step as AgrarNextStep)) {
    return null
  }
  return {
    contract_ref: contractRef,
    source_model: source,
    next_step: step as AgrarNextStep,
    reason,
  }
}

export function agrarChainParams(query: AgrarChainQuery): Record<string, string | boolean> {
  const params: Record<string, string | boolean> = {
    contract_ref: query.contract_ref.trim(),
    source_model: query.source_model,
  }
  if (nonempty(query.contract_status)) params.contract_status = query.contract_status.trim()
  if (nonempty(query.disposition_status)) params.disposition_status = query.disposition_status.trim()
  if (nonempty(query.weighing_status)) params.weighing_status = query.weighing_status.trim()
  if (nonempty(query.settlement_status)) params.settlement_status = query.settlement_status.trim()
  if (nonempty(query.allocation_status)) params.allocation_status = query.allocation_status.trim()
  if (nonempty(query.harvest_release_status)) {
    params.harvest_release_status = query.harvest_release_status.trim()
  }
  if (nonempty(query.quality_status)) params.quality_status = query.quality_status.trim()
  if (query.weighing_present === true) params.weighing_present = true
  if (query.quality_is_final === true) params.quality_is_final = true
  return params
}

function readString(value: unknown): string {
  return typeof value === 'string' ? value.trim() : ''
}

function readKontraktItems(payload: unknown): unknown[] {
  if (Array.isArray(payload)) {
    return payload
  }
  if (!payload || typeof payload !== 'object') {
    return []
  }
  const raw = payload as Record<string, unknown>
  if (Array.isArray(raw.items)) {
    return raw.items
  }
  if (raw.data && typeof raw.data === 'object') {
    const nested = raw.data as Record<string, unknown>
    if (Array.isArray(nested.items)) {
      return nested.items
    }
    if (Array.isArray(raw.data)) {
      return raw.data
    }
  }
  return []
}

/** Nur Felder, die der Kontrakt-Index wirklich liefert — kein AgrarContract. */
export function queriesFromKontraktIndex(payload: unknown): AgrarChainQuery[] {
  const queries: AgrarChainQuery[] = []
  for (const item of readKontraktItems(payload)) {
    if (!item || typeof item !== 'object') {
      continue
    }
    const raw = item as Record<string, unknown>
    const contractRef = readString(raw.contract_id) || readString(raw.id)
    if (!contractRef) {
      continue
    }
    const query: AgrarChainQuery = {
      contract_ref: contractRef,
      source_model: 'kon',
    }
    const status = readString(raw.status).toUpperCase()
    if (KON_CONTRACT_STATUSES.has(status)) {
      query.contract_status = status
    }
    const lieferstatus = readString(raw.lieferstatus).toUpperCase()
    if (lieferstatus in KON_ABRUF_RANK) {
      query.disposition_status = lieferstatus
    }
    if (hasChainProjection(query)) {
      queries.push(query)
    }
  }
  return queries
}

function applyOptionalAgrarFields(query: AgrarChainQuery, raw: Record<string, unknown>): void {
  const qualityStatus = readString(raw.quality_status)
  if (qualityStatus) {
    query.quality_status = qualityStatus
  }
  if (raw.quality_is_final === true) {
    query.quality_is_final = true
  }
  const settlement = readString(raw.settlement_status)
  if (settlement) {
    query.settlement_status = settlement
  }
  const harvest = readString(raw.harvest_release_status)
  if (harvest) {
    query.harvest_release_status = harvest
  }
  const weighing = readString(raw.weighing_status)
  if (weighing) {
    query.weighing_status = weighing
  }
  const allocation = readString(raw.allocation_status)
  if (allocation) {
    query.allocation_status = allocation
  }
}

/** AgrarContract-Liste: id + status, QS/Settlement nur wenn der Payload sie wirklich hat. */
export function queriesFromAgrarContractIndex(payload: unknown): AgrarChainQuery[] {
  const queries: AgrarChainQuery[] = []
  for (const item of readKontraktItems(payload)) {
    if (!item || typeof item !== 'object') {
      continue
    }
    const raw = item as Record<string, unknown>
    const contractRef = readString(raw.id) || readString(raw.contract_id)
    if (!contractRef) {
      continue
    }
    const status = readString(raw.status).toLowerCase()
    if (!AGRAR_CONTRACT_STATUSES.has(status)) {
      continue
    }
    const query: AgrarChainQuery = {
      contract_ref: contractRef,
      source_model: 'agrar',
      contract_status: status,
    }
    applyOptionalAgrarFields(query, raw)
    if (hasChainProjection(query)) {
      queries.push(query)
    }
  }
  return queries
}

export function isAgrarChainUnavailable(error: unknown): boolean {
  if (isAxiosError(error)) {
    const status = error.response?.status
    if (status === 401 || status === 403) {
      return true
    }
    return status == null || error.code === 'ERR_NETWORK' || error.message === 'Network Error'
  }
  return false
}

export function agrarChainErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const status = error.response?.status
    if (status != null) {
      return `Agrar-Kette nicht lesbar (HTTP ${status}).`
    }
    if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      return 'Agrar-Kette nicht lesbar: offline.'
    }
  }
  if (error instanceof Error && error.message.trim()) {
    return error.message
  }
  return 'Agrar-Kette nicht lesbar.'
}

export async function fetchAgrarChain(query: AgrarChainQuery): Promise<AgrarChainHint> {
  const response = await apiClient.get<AgrarChainHint>(AGRAR_CHAIN_PATH, {
    params: agrarChainParams(query),
  })
  const hint = parseAgrarChainHint(response.data ?? response)
  if (!hint) {
    throw new Error('Agrar-Kette: ungueltige Antwort.')
  }
  return hint
}

export async function loadAgrarChainHints(queries: AgrarChainQuery[]): Promise<AgrarChainViewState> {
  const projected = queries.filter(hasChainProjection)
  if (projected.length === 0) {
    return { status: 'empty' }
  }

  const results = await Promise.allSettled(projected.map((query) => fetchAgrarChain(query)))
  const hints: AgrarChainHint[] = []
  const failures: unknown[] = []
  let unavailable = 0
  for (const result of results) {
    if (result.status === 'fulfilled') {
      hints.push(result.value)
      continue
    }
    if (isAgrarChainUnavailable(result.reason)) {
      unavailable += 1
      continue
    }
    failures.push(result.reason)
  }

  if (hints.length === 0 && unavailable === results.length) {
    return { status: 'hidden' }
  }
  if (hints.length === 0 && failures.length > 0) {
    return { status: 'error', message: agrarChainErrorMessage(failures[0]) }
  }
  if (hints.length === 0) {
    return { status: 'empty' }
  }
  return {
    status: 'ready',
    hints,
    warning: failures.length > 0 ? agrarChainErrorMessage(failures[0]) : undefined,
  }
}

function readAbrufRows(payload: unknown): unknown[] {
  if (Array.isArray(payload)) {
    return payload
  }
  if (payload && typeof payload === 'object') {
    const raw = payload as Record<string, unknown>
    if (Array.isArray(raw.data)) {
      return raw.data
    }
    if (Array.isArray(raw.items)) {
      return raw.items
    }
  }
  return []
}

/** Nimmt den weitesten echten Abrufstatus — kein erfundener Lieferstatus. */
export function pickAbrufProjection(
  rows: unknown[],
): Pick<AgrarChainQuery, 'disposition_status' | 'weighing_present'> {
  let best: string | undefined
  let bestRank = -1
  let weighingPresent = false
  for (const row of rows) {
    if (!row || typeof row !== 'object') {
      continue
    }
    const raw = row as Record<string, unknown>
    const status = readString(raw.status).toUpperCase()
    const rank = KON_ABRUF_RANK[status]
    if (rank != null && rank > bestRank) {
      bestRank = rank
      best = status
    }
    if (readString(raw.wiegeschein_id) || readString(raw.wiegeschein_nr)) {
      weighingPresent = true
    }
  }
  const projection: Pick<AgrarChainQuery, 'disposition_status' | 'weighing_present'> = {}
  if (best) {
    projection.disposition_status = best
  }
  if (weighingPresent) {
    projection.weighing_present = true
  }
  return projection
}

function needsAbrufLookup(query: AgrarChainQuery): boolean {
  if (query.source_model !== 'kon') {
    return false
  }
  const status = (query.contract_status ?? '').toUpperCase()
  if (status === 'ERLEDIGT' || status === 'STORNIERT') {
    return false
  }
  return !query.disposition_status
}

async function enrichQueriesWithAbrufe(queries: AgrarChainQuery[]): Promise<AgrarChainViewState | AgrarChainQuery[]> {
  const pending = queries.filter(needsAbrufLookup)
  if (pending.length === 0) {
    return queries
  }

  const byRef = new Map(queries.map((query) => [query.contract_ref, query]))
  const failures: unknown[] = []
  let unavailable = 0
  const results = await Promise.allSettled(
    pending.map(async (query) => {
      const response = await apiClient.get<unknown>(dispositionenPath(query.contract_ref))
      return { ref: query.contract_ref, rows: readAbrufRows(response.data ?? response) }
    }),
  )

  for (const result of results) {
    if (result.status === 'fulfilled') {
      const current = byRef.get(result.value.ref)
      if (current) {
        byRef.set(result.value.ref, { ...current, ...pickAbrufProjection(result.value.rows) })
      }
      continue
    }
    if (isAgrarChainUnavailable(result.reason)) {
      unavailable += 1
      continue
    }
    failures.push(result.reason)
  }

  const keptWithoutLookup = queries.filter((query) => !needsAbrufLookup(query))
  if (unavailable === pending.length && failures.length === 0) {
    if (keptWithoutLookup.length === 0) {
      return { status: 'hidden' }
    }
    return keptWithoutLookup
  }
  if (unavailable + failures.length === pending.length && failures.length > 0 && keptWithoutLookup.length === 0) {
    return { status: 'error', message: agrarChainErrorMessage(failures[0]) }
  }

  return [...byRef.values()]
}

async function readIndexPayload(
  path: string,
  params: Record<string, string | number | boolean>,
): Promise<{ ok: true; payload: unknown } | { ok: false; error: unknown }> {
  try {
    const response = await apiClient.get<unknown>(path, { params })
    return { ok: true, payload: response.data ?? response }
  } catch (error) {
    return { ok: false, error }
  }
}

export async function loadVisibleAgrarChain(): Promise<AgrarChainViewState> {
  const [konResult, agrarResult] = await Promise.all([
    readIndexPayload(OPEN_KONTRAKTE_PATH, OPEN_KONTRAKTE_PARAMS),
    readIndexPayload(AGRAR_CONTRACTS_PATH, AGRAR_CONTRACTS_PARAMS),
  ])

  const failures: unknown[] = []
  let unavailable = 0
  const queries: AgrarChainQuery[] = []

  if (konResult.ok) {
    queries.push(...queriesFromKontraktIndex(konResult.payload))
  } else if (isAgrarChainUnavailable(konResult.error)) {
    unavailable += 1
  } else {
    failures.push(konResult.error)
  }

  if (agrarResult.ok) {
    queries.push(...queriesFromAgrarContractIndex(agrarResult.payload))
  } else if (isAgrarChainUnavailable(agrarResult.error)) {
    unavailable += 1
  } else {
    failures.push(agrarResult.error)
  }

  if (queries.length === 0 && unavailable === 2) {
    return { status: 'hidden' }
  }
  if (queries.length === 0 && failures.length > 0) {
    return { status: 'error', message: agrarChainErrorMessage(failures[0]) }
  }
  if (queries.length === 0) {
    return { status: 'empty' }
  }

  const enriched = await enrichQueriesWithAbrufe(queries)
  if (!Array.isArray(enriched)) {
    return enriched
  }
  const loaded = await loadAgrarChainHints(enriched)
  if (loaded.status === 'ready' && failures.length > 0) {
    return { ...loaded, warning: agrarChainErrorMessage(failures[0]) }
  }
  return loaded
}
