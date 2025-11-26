import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { CrudAuditTrailPanel, CrudCancelDialog } from '@/features/crud/components'
import { useCrudAuditTrail } from '@/features/crud/hooks'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { History, XCircle, AlertTriangle, Mail, Globe } from 'lucide-react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

// Zod-Schema für Bestellung (wird in Komponente mit i18n erstellt)
const createBestellungSchema = (t: any) => z.object({
  nummer: z.string().min(1, t('crud.messages.validationError')),
  lieferantId: z.string().min(1, t('crud.messages.validationError')),
  status: z.enum(['ENTWURF', 'FREIGEGEBEN', 'TEILGELIEFERT', 'VOLLGELIEFERT', 'STORNIERT']),
  liefertermin: z.string().min(1, t('crud.messages.validationError')),
  zahlungsbedingungen: z.string().optional(),
  positionen: z.array(z.object({
    artikelId: z.string().min(1, t('crud.messages.validationError')),
    menge: z.number().min(0.1, t('crud.messages.validationError')),
    einheit: z.string().min(1, t('crud.messages.validationError')),
    preis: z.number().min(0, t('crud.messages.validationError')),
    wunschtermin: z.string().optional()
  })).min(1, t('crud.messages.validationError')),
  bemerkungen: z.string().optional()
})

// Konfiguration für Bestellung ObjectPage (wird in Komponente mit i18n erstellt)
const createBestellungConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
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
          endpoint: '/api/partners?type=supplier',
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
          ] as any,
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
      onClick: () => console.log('Freigeben clicked')
    },
    {
      key: 'stornieren',
      label: t('crud.actions.cancel'),
      type: 'danger',
      onClick: () => console.log('Stornieren clicked')
    },
    {
      key: 'drucken',
      label: t('crud.actions.print'),
      type: 'secondary',
      onClick: () => {
        if (id || data?.nummer) {
          window.open(`/api/mcp/documents/purchase_order/${id || data.nummer}/print?locale=${sendLanguage}`, '_blank')
        }
      }
    },
    {
      key: 'senden',
      label: t('crud.actions.send'),
      type: 'secondary',
      onClick: () => {
        if (data?.lieferantId) {
          setSendRecipients([data.lieferantId])
          setSendDialogOpen(true)
        }
      },
      disabled: !data || data.status === 'ENTWURF' || data.status === 'STORNIERT'
    }
  ],
  api: {
    baseUrl: '/api/einkauf/bestellungen',
    endpoints: {
      list: '/api/einkauf/bestellungen',
      get: '/api/einkauf/bestellungen/{id}',
      create: '/api/einkauf/bestellungen',
      update: '/api/einkauf/bestellungen/{id}',
      delete: '/api/einkauf/bestellungen/{id}'
    }
  },
  validation: createBestellungSchema(t),
  permissions: ['einkauf.read', 'einkauf.write']
})

