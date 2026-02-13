import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useFoerderAntraege } from '@/lib/api/betrieb'
import { Euro, FileText, TrendingUp } from 'lucide-react'

export default function SubventionenDashboardPage(): JSX.Element {
  const { data: antraege, isLoading } = useFoerderAntraege()

  if (isLoading) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <div><Skeleton className="h-9 w-48" /><Skeleton className="mt-2 h-5 w-64" /></div>
        <div className="grid gap-4 md:grid-cols-4">
          {[1,2,3,4].map(i => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  const items = antraege ?? []
  const beantragt = items.reduce((s, a) => s + a.betrag, 0)
  const bewilligt = items.filter(a => a.status === 'bewilligt' || a.status === 'eingereicht').reduce((s, a) => s + a.betrag, 0)
  const ausgezahlt = items.filter(a => a.status === 'bewilligt').reduce((s, a) => s + a.betrag, 0)
  const quote = beantragt > 0 ? ((bewilligt / beantragt) * 100).toFixed(1) : '0.0'

  const programme = items.map(a => ({
    name: a.programm,
    betrag: a.betrag,
    status: a.status === 'bewilligt' ? 'ausgezahlt' : a.status === 'eingereicht' ? 'in-pruefung' : a.status,
  }))

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Subventionen</h1>
        <p className="text-muted-foreground">Foerdermittel-Dashboard {new Date().getFullYear()}</p>
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
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(beantragt)}
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
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(bewilligt)}
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
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(ausgezahlt)}
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
              {quote}%
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
            {programme.map((programm, i) => (
              <div key={i} className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="font-semibold">{programm.name}</div>
                    <div className="text-sm text-muted-foreground mt-1">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(programm.betrag)}
                    </div>
                  </div>
                  <Badge variant={programm.status === 'ausgezahlt' ? 'outline' : programm.status === 'bewilligt' ? 'secondary' : 'default'}>
                    {programm.status === 'ausgezahlt' ? 'Ausgezahlt' : programm.status === 'bewilligt' ? 'Bewilligt' : 'In Pruefung'}
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
