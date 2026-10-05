import { apiClient } from '@/lib/api-client'

export type MaskClass = 'A' | 'B' | 'C'

export interface MaskRegistryEntry {
  mask_id: string
  route: string
  label: string
  domain: string
  mask_class: MaskClass
  process_key?: string | null
  explainability: string
  requires_approval_ui: boolean
  gobd_relevant: boolean
  wave1_contract: boolean
  notes?: string | null
  schema_version: number
}

export interface MaskRegistryResponse {
  masks: MaskRegistryEntry[]
  schema_version: number
}

export async function fetchMaskRegistry(): Promise<MaskRegistryResponse> {
  const response = await apiClient.get<MaskRegistryResponse>('/api/v1/ui/mask-registry')
  return response.data
}

// ── Omnibox-Katalog (UIX-060) ────────────────────────────────────────────────
// Matching-Basis fuer den Intent-Compiler: kuratierte Synonyme, Beispiel-Prompts,
// filterbare Felder und die reale Listen-Route je ScreenDefinition.

export interface OmniboxFilterField {
  key: string
  label: string
  type: 'enum' | 'date' | 'number' | 'text'
}

/** Draftbare Command-Aktion je Maske (UIX-070). */
export interface OmniboxAction {
  key: string
  label: string
  dangerLevel: 'safe' | 'moderate' | 'high' | 'critical'
  requiresConfirmation: boolean
  forbiddenForAgents: boolean
  verbs: string[]
  fields: { key: string; type: string; required: boolean }[]
}

export interface OmniboxCatalogEntry {
  screen_id: string
  title: string
  domain: string
  floorplan: string
  /** Kuratierte Frontend-Listen-Route (leer, wenn ungebunden). */
  route: string
  synonyms: string[]
  example_prompts: string[]
  filterable_fields: OmniboxFilterField[]
  /** Draftbare Aktionen fuer den NL-Command-Pfad (UIX-070). */
  actions?: OmniboxAction[]
}

export async function fetchOmniboxCatalog(): Promise<OmniboxCatalogEntry[]> {
  const response = await apiClient.get<OmniboxCatalogEntry[]>(
    '/api/v1/ui/mask-registry/omnibox-catalog',
  )
  return response.data
}

// ── Omnibox-Telemetrie (UIX-060) ─────────────────────────────────────────────
// Datenschutzfreundliches Signal: nur SHA-256 des normalisierten Eingabetexts,
// nie Klartext. Basis fuer M2-Tuning (Synonyme/Schwellwerte).

export interface OmniboxTelemetrySignal {
  intent_hash: string
  matched_screen_id: string | null
  confidence: number
  accepted: boolean
}

/** SHA-256-Hex ueber Web Crypto; null wenn nicht verfuegbar (Nicht-HTTPS-Kontext). */
export async function sha256Hex(text: string): Promise<string | null> {
  const subtle = globalThis.crypto?.subtle
  if (!subtle) return null
  const bytes = new TextEncoder().encode(text)
  const digest = await subtle.digest('SHA-256', bytes)
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
}

export async function recordOmniboxSignal(signal: OmniboxTelemetrySignal): Promise<void> {
  await apiClient.post('/api/v1/ux-telemetry/omnibox', signal)
}

// ── Rollen-Workspaces (UIX-061) ──────────────────────────────────────────────

export interface WorkspaceStartpage {
  role: string | null
  screenId: string | null
  route: string | null
}

export async function fetchWorkspaceStartpage(role: string): Promise<WorkspaceStartpage> {
  const response = await apiClient.get<WorkspaceStartpage>(
    `/api/v1/ui/mask-registry/workspace-startpage?role=${encodeURIComponent(role)}`,
  )
  return response.data
}
