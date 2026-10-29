/**
 * Adaptive Workspace — Vertraege fuer Module, Views, typisierte Fachaktionen
 * und User-Context. Keine direkten API/DB-Calls; Rechte bleiben serverseitig.
 */

export type WorkspaceLayer = 'personal' | 'situational' | 'proactive' | 'dialog'

export type FachaktionKind = 'navigate' | 'open-worklist' | 'prepare-command'

export type SignalKind =
  | 'season'
  | 'time-of-day'
  | 'incident'
  | 'open-task'
  | 'bottleneck'
  | 'risk'
  | 'deadline'

export type SignalSeverity = 1 | 2 | 3 | 4 | 5

export type SeasonId = 'harvest' | 'planting' | 'off-season'

export type DayPart = 'morning' | 'midday' | 'afternoon' | 'evening'

/** Studio-Metadaten-IDs. Renderer liegen in Phase 2 (Geschwister-Slices). */
export const SPECIALIST_COMPONENT_IDS = {
  documentInbox: 'workspace.specialist.document-inbox',
  dispoBoard: 'workspace.specialist.dispo-board',
  gantt: 'workspace.specialist.gantt',
  map: 'workspace.specialist.map',
} as const

export type SpecialistComponentId =
  (typeof SPECIALIST_COMPONENT_IDS)[keyof typeof SPECIALIST_COMPONENT_IDS]

export type WorkspaceModule = {
  id: string
  label: string
  domain: string
  viewIds: string[]
}

export type WorkspaceView = {
  id: string
  moduleId: string
  label: string
  route: string
  specialistComponentId?: SpecialistComponentId
  /** Studio-Kind, nur gelesen: `inbox` | `disposition_board`. */
  specializedKind?: 'inbox' | 'disposition_board'
  /** Geschwister-Registry-ID, z. B. `lkw-disposition-board`. */
  specializedId?: string
}

export type FachaktionTarget = {
  route: string
  screenId?: string
  actionKey?: string
  worklistQuery?: Record<string, string>
}

export type TypedFachaktion = {
  id: string
  label: string
  kind: FachaktionKind
  layer: WorkspaceLayer
  keywords: string[]
  requiredScopes: string[]
  businessDomain: string
  target: FachaktionTarget
  mcpIntent: string
  reasonTemplate: string
  /** Abgleich mit config/adaptive_workspace_fachaktionen.yaml (Geschwister-Katalog). */
  catalogId?: string
  /** Launchpad-Kachel, die diese Aktion in Spaces/Pages hebt. */
  launchpadTileId?: string
}

export type UserContext = {
  roles: string[]
  scopes: string[]
  favorites: string[]
  pinned: string[]
  surfaceLocked: boolean
  locale: string
}

export type WorkspaceSignal = {
  id: string
  kind: SignalKind
  layer: 'situational' | 'proactive'
  relatedActionIds: string[]
  severity: SignalSeverity
  source: string
  dueAt?: string
  count?: number
  season?: SeasonId
  dayPart?: DayPart
  /** Schon berechnete Pruefcodes; rankWorkspaceItems haengt sie an die Rangzeile. */
  reasonCodes?: readonly string[]
}

export type RankedWorkItem = {
  action: TypedFachaktion
  score: number
  reasonCodes: string[]
}

export type RankingAdvisor = (items: RankedWorkItem[]) => RankedWorkItem[]

export type CommandCenterEntry = {
  id: string
  label: string
  keywords: string[]
  category: string
  actionId: string
  actionParams: Record<string, unknown>
  hint?: string
  mcp: {
    intent: string
    businessDomain: string
    requiredScopes?: string[]
  }
}

export type WorkspaceCatalog = {
  modules: WorkspaceModule[]
  views: WorkspaceView[]
  actions: TypedFachaktion[]
}
