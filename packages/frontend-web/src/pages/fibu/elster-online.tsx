/**
 * ELSTER Online – Integrierter UStVA-Workflow
 * Prozedere: Berechnen aus Sachkonten → ELSTER-XML exportieren → Upload bei Mein ELSTER
 * Referenz: JuryOberst/Elster (GitHub), offizielle ELSTER-Doku (elster.de)
 */

import { useMemo, useRef, useState } from 'react'
import { Link } from '@/app/routing/typed-router'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  ArrowLeft,
  Calculator,
  Download,
  ExternalLink,
  AlertCircle,
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import {
  useVATReturns,
  useCalculateVATReturn,
  useFibuCockpit,
  downloadELSTERXml,
  type VATReturn,
} from '@/lib/api/fibu'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import { useTouchDevice } from '@/hooks/useTouchDevice'

const MEIN_ELSTER_URL = 'https://www.elster.de/eportal/login'
const MONATE = [
  { value: '2025-01', label: 'Januar 2025' },
  { value: '2025-02', label: 'Februar 2025' },
  { value: '2025-03', label: 'März 2025' },
  { value: '2025-04', label: 'April 2025' },
  { value: '2025-05', label: 'Mai 2025' },
  { value: '2025-06', label: 'Juni 2025' },
  { value: '2025-07', label: 'Juli 2025' },
  { value: '2025-08', label: 'August 2025' },
  { value: '2025-09', label: 'September 2025' },
  { value: '2025-10', label: 'Oktober 2025' },
  { value: '2025-11', label: 'November 2025' },
  { value: '2025-12', label: 'Dezember 2025' },
]

function formatCurrency(val: number): string {
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(val)
}

function StatusBadge({ status }: { status: VATReturn['status'] }) {
  const map: Record<VATReturn['status'], { label: string; variant: 'default' | 'secondary' | 'outline' | 'destructive' }> = {
    draft: { label: 'Entwurf', variant: 'secondary' },
    calculated: { label: 'Berechnet', variant: 'outline' },
    validated: { label: 'Geprüft', variant: 'default' },
    submitted: { label: 'Übermittelt', variant: 'default' },
  }
  const { label, variant } = map[status] ?? { label: status, variant: 'secondary' }
  return <Badge variant={variant}>{label}</Badge>
}

