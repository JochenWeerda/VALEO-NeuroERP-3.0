import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { AlertTriangle, CheckCircle, ClipboardCheck } from 'lucide-react'

type ComplianceItem = {
  id: string
  bereich: string
  anforderung: string
  erfuellt: boolean
  nachweis: string
  frist: string
}

const mockCompliance: ComplianceItem[] = [
  { id: '1', bereich: 'Gewässerschutz', anforderung: 'Gewässerrandstreifen 5m', erfuellt: true, nachweis: 'Feldprotokoll 2025', frist: '2025-12-31' },
  { id: '2', bereich: 'Tierschutz', anforderung: 'Stallgröße mind. 6qm/GV', erfuellt: true, nachweis: 'Stallplan', frist: '2025-12-31' },
  { id: '3', bereich: 'Düngeverordnung', anforderung: 'Nährstoffbilanz', erfuellt: false, nachweis: 'Ausstehend', frist: '2025-11-15' },
]

export default function CrossCompliancePage(): JSX.Element {
  const [_searchTerm, _setSearchTerm] = useState('')

  const columns = [
    { key: 'bereich' as const, label: 'Bereich', render: (c: ComplianceItem) => <Badge variant="outline">{c.bereich}</Badge> },
    { key: 'anforderung' as const, label: 'Anforderung' },
    {
      key: 'erfuellt' as const,
      label: 'Erfüllt',
      render: (c: ComplianceItem) => (
        c.erfuellt ? (
          <CheckCircle className="h-5 w-5 text-green-600" />
        ) : (
          <AlertTriangle className="h-5 w-5 text-red-600" />
        )
      ),
    },
    { key: 'nachweis' as const, label: 'Nachweis' },
    {
      key: 'frist' as const,
      label: 'Frist',
      render: (c: ComplianceItem) => new Date(c.frist).toLocaleDateString('de-DE'),
    },
  ]

  const erfuellt = mockCompliance.filter((c) => c.erfuellt).length
  const offen = mockCompliance.filter((c) => !c.erfuellt).length

  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-3xl font-bold">Cross-Compliance</h1>
        <p className="text-muted-foreground">Förder-Voraussetzungen</p>
      </div>

      {offen > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{offen} Anforderung(en) NICHT erfüllt!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Anforderungen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <ClipboardCheck className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockCompliance.length}</span>
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
          <DataTable data={mockCompliance} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
