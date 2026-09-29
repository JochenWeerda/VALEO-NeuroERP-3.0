import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Callout } from '@/components/ui/callout'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertTriangle, Award, FileDown, Plus, Search, CheckCircle, XCircle } from 'lucide-react'
import { usePSMSachkundeRegister, type PSMSachkundeNachweis } from '@/lib/api/agrar'
import { ErrorState } from '@/components/ErrorState'
import { useToast } from '@/hooks/use-toast'
import { useTouchDevice } from '@/hooks/useTouchDevice'

export default function PSMSachkundeRegisterPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const { data, isLoading, isError, error, refetch } = usePSMSachkundeRegister()

  const nachweise: PSMSachkundeNachweis[] = data ?? []

  const ablaufend = useMemo(() => {
    const warnung = new Date()
    warnung.setMonth(warnung.getMonth() + 3)
    return nachweise.filter((s) => {
      const ablauf = new Date(s.gueltigBis)
      return ablauf <= warnung && ablauf >= new Date()
    }).length
  }, [nachweise])

  const nonCompliant = useMemo(
    () => nachweise.filter((s) => s.complianceStatus === 'non-compliant').length,
    [nachweise]
  )

  const filteredData = useMemo(
    () => nachweise.filter((item) =>
      [item.kunde, item.nachweisNr, item.kundennr].some((v) => v.toLowerCase().includes(searchTerm.toLowerCase()))
    ),
    [nachweise, searchTerm]
  )

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-[400px] w-full" />
      </div>
    )
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleExport = (): void => {
    const header = 'Kunde;Kd-Nr;Nachweis-Nr;Gueltig bis;Ausstellende Stelle;Status;Compliance\n'
    const rows = filteredData.map((s) =>
      [s.kunde, s.kundennr, s.nachweisNr, s.gueltigBis, s.ausstellendeStelle ?? '', s.status, s.complianceStatus ?? ''].map((v) => `"${String(v).replace(/"/g, '""')}"`).join(';')
    )
    const blob = new Blob([header + rows.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `PSM_Sachkunde_Register_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export', description: `${filteredData.length} Einträge exportiert.` })
  }

  const columns = [
    {
      key: 'kunde' as const,
      label: 'Kunde',
      render: (s: PSMSachkundeNachweis) => (
        <button
          type="button"
          onClick={() => navigate(`/verkauf/kunden-stamm/${s.id}`)}
          className="min-h-11 font-medium text-primary touch-manipulation"
        >
          {s.kunde}
        </button>
      ),
    },
    { key: 'kundennr' as const, label: 'Kd-Nr', render: (s: PSMSachkundeNachweis) => <span className="font-mono text-sm">{s.kundennr}</span> },
    { key: 'nachweisNr' as const, label: 'Nachweis-Nr', render: (s: PSMSachkundeNachweis) => <span className="font-mono">{s.nachweisNr}</span> },
    {
      key: 'gueltigBis' as const,
      label: 'Gueltig bis',
      render: (s: PSMSachkundeNachweis) => {
        const ablauf = new Date(s.gueltigBis)
        const isAblaufend = ablauf <= new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
        return (
          <span className={isAblaufend ? 'font-semibold text-status-warning' : ''}>
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
          {s.status === 'gueltig' ? 'Gueltig' : s.status === 'ablaufend' ? 'Laeuft ab' : 'Abgelaufen'}
        </Badge>
      ),
    },
    {
      key: 'complianceStatus' as const,
      label: 'Compliance',
      render: (s: PSMSachkundeNachweis) => {
        const status = s.complianceStatus ?? 'warning'
        const statusConfig = {
          compliant: { icon: CheckCircle, color: 'text-status-success', bg: 'bg-status-success/10', text: 'Vollständig' },
          warning: { icon: AlertTriangle, color: 'text-status-warning', bg: 'bg-status-warning/10', text: 'Warnung' },
          'non-compliant': { icon: XCircle, color: 'text-status-error', bg: 'bg-status-error/10', text: 'Nicht vollständig' },
        } as const
        const config = statusConfig[status as keyof typeof statusConfig] ?? statusConfig.warning
        const Icon = config.icon
        return (
          <div className={`flex items-center gap-2 rounded px-2 py-1 ${config.bg}`}>
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
        <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => navigate(`/agrar/psm/sachkunde/${s.id}/edit`)}>
          Bearbeiten
        </Button>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">PSM-Sachkunde</h1>
          <p className="text-muted-foreground">Nachweise suchen und prüfen</p>
        </div>
        <Button onClick={() => navigate('/agrar/psm/sachkunde/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Nachweis erfassen
        </Button>
      </div>

      {(ablaufend > 0 || nonCompliant > 0) && (
        <div className="space-y-2">
          {ablaufend > 0 && (
            <Card className="border-status-warning/40 bg-status-warning/10">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 text-status-warning">
                  <AlertTriangle className="h-5 w-5" />
                  <span className="font-semibold">{ablaufend} Nachweis(e) laufen in den nächsten 3 Monaten ab.</span>
                </div>
              </CardContent>
            </Card>
          )}
          {nonCompliant > 0 && (
            <Card className="border-status-error/40 bg-status-error/10">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 text-status-error">
                  <XCircle className="h-5 w-5" />
                  <span className="font-semibold">{nonCompliant} Nachweis(e) nicht vollständig.</span>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      <Callout variant="warning" className="rounded-lg p-4 text-sm">
        <div className="flex items-center gap-2">
          <Award className="h-4 w-4" />
          <p className="font-semibold">Verkaufsvoraussetzung PSM</p>
        </div>
        <p className="mt-1">Sachkundenachweis ist Pflicht für Anwender. Gültigkeit: 3 Jahre. Vor Vertrieb prüfen.</p>
      </Callout>

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Nachweise Gesamt</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{nachweise.length}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gueltig</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold text-status-success">{nachweise.filter((s) => s.status === 'gueltig').length}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Laeuft ab (3 Mon.)</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold text-status-warning">{ablaufend}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Abgelaufen</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold text-status-error">{nachweise.filter((s) => s.status === 'abgelaufen').length}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Nicht Compliant</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold text-status-error">{nonCompliant}</span></CardContent>
        </Card>
      </div>
      ) : null}

      <Card>
        <CardHeader><CardTitle>Suche</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                aria-label="Suche Sachkundenachweise"
                placeholder="Kunde, Nachweis-Nr oder Kd-Nr"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="min-h-touch pl-10"
              />
            </div>
            <Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={handleExport}>
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