export default function ElsterOnlinePage(): JSX.Element {
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const [period, setPeriod] = useState('2025-01')
  const downloadPendingRef = useRef(new Set<string>())
  const [downloadPending, setDownloadPending] = useState<Set<string>>(() => new Set())

  const { data: fibuCockpit } = useFibuCockpit()
  const { data: returns = [], isLoading: listLoading, refetch } = useVATReturns()
  const calculateMutation = useCalculateVATReturn()
  const latestReturn = useMemo(() => returns[0], [returns])
  const operationalStatus = normalizeOperationalStatus(
    returns.some((item) => item.status === 'validated') ? 'wartet_auf_mensch' : latestReturn?.status || 'offen',
  )
  const contextSections = [
    {
      title: 'ELSTER-Lage',
      items: [
        { label: 'UStVA-Laeufe', value: `${fibuCockpit.tax.vat_return_count}` },
        { label: 'Freigegeben', value: `${fibuCockpit.tax.approved_count}` },
        { label: 'Letzte Periode', value: fibuCockpit.tax.latest_period ?? 'n/a' },
      ],
    },
    {
      title: 'Rueckkopplung',
      items: [
        { label: 'eBilanz', value: fibuCockpit.tax.e_bilanz_ready ? 'bereit' : 'vorbereiten' },
        { label: 'E-Clearing', value: fibuCockpit.tax.e_clearing_ready ? 'bereit' : 'Rueckmeldung offen' },
        { label: 'Letzte Einreichung', value: fibuCockpit.tax.latest_submission_at ? new Date(fibuCockpit.tax.latest_submission_at).toLocaleDateString('de-DE') : 'noch nicht' },
      ],
    },
  ]
  const timelineItems = [
    {
      label: latestReturn ? `Aktive Periode ${latestReturn.period}` : 'Noch keine Periode berechnet',
      detail: latestReturn
        ? `Status ${latestReturn.status} mit Zahllast ${formatCurrency(Number(latestReturn.vat_payable))}.`
        : 'Schritt 1 erzeugt den ersten belastbaren UStVA-Lauf.',
    },
    {
      label: fibuCockpit.tax.latest_submission_at ? 'Letzte Einreichung vorhanden' : 'Noch keine Einreichung',
      detail: fibuCockpit.tax.latest_submission_at
        ? 'Der Meldepfad hat bereits eine uebermittelte Vorperiode.'
        : 'Der Online-Pfad dient aktuell als erster produktiver Einreichungspfad.',
      timestamp: fibuCockpit.tax.latest_submission_at ?? null,
    },
  ]

  const handleCalculate = async () => {
    try {
      await calculateMutation.mutateAsync({ period })
      toast({ title: 'UStVA berechnet', description: `Zeitraum ${period} wurde aus dem Sachkonto ermittelt.` })
      refetch()
    } catch (_rawErr: unknown) {
      const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({
        variant: 'destructive',
        title: 'Fehler',
        description: e?.message ?? 'Berechnung fehlgeschlagen',
      })
    }
  }

  const handleDownload = async (r: VATReturn) => {
    if (downloadPendingRef.current.has(r.id)) return
    downloadPendingRef.current.add(r.id)
    setDownloadPending(new Set(downloadPendingRef.current))
    try {
      await downloadELSTERXml(r.id, r.period)
      toast({ title: 'ELSTER-XML heruntergeladen', description: `UStVA_${r.period}_ELSTER.xml` })
    } catch (_rawErr: unknown) {
      const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({
        variant: 'destructive',
        title: 'Export fehlgeschlagen',
        description: e?.message ?? 'ELSTER-XML konnte nicht erstellt werden',
      })
    } finally {
      downloadPendingRef.current.delete(r.id)
      setDownloadPending(new Set(downloadPendingRef.current))
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-4 p-3 md:p-6">
      <div>
        <h1 className="text-2xl font-bold md:text-3xl">ELSTER (Online)</h1>
        <p className="text-muted-foreground">USt-Voranmeldung berechnen, ELSTER-konform exportieren und bei Mein ELSTER einreichen</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>UStVA-Lauf</CardTitle>
          <CardDescription>Periode berechnen, XML exportieren, bei Mein ELSTER einreichen</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Schritt 1: Berechnen */}
          <section>
            <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-primary text-xs">1</span>
              UStVA aus Sachkonten berechnen
            </h3>
            <div className="flex flex-wrap items-center gap-3">
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                aria-label="UStVA-Periode"
                className="min-h-touch touch-manipulation rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {MONATE.map((m) => (
                  <option key={m.value} value={m.value}>{m.label}</option>
                ))}
              </select>
              <Button
                onClick={handleCalculate}
                disabled={calculateMutation.isPending}
                className="min-h-touch touch-manipulation"
              >
                <Calculator className="h-4 w-4 mr-2" />
                {calculateMutation.isPending ? 'Berechne…' : 'Berechnen'}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Ermittelt Umsätze und Vorsteuern aus verbuchten Belegen (Steuerschlüssel mit UStVA-Position).
            </p>
          </section>

          {/* Schritt 2: Liste & Export */}
          <section>
            <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-primary text-xs">2</span>
              Berechnete UStVA auswählen und ELSTER-XML exportieren
            </h3>
            {listLoading ? (
              <p className="text-sm text-muted-foreground">Lade UStVA-Liste…</p>
            ) : returns.length === 0 ? (
              <div className="rounded-lg border border-dashed p-4 text-center text-sm text-muted-foreground">
                <AlertCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                Noch keine UStVA berechnet. Nutzen Sie Schritt 1, um eine Voranmeldung aus dem Sachkonto zu erstellen.
              </div>
            ) : (
              <div className="space-y-2">
                {returns.map((r) => (
                  <div
                    key={r.id}
                    className="flex flex-col gap-3 rounded-lg border p-3 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <div>
                        <p className="font-medium">{r.period}</p>
                        <p className="text-sm text-muted-foreground">
                          Zahllast {formatCurrency(Number(r.vat_payable))} · {r.taxpayer_name}
                        </p>
                      </div>
                      <StatusBadge status={r.status} />
                    </div>
                    <Button
                      variant="outline"
                      className="min-h-touch touch-manipulation"
                      disabled={downloadPending.has(r.id)}
                      onClick={() => void handleDownload(r)}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      {downloadPending.has(r.id) ? 'Lädt…' : 'ELSTER-XML'}
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Schritt 3: Mein ELSTER */}
          <section>
            <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-primary text-xs">3</span>
              Übermittlung bei Mein ELSTER
            </h3>
            <div className="rounded-lg bg-muted/50 p-4 space-y-2">
              <ol className="list-decimal list-inside text-sm space-y-1">
                <li>ELSTER-XML herunterladen (Schritt 2)</li>
                <li>
                  <a
                    href={MEIN_ELSTER_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex min-h-touch items-center gap-1 text-primary hover:underline"
                  >
                    Mein ELSTER <ExternalLink className="h-3 w-3" />
                  </a>{' '}
                  öffnen und anmelden
                </li>
                <li>Umsatzsteuer-Voranmeldung → „Datei einreichen“ → XML-Datei hochladen</li>
                <li>Prüfen und elektronisch übermitteln</li>
              </ol>
              <p className="text-xs text-muted-foreground mt-2">
                Die exportierte XML entspricht dem Schema Anmeldungssteuern v2023 (finkonsens.de) und ISO-8859-15.
              </p>
            </div>
          </section>

          {/* Weitere Links */}
          <div className="flex flex-wrap gap-2 pt-2 border-t">
            <Link to="/export/umsatzsteuervoranmeldung">
              <Button variant="outline" className="min-h-touch">UStVA-Assistent (manuell)</Button>
            </Link>
            <Link to="/finance/ustva">
              <Button variant="outline" className="min-h-touch">UStVA-Verwaltung</Button>
            </Link>
            <Link to="/fibu/schnittstellen-center">
              <Button variant="outline" className="min-h-touch">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Schnittstellen-Center
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
      {!isTouch ? (
        <>
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">UStVA-Läufe</CardTitle></CardHeader>
              <CardContent><div className="text-2xl font-semibold">{fibuCockpit.tax.vat_return_count}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">eBilanz</CardTitle></CardHeader>
              <CardContent><div className="text-sm font-semibold">{fibuCockpit.tax.e_bilanz_ready ? 'bereit' : 'Kontext ergänzen'}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">E-Clearing</CardTitle></CardHeader>
              <CardContent><div className="text-sm font-semibold">{fibuCockpit.tax.e_clearing_ready ? 'bereit' : 'Rückmeldung offen'}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Letzte Einreichung</CardTitle></CardHeader>
              <CardContent><div className="text-sm font-semibold">{fibuCockpit.tax.latest_submission_at ? new Date(fibuCockpit.tax.latest_submission_at).toLocaleDateString('de-DE') : 'noch nicht'}</div></CardContent>
            </Card>
          </div>
          <OperationalCaseHeader
            title="ELSTER Online"
            description="Der Online-Meldepfad zeigt Berechnungsstand, Freigabedruck und Rueckkopplung vor dem XML-Export."
            status={operationalStatus}
            owner="Steuer / FIBU"
            blocker={returns.length === 0 ? 'Es liegt noch kein berechneter UStVA-Lauf fuer den Export vor.' : null}
            nextAction={returns.length === 0 ? 'Periode berechnen' : returns.some((item) => item.status === 'validated') ? 'Freigegebene UStVA exportieren und einreichen' : 'Aktuelle Periode pruefen'}
            caseLabel="Vorgang: ELSTER-Einreichung"
            tags={['FIBU', 'Meldewesen']}
          />
          <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
            <OperationalTimeline title="Meldepfad" items={timelineItems} />
            <OperationalContextPanel title="ELSTER-Kontext" sections={contextSections} />
          </div>
        </>
      ) : null}
    </div>
  )
}
