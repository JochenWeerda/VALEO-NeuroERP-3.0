import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Calendar, Plus } from 'lucide-react'

export default function TerminKalenderPage(): JSX.Element {
  const termine = {
    heute: [
      { zeit: '09:00', titel: 'Lieferanten-Gespräch', typ: 'Meeting', dauer: '1h' },
      { zeit: '14:00', titel: 'Qualitäts-Audit', typ: 'Audit', dauer: '2h' },
    ],
    dieseWoche: 12,
    naechsteWoche: 8,
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Termin-Kalender</h1>
          <p className="text-muted-foreground">{new Date().toLocaleDateString('de-DE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Termin
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Termine Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{termine.heute.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Diese Woche</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{termine.dieseWoche}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Nächste Woche</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{termine.naechsteWoche}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Termine Heute</CardTitle>
        </CardHeader>
        <CardContent>
          {termine.heute.length > 0 ? (
            <div className="space-y-3">
              {termine.heute.map((termin, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <div className="font-mono font-bold text-lg">{termin.zeit}</div>
                  </div>
                  <div className="flex-1 ml-4">
                    <div className="font-semibold">{termin.titel}</div>
                    <div className="text-sm text-muted-foreground">{termin.dauer}</div>
                  </div>
                  <Badge variant="outline">{termin.typ}</Badge>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground">Keine Termine</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
