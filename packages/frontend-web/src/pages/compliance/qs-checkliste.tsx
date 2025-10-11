import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { AlertTriangle, CheckCircle, ClipboardCheck } from 'lucide-react'

type QSItem = {
  id: string
  bereich: string
  pruefpunkt: string
  erfuellt: boolean
  bemerkung: string
  geprueftAm: string
}

const mockQS: QSItem[] = [
  { id: '1', bereich: 'Wareneingangskontrolle', pruefpunkt: 'Lieferschein-Prüfung', erfuellt: true, bemerkung: 'Vollständig', geprueftAm: '2025-10-11' },
  { id: '2', bereich: 'Wareneingangskontrolle', pruefpunkt: 'Qualitätsprüfung', erfuellt: true, bemerkung: 'Alle Parameter OK', geprueftAm: '2025-10-11' },
  { id: '3', bereich: 'Hygiene', pruefpunkt: 'Reinigung Annahme', erfuellt: false, bemerkung: 'Ausstehend', geprueftAm: '' },
  { id: '4', bereich: 'Dokumentation', pruefpunkt: 'Chargendoku', erfuellt: true, bemerkung: 'Vollständig', geprueftAm: '2025-10-11' },
]

export default function QSChecklistePage(): JSX.Element {
  const [_searchTerm, _setSearchTerm] = useState('')

  const columns = [
    { key: 'bereich' as const, label: 'Bereich' },
    { key: 'pruefpunkt' as const, label: 'Prüfpunkt' },
    {
      key: 'erfuellt' as const,
      label: 'Status',
      render: (q: QSItem) => (
        q.erfuellt ? (
          <div className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="font-semibold text-green-600">Erfüllt</span>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <span className="font-semibold text-red-600">Offen</span>
          </div>
        )
      ),
    },
    { key: 'bemerkung' as const, label: 'Bemerkung' },
    {
      key: 'geprueftAm' as const,
      label: 'Geprüft am',
      render: (q: QSItem) => q.geprueftAm ? new Date(q.geprueftAm).toLocaleDateString('de-DE') : '-',
    },
  ]

  const erfuellt = mockQS.filter((q) => q.erfuellt).length
  const offen = mockQS.filter((q) => !q.erfuellt).length

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">QS-Checkliste</h1>
          <p className="text-muted-foreground">Quality & Safety</p>
        </div>
        <Button>Audit starten</Button>
      </div>

      {offen > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{offen} Prüfpunkt(e) NICHT erfüllt!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Prüfpunkte Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <ClipboardCheck className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockQS.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Erfüllt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">{erfuellt}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{offen}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockQS} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
