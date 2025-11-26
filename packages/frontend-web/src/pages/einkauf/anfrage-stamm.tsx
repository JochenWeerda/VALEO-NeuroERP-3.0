import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { CheckCircle, XCircle, ShoppingCart, AlertTriangle, Send, Mail } from 'lucide-react'
import { Checkbox } from '@/components/ui/checkbox'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

// Zod-Schema für Anfrage (wird in Komponente mit i18n erstellt)
const createAnfrageSchema = (t: any) => z.object({
  anfrageNummer: z.string().min(1, t('crud.messages.validationError')),
  typ: z.enum(['BANF', 'ANF']),
  anforderer: z.string().min(1, t('crud.messages.validationError')),
  artikel: z.string().min(1, t('crud.messages.validationError')),
  menge: z.number().min(0.1, t('crud.messages.validationError')),
  einheit: z.string().min(1, t('crud.messages.validationError')),
  prioritaet: z.enum(['niedrig', 'normal', 'hoch', 'dringend']),
  faelligkeit: z.string().min(1, t('crud.messages.validationError')),
  status: z.enum(['ENTWURF', 'FREIGEGEBEN', 'ANGEBOTSPHASE', 'BESTELLT', 'ABGELEHNT']),
  begruendung: z.string().min(1, t('crud.messages.validationError')),
  kostenstelle: z.string().optional(),
  projekt: z.string().optional(),
  bemerkungen: z.string().optional()
})

// Konfiguration für Anfrage ObjectPage (wird in Komponente mit i18n erstellt)
const createAnfrageConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.actions.create'),
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'anfrageNummer',
          label: t('crud.fields.number'),
          type: 'text',
          required: true,
          readonly: true
        },
        {
          name: 'typ',
          label: t('crud.fields.type'),
          type: 'select',
          required: true,
          options: [
            { value: 'BANF', label: t('crud.entities.purchaseRequest') + ' (BANF)' },
            { value: 'ANF', label: t('crud.entities.purchaseRequest') + ' (ANF)' }
          ]
        },
        {
          name: 'anforderer',
          label: t('crud.fields.requestedBy'),
          type: 'text',
          required: true
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'ENTWURF', label: t('status.draft') },
            { value: 'FREIGEGEBEN', label: t('status.approved') },
            { value: 'ANGEBOTSPHASE', label: t('status.pending') },
            { value: 'BESTELLT', label: t('status.completed') },
            { value: 'ABGELEHNT', label: t('status.rejected') }
          ],
          readonly: true // Status wird nur über Actions geändert
        }
      ]
    },
    {
      key: 'bedarf',
      label: t('crud.fields.requirement'),
      fields: [
        {
          name: 'artikel',
          label: t('crud.fields.product'),
          type: 'lookup',
          required: true,
          endpoint: '/api/articles',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'menge',
          label: t('crud.fields.quantity'),
          type: 'number',
          required: true
        },
        {
          name: 'einheit',
          label: t('crud.fields.unit'),
          type: 'select',
          required: true,
          options: [
            { value: 'kg', label: 'kg' },
            { value: 't', label: 't' },
            { value: 'l', label: 'l' },
            { value: 'Stk', label: 'Stk' }
          ]
        },
        {
          name: 'prioritaet',
          label: t('crud.fields.priority'),
          type: 'select',
          required: true,
          options: [
            { value: 'niedrig', label: t('crud.fields.priorityLow') },
            { value: 'normal', label: t('crud.fields.priorityNormal') },
            { value: 'hoch', label: t('crud.fields.priorityHigh') },
            { value: 'dringend', label: t('crud.fields.priorityUrgent') }
          ]
        },
        {
          name: 'faelligkeit',
          label: t('crud.fields.dueDate'),
          type: 'date',
          required: true
        }
      ]
    },
    {
      key: 'details',
      label: t('crud.detail.additionalInfo'),
      fields: [
        {
          name: 'begruendung',
          label: t('crud.fields.reason'),
          type: 'textarea',
          required: true,
          placeholder: t('crud.tooltips.placeholders.reason')
        },
        {
          name: 'kostenstelle',
          label: t('crud.fields.costCenter'),
          type: 'lookup',
          endpoint: '/api/cost-centers',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'projekt',
          label: t('crud.fields.project'),
          type: 'lookup',
          endpoint: '/api/projects',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'bemerkungen',
          label: t('crud.fields.notes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.notes')
        }
      ]
    }
  ],
  actions: [], // Actions werden in Komponente implementiert
  api: {
    baseUrl: '/api/einkauf/anfragen',
    endpoints: {
      list: '/api/einkauf/anfragen',
      get: '/api/einkauf/anfragen/{id}',
      create: '/api/einkauf/anfragen',
      update: '/api/einkauf/anfragen/{id}',
      delete: '/api/einkauf/anfragen/{id}'
    }
  },
  validation: createAnfrageSchema(t),
  permissions: ['einkauf.read', 'einkauf.write']
})

