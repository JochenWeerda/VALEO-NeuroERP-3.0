import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
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
import { useCreateCustomer } from '@/lib/api/crm'

export default function KundeNeuMaskBuilderPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { mutateAsync: createCustomer } = useCreateCustomer()
  const [maskData, setMaskData] = useState<MaskCustomerData>(() => mapCustomerToMask(undefined))
  const [error, setError] = useState<string | null>(null)

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
      navigate('/verkauf/kunden-liste', { replace: true })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unbekannter Fehler beim Speichern.'
      setError(message)
    }
  }

  return (
    <div className="space-y-4 p-6">
      <ModuleToolbar backTarget="/verkauf/kunden-liste" closeTarget="/verkauf/kunden-liste" title="Neuer Kunde" />
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
        onCancel={() => navigate('/verkauf/kunden-liste')}
      />
    </div>
  )
}
