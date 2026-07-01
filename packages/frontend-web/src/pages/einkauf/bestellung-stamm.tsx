import { useState, useEffect } from 'react'
import { useNavigate, useParams, useSearchParams } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import type { TFunction } from 'i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig, type Field } from '@/components/mask-builder/types'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { CrudAuditTrailPanel } from '@/features/crud/components'
import { useCrudAuditTrail } from '@/features/crud/hooks'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { History, XCircle, AlertTriangle, Mail, Globe } from 'lucide-react'
import { usePoCommunications, useSendPoCommunication } from '@/lib/api/procurement-plus'
import { useApprovePurchaseOrder, useCancelPurchaseOrder } from '@/lib/api/purchase-orders'
import { useAuth } from '@/hooks/useAuth'
import { useTenant } from '@/hooks/useTenant'
import type { ChangeLog } from '@/features/crud/components/CrudAuditTrailPanel'
import { WorkflowEntryBanner, readWorkflowEntryContext } from '@/components/workflow/WorkflowEntryBanner'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import { isRecord, recordArrayFromResponse, stringValue } from '@/lib/record-utils'

const createBestellungConfig = (t: TFunction, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.actions.edit'),
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'nummer',
          label: t('crud.fields.number'),
          type: 'text',
          required: true,
          readonly: true
        },
        {
          name: 'lieferantId',
          label: t('crud.entities.supplier'),
          type: 'lookup',
          required: true,
          endpoint: '/api/v1/crm/business-partners?type=supplier',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'ENTWURF', label: t('status.draft') },
            { value: 'FREIGEGEBEN', label: t('status.approved') },
            { value: 'TEILGELIEFERT', label: t('status.partial') },
            { value: 'VOLLGELIEFERT', label: t('status.completed') },
            { value: 'STORNIERT', label: t('status.cancelled') }
          ]
        },
        {
          name: 'liefertermin',
          label: t('crud.fields.deliveryDate'),
          type: 'date',
          required: true
        },
        {
          name: 'zahlungsbedingungen',
          label: t('crud.fields.paymentTerms'),
          type: 'select',
          options: [
            { value: 'sofort', label: t('crud.fields.paymentTermsImmediate') },
            { value: '14tage', label: t('crud.fields.paymentTermsNet14') },
            { value: '30tage', label: t('crud.fields.paymentTermsNet30') },
            { value: '60tage', label: t('crud.fields.paymentTermsNet60') }
          ]
        },
        {
          name: 'incoterms',
          label: t('crud.fields.incoterms'),
          type: 'select',
          options: [
            { value: 'EXW', label: t('crud.fields.incotermsEXW') },
            { value: 'FCA', label: t('crud.fields.incotermsFCA') },
            { value: 'CPT', label: t('crud.fields.incotermsCPT') },
            { value: 'CIP', label: t('crud.fields.incotermsCIP') },
            { value: 'DAT', label: t('crud.fields.incotermsDAT') },
            { value: 'DAP', label: t('crud.fields.incotermsDAP') },
            { value: 'DDP', label: t('crud.fields.incotermsDDP') }
          ]
        },
        {
          name: 'lieferadresse',
          label: t('crud.fields.deliveryAddress'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.deliveryAddress')
        },
        {
          name: 'requisitionId',
          label: t('crud.fields.requisition'),
          type: 'lookup',
          endpoint: '/api/purchase-workflow/requisitions',
          displayField: 'number',
          valueField: 'id',
          helpText: t('crud.tooltips.requisitionReference')
        },
        {
          name: 'contractId',
          label: t('crud.fields.contract'),
          type: 'lookup',
          endpoint: '/api/contracts',
          displayField: 'contractNo',
          valueField: 'id',
          helpText: t('crud.tooltips.contractReference')
        },
        {
          name: 'rfqId',
          label: t('crud.fields.rfq'),
          type: 'lookup',
          endpoint: '/api/purchase-workflow/rfqs',
          displayField: 'number',
          valueField: 'id',
          helpText: t('crud.tooltips.rfqReference')
        }
      ]
    },
    {
      key: 'positionen',
      label: t('crud.fields.items'),
      fields: [
        {
          name: 'positionen',
          label: t('crud.fields.items'),
          type: 'table',
          required: true,
          columns: [
            {
              key: 'artikelId',
              label: t('crud.fields.product'),
              type: 'lookup',
              required: true
            },
            {
              key: 'menge',
              label: t('crud.fields.quantity'),
              type: 'number',
              required: true
            },
            {
              key: 'einheit',
              label: t('crud.fields.unit'),
              type: 'select',
              required: true
            },
            {
              key: 'preis',
              label: t('crud.fields.price'),
              type: 'number'
            },
            {
              key: 'wunschtermin',
              label: t('crud.fields.dueDate'),
              type: 'date'
            }
          ] as Field[],
          helpText: t('crud.fields.items')
        }
      ]
    },
    {
      key: 'belege',
      label: t('crud.detail.additionalInfo'),
      fields: [
        {
          name: 'bemerkungen',
          label: t('crud.fields.notes'),
          type: 'textarea',
          placeholder: t('crud.fields.notes')
        }
      ]
    }
  ],
  actions: [
    {
      key: 'freigeben',
      label: t('crud.actions.approve'),
      type: 'primary',
    },
    {
      key: 'stornieren',
      label: t('crud.actions.cancel'),
      type: 'danger',
    },
    {
      key: 'drucken',
      label: t('crud.actions.print'),
      type: 'secondary',
    },
    {
      key: 'senden',
      label: t('crud.actions.send'),
      type: 'secondary',
    }
  ],
  api: {
    baseUrl: '/api/v1/purchase-orders',
    endpoints: {
      list: '/api/v1/purchase-orders',
      get: '/api/v1/purchase-orders/{id}',
      create: '/api/v1/purchase-orders',
      update: '/api/v1/purchase-orders/{id}',
      delete: '/api/v1/purchase-orders/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write']
})

