/**
 * Kundenportal E-Shop
 * 
 * Kunden können hier Produkte bestellen und Angebotsanfragen stellen
 * 
 * Verwendet das Backend-API für Produkte mit Kontrakt/Vorkauf-Informationen.
  */

import { useState, useEffect, useMemo, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { NativeSelect } from '@/components/ui/native-select'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { ErrorState } from '@/components/ErrorState'
import {
  Search,
  ShoppingCart,
  Plus,
  Minus,
  Trash2,
  Package,
  Leaf,
  Droplets,
  Bug,
  Wheat,
  Check,
  Info,
  FileQuestion,
  Send,
  RotateCcw,
  FileText,
  AlertTriangle,
  Wallet,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { Progress } from '@/components/ui/progress'
import { usePriceLists } from '@/lib/api/price-lists'
import { extractTierBreaks, fallbackTierBreaks, getTierInfo } from '@/lib/professional-workspaces'
import { portalService } from '@/lib/services/portal-service'
import { getAxiosErrorMessage } from '@/lib/api-client'

// Kontrakt-Status für Rahmenverträge
type ContractStatus = 'NONE' | 'ACTIVE' | 'LOW' | 'EXHAUSTED'

interface Product {
  id: string
  name: string
  kategorie: string
  beschreibung: string
  einheit: string
  preis: number // Listenpreis
  rabattPreis?: number // Aktionspreis
  verfuegbar: boolean
  bestand: number
  bild?: string
  zertifikate: string[]
  artikelnummer: string
  letzteBestellung?: {
    datum: string
    menge: number
  }
  // Kontrakt-Informationen
  contractStatus?: ContractStatus
  contractPrice?: number // Vertragspreis
  contractTotalQty?: number // Gesamtmenge im Vertrag
  contractRemainingQty?: number // Restmenge im Vertrag
  // Vorkauf-Informationen (z.B. bereits bezahlter Dünger)
  isPrePurchase?: boolean
  prePurchasePrice?: number // Preis zu dem vorgekauft wurde
  prePurchaseTotalQty?: number // Gesamtmenge Vorkauf
  prePurchaseRemainingQty?: number // Rest-Guthaben aus Vorkauf
}

// Hilfsfunktion: Prüft ob Datum innerhalb der letzten X Tage liegt
function isWithinDays(dateString: string, days: number): boolean {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = now.getTime() - date.getTime()
  const diffDays = diffTime / (1000 * 60 * 60 * 24)
  return diffDays <= days
}

// Lieferkonditionen / Parität
type DeliveryParity = 
  | 'frei_silo_geblasen'    // Frei Silo geblasen
  | 'frei_hof_gekippt'      // Frei Hof gekippt
  | 'auf_palette'           // Auf Palette
  | 'ab_lager'              // Ab Lager (Selbstabholung)

const DELIVERY_PARITY_OPTIONS: { value: DeliveryParity; label: string; requiresSilo: boolean; hasFreight: boolean }[] = [
  { value: 'frei_silo_geblasen', label: 'Frei Silo geblasen', requiresSilo: true, hasFreight: true },
  { value: 'frei_hof_gekippt', label: 'Frei Hof gekippt', requiresSilo: false, hasFreight: true },
  { value: 'auf_palette', label: 'Auf Palette', requiresSilo: false, hasFreight: true },
  { value: 'ab_lager', label: 'Ab Lager (Selbstabholung)', requiresSilo: false, hasFreight: false },
]

const portalAnfrageProduktOptions = [
  { value: 'saatgut', label: 'Saatgut' },
  { value: 'duenger', label: 'Duengemittel' },
  { value: 'psm', label: 'Pflanzenschutzmittel' },
  { value: 'futtermittel', label: 'Futtermittel' },
  { value: 'dienstleistung', label: 'Dienstleistung' },
  { value: 'sonstiges', label: 'Sonstiges' },
]

// Kategorien die als "lose Ware" gelten
const BULK_CATEGORIES = ['futtermittel', 'duenger']

// Prüft ob Artikel lose Ware ist
function isBulkProduct(product: Product): boolean {
  return BULK_CATEGORIES.includes(product.kategorie)
}

function getStaffelInfo(product: Product, menge: number, staffelByProduct: Record<string, ReturnType<typeof fallbackTierBreaks>>): {
  zuschlag: number
  naechsteStaffel?: { abMenge: number; ersparnis: number }
} {
  const fallbackPrice = product.rabattPreis || product.contractPrice || product.preis
  const tiers = staffelByProduct[product.id] ?? fallbackTierBreaks(product.kategorie, fallbackPrice)
  const tierInfo = getTierInfo(tiers, menge, fallbackPrice)
  return {
    zuschlag: tierInfo.surcharge,
    naechsteStaffel: tierInfo.nextTier ? { abMenge: tierInfo.nextTier.minQuantity, ersparnis: tierInfo.nextTier.savings } : undefined,
  }
}

interface CartItem extends Product {
  menge: number
  // Zusatzfelder für lose Ware
  siloNummer?: string
  deliveryParity: DeliveryParity
  frachtkosten?: number     // € pauschal
  // Letzte Bestellung für Vorbelegung
  lastOrderSilo?: string
  lastOrderParity?: DeliveryParity
}

const kategorien = [
  { value: 'alle', label: 'Alle Produkte', icon: <Package className="h-4 w-4" /> },
  { value: 'saatgut', label: 'Saatgut', icon: <Wheat className="h-4 w-4" /> },
  { value: 'duenger', label: 'Düngemittel', icon: <Droplets className="h-4 w-4" /> },
  { value: 'psm', label: 'Pflanzenschutz', icon: <Bug className="h-4 w-4" /> },
  { value: 'futtermittel', label: 'Futtermittel', icon: <Leaf className="h-4 w-4" /> },
  { value: 'sonstiges', label: 'Sonstiges', icon: <Package className="h-4 w-4" /> },
]

export default function PortalShop() {
  const [loading, setLoading] = useState(true)
  const [products, setProducts] = useState<Product[]>([])
  const [cart, setCart] = useState<CartItem[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedKategorie, setSelectedKategorie] = useState('alle')
  const [showCart, setShowCart] = useState(false)
  const [showAnfrage, setShowAnfrage] = useState(false)
  const [orderSuccess, setOrderSuccess] = useState(false)
  const [anfrageSuccess, setAnfrageSuccess] = useState(false)
  const [anfrageText, setAnfrageText] = useState('')
  const [anfrageProdukt, setAnfrageProdukt] = useState('')

  const [loadError, setLoadError] = useState<Error | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const [orderSubmitting, setOrderSubmitting] = useState(false)
  const [inquirySubmitting, setInquirySubmitting] = useState(false)
  const { data: priceLists = [] } = usePriceLists()

  const loadProducts = useCallback(async () => {
    setLoading(true)
    setLoadError(null)
    try {
      const response = await portalService.getProducts({
        kategorie: selectedKategorie !== 'alle' ? selectedKategorie : undefined,
        search: searchTerm || undefined,
      })
      setProducts(response.items.map(item => ({
        ...item,
        beschreibung: item.beschreibung || '',
      })) as Product[])
    } catch (err) {
      setProducts([])
      setLoadError(err instanceof Error ? err : new Error('Produkte konnten nicht geladen werden'))
    } finally {
      setLoading(false)
    }
  }, [selectedKategorie, searchTerm])

  useEffect(() => {
    loadProducts()
  }, [loadProducts])

  const staffelByProduct = useMemo(() => {
    const result: Record<string, ReturnType<typeof fallbackTierBreaks>> = {}
    for (const product of products) {
      const activeTierBreaks = extractTierBreaks(priceLists, {
        articleId: product.id,
        articleNumber: product.artikelnummer,
        articleGroup: product.kategorie,
      })
      result[product.id] = activeTierBreaks.length > 0 ? activeTierBreaks : fallbackTierBreaks(product.kategorie, product.rabattPreis || product.contractPrice || product.preis)
    }
    return result
  }, [priceLists, products])

  const REORDER_DAYS = 42 // Zeitraum für "Erneut bestellen" Markierung

  const filteredProducts = useMemo(() => {
    const filtered = products.filter((product) => {
      const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.artikelnummer.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesKategorie = selectedKategorie === 'alle' || product.kategorie === selectedKategorie
      return matchesSearch && matchesKategorie
    })

    // Sortierung: Kürzlich bestellte Artikel zuerst (innerhalb der letzten 42 Tage)
    return filtered.sort((a, b) => {
      const aRecentOrder = a.letzteBestellung && isWithinDays(a.letzteBestellung.datum, REORDER_DAYS)
      const bRecentOrder = b.letzteBestellung && isWithinDays(b.letzteBestellung.datum, REORDER_DAYS)
      
      // Produkte mit kürzlicher Bestellung zuerst
      if (aRecentOrder && !bRecentOrder) return -1
      if (!aRecentOrder && bRecentOrder) return 1
      
      // Bei beiden kürzlich bestellt: nach Datum sortieren (neueste zuerst)
      if (aRecentOrder && bRecentOrder) {
        const aDate = a.letzteBestellung?.datum ?? ''
        const bDate = b.letzteBestellung?.datum ?? ''
        return new Date(bDate).getTime() - new Date(aDate).getTime()
      }
      
      // Sonst: Standard-Reihenfolge beibehalten
      return 0
    })
  }, [products, searchTerm, selectedKategorie])

  // Gesamtbestellmenge pro Einheit (für Anzeige)
  const cartQuantityByUnit = useMemo(() => {
    const byUnit: Record<string, number> = {}
    cart.forEach((item) => {
      const unit = item.einheit
      byUnit[unit] = (byUnit[unit] || 0) + item.menge
    })
    return byUnit
  }, [cart])

  // Warenwert (ohne Fracht/Staffel)
  const cartWarenwert = useMemo(() => {
    return cart.reduce((sum, item) => sum + (item.rabattPreis || item.preis) * item.menge, 0)
  }, [cart])

  // Staffelzuschläge gesamt (automatisch aus Staffeltabellen berechnet)
  const cartStaffelGesamt = useMemo(() => {
    return cart.reduce((sum, item) => {
      if (isBulkProduct(item)) {
        const { zuschlag } = getStaffelInfo(item, item.menge, staffelByProduct)
        return sum + zuschlag * item.menge
      }
      return sum
    }, 0)
  }, [cart])

  // Frachtkosten gesamt
  const cartFrachtGesamt = useMemo(() => {
    return cart.reduce((sum, item) => sum + (item.frachtkosten || 0), 0)
  }, [cart])

  // Gesamtwert inkl. Zuschläge
  const cartTotal = useMemo(() => {
    return cartWarenwert + cartStaffelGesamt + cartFrachtGesamt
  }, [cartWarenwert, cartStaffelGesamt, cartFrachtGesamt])

  const cartCount = useMemo(() => {
    return cart.reduce((sum, item) => sum + item.menge, 0)
  }, [cart])

  const addToCart = (product: Product) => {
    setCart((prev) => {
      const existing = prev.find((item) => item.id === product.id)
      if (existing) {
        return prev.map((item) =>
          item.id === product.id ? { ...item, menge: item.menge + 1 } : item
        )
      }
      
      // Vorbelegung aus letzter Bestellung (Mock - später aus API)
      const lastOrderSilo = product.letzteBestellung ? 'Silo 1' : undefined
      const lastOrderParity: DeliveryParity = product.letzteBestellung ? 'frei_silo_geblasen' : 'ab_lager'
      const defaultMenge = product.letzteBestellung?.menge || 1
      
      const newItem: CartItem = {
        ...product,
        menge: defaultMenge,
        siloNummer: isBulkProduct(product) ? lastOrderSilo : undefined,
        deliveryParity: isBulkProduct(product) ? lastOrderParity : 'ab_lager',
        frachtkosten: isBulkProduct(product) && lastOrderParity !== 'ab_lager' ? 15 : undefined,
        lastOrderSilo,
        lastOrderParity,
      }
      
      return [...prev, newItem]
    })
  }

  const updateCartQuantity = (productId: string, delta: number) => {
    setCart((prev) => {
      return prev
        .map((item) => {
          if (item.id === productId) {
            const newMenge = Math.min(500, Math.max(0, item.menge + delta))
            return newMenge > 0 ? { ...item, menge: newMenge } : null
          }
          return item
        })
        .filter(Boolean) as CartItem[]
    })
  }

  // Direkte Mengeneingabe (für große Bestellmengen wie 240 dt)
  const setCartQuantity = (productId: string, menge: number) => {
    const validMenge = Math.min(500, Math.max(1, menge))
    setCart((prev) =>
      prev.map((item) =>
        item.id === productId ? { ...item, menge: validMenge } : item
      )
    )
  }

  // Silo-Nummer aktualisieren
  const updateCartSilo = (productId: string, siloNummer: string) => {
    setCart((prev) =>
      prev.map((item) =>
        item.id === productId ? { ...item, siloNummer } : item
      )
    )
  }

  // Parität / Lieferkondition aktualisieren
  const updateCartParity = (productId: string, deliveryParity: DeliveryParity) => {
    const parityOption = DELIVERY_PARITY_OPTIONS.find(p => p.value === deliveryParity)
    setCart((prev) =>
      prev.map((item) => {
        if (item.id === productId) {
          return {
            ...item,
            deliveryParity,
            // Silo nur bei "frei Silo geblasen" erforderlich
            siloNummer: parityOption?.requiresSilo ? item.siloNummer : undefined,
            // Fracht nur bei Lieferung
            frachtkosten: parityOption?.hasFreight ? (item.frachtkosten || 15) : undefined,
          }
        }
        return item
      })
    )
  }

  // Frachtkosten aktualisieren
  const updateCartFracht = (productId: string, frachtkosten: number | undefined) => {
    setCart((prev) =>
      prev.map((item) =>
        item.id === productId ? { ...item, frachtkosten } : item
      )
    )
  }

  const removeFromCart = (productId: string) => {
    setCart((prev) => prev.filter((item) => item.id !== productId))
  }

  const handleOrder = async () => {
    if (cart.length === 0) return
    setActionError(null)
    setOrderSubmitting(true)
    try {
      await portalService.createOrder({
        items: cart.map((item) => ({
          article_id: item.id,
          quantity: item.menge,
        })),
        customer_notes: cart
          .filter((item) => isBulkProduct(item))
          .map((item) => `${item.name}: ${item.deliveryParity}${item.siloNummer ? `, Silo ${item.siloNummer}` : ''}`)
          .join(' | '),
      })
      setOrderSuccess(true)
      setCart([])
      setTimeout(() => {
        setShowCart(false)
        setOrderSuccess(false)
      }, 2000)
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Bestellung konnte nicht gesendet werden')
    } finally {
      setOrderSubmitting(false)
    }
  }

  const handleAnfrage = async () => {
    if (!anfrageText || !anfrageProdukt) return
    setActionError(null)
    setInquirySubmitting(true)
    try {
      await portalService.createInquiry({
        anforderer: 'Portal-Kunde',
        typ: 'ANF',
        prioritaet: 'normal',
        artikel: anfrageProdukt,
        begruendung: `Portal-Anfrage: ${anfrageProdukt}`,
        notizen: anfrageText,
        datum: new Date().toISOString().slice(0, 10),
      })
      setAnfrageSuccess(true)
      setTimeout(() => {
        setShowAnfrage(false)
        setAnfrageSuccess(false)
        setAnfrageText('')
        setAnfrageProdukt('')
      }, 2000)
    } catch (err) {
      setActionError(getAxiosErrorMessage(err))
    } finally {
      setInquirySubmitting(false)
    }
  }

  if (loading) {
    return <ShopSkeleton />
  }

  if (loadError) {
    return <ErrorState error={loadError} onRetry={() => { void loadProducts() }} />
  }

  return (
    <div className="space-y-6">
      {actionError && (
        <Alert variant="destructive">
          <AlertTitle>Aktion fehlgeschlagen</AlertTitle>
          <AlertDescription>{actionError}</AlertDescription>
        </Alert>
      )}

      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Bestellportal</h1>
          <p className="text-muted-foreground">Futter- und Betriebsmittel bestellen</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowAnfrage(true)} className="gap-2">
            <FileQuestion className="h-4 w-4" />
            Anfrage stellen
          </Button>
          <Button onClick={() => setShowCart(true)} className="relative gap-2">
            <ShoppingCart className="h-4 w-4" />
            Warenkorb
            {cartCount > 0 && (
              <Badge className="absolute -right-2 -top-2 h-5 w-5 rounded-full p-0 text-xs">
                {cartCount}
              </Badge>
            )}
          </Button>
        </div>
      </div>

      {/* Search & Filter */}
      <div className="flex flex-col gap-4 md:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Produkt suchen..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0">
          {kategorien.map((kat) => (
            <Button
              key={kat.value}
              variant={selectedKategorie === kat.value ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedKategorie(kat.value)}
              className="gap-2 whitespace-nowrap"
            >
              {kat.icon}
              {kat.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Product Grid */}
      {filteredProducts.length === 0 ? (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>Keine Produkte gefunden</AlertTitle>
          <AlertDescription>
            Versuchen Sie einen anderen Suchbegriff oder wählen Sie eine andere Kategorie.
          </AlertDescription>
        </Alert>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filteredProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onAddToCart={() => addToCart(product)}
              inCart={cart.some((item) => item.id === product.id)}
            />
          ))}
        </div>
      )}

      {/* Warenkorb Dialog */}
      <Dialog open={showCart} onOpenChange={setShowCart}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <ShoppingCart className="h-5 w-5" />
              Warenkorb
            </DialogTitle>
            <DialogDescription>
              {cart.length === 0
                ? 'Ihr Warenkorb ist leer'
                : `${cart.length} Position${cart.length > 1 ? 'en' : ''} im Warenkorb`}
            </DialogDescription>
          </DialogHeader>

          {orderSuccess ? (
            <div className="flex flex-col items-center gap-4 py-8">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
                <Check className="h-8 w-8 text-emerald-600" />
              </div>
              <div className="text-center">
                <h3 className="text-lg font-semibold">Bestellung erfolgreich!</h3>
                <p className="text-muted-foreground">Ihre Bestellung wurde übermittelt.</p>
              </div>
            </div>
          ) : (
            <>
              <div className="space-y-4">
                {cart.map((item) => {
                  const isBulk = isBulkProduct(item)
                  const parityOption = DELIVERY_PARITY_OPTIONS.find(p => p.value === item.deliveryParity)
                  
                  return (
                    <div
                      key={item.id}
                      className={cn(
                        'rounded-lg border p-4',
                        isBulk && 'bg-amber-50/50 border-amber-200'
                      )}
                    >
                      {/* Kopfzeile: Produkt + Entfernen */}
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <div className="flex items-center gap-3">
                          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                            <Package className="h-6 w-6 text-muted-foreground" />
                          </div>
                          <div>
                            <p className="font-medium">{item.name}</p>
                            <p className="text-sm text-muted-foreground">
                              {item.artikelnummer}
                              {isBulk && <Badge variant="outline" className="ml-2 text-xs">Lose Ware</Badge>}
                            </p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                          onClick={() => removeFromCart(item.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>

                      {/* Menge & Einheit */}
                      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        <div className="space-y-1.5">
                          <Label className="text-xs text-muted-foreground">Bestellmenge ({item.einheit})</Label>
                          <div className="flex items-center gap-1">
                            <Button
                              variant="outline"
                              size="icon"
                              className="h-9 w-9"
                              onClick={() => updateCartQuantity(item.id, -10)}
                            >
                              <span className="text-xs">-10</span>
                            </Button>
                            <Button
                              variant="outline"
                              size="icon"
                              className="h-9 w-9"
                              onClick={() => updateCartQuantity(item.id, -1)}
                            >
                              <Minus className="h-3 w-3" />
                            </Button>
                            <Input
                              type="number"
                              min={1}
                              max={500}
                              value={item.menge}
                              onChange={(e) => setCartQuantity(item.id, parseInt(e.target.value) || 1)}
                              className="h-9 w-20 text-center font-semibold"
                            />
                            <Button
                              variant="outline"
                              size="icon"
                              className="h-9 w-9"
                              onClick={() => updateCartQuantity(item.id, 1)}
                            >
                              <Plus className="h-3 w-3" />
                            </Button>
                            <Button
                              variant="outline"
                              size="icon"
                              className="h-9 w-9"
                              onClick={() => updateCartQuantity(item.id, 10)}
                            >
                              <span className="text-xs">+10</span>
                            </Button>
                          </div>
                          {item.lastOrderSilo && (
                            <p className="text-xs text-blue-600">
                              Letzte Bestellung: {item.letzteBestellung?.menge} {item.einheit}
                            </p>
                          )}
                        </div>

                        {/* Parität (für alle Produkte) */}
                        <div className="space-y-1.5">
                          <Label className="text-xs text-muted-foreground">Parität / Lieferung</Label>
                          <NativeSelect
                            value={item.deliveryParity}
                            onValueChange={(value) => updateCartParity(item.id, value as DeliveryParity)}
                            className="h-9"
                            options={DELIVERY_PARITY_OPTIONS.map((option) => ({
                              value: option.value,
                              label: option.label,
                            }))}
                          />
                        </div>

                        {/* Silo-Nummer (nur bei lose Ware + frei Silo) */}
                        {isBulk && parityOption?.requiresSilo && (
                          <div className="space-y-1.5">
                            <Label className="text-xs text-muted-foreground">Silo-Nummer</Label>
                            <Input
                              placeholder="z.B. Silo 1"
                              value={item.siloNummer || ''}
                              onChange={(e) => updateCartSilo(item.id, e.target.value)}
                              className="h-9"
                            />
                            {item.lastOrderSilo && (
                              <p className="text-xs text-blue-600">
                                Zuletzt: {item.lastOrderSilo}
                              </p>
                            )}
                          </div>
                        )}

                        {/* Preis */}
                        <div className="space-y-1.5">
                          <Label className="text-xs text-muted-foreground">Stückpreis</Label>
                          <p className="h-9 flex items-center font-semibold">
                            € {formatPrice(item.rabattPreis || item.preis)} / {item.einheit}
                          </p>
                        </div>
                      </div>

                      {/* Staffel-Info und Zusatzkosten für lose Ware */}
                      {isBulk && (() => {
              const staffelInfo = getStaffelInfo(item, item.menge, staffelByProduct)
                        const staffelKosten = staffelInfo.zuschlag * item.menge
                        
                        return (
                          <div className="mt-3 pt-3 border-t border-dashed space-y-3">
                            {/* Kaufanreiz: Nächste günstigere Staffel */}
                            {staffelInfo.naechsteStaffel && (
                              <Alert className="py-2 border-emerald-200 bg-emerald-50">
                                <Info className="h-4 w-4 text-emerald-600" />
                                <AlertDescription className="text-emerald-800 text-sm">
                                  <strong>Tipp:</strong> Sie erreichen die nächst günstigere Preisstaffel ab{' '}
                                  <span className="font-bold">{staffelInfo.naechsteStaffel.abMenge} {item.einheit}</span>.
                                  <br />
                                  <span className="text-emerald-600">
                                    Ersparnis: € {formatPrice(staffelInfo.naechsteStaffel.ersparnis)}/{item.einheit}
                                  </span>
                                </AlertDescription>
                              </Alert>
                            )}

                            {/* Staffel erreicht */}
                            {!staffelInfo.naechsteStaffel && staffelInfo.zuschlag === 0 && (
                              <Alert className="py-2 border-emerald-200 bg-emerald-50">
                                <Check className="h-4 w-4 text-emerald-600" />
                                <AlertDescription className="text-emerald-800 text-sm">
                                  <strong>Beste Staffel erreicht!</strong> Kein Mengenzuschlag.
                                </AlertDescription>
                              </Alert>
                            )}

                            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                              {/* Staffelzuschlag (automatisch berechnet, nicht editierbar) */}
                              {staffelInfo.zuschlag > 0 && (
                                <div className="space-y-1.5">
                                  <Label className="text-xs text-muted-foreground">Mengenzuschlag</Label>
                                  <div className="h-9 flex items-center text-sm text-amber-700 bg-amber-50 rounded-md px-3">
                                    € {formatPrice(staffelInfo.zuschlag)}/{item.einheit}
                                    <span className="ml-1 text-xs text-muted-foreground">
                                      (= € {formatPrice(staffelKosten)})
                                    </span>
                                  </div>
                                </div>
                              )}

                              {/* Frachtkosten (nur bei Lieferung) */}
                              {item.deliveryParity !== 'ab_lager' && (
                                <div className="space-y-1.5">
                                  <Label className="text-xs text-muted-foreground">Frachtkosten (€)</Label>
                                  <Input
                                    type="number"
                                    min={0}
                                    step={1}
                                    placeholder="15"
                                    value={item.frachtkosten || ''}
                                    onChange={(e) => updateCartFracht(item.id, e.target.value ? parseFloat(e.target.value) : undefined)}
                                    className="h-9"
                                  />
                                </div>
                              )}

                              {/* Positionssumme */}
                              <div className="space-y-1.5 sm:col-span-2">
                                <Label className="text-xs text-muted-foreground">Position Gesamt</Label>
                                <div className="h-9 flex items-center flex-wrap gap-x-2 gap-y-1 text-sm">
                                  <span>{item.menge} {item.einheit}</span>
                                  <span className="text-muted-foreground">×</span>
                                  <span>€ {formatPrice(item.rabattPreis || item.preis)}</span>
                                  {staffelInfo.zuschlag > 0 && (
                                    <>
                                      <span className="text-muted-foreground">+</span>
                                      <span className="text-amber-700">€ {formatPrice(staffelKosten)} Staffel</span>
                                    </>
                                  )}
                                  {item.frachtkosten && item.deliveryParity !== 'ab_lager' && (
                                    <>
                                      <span className="text-muted-foreground">+</span>
                                      <span>€ {formatPrice(item.frachtkosten)} Fracht</span>
                                    </>
                                  )}
                                  <span className="text-muted-foreground">=</span>
                                  <span className="font-semibold">
                                    € {formatPrice(
                                      (item.rabattPreis || item.preis) * item.menge +
                                      staffelKosten +
                                      (item.deliveryParity !== 'ab_lager' ? (item.frachtkosten || 0) : 0)
                                    )}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        )
                      })()}
                    </div>
                  )
                })}
              </div>

              {cart.length > 0 && (
                <>
                  <div className="border-t pt-4 space-y-2">
                    {/* Gesamt-Bestellmenge pro Einheit */}
                    <div className="flex flex-wrap gap-4 mb-3">
                      <span className="text-sm font-medium text-muted-foreground">Gesamt-Bestellmenge:</span>
                      {Object.entries(cartQuantityByUnit).map(([unit, qty]) => (
                        <Badge key={unit} variant="secondary" className="text-sm">
                          {qty} {unit}
                        </Badge>
                      ))}
                    </div>

                    {/* Kostenaufstellung */}
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Warenwert</span>
                        <span>€ {formatPrice(cartWarenwert)}</span>
                      </div>
                      {cartStaffelGesamt > 0 && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Staffelzuschläge</span>
                          <span>€ {formatPrice(cartStaffelGesamt)}</span>
                        </div>
                      )}
                      {cartFrachtGesamt > 0 && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Frachtkosten</span>
                          <span>€ {formatPrice(cartFrachtGesamt)}</span>
                        </div>
                      )}
                      <div className="flex justify-between text-base font-semibold pt-2 border-t">
                        <span>Bestellwert (netto)</span>
                        <span>€ {formatPrice(cartTotal)}</span>
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground">zzgl. MwSt.</p>
                  </div>

                  <DialogFooter className="flex-col sm:flex-row gap-2">
                    <Button variant="outline" onClick={() => setShowCart(false)}>
                      Weiter einkaufen
                    </Button>
                    <Button onClick={() => { void handleOrder() }} className="gap-2" disabled={orderSubmitting}>
                      <Send className="h-4 w-4" />
                      {orderSubmitting ? 'Sende...' : 'Bestellung absenden'}
                    </Button>
                  </DialogFooter>
                </>
              )}
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Anfrage Dialog */}
      <Dialog open={showAnfrage} onOpenChange={setShowAnfrage}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileQuestion className="h-5 w-5" />
              Anfrage stellen
            </DialogTitle>
            <DialogDescription>
              Stellen Sie eine Anfrage für ein Produkt oder einen Service
            </DialogDescription>
          </DialogHeader>

          {anfrageSuccess ? (
            <div className="flex flex-col items-center gap-4 py-8">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
                <Check className="h-8 w-8 text-emerald-600" />
              </div>
              <div className="text-center">
                <h3 className="text-lg font-semibold">Anfrage gesendet!</h3>
                <p className="text-muted-foreground">Wir melden uns schnellstmöglich bei Ihnen.</p>
              </div>
            </div>
          ) : (
            <>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="anfrage-produkt">Produkt / Kategorie</Label>
                  <NativeSelect
                    id="anfrage-produkt"
                    value={anfrageProdukt}
                    onValueChange={setAnfrageProdukt}
                    placeholder="Waehlen Sie eine Kategorie..."
                    options={portalAnfrageProduktOptions}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="anfrage-text">Ihre Anfrage</Label>
                  <Textarea
                    id="anfrage-text"
                    placeholder="Beschreiben Sie Ihre Anfrage..."
                    value={anfrageText}
                    onChange={(e) => setAnfrageText(e.target.value)}
                    rows={5}
                  />
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setShowAnfrage(false)}>
                  Abbrechen
                </Button>
                <Button
                  onClick={() => { void handleAnfrage() }}
                  disabled={!anfrageText || !anfrageProdukt || inquirySubmitting}
                  className="gap-2"
                >
                  <Send className="h-4 w-4" />
                  {inquirySubmitting ? 'Sende...' : 'Anfrage absenden'}
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

const REORDER_DAYS_CARD = 42 // Muss mit REORDER_DAYS übereinstimmen

// Hilfsfunktion: Formatiert Preis auf Deutsch (Komma als Dezimaltrenner)
function formatPrice(price: number): string {
  return price.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}


// Kontrakt-Status Badge Konfiguration
const contractStatusConfig: Record<ContractStatus, { label: string; color: string; icon: React.ReactNode }> = {
  NONE: { label: '', color: '', icon: null },
  ACTIVE: { label: 'Kontrakt aktiv', color: 'bg-emerald-100 text-emerald-800 border-emerald-200', icon: <FileText className="h-3 w-3" /> },
  LOW: { label: 'Kontrakt fast ausgeschöpft', color: 'bg-orange-100 text-orange-800 border-orange-200', icon: <AlertTriangle className="h-3 w-3" /> },
  EXHAUSTED: { label: 'Kontrakt ausgeschöpft', color: 'bg-gray-100 text-gray-600 border-gray-200', icon: <FileText className="h-3 w-3" /> },
}

function ProductCard({
  product,
  onAddToCart,
  inCart,
}: {
  product: Product
  onAddToCart: () => void
  inCart: boolean
}) {
  const kategorieIcons: Record<string, React.ReactNode> = {
    saatgut: <Wheat className="h-8 w-8" />,
    duenger: <Droplets className="h-8 w-8" />,
    psm: <Bug className="h-8 w-8" />,
    futtermittel: <Leaf className="h-8 w-8" />,
    sonstiges: <Package className="h-8 w-8" />,
  }

  // Prüfe ob kürzlich bestellt (innerhalb der letzten 42 Tage)
  const recentlyOrdered = product.letzteBestellung && isWithinDays(product.letzteBestellung.datum, REORDER_DAYS_CARD)

  // Berechne Tage seit letzter Bestellung
  const daysSinceOrder = product.letzteBestellung
    ? Math.floor((new Date().getTime() - new Date(product.letzteBestellung.datum).getTime()) / (1000 * 60 * 60 * 24))
    : null

  // Kontrakt-Logik
  const contractStatusKey: ContractStatus = product.contractStatus ?? 'NONE'
  const hasContract = contractStatusKey !== 'NONE'
  const contractRemaining = product.contractRemainingQty ?? 0
  const contractTotal = product.contractTotalQty ?? 0
  const contractPercent = contractTotal > 0 ? (contractRemaining / contractTotal) * 100 : 0

  // Vorkauf-Logik
  const hasPrePurchase = product.isPrePurchase && product.prePurchaseRemainingQty && product.prePurchaseRemainingQty > 0
  const prePurchaseRemaining = product.prePurchaseRemainingQty ?? 0
  const prePurchaseTotal = product.prePurchaseTotalQty ?? 0
  const prePurchasePercent = prePurchaseTotal > 0 ? (prePurchaseRemaining / prePurchaseTotal) * 100 : 0
  const prePurchaseLow = prePurchasePercent < 20
  return (
    <TooltipProvider>
      <Card className={cn(
        'transition-all hover:shadow-md flex flex-col',
        !product.verfuegbar && 'opacity-60',
        recentlyOrdered && 'ring-2 ring-blue-200 ring-offset-2',
        hasPrePurchase && 'ring-2 ring-purple-200 ring-offset-2',
        hasContract && product.contractStatus === 'ACTIVE' && !hasPrePurchase && 'ring-2 ring-emerald-200 ring-offset-2'
      )}>
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between gap-1">
            <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-muted text-muted-foreground">
              {kategorieIcons[product.kategorie] || <Package className="h-8 w-8" />}
            </div>
            <div className="flex flex-col items-end gap-1">
              {/* Vorkauf Badge (hat Vorrang) */}
              {hasPrePurchase && (
                <Tooltip>
                  <TooltipTrigger>
                    <Badge className={cn(
                      'text-xs gap-1 border',
                      prePurchaseLow 
                        ? 'bg-orange-100 text-orange-800 border-orange-200 hover:bg-orange-200'
                        : 'bg-purple-100 text-purple-800 border-purple-200 hover:bg-purple-200'
                    )}>
                      <Wallet className="h-3 w-3" />
                      Vorkauf-Guthaben
                    </Badge>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Rest: {prePurchaseRemaining} {product.einheit} von {prePurchaseTotal} {product.einheit}</p>
                    <p>Vorkaufpreis: € {formatPrice((product.prePurchasePrice ?? 0))} pro {product.einheit}</p>
                  </TooltipContent>
                </Tooltip>
              )}
              
              {/* Kontrakt Badge (wenn kein Vorkauf) */}
              {!hasPrePurchase && hasContract && (
                <Tooltip>
                  <TooltipTrigger>
                    <Badge className={cn('text-xs gap-1 border', contractStatusConfig[contractStatusKey].color)}>
                      {contractStatusConfig[contractStatusKey].icon}
                      {contractStatusConfig[contractStatusKey].label}
                    </Badge>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Restmenge: {contractRemaining} {product.einheit} von {contractTotal} {product.einheit}</p>
                    <p>Vertragspreis: € {formatPrice((product.contractPrice ?? product.preis))} pro {product.einheit}</p>
                  </TooltipContent>
                </Tooltip>
              )}

              {/* Erneut bestellen Badge */}
              {recentlyOrdered && (
                <Badge className="bg-blue-600 text-xs hover:bg-blue-700 gap-1">
                  <RotateCcw className="h-3 w-3" />
                  Erneut bestellen
                </Badge>
              )}
              
              {/* Aktion Badge */}
              {product.rabattPreis && !hasPrePurchase && !hasContract && (
                <Badge variant="destructive" className="text-xs">
                  AKTION
                </Badge>
              )}
            </div>
          </div>
          <CardTitle className="mt-2 text-base">{product.name}</CardTitle>
          <CardDescription className="text-xs">{product.artikelnummer}</CardDescription>
          {recentlyOrdered && daysSinceOrder !== null && (
            <p className="text-xs text-blue-600">
              Zuletzt bestellt: vor {daysSinceOrder} Tag{daysSinceOrder !== 1 ? 'en' : ''} ({(product.letzteBestellung?.menge ?? 0)} {product.einheit})
            </p>
          )}
        </CardHeader>
        
        <CardContent className="pb-2 flex-grow">
          <p className="line-clamp-2 text-sm text-muted-foreground">{product.beschreibung}</p>
          {product.zertifikate.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {product.zertifikate.map((z) => (
                <Badge key={z} variant="secondary" className="text-xs">
                  {z}
                </Badge>
              ))}
            </div>
          )}
        </CardContent>

        {/* Preis- und Vertragsbereich */}
        <CardFooter className="flex flex-col gap-3 border-t pt-4">
          {/* Vorkauf-Darstellung */}
          {hasPrePurchase && (
            <div className="w-full space-y-2">
              <div className="flex justify-between items-baseline">
                <span className="text-xs text-muted-foreground">Vorkauf-Guthaben</span>
                <span className="text-sm font-semibold">
                  {prePurchaseRemaining} {product.einheit} von {prePurchaseTotal} {product.einheit}
                </span>
              </div>
              <Progress 
                value={prePurchasePercent} 
                className={cn('h-2', prePurchaseLow ? '[&>div]:bg-orange-500' : '[&>div]:bg-purple-500')} 
              />
              {prePurchaseLow && (
                <p className="text-xs text-orange-600">Nur noch {Math.round(prePurchasePercent)}% übrig</p>
              )}
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-xs text-muted-foreground">Vorkaufpreis (bereits bezahlt)</span>
                  <span className="text-sm font-bold text-purple-700">€ {formatPrice((product.prePurchasePrice ?? 0))}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-xs text-muted-foreground">Listenpreis</span>
                  <span className="text-xs text-muted-foreground line-through">€ {formatPrice(product.preis)}</span>
                </div>
                <div className="flex justify-between pt-1 border-t">
                  <span className="text-xs font-medium text-emerald-700">Jetzt fällig</span>
                  <span className="text-lg font-bold text-emerald-600">€ 0,00</span>
                </div>
                <p className="text-xs text-muted-foreground">(bei Abruf bis {prePurchaseRemaining} {product.einheit})</p>
              </div>
            </div>
          )}

          {/* Kontrakt-Darstellung (wenn kein Vorkauf) */}
          {!hasPrePurchase && hasContract && product.contractStatus !== 'EXHAUSTED' && (
            <div className="w-full space-y-2">
              <div className="flex justify-between items-baseline">
                <span className="text-xs text-muted-foreground">Rest Kontrakt</span>
                <span className="text-sm font-semibold">
                  {contractRemaining} {product.einheit} von {contractTotal} {product.einheit}
                </span>
              </div>
              <Progress 
                value={contractPercent} 
                className={cn('h-2', contractPercent < 20 ? '[&>div]:bg-orange-500' : '[&>div]:bg-emerald-500')} 
              />
              {contractPercent < 20 && (
                <p className="text-xs text-orange-600">Nur noch {Math.round(contractPercent)}% übrig</p>
              )}
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-xs text-muted-foreground">Kontraktpreis</span>
                  <span className="text-lg font-bold text-emerald-600">€ {formatPrice((product.contractPrice ?? product.preis))}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-xs text-muted-foreground">Listenpreis</span>
                  <span className="text-xs text-muted-foreground line-through">€ {formatPrice(product.preis)}</span>
                </div>
                <p className="text-xs text-muted-foreground">pro {product.einheit}</p>
              </div>
            </div>
          )}

          {/* Kontrakt ausgeschöpft */}
          {!hasPrePurchase && product.contractStatus === 'EXHAUSTED' && (
            <div className="w-full space-y-2">
              <div className="rounded-md bg-gray-100 p-2 text-center">
                <p className="text-xs text-gray-600 font-medium">Vertrag ausgeschöpft</p>
                <p className="text-xs text-gray-500">Bestellung zum Listenpreis</p>
              </div>
              <div className="flex justify-between items-baseline">
                <span className="text-xs text-muted-foreground">Listenpreis</span>
                <span className="text-lg font-bold">€ {formatPrice(product.preis)}</span>
              </div>
              <p className="text-xs text-muted-foreground">pro {product.einheit}</p>
            </div>
          )}

          {/* Standard-Preis (kein Kontrakt, kein Vorkauf) */}
          {!hasPrePurchase && !hasContract && (
            <div className="w-full">
              {product.rabattPreis ? (
                <div className="space-y-1">
                  <div className="flex justify-between items-baseline">
                    <span className="text-xs text-muted-foreground">Aktionspreis</span>
                    <span className="text-lg font-bold text-emerald-600">€ {formatPrice(product.rabattPreis)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-xs text-muted-foreground">Listenpreis</span>
                    <span className="text-xs text-muted-foreground line-through">€ {formatPrice(product.preis)}</span>
                  </div>
                </div>
              ) : (
                <div className="flex justify-between items-baseline">
                  <span className="text-xs text-muted-foreground">Listenpreis</span>
                  <span className="text-lg font-bold">€ {formatPrice(product.preis)}</span>
                </div>
              )}
              <p className="text-xs text-muted-foreground">pro {product.einheit}</p>
            </div>
          )}

          {/* Hinzufügen Button */}
          <Button
            size="sm"
            variant={inCart ? 'secondary' : 'default'}
            disabled={!product.verfuegbar}
            onClick={onAddToCart}
            className="w-full gap-1"
          >
            {!product.verfuegbar ? (
              'Ausverkauft'
            ) : inCart ? (
              <>
                <Check className="h-4 w-4" />
                Im Korb
              </>
            ) : (
              <>
                <Plus className="h-4 w-4" />
                Hinzufügen
              </>
            )}
          </Button>
        </CardFooter>
      </Card>
    </TooltipProvider>
  )
}

function ShopSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <Skeleton className="h-10 w-48" />
        <div className="flex gap-2">
          <Skeleton className="h-10 w-32" />
          <Skeleton className="h-10 w-32" />
        </div>
      </div>
      <div className="flex gap-4">
        <Skeleton className="h-10 flex-1" />
        <Skeleton className="h-10 w-96" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {[...Array(8)].map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-14 w-14 rounded-lg" />
              <Skeleton className="mt-2 h-5 w-32" />
              <Skeleton className="h-4 w-20" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-10 w-full" />
            </CardContent>
            <CardFooter className="border-t pt-4">
              <Skeleton className="h-8 w-20" />
              <Skeleton className="ml-auto h-9 w-24" />
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  )
}

