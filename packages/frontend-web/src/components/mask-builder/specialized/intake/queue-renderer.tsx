import { canDomainAction } from './domain-runtime'
import { ErrorState } from '@/components/ErrorState'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { PageSection, PageSurface } from '@/components/patterns/PageSurface'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Clock, Search, Truck } from 'lucide-react'
import type { LKWEintrag } from '@/lib/api/inventory'

import type { QueueState } from './queue-controller'

export function QueueRenderer({ state }: { state: QueueState }): JSX.Element {
  const { plan, navigate, isTouch, chain, supplyOps, searchInputRef, searchTerm, setSearchTerm, isLoading, isError, error, refetch, repair, openQuality, warteschlange, shortcuts, openHarvestAcceptance, openKlaerung, wartend, inBearbeitung, abgeschlossen, avgWartezeit, operationalStatus, contextSections, timelineItems } = state
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
          <Button variant="outline" className="min-h-touch touch-manipulation" disabled={!canDomainAction(plan, 'quality')} onClick={() => openQuality(l)}>
            Bearbeiten
          </Button>
          {!l.article_id && l.artikel ? (
            <Button
              variant="outline"
              className="min-h-touch touch-manipulation"
              disabled={!canDomainAction(plan, 'repair')} onClick={() => repair(l)}
            >
              Artikel reparieren
            </Button>
          ) : null}
          {l.status === 'gesperrt' && (
            <Button variant="destructive" className="min-h-touch touch-manipulation" disabled={!canDomainAction(plan, 'clarify')} onClick={() => openKlaerung(l)}>
              Klaerung starten
            </Button>
          )}
          {l.status === 'abgeschlossen' && (
            <Button className="min-h-touch touch-manipulation" disabled={!canDomainAction(plan, 'harvest')} onClick={() => openHarvestAcceptance(l)}>
              Ernte-Annahme anlegen
            </Button>
          )}
        </div>
      ),
    },
  ]

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

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

      <OperationalCaseHeader
        title="Annahme-Warteschlange"
        description="Die Queue wird als operativer Annahmefall mit Prioritaet, Blockern und naechster Massnahme ueber der Liste gefuehrt."
        status={operationalStatus}
        owner="Annahme / Disposition"
        blocker={warteschlange.some((entry) => entry.status === 'gesperrt') ? 'Mindestens ein Fahrzeug ist gesperrt und benoetigt Klaerung.' : null}
        nextAction={chain ? supplyOps.nextAction : 'Lieferkettenstatus nicht verfügbar'}
        caseLabel="Vorgang: Annahme-Queue"
        tags={['Annahme', 'Logistik']}
      />
      <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
        <OperationalTimeline title="Queue-Verlauf" items={timelineItems} />
        <OperationalContextPanel title="Queue-Kontext" sections={contextSections} />
      </div>

      <PageSection title="Queue-Lage" description="Live-Zahlen fuer wartende, laufende und abgeschlossene Abfertigungen.">
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">In Warteschlange</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Truck className="h-5 w-5 text-muted-foreground" />
                <span className="text-2xl font-bold">{wartend}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-status-warning">{inBearbeitung}</span>
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
              <span className="text-2xl font-bold text-status-success">{abgeschlossen}</span>
            </CardContent>
          </Card>
        </div>
      </PageSection>

      <PageSection title="Objektkette" description="Einlauf, Wiegung, Charge und Fracht in einer gemeinsamen Lageansicht.">
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Offene Wiegungen</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold">{chain ? chain.openWeighingTickets ?? 0 : '–'}</span></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gesperrte Chargen</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold">{chain ? chain.blockedCharges ?? 0 : '–'}</span></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Fracht unterwegs</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold">{chain ? chain.freightInTransit ?? 0 : '–'}</span></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Aktive Fahrzeuge</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold">{chain ? chain.activeVehiclePlates?.length ?? 0 : '–'}</span></CardContent>
          </Card>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Bottleneck</CardTitle></CardHeader>
            <CardContent><div className="text-lg font-semibold capitalize">{chain ? supplyOps.bottleneck : 'Nicht verfügbar'}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Druck</CardTitle></CardHeader>
            <CardContent>
              <Badge variant={supplyOps.pressure === 'hoch' ? 'destructive' : supplyOps.pressure === 'mittel' ? 'secondary' : 'outline'}>
                {chain ? supplyOps.pressure : 'Nicht verfügbar'}
              </Badge>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Naechste Aktion</CardTitle></CardHeader>
            <CardContent><div className="text-sm font-semibold">{chain ? supplyOps.nextAction : 'Nicht verfügbar'}</div></CardContent>
          </Card>
        </div>
      </PageSection>

      <PageSection title="Arbeitsliste" description="Suche nach Kennzeichen, Lieferant oder Lieferschein. Tippen öffnet den nächsten Schritt.">
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

      {!isTouch ? <KeyboardShortcutBar shortcuts={shortcuts} /> : null}
    </PageSurface>
  )
}
