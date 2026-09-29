import { useMemo, useState } from 'react'
import { useBenachrichtigungen, type Benachrichtigung } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Bell, CheckCircle } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'
import { useTouchDevice } from '@/hooks/useTouchDevice'

export default function BenachrichtigungenPage(): JSX.Element {
  const isTouch = useTouchDevice()
  const { data: benachrichtigungen = [], isError, error, refetch } = useBenachrichtigungen()
  const [gelesenIds, setGelesenIds] = useState<Set<string>>(new Set())

  const sichtbare = useMemo(
    () => benachrichtigungen.map((b) => (gelesenIds.has(b.id) ? { ...b, gelesen: true } : b)),
    [benachrichtigungen, gelesenIds],
  )

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  function markGelesen(id: string): void {
    setGelesenIds((prev) => {
      const next = new Set(prev)
      next.add(id)
      return next
    })
  }

  function markAlleGelesen(): void {
    setGelesenIds(new Set(sichtbare.filter((b) => !b.gelesen).map((b) => b.id)))
  }

  const columns = [
    {
      key: 'titel' as const,
      label: 'Titel',
      render: (b: Benachrichtigung) => (
        <div>
          <div className={`font-medium ${!b.gelesen ? 'font-bold' : ''}`}>{b.titel}</div>
          <div className="text-sm text-muted-foreground">{b.nachricht}</div>
        </div>
      ),
    },
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (b: Benachrichtigung) => (
        <Badge variant={b.typ === 'fehler' ? 'destructive' : b.typ === 'warnung' ? 'secondary' : 'outline'}>
          {b.typ === 'info' ? 'Info' : b.typ === 'warnung' ? 'Warnung' : 'Fehler'}
        </Badge>
      ),
    },
    {
      key: 'zeitstempel' as const,
      label: 'Zeit',
      render: (b: Benachrichtigung) => <span className="font-mono text-sm">{b.zeitstempel}</span>,
    },
    {
      key: 'gelesen' as const,
      label: 'Status',
      render: (b: Benachrichtigung) =>
        b.gelesen ? (
          <Badge variant="outline">
            <CheckCircle className="mr-1 inline h-3 w-3" />
            Gelesen
          </Badge>
        ) : (
          <Badge variant="default">Neu</Badge>
        ),
    },
    {
      key: 'actions' as const,
      label: 'Aktionen',
      render: (b: Benachrichtigung) => (
        <Button
          variant="outline"
          className="min-h-touch touch-manipulation"
          disabled={b.gelesen}
          onClick={() => markGelesen(b.id)}
        >
          Als gelesen markieren
        </Button>
      ),
    },
  ]

  const ungelesen = sichtbare.filter((b) => !b.gelesen).length

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Benachrichtigungen</h1>
          <p className="text-muted-foreground">Nachrichten lesen und als gelesen markieren</p>
        </div>
        <Button
          variant="outline"
          className="min-h-touch touch-manipulation"
          disabled={ungelesen === 0}
          onClick={markAlleGelesen}
        >
          Alle als gelesen markieren
        </Button>
      </div>

      {!isTouch ? (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Gesamt</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-muted-foreground" />
                <span className="text-2xl font-bold">{sichtbare.length}</span>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Ungelesen</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-status-error">{ungelesen}</span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Warnungen</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-status-warning">{sichtbare.filter((b) => b.typ === 'warnung').length}</span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Fehler</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-status-error">{sichtbare.filter((b) => b.typ === 'fehler').length}</span>
            </CardContent>
          </Card>
        </div>
      ) : null}

      <Card>
        <CardContent className="pt-6">
          <DataTable data={sichtbare} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
