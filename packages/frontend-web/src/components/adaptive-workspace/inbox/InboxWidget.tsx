import { useCallback, useEffect, useMemo, useState } from 'react'
import { isAxiosError } from 'axios'
import { AlertCircle } from 'lucide-react'
import { Badge, type BadgeVariant } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import {
  INBOX_OPEN_DOCUMENT_ACTION_LABEL,
  clearInboxPrefill,
  filterInboxQueue,
  inboxOpenDecision,
  primaryInboxAction,
  sortInboxQueue,
} from './inbox-contract'
import {
  articleCreateBlockedReason,
  createArticleFromProposal,
  createLieferantFromProposal,
  enrichArticleImageAfterCreate,
  supplierCreateBlockedReason,
} from './master-data-create'
import type { InboxCommand, InboxQueueItem, InboxQueueResponse, InboxQueueSnapshot, InboxWidgetProps } from './types'

type InboxLoadPhase = 'pending' | 'hidden' | 'error' | 'settled'

const BAND_VARIANT: Record<InboxQueueItem['confidence_band'], BadgeVariant> = {
  high: 'success',
  medium: 'info',
  low: 'warning',
  review: 'error',
}

const BAND_LABEL: Record<InboxQueueItem['confidence_band'], string> = {
  high: 'hoch',
  medium: 'mittel',
  low: 'niedrig',
  review: 'pruefen',
}

const DOCUMENT_KIND_LABEL: Record<string, string> = {
  EINGANGSRECHNUNG: 'Rechnung',
  LIEFERSCHEIN: 'Lieferschein',
  GUTSCHRIFT: 'Gutschrift',
  WIEGESCHEIN: 'Wiegeschein',
}

function formatConfidence(value: number): string {
  return new Intl.NumberFormat('de-DE', { style: 'percent', maximumFractionDigits: 0 }).format(value)
}

