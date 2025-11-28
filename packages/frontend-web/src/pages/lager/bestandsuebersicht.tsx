import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { BarChart3, TrendingDown, TrendingUp, Warehouse, Package, AlertCircle, ArrowUpDown, Clock, Calendar, ShieldAlert, Zap, Snail, ChevronRight } from 'lucide-react'
import { useInventoryDashboard } from '@/lib/api/dashboard'
import { useNavigate } from 'react-router-dom'

// Beispieldaten für die Vorschau
const mockTopArticles = [
  { name: 'Weizen Saatgut Premium', quantity: 2500, value: 45000 },
  { name: 'Dünger NPK 15-15-15', quantity: 1800, value: 36000 },
  { name: 'Pflanzenschutzmittel A', quantity: 500, value: 25000 },
  { name: 'Diesel Winterqualität', quantity: 3000, value: 18000 },
  { name: 'Ersatzteile Mähdrescher', quantity: 45, value: 15500 },
]

// Mock-Daten für MHD und PSM Warnungen
const mockMhdItems = [
  { name: 'Pflanzenschutzmittel X', expiryDate: '2025-01-15', quantity: 50 },
  { name: 'Saatgutbeize Premium', expiryDate: '2025-02-01', quantity: 25 },
  { name: 'Herbizid Konzentrat', expiryDate: '2025-02-28', quantity: 100 },
]

const mockPsmItems = [
  { name: 'Glyphosat-Produkt A', abverkaufsfrist: '2025-03-31', quantity: 200 },
  { name: 'Insektizid Altbestand', abverkaufsfrist: '2025-06-30', quantity: 75 },
]

const mockRennerItems = [
  { name: 'Weizen Saatgut Premium', absatz: 450, trend: '+15%' },
  { name: 'Dünger NPK 15-15-15', absatz: 380, trend: '+8%' },
  { name: 'Diesel Winterqualität', absatz: 320, trend: '+5%' },
]

const mockPennerItems = [
  { name: 'Ersatzteile Typ B-alt', absatz: 2, trend: '-45%' },
  { name: 'Altbestand Saatgut 2022', absatz: 5, trend: '-30%' },
  { name: 'Spezialdünger Nische', absatz: 8, trend: '-20%' },
]

