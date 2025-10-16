import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { AlertTriangle, CheckCircle, FileText, Filter, Search, Shield, XCircle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

type Auflage = {
  id: string
  psm_id: string
  psm_name: string
  auflage_typ: 'NT' | 'NW' | 'B' | 'Sonstige'
  beschreibung: string
  prioritaet: 'hoch' | 'mittel' | 'niedrig'
  status: 'offen' | 'in_bearbeitung' | 'erledigt' | 'ueberfaellig'
  faellig_am: string
  zugewiesen_an: string
  erstellt_am: string
  aktualisiert_am: string
  compliance_status: 'compliant' | 'warning' | 'non-compliant'
}

type AuflagenStatistik = {
  gesamt: number
  offen: number
  in_bearbeitung: number
  erledigt: number
  ueberfaellig: number
  nach_typ: Record<string, number>
}

export default function PSMAuflagenManagerPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()

  const [searchTerm, setSearchTerm] = useState('')
  const [filterTyp, setFilterTyp] = useState<string>('alle')
  const [filterStatus, setFilterStatus] = useState<string>('alle')
  const [filterPrioritaet, setFilterPrioritaet] = useState<string>('alle')

  // Mock data
  const auflagen: Auflage[] = [
    {
      id: '1',
      psm_id: 'PSM-001',
      psm_name: 'Roundup PowerFlex',
      auflage_typ: 'NW',
      beschreibung: 'Wasserschutz-Auflagen: Abstand zu Gewässern mind. 5m, keine Anwendung bei Wind > 3 Bft',
      prioritaet: 'hoch',
      status: 'offen',
      faellig_am: '2024-11-15',
      zugewiesen_an: 'Max Mustermann',
      erstellt_am: '2024-10-01',
      aktualisiert_am: '2024-10-15',
      compliance_status: 'warning'
    },
    {
      id: '2',
      psm_id: 'PSM-002',
      psm_name: 'Amistar Opti',
      auflage_typ: 'B',
      beschreibung: 'Bienenschutz-Auflagen: Keine Anwendung während Bienenflug (6-20 Uhr), Abstand zu Bienenvölkern 100m',
      prioritaet: 'mittel',
      status: 'in_bearbeitung',
      faellig_am: '2024-11-20',
      zugewiesen_an: 'Anna Schmidt',
      erstellt_am: '2024-10-05',
      aktualisiert_am: '2024-10-14',
      compliance_status: 'compliant'
    },
    {
      id: '3',
      psm_id: 'PSM-003',
      psm_name: 'Folicur',
      auflage_typ: 'NT',
      beschreibung: 'Anwendungsverbot in Naturschutzgebieten, Einhaltung von Abständen zu Oberflächengewässern',
      prioritaet: 'hoch',
      status: 'ueberfaellig',
      faellig_am: '2024-10-10',
      zugewiesen_an: 'Thomas Bauer',
      erstellt_am: '2024-09-15',
      aktualisiert_am: '2024-10-12',
      compliance_status: 'non-compliant'
    },
    {
      id: '4',
      psm_id: 'PSM-004',
      psm_name: 'Karate Zeon',
      auflage_typ: 'NT',
      beschreibung: 'Spezielle Lagerbedingungen für Insektizide, regelmäßige Schulungen für Anwender',
      prioritaet: 'niedrig',
      status: 'erledigt',
      faellig_am: '2024-12-01',
      zugewiesen_an: 'Lisa Wagner',
      erstellt_am: '2024-09-20',
      aktualisiert_am: '2024-10-08',
      compliance_status: 'compliant'
    }
  ]

  const statistik: AuflagenStatistik = {
    gesamt: auflagen.length,
    offen: auflagen.filter(a => a.status === 'offen').length,
    in_bearbeitung: auflagen.filter(a => a.status === 'in_bearbeitung').length,
    erledigt: auflagen.filter(a => a.status === 'erledigt').length,
    ueberfaellig: auflagen.filter(a => a.status === 'ueberfaellig').length,
    nach_typ: {
      'NT': auflagen.filter(a => a.auflage_typ === 'NT').length,
      'NW': auflagen.filter(a => a.auflage_typ === 'NW').length,
      'B': auflagen.filter(a => a.auflage_typ === 'B').length,
      'Sonstige': auflagen.filter(a => a.auflage_typ === 'Sonstige').length
    }
  }

  const filteredAuflagen = auflagen.filter(auflage => {
    const matchesSearch = auflage.psm_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         auflage.beschreibung.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesTyp = filterTyp === 'alle' || auflage.auflage_typ === filterTyp
    const matchesStatus = filterStatus === 'alle' || auflage.status === filterStatus
    const matchesPrioritaet = filterPrioritaet === 'alle' || auflage.prioritaet === filterPrioritaet

    return matchesSearch && matchesTyp && matchesStatus && matchesPrioritaet
  })

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      offen: { variant: 'secondary' as const, text: 'Offen' },
      in_bearbeitung: { variant: 'default' as const, text: 'In Bearbeitung' },
      erledigt: { variant: 'outline' as const, text: 'Erledigt' },
      ueberfaellig: { variant: 'destructive' as const, text: 'Überfällig' }
    }
    const config = statusConfig[status as keyof typeof statusConfig]
    return <Badge variant={config.variant}>{config.text}</Badge>
  }

  const getPrioritaetBadge = (prioritaet: string) => {
    const prioritaetConfig = {
      hoch: { variant: 'destructive' as const, text: 'Hoch' },
      mittel: { variant: 'secondary' as const, text: 'Mittel' },
      niedrig: { variant: 'outline' as const, text: 'Niedrig' }
    }
    const config = prioritaetConfig[prioritaet as keyof typeof prioritaetConfig]
    return <Badge variant={config.variant}>{config.text}</Badge>
  }

  const getComplianceIcon = (status: string) => {
    switch (status) {
      case 'compliant':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-orange-600" />
      case 'non-compliant':
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return null
    }
  }

  const columns = [
    {
      key: 'psm_name' as const,
      label: 'PSM',
      render: (auflage: Auflage) => (
        <button
          onClick={() => navigate(`/agrar/psm/stamm/${auflage.psm_id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {auflage.psm_name}
        </button>
      ),
    },
    {
      key: 'auflage_typ' as const,
      label: 'Typ',
      render: (auflage: Auflage) => (
        <Badge variant="outline" className="font-mono">
          {auflage.auflage_typ}
        </Badge>
      ),
    },
    {
      key: 'beschreibung' as const,
      label: 'Auflage',
      render: (auflage: Auflage) => (
        <div className="max-w-xs truncate" title={auflage.beschreibung}>
          {auflage.beschreibung}
        </div>
      ),
    },
    {
      key: 'prioritaet' as const,
      label: 'Priorität',
      render: (auflage: Auflage) => getPrioritaetBadge(auflage.prioritaet),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (auflage: Auflage) => getStatusBadge(auflage.status),
    },
    {
      key: 'faellig_am' as const,
      label: 'Fällig am',
      render: (auflage: Auflage) => {
        const faellig = new Date(auflage.faellig_am)
        const heute = new Date()
        const istUeberfaellig = faellig < heute && auflage.status !== 'erledigt'

        return (
          <span className={istUeberfaellig ? 'font-semibold text-red-600' : ''}>
            {faellig.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    {
      key: 'compliance_status' as const,
      label: 'Compliance',
      render: (auflage: Auflage) => (
        <div className="flex items-center gap-2">
          {getComplianceIcon(auflage.compliance_status)}
          <span className="text-sm capitalize">{auflage.compliance_status}</span>
        </div>
      ),
    },
    {
      key: 'zugewiesen_an' as const,
      label: 'Zugewiesen an',
      render: (auflage: Auflage) => <span className="text-sm">{auflage.zugewiesen_an}</span>,
    },
    {
      key: 'actions' as const,
      label: 'Aktionen',
      render: (auflage: Auflage) => (
        <div className="flex gap-1">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(`/agrar/psm/auflagen/${auflage.id}/bearbeiten`)}
          >
            Bearbeiten
          </Button>
          {auflage.status !== 'erledigt' && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                // Mock status update
                toast({
                  title: "Status aktualisiert",
                  description: `Auflage für ${auflage.psm_name} als erledigt markiert.`,
                })
              }}
              className="text-green-600"
            >
              <CheckCircle className="h-4 w-4" />
            </Button>
          )}
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">PSM-Auflagen-Manager</h1>
          <p className="text-muted-foreground">Compliance-Management für PSM-Auflagen</p>
        </div>
        <Button onClick={() => navigate('/agrar/psm/liste')} className="gap-2">
          <Shield className="h-4 w-4" />
          Zur PSM-Liste
        </Button>
      </div>

      {/* Statistiken */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{statistik.gesamt}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{statistik.offen}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-blue-600">{statistik.in_bearbeitung}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Überfällig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{statistik.ueberfaellig}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Erledigt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{statistik.erledigt}</span>
          </CardContent>
        </Card>
      </div>

      {/* Typ-Verteilung */}
      <Card>
        <CardHeader>
          <CardTitle>Auflagen nach Typ</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            {Object.entries(statistik.nach_typ).map(([typ, anzahl]) => (
              <div key={typ} className="text-center">
                <div className="text-2xl font-bold">{anzahl}</div>
                <div className="text-sm text-muted-foreground">{typ}-Auflagen</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Filter und Suche */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Suche & Filter
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div>
              <Label>Suche</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="PSM oder Auflage suchen..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <div>
              <Label>Auflagen-Typ</Label>
              <Select value={filterTyp} onValueChange={setFilterTyp}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="alle">Alle Typen</SelectItem>
                  <SelectItem value="NT">NT (Naturschutz)</SelectItem>
                  <SelectItem value="NW">NW (Wasserschutz)</SelectItem>
                  <SelectItem value="B">B (Bienenschutz)</SelectItem>
                  <SelectItem value="Sonstige">Sonstige</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Status</Label>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="alle">Alle Status</SelectItem>
                  <SelectItem value="offen">Offen</SelectItem>
                  <SelectItem value="in_bearbeitung">In Bearbeitung</SelectItem>
                  <SelectItem value="erledigt">Erledigt</SelectItem>
                  <SelectItem value="ueberfaellig">Überfällig</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Priorität</Label>
              <Select value={filterPrioritaet} onValueChange={setFilterPrioritaet}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="alle">Alle Prioritäten</SelectItem>
                  <SelectItem value="hoch">Hoch</SelectItem>
                  <SelectItem value="mittel">Mittel</SelectItem>
                  <SelectItem value="niedrig">Niedrig</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Auflagen-Tabelle */}
      <Card>
        <CardHeader>
          <CardTitle>Auflagen ({filteredAuflagen.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable data={filteredAuflagen} columns={columns} />
        </CardContent>
      </Card>

      {/* Warnungen */}
      {statistik.ueberfaellig > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">
                {statistik.ueberfaellig} Auflage(n) sind überfällig!
              </span>
            </div>
            <p className="mt-1 text-red-800">
              Überfällige Auflagen müssen dringend bearbeitet werden, um Compliance-Verstöße zu vermeiden.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}