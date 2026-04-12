import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { BookOpen, FileDown, Search } from 'lucide-react'
import { useHauptbuch, type HauptbuchBuchung } from '@/lib/api/fibu'
import { normalizeOperationalStatus } from '@/lib/operational-status'

export default function HauptbuchPage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const { data: items, isLoading } = useHauptbuch()

  if (isLoading) return (
    <div className="p-3 md:p-6 space-y-4">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-[400px] w-full" />
    </div>
  )

  const list = items ?? []

  const columns = [
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (b: HauptbuchBuchung) => new Date(b.datum).toLocaleDateString('de-DE'),
    },
    { key: 'belegnummer' as const, label: 'Beleg', render: (b: HauptbuchBuchung) => <span className="font-mono">{b.belegnummer}</span> },
    { key: 'konto' as const, label: 'Konto', render: (b: HauptbuchBuchung) => <Badge variant="outline">{b.konto}</Badge> },
    { key: 'text' as const, label: 'Buchungstext' },
    {
      key: 'soll' as const,
      label: 'Soll',
      render: (b: HauptbuchBuchung) => (
        <span className="font-semibold">
          {b.soll > 0 ? new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(b.soll) : '-'}
        </span>
      ),
    },
    {
      key: 'haben' as const,
      label: 'Haben',
      render: (b: HauptbuchBuchung) => (
        <span className="font-semibold">
          {b.haben > 0 ? new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(b.haben) : '-'}
        </span>
      ),
    },
  ]

  const summen = {
    soll: list.reduce((sum, b) => sum + b.soll, 0),
    haben: list.reduce((sum, b) => sum + b.haben, 0),
  }
  const diff = Math.abs(summen.soll - summen.haben)
  const operationalStatus = normalizeOperationalStatus(
    diff >= 0.01 ? 'eskaliert' : list.length > 0 ? 'in_pruefung' : 'offen'
  )
  const contextSections = [
    {
      title: 'Journal',
      items: [
        { label: 'Buchungen', value: String(list.length) },
        { label: 'Suche', value: searchTerm || 'Keine Einschraenkung' },
        { label: 'Differenz', value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(diff) },
      ],
    },
    {
      title: 'Wirtschaftslage',
      items: [
        { label: 'Soll', value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(summen.soll) },
        { label: 'Haben', value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(summen.haben) },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Naechste Aktion', value: diff >= 0.01 ? 'Journaldifferenz pruefen' : 'DATEV-Export oder Abschlussfolge' },
        { label: 'Blocker', value: diff >= 0.01 ? 'Soll und Haben sind nicht ausgeglichen.' : 'Kein akuter Blocker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Hauptbuch geladen', detail: `${list.length} Buchungen im Journal` },
    diff >= 0.01 ? { label: 'Journaldifferenz erkannt', detail: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(diff) } : null,
  ].filter((item): item is { label: string; detail: string } => item !== null)

  return (
    <div className="space-y-4 p-3 md:p-6">
      <OperationalCaseHeader
        title="Hauptbuch"
        description="Journalraum fuer Buchungsmenge, Ausgleich und DATEV-Folgepfad."
        status={operationalStatus}
        owner="Finanzbuchhaltung"
        blocker={diff >= 0.01 ? 'Soll- und Haben-Summen weichen ab.' : null}
        nextAction={diff >= 0.01 ? 'Journaldifferenz klaeren' : 'DATEV-Export oder Abschlusspruefung'}
        caseLabel="Hauptbuch"
        tags={['FIBU', 'Journal']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="Journalverlauf" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Hauptbuch</h1>
          <p className="text-muted-foreground">Buchungsjournal</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Buchungen Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{list.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Soll Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(summen.soll)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Haben Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(summen.haben)}
            </span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              DATEV Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={list} columns={columns} />
          <div className="mt-6 flex justify-between border-t pt-4 font-bold">
            <span>Summen:</span>
            <div className="flex gap-12">
              <span>
                Soll: {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(summen.soll)}
              </span>
              <span>
                Haben: {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(summen.haben)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