export default function AnfrageStammPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const [approveDialogOpen, setApproveDialogOpen] = useState(false)
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false)
  const [rejectReason, setRejectReason] = useState('')
  const [convertDialogOpen, setConvertDialogOpen] = useState(false)
  const [sendRfqDialogOpen, setSendRfqDialogOpen] = useState(false)
  const [selectedSuppliers, setSelectedSuppliers] = useState<string[]>([])
  const [availableSuppliers, setAvailableSuppliers] = useState<any[]>([])
  const [sendMethod, setSendMethod] = useState<'email' | 'portal'>('email')
  const entityType = 'purchaseRequest'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Anfrage')
  const anfrageConfig = createAnfrageConfig(t, entityTypeLabel)

  const { data, saveData, refetch } = useMaskData({
    apiUrl: anfrageConfig.api.baseUrl,
    id: id || undefined
  })

  // Lade verfügbare Lieferanten
  useEffect(() => {
    const loadSuppliers = async () => {
      try {
        const response = await fetch('/api/partners?type=supplier')
        if (response.ok) {
          const suppliers = await response.json()
          setAvailableSuppliers(suppliers.data || suppliers || [])
        }
      } catch (error) {
        console.error('Fehler beim Laden der Lieferanten:', error)
      }
    }
    if (sendRfqDialogOpen) {
      loadSuppliers()
    }
  }, [sendRfqDialogOpen])

  const handleSave = async (formData: any) => {
    setLoading(true)
    try {
      // Status-Transition validieren
      if (data && formData.status !== data.status) {
        const allowedTransitions: Record<string, string[]> = {
          'ENTWURF': ['FREIGEGEBEN'],
          'FREIGEGEBEN': ['ANGEBOTSPHASE', 'BESTELLT', 'ABGELEHNT'],
          'ANGEBOTSPHASE': ['BESTELLT', 'ABGELEHNT'],
          'BESTELLT': [],
          'ABGELEHNT': [],
        }

        const allowed = allowedTransitions[data.status] || []
        if (!allowed.includes(formData.status)) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.validationError'),
            description: `Ungültiger Status-Übergang: ${data.status} → ${formData.status}`,
          })
          setLoading(false)
          return
        }
      }

      await saveData(formData)
      toast({
        title: t('crud.messages.updateSuccess', { entityType: entityTypeLabel }),
      })
      navigate('/einkauf/anfragen')
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
      navigate('/einkauf/anfragen')
    }
  }

  const handleApprove = async () => {
    if (!data || !id) return

    setLoading(true)
    try {
      const updateData = {
        ...data,
        status: 'FREIGEGEBEN',
      }

      await saveData(updateData)

      toast({
        title: t('crud.messages.approveSuccess', { entityType: entityTypeLabel }),
        description: 'Die Anfrage wurde freigegeben',
      })

      setApproveDialogOpen(false)
      refetch()
    } catch (error: any) {
      console.error('Fehler beim Freigeben:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.approveError', { entityType: entityTypeLabel }),
        description: error.response?.data?.detail || error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleReject = async () => {
    if (!rejectReason || rejectReason.length < 10) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.messages.reasonMinLength'),
      })
      return
    }

    if (!data || !id) return

    setLoading(true)
    try {
      const updateData = {
        ...data,
        status: 'ABGELEHNT',
        ablehnungsgrund: rejectReason,
      }

      await saveData(updateData)

      toast({
        title: t('crud.messages.cancelSuccess', { entityType: entityTypeLabel }),
        description: 'Die Anfrage wurde abgelehnt',
      })

      setRejectDialogOpen(false)
      setRejectReason('')
      refetch()
    } catch (error: any) {
      console.error('Fehler beim Ablehnen:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.cancelError', { entityType: entityTypeLabel }),
        description: error.response?.data?.detail || error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleConvertToOrder = async () => {
    if (!data || !id) return

    setLoading(true)
    try {
      // Update Status auf BESTELLT
      const updateData = {
        ...data,
        status: 'BESTELLT',
      }

      await saveData(updateData)

      // Navigate to create PO from requisition
      navigate(`/einkauf/bestellung-anlegen?requisitionId=${id}`)

      toast({
        title: t('crud.messages.createSuccess', { entityType: entityTypeLabel }),
        description: 'Bitte vervollständigen Sie die Bestellung',
      })

      setConvertDialogOpen(false)
    } catch (error: any) {
      console.error('Fehler beim Umwandeln:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.createError', { entityType: entityTypeLabel }),
        description: error.response?.data?.detail || error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSendRfq = async () => {
    if (!data || !id || selectedSuppliers.length === 0) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.messages.selectAtLeastOneSupplier'),
      })
      return
    }

    setLoading(true)
    try {
      // Update Status auf ANGEBOTSPHASE
      const updateData = {
        ...data,
        status: 'ANGEBOTSPHASE',
      }

      await saveData(updateData)

      // Send RFQ to suppliers
      const sendResponse = await fetch(`/api/einkauf/anfragen/${id}/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          supplierIds: selectedSuppliers,
          method: sendMethod,
        }),
      })

      if (!sendResponse.ok) {
        throw new Error(await sendResponse.text())
      }

      toast({
        title: t('crud.messages.rfqSentSuccess'),
        description: t('crud.messages.rfqSentToSuppliers', { count: selectedSuppliers.length }),
      })

      setSendRfqDialogOpen(false)
      setSelectedSuppliers([])
      refetch()
    } catch (error: any) {
      console.error('Fehler beim Versenden der RFQ:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.rfqSendError'),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const canApprove = data?.status === 'ENTWURF'
  const canReject = data?.status === 'ENTWURF' || data?.status === 'FREIGEGEBEN'
  const canConvert = data?.status === 'FREIGEGEBEN' || data?.status === 'ANGEBOTSPHASE'
  const canSendRfq = data?.status === 'FREIGEGEBEN'

  return (
    <div className="space-y-6">
      <ObjectPage
        config={anfrageConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
      />

      {/* Action Buttons */}
      {id && data && (
        <div className="fixed bottom-6 right-6 flex flex-col gap-2">
          {canApprove && (
            <Button
              onClick={() => setApproveDialogOpen(true)}
              className="shadow-lg"
              size="lg"
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              {t('crud.actions.approve')}
            </Button>
          )}
          {canReject && (
            <Button
              variant="destructive"
              onClick={() => setRejectDialogOpen(true)}
              className="shadow-lg"
              size="lg"
            >
              <XCircle className="h-4 w-4 mr-2" />
              {t('crud.actions.reject')}
            </Button>
          )}
          {canSendRfq && (
            <Button
              variant="default"
              onClick={() => setSendRfqDialogOpen(true)}
              className="shadow-lg"
              size="lg"
            >
              <Send className="h-4 w-4 mr-2" />
              {t('crud.actions.sendRfq')}
            </Button>
          )}
          {canConvert && (
            <Button
              variant="default"
              onClick={() => setConvertDialogOpen(true)}
              className="shadow-lg"
              size="lg"
            >
              <ShoppingCart className="h-4 w-4 mr-2" />
              {t('crud.actions.convertToOrder')}
            </Button>
          )}
        </div>
      )}

      {/* Approve Dialog */}
      <Dialog open={approveDialogOpen} onOpenChange={setApproveDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('crud.actions.approve')}</DialogTitle>
            <DialogDescription>
              Möchten Sie diese Anfrage wirklich freigeben?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setApproveDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button onClick={handleApprove} disabled={loading}>
              {loading ? t('common.loading') : t('crud.actions.approve')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog open={rejectDialogOpen} onOpenChange={setRejectDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('crud.actions.reject')}</DialogTitle>
            <DialogDescription>
              Bitte geben Sie einen Grund für die Ablehnung an (mindestens 10 Zeichen).
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="rejectReason">{t('crud.dialogs.cancel.reasonRequired')}</Label>
              <Textarea
                id="rejectReason"
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder={t('crud.dialogs.cancel.reasonPlaceholder')}
                required
                minLength={10}
                rows={4}
              />
              <p className="text-sm text-muted-foreground mt-1">
                {t('crud.dialogs.cancel.reasonMinLength')}
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRejectDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button
              variant="destructive"
              onClick={handleReject}
              disabled={loading || rejectReason.length < 10}
            >
              {loading ? t('common.loading') : t('crud.actions.reject')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Convert to Order Dialog */}
      <Dialog open={convertDialogOpen} onOpenChange={setConvertDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('crud.actions.convertToOrder')}</DialogTitle>
            <DialogDescription>
              Möchten Sie aus dieser Anfrage eine Bestellung erstellen?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConvertDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button onClick={handleConvertToOrder} disabled={loading}>
              {loading ? t('common.loading') : t('crud.actions.convertToOrder')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Send RFQ Dialog */}
      <Dialog open={sendRfqDialogOpen} onOpenChange={setSendRfqDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{t('crud.actions.sendRfq')}</DialogTitle>
            <DialogDescription>
              {t('crud.dialogs.sendRfq.description')}
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
              <Label>{t('crud.fields.selectSuppliers')}</Label>
              <div className="border rounded-md p-4 max-h-64 overflow-y-auto space-y-2">
                {availableSuppliers.length === 0 ? (
                  <p className="text-sm text-muted-foreground">{t('crud.messages.noSuppliersAvailable')}</p>
                ) : (
                  availableSuppliers.map((supplier) => (
                    <div key={supplier.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={`supplier-${supplier.id}`}
                        checked={selectedSuppliers.includes(supplier.id)}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setSelectedSuppliers([...selectedSuppliers, supplier.id])
                          } else {
                            setSelectedSuppliers(selectedSuppliers.filter((id) => id !== supplier.id))
                          }
                        }}
                      />
                      <Label
                        htmlFor={`supplier-${supplier.id}`}
                        className="flex-1 cursor-pointer"
                      >
                        {supplier.name || supplier.legalName || supplier.id}
                        {supplier.email && (
                          <span className="text-sm text-muted-foreground ml-2">
                            ({supplier.email})
                          </span>
                        )}
                      </Label>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSendRfqDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button
              onClick={handleSendRfq}
              disabled={loading || selectedSuppliers.length === 0}
            >
              {loading ? t('common.loading') : (
                <>
                  <Mail className="h-4 w-4 mr-2" />
                  {t('crud.actions.sendRfq')}
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}