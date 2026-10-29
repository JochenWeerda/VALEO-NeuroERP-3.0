export type InboxConfidenceBand = 'high' | 'medium' | 'low' | 'review'

export type InboxActionKind = 'primary' | 'secondary'

export const INBOX_PREFILL_STORAGE_KEY = 'valeo.inbox.prefill'
export const INBOX_PREFILL_SCHEMA = 'valeo.inbox.prefill.v1'

export type InboxAction = {
  key: 'open_mask' | 'prepare' | string
  label: string
  kind: InboxActionKind
  href?: string | null
  enabled?: boolean
  booking: false
  command?: string
}

export type InboxProposal = {
  policy_id: string
  label: string
  document_type: string
  document_kind?: string | null
  /** Fehlt oder unklar → GUTSCHRIFT öffnet keine Übersicht (kein Raten). */
  direction?: 'incoming' | 'outgoing' | null
  target_route: string
  belegart?: string | null
  can_open?: boolean
  reason: string
}

export type InboxPrefillPartner = {
  id?: string | null
  number?: string | null
  name?: string | null
  role: string
}

export type InboxPrefillAmounts = {
  total?: string | null
  tax?: string | null
  currency: string
}

export type InboxPrefillSource = {
  kind: string
  id: string
  dmsDocumentId?: number | null
  classification?: string | null
}

export type InboxHint = {
  code: string
  detail: string
}

export type InboxPartnerMatch = {
  kind: 'business_partner'
  status: 'matched' | 'ambiguous'
  matched_by?: string | null
  partner_id?: string | null
  partner_number?: string | null
  name?: string | null
  candidates?: Array<{
    partner_id?: string | null
    partner_number?: string | null
    name?: string | null
  }>
}

export type InboxContractMatch = {
  kind: 'contract'
  status: 'matched' | 'ambiguous'
  matched_by?: string | null
  source?: string | null
  contract_id?: string | null
  contract_number?: string | null
  candidates?: Array<{
    contract_id?: string | null
    contract_number?: string | null
    source?: string | null
  }>
}

export type InboxDuplicateHint = {
  /** Verifizierte documents.id — nur wenn Backend sie aus dem Join liefert. */
  id?: string | null
  doc_type: string
  doc_number: string
}

/** Stammdaten-Vorschlag aus Extrakt — nie booking/executable aus der Inbox. */
export type InboxMasterDataProposal = {
  booking: false
  executable: false
  line_item_count: number
  supplier?: {
    kind: 'supplier_create'
    status: 'propose'
    booking: false
    executable: false
    domain_api: string
    target_route: string
    fachaktion_catalog_id?: string
    reason: string
    payload: Record<string, string | null | undefined>
    gaps?: string[]
  } | null
  articles: Array<{
    kind: 'article_create' | 'article_match'
    status: 'propose' | 'matched' | 'blocked'
    booking: false
    executable: false
    code?: string
    detail?: string
    domain_api?: string
    target_route?: string
    payload?: Record<string, string | null | undefined>
    image_research?: {
      status: 'propose' | 'gap'
      executed: false
      booking: false
      service: string
      api: string
      reason: string
      code?: string
    }
    gaps?: string[]
  }>
}

export type InboxPrefillPayload = {
  schema: typeof INBOX_PREFILL_SCHEMA
  documentId: string
  documentNumber?: string | null
  partner: InboxPrefillPartner
  amounts: InboxPrefillAmounts
  source: InboxPrefillSource
  confidence: number
  confidenceBand: InboxConfidenceBand
  policyId: string
  documentType: string
  targetRoute: string
  booking: false
  matchValues: Record<string, string>
  match?: InboxPartnerMatch | null
  contractMatch?: InboxContractMatch | null
  duplicates?: InboxDuplicateHint[]
  uncertainties?: InboxHint[]
  storageKey: typeof INBOX_PREFILL_STORAGE_KEY
  /** Create-Host mappt Kopffelder aus dem Prefill; Booking bleibt false. */
  maskConsumesPrefill: true
}

export type InboxCommand = {
  command: string
  executable: false
  booking: false
  reason: string
  policy_id: string
  document_type: string
  target_route: string
  prefill: InboxPrefillPayload
  confidence: number
  confidence_band: InboxConfidenceBand
  blockers: Array<{ code: string; detail: string }>
  match?: InboxPartnerMatch | null
  contract_match?: InboxContractMatch | null
  duplicates?: InboxDuplicateHint[]
  uncertainties?: InboxHint[]
  can_open?: boolean
  source: InboxPrefillSource
  gaps: string[]
  master_data_proposals?: InboxMasterDataProposal
}

export type InboxQueueItem = {
  id: string
  dms_document_id?: number | null
  dms_url?: string | null
  /**
   * Verifizierte ERP-Beleg-ID (Gutschrift/Wiegeschein), nur wenn Backend sie setzt.
   * Nie aus Inbox-ID, DMS-ID oder Belegnummer raten.
   */
  linked_document_id?: string | null
  status: string
  created_at?: string | null
  ocr_excerpt?: string | null
  parsed_fields: Record<string, unknown>
  match_values: Record<string, string>
  match?: InboxPartnerMatch | null
  contract_match?: InboxContractMatch | null
  confidence: number
  confidence_band: InboxConfidenceBand
  source: string
  proposal: InboxProposal
  duplicates: InboxDuplicateHint[]
  uncertainties?: InboxHint[]
  blockers: Array<{ code: string; detail: string }>
  /** Lieferant/Artikel-Vorschlaege; Anlegen nur ueber Domänen-API/Maske. */
  master_data_proposals?: InboxMasterDataProposal
  actions: InboxAction[]
  command: InboxCommand
  can_open?: boolean
  booking_allowed: false
}

export type InboxQueueResponse = {
  ok: boolean
  source: string
  available: boolean
  booking_allowed: false
  count: number
  items: InboxQueueItem[]
  gaps: string[]
  message?: string | null
}

/** Sicht der schon geladenen Queue fuer die Rangliste. 401 ist `hidden`. */
export type InboxQueueSnapshot = {
  status: 'pending' | 'hidden' | 'empty' | 'ready' | 'error'
  items: InboxQueueItem[]
}

export type InboxWidgetProps = {
  queue?: InboxQueueItem[]
  confidenceMin?: number
  compact?: boolean
  onOpenMask?: (_item: InboxQueueItem) => void
  onPrepare?: (_item: InboxQueueItem, _command: InboxCommand) => void | Promise<void>
  /** Dieselbe gefilterte Queue, die das Widget zeigt. Kein zweiter GET. */
  onQueue?: (_snapshot: InboxQueueSnapshot) => void
}
