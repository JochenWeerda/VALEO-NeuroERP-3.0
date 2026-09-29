import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertTriangle, CheckCircle, FileText, Filter, Search, Shield, XCircle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { usePSMAuflagen } from '@/lib/api/agrar'
import { useTouchDevice } from '@/hooks/useTouchDevice'

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
  const isTouch = useTouchDevice()

  const { data: auflagenData, isLoading } = usePSMAuflagen()

  const [searchTerm, setSearchTerm] = useState('')
  const [filterTyp, setFilterTyp] = useState<string>('alle')
  const [filterStatus, setFilterStatus] = useState<string>('alle')
  const [filterPrioritaet, setFilterPrioritaet] = useState<string>('alle')

  const auflagen = auflagenData ?? []

  const statistik: AuflagenStatistik = {
    gesamt: auflagen.length,
    offen: auflagen.filter(a => a.status === 'offen').length,
    in_bearbeitung: auflagen.filter(a => a.status === 'erfuellt').length,
    erledigt: auflagen.filter(a => a.status === 'erfuellt').length,
    ueberfaellig: auflagen.filter(a => a.status === 'ueberfaellig').length,
    nach_typ: {
      'NT': auflagen.filter(a => a.auflage_typ === 'NT').length,
      'NW': auflagen.filter(a => a.auflage_typ === 'NW').length,
      'B': auflagen.filter(a => a.auflage_typ === 'B').length,
      'Sonstige': auflagen.filter(a => !['NT', 'NW', 'B'].includes(a.auflage_typ)).length
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
    const statusConfig: Record<string, { variant: 'secondary' | 'default' | 'outline' | 'destructive'; text: string }> = {
      offen: { variant: 'secondary', text: 'Offen' },
      erfuellt: { variant: 'outline', text: 'Erfüllt' },
      ueberfaellig: { variant: 'destructive', text: 'Überfällig' }
    }
    const config = statusConfig[status] || { variant: 'secondary' as const, text: status }
    return <Badge variant={config.variant}>{config.text}</Badge>
  }

  const getPrioritaetBadge = (prioritaet: string) => {
    const prioritaetConfig: Record<string, { variant: 'destructive' | 'secondary' | 'outline'; text: string }> = {
      hoch: { variant: 'destructive', text: 'Hoch' },
      mittel: { variant: 'secondary', text: 'Mittel' },
      niedrig: { variant: 'outline', text: 'Niedrig' }
    }
    const config = prioritaetConfig[prioritaet] || { variant: 'secondary' as const, text: prioritaet }
    return <Badge variant={config.variant}>{config.text}</Badge>
  }

  const getComplianceIcon = (status: string) => {
    switch (status) {
      case 'ok':
        return <CheckCircle className="h-4 w-4 text-status-success" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-status-warning" />
      case 'critical':
        return <XCircle className="h-4 w-4 text-status-error" />
      default:
        return null
    }
  }

  const columns = [
    {
      key: 'psm_name' as const,
      label: 'PSM',
      render: (auflage: typeof auflagen[0]) => (
        <button
          type="button"
          onClick={() => navigate(`/agrar/psm/stamm/${auflage.psm_id}`)}
          className="min-h-11 font-medium text-primary touch-manipulation"
        >
          {auflage.psm_name}
        </button>
      ),
    },
    {
      key: 'auflage_typ' as const,
      label: 'Typ',
      render: (auflage: typeof auflagen[0]) => (
        <Badge variant="outline" className="font-mono">
          {auflage.auflage_typ}
        </Badge>
      ),
    },
    {
      key: 'beschreibung' as const,
      label: 'Auflage',
      render: (auflage: typeof auflagen[0]) => (
        <div className="max-w-xs truncate" aria-label={auflage.beschreibung}>
          {auflage.beschreibung}
        </div>
      ),
    },
    {
      key: 'prioritaet' as const,
      label: 'Priorität',
      render: (auflage: typeof auflagen[0]) => getPrioritaetBadge(auflage.prioritaet),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (auflage: typeof auflagen[0]) => getStatusBadge(auflage.status),
    },
    {
      key: 'faellig_am' as const,
      label: 'Fällig am',
      render: (auflage: typeof auflagen[0]) => {
        const faellig = new Date(auflage.faellig_am)
        const heute = new Date()
        const istUeberfaellig = faellig < heute && auflage.status !== 'erfuellt'

        return (
          <span className={istUeberfaellig ? 'font-semibold text-status-error' : ''}>
            {faellig.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    {
      key: 'compliance_status' as const,
      label: 'Compliance',
      render: (auflage: typeof auflagen[0]) => (
        <div className="flex items-center gap-2">
          {getComplianceIcon(auflage.compliance_status)}
          <span className="text-sm">
            {auflage.compliance_status === 'ok'
              ? 'In Ordnung'
              : auflage.compliance_status === 'warning'
                ? 'Warnung'
                : auflage.compliance_status === 'critical'
                  ? 'Kritisch'
                  : auflage.compliance_status}
          </span>
        </div>
      ),
    },
    {
      key: 'zugewiesen_an' as const,
      label: 'Zugewiesen an',
      render: (auflage: typeof auflagen[0]) => <span className="text-sm">{auflage.zugewiesen_an}</span>,
    },
    {
      key: 'actions' as const,
      label: 'Aktionen',
      render: (auflage: typeof auflagen[0]) => (
        <div className="flex flex-col gap-2 sm:flex-row">
          <Button
            variant="outline"
            className="min-h-touch touch-manipulation"
            onClick={() => navigate(`/agrar/psm/auflagen/${auflage.id}/bearbeiten`)}
          >
            Bearbeiten
          </Button>
          {auflage.status !== 'erfuellt' && (
            <Button
              variant="outline"
              className="min-h-touch touch-manipulation"
              onClick={() => {
                toast({
                  title: 'Status aktualisiert',
                  description: `Auflage für ${auflage.psm_name} als erledigt markiert.`,
                })
              }}
            >
              Erledigt
            </Button>
          )}
        </div>
      ),
    },
  ]

  if (isLoading) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="h-10 w-1/2" />
        <Skeleton className="h-4 w-1/3" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          {[1,2,3,4,5].map(i => <Skeleton key={i} className="h-24 w-full" />)}
        </div>
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">PSM-Auflagen</h1>
          <p className="text-muted-foreground">Auflagen suchen und abarbeiten</p>
        </div>
        <Button onClick={() => navigate('/agrar/psm/liste')} className="min-h-touch gap-2 touch-manipulation">
          <Shield className="h-4 w-4" />
          Zur PSM-Liste
        </Button>
      </div>

      {!isTouch ? (
      <>
      {/* Statistiken */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-muted-foreground" />
              <span className="text-2xl font-bold">{statistik.gesamt}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-warning">{statistik.offen}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{statistik.in_bearbeitung}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Überfällig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-error">{statistik.ueberfaellig}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Erledigt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-success">{statistik.erledigt}</span>
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
      </>
      ) : null}

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
                  aria-label="Suche Auflagen"
                  placeholder="PSM oder Auflage suchen"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="min-h-touch pl-10"
                />
              </div>
            </div>

            <div>
              <Label>Auflagen-Typ</Label>
              <NativeSelect
                ariaLabel="Auflagen-Typ"
                value={filterTyp}
                onValueChange={setFilterTyp}
                options={[
                  { value: 'alle', label: 'Alle Typen' },
                  { value: 'NT', label: 'NT (Naturschutz)' },
                  { value: 'NW', label: 'NW (Wasserschutz)' },
                  { value: 'B', label: 'B (Bienenschutz)' },
                  { value: 'Sonstige', label: 'Sonstige' },
                ]}
              />
            </div>

            <div>
              <Label>Status</Label>
              <NativeSelect
                ariaLabel="Status"
                value={filterStatus}
                onValueChange={setFilterStatus}
                options={[
                  { value: 'alle', label: 'Alle Status' },
                  { value: 'offen', label: 'Offen' },
                  { value: 'erfuellt', label: 'Erfuellt' },
                  { value: 'ueberfaellig', label: 'Ueberfaellig' },
                ]}
              />
            </div>

            <div>
              <Label>Priorität</Label>
              <NativeSelect
                ariaLabel="Prioritaet"
                value={filterPrioritaet}
                onValueChange={setFilterPrioritaet}
                options={[
                  { value: 'alle', label: 'Alle Prioritaeten' },
                  { value: 'hoch', label: 'Hoch' },
                  { value: 'mittel', label: 'Mittel' },
                  { value: 'niedrig', label: 'Niedrig' },
                ]}
              />
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
        <Card className="border-status-error/40 bg-status-error/10">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-status-error">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">
                {statistik.ueberfaellig} Auflage(n) sind überfällig!
              </span>
            </div>
            <p className="mt-1 text-status-error">
              Überfällige Auflagen müssen dringend bearbeitet werden, um Compliance-Verstöße zu vermeiden.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
