import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from '@/app/routing/typed-router'
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
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'

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

const EMPTY_COMPLIANCE_STATS: ComplianceStats = {
  cross_compliance: { total: 0, erfuellt: 0, offen: 0, quote: 0 },
  enni: { total: 0, bestaetigt: 0, in_bearbeitung: 0, durchschnitt_n: 0 },
  generated_at: '',
}

const EMPTY_SACHKUNDE_REGISTER: SachkundeRegister = {
  items: [],
  total: 0,
}

const EMPTY_QS_CHECKLISTE: QsCheckliste = {
  items: [],
  total: 0,
  erfuellt: 0,
  offen: 0,
}

const EMPTY_ZULASSUNGEN_REGISTER: ZulassungenRegister = {
  items: [],
  total: 0,
}

const EMPTY_CROSS_COMPLIANCE_LIST: CrossComplianceList = {
  items: [],
  total: 0,
  erfuellt: 0,
  offen: 0,
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

const statusBadge = (status: 'compliant' | 'warning' | 'pending' | 'error') => {
  switch (status) {
    case 'compliant':
      return <Badge variant="success">Konform</Badge>
    case 'warning':
      return <Badge variant="warning">Warnung</Badge>
    case 'pending':
      return <Badge variant="info">Laufend</Badge>
    case 'error':
      return <Badge variant="destructive">Offen</Badge>
  }
}

const scoreColor = (score: number) =>
  score >= 90
    ? 'text-[hsl(var(--color-semantic-success-700-hsl))]'
    : score >= 70
      ? 'text-[hsl(var(--color-semantic-warning-700-hsl))]'
      : 'text-destructive'

// ─── Komponente ──────────────────────────────────────────────────────────────

type ComplianceRole = 'compliance' | 'qs' | 'meldewesen' | 'leitung'

const complianceRoles = [
  { id: 'compliance', label: 'Compliance', description: 'Offene Anforderungen pruefen und Nachweise nachhalten.' },
  { id: 'qs', label: 'QS', description: 'Qualitaetspruefungen und Zulassungen fachlich bewerten.' },
  { id: 'meldewesen', label: 'Meldewesen', description: 'Meldungen, Fristen und Report-Export im Blick behalten.' },
  { id: 'leitung', label: 'Leitung', description: 'Gesamtrisiko und Abschlussfaehigkeit verdichtet bewerten.' },
] satisfies Array<{ id: ComplianceRole; label: string; description: string }>

export default function ComplianceDashboardPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [roleFocus, setRoleFocus] = useState<ComplianceRole>('compliance')
  const { data: stats, isLoading: loadStats } = useQuery({
    queryKey: ['compliance', 'stats'],
    queryFn: async () => (await apiClient.get<ComplianceStats>('/api/v1/compliance/stats')).data,
    initialData: EMPTY_COMPLIANCE_STATS,
  })

  const { data: sachkunde, isLoading: loadSachkunde } = useQuery({
    queryKey: ['compliance', 'sachkunde'],
    queryFn: async () => (await apiClient.get<SachkundeRegister>('/api/v1/compliance/sachkunde-register')).data,
    initialData: EMPTY_SACHKUNDE_REGISTER,
  })

  const { data: qs, isLoading: loadQs } = useQuery({
    queryKey: ['compliance', 'qs'],
    queryFn: async () => (await apiClient.get<QsCheckliste>('/api/v1/compliance/qs-checkliste')).data,
    initialData: EMPTY_QS_CHECKLISTE,
  })

  const { data: zulassungen, isLoading: loadZulassungen } = useQuery({
    queryKey: ['compliance', 'zulassungen'],
    queryFn: async () => (await apiClient.get<ZulassungenRegister>('/api/v1/compliance/zulassungen-register')).data,
    initialData: EMPTY_ZULASSUNGEN_REGISTER,
  })

  const { data: crossList, isLoading: loadCross } = useQuery({
    queryKey: ['compliance', 'cross-list'],
    queryFn: async () => (await apiClient.get<CrossComplianceList>('/api/v1/compliance/cross-compliance')).data,
    initialData: EMPTY_CROSS_COMPLIANCE_LIST,
  })

  const isLoading = loadStats || loadSachkunde || loadQs || loadZulassungen || loadCross

  const openComplianceDetails = (action: { id: string; anforderung: string; bereich: string }) => {
    const bereich = action.bereich.toLowerCase()
    const target = bereich.includes('sachkunde')
      ? '/compliance/sachkunde-register'
      : bereich.includes('qs')
        ? '/compliance/qs-checkliste'
        : bereich.includes('zulassung')
          ? '/compliance/zulassungen-register'
          : bereich.includes('enni')
            ? '/compliance/enni-meldungen'
            : '/compliance/cross-compliance'
    navigate(target)
    toast({ title: action.anforderung, description: `${action.bereich} geoeffnet.` })
  }

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
    } catch (_rawErr: unknown) {
      const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({ title: 'Download fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    }
  }

  const handleDetails = (action: { id: string; anforderung: string; bereich: string }) => {
    openComplianceDetails(action)
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
    ? Math.round(((stats?.enni.bestaetigt ?? 0) / (stats?.enni.total ?? 1)) * 100)
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
  const openRequirements = (crossList?.offen ?? 0) + (qs?.offen ?? 0) + zulAbgelaufen
  const complianceReady = overallScore >= 90 && openRequirements === 0
  const nextComplianceAction = openRequirements > 0
    ? `${openRequirements} offene Compliance-Punkte pruefen und Verantwortliche zuordnen.`
    : overallScore < 90
      ? 'Bereiche mit niedriger Quote oeffnen und Nachweise aktualisieren.'
      : 'Compliance-Report exportieren und als aktuellen Nachweis ablegen.'

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Shield className="h-8 w-8 text-primary" />
            Compliance-Center
          </h1>
          <p className="text-muted-foreground">Übersicht aller Compliance-Anforderungen</p>
        </div>
        <Button className="gap-2" disabled={isLoading} onClick={handleReportPdf}>
          <Download className="h-4 w-4" />
          Compliance-Report (PDF)
        </Button>
      </div>

      <RoleFocusBar
        roles={complianceRoles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={checks.length}
        totalCount={checks.length}
        title="Arbeitsrolle fuer Compliance"
      />

      <ManagementDecisionPanel
        decision={{
          allowed: complianceReady,
          allowedLabel: 'Nachweisfaehig',
          blockedLabel: 'Pruefung offen',
          summary: complianceReady
            ? 'Alle wesentlichen Compliance-Bereiche liegen im gruenen Bereich. Der Report kann als aktueller Nachweis exportiert werden.'
            : 'Offene Anforderungen, QS-Punkte oder abgelaufene Zulassungen muessen zuerst geklaert werden, damit der Compliance-Stand belastbar ist.',
          blockerCount: complianceReady ? 0 : openRequirements || checks.filter((check) => check.status !== 'compliant').length,
          nextFocus: nextComplianceAction,
          template: {
            label: 'Compliance-Pruefprotokoll',
            href: '/docs/compliance/compliance-pruefprotokoll.md',
          },
        }}
      />

      <div className="grid gap-4 xl:grid-cols-[1.15fr_1fr_1fr]">
        <OperationalTaskPlan
          title="Compliance-Pruefplan"
          items={[
            { label: 'Scores pruefen', done: overallScore >= 90, hint: `Gesamtstand liegt bei ${overallScore}%.` },
            { label: 'QS-Offenpunkte klaeren', done: (qs?.offen ?? 0) === 0, hint: `${qs?.offen ?? 0} QS-Punkt(e) offen.` },
            { label: 'Zulassungen pruefen', done: zulAbgelaufen === 0, hint: zulAbgelaufen > 0 ? `${zulAbgelaufen} Zulassung(en) abgelaufen oder gesperrt.` : 'Keine abgelaufenen oder gesperrten Zulassungen.' },
            { label: 'Report nachweisen', done: complianceReady, hint: 'Report erst exportieren, wenn offene Punkte bewertet sind.' },
          ]}
        />
        <NextActionPanel action={nextComplianceAction} tone={complianceReady ? 'emerald' : openRequirements > 0 ? 'red' : 'amber'} />
        <div className="space-y-3">
          <EvidenceTemplateLink
            link={{ label: 'Compliance-Report-Ablage', href: '/docs/compliance/compliance-report-ablage.md' }}
          />
          <CrudCapabilityChecklist
            capabilities={[
              { key: 'read', label: 'Status lesen', available: true, hint: 'Scores, offene Anforderungen und Details sind sichtbar.' },
              { key: 'update', label: 'Details klaeren', available: true, hint: 'Offene Punkte fuehren in die passende Fachmaske.' },
              { key: 'export', label: 'Report exportieren', available: true, hint: 'PDF-Report kann direkt erzeugt werden.' },
              { key: 'evidence', label: 'Nachweis', available: complianceReady, hint: 'Nachweis ist belastbar, wenn offene Punkte geklaert sind.' },
            ]}
          />
        </div>
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
                    variant={overallScore >= 90 ? 'success' : overallScore >= 70 ? 'warning' : 'destructive'}
                    className="mt-2"
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
            <div className="flex items-center gap-2 py-4 text-[hsl(var(--color-semantic-success-700-hsl))]">
              <CheckCircle className="h-5 w-5" />
              <span>Alle Cross-Compliance-Anforderungen erfüllt.</span>
            </div>
          ) : (
            <div className="space-y-3">
              {recentActions.map(action => (
                <div key={action.id} className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="flex items-center gap-3">
                    {action.erfuellt ? (
                      <CheckCircle className="h-5 w-5 shrink-0 text-[hsl(var(--color-semantic-success-700-hsl))]" />
                    ) : (
                      <XCircle className="h-5 w-5 shrink-0 text-destructive" />
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
                      ? <Badge variant="success">Erfüllt</Badge>
                      : <Badge variant="destructive">Offen</Badge>}
                    <Button variant="ghost" size="sm" onClick={() => openComplianceDetails(action)}>Details</Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Warnungen */}
      {!isLoading && zulAbgelaufen > 0 && (
        <Card className="border-[hsl(var(--color-semantic-warning-500-hsl)/0.4)] bg-[hsl(var(--color-semantic-warning-50-hsl))]">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-[hsl(var(--color-semantic-warning-700-hsl))]">
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
