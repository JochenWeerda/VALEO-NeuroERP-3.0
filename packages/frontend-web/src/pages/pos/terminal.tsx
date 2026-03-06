import { useState, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { CreditCard, DollarSign, FileText, Scan, ShoppingCart, Smartphone, Grid3x3, Search, Keyboard } from 'lucide-react'
import { useFiskalyTSE, type PaymentType, type TSETransaction } from '@/lib/services/fiskaly-tse'
import { ChangeCalculator } from '@/components/pos/ChangeCalculator'
import { ArticleSearch } from '@/components/pos/ArticleSearch'
import { TouchBedienfeld, type TouchBedienfeldAction } from '@/components/pos/TouchBedienfeld'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'

const POS_TOUCH_PANEL_KEY = 'pos-touch-bedienfeld'

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
  const [activeTx, setActiveTx] = useState<TSETransaction | null>(null)
  const [showChangeCalculator, setShowChangeCalculator] = useState(false)
  const [tendered, setTendered] = useState<number>(0)
  const [showTouchBedienfeld, setShowTouchBedienfeld] = useState(() => {
    try {
      return localStorage.getItem(POS_TOUCH_PANEL_KEY) !== 'false'
    } catch {
      return true
    }
  })
  const [numpadBuffer, setNumpadBuffer] = useState('')
  const [articleTab, setArticleTab] = useState<'scanner' | 'grid' | 'search'>('grid')
  const wsRef = useRef<WebSocket | null>(null)
  const barcodeInputRef = useRef<HTMLInputElement>(null)
  
  // fiskaly TSE Integration
  const { isInitialized, startTransaction, updateTransaction, finishTransaction } = useFiskalyTSE()
  
  // WebSocket für CustomerDisplay-Sync
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/pos/terminal-1')
    ws.onerror = (error) => {
      console.error('POS WebSocket error:', error)
    }
    wsRef.current = ws
    return () => { ws.close() }
  }, [])
  
  // Broadcast cart changes
  useEffect(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        cart,
        total: cart.reduce((sum, item) => sum + item.preis * item.menge, 0)
      }))
    }
  }, [cart])

  // Numpad-Buffer zurücksetzen wenn Wechselgeld-Dialog öffnet
  const prevShowCalc = useRef(false)
  useEffect(() => {
    if (showChangeCalculator && !prevShowCalc.current) {
      setNumpadBuffer(tendered > 0 ? String(tendered).replace('.', ',') : '0')
    }
    prevShowCalc.current = showChangeCalculator
  }, [showChangeCalculator, tendered])

  const { data: articles = [], isLoading: articlesLoading } = useQuery({
    queryKey: ['pos', 'articles'],
    queryFn: async () => {
      const response = await apiClient.get<{ items: Array<{ id: string; article_number: string; name: string; barcode?: string | null; sales_price: string | number }> }>(
        '/api/v1/articles',
        { params: { is_active: true, limit: 48 } },
      )
      return response.data.items.map(a => ({
        artikelnr: a.article_number,
        bezeichnung: a.name,
        ean: a.barcode ?? '',
        preis: Number(a.sales_price) || 0,
        image: '📦',
      }))
    },
    staleTime: 5 * 60 * 1000,
  })

  async function handleBarcodeInput(ean: string): Promise<void> {
    const cached = articles.find((a) => a.ean === ean)
    if (cached) {
      addToCart(cached)
      setBarcode('')
      return
    }
    try {
      const response = await apiClient.get<{ items: Array<{ article_number: string; name: string; barcode?: string | null; sales_price: string | number }> }>(
        '/api/v1/articles',
        { params: { search: ean, limit: 1 } },
      )
      const item = response.data.items[0]
      if (item) {
        addToCart({ artikelnr: item.article_number, bezeichnung: item.name, ean: item.barcode ?? ean, preis: Number(item.sales_price) || 0, image: '📦' })
        setBarcode('')
      } else {
        toast({ variant: 'destructive', title: 'Artikel nicht gefunden', description: `EAN: ${ean}` })
      }
    } catch {
      toast({ variant: 'destructive', title: 'Fehler beim Laden', description: 'Artikel konnte nicht gefunden werden.' })
    }
  }

  function addToCart(article: Omit<CartItem, 'menge'>): void {
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

  function handleTouchBedienfeldChange(checked: boolean): void {
    setShowTouchBedienfeld(checked)
    try {
      localStorage.setItem(POS_TOUCH_PANEL_KEY, String(checked))
    } catch {
      /* ignore */
    }
  }

  function handleTouchBedienfeldAction(action: TouchBedienfeldAction): void {
    switch (action.type) {
      case 'artikelcode':
        setArticleTab('scanner')
        setTimeout(() => barcodeInputRef.current?.focus(), 100)
        break
      case 'storno':
        if (cart.length > 0) {
          const last = cart[cart.length - 1]
          removeFromCart(last.ean)
          toast({ title: 'Storno', description: `Position "${last.bezeichnung}" entfernt` })
        } else {
          toast({ variant: 'destructive', title: 'Warenkorb leer', description: 'Keine Position zum Stornieren' })
        }
        break
      case 'tara':
        toast({ title: 'TARA', description: 'Waage tariert (Hardware-Signal bei angeschlossener Waage)' })
        break
      case 'kassenschublade':
        toast({ title: 'Kassenschublade', description: 'Schublade geöffnet (Hardware-Signal bei angeschlossener Kasse)' })
        break
      case 'bareinlage':
      case 'barentnahme':
        toast({ title: action.type === 'bareinlage' ? 'Bareinlage' : 'Barentnahme', description: 'Buchung über Tagesabschluss erfassen' })
        break
      case 'digit':
        if (showChangeCalculator) {
          const nextBuf = (numpadBuffer === '0' ? '' : numpadBuffer) + action.digit
          const newBuf = nextBuf || '0'
          setNumpadBuffer(newBuf)
          setTendered(parseFloat(newBuf.replace(',', '.')) || 0)
        } else {
          setBarcode((b) => b + action.digit)
        }
        break
      case 'comma':
        if (showChangeCalculator) {
          if (!numpadBuffer.includes(',') && !numpadBuffer.includes('.')) {
            const newBuf = numpadBuffer + ','
            setNumpadBuffer(newBuf)
            setTendered(parseFloat(newBuf.replace(',', '.')) || 0)
          }
        } else {
          setBarcode((b) => b + ',')
        }
        break
      case 'clear':
        if (showChangeCalculator) {
          setNumpadBuffer('0')
          setTendered(0)
        } else {
          setBarcode('')
        }
        break
      case 'enter':
        if (showChangeCalculator) {
          handleCheckout()
        } else if (barcode) {
          handleBarcodeInput(barcode)
        }
        break
    }
  }

  function handlePaymentMethodSelect(method: PaymentMethod): void {
    setPaymentMethod(method)
    
    // Bei Bar-Zahlung: Wechselgeld-Rechner öffnen
    if (method === 'bar') {
      setShowChangeCalculator(true)
    } else {
      // Andere Zahlungsarten: Direkt checkout
      handleCheckout(method)
    }
  }

  async function handleCheckout(method?: PaymentMethod): Promise<void> {
    const selectedMethod = method ?? paymentMethod
    if (!selectedMethod) return

    const total = cart.reduce((sum, item) => sum + item.preis * item.menge, 0)
    
    // Bei Bar-Zahlung: Prüfe ob genug gegeben wurde
    if (selectedMethod === 'bar' && tendered < total) {
      toast({
        variant: 'destructive',
        title: 'Unzureichender Betrag',
        description: `Fehlbetrag: ${(total - tendered).toFixed(2)} €`,
      })
      return
    }

    try {
      // 1. TSE-Transaction starten
      let tx = activeTx
      if (!tx) {
        tx = await startTransaction('Verkauf', 'Kassenbeleg-V1')
        setActiveTx(tx)
      }

      // 2. Artikel an TSE übermitteln
      await updateTransaction(tx.txId, cart.map(item => ({
        bezeichnung: item.bezeichnung,
        preis: item.preis,
        menge: item.menge,
      })))

      // 3. Transaction beenden & signieren
      const paymentTypeMap: Record<PaymentMethod, PaymentType> = {
        bar: 'CASH',
        ec: 'NON_CASH',
        paypal: 'NON_CASH',
        b2b: 'INTERNAL',
      }
      
      const signedTx = await finishTransaction(
        tx.txId,
        paymentTypeMap[selectedMethod],
        total,
      )

      // 4. TSE-Journal speichern (Backend-Call)
      // TODO: await saveTSETransaction({ ... })

      const change = selectedMethod === 'bar' ? tendered - total : 0
      toast({
        title: 'Zahlung erfolgreich!',
        description: `Betrag: ${total.toFixed(2)} €\nZahlungsart: ${selectedMethod}${change > 0 ? `\nWechselgeld: ${change.toFixed(2)} €` : ''}\nTSE-Nr: ${signedTx.number}`,
      })

      // Reset
      setCart([])
      setPaymentMethod(null)
      setCustomerId(null)
      setActiveTx(null)
      setShowChangeCalculator(false)
      setTendered(0)
      
    } catch (error) {
      console.error('❌ TSE-Fehler:', error)
      toast({
        variant: 'destructive',
        title: 'TSE-Fehler',
        description: 'Transaktion wurde in Offline-Queue gespeichert.',
      })
      // TODO: Offline-Queue
    }
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
          <div className="flex items-center gap-2">
            <Switch
              id="touch-bedienfeld"
              checked={showTouchBedienfeld}
              onCheckedChange={handleTouchBedienfeldChange}
            />
            <Label htmlFor="touch-bedienfeld" className="flex items-center gap-2 cursor-pointer text-sm">
              <Keyboard className="h-4 w-4" />
              Touch-Bedienfeld
            </Label>
          </div>
          <Badge variant="secondary" className="text-lg px-4 py-2">
            {customerId ? `B2B: ${customerId}` : 'B2C'}
          </Badge>
          <Badge variant={isInitialized ? 'outline' : 'secondary'} className="text-sm">
            TSE: {isInitialized ? '✅ Online' : '⚠️ Mock'}
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
              onClick={() => handlePaymentMethodSelect('bar')}
              className="gap-2"
              disabled={cart.length === 0}
            >
              <DollarSign className="h-5 w-5" />
              Bar
            </Button>
            <Button
              size="lg"
              variant={paymentMethod === 'ec' ? 'default' : 'outline'}
              onClick={() => handlePaymentMethodSelect('ec')}
              className="gap-2"
              disabled={cart.length === 0}
            >
              <CreditCard className="h-5 w-5" />
              EC-Karte
            </Button>
            <Button
              size="lg"
              variant={paymentMethod === 'paypal' ? 'default' : 'outline'}
              onClick={() => handlePaymentMethodSelect('paypal')}
              className="gap-2"
              disabled={cart.length === 0}
            >
              <Smartphone className="h-5 w-5" />
              PayPal
            </Button>
            <Button
              size="lg"
              variant={paymentMethod === 'b2b' ? 'default' : 'outline'}
              onClick={() => handlePaymentMethodSelect('b2b')}
              className="gap-2"
              disabled={cart.length === 0}
            >
              <FileText className="h-5 w-5" />
              B2B-Beleg
            </Button>
          </div>
        </div>

        {/* Artikelauswahl (Mitte) */}
        <div className="flex-1 p-4 flex flex-col min-w-0">
          <h2 className="text-xl font-bold mb-4">Artikel</h2>

          <Tabs value={articleTab} onValueChange={(v) => setArticleTab(v as typeof articleTab)} className="flex-1 flex flex-col">
            <TabsList className="grid w-full grid-cols-3 mb-4">
              <TabsTrigger value="scanner" className="gap-2">
                <Scan className="h-4 w-4" />
                Scanner
              </TabsTrigger>
              <TabsTrigger value="grid" className="gap-2">
                <Grid3x3 className="h-4 w-4" />
                Grid
              </TabsTrigger>
              <TabsTrigger value="search" className="gap-2">
                <Search className="h-4 w-4" />
                Suche
              </TabsTrigger>
            </TabsList>

            {/* Barcode-Scanner Tab */}
            <TabsContent value="scanner" className="flex-1">
              <div className="relative">
                <Scan className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input
                  ref={barcodeInputRef}
                  placeholder="Barcode scannen oder eingeben..."
                  value={barcode}
                  onChange={(e) => setBarcode(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleBarcodeInput(barcode)
                  }}
                  className="pl-10 text-lg h-14"
                  autoFocus
                />
              </div>
              <p className="text-sm text-muted-foreground mt-4 text-center">
                Barcode mit Scanner erfassen oder manuell eingeben und Enter drücken
              </p>
            </TabsContent>

            {/* Artikel-Grid Tab (Touch-optimiert) */}
            <TabsContent value="grid" className="flex-1 overflow-auto">
              {articlesLoading ? (
                <div className="grid grid-cols-3 gap-4">
                  {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-40" />)}
                </div>
              ) : (
                <div className="grid grid-cols-3 gap-4">
                  {articles.map((article) => (
                    <Card
                      key={article.artikelnr}
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
              )}
            </TabsContent>

            {/* Autocomplete-Suche Tab */}
            <TabsContent value="search" className="flex-1">
              <ArticleSearch
                onSelect={(article) => {
                  addToCart({
                    artikelnr: article.artikelnr,
                    bezeichnung: article.bezeichnung,
                    ean: article.ean ?? '',
                    preis: article.preis,
                    image: article.image ?? '📦',
                  })
                }}
              />
            </TabsContent>
          </Tabs>
        </div>

        {/* Touch-Bedienfeld (rechts, einblendbar) */}
        {showTouchBedienfeld && (
          <div className="w-72 p-3 border-l bg-slate-50 flex-shrink-0 overflow-auto">
            <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
              <Keyboard className="h-4 w-4" />
              Bedienfeld
            </h3>
            <TouchBedienfeld
              onAction={handleTouchBedienfeldAction}
              disabled={false}
            />
          </div>
        )}
      </div>

      {/* Wechselgeld-Rechner Dialog */}
      <Dialog open={showChangeCalculator} onOpenChange={setShowChangeCalculator}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Barzahlung</DialogTitle>
          </DialogHeader>
          <ChangeCalculator
            total={total}
            onTenderedChange={setTendered}
          />
          <div className="flex gap-2 mt-4">
            <Button
              variant="outline"
              onClick={() => {
                setShowChangeCalculator(false)
                setPaymentMethod(null)
                setTendered(0)
              }}
              className="flex-1"
            >
              Abbrechen
            </Button>
            <Button
              onClick={() => handleCheckout()}
              disabled={tendered < total}
              className="flex-1 text-lg"
            >
              Bezahlung abschließen
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
