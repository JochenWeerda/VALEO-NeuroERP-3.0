import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Play, Trash2, Clock, User, ShoppingCart } from 'lucide-react'

type CartItem = {
  artikelnr: string
  bezeichnung: string
  ean: string
  preis: number
  menge: number
  image?: string
}

type SuspendedSale = {
  id: string
  timestamp: string
  cart: CartItem[]
  customerId?: string
  customerName?: string
  total: number
  itemCount: number
}

// Mock-Daten (später: API)
const mockSuspendedSales: SuspendedSale[] = [
  {
    id: 'SUSP-001',
    timestamp: '2025-10-11T14:23:00',
    cart: [
      { artikelnr: 'A-001', bezeichnung: 'Blumenerde 20L', ean: '4012345678901', preis: 12.99, menge: 2, image: '🌱' },
      { artikelnr: 'A-003', bezeichnung: 'Rasendünger 5kg', ean: '4012345678903', preis: 24.99, menge: 1, image: '🌿' },
    ],
    customerId: 'K-12345',
    customerName: 'Agrar Schmidt GmbH',
    total: 50.97,
    itemCount: 3,
  },
  {
    id: 'SUSP-002',
    timestamp: '2025-10-11T15:45:00',
    cart: [
      { artikelnr: 'A-005', bezeichnung: 'Blumentopf 30cm', ean: '4012345678905', preis: 8.99, menge: 5, image: '🪴' },
    ],
    total: 44.95,
    itemCount: 5,
  },
]

export default function SuspendedSalesPage(): JSX.Element {
  const navigate = useNavigate()
  const [sales, setSales] = useState<SuspendedSale[]>(mockSuspendedSales)

  const handleResume = (saleId: string): void => {
    // TODO: Load suspended sale into POS terminal
    // navigate('/pos/terminal', { state: { resumeSaleId: saleId } })
    
    alert(`Verkauf ${saleId} wird im POS-Terminal fortgesetzt`)
    
    // Sale aus Liste entfernen
    setSales(sales.filter(s => s.id !== saleId))
  }

  const handleDelete = (saleId: string): void => {
    if (!confirm('Pausierten Verkauf wirklich löschen?')) return
    
    setSales(sales.filter(s => s.id !== saleId))
  }

  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp)
    return new Intl.DateTimeFormat('de-DE', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  const getTimeSince = (timestamp: string): string => {
    const now = new Date().getTime()
    const then = new Date(timestamp).getTime()
    const diff = Math.floor((now - then) / 60000) // Minuten
    
    if (diff < 60) return `vor ${diff} Min.`
    if (diff < 1440) return `vor ${Math.floor(diff / 60)} Std.`
    return `vor ${Math.floor(diff / 1440)} Tagen`
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-primary text-primary-foreground p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Clock className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">Pausierte Verkäufe</h1>
            <p className="text-sm opacity-90">{sales.length} Verkäufe pausiert</p>
          </div>
        </div>
        <Button variant="secondary" onClick={() => navigate('/pos/terminal')}>
          Zurück zum POS
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 overflow-auto bg-gray-50">
        {sales.length === 0 ? (
          <Card className="p-12 text-center">
            <Clock className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
            <h2 className="text-xl font-semibold mb-2">Keine pausierten Verkäufe</h2>
            <p className="text-muted-foreground">
              Verkäufe können im POS-Terminal pausiert werden
            </p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {sales.map((sale) => (
              <Card key={sale.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-bold text-lg">{sale.id}</h3>
                        <Badge variant="secondary">{getTimeSince(sale.timestamp)}</Badge>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {formatTime(sale.timestamp)} Uhr
                      </div>
                    </div>
                  </div>

                  {/* Kunde */}
                  {sale.customerName && (
                    <div className="flex items-center gap-2 mb-4 text-sm">
                      <User className="h-4 w-4 text-muted-foreground" />
                      <span className="font-semibold">{sale.customerName}</span>
                    </div>
                  )}

                  {/* Artikel-Übersicht */}
                  <div className="space-y-2 mb-4">
                    {sale.cart.slice(0, 3).map((item, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-sm">
                        <span className="text-2xl">{item.image}</span>
                        <span className="flex-1 truncate">{item.bezeichnung}</span>
                        <span className="text-muted-foreground">×{item.menge}</span>
                      </div>
                    ))}
                    {sale.cart.length > 3 && (
                      <div className="text-xs text-muted-foreground text-center">
                        + {sale.cart.length - 3} weitere Artikel
                      </div>
                    )}
                  </div>

                  {/* Zusammenfassung */}
                  <div className="border-t pt-4 mb-4 space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground flex items-center gap-1">
                        <ShoppingCart className="h-4 w-4" />
                        Artikel
                      </span>
                      <span className="font-semibold">{sale.itemCount} Stück</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="font-semibold">Gesamt</span>
                      <span className="text-xl font-bold text-primary">
                        {sale.total.toFixed(2)} €
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="grid grid-cols-2 gap-2">
                    <Button
                      variant="default"
                      onClick={() => handleResume(sale.id)}
                      className="gap-2"
                    >
                      <Play className="h-4 w-4" />
                      Fortsetzen
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => handleDelete(sale.id)}
                      className="gap-2 text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                      Löschen
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
