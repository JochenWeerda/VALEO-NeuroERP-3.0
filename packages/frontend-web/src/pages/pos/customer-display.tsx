import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

type CartItem = {
  artikelnr: string
  bezeichnung: string
  ean: string
  preis: number
  menge: number
  image?: string
}

// WebSocket Sync with POS Terminal
const usePOSSync = (terminalId = 'terminal-1') => {
  const [cart, setCart] = useState<CartItem[]>([])
  const [total, setTotal] = useState(0)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    let ws: WebSocket
    let destroyed = false

    const connect = () => {
      if (destroyed) return
      ws = new WebSocket(`ws://localhost:8000/api/v1/ws/pos/${terminalId}`)
      ws.onopen = () => { if (!destroyed) setConnected(true) }
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data as string)
          if (!destroyed) { setCart(data.cart || []); setTotal(data.total || 0) }
        } catch { /* ignore malformed messages */ }
      }
      ws.onerror = () => { if (!destroyed) setConnected(false) }
      ws.onclose = () => {
        if (!destroyed) { setConnected(false); setTimeout(connect, 3000) }
      }
    }

    connect()
    return () => { destroyed = true; ws?.close() }
  }, [terminalId])

  return { cart, total, connected }
}

export default function CustomerDisplayPage(): JSX.Element {
  const { cart, total, connected } = usePOSSync()
  const [currentTime, setCurrentTime] = useState(() =>
    new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
  )
  useEffect(() => {
    const id = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }))
    }, 10000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-primary via-primary/90 to-primary/70 text-white overflow-hidden">
      {/* Header */}
      <div className="p-8 text-center border-b border-white/20">
        <h1 className="text-5xl font-bold mb-2">Willkommen bei VALERO</h1>
        <p className="text-2xl opacity-90">Haus & Gartenmarkt</p>
        <div className="mt-4 flex items-center justify-center gap-4">
          <span className="text-lg opacity-75">{currentTime} Uhr</span>
          <Badge variant={connected ? 'default' : 'secondary'} className="text-sm">
            {connected ? '🟢 Verbunden' : '⚪ Getrennt'}
          </Badge>
        </div>
      </div>

      {/* Artikel-Liste */}
      <div className="flex-1 p-8 overflow-auto">
        {cart.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <div className="text-8xl mb-6 opacity-50">🛒</div>
              <p className="text-3xl opacity-75">Ihr Warenkorb ist leer</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4 max-w-6xl mx-auto">
            {cart.map((item, idx) => (
              <Card
                key={idx}
                className="bg-white/20 backdrop-blur-lg border-white/30 hover:bg-white/30 transition-all"
              >
                <div className="p-6 flex items-center justify-between">
                  <div className="flex items-center gap-6">
                    <div className="text-7xl">{item.image}</div>
                    <div>
                      <div className="text-3xl font-semibold mb-2">{item.bezeichnung}</div>
                      <div className="text-xl opacity-90">
                        {item.menge} × {item.preis.toFixed(2)} €
                      </div>
                    </div>
                  </div>
                  <div className="text-5xl font-bold">
                    {(item.menge * item.preis).toFixed(2)} €
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Gesamt (fixiert unten) */}
      {cart.length > 0 && (
        <div className="bg-white/30 backdrop-blur-xl p-12 border-t border-white/30">
          <div className="max-w-6xl mx-auto flex justify-between items-center">
            <div className="flex items-center gap-4">
              <span className="text-4xl font-semibold">Gesamt</span>
              <Badge variant="secondary" className="text-xl px-4 py-2">
                {cart.reduce((sum, item) => sum + item.menge, 0)} Artikel
              </Badge>
            </div>
            <div className="text-7xl font-bold">
              {total.toFixed(2)} €
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="p-4 text-center text-sm opacity-50 border-t border-white/20">
        Vielen Dank für Ihren Einkauf! | VALERO Landhandel GmbH
      </div>
    </div>
  )
}
