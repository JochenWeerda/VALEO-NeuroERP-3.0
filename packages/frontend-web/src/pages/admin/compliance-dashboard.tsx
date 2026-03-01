import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Shield, AlertTriangle, CheckCircle, FileText,
  TrendingUp, Download, XCircle,
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { api } from '@/lib/axios'
import { useToast } from '@/hooks/use-toast'

// ─── API-Typen ───────────────────────────────────────────────────────────────

type ComplianceStats = {
  cross_compliance: { total: number; erfuellt: number; offen: number; quote: number }
  enni: { total: number; bestaetigt: number; in_bearbeitung: number; durchschnitt_n: number }
  generated_at: string
}

type SachkundeRegister = {
  items: Array<{ id: string; kunde: string; status: string; gueltig_bis?: string }>
  total: number
}

type QsCheckliste = {
  items: Array<{ id: string; pruefpunkt: string; erfuellt: boolean; geprueft_am?: string; bereich?: string }>
  total: number
  erfuellt: number
  offen: number
}

type ZulassungenRegister = {
  items: Array<{ id: string; produkt: string; typ: string; status: string; gueltig_bis?: string }>
  total: number
}

type CrossComplianceList = {
  items: Array<{ id: string; bereich: string; anforderung: string; erfuellt: boolean; nachweis?: string; frist?: string }>
  total: number
  erfuellt: number
  offen: number
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

const statusBadge = (status: 'compliant' | 'warning' | 'pending' | 'error') => {
  switch (status) {
    case 'compliant':
      return <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">Konform</Badge>
    case 'warning':
      return <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">Warnung</Badge>
    case 'pending':
      return <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">Laufend</Badge>
    case 'error':
      return <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">Offen</Badge>
  }
}

const scoreColor = (score: number) =>
  score >= 90 ? 'text-green-600' : score >= 70 ? 'text-orange-600' : 'text-red-600'

// ─── Komponente ──────────────────────────────────────────────────────────────

export default function ComplianceDashboardPage(): JSX.Element {
  const { toast } = useToast()
  const { data: stats, isLoading: loadStats } = useQuery({
    queryKey: ['compliance', 'stats'],
    queryFn: async () => (await apiClient.get<ComplianceStats>('/api/v1/compliance/stats')).data,
  })

  const { data: sachkunde, isLoading: loadSachkunde } = useQuery({
    queryKey: ['compliance', 'sachkunde'],
    queryFn: async () => (await apiClient.get<SachkundeRegister>('/api/v1/compliance/sachkunde-register')).data,
  })

  const { data: qs, isLoading: loadQs } = useQuery({
    queryKey: ['compliance', 'qs'],
    queryFn: async () => (await apiClient.get<QsCheckliste>('/api/v1/compliance/qs-checkliste')).data,
  })

  const { data: zulassungen, isLoading: loadZulassungen } = useQuery({
    queryKey: ['compliance', 'zulassungen'],
    queryFn: async () => (await apiClient.get<ZulassungenRegister>('/api/v1/compliance/zulassungen-register')).data,
  })

  const { data: crossList, isLoading: loadCross } = useQuery({
    queryKey: ['compliance', 'cross-list'],
    queryFn: async () => (await apiClient.get<CrossComplianceList>('/api/v1/compliance/cross-compliance')).data,
  })

  const isLoading = loadStats || loadSachkunde || loadQs || loadZulassungen || loadCross

  const handleReportPdf = async () => {
    try {
      const res = await api.get('/api/v1/compliance/report-pdf', { responseType: 'blob' })
      const blob = res.data as Blob
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `compliance-report-${new Date().toISOString().slice(0, 10)}.pdf`
      a.click()
      URL.revokeObjectURL(url)
      toast({ title: 'Compliance-Report', description: 'Download gestartet.' })
    } catch (e: any) {
      toast({ title: 'Download fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    }
  }

  const handleDetails = (action: { id: string; anforderung: string; bereich: string }) => {
    toast({ title: action.anforderung, description: `${action.bereich} — Detailansicht in Kürze verfügbar.` })
  }

  // ── Berechnungen ──────────────────────────────────────────────────────────

  const sachkundeAktiv = sachkunde?.items.filter(i => i.status === 'aktiv').length ?? 0
  const sachkundeTotal = sachkunde?.total ?? 0
  const sachkundeScore = sachkundeTotal > 0 ? Math.round((sachkundeAktiv / sachkundeTotal) * 100) : 0

  const qsScore = (qs && qs.total > 0) ? Math.round((qs.erfuellt / qs.total) * 100) : 0

  const zulAbgelaufen = zulassungen?.items.filter(z => z.status === 'abgelaufen' || z.status === 'gesperrt').length ?? 0
  const zulTotal = zulassungen?.total ?? 0
  const zulScore = zulTotal > 0 ? Math.round(((zulTotal - zulAbgelaufen) / zulTotal) * 100) : 0

  const crossScore = stats?.cross_compliance.quote ?? 0
  const enniScore = (stats?.enni.total ?? 0) > 0
    ? Math.round((stats!.enni.bestaetigt / stats!.enni.total) * 100)
    : 0

  const scores = [sachkundeScore, qsScore, zulScore, crossScore, enniScore].filter(s => s > 0)
  const overallScore = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0

  // Letzte Aktivitäten aus Cross-Compliance-Items
  const recentActions = (crossList?.items ?? [])
    .slice()
    .sort((a, b) => (b.frist ?? '').localeCompare(a.frist ?? ''))
    .slice(0, 5)

  const checks = [
    {
      key: 'PSM Sachkunde',
      label: 'PSM Sachkunde',
      score: sachkundeScore,
      details: sachkundeTotal > 0
        ? `${sachkundeAktiv}/${sachkundeTotal} Nachweise aktiv`
        : 'Keine Einträge',
      status: (sachkundeScore >= 90 ? 'compliant' : sachkundeScore >= 70 ? 'warning' : 'error') as 'compliant' | 'warning' | 'error',
    },
    {
      key: 'QS Checkliste',
      label: 'QS Checkliste',
      score: qsScore,
      details: qs ? `${qs.erfuellt}/${qs.total} Prüfpunkte erfüllt` : 'Keine Daten',
      status: (qsScore >= 90 ? 'compliant' : qsScore >= 70 ? 'warning' : 'error') as 'compliant' | 'warning' | 'error',
    },
    {
      key: 'Zulassungen',
      label: 'Zulassungen',
      score: zulScore,
      details: zulAbgelaufen > 0
        ? `${zulAbgelaufen} abgelaufen / ${zulTotal} gesamt`
        : `${zulTotal} Zulassungen gültig`,
      status: (zulAbgelaufen === 0 ? 'compliant' : zulAbgelaufen <= 2 ? 'warning' : 'error') as 'compliant' | 'warning' | 'error',
    },
    {
      key: 'Cross-Compliance',
      label: 'Cross-Compliance',
      score: crossScore,
      details: stats
        ? `${stats.cross_compliance.erfuellt}/${stats.cross_compliance.total} Anforderungen erfüllt`
        : 'Keine Daten',
      status: (crossScore >= 90 ? 'compliant' : crossScore >= 70 ? 'warning' : 'pending') as 'compliant' | 'warning' | 'pending',
    },
    {
      key: 'ENNI',
      label: 'ENNI Nährstoffbilanz',
      score: enniScore,
      details: stats
        ? `${stats.enni.bestaetigt}/${stats.enni.total} Meldungen bestätigt · Ø ${stats.enni.durchschnitt_n} kg N`
        : 'Keine Daten',
      status: (enniScore >= 90 ? 'compliant' : enniScore >= 70 ? 'warning' : 'pending') as 'compliant' | 'warning' | 'pending',
    },
  ]

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Shield className="h-8 w-8 text-blue-600" />
            Compliance-Center
          </h1>
          <p className="text-muted-foreground">Übersicht aller Compliance-Anforderungen</p>
        </div>
        <Button className="gap-2" disabled={isLoading} onClick={handleReportPdf}>
          <Download className="h-4 w-4" />
          Compliance-Report (PDF)
        </Button>
      </div>

      {/* Overall Score */}
      <Card className="border-2 border-primary">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold mb-1">Gesamt-Compliance-Score</h2>
              <p className="text-sm text-muted-foreground">Alle Bereiche zusammengefasst</p>
              {stats?.generated_at && (
                <p className="text-xs text-muted-foreground mt-1">
                  Stand: {new Date(stats.generated_at).toLocaleString('de-DE')}
                </p>
              )}
            </div>
            <div className="text-center">
              {isLoading ? (
                <Skeleton className="h-16 w-24" />
              ) : (
                <>
                  <div className={`text-6xl font-bold ${scoreColor(overallScore)}`}>{overallScore}%</div>
                  <Badge
                    variant="outline"
                    className={`mt-2 ${overallScore >= 90 ? 'bg-green-50 text-green-700 border-green-200' : overallScore >= 70 ? 'bg-orange-50 text-orange-700 border-orange-200' : 'bg-red-50 text-red-700 border-red-200'}`}
                  >
                    {overallScore >= 90 ? 'Sehr gut' : overallScore >= 70 ? 'Verbesserungsbedarf' : 'Kritisch'}
                  </Badge>
                </>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Compliance-Checks */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {checks.map(check => (
          <Card key={check.key} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center justify-between">
                <span>{check.label}</span>
                {isLoading ? <Skeleton className="h-6 w-20" /> : statusBadge(check.status)}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className="h-12 w-full" />
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <div className={`text-4xl font-bold ${scoreColor(check.score)}`}>{check.score}%</div>
                    <TrendingUp className={`h-5 w-5 ${scoreColor(check.score)}`} />
                  </div>
                  <p className="text-sm text-muted-foreground">{check.details}</p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Letzte Aktivitäten */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Offene Cross-Compliance-Anforderungen
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loadCross ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-16" />)}
            </div>
          ) : recentActions.length === 0 ? (
            <div className="flex items-center gap-2 text-green-700 py-4">
              <CheckCircle className="h-5 w-5" />
              <span>Alle Cross-Compliance-Anforderungen erfüllt.</span>
            </div>
          ) : (
            <div className="space-y-3">
              {recentActions.map(action => (
                <div key={action.id} className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="flex items-center gap-3">
                    {action.erfuellt ? (
                      <CheckCircle className="h-5 w-5 text-green-600 shrink-0" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-600 shrink-0" />
                    )}
                    <div>
                      <div className="font-semibold">{action.anforderung}</div>
                      <div className="text-sm text-muted-foreground">
                        {action.bereich}
                        {action.frist && ` · Frist: ${new Date(action.frist).toLocaleDateString('de-DE')}`}
                        {action.nachweis && ` · ${action.nachweis}`}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {action.erfuellt
                      ? <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">Erfüllt</Badge>
                      : <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">Offen</Badge>}
                    <Button variant="ghost" size="sm" onClick={() => handleDetails(action)}>Details</Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Warnungen */}
      {!isLoading && zulAbgelaufen > 0 && (
        <Card className="border-orange-400 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-800">
              <AlertTriangle className="h-5 w-5 shrink-0" />
              <span className="font-medium">
                {zulAbgelaufen} Zulassung{zulAbgelaufen > 1 ? 'en' : ''} abgelaufen oder gesperrt — Erneuerung erforderlich.
              </span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
