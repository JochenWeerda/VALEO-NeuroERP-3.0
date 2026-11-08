import { isAxiosError } from 'axios'
import { apiClient } from '@/lib/api-client'
import { WORKSPACE_FACHAKTIONEN } from './registry'
import type { TypedFachaktion } from './types'

export const FACHAKTION_RESOLVE_TOOL = 'workspace.fachaktion.resolve'
export const FACHAKTION_MCP_CALL_PATH = '/api/v1/mcp/tools/call'

export type FachaktionResolution = {
  action_id: string | null
  authorized: boolean
  reason: string
  four_eyes: boolean
  executable: boolean
  access: string | null
  command_endpoint: string | null
  route_path: string | null
  screen_id: string | null
}

export type FachaktionResolveSource = 'live' | 'local' | 'blocked' | 'unavailable'

export type ConsumedFachaktionResolve = {
  source: FachaktionResolveSource
  action?: TypedFachaktion
  resolution?: FachaktionResolution
}

function readString(value: unknown): string | null {
  return typeof value === 'string' && value.trim().length > 0 ? value : null
}

export function parseFachaktionResolution(payload: unknown): FachaktionResolution | null {
  if (!payload || typeof payload !== 'object') {
    return null
  }
  const raw = payload as Record<string, unknown>
  return {
    action_id: readString(raw.action_id),
    authorized: raw.authorized === true,
    reason: typeof raw.reason === 'string' ? raw.reason : '',
    four_eyes: raw.four_eyes === true,
    executable: raw.executable !== false,
    access: readString(raw.access),
    command_endpoint: readString(raw.command_endpoint),
    route_path: readString(raw.route_path),
    screen_id: readString(raw.screen_id),
  }
}

export function isLiveResolveUnavailable(error: unknown): boolean {
  if (isAxiosError(error)) {
    const status = error.response?.status
    if (status === 401 || status === 403) {
      return true
    }
    if (status == null || error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      return true
    }
  }
  return true
}

/** WRITE/Vier-Augen/executable:false werden im Client nicht ausgefuehrt. */
export function shouldBlockClientExecution(resolution: FachaktionResolution): boolean {
  return (
    resolution.authorized !== true
    || resolution.executable === false
    || resolution.four_eyes === true
    || resolution.access === 'write'
  )
}

/**
 * Spiegel der YAML-Aliase aus config/adaptive_workspace_fachaktionen.yaml.
 * Keine neuen Synonyme — nur der bestehende Katalog.
 */
