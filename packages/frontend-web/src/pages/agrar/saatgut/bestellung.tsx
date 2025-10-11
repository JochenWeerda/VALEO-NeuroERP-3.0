import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useSubmitSeedOrder } from '@/features/agrar/hooks'
import { type SeedOrderItem, type SeedOrderPayload } from '@/features/agrar/types'
import { useToast } from '@/hooks/use-toast'

const ISO_DATE_LENGTH = 10

const createInitialOrder = (): SeedOrderPayload => ({
  customer: 'Landhandel Nord GmbH',
  season: 'Herbst 2024',
  deliveryDate: new Date().toISOString().slice(0, ISO_DATE_LENGTH),
  paymentTerms: '14 Tage netto',
  notes: '',
  items: [
    {
      productId: 'SEED-00123',
      productName: 'Falkenstein Premium',
      quantityKg: 2500,
      pricePerKg: 3.9,
    },
    {
      productId: 'FERT-2007',
      productName: 'NPK 12-12-17 Premium',
      quantityKg: 1200,
      pricePerKg: 0.82,
    },
  ],
})

const calculateTotal = (items: SeedOrderItem[]): number => {
  return items.reduce((sum, item) => sum + item.quantityKg * item.pricePerKg, 0)
}

export default function SeedOrderWizardPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [order, setOrder] = useState<SeedOrderPayload>(createInitialOrder)
  const mutation = useSubmitSeedOrder()

  const updateGeneralField = (field: keyof SeedOrderPayload, value: string): void => {
    setOrder((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const updateItemQuantity = (productId: string, quantityKg: number): void => {
    setOrder((prev) => ({
      ...prev,
      items: prev.items.map((item) =>
        item.productId === productId ? { ...item, quantityKg: Math.max(0, quantityKg) } : item,
      ),
    }))
  }


  const steps = useMemo(
    () => [
      {
        id: 'general',
        title: 'Allgemein',
        description: 'Kunden- und Saisonangaben definieren.',
        content: (
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="customer">Kunde</Label>
              <Input
                id="customer"
                value={order.customer}
                onChange={(event) => updateGeneralField('customer', event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="season">Saison</Label>
              <Input
                id="season"
                value={order.season}
                onChange={(event) => updateGeneralField('season', event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="deliveryDate">Lieferdatum</Label>
              <Input
                id="deliveryDate"
                type="date"
                value={order.deliveryDate}
                onChange={(event) => updateGeneralField('deliveryDate', event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="paymentTerms">Zahlungsziel</Label>
              <Input
                id="paymentTerms"
                value={order.paymentTerms}
                onChange={(event) => updateGeneralField('paymentTerms', event.target.value)}
              />
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="notes">Notizen</Label>
              <Textarea
                id="notes"
                value={order.notes ?? ''}
                onChange={(event) => updateGeneralField('notes', event.target.value)}
                placeholder="Optionale Hinweise fuer Logistik oder Vertrieb"
                rows={4}
              />
            </div>
          </div>
        ),
      },
      {
        id: 'items',
        title: 'Positionen',
        description: 'Mengen und Produkte pruefen.',
        content: (
          <div className="space-y-4">
            {order.items.map((item) => (
              <div key={item.productId} className="rounded border bg-muted/40 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold">{item.productName}</p>
                    <p className="text-xs text-muted-foreground">{item.productId}</p>
                  </div>
                  <div className="w-40 space-y-2">
                    <Label htmlFor={`qty-${item.productId}`}>Menge (kg)</Label>
                    <Input
                      id={`qty-${item.productId}`}
                      type="number"
                      min={0}
                      value={item.quantityKg}
                      onChange={(event) => updateItemQuantity(item.productId, Number(event.target.value))}
                    />
                  </div>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">
                  Preis: {item.pricePerKg.toLocaleString('de-DE', { minimumFractionDigits: 2 })} EUR/kg
                </p>
              </div>
            ))}
          </div>
        ),
      },
      {
        id: 'review',
        title: 'Pruefung',
        description: 'Zusammenfassung kontrollieren und abschliessen.',
        content: (
          <div className="space-y-4 text-sm">
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <p className="text-xs text-muted-foreground">Kunde</p>
                <p className="font-medium">{order.customer}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Lieferdatum</p>
                <p className="font-medium">
                  {order.deliveryDate && order.deliveryDate.length > 0
                    ? new Date(order.deliveryDate).toLocaleDateString('de-DE')
                    : '-'}
                </p>
              </div>
            </div>
            <div className="rounded border border-dashed p-4">
              <p className="text-xs text-muted-foreground">Gesamtbetrag</p>
              <p className="text-2xl font-semibold">
                {calculateTotal(order.items).toLocaleString('de-DE', {
                  style: 'currency',
                  currency: 'EUR',
                })}
              </p>
            </div>
          </div>
        ),
      },
    ],
    [order],
  )

  const handleFinish = (): void => {
    mutation.mutate(order, {
      onSuccess: (result) => {
        toast({
          title: 'Bestellung angelegt',
          description: `Auftrag ${result.orderId} wurde gespeichert.`,
        })
        navigate('/agrar/saatgut/stamm?id=SEED-00123')
      },
      onError: () => {
        toast({
          title: 'Fehler beim Speichern',
          description: 'Bitte spaeter erneut versuchen.',
          variant: 'destructive',
        })
      },
    })
  }

  return (
    <Wizard
      title="Saatgut-Bestellung anlegen"
      subtitle="Mehrstufiger Prozess fuer Saatgut und Duenger"
      steps={steps}
      onCancel={() => navigate('/agrar/saatgut/liste')}
      onFinish={handleFinish}
      loading={mutation.isPending}
      mcpContext={{
        process: 'agrar-seed-order',
        entityType: 'seed-order',
      }}
    />
  )
}
