import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from '@/app/routing/typed-router'
import { ObjectPage } from '@/components/mask-builder'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useToast } from '@/hooks/use-toast'
import {
  CUSTOMER_MASK_OBJECT_PAGE_CONFIG,
  validateCustomerPayload,
} from '@/features/crm-masks/customer-mask-support'
import {
  getNested,
  mapCustomerToMask,
  mapMaskToCustomer,
  type MaskCustomerData,
} from '@/features/crm-masks/mappers'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useCustomer, useUpdateCustomer } from '@/lib/api/crm'
import { Loader2, ArrowLeft } from 'lucide-react'

function CustomerMaskEditPage(): JSX.Element {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { toast } = useToast()
  const { data: customer, isLoading, error } = useCustomer(id ?? '')
  const updateCustomer = useUpdateCustomer()
  const [maskData, setMaskData] = useState<MaskCustomerData | null>(null)
  const [formError, setFormError] = useState<string | null>(null)
  const editMaskConfig = useMemo(
    () => ({
      ...CUSTOMER_MASK_OBJECT_PAGE_CONFIG,
      title: 'Kundenstamm bearbeiten',
    }),
    [],
  )

  useEffect(() => {
    if (customer) {
      setMaskData(mapCustomerToMask(customer))
    }
  }, [customer])

  const handleMaskSave = async (data: MaskCustomerData): Promise<void> => {
    if (!id) {
      setFormError('Keine Kunden-ID angegeben.')
      return
    }

    const payload = mapMaskToCustomer(data)
    const validationError = validateCustomerPayload(payload)
    if (validationError) {
      setFormError(validationError)
      return
    }

    setFormError(null)

    try {
      await updateCustomer.mutateAsync({ id, data: payload })
      setMaskData(data)
      const customerNumber = getNested<string>(payload, 'customer.customer_number') ?? ''
      const customerName = getNested<string>(payload, 'customer.name1') ?? ''
      toast({
        title: 'Kunde aktualisiert',
        description: `${customerName || 'Kunde'} (${customerNumber}) wurde erfolgreich gespeichert.`,
      })
    } catch (err) {
      setFormError(getAxiosErrorMessage(err))
    }
  }

  if (!id) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTitle>Keine Kunden-ID</AlertTitle>
          <AlertDescription>Bitte rufen Sie die Seite mit einer gültigen Kunden-ID auf.</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (error) {
    const message = getAxiosErrorMessage(error)
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTitle>Fehler</AlertTitle>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (isLoading || !maskData) {
    return (
      <div className="flex items-center justify-center p-10">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="ml-2 text-sm text-muted-foreground">Kundenmaske wird geladen…</span>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground mb-1">CRM &gt; Kunden</p>
          <h1 className="text-3xl font-bold">{customer?.name ?? 'Kundenstamm bearbeiten'}</h1>
          <p className="text-muted-foreground">Mask Builder Formular (Beta)</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate(-1)} className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Zurück
          </Button>
        </div>
      </div>

      {formError ? (
        <Alert variant="destructive">
          <AlertTitle>Speichern fehlgeschlagen</AlertTitle>
          <AlertDescription>{formError}</AlertDescription>
        </Alert>
      ) : null}

      {customer?.business_partner_id ? (
        <Alert className="border-amber-300 bg-amber-50">
          <AlertTitle>Verkaufs-Stammdaten</AlertTitle>
          <AlertDescription>
            Dieser CRM-Kunde ist mit einem Business-Partner verknüpft. Für die kanonische Pflege (Chef-Anweisungen,
            Tab 21–25) den{' '}
            <Link
              to={`/verkauf/kunden-stamm/${customer.business_partner_id}`}
              className="font-medium underline underline-offset-2"
            >
              Kundenstamm (Verkauf)
            </Link>{' '}
            öffnen.
          </AlertDescription>
        </Alert>
      ) : null}

      <ObjectPage
        config={editMaskConfig}
        data={maskData}
        onChange={setMaskData}
        onSave={handleMaskSave}
        onCancel={() => navigate(-1)}
      />
    </div>
  )
}

export default CustomerMaskEditPage