export const FACHAKTION_CATALOG_ALIASES: Record<string, readonly string[]> = {
  'logistik.undispatched_vehicles.list': [
    'nicht disponierte lkw',
    'nicht disponierte lastwagen',
    'lkw nicht disponiert',
    'undispatched trucks',
    'fahrzeuge ohne tour',
  ],
  'logistik.tour.anlegen': ['tour anlegen', 'lkw disponieren', 'fahrzeug einer tour zuordnen'],
  'agrar.contract.overdue.list': [
    'ueberfaellige kontrakte',
    'ueberfaellige vertraege',
    'kontraktmahnung',
    'overdue contracts',
  ],
  'agrar.contract.reminder.create': ['kontrakt mahnen', 'mahnung kontrakt'],
  'sales.customer_quote.list': [
    'angebot kunde',
    'kundenangebot',
    'verkaufsangebot',
    'angebote kunde',
    'quote customer',
  ],
  'sales.customer_quote.create': ['angebot anlegen', 'neues angebot', 'verkaufsangebot anlegen'],
  'einkauf.goods_receipt.quantity_variance.list': [
    'we mengenabweichung',
    'wareneingang mengenabweichung',
    'mengenabweichung we',
    'quantity variance',
    '3-wege-match abweichung',
  ],
  'einkauf.anlieferavis.wareneingang': ['wareneingang buchen', 'we buchen', 'avis wareneingang'],
  'finance.ap_invoice.approval.worklist': [
    'rechnungen freigabe',
    'rechnungsfreigabe',
    'ap freigabe',
    'eingangsrechnungen freigabe',
  ],
  'finance.ap_invoice.propose': ['rechnungsfreigabe vorschlagen', 'ap freigabe vorschlagen'],
  'finance.ap_invoice.freigeben': [
    'rechnungen freigeben',
    'rechnung freigeben',
    'ap rechnung freigeben',
  ],
  'harvest.intake-queue': [
    'harvest.intake-queue',
    'annahme warteschlange',
    'warteschlange',
    'waage annahme',
    'ernte annahme',
    'hof warteschlange',
    'intake queue',
  ],
  'workspace.document-inbox': [
    'workspace.document-inbox',
    'beleg inbox',
    'beleg-inbox',
    'dokumenteneingang',
    'eingehende belege',
    'document inbox',
  ],
  'document.capture.open': ['document.capture.open', 'document capture open', 'beleg capture'],
  'agrar.qualitaets-handlungsbedarf': [
    'agrar.qualitaets-handlungsbedarf',
    'qualitaets handlungsbedarf',
    'qualitaets-check',
    'qualitaetsprotokoll',
    'handlungsbedarf',
  ],
  'sales.credit_note.list': [
    'sales.credit_note.list',
    'gutschriften verkauf',
    'verkauf gutschriften',
    'credit notes',
    'ausgehende gutschrift',
  ],
  'einkauf.gutschrift.list': [
    'einkauf.gutschrift.list',
    'gutschriften einkauf',
    'einkauf gutschriften',
    'gutschriften belastungen',
    'eingehende gutschrift',
  ],
  'weighing.tickets.list': [
    'weighing.tickets.list',
    'wiegescheine',
    'wiegeschein liste',
    'weighing tickets',
    'waage liste',
  ],
  'einkauf.lieferschein.list': [
    'einkauf.lieferschein.list',
    'lieferscheine einkauf',
    'einkauf lieferscheine',
    'lieferschein erfassung',
    'eingang lieferschein',
  ],
  'einkauf.lieferant.create': [
    'einkauf.lieferant.create',
    'lieferant anlegen',
    'lieferantenstamm',
    'kreditor anlegen',
  ],
  'artikel.stamm.create': [
    'artikel.stamm.create',
    'artikel anlegen',
    'artikelstamm',
    'neuer artikel',
  ],
}

const FILLERS = new Set([
  'zeige',
  'zeig',
  'welche',
  'welcher',
  'welches',
  'liste',
  'list',
  'oeffne',
  'offen',
  'der',
  'die',
  'das',
  'alle',
  'mir',
  'bitte',
  'sind',
  'ist',
  'den',
  'dem',
  'ein',
  'eine',
  'einen',
  'fuer',
  'zum',
  'zur',
  'und',
  'von',
  'im',
  'in',
])

const UMLAUT: Record<string, string> = { ä: 'ae', ö: 'oe', ü: 'ue', ß: 'ss' }

export function aliasesForCatalogId(catalogId: string | undefined): string[] {
  if (!catalogId) {
    return []
  }
  return [...(FACHAKTION_CATALOG_ALIASES[catalogId] ?? [])]
}

/** Gleicher Normalisierer wie app/workspace/fachaktionen.py — kein LLM. */
export function normalizeFachaktionCommand(text: string): string {
  const lowered = (text || '').trim().toLowerCase().replace(/[äöüß]/g, (ch) => UMLAUT[ch] ?? ch)
  const raw = lowered.replace(/[^a-z0-9.]+/g, ' ')
  return raw
    .split(/\s+/)
    .filter((token) => token.length > 0 && !FILLERS.has(token))
    .join(' ')
}

function inflectionVariants(command: string): string[] {
  const variants = [command]
  const alt = command
    .split(' ')
    .map((token) => (token.endsWith('en') && token.length > 8 ? `${token.slice(0, -2)}e` : token))
    .join(' ')
  if (alt !== command) {
    variants.push(alt)
  }
  return variants
}

function phraseHits(command: string, alias: string): boolean {
  if (!alias || !command) {
    return false
  }
  if (command === alias) {
    return true
  }
  const escaped = alias.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return new RegExp(`(?:^|\\s)${escaped}(?:$|\\s)`).test(command)
}

function buildAliasIndex(): Map<string, string> {
  const index = new Map<string, string>()
  for (const [actionId, aliases] of Object.entries(FACHAKTION_CATALOG_ALIASES)) {
    index.set(normalizeFachaktionCommand(actionId), actionId)
    for (const alias of aliases) {
      index.set(normalizeFachaktionCommand(alias), actionId)
    }
  }
  return index
}

