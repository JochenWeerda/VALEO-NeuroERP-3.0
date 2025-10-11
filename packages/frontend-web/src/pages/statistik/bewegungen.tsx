import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowDownCircle, ArrowUpCircle, BarChart3, TrendingUp } from 'lucide-react'

export default function BewegungenStatistikPage(): JSX.Element {
  const bewegungen = {
    heute: {
      eingaenge: 12,
      ausgaenge: 18,
      umlagerungen: 3,
    },
    woche: {
      eingaenge: 85,
      ausgaenge: 102,
    },
    topArtikel: [
      { artikel: 'Weizen Premium', eingaenge: 125, ausgaenge: 98, netto: 27 },
      { artikel: 'Sojaschrot 44%', eingaenge: 68, ausgaenge: 95, netto: -27 },
      { artikel: 'NPK-Dünger', eingaenge: 42, ausgaenge: 55, netto: -13 },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Lagerbewegungen</h1>
        <p className="text-muted-foreground">Statistik & Analyse</p>
      </div>

      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Eingänge Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <ArrowDownCircle className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">{bewegungen.heute.eingaenge}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ausgänge Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <ArrowUpCircle className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold text-blue-600">{bewegungen.heute.ausgaenge}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Umlagerungen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{bewegungen.heute.umlagerungen}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Woche Eingänge</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{bewegungen.woche.eingaenge}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Woche Ausgänge</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-blue-600">{bewegungen.woche.ausgaenge}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Top-Artikel (Woche)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {bewegungen.topArtikel.map((artikel, i) => (
              <div key={i} className="rounded-lg border p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="font-semibold">{artikel.artikel}</div>
                  <div className="flex items-center gap-2">
                    {artikel.netto > 0 ? (
                      <TrendingUp className="h-4 w-4 text-green-600" />
                    ) : (
                      <ArrowUpCircle className="h-4 w-4 text-blue-600" />
                    )}
                    <Badge variant={artikel.netto > 0 ? 'outline' : 'secondary'}>
                      {artikel.netto > 0 ? '+' : ''}{artikel.netto} t
                    </Badge>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Eingänge:</span>
                    <span className="font-semibold text-green-600">{artikel.eingaenge} t</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Ausgänge:</span>
                    <span className="font-semibold text-blue-600">{artikel.ausgaenge} t</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
