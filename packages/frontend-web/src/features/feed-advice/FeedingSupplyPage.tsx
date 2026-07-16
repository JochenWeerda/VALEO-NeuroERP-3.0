import { useState } from 'react'
import { ExternalLink } from 'lucide-react'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { createProcurementHandoff, type FeedingSupplyProjection } from '@/lib/api/feeding-supply'
import { useScreenDefinition } from '@/lib/api/masks'

export function FeedingSupplyPage(): JSX.Element {
  const schemaQuery = useScreenDefinition('agrar/feed-readiness')
  const runtime = useUniversalMaskRuntime({
    screenId: 'agrar/feed-readiness', schema: schemaQuery.data,
    enabled: schemaQuery.data?.adapter?.temporary === false,
    permissions: ['futtermittel.rations.update'],
  })
  const [selected, setSelected] = useState<FeedingSupplyProjection | null>(null)
  const [reason, setReason] = useState('')
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [handoffCreated, setHandoffCreated] = useState(false)

  function handleAction(actionKey: string, payload: Record<string, unknown>): void {
    if (actionKey === 'open_inventory') {
      window.location.assign('/futtermittel/einzelfuttermittel-liste')
      return
    }
    if (actionKey !== 'create_handoff') return
    const row = payload as unknown as FeedingSupplyProjection
    if (!row.plan_version_id) {
      setFeedback('Bitte die Aktion in der Zeile der konkreten Unterdeckung auswaehlen.')
    } else if (row.stock_kg == null) {
      setFeedback('Der Bestand ist unbekannt. Erst nach Bestandsklaerung kann eine Einkaufsmenge vorgeschlagen werden.')
    } else if (!row.shortage_kg || row.shortage_kg <= 0) {
      setFeedback('Fuer dieses Futtermittel besteht im gewaehlten Horizont keine Unterdeckung.')
    } else if (row.suggested_order_kg == null) {
      setFeedback('Die Handelseinheit ist nicht eindeutig. Bitte zuerst die Produktverpackung pflegen.')
    } else {
      setSelected(row); setReason(''); setHandoffCreated(false); setFeedback(null)
    }
  }

  async function submit(): Promise<void> {
    if (!selected) return
    setSaving(true); setFeedback(null)
    try {
      await createProcurementHandoff(selected, reason.trim())
      setSelected(null); setReason(''); setHandoffCreated(true)
      setFeedback('Bedarfsvorschlag wurde revisionssicher an den Einkauf uebergeben. Es wurde keine Bestellung erzeugt.')
      await runtime.refetch()
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  if (schemaQuery.error || runtime.entityError) return <p className="p-4" role="alert">{getAxiosErrorMessage(schemaQuery.error ?? runtime.entityError)}</p>
  if (!runtime.plan) return <p className="p-4 text-sm text-muted-foreground">Versorgungsplanung wird geladen...</p>

  return <div data-testid="feeding-supply-page" data-runtime="native">
    {feedback ? <div className="mx-4 mt-3 flex flex-wrap items-center gap-3 rounded-md border bg-muted px-3 py-2 text-sm" role="status">
      <span>{feedback}</span>
      {handoffCreated ? <a className="inline-flex items-center gap-1 font-medium text-primary hover:underline" href="/einkauf/bestellvorschlaege">Bestellvorschlaege oeffnen <ExternalLink className="h-4 w-4" /></a> : null}
    </div> : null}
    <UniversalMaskRenderer
      plan={runtime.plan} data={runtime.entityData} tables={runtime.tableRows}
      tableQueryStates={runtime.tableQueryStates} tableTotals={runtime.tableTotals}
      onTableQueryChange={runtime.setTableQuery} lookupBindings={runtime.lookupBindings}
      overlay={runtime.userOverlay} onOverlayChange={runtime.updateUserOverlay} onOverlayReset={runtime.resetUserOverlay}
      onAction={handleAction}
    />
    <Dialog open={selected !== null} onOpenChange={(open) => { if (!open) setSelected(null) }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Unterdeckung an Einkauf uebergeben</DialogTitle>
          <DialogDescription>Der Handoff legt einen auditierbaren Bedarfsvorschlag an. Eine Bestellung entsteht erst im Einkaufsprozess.</DialogDescription>
        </DialogHeader>
        {selected ? <div className="grid gap-4 py-2">
          <dl className="grid grid-cols-2 gap-2 rounded-md bg-muted p-3 text-sm">
            <dt>Tiergruppe</dt><dd className="font-medium">{selected.group_name}</dd>
            <dt>Futtermittel</dt><dd className="font-medium">{selected.feed_name}</dd>
            <dt>Unterdeckung</dt><dd>{Number(selected.shortage_kg).toLocaleString('de-DE')} kg</dd>
            <dt>Gerundeter Vorschlag</dt><dd>{Number(selected.suggested_order_kg).toLocaleString('de-DE')} kg</dd>
            <dt>Rundungsaufschlag</dt><dd>{Number(selected.order_rounding_delta_kg).toLocaleString('de-DE')} kg</dd>
          </dl>
          <div className="grid gap-2"><Label htmlFor="handoff-reason">Begruendung</Label><Input id="handoff-reason" value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Warum soll der Einkauf diesen Bedarf pruefen?" /></div>
        </div> : null}
        <DialogFooter><Button variant="outline" onClick={() => setSelected(null)}>Abbrechen</Button><Button disabled={saving || reason.trim().length < 10} onClick={() => { void submit() }}>{saving ? 'Uebergibt...' : 'Bedarf uebergeben'}</Button></DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
}
