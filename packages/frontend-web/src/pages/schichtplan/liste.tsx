import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Calendar, Clock, Users } from 'lucide-react'

export default function SchichtplanPage(): JSX.Element {
  const schichtplan = {
    heute: [
      { schicht: 'Früh (06-14)', mitarbeiter: ['Schmidt', 'Müller', 'Weber'], bereich: 'Annahme' },
      { schicht: 'Spät (14-22)', mitarbeiter: ['Koch', 'Bauer'], bereich: 'Annahme' },
      { schicht: 'Früh (06-14)', mitarbeiter: ['Fischer', 'Wagner', 'Hoffmann', 'Schulz'], bereich: 'Lager' },
    ],
    woche: 42,
    mitarbeiterHeute: 9,
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Schichtplan</h1>
          <p className="text-muted-foreground">
            KW {schichtplan.woche} • {new Date().toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>
        <Button>Plan bearbeiten</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Schichten Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{schichtplan.heute.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Mitarbeiter Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">{schichtplan.mitarbeiterHeute}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kalenderwoche</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              <span className="text-2xl font-bold">KW {schichtplan.woche}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Schichten Heute</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {schichtplan.heute.map((schicht, i) => (
              <div key={i} className="rounded-lg border p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <div className="font-semibold text-lg">{schicht.schicht}</div>
                    <Badge variant="outline" className="mt-1">{schicht.bereich}</Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    <span className="font-semibold">{schicht.mitarbeiter.length} Mitarbeiter</span>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {schicht.mitarbeiter.map((ma, j) => (
                    <Badge key={j} variant="secondary">{ma}</Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
