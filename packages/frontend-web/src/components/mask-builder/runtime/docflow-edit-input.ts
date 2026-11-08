import type { ScreenActionDefinition } from '../schema'

const LINE_FIELDS = ['article_number', 'description', 'quantity', 'unit', 'unit_price',
  'discount_percent', 'tax_code', 'tax_rate', 'expense_account', 'batch_id', 'charge']

export function isDocflowEdit(action?: ScreenActionDefinition): boolean {
  return action?.commandBinding?.adapter === 'docflow.v1' && action.commandBinding.command === 'update'
}

/** Full canonical DTO only; never seed a replacement command from a paginated tab. */
export function docflowEditInput(action: ScreenActionDefinition, response: unknown,
  entityId: string, version: number | undefined, docType: unknown): Record<string, unknown> {
  const document = response as Record<string, unknown> | null
  if (!isDocflowEdit(action) || action.method !== 'PUT' || action.commandEndpoint !== '/api/v1/docflow/{entity_id}' ||
    !Number.isInteger(version) || document?.id !== entityId || document.version !== version ||
    document.doc_type !== docType || document.status !== 'draft' || !Array.isArray(document.items)) {
    throw new Error('Belegkontext ist unvollstaendig oder veraltet. Bitte neu laden.')
  }
  if (document.items.some(item => !item || typeof item !== 'object' || Array.isArray(item) ||
    (item as Record<string, unknown>).source_line_id)) {
    throw new Error('Verknuepfte Positionen benoetigen eine fachliche Korrektur statt Vollersatz.')
  }
  return {
    currency: document.currency,
    document_date: typeof document.document_date === 'string' ? document.document_date.slice(0, 10) : undefined,
    source_ref: document.source_ref ?? '',
    items: document.items.map(item => Object.fromEntries(LINE_FIELDS.filter(key =>
      Object.prototype.hasOwnProperty.call(item, key)).map(key => [key, (item as Record<string, unknown>)[key]]))),
  }
}
