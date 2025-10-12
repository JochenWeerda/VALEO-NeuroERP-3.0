import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { BarChart3, TrendingDown, TrendingUp, Warehouse, Loader2 } from 'lucide-react'
import { useInventoryDashboard } from '@/lib/api/dashboard'

export default function BestandsuebersichtPage(): JSX.Element {
  const { data: bestand, isLoading } = useInventoryDashboard()
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }
  
  if (!bestand) {
    return <div>Keine Daten verfügbar</div>
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Bestandsübersicht</h1>
        <p className="text-muted-foreground">Lagerbestände & Kennzahlen</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Artikel Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Warehouse className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{bestand.totalArticles}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtwert</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(bestand.totalValue)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bewegungen heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">{bestand.lowStockCount}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Reichweite (Tage)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold">{bestand.totalArticles}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Top-Artikel nach Wert
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {bestand.topArticles.map((artikel, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">{artikel.name}</div>
                  <div className="text-sm text-muted-foreground">{artikel.quantity} Stk</div>
                </div>
                <div className="text-right">
                  <div className="font-bold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(artikel.value)}
                  </div>
                  <Badge variant="outline">#{i + 1}</Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
