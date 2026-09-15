import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'

export type SourceProposalContext = {
  party_id: string
  direction: 'incoming' | 'outgoing'
  document_date: string
  warehouse_id?: string
  lines: Array<{
    line_id: string; article_id?: string; article_number?: string
    quantity: number; unit: string; charge?: string; bio?: boolean; contract_reference?: string
  }>
}

type ProposalResult = {
  notice: string
  lines: Array<{
    line_id: string; article_number?: string; unit: string
    groups: Array<{
      kind: 'contract' | 'foreign_stock'; uncovered_quantity: string
      proposals: Array<{
        source_id: string; reference: string; quantity: string; unit: string
        recorded_remaining: string; owner_id?: string; warehouse_id?: string; charge?: string
        reason: string; billing: 'goods' | 'services_only'
      }>
    }>
  }>
}

export function SourceProposalRenderer({ context }: { context: unknown }): JSX.Element | null {
  const requestKey = JSON.stringify(context ?? null)
  const [result, setResult] = useState<{ key: string; value: ProposalResult } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [refresh, setRefresh] = useState(0)
  const input = context as SourceProposalContext | undefined
  const ready = Boolean(input?.party_id && input?.document_date && input.lines?.length)
  useEffect(() => {
    let current = true
    setError(null)
    setResult(null)
    if (!ready) return
    const timer = setTimeout(() => {
      void apiClient.post<ProposalResult>('/api/v1/docflow/source-proposals', JSON.parse(requestKey))
        .then((response) => { if (current) setResult({ key: requestKey, value: response.data }) })
        .catch(() => { if (current) setError('Quellen konnten nicht geprueft werden. Bitte erneut pruefen.') })
    }, 300)
    return () => { current = false; clearTimeout(timer) }
  }, [requestKey, ready, refresh])
  if (!context) return null
  const model = result?.key === requestKey ? result.value : null
  return (
    <section aria-label="Kontrakt- und Fremdlagervorschlaege" className="rounded border p-3 space-y-2 text-sm">
      <div className="flex items-center justify-between gap-2">
        <h2 className="font-semibold">Passende Kontrakte und Fremdlager</h2>
        <Button type="button" variant="outline" size="sm" disabled={!ready} onClick={() => setRefresh((value) => value + 1)}>Erneut pruefen</Button>
      </div>
      {!ready ? <p>Partner, Artikel, Menge und Einheit erfassen.</p> : null}
      {error ? <p role="alert">{error}</p> : null}
      {ready && !model && !error ? <p role="status">Quellen werden geprueft …</p> : null}
      {model ? <>
        <p className="text-muted-foreground">{model.notice}</p>
        {model.lines.map((line) => <div key={line.line_id} className="space-y-2">
          <h3 className="font-medium">Position {line.line_id}{line.article_number ? ` · ${line.article_number}` : ''}</h3>
          {line.groups.map((group) => <div key={group.kind}>
            <h4>{group.kind === 'contract' ? 'Kontraktabruf' : 'Kundeneigene Ware – alternative Eigentumsart'}</h4>
            {group.proposals.length ? <div className="overflow-x-auto"><table className="w-full text-left">
              <thead><tr><th>Quelle</th><th className="text-right">Teilmenge</th><th>Begruendung / Zuordnung</th></tr></thead>
              <tbody>{group.proposals.map((item) => <tr key={item.source_id} className="border-t">
                <td>{item.reference}</td><td className="text-right tabular-nums">{item.quantity} {item.unit}</td>
                <td>{item.reason}{item.owner_id ? ` · Eigentuemer ${item.owner_id}` : ''}{item.warehouse_id ? ` · Lager ${item.warehouse_id}` : ''}{item.charge ? ` · Charge ${item.charge}` : ''}
                  {item.billing === 'services_only' ? ' · Keine Warenrechnung; Leistungen separat' : ''}</td>
              </tr>)}</tbody>
            </table></div> : <p className="text-muted-foreground">Keine nachgewiesene passende Quelle.</p>}
            {Number(group.uncovered_quantity) > 0 ? <p>Nicht gedeckt: {group.uncovered_quantity} {line.unit}</p> : null}
          </div>)}
        </div>)}
      </> : null}
    </section>
  )
}
