import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Euro, FileText, TrendingUp } from 'lucide-react'

export default function SubventionenDashboardPage(): JSX.Element {
  const subventionen = {
    jahr: 2025,
    beantragt: 45000,
    bewilligt: 40250,
    ausgezahlt: 38000,
    programme: [
      { name: 'Greening / Direktzahlungen', betrag: 21250, status: 'bewilligt' },
      { name: 'Biodiversität', betrag: 18960, status: 'in-pruefung' },
      { name: 'Agrarumwelt-Maßnahmen', betrag: 5040, status: 'ausgezahlt' },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Subventionen</h1>
        <p className="text-muted-foreground">Fördermittel-Dashboard {subventionen.jahr}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Beantragt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(subventionen.beantragt)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bewilligt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(subventionen.bewilligt)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ausgezahlt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(subventionen.ausgezahlt)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bewilligungsquote</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">
              {((subventionen.bewilligt / subventionen.beantragt) * 100).toFixed(1)}%
            </span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Programme & Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {subventionen.programme.map((programm, i) => (
              <div key={i} className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="font-semibold">{programm.name}</div>
                    <div className="text-sm text-muted-foreground mt-1">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(programm.betrag)}
                    </div>
                  </div>
                  <Badge variant={programm.status === 'ausgezahlt' ? 'outline' : programm.status === 'bewilligt' ? 'secondary' : 'default'}>
                    {programm.status === 'ausgezahlt' ? 'Ausgezahlt' : programm.status === 'bewilligt' ? 'Bewilligt' : 'In Prüfung'}
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
