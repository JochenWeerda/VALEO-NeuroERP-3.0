import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { CreditCard, DollarSign, FileText, Scan, ShoppingCart, Smartphone } from 'lucide-react'

type CartItem = {
  artikelnr: string
  bezeichnung: string
  ean: string
  preis: number
  menge: number
  image?: string
}

type PaymentMethod = 'bar' | 'ec' | 'paypal' | 'b2b'

export default function POSTerminalPage(): JSX.Element {
  const [cart, setCart] = useState<CartItem[]>([])
  const [barcode, setBarcode] = useState('')
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod | null>(null)
  const [customerId, setCustomerId] = useState<string | null>(null)

  // Mock-Artikel-Datenbank
  const articles = [
    { artikelnr: 'A-1001', bezeichnung: 'Blumenerde 20L', ean: '4012345678901', preis: 12.99, image: '🌱' },
    { artikelnr: 'A-1002', bezeichnung: 'Tomatensamen', ean: '4012345678902', preis: 2.99, image: '🍅' },
    { artikelnr: 'A-1003', bezeichnung: 'Rasendünger 5kg', ean: '4012345678903', preis: 24.99, image: '🌿' },
    { artikelnr: 'A-1004', bezeichnung: 'Gartenschere', ean: '4012345678904', preis: 19.99, image: '✂️' },
    { artikelnr: 'A-1005', bezeichnung: 'Blumentopf 30cm', ean: '4012345678905', preis: 8.99, image: '🪴' },
    { artikelnr: 'A-1006', bezeichnung: 'Gießkanne 10L', ean: '4012345678906', preis: 14.99, image: '💧' },
  ]

  function handleBarcodeInput(ean: string): void {
    const article = articles.find((a) => a.ean === ean)
    if (article) {
      addToCart(article)
      setBarcode('')
    }
  }

  function addToCart(article: typeof articles[0]): void {
    const existing = cart.find((item) => item.ean === article.ean)
    if (existing) {
      setCart(cart.map((item) => (item.ean === article.ean ? { ...item, menge: item.menge + 1 } : item)))
    } else {
      setCart([...cart, { ...article, menge: 1 }])
    }
  }

  function removeFromCart(ean: string): void {
    setCart(cart.filter((item) => item.ean !== ean))
  }

  function updateQuantity(ean: string, menge: number): void {
    if (menge <= 0) {
      removeFromCart(ean)
    } else {
      setCart(cart.map((item) => (item.ean === ean ? { ...item, menge } : item)))
    }
  }

  async function handleCheckout(): Promise<void> {
    if (!paymentMethod) return

    const total = cart.reduce((sum, item) => sum + item.preis * item.menge, 0)

    // Mock TSE-Signierung
    const tseSignature = {
      transactionNumber: Math.floor(Math.random() * 10000),
      signature: `TSE_SIG_${  Date.now()}`,
      timestamp: new Date().toISOString(),
      qrCode: 'V0;VALERO-POS;fiskaly-TSS-12345;...',
    }

    console.log('Checkout:', {
      cart,
      paymentMethod,
      customerId,
      total,
      tse: tseSignature,
    })

    // Mock: Kassenladen öffnen (Serial-Signal)
    if (paymentMethod === 'bar') {
      console.log('🔓 Kassenladen geöffnet')
    }

    // Mock: EC-Terminal
    if (paymentMethod === 'ec') {
      console.log('💳 EC-Terminal: Betrag', total.toFixed(2), '€')
    }

    // Mock: Bon drucken mit TSE
    console.log('🧾 Bon gedruckt mit TSE-Signatur:', tseSignature)

    alert(`Zahlung erfolgreich!\n\nBetrag: ${total.toFixed(2)} €\nZahlungsart: ${paymentMethod}\nTSE-Nr: ${tseSignature.transactionNumber}`)

    // Reset
    setCart([])
    setPaymentMethod(null)
    setCustomerId(null)
  }

  const total = cart.reduce((sum, item) => sum + item.preis * item.menge, 0)

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-primary text-primary-foreground p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ShoppingCart className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">VALERO POS</h1>
            <p className="text-sm opacity-90">Haus & Gartenmarkt</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Badge variant="secondary" className="text-lg px-4 py-2">
            {customerId ? `B2B: ${customerId}` : 'B2C'}
          </Badge>
          <Badge variant="outline" className="text-sm">
            TSE: ✅ Online
          </Badge>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Warenkorb (Links) */}
        <div className="w-1/3 p-4 border-r bg-white flex flex-col">
          <h2 className="text-xl font-bold mb-4">Warenkorb</h2>

          <div className="flex-1 overflow-auto space-y-2">
            {cart.map((item) => (
              <Card key={item.ean}>
                <CardContent className="p-3">
                  <div className="flex items-center gap-3">
                    <div className="text-4xl">{item.image}</div>
                    <div className="flex-1">
                      <div className="font-semibold">{item.bezeichnung}</div>
                      <div className="text-sm text-muted-foreground">{item.preis.toFixed(2)} €</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button size="sm" variant="outline" onClick={() => updateQuantity(item.ean, item.menge - 1)}>
                        −
                      </Button>
                      <span className="w-8 text-center font-bold">{item.menge}</span>
                      <Button size="sm" variant="outline" onClick={() => updateQuantity(item.ean, item.menge + 1)}>
                        +
                      </Button>
                    </div>
                    <Button size="sm" variant="destructive" onClick={() => removeFromCart(item.ean)}>
                      ✕
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Gesamt */}
          <div className="mt-4 p-4 bg-primary text-primary-foreground rounded-lg">
            <div className="flex justify-between items-center">
              <span className="text-xl font-semibold">Gesamt</span>
              <span className="text-3xl font-bold">{total.toFixed(2)} €</span>
            </div>
          </div>

          {/* Zahlungsarten */}
          <div className="mt-4 grid grid-cols-2 gap-2">
            <Button
              size="lg"
              variant={paymentMethod === 'bar' ? 'default' : 'outline'}
              onClick={() => setPaymentMethod('bar')}
              className="gap-2"
            >
              <DollarSign className="h-5 w-5" />
              Bar
            </Button>
            <Button
              size="lg"
              variant={paymentMethod === 'ec' ? 'default' : 'outline'}
              onClick={() => setPaymentMethod('ec')}
              className="gap-2"
            >
              <CreditCard className="h-5 w-5" />
              EC-Karte
            </Button>
            <Button
              size="lg"
              variant={paymentMethod === 'paypal' ? 'default' : 'outline'}
              onClick={() => setPaymentMethod('paypal')}
              className="gap-2"
            >
              <Smartphone className="h-5 w-5" />
              PayPal
            </Button>
            <Button
              size="lg"
              variant={paymentMethod === 'b2b' ? 'default' : 'outline'}
              onClick={() => setPaymentMethod('b2b')}
              className="gap-2"
            >
              <FileText className="h-5 w-5" />
              B2B-Beleg
            </Button>
          </div>

          <Button
            size="lg"
            className="mt-4 w-full text-lg"
            disabled={cart.length === 0 || !paymentMethod}
            onClick={handleCheckout}
          >
            Bezahlen ({total.toFixed(2)} €)
          </Button>
        </div>

        {/* Artikelauswahl (Rechts) */}
        <div className="flex-1 p-4 flex flex-col">
          <h2 className="text-xl font-bold mb-4">Artikel</h2>

          {/* Barcode-Scanner */}
          <div className="mb-4">
            <div className="relative">
              <Scan className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                placeholder="Barcode scannen oder eingeben..."
                value={barcode}
                onChange={(e) => setBarcode(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleBarcodeInput(barcode)
                }}
                className="pl-10 text-lg"
                autoFocus
              />
            </div>
          </div>

          {/* Artikel-Grid (Touch-optimiert) */}
          <div className="grid grid-cols-3 gap-4 overflow-auto">
            {articles.map((article) => (
              <Card
                key={article.ean}
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => addToCart(article)}
              >
                <CardContent className="p-6 text-center">
                  <div className="text-6xl mb-3">{article.image}</div>
                  <div className="font-semibold mb-1">{article.bezeichnung}</div>
                  <div className="text-2xl font-bold text-primary">{article.preis.toFixed(2)} €</div>
                  <div className="text-xs text-muted-foreground mt-1 font-mono">{article.artikelnr}</div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
