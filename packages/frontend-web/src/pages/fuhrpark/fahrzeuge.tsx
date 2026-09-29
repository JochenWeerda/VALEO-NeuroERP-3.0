import { useMemo, useState } from 'react'
import { Callout } from '@/components/ui/callout'
import { useNavigate } from '@/app/routing/typed-router'
import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, FileDown, Plus, Search, Truck } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { listFuhrparkFahrzeuge, type FuhrparkFahrzeug } from '@/lib/api/fuhrpark'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { exportToCSV } from '@/lib/export-utils'
import { useToast } from '@/hooks/use-toast'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'

type FleetRole = 'fuhrpark' | 'disposition' | 'werkstatt' | 'leitung'

const fleetRoles = [
  { id: 'fuhrpark', label: 'Fuhrpark', description: 'Prueft Fahrzeugstatus, Fristen und Pflege der Fahrzeugdaten.' },
  { id: 'disposition', label: 'Disposition', description: 'Sieht, welche Fahrzeuge verfuegbar, unterwegs oder blockiert sind.' },
  { id: 'werkstatt', label: 'Werkstatt', description: 'Fokussiert faellige Inspektionen und Fahrzeuge in Werkstattstatus.' },
  { id: 'leitung', label: 'Leitung', description: 'Sieht Fristendruck, Verfuegbarkeit und naechste Entscheidung.' },
] satisfies Array<{ id: FleetRole; label: string; description: string }>

function LoadingSkeleton(): JSX.Element {
  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div><Skeleton className="h-8 w-32" /><Skeleton className="mt-2 h-4 w-48" /></div>
        <Skeleton className="h-10 w-40" />
      </div>
      <Callout variant="warning" className="pt-4"><Skeleton className="h-5 w-64" /></Callout>
      <Card><CardContent className="pt-6"><Skeleton className="h-64 w-full" /></CardContent></Card>
    </div>
  )
}

function ErrorState({ error, onRetry }: { error: Error | null; onRetry: () => void }): JSX.Element {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <AlertTriangle className="mb-4 h-12 w-12 text-status-error" />
      <h2 className="mb-2 text-xl font-semibold text-status-error">Backend nicht erreichbar</h2>
      <p className="mb-4 text-muted-foreground">{error?.message || 'Die Fahrzeug-Daten konnten nicht geladen werden.'}</p>
      <Button onClick={onRetry} variant="outline" className="gap-2"><Truck className="h-4 w-4" />Erneut versuchen</Button>
    </div>
  )
}

