import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import { toast } from '@/hooks/use-toast'
import { Wizard } from '@/components/patterns/Wizard'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Plus, Trash2 } from 'lucide-react'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { apiClient } from '@/lib/api-client'
import { saveFlowSpineResumeCheckpoint } from '@/lib/api/flow-spines'
import { WorkflowEntryBanner, readWorkflowEntryContext } from '@/components/workflow/WorkflowEntryBanner'

type BestellungData = {
  lieferant: string
  liefertermin: string
  zahlungsbedingung: string
  incoterms?: string
  lieferadresse: string
  requisitionId?: string
  contractId?: string
  rfqId?: string
  positionen: Array<{
    artikel: string
    menge: number
    einheit: string
    preis: number
  }>
  notizen: string
}

type EinkaufAnfragePrefill = {
  id: string
  anfrageNummer?: string
  typ?: string
  anforderer?: string
  artikel?: string
  menge?: number
  prioritaet?: string
  status?: string
  faelligkeit?: string | null
}

function mergeNotes(existingNotes: string, lines: Array<string | undefined | null>): string {
  const existing = existingNotes
    .split('\n')
    .map((entry) => entry.trim())
    .filter(Boolean)
  const additions = lines.map((entry) => entry?.trim() ?? '').filter(Boolean)
  const unique = [...existing]
  for (const addition of additions) {
    if (!unique.includes(addition)) {
      unique.push(addition)
    }
  }
  return unique.join('\n')
}

function buildRequestPositions(request: EinkaufAnfragePrefill, fallback: BestellungData['positionen']): BestellungData['positionen'] {
  const artikel = request.artikel?.trim() ?? ''
  const menge = typeof request.menge === 'number' && request.menge > 0 ? request.menge : 1
  if (!artikel) {
    return fallback
  }
  return [{ artikel, menge, einheit: 't', preis: 0 }]
}

function buildContractPositions(contract: Record<string, unknown>, fallback: BestellungData['positionen']): BestellungData['positionen'] {
  const artikel = String(contract.commodity || '').trim()
  const contractedQuantity = Number(contract.qty?.contracted ?? 0)
  if (!artikel) {
    return fallback
  }
  return [{ artikel, menge: contractedQuantity > 0 ? contractedQuantity : 1, einheit: String(contract.qty?.unit || 'kg') || 'kg', preis: 0 }]
}

function getErrorMessage(error: unknown): string {
  if (typeof error === 'object' && error !== null) {
    const maybeMessage = (error as { message?: unknown }).message
    if (typeof maybeMessage === 'string' && maybeMessage.trim()) {
      return maybeMessage
    }
  }
  return 'Die Quelldaten konnten nicht geladen werden.'
}

