import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Zap, TrendingDown } from 'lucide-react'

export default function EnergieverbrauchPage(): JSX.Element {
  const verbrauch = {
    heute: {
      strom: 1250,
      gas: 840,
    },
    monat: {
      strom: 35200,
      gas: 22800,
      zielStrom: 38000,
      zielGas: 25000,
    },
  }

  const stromEinsparung = ((1 - verbrauch.monat.strom / verbrauch.monat.zielStrom) * 100).toFixed(1)
  const gasEinsparung = ((1 - verbrauch.monat.gas / verbrauch.monat.zielGas) * 100).toFixed(1)

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Energieverbrauch</h1>
        <p className="text-muted-foreground">Monitoring & Controlling</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Strom Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-yellow-600" />
              <span className="text-2xl font-bold">{verbrauch.heute.strom} kWh</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gas Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{verbrauch.heute.gas} kWh</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Strom-Einsparung</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">{stromEinsparung}%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gas-Einsparung</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">{gasEinsparung}%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Monatsverbrauch (Soll/Ist)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="rounded-lg border p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-lg">Strom</span>
                <Badge variant="outline" className="text-green-600">-{stromEinsparung}% vs. Ziel</Badge>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">Ist</div>
                  <div className="text-2xl font-bold">{verbrauch.monat.strom.toLocaleString('de-DE')} kWh</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Ziel</div>
                  <div className="text-2xl font-bold text-muted-foreground">{verbrauch.monat.zielStrom.toLocaleString('de-DE')} kWh</div>
                </div>
              </div>
            </div>
            <div className="rounded-lg border p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-lg">Gas</span>
                <Badge variant="outline" className="text-green-600">-{gasEinsparung}% vs. Ziel</Badge>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">Ist</div>
                  <div className="text-2xl font-bold">{verbrauch.monat.gas.toLocaleString('de-DE')} kWh</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Ziel</div>
                  <div className="text-2xl font-bold text-muted-foreground">{verbrauch.monat.zielGas.toLocaleString('de-DE')} kWh</div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
