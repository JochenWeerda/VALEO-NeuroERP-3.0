import { Badge, type BadgeVariant } from '@/components/ui/badge'
import type { InboxPrefillPayload } from './types'

const BAND_VARIANT: Record<InboxPrefillPayload['confidenceBand'], BadgeVariant> = {
  high: 'success',
  medium: 'info',
  low: 'warning',
  review: 'error',
}

const BAND_LABEL: Record<InboxPrefillPayload['confidenceBand'], string> = {
  high: 'hoch',
  medium: 'mittel',
  low: 'niedrig',
  review: 'pruefen',
}

function formatConfidence(value: number): string {
  return new Intl.NumberFormat('de-DE', { style: 'percent', maximumFractionDigits: 0 }).format(value)
}

export function InboxPrefillBanner({ payload }: { payload: InboxPrefillPayload }): JSX.Element {
  const partner = payload.partner.name || payload.partner.number || payload.partner.id || 'unbekannt'
  const number = payload.documentNumber || payload.matchValues.invoiceNumber
  const match = payload.match
  const duplicates = payload.duplicates ?? []
  const uncertainties = payload.uncertainties ?? []
  /** Backend: classification_source → prefill.source.classification. Nicht raten. */
  const classification = payload.source.classification?.trim() || null

  return (
    <aside
      data-testid="inbox-prefill-banner"
      className="mb-3 rounded-(--radius) border border-border bg-card px-3 py-2"
      aria-label="Inbox-Vorschlag"
    >
      <p className="text-2xs tracking-wide uppercase text-muted-foreground">Vorschlag aus Beleg-Inbox</p>
      <div className="mt-1 flex flex-wrap items-center gap-2">
        <Badge
          variant={BAND_VARIANT[payload.confidenceBand]}
          data-testid="inbox-prefill-confidence"
        >
          Konfidenz {formatConfidence(payload.confidence)} · {BAND_LABEL[payload.confidenceBand]}
        </Badge>
        {classification ? (
          <p
            className="text-2xs tracking-wide uppercase text-muted-foreground"
            data-testid="inbox-prefill-classification"
          >
            {classification}
          </p>
        ) : null}
        <p className="text-sm">
          Lieferant {partner}
          {number ? ` · ${number}` : ''}
        </p>
      </div>
      {match?.status === 'matched' ? (
        <p className="mt-1 text-xs text-muted-foreground" data-testid="inbox-prefill-match">
          Stamm-Treffer {match.partner_number || match.partner_id}
          {match.matched_by ? ` (${match.matched_by})` : ''}
        </p>
      ) : null}
      {duplicates.length > 0 ? (
        <p className="mt-1 text-xs text-status-warning" data-testid="inbox-prefill-duplicates">
          Dublette: {duplicates.map((row) => row.doc_number).join(', ')}
        </p>
      ) : null}
      {uncertainties.length > 0 ? (
        <ul className="mt-1 list-disc pl-4 text-xs text-status-warning" data-testid="inbox-prefill-uncertainties">
          {uncertainties.map((hint) => (
            <li key={`${hint.code}:${hint.detail}`}>{hint.detail}</li>
          ))}
        </ul>
      ) : null}
      <p className="mt-1 text-xs text-muted-foreground">
        Buchung nur über Speichern in dieser Maske, nicht über die Inbox.
      </p>
    </aside>
  )
}