export default function BestellungStammPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const { user } = useAuth()
  const { tenantId } = useTenant()
  const [loading, setLoading] = useState(false)
  const [stornoDialogOpen, setStornoDialogOpen] = useState(false)
  const [stornoReason, setStornoReason] = useState('')
  const [approvalRequired, setApprovalRequired] = useState(false)
  const [originalData, setOriginalData] = useState<Record<string, unknown> | null>(null)
  const [sendDialogOpen, setSendDialogOpen] = useState(false)
  const [sendMethod, setSendMethod] = useState<'email' | 'portal'>('email')
  const [sendLanguage, setSendLanguage] = useState<'de' | 'en'>('de')
  const [sendRecipients] = useState<string[]>([])
  const [sendMessage, setSendMessage] = useState('')
  const entityType = 'purchaseOrder'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Bestellung')
  const bestellungConfig = createBestellungConfig(t, entityTypeLabel)
  const workflowContext = readWorkflowEntryContext(searchParams)

  const { data, saveData } = useMaskData({
    apiUrl: bestellungConfig.api.baseUrl,
    id: id || undefined
  })
  const poCommunicationId = stringValue(id || data?.nummer || data?.purchaseOrderNumber || data?.id)
  const { data: poCommunications = [] } = usePoCommunications(poCommunicationId)
  const sendPoEmail = useSendPoCommunication(poCommunicationId, 'email')
  const sendPoPortal = useSendPoCommunication(poCommunicationId, 'portal')
  const approvePurchaseOrder = useApprovePurchaseOrder()
  const cancelPurchaseOrder = useCancelPurchaseOrder()

  // Audit Trail
  const { changeLogs, isLoading: isLoadingAudit, refetch: refetchAudit } = useCrudAuditTrail({
    entityType: 'purchaseOrder',
    entityId: id || '',
    fetchAuditTrail: async (entityType: string, entityId: string) => {
      const response = await apiClient.get<unknown>(`/api/v1/audit/logs?entity_type=${entityType}&entity_id=${entityId}&limit=50`)
      return recordArrayFromResponse(response.data).map(log => {
        const changes = isRecord(log.changes) ? log.changes : {}
        return {
        id: stringValue(log.id),
        timestamp: new Date(stringValue(log.timestamp)),
        action: stringValue(log.action),
        userId: stringValue(log.user_id ?? log.user_email, 'system'),
        userName: stringValue(log.user_email ?? log.user_id, 'system'),
        changedFields: Array.isArray(log.changes) ? log.changes.map(String) : Object.keys(changes),
        oldValue: changes.before,
        newValue: changes.after,
        reason: stringValue(log.reason),
        }
      }) as ChangeLog[]
    },
  })

  // Lade Original-Daten beim ersten Laden
  useEffect(() => {
    if (data && !originalData) {
      setOriginalData(JSON.parse(JSON.stringify(data)))
    }
  }, [data, originalData])

  // Prüfe ob Genehmigung erforderlich ist
  useEffect(() => {
    if (data && originalData && data.status !== 'ENTWURF') {
      // Prüfe ob Änderungen gemacht wurden
      const hasChanges = JSON.stringify(data) !== JSON.stringify(originalData)
      if (hasChanges) {
        setApprovalRequired(true)
      }
    }
  }, [data, originalData])

  const handleSave = async (formData: Record<string, unknown>) => {
    setLoading(true)
    try {
      // Prüfe ob Genehmigung erforderlich ist
      if (approvalRequired && formData.status !== 'ENTWURF') {
        // Erstelle Audit-Log für Änderung
        try {
          await apiClient.post('/api/v1/audit/log', {
            user_id: user?.sub ?? 'current-user',
            user_email: user?.email ?? 'user@example.com',
            tenant_id: tenantId,
            action: 'UPDATE',
            entity_type: 'purchaseOrder',
            entity_id: id || formData.id,
            changes: {
              before: originalData,
              after: formData,
            },
          })
        } catch {
          // Audit-Log-Erstellung schlägt still fehl — Hauptaktion (Speichern/Storno) ist abgeschlossen
        }
      }

      // Update mit Version-Incrementierung
      const updateData = {
        ...formData,
        version: (Number(formData.version) || 0) + 1,
      }

      await saveData(updateData)
      
      // Refresh Audit Trail
      if (id) {
        refetchAudit()
      }

      toast({
        title: t('crud.messages.updateSuccess', { entityType: entityTypeLabel }),
      })

      navigate('/einkauf/bestellungen')
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.updateError', { entityType: entityTypeLabel }),
        description: (error as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail || (error as Error)?.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm(t('crud.messages.discardChanges'))) {
      navigate('/einkauf/bestellungen')
    }
  }

  const { handleAction, loadingActionKey } = useMaskActions(async (key: string, formData: Record<string, unknown>) => {
    const purchaseOrderId = id || formData?.id || data?.id || data?.nummer || data?.purchaseOrderNumber
    if (key === 'freigeben') {
      if (!purchaseOrderId) {
        toast({
          variant: 'destructive',
          title: 'Freigabe nicht moeglich',
          description: 'Die Bestellung muss zuerst gespeichert werden.',
        })
        return
      }
      await approvePurchaseOrder.mutateAsync(String(purchaseOrderId))
      toast({ title: 'Bestellung freigegeben', description: `Bestellung ${data?.nummer || data?.purchaseOrderNumber || purchaseOrderId} wurde freigegeben.` })
      navigate('/einkauf/bestellungen')
    } else if (key === 'stornieren') {
      setStornoDialogOpen(true)
    } else if (key === 'drucken') {
      if (purchaseOrderId) {
        window.open(`/api/mcp/documents/purchase_order/${purchaseOrderId}/print?locale=${sendLanguage}`, '_blank')
      }
    } else if (key === 'senden') {
      if (formData?.lieferantId || data?.lieferantId) {
        setSendDialogOpen(true)
      }
    }
  })

  const handleStorno = async () => {
    if (!stornoReason || stornoReason.length < 10) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.messages.reasonMinLength'),
      })
      return
    }

    setLoading(true)
    try {
      const purchaseOrderId = id || data?.id || data?.nummer || data?.purchaseOrderNumber
      if (!purchaseOrderId) {
        throw new Error('Bestellung muss zuerst gespeichert werden.')
      }
      await cancelPurchaseOrder.mutateAsync({ id: String(purchaseOrderId), reason: stornoReason })

      // Erstelle Audit-Log für Storno
      try {
        await apiClient.post('/api/v1/audit/log', {
          user_id: user?.sub ?? 'current-user',
          user_email: user?.email ?? 'user@example.com',
          tenant_id: tenantId,
          action: 'CANCEL',
          entity_type: 'purchaseOrder',
          entity_id: String(purchaseOrderId),
          changes: {
            status: 'STORNIERT',
            reason: stornoReason,
          },
        })
      } catch {
        // Audit-Log-Erstellung schlägt still fehl — Hauptaktion (Speichern/Storno) ist abgeschlossen
      }

      toast({
        title: t('crud.messages.cancelSuccess', { entityType: entityTypeLabel }),
      })

      setStornoDialogOpen(false)
      setStornoReason('')
      navigate('/einkauf/bestellungen')
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.cancelError', { entityType: entityTypeLabel }),
        description: (error as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail || (error as Error)?.message,
      })
    } finally {
      setLoading(false)
    }
  }

  // Erweitere Config um Change-Log Tab
  const extendedConfig: MaskConfig = {
    ...bestellungConfig,
    tabs: [
      ...bestellungConfig.tabs,
      {
        key: 'versionierung',
        label: t('crud.audit.title'),
        fields: [], // Wird durch CrudAuditTrailPanel ersetzt
      },
    ],
  }

  const normalizedStatus = normalizeOperationalStatus(stringValue(data?.status))
  const blocker =
    data?.status === 'STORNIERT'
      ? 'Die Bestellung ist storniert und kann nicht weiter disponiert werden.'
      : approvalRequired
        ? 'Aenderungen an einer bereits freigegebenen Bestellung brauchen erneute Freigabe.'
        : undefined
  const timelineItems = [
    data?.createdAt
      ? {
          label: 'Bestellung angelegt',
          detail: `Beleg ${data?.nummer || data?.purchaseOrderNumber || id || 'neu'} wurde als Vorgang erfasst.`,
          timestamp: data.createdAt,
        }
      : null,
    data?.approvedAt
      ? {
          label: 'Freigabe erteilt',
          detail: data?.approvedBy ? `Freigegeben durch ${data.approvedBy}.` : 'Freigabe liegt vor.',
          timestamp: data.approvedAt,
        }
      : null,
    poCommunications[0]
      ? {
          label: 'Letzte Lieferantenkommunikation',
          detail: `${poCommunications[0].channel || 'email'} / ${poCommunications[0].status || 'offen'}`,
          timestamp: poCommunications[0].createdAt,
        }
      : null,
    changeLogs[0]
      ? {
          label: 'Letzter Eingriff',
          detail: `${changeLogs[0].action} durch ${changeLogs[0].userName}`,
          timestamp: changeLogs[0].timestamp instanceof Date ? changeLogs[0].timestamp.toISOString() : undefined,
        }
      : null,
  ].filter(Boolean) as Array<{ label: string; detail?: string; timestamp?: string | null }>

  return (
    <div className="space-y-6">
      {workflowContext ? <WorkflowEntryBanner context={workflowContext} /> : null}

      <OperationalCaseHeader
        title={stringValue(data?.nummer ?? data?.purchaseOrderNumber, 'Bestellung')}
        description="Bestellung als gefuehrter Beschaffungsvorgang mit Objekt-, Governance- und Kommunikationskontext."
        status={normalizedStatus}
        owner={stringValue(data?.lieferant ?? data?.supplierName, 'Einkauf')}
        blocker={blocker}
        nextAction={
          data?.status === 'ENTWURF'
            ? 'Bestellung pruefen und freigeben'
            : data?.status === 'FREIGEGEBEN'
              ? 'Lieferantenkommunikation ausloesen'
              : data?.status === 'TEILGELIEFERT'
                ? 'Restmengen und Liefertermine nachsteuern'
                : data?.status === 'VOLLGELIEFERT'
                  ? 'Abschluss und Rechnungseingang abstimmen'
                  : 'Vorgang pruefen'
        }
        caseLabel={workflowContext?.caseNumber || 'Beschaffungsvorgang'}
        tags={[
          stringValue(data?.zahlungsbedingungen, 'Zahlungsziel offen'),
          stringValue(data?.incoterms, 'Incoterms offen'),
          stringValue(data?.status, 'Status offen'),
        ]}
      />

      <div className="grid gap-6 xl:grid-cols-[1.25fr_0.95fr]">
        <OperationalTimeline title="Vorgang und Timeline" items={timelineItems} />
        <OperationalContextPanel
          title="Bestellkontext"
          sections={[
            {
              title: 'Ressourcenlage',
              items: [
                { label: 'Positionen', value: String((Array.isArray(data?.positionen) ? data.positionen.length : undefined) ?? (Array.isArray(data?.items) ? data.items.length : 0)) },
                { label: 'Liefertermin', value: stringValue(data?.liefertermin ?? data?.deliveryDate, '-') },
              ],
            },
            {
              title: 'Wirtschaftslage',
              items: [
                { label: 'Zahlungsbedingungen', value: stringValue(data?.zahlungsbedingungen ?? data?.paymentTerms, '-') },
                { label: 'Incoterms', value: stringValue(data?.incoterms, '-') },
              ],
            },
            {
              title: 'Governance',
              items: [
                { label: 'Version', value: String(data?.version ?? 0) },
                { label: 'Audit-Eintraege', value: String(changeLogs.length) },
              ],
            },
          ]}
        />
      </div>

      <ObjectPage
        config={extendedConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
        onAction={handleAction}
        loadingActionKey={loadingActionKey}
      />

      {/* Change-Log Panel (wenn ID vorhanden) */}
      {id && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5" />
              {t('crud.audit.title')}
              {Boolean(data?.version) && (
                <Badge variant="outline" className="ml-2">
                  {t('crud.fields.version')}: {stringValue(data?.version)}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CrudAuditTrailPanel
              entityType={entityTypeLabel}
              entityId={id}
              changeLogs={changeLogs}
              isLoading={isLoadingAudit}
            />
          </CardContent>
        </Card>
      )}

      {/* PO-Kommunikation */}
      {poCommunicationId && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mail className="h-5 w-5" />
              Kommunikation
            </CardTitle>
          </CardHeader>
          <CardContent>
            {poCommunications.length === 0 ? (
              <div className="text-sm text-muted-foreground">Keine Kommunikation vorhanden.</div>
            ) : (
              <div className="space-y-2">
                {poCommunications.map((entry) => (
                  <div key={entry.id} className="flex items-center justify-between rounded border p-3">
                    <div className="space-y-1">
                      <div className="font-medium">{entry.subject || 'PO Kommunikation'}</div>
                      <div className="text-sm text-muted-foreground">{entry.message || '-'}</div>
                      <div className="text-xs text-muted-foreground">
                        {entry.createdAt ? new Date(entry.createdAt).toLocaleString() : '-'}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{entry.status || '-'}</Badge>
                      <Badge variant="secondary" className="flex items-center gap-1">
                        {entry.channel === 'portal' ? <Globe className="h-3 w-3" /> : <Mail className="h-3 w-3" />}
                        {entry.channel || 'email'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Storno Dialog */}
      <Dialog open={stornoDialogOpen} onOpenChange={setStornoDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('crud.dialogs.cancel.title', { entityType: entityTypeLabel })}</DialogTitle>
            <DialogDescription>
              {t('crud.dialogs.cancel.descriptionGeneric', { entityType: entityTypeLabel })}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="stornoReason">{t('crud.dialogs.cancel.reasonRequired')}</Label>
              <Textarea
                id="stornoReason"
                value={stornoReason}
                onChange={(e) => setStornoReason(e.target.value)}
                placeholder={t('crud.dialogs.cancel.reasonPlaceholder')}
                required
                minLength={10}
                rows={4}
              />
              <p className="text-sm text-muted-foreground mt-1">
                {t('crud.dialogs.cancel.reasonMinLength')}
              </p>
            </div>
            {data?.status === 'FREIGEGEBEN' && (
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5" />
                  <div className="text-sm text-yellow-800">
                    {t('crud.dialogs.cancel.warning')}
                  </div>
                </div>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setStornoDialogOpen(false)}>
              {t('crud.dialogs.cancel.cancelButton')}
            </Button>
            <Button variant="destructive" onClick={handleStorno} disabled={loading || stornoReason.length < 10}>
              {loading ? t('crud.dialogs.cancel.confirming') : t('crud.dialogs.cancel.confirmButton')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Send PO Dialog */}
      <Dialog open={sendDialogOpen} onOpenChange={setSendDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{t('crud.actions.sendPo')}</DialogTitle>
            <DialogDescription>
              {t('crud.dialogs.sendPo.description')}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>{t('crud.fields.sendMethod')}</Label>
              <NativeSelect
                value={sendMethod}
                onValueChange={(value) => setSendMethod(value as 'email' | 'portal')}
                options={[
                  { value: 'email', label: t('crud.fields.email') },
                  { value: 'portal', label: t('crud.fields.portal') },
                ]}
              />
            </div>

            <div>
              <Label>{t('crud.fields.language')}</Label>
              <NativeSelect
                value={sendLanguage}
                onValueChange={(value) => setSendLanguage(value as 'de' | 'en')}
                options={[
                  { value: 'de', label: t('crud.fields.german') },
                  { value: 'en', label: t('crud.fields.english') },
                ]}
              />
            </div>

            {sendMethod === 'email' && (
              <div>
                <Label>{t('crud.fields.recipients')}</Label>
                <div className="space-y-2">
                  {Boolean(data?.lieferant) && (
                    <div className="flex items-center justify-between p-2 border rounded">
                      <span>{stringValue(data?.lieferant)}</span>
                      <Badge variant="outline">{t('crud.entities.supplier')}</Badge>
                    </div>
                  )}
                  <p className="text-sm text-muted-foreground">
                    {t('crud.dialogs.sendPo.recipientInfo')}
                  </p>
                </div>
              </div>
            )}

            {sendMethod === 'portal' && (
              <div>
                <Label>{t('crud.fields.portalAccess')}</Label>
                <p className="text-sm text-muted-foreground">
                  {t('crud.dialogs.sendPo.portalInfo')}
                </p>
              </div>
            )}

            <div>
              <Label htmlFor="sendMessage">{t('crud.fields.message')} ({t('crud.fields.optional')})</Label>
              <Textarea
                id="sendMessage"
                value={sendMessage}
                onChange={(e) => setSendMessage(e.target.value)}
                placeholder={t('crud.tooltips.placeholders.sendMessage')}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setSendDialogOpen(false)
              setSendMessage('')
            }}>
              {t('common.cancel')}
            </Button>
            <Button
              onClick={async () => {
                if (!id && !data?.nummer) {
                  toast({
                    variant: 'destructive',
                    title: t('crud.messages.validationError'),
                    description: t('crud.messages.saveFirstGeneric'),
                  })
                  return
                }

                setLoading(true)
                try {
                  const poId = id || data?.nummer
                  const sendPayload = {
                    subject: `Bestellung ${stringValue(data?.nummer ?? data?.purchaseOrderNumber ?? poId)}`,
                    recipient: sendRecipients[0] || stringValue(data?.lieferantId ?? data?.supplierId),
                    message: sendMessage || undefined,
                    language: sendLanguage,
                  }

                  if (sendMethod === 'email') {
                    await sendPoEmail.mutateAsync(sendPayload)
                  } else {
                    await sendPoPortal.mutateAsync(sendPayload)
                  }

                  toast({
                    title: t('crud.messages.poSentSuccess'),
                    description: t('crud.messages.poSentToSupplier', { method: sendMethod === 'email' ? t('crud.fields.email') : t('crud.fields.portal') }),
                  })

                  setSendDialogOpen(false)
                  setSendMessage('')
                } catch (error: unknown) {
                  toast({
                    variant: 'destructive',
                    title: t('crud.messages.poSendError'),
                    description: (error as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail || (error as Error)?.message,
                  })
                } finally {
                  setLoading(false)
                }
              }}
              disabled={loading}
            >
              {loading ? t('common.loading') : t('crud.actions.send')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Storno Button (wenn Status erlaubt) */}
      {data && data.status !== 'STORNIERT' && data.status !== 'VOLLGELIEFERT' && (
        <div className="fixed bottom-6 right-6">
          <Button
            variant="destructive"
            size="lg"
            onClick={() => setStornoDialogOpen(true)}
            className="shadow-lg"
          >
            <XCircle className="h-4 w-4 mr-2" />
            {t('crud.actions.cancel')}
          </Button>
        </div>
      )}

      {/* Genehmigung-Hinweis */}
      {approvalRequired && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div>
                <div className="font-semibold text-yellow-800 mb-1">
                  {t('crud.messages.approvalRequired')}
                </div>
                <p className="text-sm text-yellow-700">
                  {t('crud.messages.approvalRequiredDesc')}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
