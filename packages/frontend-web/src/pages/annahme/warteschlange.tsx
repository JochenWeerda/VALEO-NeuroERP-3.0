import { useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { PageSection, PageSurface } from '@/components/patterns/PageSurface'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { Clock, Search, Truck } from 'lucide-react'
import { useWarteschlange, type LKWEintrag } from '@/lib/api/inventory'

export default function WarteschlangePage(): JSX.Element {
  const navigate = useNavigate()
  const searchInputRef = useRef<HTMLInputElement | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const { data, isLoading, refetch } = useWarteschlange()
  const warteschlange = useMemo(() => {
    const items = data?.items ?? []
    if (!searchTerm.trim()) {
      return items
    }
    const term = searchTerm.trim().toLowerCase()
    return items.filter((entry) =>
      [entry.kennzeichen, entry.lieferant, entry.artikel, entry.lieferschein_nr]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(term)),
    )
  }, [data?.items, searchTerm])

  const shortcuts = buildCoreMaskShortcuts({
    onNew: () => navigate('/annahme/lkw-registrierung'),
    onSearch: () => searchInputRef.current?.focus(),
    onRefresh: () => {
      void refetch()
    },
  })
  useKeyboardShortcuts(shortcuts)

  const openHarvestAcceptance = (entry: LKWEintrag): void => {
    const searchParams = new URLSearchParams({
      workflowProcess: 'harvest-to-settlement',
      workflowLabel: `queue-entry:${entry.id}`,
      entryMode: 'Warteschlange',
    })
    if (entry.lieferant) searchParams.set('partnerName', entry.lieferant)
    if (entry.lieferschein_nr) searchParams.set('lieferscheinNr', entry.lieferschein_nr)
    if (entry.kennzeichen) searchParams.set('vehiclePlate', entry.kennzeichen)
    if (entry.article_id) searchParams.set('articleId', entry.article_id)
    if (entry.artikel) {
      searchParams.set('articleName', entry.artikel)
      searchParams.set('subject', `${entry.artikel} / Queue`)
    }
    searchParams.set('queueEntryId', entry.id)
    navigate(`/agrar/ernte-annahme-erfassung?${searchParams.toString()}`)
  }

  const openKlaerung = (entry: LKWEintrag): void => {
    const searchParams = new URLSearchParams({
      queueEntryId: entry.id,
    })
    navigate(`/annahme/klaerung-gesperrt?${searchParams.toString()}`)
  }

  const columns = [
    { key: 'position' as const, label: '#', render: (l: LKWEintrag) => <span className="text-lg font-bold">#{l.position}</span> },
    {
      key: 'kennzeichen' as const,
      label: 'Kennzeichen',
      render: (l: LKWEintrag) => (
        <div>
          <div className="font-mono font-bold">{l.kennzeichen}</div>
          <div className="text-sm text-muted-foreground">{l.lieferant}</div>
        </div>
      ),
    },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'ankunft' as const, label: 'Ankunft' },
    {
      key: 'wartezeit' as const,
      label: 'Wartezeit',
      render: (l: LKWEintrag) => (
        <div className="flex items-center gap-1">
          <Clock className="h-4 w-4" />
          <span>{l.wartezeit} min</span>
        </div>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (l: LKWEintrag) => (
        <Badge
          variant={
            l.status === 'gesperrt'
              ? 'destructive'
              : l.status === 'abgeschlossen'
                ? 'outline'
                : l.status === 'in-bearbeitung'
                  ? 'secondary'
                  : 'default'
          }
        >
          {l.status === 'wartend'
            ? 'Wartend'
            : l.status === 'in-bearbeitung'
              ? 'In Bearbeitung'
              : l.status === 'gesperrt'
                ? 'Gesperrt'
                : 'Abgeschlossen'}
        </Badge>
      ),
    },
    {
      key: 'actions' as const,
      label: 'Aktionen',
      render: (l: LKWEintrag) => (
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => navigate('/annahme/qualitaets-check', { state: { eintragId: l.id } })}>
            Bearbeiten
          </Button>
          {l.status === 'gesperrt' && (
            <Button size="sm" variant="destructive" onClick={() => openKlaerung(l)}>
              Klaerung starten
            </Button>
          )}
          {l.status === 'abgeschlossen' && (
            <Button size="sm" onClick={() => openHarvestAcceptance(l)}>
              Ernte-Annahme anlegen
            </Button>
          )}
        </div>
      ),
    },
  ]

  const wartend = warteschlange.filter(l => l.status === 'wartend').length
  const inBearbeitung = warteschlange.filter(l => l.status === 'in-bearbeitung').length
  const abgeschlossen = warteschlange.filter(l => l.status === 'abgeschlossen').length
  const avgWartezeit = warteschlange.length > 0
    ? Math.round(warteschlange.reduce((sum, l) => sum + l.wartezeit, 0) / warteschlange.length)
    : 0

  if (isLoading) {
    return (
      <PageSurface data-page-surface="annahme-warteschlange-loading" contentClassName="space-y-4">
        <div className="space-y-2">
          <Skeleton className="h-8 w-56" />
          <Skeleton className="h-4 w-32" />
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-24 w-full" />)}
        </div>
        <Skeleton className="h-48 w-full" />
      </PageSurface>
    )
  }

  return (
    <PageSurface data-page-surface="annahme-warteschlange" contentClassName="space-y-6">
      <PageSection
        description="Rueckwirkend auf den DS-Rahmen, Keyboard-first und touch-feste Operator-Bedienung gehoben."
      >
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-3xl font-bold">Annahme-Warteschlange</h1>
            <p className="text-muted-foreground">LKW-Abfertigung mit QR-, Search- und Queue-Sicht.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={() => navigate('/annahme/qr')}>
              QR-Code (Handy)
            </Button>
            <Button className="min-h-touch gap-2 touch-manipulation" onClick={() => navigate('/annahme/lkw-registrierung')}>
              LKW anmelden
            </Button>
          </div>
        </div>
      </PageSection>

      <PageSection title="Queue-Lage" description="Live-Zahlen fuer wartende, laufende und abgeschlossene Abfertigungen.">
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">In Warteschlange</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Truck className="h-5 w-5 text-blue-600" />
                <span className="text-2xl font-bold">{wartend}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-orange-600">{inBearbeitung}</span>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Avg. Wartezeit</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                <span className="text-2xl font-bold">{avgWartezeit} min</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Heute abgefertigt</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-green-600">{abgeschlossen}</span>
            </CardContent>
          </Card>
        </div>
      </PageSection>

      <PageSection title="Arbeitsliste" description="Ctrl+F fokussiert die Suche, Ctrl+N oeffnet die Registrierung, F5 aktualisiert die Queue.">
        <div className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              ref={searchInputRef}
              aria-label="Suche Warteschlange"
              placeholder="Kennzeichen, Lieferant, Artikel oder Lieferschein suchen"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              className="min-h-touch pl-10"
            />
          </div>
          <Card>
            <CardContent className="pt-6">
              <DataTable data={warteschlange} columns={columns} />
            </CardContent>
          </Card>
        </div>
      </PageSection>

      <KeyboardShortcutBar shortcuts={shortcuts} />
    </PageSurface>
  )
}