export default function BestellungAnlegenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const entityType = 'purchaseOrder'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Bestellung')
  const requisitionId = searchParams.get('requisitionId')
  const contractId = searchParams.get('contractId')
  const rfqId = searchParams.get('rfqId')
  const workflowContext = useMemo(() => readWorkflowEntryContext(searchParams), [searchParams])

  const buildWorkflowResumeQuery = (purchaseOrderId?: string): string => {
    const params = new URLSearchParams(searchParams)
    if (purchaseOrderId) params.set('purchaseOrderId', purchaseOrderId)
    return params.toString()
  }

  const persistWorkflowResume = async (purchaseOrderId?: string): Promise<void> => {
    if (!workflowContext?.process || !workflowContext.instanceId) return
    const query = buildWorkflowResumeQuery(purchaseOrderId)
    const basePath = purchaseOrderId
      ? `/einkauf/bestellungen/${encodeURIComponent(purchaseOrderId)}`
      : '/einkauf/bestellungen/neu'
    await saveFlowSpineResumeCheckpoint(workflowContext.process, workflowContext.instanceId, {
      resume_node_id: 'purchase-order',
      resume_route: `${basePath}${query ? `?${query}` : ''}`,
      resume_payload: {
        screen: purchaseOrderId ? 'purchase-order-detail' : 'purchase-order-create',
        purchaseOrderId: purchaseOrderId || undefined,
        workflowCase: workflowContext.caseNumber || undefined,
      },
      business_status: purchaseOrderId ? 'bestellung_erfasst' : 'bestellung_in_bearbeitung',
      action_label: purchaseOrderId ? 'Bestellung gespeichert' : 'Bestellentwurf gesichert',
    })
  }
  
  const [bestellung, setBestellung] = useState<BestellungData>({
    lieferant: '',
    liefertermin: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
    zahlungsbedingung: 'net30',
    incoterms: '',
    lieferadresse: '',
    requisitionId: requisitionId || undefined,
    contractId: contractId || undefined,
    rfqId: rfqId || undefined,
    positionen: [{ artikel: '', menge: 1, einheit: 't', preis: 0 }],
    notizen: '',
  })

  useEffect(() => {
    // Lade Requisition-Daten, falls requisitionId vorhanden
    if (requisitionId) {
      loadRequisitionData(requisitionId)
    }
    // Lade Contract-Daten, falls contractId vorhanden
    if (contractId) {
      loadContractData(contractId)
    }
    // Lade RFQ-Daten, falls rfqId vorhanden
    if (rfqId) {
      loadRFQData(rfqId)
    }
  }, [requisitionId, contractId, rfqId])

  useEffect(() => {
    if (!workflowContext) return
    setBestellung((prev) => ({
      ...prev,
      lieferant: prev.lieferant || workflowContext.partnerName,
      notizen: prev.notizen || [
        workflowContext.caseNumber ? `Workflow-Vorgang ${workflowContext.caseNumber}` : '',
        workflowContext.entryMode ? `Einstieg: ${workflowContext.entryMode}` : '',
        workflowContext.subject,
      ].filter(Boolean).join('\n'),
    }))
  }, [workflowContext])

  const loadRequisitionData = async (id: string) => {
    try {
      const req = (await apiClient.get<Record<string, unknown>>(`/api/v1/einkauf/anfragen/${id}`)).data
      if (req) {
        setBestellung(prev => ({
          ...prev,
          requisitionId: req.anfrageNummer || req.id || prev.requisitionId,
          liefertermin: req.faelligkeit || prev.liefertermin,
          positionen: buildRequestPositions(req, prev.positionen),
          notizen: mergeNotes(prev.notizen, [
            req.anfrageNummer ? `Bedarfsmeldung ${req.anfrageNummer}` : '',
            req.anforderer ? `Anforderer: ${req.anforderer}` : '',
          ]),
        }))
        toast({ title: 'Bedarfsmeldung geladen', description: `Felder aus Bedarfsmeldung ${req.anfrageNummer || id} vorbelegt.` })
      }
    } catch (error) {
      toast({
        title: 'Bedarfsmeldung konnte nicht geladen werden',
        description: getErrorMessage(error),
        variant: 'destructive',
      })
    }
  }

  const loadContractData = async (id: string) => {
    try {
      const contract: Record<string, unknown> = (await apiClient.get<Record<string, unknown>>(`/api/v1/contracts/${id}`)).data
      if (contract) {
        setBestellung(prev => ({
          ...prev,
          contractId: contract.contractNo || contract.id || prev.contractId,
          lieferant: contract.supplierId || contract.counterpartyId || prev.lieferant,
          liefertermin: contract.deliveryWindow?.to || prev.liefertermin,
          incoterms: contract.incoterms || prev.incoterms,
          zahlungsbedingung: contract.paymentTerms || prev.zahlungsbedingung,
          positionen: buildContractPositions(contract, prev.positionen),
          notizen: mergeNotes(prev.notizen, [
            contract.contractNo ? `Vertragsbezug ${contract.contractNo}` : '',
          ]),
        }))
        toast({ title: 'Vertrag geladen', description: `Felder aus Vertrag ${contract.contractNo || id} vorbelegt.` })
      }
    } catch (error) {
      toast({
        title: 'Vertrag konnte nicht geladen werden',
        description: getErrorMessage(error),
        variant: 'destructive',
      })
    }
  }

  const loadRFQData = async (id: string) => {
    try {
      const rfq = (await apiClient.get<Record<string, unknown>>(`/api/v1/einkauf/anfragen/${id}`)).data
      if (rfq) {
        setBestellung(prev => ({
          ...prev,
          rfqId: rfq.anfrageNummer || rfq.id || prev.rfqId,
          liefertermin: rfq.faelligkeit || prev.liefertermin,
          positionen: buildRequestPositions(rfq, prev.positionen),
          notizen: mergeNotes(prev.notizen, [
            rfq.anfrageNummer ? `RFQ-Bezug ${rfq.anfrageNummer}` : '',
            rfq.status ? `RFQ-Status: ${rfq.status}` : '',
          ]),
        }))
        toast({ title: 'Anfrage geladen', description: `Felder aus Anfrage ${rfq.anfrageNummer || id} vorbelegt.` })
      }
    } catch (error) {
      toast({
        title: 'Anfrage konnte nicht geladen werden',
        description: getErrorMessage(error),
        variant: 'destructive',
      })
    }
  }

  function updateField<K extends keyof BestellungData>(key: K, value: BestellungData[K]): void {
    setBestellung((prev) => ({ ...prev, [key]: value }))
  }

  function addPosition(): void {
    setBestellung((prev) => ({
      ...prev,
      positionen: [...prev.positionen, { artikel: '', menge: 1, einheit: 't', preis: 0 }],
    }))
  }

  function updatePosition(index: number, field: string, value: string | number): void {
    setBestellung((prev) => ({
      ...prev,
      positionen: prev.positionen.map((pos, i) => (i === index ? { ...pos, [field]: value } : pos)),
    }))
  }

  function removePosition(index: number): void {
    setBestellung((prev) => ({
      ...prev,
      positionen: prev.positionen.filter((_, i) => i !== index),
    }))
  }

  function validateBestellung(): string | null {
    if (!bestellung.lieferant.trim()) {
      return 'Lieferant ist ein Pflichtfeld.'
    }

    if (!bestellung.liefertermin) {
      return 'Liefertermin ist ein Pflichtfeld.'
    }

    if (bestellung.positionen.length === 0) {
      return 'Mindestens eine Position ist erforderlich.'
    }

    const invalidPosition = bestellung.positionen.find(
      (position) => !position.artikel.trim() || position.menge <= 0 || position.preis < 0,
    )

    if (invalidPosition) {
      return 'Alle Positionen brauchen Artikel, Menge groesser 0 und einen nicht negativen Preis.'
    }

    return null
  }

  function validateStep(stepId: string): string | null {
    if (stepId === 'lieferant') {
      if (!bestellung.lieferant.trim()) {
        return 'Lieferant ist ein Pflichtfeld.'
      }
      if (!bestellung.liefertermin) {
        return 'Liefertermin ist ein Pflichtfeld.'
      }
      return null
    }

    if (stepId === 'positionen') {
      if (bestellung.positionen.length === 0) {
        return 'Mindestens eine Position ist erforderlich.'
      }
      const invalidPosition = bestellung.positionen.find(
        (position) => !position.artikel.trim() || position.menge <= 0 || position.preis < 0,
      )
      if (invalidPosition) {
        return 'Alle Positionen brauchen Artikel, Menge groesser 0 und einen nicht negativen Preis.'
      }
    }

    return null
  }

  async function handleSubmit(): Promise<void> {
    const validationError = validateBestellung()
    if (validationError) {
      toast({
        title: t('crud.messages.validationError', { defaultValue: 'Validierung fehlgeschlagen' }),
        description: validationError,
        variant: 'destructive',
      })
      return
    }

    try {
      const purchaseOrder = {
        orderDate: new Date().toISOString().slice(0, 10),
        supplierId: bestellung.lieferant,
        subject: workflowContext?.subject || 'Bestellung',
        description: bestellung.notizen || '',
        status: 'ENTWURF',
        deliveryDate: bestellung.liefertermin,
        deliveryAddress: bestellung.lieferadresse,
        shippingAddress: bestellung.lieferadresse,
        paymentTerms: bestellung.zahlungsbedingung,
        incoterms: bestellung.incoterms,
        requisitionId: bestellung.requisitionId,
        contractId: bestellung.contractId,
        rfqId: bestellung.rfqId,
        notes: bestellung.notizen || undefined,
        taxRate: 19,
        items: bestellung.positionen.map((pos) => ({
          itemType: 'PRODUCT',
          description: pos.artikel,
          quantity: pos.menge,
          unitPrice: pos.preis,
          discountPercent: 0,
        })),
      }

      const created = await apiClient.post<{ id?: string; purchaseOrderNumber?: string }>(
        '/api/v1/purchase-orders',
        purchaseOrder,
      )
      const purchaseOrderId = created.id || created.purchaseOrderNumber
      await persistWorkflowResume(purchaseOrderId)
      if (purchaseOrderId) {
        navigate(`/einkauf/bestellungen/${encodeURIComponent(purchaseOrderId)}?${buildWorkflowResumeQuery(purchaseOrderId)}`)
      } else {
        navigate('/einkauf/bestellungen')
      }
    } catch (error) {
      toast({ title: t('common.error', { defaultValue: 'Fehler' }), description: t('crud.messages.createError', { entityType: entityTypeLabel, defaultValue: 'Erstellen fehlgeschlagen.' }), variant: 'destructive' })
    }
  }

  const gesamtBetrag = bestellung.positionen.reduce((sum, pos) => sum + pos.menge * pos.preis, 0)

  const steps = [
    {
      id: 'lieferant',
      title: t('crud.entities.supplier'),
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="lieferant">{t('crud.entities.supplier')} *</Label>
            <Input
              id="lieferant"
              value={bestellung.lieferant}
              onChange={(e) => updateField('lieferant', e.target.value)}
              placeholder={t('crud.fields.supplier')}
              required
            />
          </div>
          <div>
            <Label htmlFor="liefertermin">{t('crud.fields.deliveryDate')} *</Label>
            <Input
              id="liefertermin"
              type="date"
              value={bestellung.liefertermin}
              onChange={(e) => updateField('liefertermin', e.target.value)}
              required
            />
            <p className="mt-1 text-sm text-muted-foreground">{t('crud.fields.deliveryDate')}</p>
          </div>
          <div>
            <Label htmlFor="zahlungsbedingung">{t('crud.fields.paymentTerms')}</Label>
            <select
              id="zahlungsbedingung"
              value={bestellung.zahlungsbedingung}
              onChange={(e) => updateField('zahlungsbedingung', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="net30">{t('crud.fields.paymentTermsNet30')}</option>
              <option value="net14">{t('crud.fields.paymentTermsNet14')}</option>
              <option value="net7">{t('crud.fields.paymentTermsNet7')}</option>
              <option value="prepay">{t('crud.fields.paymentTermsPrepay')}</option>
            </select>
          </div>
          <div>
            <Label htmlFor="incoterms">{t('crud.fields.incoterms')}</Label>
            <NativeSelect
              value={bestellung.incoterms || ''}
              onValueChange={(value) => updateField('incoterms', value)}
              options={[
                { value: 'EXW', label: t('crud.fields.incotermsEXW') },
                { value: 'FCA', label: t('crud.fields.incotermsFCA') },
                { value: 'CPT', label: t('crud.fields.incotermsCPT') },
                { value: 'CIP', label: t('crud.fields.incotermsCIP') },
                { value: 'DAT', label: t('crud.fields.incotermsDAT') },
                { value: 'DAP', label: t('crud.fields.incotermsDAP') },
                { value: 'DDP', label: t('crud.fields.incotermsDDP') },
              ]}
              placeholder={t('crud.tooltips.placeholders.incoterms')}
            />
          </div>
          <div>
            <Label htmlFor="lieferadresse">{t('crud.fields.deliveryAddress')}</Label>
            <Textarea
              id="lieferadresse"
              value={bestellung.lieferadresse}
              onChange={(e) => updateField('lieferadresse', e.target.value)}
              placeholder={t('crud.tooltips.placeholders.deliveryAddress')}
              rows={3}
            />
          </div>
          {bestellung.requisitionId && (
            <div className="p-3 bg-blue-50 rounded-md">
              <p className="text-sm text-blue-700">
                {t('crud.fields.requisition')}: {bestellung.requisitionId}
              </p>
            </div>
          )}
          {bestellung.contractId && (
            <div className="p-3 bg-green-50 rounded-md">
              <p className="text-sm text-green-700">
                {t('crud.fields.contract')}: {bestellung.contractId}
              </p>
            </div>
          )}
          {bestellung.rfqId && (
            <div className="p-3 bg-yellow-50 rounded-md">
              <p className="text-sm text-yellow-700">
                {t('crud.fields.rfq')}: {bestellung.rfqId}
              </p>
            </div>
          )}
        </div>
      ),
    },
    {
      id: 'positionen',
      title: t('crud.fields.items'),
      content: (
        <div className="space-y-4">
          {bestellung.positionen.map((pos, index) => (
            <Card key={index}>
              <CardContent className="pt-6">
                <div className="flex gap-4">
                  <div className="flex-1">
                    <Label>{t('crud.fields.product')} *</Label>
                    <Input
                      value={pos.artikel}
                      onChange={(e) => updatePosition(index, 'artikel', e.target.value)}
                      placeholder={t('crud.fields.product')}
                    />
                  </div>
                  <div className="w-24">
                    <Label>{t('crud.fields.quantity')}</Label>
                    <Input
                      type="number"
                      value={pos.menge}
                      onChange={(e) => updatePosition(index, 'menge', Number(e.target.value))}
                      min="0"
                    />
                  </div>
                  <div className="w-20">
                    <Label>{t('crud.fields.unit')}</Label>
                    <select
                      value={pos.einheit}
                      onChange={(e) => updatePosition(index, 'einheit', e.target.value)}
                      className="w-full rounded-md border border-input bg-background px-3 py-2"
                    >
                      <option value="t">t</option>
                      <option value="kg">kg</option>
                      <option value="l">l</option>
                      <option value="Stk">Stk</option>
                    </select>
                  </div>
                  <div className="w-32">
                    <Label>{t('crud.fields.price')} (€)</Label>
                    <Input
                      type="number"
                      value={pos.preis}
                      onChange={(e) => updatePosition(index, 'preis', Number(e.target.value))}
                      min="0"
                      step="0.01"
                    />
                  </div>
                  <div className="flex items-end">
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      onClick={() => removePosition(index)}
                      disabled={bestellung.positionen.length === 1}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <div className="mt-2 text-right text-sm text-muted-foreground">
                  {t('crud.fields.total')}:{' '}
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                    pos.menge * pos.preis
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
          <Button type="button" variant="outline" className="w-full gap-2" onClick={addPosition}>
            <Plus className="h-4 w-4" />
            {t('crud.actions.addItem')}
          </Button>
        </div>
      ),
    },
    {
      id: 'lieferung',
      title: t('crud.entities.delivery'),
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="lieferadresse">{t('crud.fields.deliveryAddress')}</Label>
            <Textarea
              id="lieferadresse"
              value={bestellung.lieferadresse}
              onChange={(e) => updateField('lieferadresse', e.target.value)}
              placeholder={t('crud.fields.deliveryAddress')}
              rows={4}
            />
          </div>
          <div>
            <Label htmlFor="notizen">{t('crud.fields.notes')} ({t('common.optional')})</Label>
            <Textarea
              id="notizen"
              value={bestellung.notizen}
              onChange={(e) => updateField('notizen', e.target.value)}
              placeholder={t('crud.fields.notes')}
              rows={4}
            />
          </div>
        </div>
      ),
    },
    {
      id: 'zusammenfassung',
      title: t('crud.detail.summary'),
      content: (
        <div className="space-y-6">
          <Card>
            <CardContent className="pt-6">
              <h3 className="mb-4 text-lg font-semibold">{t('crud.detail.basicInfo')}</h3>
              <dl className="grid gap-3 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">{t('crud.entities.supplier')}</dt>
                  <dd className="text-sm">{bestellung.lieferant || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">{t('crud.fields.deliveryDate')}</dt>
                  <dd className="text-sm">
                    {new Date(bestellung.liefertermin).toLocaleDateString('de-DE')}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">{t('crud.fields.paymentTerms')}</dt>
                  <dd className="text-sm">{bestellung.zahlungsbedingung}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">{t('crud.fields.deliveryAddress')}</dt>
                  <dd className="text-sm">{bestellung.lieferadresse || t('crud.fields.standard')}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <h3 className="mb-4 text-lg font-semibold">{t('crud.fields.items')} ({bestellung.positionen.length})</h3>
              <div className="space-y-2">
                {bestellung.positionen.map((pos, index) => (
                  <div key={index} className="flex justify-between text-sm">
                    <span>
                      {pos.artikel || t('crud.fields.product')} ({pos.menge} {pos.einheit})
                    </span>
                    <span className="font-medium">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                        pos.menge * pos.preis
                      )}
                    </span>
                  </div>
                ))}
                <div className="mt-4 flex justify-between border-t pt-2 font-semibold">
                  <span>{t('crud.fields.total')}</span>
                  <span>
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                      gesamtBetrag
                    )}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      {workflowContext ? (
        <WorkflowEntryBanner
          context={workflowContext}
          title="Workflow-Handover aus Procure-to-Pay"
          description="Lieferant, Positionen, Mengen, Preise, Incoterms und Termine werden jetzt in der Bestellmaske gepflegt. Die Bestellnummer wird erst beim Speichern im Backend aus dem Nummernkreis vergeben."
        />
      ) : null}
      <Card className="border-dashed border-slate-300/60 bg-slate-50/40 dark:bg-slate-900/20">
        <CardContent className="py-3 text-sm text-muted-foreground">
          <div className="font-medium text-foreground">Bestellnummer</div>
          <div>Wird beim Speichern serverseitig aus dem Nummernkreis vergeben. Im Workflow erfasst du hier zuerst Lieferant, Positionen, Mengen, Preise, Zahlungsbedingungen und Lieferadresse.</div>
        </CardContent>
      </Card>
      <Wizard
        title={`${t('crud.actions.new')} ${entityTypeLabel} ${t('crud.actions.create')}`}
        steps={steps}
        getStepValidationError={validateStep}
        onStepValidationError={(_stepId, message) =>
          toast({
            title: t('crud.messages.validationError', { defaultValue: 'Validierung fehlgeschlagen' }),
            description: message,
            variant: 'destructive',
          })
        }
        onFinish={handleSubmit}
        onCancel={() => navigate('/einkauf/bestellungen')}
      />
    </div>
  )
}




