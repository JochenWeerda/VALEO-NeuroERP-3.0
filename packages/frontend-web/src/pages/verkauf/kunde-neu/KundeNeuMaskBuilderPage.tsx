import { useMemo, useState } from 'react'
import { useLocation, useNavigate } from '@/app/routing/react-router-compat'
import { ObjectPage } from '@/components/mask-builder'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useToast } from '@/hooks/use-toast'
import {
  type MaskCustomerData,
  mapCustomerToMask,
  mapMaskToCustomer,
} from '@/features/crm-masks/mappers'
import {
  CUSTOMER_MASK_OBJECT_PAGE_CONFIG,
  validateCustomerPayload,
} from '@/features/crm-masks/customer-mask-support'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useCreateCustomer } from '@/lib/api/crm'

function buildReturnHref(returnTo: string, created: { id: string; name?: string; customer_number?: string }): string {
  const [path, existingQuery = ''] = returnTo.split('?')
  const params = new URLSearchParams(existingQuery)
  params.set('newCustomerId', created.id)
  if (created.name) params.set('newCustomerName', created.name)
  if (created.customer_number) params.set('newCustomerNumber', created.customer_number)
  params.set('openNewInstance', '1')
  return `${path}?${params.toString()}`
}

export default function KundeNeuMaskBuilderPage(): JSX.Element {
  const navigate = useNavigate()
  const location = useLocation()
  const { toast } = useToast()
  const { mutateAsync: createCustomer } = useCreateCustomer()

  const urlParams = useMemo(() => new URLSearchParams(location.search), [location.search])
  const returnTo = urlParams.get('returnTo') || ''
  const initialName = urlParams.get('initialName') || ''

  const [maskData, setMaskData] = useState<MaskCustomerData>(() => {
    const base = mapCustomerToMask(undefined)
    if (initialName) {
      return { ...base, customer: { ...(base.customer ?? {}), name1: initialName } }
    }
    return base
  })
  const [error, setError] = useState<string | null>(null)

  const cancelTarget = returnTo || '/verkauf/kunden-liste'

  async function handleMaskSave(data: MaskCustomerData): Promise<void> {
    setError(null)
    const payload = mapMaskToCustomer(data)
    const validationError = validateCustomerPayload(payload)
    if (validationError) {
      setError(validationError)
      return
    }

    try {
      const created = await createCustomer(payload)
      toast({
        title: 'Kunde angelegt',
        description: `${created.name} (${created.customer_number}) wurde erfolgreich erstellt.`,
      })
      if (returnTo) {
        navigate(buildReturnHref(returnTo, created), { replace: true })
        return
      }
      navigate('/verkauf/kunden-liste', { replace: true })
    } catch (err) {
      setError(getAxiosErrorMessage(err))
    }
  }

  return (
    <div className="space-y-4 p-6">
      <ModuleToolbar backTarget={cancelTarget} closeTarget={cancelTarget} title="Neuer Kunde" />
      {error ? (
        <Alert variant="destructive">
          <AlertTitle>Speichern fehlgeschlagen</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}
      <ObjectPage
        config={CUSTOMER_MASK_OBJECT_PAGE_CONFIG}
        data={maskData}
        onChange={setMaskData}
        onSave={handleMaskSave}
        onCancel={() => navigate(cancelTarget)}
      />
    </div>
  )
}
