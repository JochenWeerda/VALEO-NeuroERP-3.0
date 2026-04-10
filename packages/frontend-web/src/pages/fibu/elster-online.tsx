/**
 * ELSTER Online – Integrierter UStVA-Workflow
 * Prozedere: Berechnen aus Sachkonten → ELSTER-XML exportieren → Upload bei Mein ELSTER
 * Referenz: JuryOberst/Elster (GitHub), offizielle ELSTER-Doku (elster.de)
 */

import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  FileText,
  ArrowLeft,
  Calculator,
  Download,
  ExternalLink,
  CheckCircle,
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
  const [period, setPeriod] = useState('2025-01')

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
    } catch (e: any) {
      toast({
        variant: 'destructive',
        title: 'Fehler',
        description: e?.message ?? 'Berechnung fehlgeschlagen',
      })
    }
  }

  const handleDownload = async (r: VATReturn) => {
    try {
      await downloadELSTERXml(r.id, r.period)
      toast({ title: 'ELSTER-XML heruntergeladen', description: `UStVA_${r.period}_ELSTER.xml` })
    } catch (e: any) {
      toast({
        variant: 'destructive',
        title: 'Export fehlgeschlagen',
        description: e?.message ?? 'ELSTER-XML konnte nicht erstellt werden',
      })
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
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
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <span className="rounded-lg border bg-muted/40 p-2">
              <FileText className="h-5 w-5" />
            </span>
            <div>
              <CardTitle>ELSTER (Online)</CardTitle>
              <CardDescription>
                USt-Voranmeldung berechnen, ELSTER-konform exportieren und bei Mein ELSTER einreichen
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
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
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {MONATE.map((m) => (
                  <option key={m.value} value={m.value}>{m.label}</option>
                ))}
              </select>
              <Button
                onClick={handleCalculate}
                disabled={calculateMutation.isPending}
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
                    className="flex items-center justify-between rounded-lg border p-3"
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
                      size="sm"
                      onClick={() => handleDownload(r)}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      ELSTER-XML
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
                    className="text-primary hover:underline inline-flex items-center gap-1"
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
              <Button variant="outline" size="sm">UStVA-Assistent (manuell)</Button>
            </Link>
            <Link to="/finance/ustva">
              <Button variant="outline" size="sm">UStVA-Verwaltung</Button>
            </Link>
            <Link to="/fibu/schnittstellen-center">
              <Button variant="outline" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Schnittstellen-Center
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
