import { FormEvent, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader2, Save } from 'lucide-react'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { NativeSelect } from '@/components/ui/native-select'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useToast } from '@/hooks/use-toast'
import { type CustomerCreate, useCreateCustomer } from '@/lib/api/crm'

type FormState = {
  customer_number: string
  name: string
  email: string
  phone: string
  address: string
  tax_id: string
  payment_terms: string
  credit_limit: string
  is_active: 'true' | 'false'
}

const DEFAULT_STATE: FormState = {
  customer_number: '',
  name: '',
  email: '',
  phone: '',
  address: '',
  tax_id: '',
  payment_terms: '30',
  credit_limit: '',
  is_active: 'true',
}

function generateDefaultCustomerNumber(): string {
  const year = new Date().getFullYear()
  const seq = Date.now().toString(36).toUpperCase().slice(-4)
  return `K-${year}-${seq}`
}


export default function LegacyKundeNeuPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { mutateAsync: createCustomer, isPending } = useCreateCustomer()
  const [formState, setFormState] = useState<FormState>(() => ({
    ...DEFAULT_STATE,
    customer_number: generateDefaultCustomerNumber(),
  }))
  const [error, setError] = useState<string | null>(null)

  const paymentOptions = useMemo(() => ['7', '14', '30', '45', '60', '90'], [])

  function updateField<T extends keyof FormState>(field: T, value: FormState[T]): void {
    setFormState((prev) => ({ ...prev, [field]: value }))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    const payload: CustomerCreate = {
      customer_number: formState.customer_number.trim(),
      name: formState.name.trim(),
      email: formState.email.trim() || undefined,
      phone: formState.phone.trim() || undefined,
      address: formState.address.trim() || undefined,
      tax_id: formState.tax_id.trim() || undefined,
      payment_terms: Number(formState.payment_terms) || 30,
      credit_limit: formState.credit_limit ? Number(formState.credit_limit) : undefined,
      is_active: formState.is_active === 'true',
    }

    if (!payload.customer_number || !payload.name) {
      setError('Bitte Pflichtfelder ausf?llen.')
      return
    }
    setError(null)

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
    <div className="p-6 space-y-6">
      <ModuleToolbar backTarget="/verkauf/kunden-liste" closeTarget="/verkauf/kunden-liste" title="Neuer Kunde" />
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground mb-1">Vertrieb &gt; Kunden</p>
          <h1 className="text-3xl font-bold">Neuen Kunden anlegen</h1>
          <p className="text-muted-foreground">Pflege Stammdaten und Zahlungsinformationen fuer einen neuen Geschaeftspartner.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate(-1)} className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Zurueck
          </Button>
          <Button type="submit" form="create-customer-form" disabled={isPending} className="gap-2">
            {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            Speichern
          </Button>
        </div>
      </div>

      {error ? (
        <Alert variant="destructive">
          <AlertTitle>Speichern fehlgeschlagen</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}

      <form id="create-customer-form" className="space-y-6" onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Stammdaten</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <Label htmlFor="customer_number">Kundennummer *</Label>
                <Input id="customer_number" value={formState.customer_number} onChange={(event) => updateField('customer_number', event.target.value)} placeholder="z. B. K-2025-001" required />
              </div>
              <div>
                <Label htmlFor="name">Firmenname *</Label>
                <Input id="name" value={formState.name} onChange={(event) => updateField('name', event.target.value)} placeholder="Landhandel Nord GmbH" required />
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <Label htmlFor="email">E-Mail</Label>
                <Input id="email" type="email" value={formState.email} onChange={(event) => updateField('email', event.target.value)} placeholder="kontakt@kunde.de" />
              </div>
              <div>
                <Label htmlFor="phone">Telefon</Label>
                <Input id="phone" type="tel" value={formState.phone} onChange={(event) => updateField('phone', event.target.value)} placeholder="+49 123 456789" />
              </div>
            </div>
            <div>
              <Label htmlFor="address">Adresse</Label>
              <Textarea id="address" value={formState.address} onChange={(event) => updateField('address', event.target.value)} placeholder="Strasse, PLZ Ort" rows={3} />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <Label htmlFor="tax_id">USt-IdNr.</Label>
                <Input id="tax_id" value={formState.tax_id} onChange={(event) => updateField('tax_id', event.target.value)} placeholder="DE123456789" />
              </div>
              <div>
                <Label htmlFor="status">Status</Label>
                <NativeSelect value={formState.is_active} onValueChange={(value) => updateField('is_active', value as 'true' | 'false')} placeholder="Status waehlen" options={[{ value: 'true', label: 'Aktiv' }, { value: 'false', label: 'Inaktiv' }]} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Zahlung &amp; Konditionen</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <div>
              <Label htmlFor="payment_terms">Zahlungsziel (Tage)</Label>
              <NativeSelect value={formState.payment_terms} onValueChange={(value) => updateField('payment_terms', value)} placeholder="Zahlungsziel auswaehlen" options={paymentOptions.map((option) => ({ value: option, label: `${option} Tage` }))} />
            </div>
            <div>
              <Label htmlFor="credit_limit">Kreditlimit (EUR)</Label>
              <Input id="credit_limit" type="number" min="0" value={formState.credit_limit} onChange={(event) => updateField('credit_limit', event.target.value)} placeholder="z. B. 25000" />
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}
