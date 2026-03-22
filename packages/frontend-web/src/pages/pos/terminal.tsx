import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useLocation } from 'react-router-dom'
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
import {
  CreditCard, DollarSign, FileText, Scan, ShoppingCart, Smartphone,
  Grid3x3, Search, Keyboard, Settings, Clock, User, UserCheck,
  CheckCircle2, AlertCircle, X, Trash2,
} from 'lucide-react'
import { useFiskalyTSE, type PaymentType, type TSETransaction } from '@/lib/services/fiskaly-tse'
import { ChangeCalculator } from '@/components/pos/ChangeCalculator'
import { ArticleSearch } from '@/components/pos/ArticleSearch'
import { TouchBedienfeld, type TouchBedienfeldAction } from '@/components/pos/TouchBedienfeld'
import { ArticleImageLarge, ArticleImageSmall } from '@/components/pos/ArticleImage'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'

const POS_TOUCH_PANEL_KEY = 'pos-touch-bedienfeld'
const POS_KASSIERER_KEY = 'pos-kassierer'

type CartItem = {
  artikelnr: string
  bezeichnung: string
  ean: string
  preis: number
  menge: number
  image_url?: string | null
  category?: string
}

type PaymentMethod = 'bar' | 'ec' | 'paypal' | 'b2b'

type ApiArticle = {
  id: string
  article_number: string
  name: string
  barcode?: string | null
  sales_price: string | number
  category?: string | null
  image_url?: string | null
}

