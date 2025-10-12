import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'

interface ChangeCalculatorProps {
  total: number
  onTenderedChange?: (tendered: number) => void
}

export function ChangeCalculator({ total, onTenderedChange }: ChangeCalculatorProps) {
  const [tendered, setTendered] = useState<number>(0)
  const change = tendered - total

  const handleTenderedChange = (value: number): void => {
    setTendered(value)
    onTenderedChange?.(value)
  }

  const quickAmounts = [5, 10, 20, 50, 100, 200, 500]

  return (
    <Card className="border-2">
      <CardContent className="space-y-6 pt-6">
        {/* Zu zahlen */}
        <div>
          <Label className="text-sm text-muted-foreground">Zu zahlen</Label>
          <div className="text-4xl font-bold text-primary">
            {total.toFixed(2)} €
          </div>
        </div>

        {/* Gegeben */}
        <div>
          <Label htmlFor="tendered" className="text-sm font-semibold">
            Gegeben
          </Label>
          <Input
            id="tendered"
            type="number"
            step="0.01"
            min="0"
            value={tendered || ''}
            onChange={(e) => handleTenderedChange(Number(e.target.value))}
            className="text-3xl font-mono h-16 text-center"
            placeholder="0.00"
            autoFocus
          />
        </div>

        {/* Schnellauswahl */}
        <div>
          <Label className="text-sm text-muted-foreground mb-2 block">
            Schnellauswahl
          </Label>
          <div className="grid grid-cols-4 gap-2">
            {quickAmounts.map((amount) => (
              <Button
                key={amount}
                variant="outline"
                size="lg"
                onClick={() => handleTenderedChange(amount)}
                className="h-16 text-xl font-semibold"
              >
                {amount} €
              </Button>
            ))}
            <Button
              variant="outline"
              size="lg"
              onClick={() => handleTenderedChange(Math.ceil(total))}
              className="h-16 text-lg font-semibold"
            >
              Passend
            </Button>
          </div>
        </div>

        {/* Wechselgeld */}
        {tendered > 0 && (
          <div
            className={`p-6 rounded-lg transition-colors ${
              change >= 0
                ? 'bg-green-50 border-2 border-green-200'
                : 'bg-red-50 border-2 border-red-200'
            }`}
          >
            <Label className="text-sm text-muted-foreground">
              {change >= 0 ? 'Wechselgeld' : 'Fehlbetrag'}
            </Label>
            <div
              className={`text-5xl font-bold ${
                change >= 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {Math.abs(change).toFixed(2)} €
            </div>
            {change < 0 && (
              <p className="text-sm text-red-600 mt-2">
                Noch {Math.abs(change).toFixed(2)} € fehlen
              </p>
            )}
          </div>
        )}

        {/* Info: Exact change */}
        {change === 0 && tendered > 0 && (
          <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-200 text-center">
            <p className="text-blue-700 font-semibold">✅ Passend bezahlt</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
