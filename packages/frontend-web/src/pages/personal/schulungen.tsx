import { useState, useMemo } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Callout } from '@/components/ui/callout'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertTriangle, Award, FileDown, Plus, Search } from 'lucide-react'
import { useSchulungen, type Schulung } from '@/lib/api/personal'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { exportToCSV } from '@/lib/export-utils'
import { useToast } from '@/hooks/use-toast'

export default function SchulungenPage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [nurPsm, setNurPsm] = useState(false)
  const [nurAblaufende, setNurAblaufende] = useState(false)
  const { data: schulungen, isLoading } = useSchulungen()
  const list = useMemo(() => schulungen ?? [], [schulungen])

  const ablaufend = useMemo(() =>
    list.filter((s) => {
      if (!s.gueltigBis) return false
      const ablauf = new Date(s.gueltigBis)
      const warnung = new Date()
      warnung.setMonth(warnung.getMonth() + 2)
      return ablauf <= warnung && ablauf >= new Date()
    }).length
  , [list])

  const filtered = useMemo(() => {
    return list.filter((sch) => {
      if (searchTerm) {
        const s = searchTerm.toLowerCase()
        const matchesSearch = sch.mitarbeiter.toLowerCase().includes(s) || sch.thema.toLowerCase().includes(s)
        if (!matchesSearch) return false
      }
      if (nurPsm && !String(sch.typ ?? sch.thema ?? '').toLowerCase().includes('psm')) return false
      if (nurAblaufende) {
        if (!sch.gueltigBis) return false
        const ablauf = new Date(sch.gueltigBis)
        const warnung = new Date()
        warnung.setMonth(warnung.getMonth() + 2)
        if (!(ablauf <= warnung && ablauf >= new Date())) return false
      }
      return true
    })
  }, [list, searchTerm, nurPsm, nurAblaufende])

  const columns = [
    {
      key: 'mitarbeiter' as const,
      label: 'Mitarbeiter',
      render: (s: Schulung) => (
        <div>
          <button type="button" onClick={() => navigate(`/personal/mitarbeiter/${s.id}`)} className="min-h-11 font-medium text-primary touch-manipulation">
            {s.mitarbeiter}
          </button>
          <div className="text-xs text-muted-foreground font-mono">{s.personalnr}</div>
        </div>
      ),
    },
    { key: 'typ' as const, label: 'Typ', render: (s: Schulung) => <Badge variant="outline">{s.typ}</Badge> },
    { key: 'thema' as const, label: 'Schulungsthema' },
    { key: 'datum' as const, label: 'Datum', render: (s: Schulung) => new Date(s.datum).toLocaleDateString('de-DE') },
    { key: 'dauer' as const, label: 'Dauer', render: (s: Schulung) => `${s.dauer}h` },
    { key: 'schulungsleiter' as const, label: 'Schulungsleiter' },
    {
      key: 'zertifikatNr' as const,
      label: 'Zertifikat',
      render: (s: Schulung) => (s.zertifikatNr ? <span className="font-mono text-sm">{s.zertifikatNr}</span> : <span className="text-muted-foreground">–</span>),
    },
    {
      key: 'gueltigBis' as const,
      label: 'Gültig bis',
      render: (s: Schulung) => {
        if (!s.gueltigBis) return <span className="text-muted-foreground">–</span>
        const ablauf = new Date(s.gueltigBis)
        const isExpiring = ablauf <= new Date(Date.now() + 60 * 24 * 60 * 60 * 1000)
        return (
          <span className={isExpiring ? 'font-semibold text-status-warning' : ''}>
            {ablauf.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (s: Schulung) => (
        <Badge variant={s.status === 'gueltig' ? 'outline' : s.status === 'ablaufend' ? 'secondary' : 'destructive'}>
          {s.status === 'gueltig' ? 'Gültig' : s.status === 'ablaufend' ? 'Läuft ab' : 'Abgelaufen'}
        </Badge>
      ),
    },
  ]

  if (isLoading) {
    return (
      <div className="space-y-4 p-3 md:p-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-center gap-3">
          <Award className="h-10 w-10 text-primary" />
          <div>
            <h1 className="text-2xl font-bold md:text-3xl">Schulungsnachweise</h1>
            <p className="text-muted-foreground">Nachweise suchen und pruefen</p>
          </div>
        </div>
        <Button onClick={() => navigate('/personal/schulung-neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Schulung erfassen
        </Button>
      </div>

      {ablaufend > 0 && (
        <Card className="border-status-warning/40 bg-status-warning/10">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-status-warning">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{ablaufend} Schulung(en) laufen in den nächsten 2 Monaten ab!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <Callout variant="info" className="rounded-lg p-4 text-sm">
        <div className="flex items-center gap-2">
          <Award className="h-4 w-4" />
          <p className="font-semibold">Pflicht-Schulungen Landhandel</p>
        </div>
        <p className="mt-1">
          <strong>PSM:</strong> § 9 PflSchG (Sachkunde) • <strong>Gabelstapler:</strong> DGUV Vorschrift 68 •
          <strong>Erste Hilfe:</strong> DGUV Vorschrift 1 • <strong>Gefahrstoffe:</strong> GefStoffV § 14
        </p>
      </Callout>

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Schulungen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{list.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gültig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-success">{list.filter((s) => s.status === 'gueltig').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Laufen ab (60 Tage)</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-warning">{ablaufend}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgelaufen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-error">{list.filter((s) => s.status === 'abgelaufen').length}</span>
          </CardContent>
        </Card>
      </div>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Suche & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input aria-label="Suche Schulungen" placeholder="Mitarbeiter, Thema" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="min-h-touch pl-10" />
            </div>
            <Button variant={nurPsm ? 'default' : 'outline'} className="min-h-touch touch-manipulation" onClick={() => setNurPsm((v) => !v)}>Nur PSM</Button>
            <Button variant={nurAblaufende ? 'default' : 'outline'} className="min-h-touch touch-manipulation" onClick={() => setNurAblaufende((v) => !v)}>Nur ablaufende</Button>
            <Button
              variant="outline"
              className="min-h-touch gap-2 touch-manipulation"
              onClick={() => {
                if (filtered.length === 0) {
                  toast({ title: 'Kein Export', description: 'Keine Schulungen in der aktuellen Sicht.', variant: 'destructive' })
                  return
                }
                exportToCSV(
                  filtered.map((s) => ({
                    mitarbeiter: s.mitarbeiter,
                    personalnr: s.personalnr,
                    typ: s.typ,
                    thema: s.thema,
                    datum: s.datum,
                    gueltigBis: s.gueltigBis ?? '',
                    status: s.status,
                  })),
                  `schulungen-${new Date().toISOString().slice(0, 10)}.csv`,
                  [
                    { key: 'mitarbeiter', label: 'Mitarbeiter' },
                    { key: 'personalnr', label: 'Personalnr' },
                    { key: 'typ', label: 'Typ' },
                    { key: 'thema', label: 'Thema' },
                    { key: 'datum', label: 'Datum' },
                    { key: 'gueltigBis', label: 'Gueltig bis' },
                    { key: 'status', label: 'Status' },
                  ],
                )
              }}
            >
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filtered} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