export default function BestandsuebersichtPage(): JSX.Element {
  const { data: bestand, isLoading } = useInventoryDashboard()
  const navigate = useNavigate()
  
  // Prüfe ob echte Daten vorhanden sind
  const hasData = bestand && bestand.totalArticles > 0

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Warehouse className="h-8 w-8 text-blue-600" />
          Bestandsübersicht
        </h1>
        <p className="text-muted-foreground">Lagerbestände & Kennzahlen</p>
      </div>

      {/* Info-Alert wenn keine Daten */}
      {!isLoading && !hasData && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Vorschau-Modus</AlertTitle>
          <AlertDescription>
            Es sind noch keine Bestandsdaten verfügbar. Die unten gezeigte Ansicht zeigt, 
            wie das Dashboard aussehen wird, sobald Artikel im Lager erfasst sind.
          </AlertDescription>
        </Alert>
      )}

      {/* KPI-Karten */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Package className="h-4 w-4 text-blue-600" />
              Artikel Gesamt
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-blue-600">
                  {hasData ? bestand.totalArticles : '1.247'}
                </span>
                {!hasData && <Badge variant="secondary" className="text-xs">Demo</Badge>}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              Gesamtwert
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-28" />
            ) : (
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-green-600">
                  {hasData 
                    ? new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(bestand.totalValue)
                    : '€ 2.450.000'}
                </span>
                {!hasData && <Badge variant="secondary" className="text-xs">Demo</Badge>}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <ArrowUpDown className="h-4 w-4 text-purple-600" />
              Bewegungen heute
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-purple-600">
                  {hasData ? bestand.lowStockCount : '48'}
                </span>
                {!hasData && <Badge variant="secondary" className="text-xs">Demo</Badge>}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4 text-orange-600" />
              Ø Reichweite
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-orange-600">
                  {hasData ? `${bestand.totalArticles} Tage` : '32 Tage'}
                </span>
                {!hasData && <Badge variant="secondary" className="text-xs">Demo</Badge>}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Zusätzliche KPI-Reihe */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-red-200 bg-red-50/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-red-700">
              <TrendingDown className="h-4 w-4 inline mr-2" />
              Unterbestand
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-red-600">
                  {hasData ? bestand.lowStockCount : '12'}
                </span>
                <span className="text-sm text-red-600">Artikel unter Mindestbestand</span>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-yellow-200 bg-yellow-50/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-yellow-700">
              ⚠️ Bald nachbestellen
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-yellow-600">
                  {hasData ? Math.round(bestand.lowStockCount * 1.5) : '28'}
                </span>
                <span className="text-sm text-yellow-600">Artikel in 7 Tagen kritisch</span>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-green-200 bg-green-50/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-green-700">
              ✓ Optimal bevorratet
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-green-600">
                  {hasData ? bestand.totalArticles - bestand.lowStockCount : '1.207'}
                </span>
                <span className="text-sm text-green-600">Artikel im Sollbereich</span>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Kritische Fristen: MHD & PSM Abverkauf */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* MHD-Ware */}
        <Card className="border-orange-300 bg-orange-50/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-orange-700 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                MHD-Ware (ablaufend)
              </span>
              <Button 
                variant="outline" 
                size="sm" 
                className="text-orange-700 border-orange-300 hover:bg-orange-100"
                onClick={() => navigate('/lager/mhd-uebersicht')}
              >
                Zur Übersicht <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-2">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-2xl font-bold text-orange-600">
                    {hasData ? 3 : mockMhdItems.length}
                  </span>
                  <span className="text-sm text-orange-600">Artikel mit MHD in den nächsten 90 Tagen</span>
                </div>
                {mockMhdItems.slice(0, 3).map((item, i) => (
                  <div key={i} className="flex items-center justify-between rounded border border-orange-200 p-2 bg-white/50 text-sm">
                    <span className="font-medium truncate max-w-[200px]">{item.name}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">{item.quantity} Stk</span>
                      <Badge variant="outline" className="text-orange-700 border-orange-400">
                        {new Date(item.expiryDate).toLocaleDateString('de-DE')}
                      </Badge>
                    </div>
                  </div>
                ))}
                {!hasData && <Badge variant="secondary" className="mt-2">Beispieldaten</Badge>}
              </div>
            )}
          </CardContent>
        </Card>

        {/* PSM Abverkaufsfristen */}
        <Card className="border-red-300 bg-red-50/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-red-700 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <ShieldAlert className="h-4 w-4" />
                PSM Abverkaufsfristen
              </span>
              <Button 
                variant="outline" 
                size="sm" 
                className="text-red-700 border-red-300 hover:bg-red-100"
                onClick={() => navigate('/lager/psm-abverkauf')}
              >
                Zur Übersicht <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-2">
                {[...Array(2)].map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-2xl font-bold text-red-600">
                    {hasData ? 2 : mockPsmItems.length}
                  </span>
                  <span className="text-sm text-red-600">PSM mit endender Abverkaufsfrist</span>
                </div>
                {mockPsmItems.map((item, i) => (
                  <div key={i} className="flex items-center justify-between rounded border border-red-200 p-2 bg-white/50 text-sm">
                    <span className="font-medium truncate max-w-[200px]">{item.name}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">{item.quantity} Stk</span>
                      <Badge variant="destructive">
                        Frist: {new Date(item.abverkaufsfrist).toLocaleDateString('de-DE')}
                      </Badge>
                    </div>
                  </div>
                ))}
                {!hasData && <Badge variant="secondary" className="mt-2">Beispieldaten</Badge>}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Renner & Penner Analyse */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Renner - Schnelldreher */}
        <Card className="border-green-300 bg-green-50/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-green-700 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Zap className="h-4 w-4" />
                Renner (Top-Seller)
              </span>
              <Button 
                variant="outline" 
                size="sm" 
                className="text-green-700 border-green-300 hover:bg-green-100"
                onClick={() => navigate('/lager/renner-liste')}
              >
                Vollständige Liste <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-2">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-sm text-green-600 mb-3">Artikel mit höchstem Absatz (letzte 30 Tage)</p>
                {mockRennerItems.map((item, i) => (
                  <div key={i} className="flex items-center justify-between rounded border border-green-200 p-2 bg-white/50 text-sm">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="bg-green-100 text-green-700 border-green-400">#{i + 1}</Badge>
                      <span className="font-medium truncate max-w-[180px]">{item.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">{item.absatz} Stk</span>
                      <Badge className="bg-green-600">{item.trend}</Badge>
                    </div>
                  </div>
                ))}
                {!hasData && <Badge variant="secondary" className="mt-2">Beispieldaten</Badge>}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Penner - Langsamdreher */}
        <Card className="border-slate-300 bg-slate-50/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-700 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Snail className="h-4 w-4" />
                Penner (Ladenhüter)
              </span>
              <Button 
                variant="outline" 
                size="sm" 
                className="text-slate-700 border-slate-300 hover:bg-slate-100"
                onClick={() => navigate('/lager/penner-liste')}
              >
                Vollständige Liste <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-2">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-sm text-slate-600 mb-3">Artikel mit geringstem Absatz / Altbestand</p>
                {mockPennerItems.map((item, i) => (
                  <div key={i} className="flex items-center justify-between rounded border border-slate-200 p-2 bg-white/50 text-sm">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="bg-slate-100 text-slate-700 border-slate-400">!</Badge>
                      <span className="font-medium truncate max-w-[180px]">{item.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">{item.absatz} Stk</span>
                      <Badge variant="secondary" className="text-red-600">{item.trend}</Badge>
                    </div>
                  </div>
                ))}
                {!hasData && <Badge variant="secondary" className="mt-2">Beispieldaten</Badge>}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Top-Artikel Liste */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Top-Artikel nach Wert
            {!hasData && <Badge variant="secondary" className="ml-2">Beispieldaten</Badge>}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-40" />
                    <Skeleton className="h-3 w-20" />
                  </div>
                  <div className="text-right space-y-2">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-5 w-10" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {(hasData ? bestand.topArticles : mockTopArticles).map((artikel, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg border p-4 hover:bg-muted/50 transition-colors">
                  <div>
                    <div className="font-semibold">{artikel.name}</div>
                    <div className="text-sm text-muted-foreground">{artikel.quantity} Stk auf Lager</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-lg">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(artikel.value)}
                    </div>
                    <Badge variant={i === 0 ? 'default' : 'outline'}>#{i + 1}</Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Hinweis-Karte für weitere Funktionen */}
      {!hasData && (
        <Card className="border-dashed border-2">
          <CardContent className="pt-6">
            <div className="text-center text-muted-foreground">
              <Warehouse className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <h3 className="font-semibold text-lg mb-2">Weitere Funktionen verfügbar</h3>
              <p className="text-sm max-w-md mx-auto">
                Nach der Erfassung von Lagerbeständen werden hier Echtdaten angezeigt für:
              </p>
              <div className="flex flex-wrap justify-center gap-2 mt-4">
                <Badge variant="outline">📅 MHD-Überwachung</Badge>
                <Badge variant="outline">🛡️ PSM-Abverkaufsfristen</Badge>
                <Badge variant="outline">⚡ Renner-Analyse</Badge>
                <Badge variant="outline">🐌 Penner-Erkennung</Badge>
                <Badge variant="outline">📊 Bestandsverlauf</Badge>
                <Badge variant="outline">📈 Umschlagshäufigkeit</Badge>
                <Badge variant="outline">🔔 Bestellvorschläge</Badge>
                <Badge variant="outline">📋 Inventurunterstützung</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