export function InboxWidget({
  queue,
  confidenceMin = 0,
  compact = false,
  onOpenMask,
  onPrepare,
  onQueue,
}: InboxWidgetProps): JSX.Element {
  const [loaded, setLoaded] = useState<InboxQueueItem[] | null>(queue ?? null)
  const [gaps, setGaps] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [phase, setPhase] = useState<InboxLoadPhase>(queue !== undefined ? 'settled' : 'pending')
  const [pendingKeys, setPendingKeys] = useState<Set<string>>(new Set())

  const usesExternalQueue = queue !== undefined

  useEffect(() => {
    if (usesExternalQueue) {
      setLoaded(queue ?? [])
      setError(null)
      setPhase('settled')
      return
    }
    let cancelled = false
    void (async () => {
      try {
        const response = await apiClient.get<InboxQueueResponse>('/api/mcp/documents/inbox/queue')
        if (cancelled) return
        setLoaded(response.data.items ?? [])
        setGaps(response.data.gaps ?? [])
        setError(response.data.available === false ? (response.data.message || 'Inbox nicht verfuegbar') : null)
        setPhase('settled')
      } catch (cause) {
        if (cancelled) return
        setError(cause instanceof Error ? cause.message : 'Inbox konnte nicht geladen werden')
        setLoaded([])
        setPhase(isAxiosError(cause) && cause.response?.status === 401 ? 'hidden' : 'error')
      }
    })()
    return () => {
      cancelled = true
    }
  }, [queue, usesExternalQueue])

  const items = useMemo(
    () => sortInboxQueue(filterInboxQueue(loaded ?? [], confidenceMin)),
    [loaded, confidenceMin],
  )

  const snapshot = useMemo<InboxQueueSnapshot>(() => {
    if (phase === 'pending') return { status: 'pending', items: [] }
    if (phase === 'hidden') return { status: 'hidden', items: [] }
    if (phase === 'error') return { status: 'error', items: [] }
    if (items.length === 0) return { status: 'empty', items: [] }
    return { status: 'ready', items }
  }, [items, phase])

  useEffect(() => {
    onQueue?.(snapshot)
  }, [onQueue, snapshot])

  useEffect(() => {
    return () => {
      onQueue?.({ status: 'pending', items: [] })
    }
  }, [onQueue])

  const withPending = useCallback(async (key: string, work: () => Promise<void>) => {
    setPendingKeys((current) => {
      if (current.has(key)) return current
      const next = new Set(current)
      next.add(key)
      return next
    })
    try {
      await work()
    } finally {
      setPendingKeys((current) => {
        const next = new Set(current)
        next.delete(key)
        return next
      })
    }
  }, [])

  const navigateDecision = useCallback((item: InboxQueueItem, href: string) => {
    if (!href) return
    clearInboxPrefill()
    if (onOpenMask) {
      onOpenMask(item)
      return
    }
    window.location.assign(href)
  }, [onOpenMask])

  const openPrimary = useCallback((item: InboxQueueItem) => {
    const decision = inboxOpenDecision(item)
    navigateDecision(item, decision.href)
  }, [navigateDecision])

  const openDocument = useCallback((item: InboxQueueItem) => {
    const decision = inboxOpenDecision(item)
    if (!decision.documentOpenEnabled || !decision.documentOpenHref) return
    navigateDecision(item, decision.documentOpenHref)
  }, [navigateDecision])

  const prepareItem = useCallback(async (item: InboxQueueItem) => {
    const key = `${item.id}:prepare`
    await withPending(key, async () => {
      try {
        const response = await apiClient.post<{ command: InboxCommand }>(
          `/api/mcp/documents/inbox/${encodeURIComponent(item.id)}/prepare`,
          {},
        )
        const command = response.data.command
        if (onPrepare) {
          await onPrepare(item, command)
          return
        }
        setError(command.blockers[0]?.detail ?? command.reason)
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : 'Vorschlag konnte nicht geprueft werden')
      }
    })
  }, [onPrepare, withPending])

  const createSupplier = useCallback(async (item: InboxQueueItem) => {
    const supplier = item.master_data_proposals?.supplier
    if (!supplier || supplier.status !== 'propose') return
    const blocked = supplierCreateBlockedReason(supplier)
    if (blocked) {
      toast({ title: 'Lieferant anlegen nicht moeglich', description: blocked, variant: 'destructive' })
      return
    }
    const name = supplier.payload.firmenname || supplier.payload.lieferantennummer || 'Lieferant'
    const confirmed = window.confirm(
      `Lieferant „${name}“ jetzt ueber POST /api/v1/einkauf/lieferanten anlegen?\n\n`
        + 'Vier-Augen/RBAC des Endpoints gelten. Kein Inbox-Approve, keine Buchung.',
    )
    if (!confirmed) return
    const key = `${item.id}:supplier-create`
    await withPending(key, async () => {
      const result = await createLieferantFromProposal(supplier)
      if (result.ok) {
        toast({
          title: result.alreadyExists ? 'Lieferant bereits vorhanden' : 'Lieferant angelegt',
          description: result.alreadyExists
            ? `${name} — Nummer schon im Stamm (409); kein erneutes Anlegen.`
            : result.id
              ? `${name} (ID ${result.id}) — Stamm pruefen.`
              : `${name} — Stamm pruefen.`,
        })
        return
      }
      toast({ title: 'Lieferant anlegen fehlgeschlagen', description: result.message, variant: 'destructive' })
      setError(result.message)
    })
  }, [withPending])

  const createArticle = useCallback(async (item: InboxQueueItem) => {
    const article = item.master_data_proposals?.articles?.find(
      (row) => row.kind === 'article_create' && row.status === 'propose',
    )
    if (!article) return
    const blocked = articleCreateBlockedReason(article)
    if (blocked) {
      toast({ title: 'Artikel anlegen nicht moeglich', description: blocked, variant: 'destructive' })
      return
    }
    const name = article.payload?.name || article.payload?.article_number || 'Artikel'
    const confirmed = window.confirm(
      `Artikel „${name}“ jetzt ueber POST /api/v1/articles/ anlegen?\n\n`
        + 'Defaults: Einheit t (oder unit_hint), Kategorie Sonstige, VK 0 — aus Artikelstamm.\n'
        + 'Danach optional Bild via fetch-image. Kein Inbox-Approve, keine Buchung.',
    )
    if (!confirmed) return
    const key = `${item.id}:article-create`
    await withPending(key, async () => {
      const result = await createArticleFromProposal(article)
      if (!result.ok) {
        toast({ title: 'Artikel anlegen fehlgeschlagen', description: result.message, variant: 'destructive' })
        setError(result.message)
        return
      }
      toast({
        title: 'Artikel angelegt',
        description: result.id
          ? `${name} (ID ${result.id}) — Stamm pruefen.`
          : `${name} — Stamm pruefen.`,
      })
      if (!result.id || article.image_research?.status !== 'propose') return
      const enrich = await enrichArticleImageAfterCreate(result.id, article)
      if (enrich.ok) {
        toast({
          title: 'Bild-Anreicherung',
          description: enrich.image_url
            ? 'Bild gesetzt (category / OFF / Wikipedia).'
            : 'Kein Bild gefunden — Slot bleibt leer.',
        })
        return
      }
      toast({
        title: 'Bild-Anreicherung fehlgeschlagen',
        description: enrich.message,
        variant: 'destructive',
      })
    })
  }, [withPending])

  return (
    <section
      data-testid="adaptive-workspace-inbox"
      className={compact ? 'flex flex-col gap-2' : 'flex flex-col gap-3'}
      aria-label="Beleg-Inbox"
    >
      <header className="flex items-baseline justify-between gap-3">
        <h2 className="text-sm font-semibold tracking-tight">Beleg-Inbox</h2>
        <p className="text-2xs tracking-wide uppercase text-muted-foreground">
          {items.length} offen · keine Buchung
        </p>
      </header>

      {error ? (
        <p className="flex items-start gap-2 text-sm text-status-error" role="alert">
          <AlertCircle className="mt-0.5 h-4 w-4" aria-hidden="true" />
          {error}
        </p>
      ) : null}

      {loaded === null ? (
        <p className="text-sm text-muted-foreground">Inbox wird geladen…</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-muted-foreground">Kein Eingang in der Queue.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b text-left text-2xs tracking-wide uppercase text-muted-foreground">
                <th className="py-2 pr-3 font-medium">Vorschlag</th>
                <th className="py-2 pr-3 font-medium">Konfidenz</th>
                {!compact ? <th className="py-2 pr-3 font-medium">Quelle</th> : null}
                <th className="py-2 pr-3 font-medium">Partner</th>
                {!compact ? <th className="py-2 pr-3 font-medium">Hinweise</th> : null}
                <th className="py-2 font-medium">Aktion</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => {
                const pendingPrepare = pendingKeys.has(`${item.id}:prepare`)
                const pendingSupplier = pendingKeys.has(`${item.id}:supplier-create`)
                const pendingArticle = pendingKeys.has(`${item.id}:article-create`)
                const pending = pendingPrepare || pendingSupplier || pendingArticle
                const primary = primaryInboxAction(item)
                const decision = inboxOpenDecision(item)
                const canOpen = decision.href !== '' && primary?.enabled !== false
                const href = canOpen ? decision.href : undefined
                const openReason = canOpen ? null : decision.reason
                const showDocumentOpenAside = decision.mode === 'overview'
                const partnerLabel =
                  item.match?.status === 'matched'
                    ? (item.match.name || item.match.partner_number || item.match.partner_id)
                    : (item.match_values.supplierName || item.match_values.supplierId || '—')
                const hintParts: string[] = []
                if (item.duplicates.length > 0) {
                  hintParts.push(`Dublette ${item.duplicates.map((row) => row.doc_number).join(', ')}`)
                }
                if (item.match?.status === 'ambiguous') {
                  hintParts.push('Partner mehrdeutig')
                }
                if (item.contract_match?.status === 'matched') {
                  hintParts.push(
                    `Kontrakt ${item.contract_match.contract_number || item.contract_match.contract_id || 'Treffer'}`,
                  )
                } else if (item.contract_match?.status === 'ambiguous') {
                  hintParts.push('Kontrakt mehrdeutig')
                }
                if (item.linked_document_id) {
                  hintParts.push(`Beleg-ID ${item.linked_document_id}`)
                }
                for (const hint of item.uncertainties ?? []) {
                  if (hint.code === 'dublette') continue
                  if (hint.code.startsWith('kontrakt_') && item.contract_match?.status === 'matched') {
                    continue
                  }
                  hintParts.push(hint.detail)
                }
                const md = item.master_data_proposals
                const supplierPropose = md?.supplier?.status === 'propose' ? md.supplier : null
                const supplierBlocked = supplierPropose
                  ? supplierCreateBlockedReason(supplierPropose)
                  : null
                if (supplierPropose) {
                  hintParts.push(`Lieferant-Vorschlag: ${supplierPropose.payload.firmenname || '—'}`)
                }
                const articlePropose = md?.articles?.find(
                  (row) => row.kind === 'article_create' && row.status === 'propose',
                )
                const articleBlockedReason = articlePropose
                  ? articleCreateBlockedReason(articlePropose)
                  : null
                if (articlePropose?.payload?.name) {
                  hintParts.push(`Artikel-Vorschlag: ${articlePropose.payload.name}`)
                }
                const articleBlocked = md?.articles?.find(
                  (row) => row.kind === 'article_create' && row.status === 'blocked',
                )
                if (articleBlocked?.detail) {
                  hintParts.push(articleBlocked.detail)
                }
                return (
                  <tr key={item.id} className="border-b align-top" data-testid={`inbox-row-${item.id}`}>
                    <td className="py-2 pr-3">
                      <p className="font-medium">{item.proposal.label}</p>
                      {item.proposal.document_kind ? (
                        <p
                          className="text-2xs tracking-wide uppercase text-muted-foreground"
                          data-testid={`inbox-kind-${item.id}`}
                        >
                          {DOCUMENT_KIND_LABEL[item.proposal.document_kind] ?? item.proposal.document_kind}
                        </p>
                      ) : null}
                      {item.blockers.length > 0 ? (
                        <p className="text-xs text-status-warning">{item.blockers[0]?.detail}</p>
                      ) : null}
                    </td>
                    <td className="py-2 pr-3">
                      {/* confidence = Backend blend_confidence; source = classification_source */}
                      <Badge
                        variant={BAND_VARIANT[item.confidence_band]}
                        data-testid={`inbox-confidence-${item.id}`}
                      >
                        {formatConfidence(item.confidence)} · {BAND_LABEL[item.confidence_band]}
                      </Badge>
                      {compact ? (
                        <p
                          className="mt-0.5 text-2xs tracking-wide uppercase text-muted-foreground"
                          data-testid={`inbox-source-${item.id}`}
                        >
                          {item.source}
                        </p>
                      ) : null}
                    </td>
                    {!compact ? (
                      <td className="py-2 pr-3 text-muted-foreground" data-testid={`inbox-source-${item.id}`}>
                        {item.source}
                      </td>
                    ) : null}
                    <td className="py-2 pr-3" data-testid={`inbox-partner-${item.id}`}>
                      {partnerLabel}
                      {item.match?.status === 'matched' ? (
                        <span className="mt-0.5 block text-2xs tracking-wide uppercase text-muted-foreground">
                          Stamm {item.match.matched_by || 'treffer'}
                        </span>
                      ) : null}
                      {item.contract_match?.status === 'matched' ? (
                        <span
                          className="mt-0.5 block text-2xs tracking-wide uppercase text-muted-foreground"
                          data-testid={`inbox-contract-${item.id}`}
                        >
                          Kontrakt {item.contract_match.contract_number || item.contract_match.contract_id}
                          {item.contract_match.source ? ` · ${item.contract_match.source}` : ''}
                        </span>
                      ) : null}
                    </td>
                    {!compact ? (
                      <td className="py-2 pr-3 text-xs text-status-warning" data-testid={`inbox-hints-${item.id}`}>
                        {hintParts.length > 0 ? hintParts.join(' · ') : '—'}
                      </td>
                    ) : null}
                    <td className="py-2">
                      <div className="flex flex-wrap gap-2">
                        <Button
                          type="button"
                          size="sm"
                          disabled={pending || !canOpen}
                          onClick={() => openPrimary(item)}
                          data-testid={`inbox-primary-open-${item.id}`}
                        >
                          {/* Gate Übersicht-vs-Beleg: immer decision.actionLabel, nie Backend-ASCII. */}
                          {decision.actionLabel}
                        </Button>
                        {showDocumentOpenAside ? (
                          <Button
                            type="button"
                            size="sm"
                            variant="outline"
                            disabled={pending || !decision.documentOpenEnabled}
                            onClick={() => openDocument(item)}
                            data-testid={`inbox-document-open-${item.id}`}
                          >
                            {INBOX_OPEN_DOCUMENT_ACTION_LABEL}
                          </Button>
                        ) : null}
                        {href ? (
                          <a className="sr-only" href={href}>
                            {decision.mode === 'overview' ? `Zur Übersicht ${item.id}` : `Zur Belegmaske ${item.id}`}
                          </a>
                        ) : null}
                        {decision.documentOpenEnabled && decision.documentOpenHref ? (
                          <a className="sr-only" href={decision.documentOpenHref}>
                            Zum Beleg {item.id}
                          </a>
                        ) : null}
                        <Button
                          type="button"
                          size="sm"
                          variant="outline"
                          disabled={pending}
                          onClick={() => {
                            void prepareItem(item)
                          }}
                        >
                          {pendingPrepare ? 'Prueft…' : 'Vorschlag'}
                        </Button>
                        {supplierPropose ? (
                          <Button
                            type="button"
                            size="sm"
                            variant="outline"
                            disabled={pending || Boolean(supplierBlocked)}
                            title={supplierBlocked ?? undefined}
                            onClick={() => {
                              void createSupplier(item)
                            }}
                            data-testid={`inbox-supplier-create-${item.id}`}
                          >
                            {pendingSupplier ? 'Legt an…' : 'Lieferant anlegen'}
                          </Button>
                        ) : null}
                        {articlePropose ? (
                          <Button
                            type="button"
                            size="sm"
                            variant="outline"
                            disabled={pending || Boolean(articleBlockedReason)}
                            title={articleBlockedReason ?? undefined}
                            onClick={() => {
                              void createArticle(item)
                            }}
                            data-testid={`inbox-article-create-${item.id}`}
                          >
                            {pendingArticle ? 'Legt an…' : 'Artikel anlegen'}
                          </Button>
                        ) : null}
                      </div>
                      {openReason ? (
                        <p
                          className="mt-1 max-w-xs text-xs text-muted-foreground"
                          data-testid={`inbox-open-reason-${item.id}`}
                        >
                          {openReason}
                        </p>
                      ) : null}
                      {showDocumentOpenAside && decision.documentOpenReason ? (
                        <p
                          className="mt-1 max-w-xs text-xs text-muted-foreground"
                          data-testid={`inbox-document-open-reason-${item.id}`}
                        >
                          {decision.documentOpenReason}
                        </p>
                      ) : null}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {gaps.length > 0 && !compact ? (
        <p className="text-2xs tracking-wide uppercase text-muted-foreground">
          Offene Pipeline-Luecken: {gaps.join(', ')}
        </p>
      ) : null}
    </section>
  )
}