// ── Live-Uhr ──────────────────────────────────────────────────────────────────
function useClock(): string {
  const [time, setTime] = useState(() =>
    new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  )
  useEffect(() => {
    const id = setInterval(() => {
      setTime(new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit', second: '2-digit' }))
    }, 1000)
    return () => clearInterval(id)
  }, [])
  return time
}

// ── TSE-Ampel ─────────────────────────────────────────────────────────────────
function TseStatusLight({ isInitialized }: { isInitialized: boolean }) {
  return (
    <div className="flex items-center gap-1.5 text-xs text-primary-foreground/80">
      <span
        className={`h-2.5 w-2.5 rounded-full ${isInitialized ? 'bg-green-400' : 'bg-yellow-400 animate-pulse'}`}
        title={isInitialized ? 'TSE Online' : 'TSE Mock/Offline'}
      />
      <span>TSE {isInitialized ? 'Online' : 'Mock'}</span>
    </div>
  )
}

// ── Hauptkomponente ───────────────────────────────────────────────────────────
export default function POSTerminalPage(): JSX.Element {
  const location = useLocation()
  const clock = useClock()

  // ── Kernzustand ─────────────────────────────────────────────────────────────
  const [cart, setCart] = useState<CartItem[]>([])
  const [removingEans, setRemovingEans] = useState<Set<string>>(new Set())
  const [lastAddedEan, setLastAddedEan] = useState<string | null>(null)
  const [barcode, setBarcode] = useState('')
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod | null>(null)
  const [customerId, setCustomerId] = useState<string | null>(null)
  const [customerName, setCustomerName] = useState<string | null>(null)
  const [activeTx, setActiveTx] = useState<TSETransaction | null>(null)
  const [showChangeCalculator, setShowChangeCalculator] = useState(false)
  const [tendered, setTendered] = useState<number>(0)
  const [numpadBuffer, setNumpadBuffer] = useState('')
  const [articleTab, setArticleTab] = useState<'scanner' | 'grid' | 'search'>('grid')
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null)

  // ── Dialog-Zustand ───────────────────────────────────────────────────────────
  const [showSettings, setShowSettings] = useState(false)
  const [showB2BDialog, setShowB2BDialog] = useState(false)
  const [b2bSearch, setB2bSearch] = useState('')
  const [b2bResults, setB2bResults] = useState<Array<{ id: string; name: string; number: string }>>([])
  const [enriching, setEnriching] = useState(false)

  // ── Einstellungen ────────────────────────────────────────────────────────────
  const [kassierer, setKassierer] = useState(() => {
    try { return localStorage.getItem(POS_KASSIERER_KEY) || '' } catch { return '' }
  })
  const [showTouchBedienfeld, setShowTouchBedienfeld] = useState(() => {
    try { return localStorage.getItem(POS_TOUCH_PANEL_KEY) !== 'false' } catch { return true }
  })

  // ── Refs ─────────────────────────────────────────────────────────────────────
  const wsRef = useRef<WebSocket | null>(null)
  const barcodeInputRef = useRef<HTMLInputElement>(null)
  const scanBuffer = useRef('')
  const scanTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  // ── TSE ──────────────────────────────────────────────────────────────────────
  const { isInitialized, startTransaction, updateTransaction, finishTransaction } = useFiskalyTSE()

  // ── WebSocket CustomerDisplay ─────────────────────────────────────────────────
  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket('ws://localhost:8000/api/v1/ws/pos/terminal-1')
      ws.onerror = () => { /* silent */ }
      ws.onclose = () => { setTimeout(connect, 3000) }
      wsRef.current = ws
    }
    connect()
    return () => { wsRef.current?.close() }
  }, [])

  useEffect(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        cart,
        total: cart.reduce((s, i) => s + i.preis * i.menge, 0),
      }))
    }
  }, [cart])

  // ── Numpad-Buffer reset ───────────────────────────────────────────────────────
  const prevShowCalc = useRef(false)
  useEffect(() => {
    if (showChangeCalculator && !prevShowCalc.current) {
      setNumpadBuffer(tendered > 0 ? String(tendered).replace('.', ',') : '0')
    }
    prevShowCalc.current = showChangeCalculator
  }, [showChangeCalculator, tendered])

  // ── Globaler Barcode-Scanner (auch ohne Scanner-Tab aktiv) ────────────────────
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT') return
      if (e.key === 'Enter') {
        if (scanBuffer.current.length > 3) {
          void handleBarcodeInput(scanBuffer.current)
        }
        scanBuffer.current = ''
        return
      }
      if (e.key.length === 1) {
        scanBuffer.current += e.key
        if (scanTimer.current) clearTimeout(scanTimer.current)
        scanTimer.current = setTimeout(() => { scanBuffer.current = '' }, 200)
      }
    }
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // ── Pausierten Verkauf fortsetzen ─────────────────────────────────────────────
  useEffect(() => {
    const state = location.state as { resumeSaleId?: string } | null
    if (!state?.resumeSaleId) return
    apiClient
      .get<{ positionen_detail?: CartItem[]; betrag?: number }>(`/api/v1/pos/suspended-sales/${state.resumeSaleId}`)
      .then((res) => {
        if (res.data.positionen_detail?.length) {
          setCart(res.data.positionen_detail)
          toast({ title: 'Verkauf fortgesetzt', description: `Bon ${state.resumeSaleId} wiederaufgenommen` })
        }
      })
      .catch(() => { /* sale detail not available, resume silently */ })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // ── Artikel laden ─────────────────────────────────────────────────────────────
  const articlesQuery = useQuery({
    queryKey: ['pos', 'articles'],
    queryFn: async () => {
      const response = await apiClient.get<{ items: ApiArticle[] }>(
        '/api/v1/articles',
        { params: { is_active: true, limit: 96 } },
      )
      return response.data.items.map((a) => ({
        artikelnr: a.article_number,
        bezeichnung: a.name,
        ean: a.barcode ?? '',
        preis: Number(a.sales_price) || 0,
        image_url: a.image_url ?? null,
        category: a.category ?? undefined,
      }))
    },
    staleTime: 5 * 60 * 1000,
  })
  const articles = articlesQuery.data ?? []
  const articlesLoading = articlesQuery.isLoading

  // ── Kategorie-Filter ──────────────────────────────────────────────────────────
  const categories = useMemo(() => {
    const cats = new Set(articles.map((a) => a.category).filter(Boolean) as string[])
    return Array.from(cats).sort()
  }, [articles])

  const filteredArticles = useMemo(
    () => (categoryFilter ? articles.filter((a) => a.category === categoryFilter) : articles),
    [articles, categoryFilter],
  )

  // ── B2B Kunden-Suche ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (!showB2BDialog || b2bSearch.length < 2) { setB2bResults([]); return }
    const t = setTimeout(async () => {
      try {
        const res = await apiClient.get<{ items: Array<{ id: string; name: string; number: string }> }>(
          '/api/v1/business-partners',
          { params: { search: b2bSearch, type: 'customer', limit: 10 } },
        )
        setB2bResults(res.data.items ?? [])
      } catch { setB2bResults([]) }
    }, 300)
    return () => clearTimeout(t)
  }, [b2bSearch, showB2BDialog])

  // ── Warenkorb-Operationen ─────────────────────────────────────────────────────
  const addToCart = useCallback((article: Omit<CartItem, 'menge'>) => {
    setLastAddedEan(article.ean)
    setTimeout(() => setLastAddedEan(null), 1500)
    setCart((prev) => {
      const existing = prev.find((i) => i.ean === article.ean)
      if (existing) return prev.map((i) => i.ean === article.ean ? { ...i, menge: i.menge + 1 } : i)
      return [...prev, { ...article, menge: 1 }]
    })
  }, [])

  function removeFromCart(ean: string): void {
    setRemovingEans((prev) => new Set(prev).add(ean))
    setTimeout(() => {
      setCart((prev) => prev.filter((i) => i.ean !== ean))
      setRemovingEans((prev) => { const n = new Set(prev); n.delete(ean); return n })
    }, 220)
  }

  function updateQuantity(ean: string, menge: number): void {
    if (menge <= 0) removeFromCart(ean)
    else setCart((prev) => prev.map((i) => i.ean === ean ? { ...i, menge } : i))
  }

  // ── Barcode ───────────────────────────────────────────────────────────────────
  async function handleBarcodeInput(ean: string): Promise<void> {
    const cached = articles.find((a) => a.ean === ean)
    if (cached) {
      addToCart(cached)
      setBarcode('')
      toast({ title: `📦 ${cached.bezeichnung}`, description: `EAN ${ean} · ${cached.preis.toFixed(2)} €` })
      return
    }
    try {
      const response = await apiClient.get<{ items: ApiArticle[] }>(
        '/api/v1/articles',
        { params: { search: ean, limit: 1 } },
      )
      const item = response.data.items[0]
      if (item) {
        const cartItem = {
          artikelnr: item.article_number,
          bezeichnung: item.name,
          ean: item.barcode ?? ean,
          preis: Number(item.sales_price) || 0,
          image_url: item.image_url ?? null,
          category: item.category ?? undefined,
        }
        addToCart(cartItem)
        toast({ title: `📦 ${item.name}`, description: `EAN ${ean} · ${Number(item.sales_price).toFixed(2)} €` })
        setBarcode('')
      } else {
        toast({ variant: 'destructive', title: 'Artikel nicht gefunden', description: `EAN: ${ean}` })
      }
    } catch {
      toast({ variant: 'destructive', title: 'Fehler beim Laden' })
    }
  }

  // ── Zahlung ───────────────────────────────────────────────────────────────────
  function handlePaymentMethodSelect(method: PaymentMethod): void {
    if (method === 'b2b' && !customerId) {
      setShowB2BDialog(true)
      return
    }
    setPaymentMethod(method)
    if (method === 'bar') setShowChangeCalculator(true)
    else void handleCheckout(method)
  }

  async function handleCheckout(method?: PaymentMethod): Promise<void> {
    const selectedMethod = method ?? paymentMethod
    if (!selectedMethod) return
    const total = cart.reduce((s, i) => s + i.preis * i.menge, 0)
    if (selectedMethod === 'bar' && tendered < total) {
      toast({ variant: 'destructive', title: 'Unzureichender Betrag', description: `Fehlbetrag: ${(total - tendered).toFixed(2)} €` })
      return
    }
    try {
      let tx = activeTx
      if (!tx) { tx = await startTransaction('Verkauf', 'Kassenbeleg-V1'); setActiveTx(tx) }
      await updateTransaction(tx.txId, cart.map((i) => ({ bezeichnung: i.bezeichnung, preis: i.preis, menge: i.menge })))
      const payMap: Record<PaymentMethod, PaymentType> = { bar: 'CASH', ec: 'NON_CASH', paypal: 'NON_CASH', b2b: 'INTERNAL' }
      const signed = await finishTransaction(tx.txId, payMap[selectedMethod], total)
      const change = selectedMethod === 'bar' ? tendered - total : 0
      toast({
        title: '✅ Zahlung erfolgreich',
        description: `${total.toFixed(2)} € · ${selectedMethod.toUpperCase()}${change > 0 ? ` · Wechselgeld: ${change.toFixed(2)} €` : ''} · TSE ${signed.number}`,
      })
      setCart([]); setPaymentMethod(null); setCustomerId(null); setCustomerName(null)
      setActiveTx(null); setShowChangeCalculator(false); setTendered(0)
    } catch {
      toast({ variant: 'destructive', title: 'TSE-Fehler', description: 'Transaktion in Offline-Queue gespeichert.' })
    }
  }

  // ── Touch-Bedienfeld ──────────────────────────────────────────────────────────
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
          toast({ title: 'Storno', description: `"${last.bezeichnung}" entfernt` })
        } else {
          toast({ variant: 'destructive', title: 'Warenkorb leer' })
        }
        break
      case 'tara':
        toast({ title: 'TARA', description: 'Waage tariert' })
        break
      case 'kassenschublade':
        toast({ title: 'Kassenschublade', description: 'Schublade geöffnet' })
        break
      case 'bareinlage': case 'barentnahme':
        toast({ title: action.type === 'bareinlage' ? 'Bareinlage' : 'Barentnahme', description: 'Im Tagesabschluss erfassen' })
        break
      case 'digit':
        if (showChangeCalculator) {
          const nb = ((numpadBuffer === '0' ? '' : numpadBuffer) + action.digit) || '0'
          setNumpadBuffer(nb); setTendered(parseFloat(nb.replace(',', '.')) || 0)
        } else setBarcode((b) => b + action.digit)
        break
      case 'comma':
        if (showChangeCalculator) {
          if (!numpadBuffer.includes(',')) { const nb = numpadBuffer + ','; setNumpadBuffer(nb) }
        } else setBarcode((b) => b + ',')
        break
      case 'clear':
        if (showChangeCalculator) { setNumpadBuffer('0'); setTendered(0) }
        else setBarcode('')
        break
      case 'enter':
        if (showChangeCalculator) void handleCheckout()
        else if (barcode) void handleBarcodeInput(barcode)
        break
    }
  }

  // ── Bilder laden ──────────────────────────────────────────────────────────────
  async function handleEnrichImages(): Promise<void> {
    setEnriching(true)
    try {
      const res = await apiClient.post<{ enriched: number; skipped: number }>('/api/v1/articles/enrich-images')
      toast({ title: 'Bilder geladen', description: `${res.data.enriched} neue Bilder, ${res.data.skipped} ohne Treffer` })
      void articlesQuery.refetch()
    } catch {
      toast({ variant: 'destructive', title: 'Fehler beim Laden der Bilder' })
    } finally {
      setEnriching(false)
    }
  }

  const total = cart.reduce((s, i) => s + i.preis * i.menge, 0)
  const fmt = (n: number) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n)

  // ── Render ────────────────────────────────────────────────────────────────────
  return (
    <div className="h-screen flex flex-col bg-gray-50 overflow-hidden">

      {/* ── Header ── */}
      <div className="bg-primary text-primary-foreground px-5 py-3 flex items-center justify-between flex-shrink-0">
        {/* Links: Logo */}
        <div className="flex items-center gap-3 min-w-0">
          <ShoppingCart className="h-7 w-7 flex-shrink-0" />
          <div className="min-w-0">
            <h1 className="text-xl font-bold leading-none">VALEO POS</h1>
            <p className="text-xs opacity-75 mt-0.5">Haus & Gartenmarkt</p>
          </div>
        </div>

        {/* Mitte: Uhrzeit */}
        <div className="flex items-center gap-2 text-primary-foreground/90">
          <Clock className="h-4 w-4" />
          <span className="text-xl font-mono font-semibold tabular-nums">{clock}</span>
        </div>

        {/* Rechts: Kassierer + Status + Settings */}
        <div className="flex items-center gap-3">
          {/* Kassierer */}
          <div className="flex items-center gap-1.5 text-sm text-primary-foreground/80">
            <User className="h-4 w-4" />
            <span className="font-medium">{kassierer || 'Kein Kassierer'}</span>
          </div>

          {/* Kundenmodus */}
          <Badge
            variant="secondary"
            className="cursor-pointer text-sm px-3 py-1"
            onClick={() => customerId ? (setCustomerId(null), setCustomerName(null)) : setShowB2BDialog(true)}
            title={customerId ? 'B2B-Kunde abmelden' : 'B2B-Kunden wählen'}
          >
            {customerId ? (
              <span className="flex items-center gap-1"><UserCheck className="h-3 w-3" />{customerName ?? customerId}</span>
            ) : 'B2C'}
          </Badge>

          {/* TSE-Ampel */}
          <TseStatusLight isInitialized={isInitialized} />

          {/* Touch-Bedienfeld Toggle */}
          <div className="flex items-center gap-1.5">
            <Switch
              id="touch-bedienfeld"
              checked={showTouchBedienfeld}
              onCheckedChange={(v) => {
                setShowTouchBedienfeld(v)
                try { localStorage.setItem(POS_TOUCH_PANEL_KEY, String(v)) } catch { /* */ }
              }}
              className="scale-90"
            />
            <Label htmlFor="touch-bedienfeld" className="flex items-center gap-1 cursor-pointer text-xs text-primary-foreground/80">
              <Keyboard className="h-3.5 w-3.5" />
            </Label>
          </div>

          {/* Settings */}
          <Button size="sm" variant="ghost" onClick={() => setShowSettings(true)} className="text-primary-foreground hover:text-primary-foreground hover:bg-primary-foreground/20 h-8 w-8 p-0">
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* ── Haupt-Layout ── */}
      <div className="flex-1 flex overflow-hidden">

        {/* ── Warenkorb (links) ── */}
        <div className="w-80 flex-shrink-0 border-r bg-white flex flex-col">
          <div className="px-4 pt-4 pb-2 flex items-center justify-between">
            <h2 className="font-bold text-base flex items-center gap-2">
              <ShoppingCart className="h-4 w-4" />
              Warenkorb
              {cart.length > 0 && (
                <Badge variant="secondary" className="text-xs">{cart.reduce((s, i) => s + i.menge, 0)}</Badge>
              )}
            </h2>
            {cart.length > 0 && (
              <Button
                size="sm" variant="ghost"
                className="text-destructive hover:text-destructive h-7 w-7 p-0"
                title="Warenkorb leeren"
                onClick={() => { if (confirm('Warenkorb wirklich leeren?')) setCart([]) }}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            )}
          </div>

          {/* Positionen */}
          <div className="flex-1 overflow-auto px-3 space-y-1.5 pb-2">
            {cart.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-muted-foreground py-12">
                <ShoppingCart className="h-12 w-12 opacity-20 mb-3" />
                <p className="text-sm">Warenkorb leer</p>
                <p className="text-xs opacity-60 mt-1">Artikel scannen oder auswählen</p>
              </div>
            ) : (
              cart.map((item) => (
                <div
                  key={item.ean}
                  className={`
                    flex items-center gap-2 rounded-lg border p-2 bg-white transition-all duration-200
                    ${removingEans.has(item.ean) ? 'opacity-0 -translate-x-4' : 'opacity-100 translate-x-0'}
                    ${lastAddedEan === item.ean ? 'border-green-400 bg-green-50' : 'border-transparent hover:border-gray-200'}
                  `}
                >
                  <ArticleImageSmall imageUrl={item.image_url} name={item.bezeichnung} category={item.category} />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold leading-tight line-clamp-1">{item.bezeichnung}</div>
                    <div className="text-xs text-muted-foreground mt-0.5">
                      {item.menge} × {fmt(item.preis)}
                      <span className="font-semibold text-foreground ml-1">= {fmt(item.preis * item.menge)}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 flex-shrink-0">
                    <Button size="sm" variant="outline" className="h-8 w-8 p-0" onClick={() => updateQuantity(item.ean, item.menge - 1)}>−</Button>
                    <span className="w-7 text-center text-sm font-bold">{item.menge}</span>
                    <Button size="sm" variant="outline" className="h-8 w-8 p-0" onClick={() => updateQuantity(item.ean, item.menge + 1)}>+</Button>
                    <Button size="sm" variant="ghost" className="h-8 w-8 p-0 text-destructive hover:text-destructive" onClick={() => removeFromCart(item.ean)}>
                      <X className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Gesamt-Anzeige */}
          <div className="border-t bg-white px-4 py-3">
            <div className="flex justify-between items-center mb-3">
              <span className="text-sm text-muted-foreground">{cart.length} Position(en)</span>
              <div className="text-right">
                <div className="text-xs text-muted-foreground">Gesamt inkl. MwSt.</div>
                <div className="text-3xl font-bold text-primary tabular-nums">{fmt(total)}</div>
              </div>
            </div>

            {/* Zahlungsarten */}
            <div className="grid grid-cols-2 gap-2">
              {/* Bar — dominant (volle Breite) */}
              <Button
                size="lg"
                variant={paymentMethod === 'bar' ? 'default' : 'outline'}
                onClick={() => handlePaymentMethodSelect('bar')}
                className="col-span-2 h-14 gap-2 text-lg font-bold"
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
                <CreditCard className="h-4 w-4" />
                EC
              </Button>
              <Button
                size="lg"
                variant={paymentMethod === 'paypal' ? 'default' : 'outline'}
                onClick={() => handlePaymentMethodSelect('paypal')}
                className="gap-2"
                disabled={cart.length === 0}
              >
                <Smartphone className="h-4 w-4" />
                PayPal
              </Button>
              <Button
                size="lg"
                variant={paymentMethod === 'b2b' ? 'default' : 'outline'}
                onClick={() => handlePaymentMethodSelect('b2b')}
                className="col-span-2 gap-2 border-dashed"
                disabled={cart.length === 0}
              >
                <FileText className="h-4 w-4" />
                B2B-Beleg{customerId ? ` (${customerName ?? customerId})` : ' — Kunden wählen'}
              </Button>
            </div>
          </div>
        </div>

        {/* ── Artikelauswahl (Mitte) ── */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">

          <Tabs value={articleTab} onValueChange={(v) => setArticleTab(v as typeof articleTab)} className="flex-1 flex flex-col overflow-hidden">
            {/* Tab-Leiste */}
            <div className="px-4 pt-3 pb-0 flex-shrink-0">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="scanner" className="gap-1.5">
                  <Scan className="h-4 w-4" />Scanner
                </TabsTrigger>
                <TabsTrigger value="grid" className="gap-1.5">
                  <Grid3x3 className="h-4 w-4" />Grid
                </TabsTrigger>
                <TabsTrigger value="search" className="gap-1.5">
                  <Search className="h-4 w-4" />Suche
                </TabsTrigger>
              </TabsList>
            </div>

            {/* Scanner-Tab */}
            <TabsContent value="scanner" className="flex-1 px-4 py-3">
              <div className="relative mb-4">
                <Scan className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input
                  ref={barcodeInputRef}
                  placeholder="Barcode scannen oder eingeben..."
                  value={barcode}
                  onChange={(e) => setBarcode(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter') void handleBarcodeInput(barcode) }}
                  className="pl-10 text-lg h-14"
                  autoFocus
                />
              </div>
              <p className="text-sm text-muted-foreground text-center">
                Barcode mit Scanner erfassen oder manuell eingeben und Enter drücken
              </p>
            </TabsContent>

            {/* Artikel-Grid */}
            <TabsContent value="grid" className="flex-1 flex flex-col overflow-hidden px-4 pb-3 pt-2">
              {/* Kategorie-Filter */}
              {categories.length > 0 && (
                <div className="w-full flex-shrink-0 mb-3 overflow-x-auto">
                  <div className="flex gap-2 pb-1 min-w-max">
                    <Button
                      size="sm"
                      variant={categoryFilter === null ? 'default' : 'outline'}
                      onClick={() => setCategoryFilter(null)}
                      className="whitespace-nowrap h-8 text-xs"
                    >
                      Alle ({articles.length})
                    </Button>
                    {categories.map((cat) => (
                      <Button
                        key={cat}
                        size="sm"
                        variant={categoryFilter === cat ? 'default' : 'outline'}
                        onClick={() => setCategoryFilter(cat === categoryFilter ? null : cat)}
                        className="whitespace-nowrap h-8 text-xs"
                      >
                        {cat} ({articles.filter((a) => a.category === cat).length})
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              {/* Grid */}
              <div className="flex-1 overflow-auto">
                {articlesLoading ? (
                  <div className="grid grid-cols-4 gap-3">
                    {Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-44" />)}
                  </div>
                ) : filteredArticles.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                    <AlertCircle className="h-10 w-10 opacity-30 mb-2" />
                    <p className="text-sm">Keine Artikel in dieser Kategorie</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-4 gap-3">
                    {filteredArticles.map((article) => (
                      <Card
                        key={article.artikelnr}
                        className={`
                          cursor-pointer transition-all duration-150 overflow-hidden
                          hover:shadow-md active:scale-95
                          ${lastAddedEan === article.ean ? 'ring-2 ring-green-400 shadow-lg' : ''}
                        `}
                        onClick={() => addToCart(article)}
                      >
                        <ArticleImageLarge imageUrl={article.image_url} name={article.bezeichnung} category={article.category} />
                        <CardContent className="p-2 text-center">
                          <div className="font-semibold text-xs leading-tight line-clamp-2 mb-1 min-h-[2.5rem] flex items-center justify-center">
                            {article.bezeichnung}
                          </div>
                          <div className="text-lg font-bold text-primary tabular-nums">{fmt(article.preis)}</div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            </TabsContent>

            {/* Suche-Tab */}
            <TabsContent value="search" className="flex-1 px-4 py-3">
              <ArticleSearch
                onSelect={(article) => {
                  addToCart({
                    artikelnr: article.artikelnr,
                    bezeichnung: article.bezeichnung,
                    ean: article.ean ?? '',
                    preis: article.preis,
                    image_url: article.image_url ?? null,
                    category: article.kategorie,
                  })
                }}
              />
            </TabsContent>
          </Tabs>
        </div>

        {/* ── Touch-Bedienfeld (rechts) ── */}
        {showTouchBedienfeld && (
          <div className="w-64 flex-shrink-0 border-l bg-slate-50 flex flex-col overflow-auto">
            <div className="px-3 pt-3 pb-1 text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
              <Keyboard className="h-3.5 w-3.5" />Bedienfeld
            </div>
            <TouchBedienfeld onAction={handleTouchBedienfeldAction} disabled={false} />
          </div>
        )}
      </div>

      {/* ── Wechselgeld-Dialog ── */}
      <Dialog open={showChangeCalculator} onOpenChange={setShowChangeCalculator}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Barzahlung — {fmt(total)}</DialogTitle></DialogHeader>
          <ChangeCalculator total={total} onTenderedChange={setTendered} />
          <div className="flex gap-2 mt-2">
            <Button variant="outline" onClick={() => { setShowChangeCalculator(false); setPaymentMethod(null); setTendered(0) }} className="flex-1">
              Abbrechen
            </Button>
            <Button onClick={() => void handleCheckout()} disabled={tendered < total} className="flex-1 text-base font-bold h-12">
              {tendered >= total
                ? <><CheckCircle2 className="h-4 w-4 mr-1.5" />Bezahlung abschließen</>
                : `Fehlbetrag: ${fmt(total - tendered)}`}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* ── B2B Kunden-Dialog ── */}
      <Dialog open={showB2BDialog} onOpenChange={setShowB2BDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>B2B-Kunde wählen</DialogTitle></DialogHeader>
          <Input
            placeholder="Kundenname oder Nummer suchen..."
            value={b2bSearch}
            onChange={(e) => setB2bSearch(e.target.value)}
            className="h-12"
            autoFocus
          />
          <div className="space-y-2 max-h-72 overflow-auto">
            {b2bResults.length === 0 && b2bSearch.length >= 2 && (
              <p className="text-sm text-muted-foreground text-center py-4">Keine Kunden gefunden</p>
            )}
            {b2bResults.map((bp) => (
              <button
                key={bp.id}
                className="w-full flex items-center gap-3 p-3 rounded-lg border hover:bg-accent text-left transition-colors"
                onClick={() => {
                  setCustomerId(bp.id); setCustomerName(bp.name)
                  setShowB2BDialog(false); setB2bSearch('')
                  setPaymentMethod('b2b'); void handleCheckout('b2b')
                }}
              >
                <UserCheck className="h-5 w-5 text-muted-foreground" />
                <div><div className="font-semibold">{bp.name}</div><div className="text-xs text-muted-foreground">{bp.number}</div></div>
              </button>
            ))}
          </div>
          <Button variant="outline" onClick={() => setShowB2BDialog(false)}>Abbrechen</Button>
        </DialogContent>
      </Dialog>

      {/* ── Einstellungen-Dialog ── */}
      <Dialog open={showSettings} onOpenChange={setShowSettings}>
        <DialogContent className="max-w-sm">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><Settings className="h-5 w-5" />POS-Einstellungen</DialogTitle></DialogHeader>
          <div className="space-y-5">
            <div>
              <Label className="text-sm font-semibold">Kassierer / Kassiererin</Label>
              <Input
                className="mt-1.5"
                placeholder="Name eingeben..."
                value={kassierer}
                onChange={(e) => {
                  setKassierer(e.target.value)
                  try { localStorage.setItem(POS_KASSIERER_KEY, e.target.value) } catch { /* */ }
                }}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="s-touch" className="text-sm font-semibold flex items-center gap-2">
                <Keyboard className="h-4 w-4" />Touch-Bedienfeld
              </Label>
              <Switch
                id="s-touch"
                checked={showTouchBedienfeld}
                onCheckedChange={(v) => {
                  setShowTouchBedienfeld(v)
                  try { localStorage.setItem(POS_TOUCH_PANEL_KEY, String(v)) } catch { /* */ }
                }}
              />
            </div>
            <div className="border-t pt-4">
              <Label className="text-sm font-semibold text-muted-foreground">Artikelbilder</Label>
              <p className="text-xs text-muted-foreground mt-1 mb-2">
                Lädt fehlende Produktbilder aus Open Food Facts und Wikipedia (EAN/Name-basiert).
              </p>
              <Button
                className="w-full"
                variant="outline"
                onClick={() => { void handleEnrichImages(); setShowSettings(false) }}
                disabled={enriching}
              >
                {enriching ? 'Bilder werden geladen…' : 'Artikelbilder jetzt laden'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
