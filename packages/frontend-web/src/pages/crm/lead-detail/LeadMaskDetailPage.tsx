import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ObjectPage } from '@/components/mask-builder'
import { Button } from '@/components/ui/button'
import { Loader2, ArrowLeft, Trash2 } from 'lucide-react'
import { queryKeys, mutationKeys } from '@/lib/query'
import { crmService, type Lead } from '@/lib/services/crm-service'
import { useToast } from '@/components/ui/toast-provider'
import {
  LEAD_MASK_OBJECT_PAGE_CONFIG,
  mapLeadToMask,
  mapMaskToLead,
  type MaskLeadData,
  validateLeadPayload,
} from '@/features/crm-masks/lead-mask-support'
import { getSuccessMessage, getErrorMessage } from '@/features/crud/utils/i18n-helpers'

function LeadMaskDetailPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams()
  const queryClient = useQueryClient()
  const toast = useToast()
  const isNew = !id || id === 'neu'
  const leadId = !isNew ? id ?? '' : ''
  const entityType = 'lead'

  const { data: existingLead, isLoading, error } = useQuery({
    queryKey: queryKeys.crm.leads.detail(leadId),
    queryFn: () => crmService.getFunnelLead(leadId),
    enabled: Boolean(leadId),
  })

  const [maskData, setMaskData] = useState<MaskLeadData>(() => mapLeadToMask(null))
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    if (existingLead) {
      setMaskData(mapLeadToMask(existingLead))
    } else if (isNew) {
      setMaskData(mapLeadToMask(null))
    }
  }, [existingLead, isNew])

  const createMutation = useMutation({
    mutationKey: mutationKeys.crm.leads.create,
    mutationFn: (data: Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>) => crmService.createLead(data),
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'create', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.all })
      navigate('/crm/leads')
    },
    onError: (err) => {
      toast.push(getErrorMessage(t, 'create', entityType))
    },
  })

  const updateMutation = useMutation({
    mutationKey: mutationKeys.crm.leads.update,
    mutationFn: (data: Partial<Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>>) =>
      crmService.updateLead(leadId, data),
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'update', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.detail(leadId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.all })
    },
    onError: (err) => {
      toast.push(getErrorMessage(t, 'update', entityType))
    },
  })

  const deleteMutation = useMutation({
    mutationKey: mutationKeys.crm.leads.delete,
    mutationFn: () => crmService.deleteLead(leadId),
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'delete', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.all })
      navigate('/crm/leads')
    },
    onError: (err) => {
      toast.push(getErrorMessage(t, 'delete', entityType))
    },
  })

  const handleMaskSave = async (data: MaskLeadData): Promise<void> => {
    const payload = mapMaskToLead(data)
    const validationError = validateLeadPayload(payload)
    if (validationError) {
      setFormError(validationError)
      toast.push(validationError)
      return
    }

    setFormError(null)

    if (isNew) {
      await createMutation.mutateAsync(payload as Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>)
    } else {
      await updateMutation.mutateAsync(payload)
    }
  }

  const handleDelete = () => {
    if (!leadId) {
      return
    }
    if (window.confirm('Möchten Sie diesen Lead wirklich löschen?')) {
      deleteMutation.mutate()
    }
  }

  if (error) {
    return (
      <div className="p-6">
        <p className="text-sm text-destructive">Fehler beim Laden des Leads.</p>
      </div>
    )
  }

  if (isLoading && !isNew) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Lead wird geladen...</span>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground mb-1">CRM &gt; Leads</p>
          <h1 className="text-3xl font-bold">
            {existingLead?.company ?? (isNew ? 'Neuen Lead anlegen' : 'Lead bearbeiten')}
          </h1>
          <p className="text-muted-foreground">Mask Builder Formular (Beta)</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate(-1)} className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Zurück
          </Button>
          {!isNew && (
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Trash2 className="h-4 w-4" />
              )}
              Löschen
            </Button>
          )}
      </div>
    </div>

      {formError ? (
        <p className="text-sm text-destructive">{formError}</p>
      ) : null}

      <ObjectPage
        config={LEAD_MASK_OBJECT_PAGE_CONFIG}
        data={maskData}
        onChange={setMaskData}
        onSave={handleMaskSave}
        onCancel={() => navigate(-1)}
        isLoading={isLoading && !isNew}
      />
    </div>
  )
}

export default LeadMaskDetailPage