const ALIAS_INDEX = buildAliasIndex()

/**
 * YAML-Alias / action_id → catalogId. Unbekannter Text, URLs und SQL bleiben ohne Treffer.
 */
export function resolveCatalogIdFromCommand(command: string): string | null {
  const normalized = normalizeFachaktionCommand(command)
  if (!normalized) {
    return null
  }
  for (const variant of inflectionVariants(normalized)) {
    const exact = ALIAS_INDEX.get(variant)
    if (exact) {
      return exact
    }
  }
  const bestByAction = new Map<string, { length: number; alias: string }>()
  for (const [alias, actionId] of ALIAS_INDEX.entries()) {
    if (!phraseHits(normalized, alias)) {
      continue
    }
    const prev = bestByAction.get(actionId)
    if (!prev || alias.length > prev.length) {
      bestByAction.set(actionId, { length: alias.length, alias })
    }
  }
  if (bestByAction.size === 0) {
    return null
  }
  const ranked = [...bestByAction.entries()]
    .map(([actionId, hit]) => ({ actionId, ...hit }))
    .sort((left, right) => right.length - left.length || left.alias.localeCompare(right.alias) || left.actionId.localeCompare(right.actionId))
  const longest = ranked[0].length
  const tied = ranked.filter((item) => item.length === longest)
  if (tied.length > 1) {
    return null
  }
  return ranked[0].actionId
}

export function findLocalByCatalogId(
  actionId: string | null,
  actions: TypedFachaktion[] = WORKSPACE_FACHAKTIONEN,
): TypedFachaktion | undefined {
  if (!actionId) {
    return undefined
  }
  return actions.find((action) => action.catalogId === actionId)
}

export function localResolveFallback(
  command: string,
  actions: TypedFachaktion[] = WORKSPACE_FACHAKTIONEN,
): TypedFachaktion | undefined {
  const catalogId = resolveCatalogIdFromCommand(command)
  if (catalogId) {
    return findLocalByCatalogId(catalogId, actions)
  }
  const needle = normalizeFachaktionCommand(command)
  if (!needle) {
    return undefined
  }
  return actions.find(
    (action) =>
      normalizeFachaktionCommand(action.catalogId ?? '') === needle
      || normalizeFachaktionCommand(action.id) === needle
      || normalizeFachaktionCommand(action.label) === needle,
  )
}

/**
 * Live-Treffer nur ueber catalogId = YAML action_id. Kein zweiter Katalog,
 * kein POST auf command_endpoint, kein Auto-Submit.
 */
export function consumeResolvedFachaktion(
  live: FachaktionResolution | null | 'unavailable',
  command: string,
  actions: TypedFachaktion[] = WORKSPACE_FACHAKTIONEN,
): ConsumedFachaktionResolve {
  if (live && live !== 'unavailable' && live.action_id) {
    const local = findLocalByCatalogId(live.action_id, actions)
    if (!local) {
      return { source: 'blocked', resolution: live }
    }
    if (shouldBlockClientExecution(live) && local.kind !== 'prepare-command') {
      return { source: 'blocked', action: local, resolution: live }
    }
    return { source: 'live', action: local, resolution: live }
  }

  const fallback = localResolveFallback(command, actions)
  return { source: 'local', action: fallback }
}

export async function resolveFachaktionLive(
  command: string,
): Promise<FachaktionResolution | 'unavailable'> {
  const needle = command.trim()
  if (!needle) {
    return 'unavailable'
  }
  try {
    const response = await apiClient.post<FachaktionResolution>(FACHAKTION_MCP_CALL_PATH, {
      tool_name: FACHAKTION_RESOLVE_TOOL,
      parameters: { command: needle },
      mode: 'dryRun',
    })
    return parseFachaktionResolution(response.data) ?? 'unavailable'
  } catch (error) {
    if (isLiveResolveUnavailable(error)) {
      return 'unavailable'
    }
    return 'unavailable'
  }
}

export async function resolveFachaktionCommand(
  command: string,
  actions: TypedFachaktion[] = WORKSPACE_FACHAKTIONEN,
): Promise<ConsumedFachaktionResolve> {
  const live = await resolveFachaktionLive(command)
  return consumeResolvedFachaktion(live, command, actions)
}
