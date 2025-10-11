import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, CheckCircle, Globe, MapPin } from 'lucide-react'

export default function EUDRCompliancePage(): JSX.Element {
  const eudr = {
    chargen: 245,
    konform: 238,
    pruefung: 5,
    nichtKonform: 2,
    laender: [
      { name: 'Brasilien', chargen: 120, konform: 115 },
      { name: 'Ukraine', chargen: 80, konform: 80 },
      { name: 'Deutschland', chargen: 45, konform: 45 },
    ],
  }

  const compliance = ((eudr.konform / eudr.chargen) * 100).toFixed(1)

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">EUDR-Compliance</h1>
        <p className="text-muted-foreground">Entwaldungsfreie Lieferketten</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Chargen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Globe className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{eudr.chargen}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Konform</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">{eudr.konform}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Prüfung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{eudr.pruefung}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Compliance-Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">{compliance}%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {eudr.nichtKonform > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{eudr.nichtKonform} Charge(n) sind NICHT EUDR-konform!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Herkunftsländer
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {eudr.laender.map((land, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">{land.name}</div>
                  <div className="text-sm text-muted-foreground">{land.chargen} Chargen</div>
                </div>
                <div className="text-right">
                  <div className="font-bold">{land.konform} / {land.chargen}</div>
                  <Badge variant={land.konform === land.chargen ? 'outline' : 'secondary'}>
                    {((land.konform / land.chargen) * 100).toFixed(0)}%
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
