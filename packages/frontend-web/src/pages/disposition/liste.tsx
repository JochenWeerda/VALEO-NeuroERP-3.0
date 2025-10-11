import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { AlertTriangle, BarChart3, CheckCircle } from 'lucide-react'

type DispoPosition = {
  id: string
  artikel: string
  bestand: number
  mindestbestand: number
  bedarf: number
  empfehlung: string
  prioritaet: 'hoch' | 'normal'
}

const mockDispo: DispoPosition[] = [
  { id: '1', artikel: 'Weizen Premium', bestand: 120, mindestbestand: 200, bedarf: 80, empfehlung: 'Nachbestellen: 100 t', prioritaet: 'hoch' },
  { id: '2', artikel: 'Sojaschrot 44%', bestand: 180, mindestbestand: 150, bedarf: 0, empfehlung: 'Ausreichend', prioritaet: 'normal' },
  { id: '3', artikel: 'NPK-Dünger', bestand: 80, mindestbestand: 100, bedarf: 50, empfehlung: 'Nachbestellen: 50 t', prioritaet: 'normal' },
]

export default function DispositionPage(): JSX.Element {
  const navigate = useNavigate()

  const unterMindest = mockDispo.filter((d) => d.bestand < d.mindestbestand).length

  const columns = [
    { key: 'artikel' as const, label: 'Artikel' },
    {
      key: 'bestand' as const,
      label: 'Bestand',
      render: (d: DispoPosition) => (
        <span className={d.bestand < d.mindestbestand ? 'font-semibold text-red-600' : ''}>
          {d.bestand} t
        </span>
      ),
    },
    { key: 'mindestbestand' as const, label: 'Mindest', render: (d: DispoPosition) => `${d.mindestbestand} t` },
    { key: 'bedarf' as const, label: 'Bedarf', render: (d: DispoPosition) => d.bedarf > 0 ? `${d.bedarf} t` : '-' },
    {
      key: 'empfehlung' as const,
      label: 'Empfehlung',
      render: (d: DispoPosition) => (
        <div className="flex items-center gap-2">
          {d.bedarf > 0 ? (
            <AlertTriangle className="h-4 w-4 text-orange-600" />
          ) : (
            <CheckCircle className="h-4 w-4 text-green-600" />
          )}
          <span>{d.empfehlung}</span>
        </div>
      ),
    },
    {
      key: 'prioritaet' as const,
      label: 'Priorität',
      render: (d: DispoPosition) => (
        <Badge variant={d.prioritaet === 'hoch' ? 'destructive' : 'outline'}>
          {d.prioritaet === 'hoch' ? 'Hoch' : 'Normal'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Disposition</h1>
          <p className="text-muted-foreground">Bedarfsplanung</p>
        </div>
        <Button onClick={() => navigate('/einkauf/bestellvorschlaege')}>Zu Bestellvorschlägen</Button>
      </div>

      {unterMindest > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{unterMindest} Artikel unter Mindestbestand!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Artikel in Dispo</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockDispo.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Unter Mindestbestand</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{unterMindest}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Hohe Priorität</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{mockDispo.filter((d) => d.prioritaet === 'hoch').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Bedarf</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockDispo.reduce((sum, d) => sum + d.bedarf, 0)} t</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockDispo} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