export default function FahrzeugePage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFocus, setRoleFocus] = useState<FleetRole>('fuhrpark')

  const { data: fahrzeuge = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ['fuhrpark', 'fahrzeuge'],
    queryFn: listFuhrparkFahrzeuge,
  })

  const filteredFahrzeuge = useMemo(() => {
    if (!searchTerm) return fahrzeuge
    const term = searchTerm.toLowerCase()
    return fahrzeuge.filter((f) =>
      f.kennzeichen.toLowerCase().includes(term) ||
      f.typ.toLowerCase().includes(term) ||
      (f.ro_nummer ?? '').toLowerCase().includes(term),
    )
  }, [fahrzeuge, searchTerm])

  const inspektionFaellig = filteredFahrzeuge.filter((f) => {
    if (!f.naechste_inspektion) return false
    return new Date(f.naechste_inspektion) < new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)
  }).length
  const werkstattCount = filteredFahrzeuge.filter((f) => f.status === 'werkstatt').length
  const verfuegbarCount = filteredFahrzeuge.filter((f) => f.status === 'verfuegbar').length
  const fleetBlockers = inspektionFaellig + werkstattCount
  const nextFleetAction = inspektionFaellig > 0
    ? `${inspektionFaellig} faellige Inspektion(en) terminieren und Nachweis aktualisieren.`
    : werkstattCount > 0
      ? `${werkstattCount} Fahrzeug(e) im Werkstattstatus pruefen.`
      : filteredFahrzeuge.length === 0
        ? 'Suchfilter pruefen oder neues Fahrzeug anlegen.'
        : 'Fahrzeugbestand ist arbeitsfaehig; naechste Fristenpruefung planen.'

  function handleExport(): void {
    if (filteredFahrzeuge.length === 0) {
      toast({ title: 'Kein Export', description: 'Keine Fahrzeuge in der aktuellen Sicht.', variant: 'destructive' })
      return
    }
    exportToCSV(
      filteredFahrzeuge.map((f) => ({
        kennzeichen: f.kennzeichen,
        ro_nummer: f.ro_nummer ?? '',
        typ: f.typ,
        kilometerstand: f.kilometerstand ?? 0,
        naechste_inspektion: f.naechste_inspektion ?? '',
        status: f.status,
      })),
      `fuhrpark-${new Date().toISOString().slice(0, 10)}.csv`,
      [
        { key: 'kennzeichen', label: 'Kennzeichen' },
        { key: 'ro_nummer', label: 'RO-Nr' },
        { key: 'typ', label: 'Typ' },
        { key: 'kilometerstand', label: 'km-Stand' },
        { key: 'naechste_inspektion', label: 'Inspektion' },
        { key: 'status', label: 'Status' },
      ],
    )
  }

  if (isError && !isLoading) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  if (isLoading) return <LoadingSkeleton />

  const columns = [
    {
      key: 'kennzeichen' as const,
      label: 'Kennzeichen',
      render: (f: FuhrparkFahrzeug) => (
        <button type="button" onClick={() => navigate(`/fuhrpark/fahrzeug/${f.id}`)} className="min-h-11 font-mono font-medium text-primary touch-manipulation">{f.kennzeichen}</button>
      ),
    },
    { key: 'ro_nummer' as const, label: 'RO-Nr.' },
    { key: 'typ' as const, label: 'Typ' },
    { key: 'kilometerstand' as const, label: 'km-Stand', render: (f: FuhrparkFahrzeug) => Number(f.kilometerstand ?? 0).toLocaleString('de-DE') },
    {
      key: 'naechste_inspektion' as const,
      label: 'Inspektion',
      render: (f: FuhrparkFahrzeug) => {
        if (!f.naechste_inspektion) return '-'
        const datum = new Date(f.naechste_inspektion)
        const faellig = datum < new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)
        return <span className={faellig ? 'font-semibold text-status-warning' : ''}>{datum.toLocaleDateString('de-DE')}</span>
      },
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (f: FuhrparkFahrzeug) => (
        <Badge variant={f.status === 'verfuegbar' ? 'outline' : f.status === 'unterwegs' ? 'secondary' : 'destructive'}>
          {f.status === 'verfuegbar' ? 'Verfuegbar' : f.status === 'unterwegs' ? 'Unterwegs' : 'Werkstatt'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Fuhrpark</h1>
          <p className="text-muted-foreground">Fahrzeuge suchen und oeffnen</p>
        </div>
        <Button onClick={() => navigate('/fuhrpark/fahrzeug/neu')} className="min-h-touch gap-2 touch-manipulation"><Plus className="h-4 w-4" />Neues Fahrzeug</Button>
      </div>

      {!isTouch ? (
      <RoleFocusBar roles={fleetRoles} value={roleFocus} onChange={setRoleFocus} visibleCount={filteredFahrzeuge.length} totalCount={fahrzeuge.length} title="Wer steuert den Fuhrpark?" />
      ) : null}

      {!isTouch ? (
      <>
      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <ManagementDecisionPanel
          decision={{
            allowed: fleetBlockers === 0 && filteredFahrzeuge.length > 0,
            allowedLabel: 'Fuhrpark arbeitsfaehig',
            blockedLabel: 'Fristen pruefen',
            summary: fleetBlockers > 0
              ? `${inspektionFaellig} Inspektion(en) und ${werkstattCount} Werkstattfall/-faelle brauchen Klaerung.`
              : `${verfuegbarCount} Fahrzeug(e) sind verfuegbar; keine kritische Frist in der aktuellen Sicht.`,
            blockerCount: fleetBlockers + (filteredFahrzeuge.length === 0 ? 1 : 0),
            nextFocus: nextFleetAction,
            template: { label: 'Fuhrpark-Fristen- und Fahrzeugnachweis', href: '/docs/fuhrpark/fristen-fahrzeugnachweis.md' },
          }}
        />
        <div className="space-y-4">
          <NextActionPanel action={nextFleetAction} tone={fleetBlockers > 0 ? 'amber' : 'emerald'} />
          <EvidenceTemplateLink link={{ label: 'Inspektions- und Statusnachweis', href: '/docs/fuhrpark/inspektionsnachweis.md' }} />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <OperationalTaskPlan
          title="Fuhrpark-Fristenplan"
          items={[
            { label: 'Fahrzeuge laden', done: fahrzeuge.length > 0, hint: `${fahrzeuge.length} Fahrzeug(e) im Bestand.` },
            { label: 'Verfuegbarkeit pruefen', done: verfuegbarCount > 0, hint: `${verfuegbarCount} verfuegbar, ${werkstattCount} in Werkstatt.` },
            { label: 'Inspektionen klaeren', done: inspektionFaellig === 0, hint: inspektionFaellig > 0 ? `${inspektionFaellig} Inspektion(en) in 14 Tagen faellig.` : 'Keine kurzfristig faellige Inspektion.' },
            { label: 'Nachweis sichern', done: filteredFahrzeuge.length > 0, hint: 'Fahrzeugstatus und Fristen bilden den operativen Mindestnachweis.' },
          ]}
        />
        <CrudCapabilityChecklist
          capabilities={[
            { key: 'create', label: 'Fahrzeug anlegen', available: true, hint: 'Neues Fahrzeug kann ueber die Aktion angelegt werden.' },
            { key: 'read', label: 'Status lesen', available: true, hint: 'Kennzeichen, Typ, Kilometer, Frist und Status sind sichtbar.' },
            { key: 'update', label: 'Fahrzeug bearbeiten', available: true, hint: 'Klick auf Kennzeichen fuehrt in die Bearbeitung.' },
            { key: 'export', label: 'Export', available: true, hint: 'Export-Aktion ist vorhanden.' },
            { key: 'evidence', label: 'Fristennachweis', available: true, hint: 'Inspektionsnachweis ist verlinkt.' },
            { key: 'audit', label: 'Letzte Frist', available: true, hint: 'Naechste Inspektion ist je Fahrzeug sichtbar.' },
          ]}
        />
      </div>
      </>
      ) : null}

      {inspektionFaellig > 0 && (
        <Callout variant="warning" className="pt-4"><div className="flex items-center gap-2 text-status-warning"><AlertTriangle className="h-5 w-5" /><span className="font-semibold">{inspektionFaellig} Inspektion(en) in den naechsten 14 Tagen faellig!</span></div></Callout>
      )}

      <Card>
        <CardHeader><CardTitle>Suche</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input aria-label="Suche Fahrzeuge" placeholder="Kennzeichen, Typ, RO-Nr" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="min-h-touch pl-10" /></div>
            <Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={handleExport}><FileDown className="h-4 w-4" />Export</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6"><DataTable data={filteredFahrzeuge} columns={columns} /></CardContent>
      </Card>
    </div>
  )
}
