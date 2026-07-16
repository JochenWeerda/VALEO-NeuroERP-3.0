import { useEffect, useState } from 'react'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useScreenDefinition } from '@/lib/api/masks'
import {
  applyRationTemplate,
  createRationTemplate,
  fetchBusinessRations,
  fetchRationTemplates,
  type BusinessRationSummary,
  type RationTemplate,
} from '@/lib/api/feeding-ration-templates'

type DialogMode = 'create' | 'apply' | null

export function FeedingBusinessDetail({ businessId }: { businessId: string }): JSX.Element {
  const schemaQuery = useScreenDefinition('agrar/feeding-business', { enabled: Boolean(businessId) })
  const runtime = useUniversalMaskRuntime({
    screenId: 'agrar/feeding-business', entityId: businessId, schema: schemaQuery.data,
    enabled: Boolean(businessId) && schemaQuery.data?.adapter?.temporary === false,
  })
  const [mode, setMode] = useState<DialogMode>(null)
  const [rations, setRations] = useState<BusinessRationSummary[]>([])
  const [templates, setTemplates] = useState<RationTemplate[]>([])
  const [sourceVersionId, setSourceVersionId] = useState('')
  const [templateId, setTemplateId] = useState('')
  const [targetRationId, setTargetRationId] = useState('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [reason, setReason] = useState('')
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)

  async function loadChoices(): Promise<void> {
    const [rationRows, templateRows] = await Promise.all([
      fetchBusinessRations(businessId), fetchRationTemplates(businessId),
    ])
    setRations(rationRows)
    setTemplates(templateRows)
    setSourceVersionId((current) => current || rationRows[0]?.version_id || '')
    setTargetRationId((current) => current || rationRows[0]?.id || '')
    setTemplateId((current) => current || templateRows[0]?.id || '')
  }

  useEffect(() => { void loadChoices().catch((error) => setFeedback(getAxiosErrorMessage(error))) }, [businessId])

  async function save(): Promise<void> {
    setSaving(true); setFeedback(null)
    try {
      if (mode === 'create') {
        await createRationTemplate({ name: name.trim(), description: description.trim() || null, source_ration_version_id: sourceVersionId })
        setFeedback('Rationsvorlage wurde revisionssicher angelegt.')
      } else if (mode === 'apply') {
        const target = rations.find((ration) => ration.id === targetRationId)
        if (!target) return
        await applyRationTemplate(templateId, {
          target_ration_id: target.id, expected_latest_version_no: target.version_no, reason: reason.trim(),
        })
        setFeedback(`Neue Draft-Version fuer ${target.name} wurde angelegt.`)
      }
      setMode(null); setName(''); setDescription(''); setReason('')
      await Promise.all([loadChoices(), runtime.refetch()])
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  function handleAction(actionKey: string): void {
    if (actionKey === 'create_template') setMode('create')
    if (actionKey === 'apply_template') setMode('apply')
  }

  if (schemaQuery.error || runtime.entityError) return <p role="alert">{getAxiosErrorMessage(schemaQuery.error ?? runtime.entityError)}</p>
  if (!runtime.plan) return <p className="p-4 text-sm text-muted-foreground">Betriebsakte wird geladen...</p>

  return (
    <div data-testid="feeding-business-detail" data-runtime="native">
      {feedback ? <p className="mb-3 rounded-md border bg-muted px-3 py-2 text-sm" role="status">{feedback}</p> : null}
      <UniversalMaskRenderer
        plan={runtime.plan} data={runtime.entityData} entityId={businessId}
        tables={runtime.tableRows} tableQueryStates={runtime.tableQueryStates} tableTotals={runtime.tableTotals}
        lookupBindings={runtime.lookupBindings} onTableQueryChange={runtime.setTableQuery}
        overlay={runtime.userOverlay} onOverlayChange={runtime.updateUserOverlay} onOverlayReset={runtime.resetUserOverlay}
        onAction={(key) => handleAction(key)}
      />
      <Dialog open={mode !== null} onOpenChange={(open) => { if (!open) setMode(null) }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{mode === 'create' ? 'Rationsvorlage anlegen' : 'Vorlage als neue Draft-Version anwenden'}</DialogTitle>
            <DialogDescription>Die Quellversion bleibt unveraenderlich; Herkunft und Begruendung werden auditierbar gespeichert.</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-2">
            {mode === 'create' ? <>
              <div className="grid gap-2"><Label htmlFor="template-name">Vorlagenname</Label><Input id="template-name" value={name} onChange={(event) => setName(event.target.value)} /></div>
              <div className="grid gap-2"><Label htmlFor="template-source">Quellration</Label><select id="template-source" className="h-10 rounded-md border bg-background px-3" value={sourceVersionId} onChange={(event) => setSourceVersionId(event.target.value)}>{rations.map((ration) => <option key={ration.version_id} value={ration.version_id}>{ration.group_name} · {ration.name} · v{ration.version_no}</option>)}</select></div>
              <div className="grid gap-2"><Label htmlFor="template-description">Beschreibung</Label><Input id="template-description" value={description} onChange={(event) => setDescription(event.target.value)} /></div>
            </> : <>
              <div className="grid gap-2"><Label htmlFor="apply-template">Vorlage</Label><select id="apply-template" className="h-10 rounded-md border bg-background px-3" value={templateId} onChange={(event) => setTemplateId(event.target.value)}>{templates.map((template) => <option key={template.id} value={template.id}>{template.name} · {template.source_ration_name} v{template.source_version_no}</option>)}</select></div>
              <div className="grid gap-2"><Label htmlFor="apply-target">Zielration</Label><select id="apply-target" className="h-10 rounded-md border bg-background px-3" value={targetRationId} onChange={(event) => setTargetRationId(event.target.value)}>{rations.map((ration) => <option key={ration.id} value={ration.id}>{ration.group_name} · {ration.name} · aktuell v{ration.version_no}</option>)}</select></div>
              <div className="grid gap-2"><Label htmlFor="apply-reason">Kopiergrund</Label><Input id="apply-reason" value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Mindestens 10 Zeichen" /></div>
            </>}
          </div>
          <DialogFooter><Button variant="outline" onClick={() => setMode(null)}>Abbrechen</Button><Button disabled={saving || (mode === 'create' ? !name.trim() || !sourceVersionId : !templateId || !targetRationId || reason.trim().length < 10)} onClick={() => { void save() }}>{saving ? 'Speichert...' : 'Ausfuehren'}</Button></DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
