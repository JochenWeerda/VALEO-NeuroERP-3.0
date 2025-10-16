import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, Award, FileDown, Plus, Search, CheckCircle, XCircle } from 'lucide-react'

type PSMSachkundeNachweis = {
  id: string
  kunde: string
  kundennr: string
  nachweisNr: string
  ausstellungsdatum: string
  gueltigBis: string
  ausstellendeStelle: string
  status: 'gueltig' | 'ablaufend' | 'abgelaufen'
  complianceStatus: 'compliant' | 'warning' | 'non-compliant'
  letztePruefung: string
  pruefer: string
}

const mockPSMSachkunde: PSMSachkundeNachweis[] = [
  {
    id: '1',
    kunde: 'Landwirtschaft Müller',
    kundennr: 'K-10023',
    nachweisNr: 'SK-PSM-2022-4567',
    ausstellungsdatum: '2022-03-15',
    gueltigBis: '2025-03-15',
    ausstellendeStelle: 'LWK Niedersachsen',
    status: 'ablaufend',
    complianceStatus: 'warning',
    letztePruefung: '2024-09-15',
    pruefer: 'Dr. Schmidt'
  },
  {
    id: '2',
    kunde: 'Hofgut Weber',
    kundennr: 'K-10045',
    nachweisNr: 'SK-PSM-2023-8901',
    ausstellungsdatum: '2023-06-20',
    gueltigBis: '2026-06-20',
    ausstellendeStelle: 'LWK Niedersachsen',
    status: 'gueltig',
    complianceStatus: 'compliant',
    letztePruefung: '2024-10-01',
    pruefer: 'Dr. Müller'
  },
  {
    id: '3',
    kunde: 'Agrar GmbH Schmidt',
    kundennr: 'K-10067',
    nachweisNr: 'SK-PSM-2021-2345',
    ausstellungsdatum: '2021-11-10',
    gueltigBis: '2024-11-10',
    ausstellendeStelle: 'LWK Niedersachsen',
    status: 'abgelaufen',
    complianceStatus: 'non-compliant',
    letztePruefung: '2024-08-20',
    pruefer: 'Dr. Wagner'
  },
]

export default function PSMSachkundeRegisterPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const ablaufend = mockPSMSachkunde.filter((s) => {
    const ablauf = new Date(s.gueltigBis)
    const warnung = new Date()
    warnung.setMonth(warnung.getMonth() + 3) // 3 Monate Vorlauf
    return ablauf <= warnung && ablauf >= new Date()
  }).length

  const nonCompliant = mockPSMSachkunde.filter((s) => s.complianceStatus === 'non-compliant').length

  const columns = [
    {
      key: 'kunde' as const,
      label: 'Kunde',
      render: (s: PSMSachkundeNachweis) => (
        <button
          onClick={() => navigate(`/verkauf/kunden-stamm/${s.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {s.kunde}
        </button>
      ),
    },
    { key: 'kundennr' as const, label: 'Kd-Nr', render: (s: PSMSachkundeNachweis) => <span className="font-mono text-sm">{s.kundennr}</span> },
    { key: 'nachweisNr' as const, label: 'Nachweis-Nr', render: (s: PSMSachkundeNachweis) => <span className="font-mono">{s.nachweisNr}</span> },
    {
      key: 'gueltigBis' as const,
      label: 'Gültig bis',
      render: (s: PSMSachkundeNachweis) => {
        const ablauf = new Date(s.gueltigBis)
        const ablaufend = ablauf <= new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
        return (
          <span className={ablaufend ? 'font-semibold text-orange-600' : ''}>
            {ablauf.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    { key: 'ausstellendeStelle' as const, label: 'Ausgestellt von' },
    {
      key: 'status' as const,
      label: 'Status',
      render: (s: PSMSachkundeNachweis) => (
        <Badge variant={s.status === 'gueltig' ? 'outline' : s.status === 'ablaufend' ? 'secondary' : 'destructive'}>
          {s.status === 'gueltig' ? 'Gültig' : s.status === 'ablaufend' ? 'Läuft ab' : 'Abgelaufen'}
        </Badge>
      ),
    },
    {
      key: 'complianceStatus' as const,
      label: 'Compliance',
      render: (s: PSMSachkundeNachweis) => {
        const statusConfig = {
          compliant: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50', text: 'Compliant' },
          warning: { icon: AlertTriangle, color: 'text-orange-600', bg: 'bg-orange-50', text: 'Warnung' },
          'non-compliant': { icon: XCircle, color: 'text-red-600', bg: 'bg-red-50', text: 'Nicht compliant' }
        }
        const config = statusConfig[s.complianceStatus]
        const Icon = config.icon
        return (
          <div className={`flex items-center gap-2 px-2 py-1 rounded ${config.bg}`}>
            <Icon className={`h-4 w-4 ${config.color}`} />
            <span className={`text-sm font-medium ${config.color}`}>{config.text}</span>
          </div>
        )
      },
    },
    {
      key: 'actions' as const,
      label: 'Aktionen',
      render: (s: PSMSachkundeNachweis) => (
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate(`/agrar/psm/sachkunde/${s.id}/edit`)}
        >
          Bearbeiten
        </Button>
      ),
    },
  ]

  const filteredData = mockPSMSachkunde.filter((item) =>
    item.kunde.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.nachweisNr.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.kundennr.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">PSM-Sachkunde-Register</h1>
          <p className="text-muted-foreground">Sachkundenachweise für PSM-Vertrieb (§ 9 PflSchG)</p>
        </div>
        <Button onClick={() => navigate('/agrar/psm/sachkunde/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Nachweis erfassen
        </Button>
      </div>

      {(ablaufend > 0 || nonCompliant > 0) && (
        <div className="space-y-2">
          {ablaufend > 0 && (
            <Card className="border-orange-500 bg-orange-50">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 text-orange-900">
                  <AlertTriangle className="h-5 w-5" />
                  <span className="font-semibold">{ablaufend} Nachweis(e) läuft/laufen in den nächsten 3 Monaten ab!</span>
                </div>
              </CardContent>
            </Card>
          )}
          {nonCompliant > 0 && (
            <Card className="border-red-500 bg-red-50">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 text-red-900">
                  <XCircle className="h-5 w-5" />
                  <span className="font-semibold">{nonCompliant} Nachweis(e) nicht compliant!</span>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      <div className="rounded-lg bg-orange-50 p-4 text-sm text-orange-900">
        <div className="flex items-center gap-2">
          <Award className="h-4 w-4" />
          <p className="font-semibold">Verkaufsvoraussetzung PSM</p>
        </div>
        <p className="mt-1">
          Sachkundenachweis Pflicht für Anwender • Gültigkeit: 3 Jahre • Bei PSM-Vertrieb prüfen!
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Nachweise Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockPSMSachkunde.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gültig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockPSMSachkunde.filter((s) => s.status === 'gueltig').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Läuft ab (3 Mon.)</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{ablaufend}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgelaufen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{mockPSMSachkunde.filter((s) => s.status === 'abgelaufen').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Nicht Compliant</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{nonCompliant}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Suche Kunde, Nachweis-Nr oder Kd-Nr..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredData} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}