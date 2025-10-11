import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, Euro, FileText, TrendingUp } from 'lucide-react'

export default function OPVerwaltungPage(): JSX.Element {
  const navigate = useNavigate()

  const opData = {
    debitoren: {
      gesamt: 3,
      summe: 36450,
      ueberfaellig: 1,
      mahnungen: 1,
    },
    kreditoren: {
      gesamt: 3,
      summe: 39550,
      zahlbar: 2,
      skonto: 2,
    },
    liquiditaet: {
      bank: 285000,
      erwarteteEingaenge: 36450,
      falligeAusgaben: 27250,
      prognose: 294200,
    },
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Offene Posten Verwaltung</h1>
        <p className="text-muted-foreground">Überblick Debitoren & Kreditoren</p>
      </div>

      {opData.debitoren.ueberfaellig > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{opData.debitoren.ueberfaellig} überfällige Debitorenrechnung(en)!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offene Forderungen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.debitoren.summe)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offene Verbindlichkeiten</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold text-blue-600">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.kreditoren.summe)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Liquidität (Bank)</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.bank)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Prognose</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.prognose)}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* DEBITOREN */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl flex items-center justify-between">
              <span>Debitoren (Forderungen)</span>
              <Button onClick={() => navigate('/fibu/debitoren')}>Details</Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border p-4">
              <div className="flex justify-between items-center mb-3">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-orange-600" />
                  <span className="font-semibold">Offene Posten</span>
                </div>
                <Badge variant="outline">{opData.debitoren.gesamt}</Badge>
              </div>
              <div className="text-3xl font-bold text-orange-600">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.debitoren.summe)}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border p-3">
                <div className="text-sm text-muted-foreground mb-1">Überfällig</div>
                <div className="text-2xl font-bold text-red-600">{opData.debitoren.ueberfaellig}</div>
              </div>
              <div className="rounded-lg border p-3">
                <div className="text-sm text-muted-foreground mb-1">In Mahnung</div>
                <div className="text-2xl font-bold text-red-600">{opData.debitoren.mahnungen}</div>
              </div>
            </div>

            <div className="rounded-lg bg-orange-50 p-4 text-center">
              <div className="text-sm text-muted-foreground mb-1">Erwartete Zahlungseingänge</div>
              <div className="text-xl font-bold text-orange-900">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.erwarteteEingaenge)}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* KREDITOREN */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl flex items-center justify-between">
              <span>Kreditoren (Verbindlichkeiten)</span>
              <Button onClick={() => navigate('/fibu/kreditoren')}>Details</Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border p-4">
              <div className="flex justify-between items-center mb-3">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-blue-600" />
                  <span className="font-semibold">Offene Posten</span>
                </div>
                <Badge variant="outline">{opData.kreditoren.gesamt}</Badge>
              </div>
              <div className="text-3xl font-bold text-blue-600">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.kreditoren.summe)}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border p-3">
                <div className="text-sm text-muted-foreground mb-1">Zahlbar</div>
                <div className="text-2xl font-bold text-green-600">{opData.kreditoren.zahlbar}</div>
              </div>
              <div className="rounded-lg border p-3">
                <div className="text-sm text-muted-foreground mb-1">Skonto verfügbar</div>
                <div className="text-2xl font-bold text-green-600">{opData.kreditoren.skonto}</div>
              </div>
            </div>

            <div className="rounded-lg bg-blue-50 p-4 text-center">
              <div className="text-sm text-muted-foreground mb-1">Fällige Zahlungen</div>
              <div className="text-xl font-bold text-blue-900">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.falligeAusgaben)}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* LIQUIDITÄTSPROGNOSE */}
      <Card>
        <CardHeader>
          <CardTitle>Liquiditätsprognose (30 Tage)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between border-b pb-2">
              <span className="font-semibold">Aktuelle Liquidität (Bank)</span>
              <span className="font-bold text-green-600">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.bank)}
              </span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span>+ Erwartete Zahlungseingänge</span>
              <span className="text-green-600">
                + {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.erwarteteEingaenge)}
              </span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span>- Fällige Zahlungen</span>
              <span className="text-red-600">
                - {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.falligeAusgaben)}
              </span>
            </div>
            <div className="flex justify-between pt-3 border-t-2">
              <span className="text-xl font-bold">= Prognostizierte Liquidität</span>
              <span className="text-xl font-bold text-green-600">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.prognose)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
