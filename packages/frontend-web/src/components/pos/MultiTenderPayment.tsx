import { useState, type ReactNode } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { X, DollarSign, CreditCard, Gift } from 'lucide-react'

export type PaymentEntry = {
  id: string
  type: 'bar' | 'ec' | 'paypal' | 'gift_card'
  amount: number
  reference?: string // Gift Card-Nr oder EC-Beleg-Nr
}

interface MultiTenderPaymentProps {
  total: number
  onPaymentsChange: (payments: PaymentEntry[]) => void
}

export function MultiTenderPayment({ total, onPaymentsChange }: MultiTenderPaymentProps) {
  const [payments, setPayments] = useState<PaymentEntry[]>([])
  const [selectedType, setSelectedType] = useState<PaymentEntry['type'] | null>(null)
  const [amount, setAmount] = useState<number>(0)
  const [reference, setReference] = useState('')

  const paid = payments.reduce((sum, p) => sum + p.amount, 0)
  const remaining = total - paid

  const paymentTypeLabels: Record<PaymentEntry['type'], string> = {
    bar: 'Bar',
    ec: 'EC-Karte',
    paypal: 'PayPal',
    gift_card: 'Geschenkkarte',
  }

  const paymentTypeIcons: Record<PaymentEntry['type'], ReactNode> = {
    bar: <DollarSign className="h-4 w-4" />,
    ec: <CreditCard className="h-4 w-4" />,
    paypal: <CreditCard className="h-4 w-4" />,
    gift_card: <Gift className="h-4 w-4" />,
  }

  const handleAddPayment = (): void => {
    if (!selectedType || amount <= 0) return

    const newPayment: PaymentEntry = {
      id: `payment-${Date.now()}`,
      type: selectedType,
      amount: Math.min(amount, remaining), // Max. Restbetrag
      reference: reference || undefined,
    }

    const updatedPayments = [...payments, newPayment]
    setPayments(updatedPayments)
    onPaymentsChange(updatedPayments)

    // Reset
    setSelectedType(null)
    setAmount(0)
    setReference('')
  }

  const handleRemovePayment = (id: string): void => {
    const updatedPayments = payments.filter((p) => p.id !== id)
    setPayments(updatedPayments)
    onPaymentsChange(updatedPayments)
  }

  const handleQuickAmount = (quickAmount: number): void => {
    setAmount(Math.min(quickAmount, remaining))
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Teilzahlungen</span>
          {remaining > 0 ? (
            <Badge variant="destructive" className="text-lg">
              Offen: {remaining.toFixed(2)} €
            </Badge>
          ) : (
            <Badge variant="default" className="text-lg bg-green-600">
              ✅ Vollständig bezahlt
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Bisherige Zahlungen */}
        {payments.length > 0 && (
          <div className="space-y-2">
            <Label className="text-sm text-muted-foreground">Hinzugefügte Zahlungen</Label>
            {payments.map((payment) => (
              <div
                key={payment.id}
                className="flex items-center justify-between bg-muted p-3 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  {paymentTypeIcons[payment.type]}
                  <div>
                    <div className="font-semibold">{paymentTypeLabels[payment.type]}</div>
                    {payment.reference && (
                      <div className="text-xs text-muted-foreground">
                        Ref: {payment.reference}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-lg font-bold">{payment.amount.toFixed(2)} €</span>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleRemovePayment(payment.id)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Neue Zahlung hinzufügen */}
        {remaining > 0 && (
          <>
            <div>
              <Label className="text-sm font-semibold mb-2 block">
                Zahlungsart auswählen
              </Label>
              <div className="grid grid-cols-2 gap-2">
                <Button
                  size="lg"
                  variant={selectedType === 'bar' ? 'default' : 'outline'}
                  onClick={() => setSelectedType('bar')}
                  className="gap-2"
                >
                  <DollarSign className="h-5 w-5" />
                  Bar
                </Button>
                <Button
                  size="lg"
                  variant={selectedType === 'ec' ? 'default' : 'outline'}
                  onClick={() => setSelectedType('ec')}
                  className="gap-2"
                >
                  <CreditCard className="h-5 w-5" />
                  EC-Karte
                </Button>
                <Button
                  size="lg"
                  variant={selectedType === 'paypal' ? 'default' : 'outline'}
                  onClick={() => setSelectedType('paypal')}
                  className="gap-2"
                >
                  <CreditCard className="h-5 w-5" />
                  PayPal
                </Button>
                <Button
                  size="lg"
                  variant={selectedType === 'gift_card' ? 'default' : 'outline'}
                  onClick={() => setSelectedType('gift_card')}
                  className="gap-2"
                >
                  <Gift className="h-5 w-5" />
                  Geschenkkarte
                </Button>
              </div>
            </div>

            {selectedType && (
              <>
                <div>
                  <Label htmlFor="amount" className="text-sm font-semibold">
                    Betrag
                  </Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    min="0"
                    max={remaining}
                    value={amount || ''}
                    onChange={(e) => setAmount(Number(e.target.value))}
                    className="text-2xl font-mono h-14 text-center"
                    placeholder="0.00"
                    autoFocus
                  />
                </div>

                {/* Schnellauswahl */}
                <div className="grid grid-cols-4 gap-2">
                  {[5, 10, 20, 50].map((quickAmount) => (
                    <Button
                      key={quickAmount}
                      variant="outline"
                      onClick={() => handleQuickAmount(quickAmount)}
                      disabled={quickAmount > remaining}
                    >
                      {quickAmount} €
                    </Button>
                  ))}
                  <Button
                    variant="outline"
                    onClick={() => handleQuickAmount(remaining)}
                    className="col-span-2"
                  >
                    Restbetrag ({remaining.toFixed(2)} €)
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleQuickAmount(Math.ceil(remaining))}
                    className="col-span-2"
                  >
                    Aufrunden
                  </Button>
                </div>

                {/* Referenz (für Gift Card oder EC-Beleg) */}
                {(selectedType === 'gift_card' || selectedType === 'ec') && (
                  <div>
                    <Label htmlFor="reference" className="text-sm">
                      {selectedType === 'gift_card'
                        ? 'Geschenkkarten-Nummer'
                        : 'EC-Beleg-Nummer (optional)'}
                    </Label>
                    <Input
                      id="reference"
                      value={reference}
                      onChange={(e) => setReference(e.target.value)}
                      placeholder={
                        selectedType === 'gift_card'
                          ? 'GC-2025-000123'
                          : 'Optional'
                      }
                      className="font-mono"
                    />
                  </div>
                )}

                <Button
                  size="lg"
                  onClick={handleAddPayment}
                  disabled={amount <= 0 || amount > remaining}
                  className="w-full"
                >
                  Zahlung hinzufügen ({amount.toFixed(2)} €)
                </Button>
              </>
            )}
          </>
        )}

        {/* Zusammenfassung */}
        <div className="border-t pt-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Gesamt</span>
            <span className="font-semibold">{total.toFixed(2)} €</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Bereits bezahlt</span>
            <span className="font-semibold text-green-600">{paid.toFixed(2)} €</span>
          </div>
          <div className="flex justify-between text-lg font-bold">
            <span>Offen</span>
            <span className={remaining > 0 ? 'text-orange-600' : 'text-green-600'}>
              {remaining.toFixed(2)} €
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