export default function BestellungStammPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const [stornoDialogOpen, setStornoDialogOpen] = useState(false)
  const [stornoReason, setStornoReason] = useState('')
  const [approvalRequired, setApprovalRequired] = useState(false)
  const [originalData, setOriginalData] = useState<any>(null)
  const [sendDialogOpen, setSendDialogOpen] = useState(false)
  const [sendMethod, setSendMethod] = useState<'email' | 'portal'>('email')
  const [sendLanguage, setSendLanguage] = useState<'de' | 'en'>('de')
  const [sendRecipients, setSendRecipients] = useState<string[]>([])
  const [sendMessage, setSendMessage] = useState('')
  const entityType = 'purchaseOrder'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Bestellung')
  const bestellungConfig = createBestellungConfig(t, entityTypeLabel)

  const { data, saveData } = useMaskData({
    apiUrl: bestellungConfig.api.baseUrl,
    id: id || undefined
  })

  // Audit Trail
  const { changeLogs, isLoading: isLoadingAudit, refetch: refetchAudit } = useCrudAuditTrail({
    entityType: 'purchaseOrder',
    entityId: id || '',
    fetchAuditTrail: async (entityType: string, entityId: string) => {
      const response = await apiClient.get(`/api/v1/audit/logs?entity_type=${entityType}&entity_id=${entityId}&limit=50`)
      return response.data.map((log: any) => ({
        id: log.id,
        timestamp: new Date(log.timestamp),
        action: log.action,
        user: log.user_email || log.user_id,
        changedFields: log.changes || {},
        reason: log.reason || '',
      }))
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

  const handleSave = async (formData: any) => {
    setLoading(true)
    try {
      // Prüfe ob Genehmigung erforderlich ist
      if (approvalRequired && formData.status !== 'ENTWURF') {
        // Erstelle Audit-Log für Änderung
        try {
          await apiClient.post('/api/v1/audit/log', {
            user_id: 'current-user', // TODO: Get from auth context
            user_email: 'user@example.com', // TODO: Get from auth context
            tenant_id: 'default', // TODO: Get from tenant context
            action: 'UPDATE',
            entity_type: 'purchaseOrder',
            entity_id: id || formData.id,
            changes: {
              before: originalData,
              after: formData,
            },
          })
        } catch (auditError) {
          console.warn('Audit-Log konnte nicht erstellt werden:', auditError)
        }
      }

      // Update mit Version-Incrementierung
      const updateData = {
        ...formData,
        version: (formData.version || 0) + 1,
      }

      await saveData(updateData)
      
      // Refresh Audit Trail
      if (id) {
        refetchAudit()
      }

      toast({
        title: t('crud.messages.updateSuccess', { entityType: entityTypeLabel }),
      })

      navigate('/einkauf/bestellungen-liste')
    } catch (error: any) {
      console.error(t('crud.messages.updateError', { entityType: entityTypeLabel }), error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.updateError', { entityType: entityTypeLabel }),
        description: error.response?.data?.detail || error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm(t('crud.messages.discardChanges'))) {
      navigate('/einkauf/bestellungen-liste')
    }
  }

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
      // Update Status auf STORNIERT
      const updateData = {
        ...data,
        status: 'STORNIERT',
        version: (data?.version || 0) + 1,
      }

      await saveData(updateData)

      // Erstelle Audit-Log für Storno
      try {
        await apiClient.post('/api/v1/audit/log', {
          user_id: 'current-user', // TODO: Get from auth context
          user_email: 'user@example.com', // TODO: Get from auth context
          tenant_id: 'default', // TODO: Get from tenant context
          action: 'CANCEL',
          entity_type: 'purchaseOrder',
          entity_id: id || data?.id,
          changes: {
            status: 'STORNIERT',
            reason: stornoReason,
          },
        })
      } catch (auditError) {
        console.warn('Audit-Log konnte nicht erstellt werden:', auditError)
      }

      toast({
        title: t('crud.messages.cancelSuccess', { entityType: entityTypeLabel }),
      })

      setStornoDialogOpen(false)
      setStornoReason('')
      navigate('/einkauf/bestellungen-liste')
    } catch (error: any) {
      console.error(t('crud.messages.cancelError', { entityType: entityTypeLabel }), error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.cancelError', { entityType: entityTypeLabel }),
        description: error.response?.data?.detail || error.message,
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

  return (
    <div className="space-y-6">
      <ObjectPage
        config={extendedConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
      />

      {/* Change-Log Panel (wenn ID vorhanden) */}
      {id && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5" />
              {t('crud.audit.title')}
              {data?.version && (
                <Badge variant="outline" className="ml-2">
                  {t('crud.fields.version')}: {data.version}
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
              <Select value={sendMethod} onValueChange={(value: 'email' | 'portal') => setSendMethod(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="email">{t('crud.fields.email')}</SelectItem>
                  <SelectItem value="portal">{t('crud.fields.portal')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>{t('crud.fields.language')}</Label>
              <Select value={sendLanguage} onValueChange={(value: 'de' | 'en') => setSendLanguage(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="de">{t('crud.fields.german')}</SelectItem>
                  <SelectItem value="en">{t('crud.fields.english')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {sendMethod === 'email' && (
              <div>
                <Label>{t('crud.fields.recipients')}</Label>
                <div className="space-y-2">
                  {data?.lieferant && (
                    <div className="flex items-center justify-between p-2 border rounded">
                      <span>{data.lieferant}</span>
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
                  
                  // Send PO via email or portal
                  await apiClient.post(`/api/einkauf/bestellungen/${poId}/send`, {
                    method: sendMethod,
                    language: sendLanguage,
                    recipients: sendRecipients,
                    message: sendMessage || undefined,
                  })

                  toast({
                    title: t('crud.messages.poSentSuccess'),
                    description: t('crud.messages.poSentToSupplier', { method: sendMethod === 'email' ? t('crud.fields.email') : t('crud.fields.portal') }),
                  })

                  setSendDialogOpen(false)
                  setSendMessage('')
                } catch (error: any) {
                  console.error('Fehler beim Versenden der PO:', error)
                  toast({
                    variant: 'destructive',
                    title: t('crud.messages.poSendError'),
                    description: error.message,
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