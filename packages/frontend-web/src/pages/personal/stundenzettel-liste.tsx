import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus } from 'lucide-react'
import { useStundenzettelListe, type StundenzettelEintrag } from '@/lib/api/personal'

const toCsv = (rows: StundenzettelEintrag[]): string => {
  const header = 'Datum;Fahrer;Kennzeichen;Touren;Gesamtstunden;Ueberstunden;ErstelltAm'
  const lines = rows.map((row) => {
    const tourCount = row.touren.length
    return [
      row.datum,
      row.fahrer,
      row.kennzeichen,
      String(tourCount),
      row.gesamtArbeitszeit.toFixed(2),
      row.ueberstunden.toFixed(2),
      row.erstelltAm,
    ]
      .map((value) => `"${String(value).replaceAll('"', '""')}"`)
      .join(';')
  })
  return [header, ...lines].join('\n')
}

const download = (filename: string, content: string): void => {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export default function StundenzettelListePage(): JSX.Element {
  const navigate = useNavigate()
  const [datumVon, setDatumVon] = useState('')
  const [datumBis, setDatumBis] = useState('')
  const { data, isLoading } = useStundenzettelListe({ datumVon, datumBis })
  const list = useMemo(() => data ?? [], [data])

  const columns = [
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (row: StundenzettelEintrag) => new Date(row.datum).toLocaleDateString('de-DE'),
    },
    { key: 'fahrer' as const, label: 'Fahrer' },
    { key: 'kennzeichen' as const, label: 'Kennzeichen' },
    {
      key: 'touren' as const,
      label: 'Touren',
      render: (row: StundenzettelEintrag) => row.touren.length,
    },
    {
      key: 'gesamtArbeitszeit' as const,
      label: 'Gesamtstunden',
      render: (row: StundenzettelEintrag) => `${row.gesamtArbeitszeit.toFixed(2)} h`,
    },
    {
      key: 'ueberstunden' as const,
      label: 'Ueberstunden',
      render: (row: StundenzettelEintrag) => `${row.ueberstunden.toFixed(2)} h`,
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Stundenzettel</h1>
          <p className="text-muted-foreground">Liste und Export</p>
        </div>
        <Button onClick={() => navigate('/personal/stundenzettel')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Stundenzettel
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filter</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Input type="date" value={datumVon} onChange={(e) => setDatumVon(e.target.value)} className="max-w-xs" />
          <Input type="date" value={datumBis} onChange={(e) => setDatumBis(e.target.value)} className="max-w-xs" />
          <Button
            variant="outline"
            className="gap-2"
            onClick={() => download(`stundenzettel-${new Date().toISOString().slice(0, 10)}.csv`, toCsv(list))}
            disabled={list.length === 0}
          >
            <FileDown className="h-4 w-4" />
            CSV Export
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? <div className="text-sm text-muted-foreground">Laedt...</div> : <DataTable data={list} columns={columns} />}
        </CardContent>
      </Card>
    </div>
  )
}
