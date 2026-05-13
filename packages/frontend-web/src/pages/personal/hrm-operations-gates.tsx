import { useMemo, useState } from 'react'
import {
  AlertTriangle,
  ArrowRight,
  Calendar,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  FileCheck2,
  FilePlus,
  FileText,
  History,
  Plug,
  Shield,
  ShieldAlert,
  User,
  X,
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/components/ui/toast-provider'
import { getAxiosErrorMessage } from '@/lib/api-client'
import {
  useCreateHrmOperationsGateEvidence,
  useDecideHrmOperationsGate,
  useHrmOperationsGates,
  useHrmOperationsGoLivePolicy,
  useRecordHrmOperationsGateProbe,
  type HrmOperationsGate,
} from '@/lib/api/personal'

type GateFormState = {
  evidenceType: string
  title: string
  artifactRef: string
  submittedBy: string
  provider: string
  probeType: string
  probeResult: 'passed' | 'failed' | 'manual' | 'not_configured'
  performedBy: string
  decidedBy: string
  decisionReason: string
}

const defaultForm: GateFormState = {
  evidenceType: 'Freigabedokument',
  title: '',
  artifactRef: '',
  submittedBy: '',
  provider: '',
  probeType: 'Startpruefung',
  probeResult: 'passed',
  performedBy: '',
  decidedBy: '',
  decisionReason: '',
}

const statusLabel: Record<string, string> = {
  external_evidence_required: 'Nachweis offen',
  evidence_submitted: 'Nachweis liegt vor',
  probe_passed: 'Test bestanden',
  approved: 'Erledigt',
  rejected: 'Zurueckgewiesen',
  external_gates_defined: 'Vorbereitet',
}

const probeLabel: Record<string, string> = {
  passed: 'bestanden',
  failed: 'fehlgeschlagen',
  manual: 'manuell geprueft',
  not_configured: 'nicht konfiguriert',
}

function checkpointStatus(gate: HrmOperationsGate): 'offen' | 'stopper' | 'erledigt' | 'teilweise' {
  if (gate.status === 'approved') return 'erledigt'
  if (gate.status === 'rejected' || (gate.goLiveBlocking && gate.status !== 'approved')) return 'stopper'
  if (gate.status === 'evidence_submitted' || gate.status === 'probe_passed') return 'teilweise'
  return 'offen'
}

function formatDate(value?: string | null): string {
  if (!value) return '-'
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString('de-DE')
}

function formatDateOnly(value?: string | null): string {
  if (!value) return '-'
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleDateString('de-DE')
}

function simpleGateTitle(gate: HrmOperationsGate): string {
  const titles: Record<string, string> = {
    'eau-communication': 'Krankmeldungen und eAU',
    'datev-payroll': 'Lohnabrechnung und DATEV',
    'office-sso-connectors': 'Anmeldung, Kalender und Benutzerkonten',
    'documents-esign': 'Vertraege, Dokumente und Unterschriften',
    'privacy-contracts': 'Datenschutz-Vertraege und Anbieter',
    'works-council-dsfa': 'Betriebsrat, Datenschutzpruefung und KI',
    'retention-legal': 'Aufbewahren und Loeschen von Personalunterlagen',
  }
  return titles[gate.id] ?? gate.title
}

function gatePurpose(gate: HrmOperationsGate): string {
  const purposes: Record<string, string> = {
    'eau-communication': 'Krankmeldungen duerfen erst produktiv laufen, wenn Zugang, Fristen und Rueckmeldungen ohne Diagnosedaten geklaert sind.',
    'datev-payroll': 'Lohnabrechnung darf erst uebergeben werden, wenn DATEV-Format, Testexport und Steuerberaterfreigabe vorliegen.',
    'office-sso-connectors': 'Anmeldung und Kalender duerfen erst verbunden werden, wenn Rollen, MFA und private Termine sauber geschuetzt sind.',
    'documents-esign': 'Vertraege duerfen erst digital erzeugt und unterschrieben werden, wenn Vorlage, Ablage und Signaturweg freigegeben sind.',
    'privacy-contracts': 'Externe Anbieter duerfen erst produktiv genutzt werden, wenn Datenschutzvertrag, Hostingort und Datenexport geklaert sind.',
    'works-council-dsfa': 'Auswertungen und KI duerfen erst laufen, wenn Betriebsrat, DSFA und menschliche Kontrolle geklaert sind.',
    'retention-legal': 'Personalunterlagen duerfen erst automatisch aufbewahrt oder geloescht werden, wenn die Rechtsfreigabe vorliegt.',
  }
  return purposes[gate.id] ?? gate.title
}

function nextAction(gate: HrmOperationsGate): string {
  if (gate.status === 'approved') return 'Kein Sofortbedarf. Beim naechsten Regeltermin erneut pruefen.'
  if (gate.status === 'rejected') return 'Klaeren, warum der Punkt zurueckgewiesen wurde, und einen neuen Nachweis einreichen.'
  if (gate.evidenceCount < 1) return 'Den fehlenden Nachweis als Datei, Link oder Aktenzeichen eintragen.'
  if (!gate.lastProbeStatus || gate.lastProbeStatus === 'failed' || gate.lastProbeStatus === 'not_configured') return 'Den fachlichen oder technischen Test nachtragen.'
  if (gate.status === 'probe_passed' || gate.status === 'evidence_submitted') return 'Die verantwortliche Person soll den Punkt freigeben oder zurueckweisen.'
  return 'Pruefen, welcher Nachweis noch fehlt.'
}

function StatusPill({ status }: { status: ReturnType<typeof checkpointStatus> }): JSX.Element {
  const config = {
    offen: { label: 'Nachweis offen', className: 'border-amber-200 bg-amber-50 text-amber-700', icon: AlertTriangle },
    stopper: { label: 'Stopper', className: 'border-red-200 bg-red-50 text-red-700', icon: ShieldAlert },
    erledigt: { label: 'Erledigt', className: 'border-emerald-200 bg-emerald-50 text-emerald-700', icon: CheckCircle2 },
    teilweise: { label: 'Teilweise', className: 'border-blue-200 bg-blue-50 text-blue-700', icon: FileCheck2 },
  }[status]
  const Icon = config.icon
  return (
    <span className={`inline-flex items-center gap-1.5 rounded border px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide ${config.className}`}>
      <Icon className="h-3 w-3" />
      {config.label}
    </span>
  )
}

function KpiItem({ label, value, icon: Icon, colorClass }: { label: string; value: string | number; icon: typeof CheckCircle2; colorClass: string }): JSX.Element {
  return (
    <div className="flex flex-col gap-2 rounded border border-gray-200 border-b-gray-100 border-b-4 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-bold uppercase tracking-[0.1em] text-gray-500">{label}</span>
        <Icon className={`h-4 w-4 ${colorClass}`} />
      </div>
      <span className="text-2xl font-bold leading-none text-gray-900">{value}</span>
    </div>
  )
}

function GateActions({ gate }: { gate: HrmOperationsGate }): JSX.Element {
  const { push } = useToast()
  const evidenceMutation = useCreateHrmOperationsGateEvidence(gate.id)
  const probeMutation = useRecordHrmOperationsGateProbe(gate.id)
  const decisionMutation = useDecideHrmOperationsGate(gate.id)
  const [form, setForm] = useState<GateFormState>({
    ...defaultForm,
    title: `${simpleGateTitle(gate)} Nachweis`,
    provider: simpleGateTitle(gate).split(' ')[0] || gate.id,
  })

  const update = <K extends keyof GateFormState>(key: K, value: GateFormState[K]): void => {
    setForm((current) => ({ ...current, [key]: value }))
  }

  const createEvidence = (): void => {
    if (!form.title.trim() || !form.artifactRef.trim() || !form.submittedBy.trim()) {
      push('Bitte Titel, Ablageort und eingetragene Person angeben.')
      return
    }
    evidenceMutation.mutate(
      {
        evidenceType: form.evidenceType.trim(),
        title: form.title.trim(),
        artifactRef: form.artifactRef.trim(),
        submittedBy: form.submittedBy.trim(),
        metadata: { gateTitle: simpleGateTitle(gate) },
      },
      {
        onSuccess: () => {
          push('Nachweis gespeichert.')
          update('artifactRef', '')
        },
        onError: (error) => push(getAxiosErrorMessage(error)),
      },
    )
  }

  const recordProbe = (): void => {
    if (!form.provider.trim() || !form.probeType.trim() || !form.performedBy.trim()) {
      push('Bitte System, Pruefung und getestete Person angeben.')
      return
    }
    probeMutation.mutate(
      {
        provider: form.provider.trim(),
        probeType: form.probeType.trim(),
        result: form.probeResult,
        performedBy: form.performedBy.trim(),
        details: { gateTitle: simpleGateTitle(gate) },
      },
      {
        onSuccess: () => push('Test gespeichert.'),
        onError: (error) => push(getAxiosErrorMessage(error)),
      },
    )
  }

  const decide = (decision: 'approve' | 'reject'): void => {
    if (!form.decidedBy.trim()) {
      push('Bitte verantwortliche Person angeben.')
      return
    }
    if (decision === 'reject' && !form.decisionReason.trim()) {
      push('Bitte Kommentar fuer die Zurueckweisung angeben.')
      return
    }
    decisionMutation.mutate(
      {
        decision,
        decidedBy: form.decidedBy.trim(),
        reason: form.decisionReason.trim() || undefined,
      },
      {
        onSuccess: () => push(decision === 'approve' ? 'Pruefpunkt freigegeben.' : 'Pruefpunkt zurueckgewiesen.'),
        onError: (error) => push(getAxiosErrorMessage(error)),
      },
    )
  }

  const busy = evidenceMutation.isPending || probeMutation.isPending || decisionMutation.isPending

  return (
    <div className="flex flex-col gap-4">
      <div className="rounded border border-gray-200 bg-white p-4 shadow-sm">
        <h4 className="mb-4 border-b pb-2 text-xs font-bold uppercase text-gray-800">1. Nachweis ablegen</h4>
        <div className="space-y-4">
          <div>
            <Label className="mb-1 block text-[10px] font-bold uppercase text-gray-400" htmlFor={`${gate.id}-evidence-type`}>Art des Nachweises</Label>
            <Input id={`${gate.id}-evidence-type`} value={form.evidenceType} onChange={(event) => update('evidenceType', event.target.value)} />
          </div>
          <div>
            <Label className="mb-1 block text-[10px] font-bold uppercase text-gray-400" htmlFor={`${gate.id}-title`}>Titel / Bezeichnung</Label>
            <Input id={`${gate.id}-title`} value={form.title} onChange={(event) => update('title', event.target.value)} />
          </div>
          <div>
            <Label className="mb-1 block text-[10px] font-bold uppercase text-gray-400" htmlFor={`${gate.id}-artifact`}>Ablageort / Link</Label>
            <div className="relative">
              <Input id={`${gate.id}-artifact`} value={form.artifactRef} onChange={(event) => update('artifactRef', event.target.value)} placeholder="dms://..." className="pr-8 font-mono text-xs" />
              <ExternalLink className="absolute right-2 top-2.5 h-3.5 w-3.5 text-gray-300" />
            </div>
          </div>
          <div>
            <Label className="mb-1 block text-[10px] font-bold uppercase text-gray-400" htmlFor={`${gate.id}-submitted-by`}>Eingetragen von</Label>
            <Input id={`${gate.id}-submitted-by`} value={form.submittedBy} onChange={(event) => update('submittedBy', event.target.value)} />
          </div>
          <Button onClick={createEvidence} disabled={busy} className="w-full gap-2 bg-blue-700 hover:bg-blue-800">
            <FilePlus className="h-4 w-4" />
            Nachweis speichern
          </Button>
        </div>
      </div>

      <div className="rounded border border-gray-200 bg-white p-4 shadow-sm">
        <h4 className="mb-4 border-b pb-2 text-xs font-bold uppercase text-gray-800">2. Test eintragen</h4>
        <div className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <Label className="mb-1 block text-[10px] font-bold uppercase text-gray-400" htmlFor={`${gate.id}-provider`}>System</Label>
              <Input id={`${gate.id}-provider`} value={form.provider} onChange={(event) => update('provider', event.target.value)} />
            </div>
            <div>
              <Label className="mb-1 block text-[10px] font-bold uppercase text-gray-400" htmlFor={`${gate.id}-probe-type`}>Was pruefen?</Label>
              <Input id={`${gate.id}-probe-type`} value={form.probeType} onChange={(event) => update('probeType', event.target.value)} />
            </div>
          </div>
          <div>
            <Label className="mb-1 block text-[10px] font-bold uppercase text-gray-400" htmlFor={`${gate.id}-probe-result`}>Ergebnis</Label>
            <select
              id={`${gate.id}-probe-result`}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={form.probeResult}
              onChange={(event) => update('probeResult', event.target.value as GateFormState['probeResult'])}
            >
              <option value="passed">bestanden</option>
              <option value="failed">fehlgeschlagen</option>
              <option value="manual">manuell geprueft</option>
              <option value="not_configured">nicht konfiguriert</option>
            </select>
          </div>
          <div>
            <Label className="mb-1 block text-[10px] font-bold uppercase text-gray-400" htmlFor={`${gate.id}-performed-by`}>Getestet von</Label>
            <Input id={`${gate.id}-performed-by`} value={form.performedBy} onChange={(event) => update('performedBy', event.target.value)} />
          </div>
          <Button onClick={recordProbe} disabled={busy} className="w-full gap-2 bg-gray-900 hover:bg-black">
            <Plug className="h-4 w-4" />
            Test speichern
          </Button>
        </div>
      </div>

      <div className="rounded border border-gray-200 bg-white p-4 shadow-sm">
        <h4 className="mb-4 border-b pb-2 text-xs font-bold uppercase text-gray-800">3. Freigabe</h4>
        <div className="space-y-4">
          <div>
            <Label className="mb-1 block text-[10px] font-bold uppercase text-gray-400" htmlFor={`${gate.id}-decided-by`}>Verantwortliche Person</Label>
            <Input id={`${gate.id}-decided-by`} value={form.decidedBy} onChange={(event) => update('decidedBy', event.target.value)} />
          </div>
          <div>
            <Label className="mb-1 block text-[10px] font-bold uppercase text-gray-400" htmlFor={`${gate.id}-reason`}>Kommentar</Label>
            <Textarea id={`${gate.id}-reason`} value={form.decisionReason} onChange={(event) => update('decisionReason', event.target.value)} rows={3} />
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <Button onClick={() => decide('approve')} disabled={busy || gate.evidenceCount < 1} className="gap-2 bg-emerald-700 hover:bg-emerald-800">
              <Check className="h-4 w-4" />
              Freigeben
            </Button>
            <Button onClick={() => decide('reject')} disabled={busy} variant="destructive" className="gap-2">
              <X className="h-4 w-4" />
              Zurueckweisen
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

function GateRow({ gate, expanded, onToggle }: { gate: HrmOperationsGate; expanded: boolean; onToggle: () => void }): JSX.Element {
  const status = checkpointStatus(gate)
  const isStopper = gate.goLiveBlocking && gate.status !== 'approved'

  return (
    <div className={`overflow-hidden rounded border bg-white shadow-sm ${isStopper ? 'border-l-4 border-l-red-600' : 'border-gray-200'}`}>
      <button type="button" className="flex w-full items-center justify-between gap-4 p-4 text-left hover:bg-gray-50" onClick={onToggle}>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-3">
            <h3 className="text-[15px] font-bold tracking-tight text-gray-900">{simpleGateTitle(gate)}</h3>
            <StatusPill status={status} />
            {isStopper ? <span className="rounded bg-red-600 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-white">Stopper</span> : null}
          </div>
          <p className="mt-2 truncate text-xs italic text-gray-500">{gatePurpose(gate)}</p>

          <div className="mt-3 grid gap-x-4 gap-y-2 sm:grid-cols-2 lg:grid-cols-6">
            <div className="flex flex-col">
              <span className="text-[9px] font-bold uppercase text-gray-400">Zustaendig</span>
              <span className="flex items-center gap-1.5 text-[13px] font-medium text-gray-700">
                <User className="h-3 w-3 text-gray-400" />
                {gate.ownerRole}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-[9px] font-bold uppercase text-gray-400">Risiko / Prio</span>
              <span className="flex items-center gap-1.5 text-[13px] font-medium text-gray-700">
                <AlertTriangle className={`h-3 w-3 ${gate.riskLevel === 'hoch' ? 'text-red-500' : 'text-amber-500'}`} />
                {gate.riskLevel.toUpperCase()} / {gate.priority}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-[9px] font-bold uppercase text-gray-400">Faellig bis</span>
              <span className="flex items-center gap-1.5 text-[13px] font-medium text-gray-700">
                <Calendar className="h-3 w-3 text-gray-400" />
                {formatDateOnly(gate.dueDate)}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-[9px] font-bold uppercase text-gray-400">Letzter Test</span>
              <span className={`text-[13px] font-bold ${gate.lastProbeStatus === 'passed' ? 'text-emerald-600' : gate.lastProbeStatus === 'failed' ? 'text-red-600' : 'text-gray-700'}`}>
                {gate.lastProbeStatus ? probeLabel[gate.lastProbeStatus] ?? gate.lastProbeStatus : '-'}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-[9px] font-bold uppercase text-gray-400">Nachweise</span>
              <span className="flex items-center gap-1.5 text-[13px] font-medium text-gray-700">
                <FileText className="h-3 w-3 text-blue-500" />
                {gate.evidenceCount}
              </span>
            </div>
            <div className="flex min-w-0 flex-col">
              <span className="text-[9px] font-bold uppercase text-gray-400">Naechste Aktion</span>
              <span className="truncate text-[13px] font-bold text-blue-700">{nextAction(gate)}</span>
            </div>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-4">
          {gate.approvedAt ? (
            <div className="hidden text-right sm:block">
              <p className="text-[9px] font-bold uppercase text-gray-400">Freigegeben</p>
              <p className="text-[13px] font-bold text-emerald-700">{formatDateOnly(gate.approvedAt)}</p>
            </div>
          ) : null}
          {expanded ? <ChevronUp className="h-5 w-5 text-gray-400" /> : <ChevronDown className="h-5 w-5 text-gray-400" />}
        </div>
      </button>

      {expanded ? (
        <div className="border-t border-gray-100 bg-gray-50/30 p-6">
          <div className="grid gap-8 lg:grid-cols-12">
            <div className="flex flex-col gap-6 lg:col-span-8">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded border border-gray-200 bg-white p-4 shadow-sm">
                  <h4 className="mb-4 border-b pb-2 text-xs font-bold uppercase text-gray-700">Was muss vorliegen?</h4>
                  <ul className="space-y-3">
                    {gate.evidenceRequired.map((item) => (
                      <li key={item} className="flex items-start gap-2.5 text-[13px] text-gray-600">
                        <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-blue-600" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="rounded border border-gray-200 bg-white p-4 shadow-sm">
                  <h4 className="mb-4 border-b pb-2 text-xs font-bold uppercase text-gray-700">Wann ist es erledigt?</h4>
                  <ul className="space-y-3">
                    {gate.acceptanceCriteria.map((item) => (
                      <li key={item} className="flex items-start gap-2.5 text-[13px] text-gray-600">
                        <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-600" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="rounded border border-gray-200 bg-white p-4 shadow-sm">
                <h4 className="mb-4 border-b pb-2 text-xs font-bold uppercase text-gray-700">Was wird protokolliert?</h4>
                <div className="mb-4 flex flex-wrap gap-2">
                  {gate.auditTrail.map((item) => (
                    <span key={item} className="rounded border border-gray-200 bg-gray-100 px-2 py-0.5 text-[10px] font-bold uppercase text-gray-500">
                      {item}
                    </span>
                  ))}
                </div>
                <div className="space-y-2 text-[12px] text-gray-500">
                  <p className="flex items-center gap-2">
                    <History className="h-3 w-3 text-gray-400" />
                    Letzte Aenderung: {formatDate(gate.lastChangedAt)}
                  </p>
                  <p className="flex items-center gap-2">
                    <History className="h-3 w-3 text-gray-400" />
                    Rollen mit Schreibrecht: {gate.allowedRoles.join(', ')}
                  </p>
                  <p className="flex items-center gap-2">
                    <History className="h-3 w-3 text-gray-400" />
                    Nur lesend: {gate.readOnlyRoles.join(', ')}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 rounded-lg border border-blue-100 bg-blue-50 p-4">
                <ArrowRight className="mt-0.5 h-4.5 w-4.5 shrink-0 text-blue-700" />
                <div>
                  <h5 className="mb-0.5 text-[13px] font-bold text-blue-950">Empfohlene naechste Aktion</h5>
                  <p className="text-[13px] text-blue-800">{nextAction(gate)}</p>
                </div>
              </div>
            </div>

            <div className="lg:col-span-4">
              <GateActions gate={gate} />
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}

export default function HrmOperationsGatesPage(): JSX.Element {
  const gatesQuery = useHrmOperationsGates()
  const policyQuery = useHrmOperationsGoLivePolicy()
  const gates = useMemo(() => gatesQuery.data?.gates ?? [], [gatesQuery.data?.gates])
  const [expandedGateId, setExpandedGateId] = useState<string | null>(null)
  const approvedCount = gates.filter((gate) => gate.status === 'approved').length
  const evidenceCount = gates.reduce((sum, gate) => sum + gate.evidenceCount, 0)
  const blockerCount = policyQuery.data?.blockerCount ?? gates.filter((gate) => gate.goLiveBlocking && gate.status !== 'approved').length
  const isGoLiveAllowed = policyQuery.data?.goLiveAllowed ?? blockerCount === 0
  const blockers = policyQuery.data?.blockers ?? gates.filter((gate) => gate.goLiveBlocking && gate.status !== 'approved')

  if (gatesQuery.isLoading && gates.length === 0) {
    return (
      <div className="space-y-4 bg-[#f5f6f7] p-3 md:p-6">
        <Skeleton className="h-16 w-full" />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((item) => <Skeleton key={item} className="h-24" />)}
        </div>
        <Skeleton className="h-96" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#f5f6f7] pb-12 text-gray-900">
      <header className="sticky top-0 z-20 border-b border-gray-300 bg-white shadow-sm">
        <div className="mx-auto flex min-h-[72px] max-w-[1440px] items-center justify-between gap-4 px-4 py-3 lg:px-8">
          <div className="flex flex-col gap-0.5">
            <div className="flex items-center gap-3">
              <div className="flex h-7 w-7 items-center justify-center rounded-sm bg-[#005ca5] text-xs font-black text-white">V</div>
              <h1 className="text-xl font-bold tracking-tight text-gray-900">HRM-Betriebsfreigaben</h1>
            </div>
            <p className="text-[11px] font-bold uppercase tracking-wide text-gray-500">
              Admin-Cockpit fuer technische, rechtliche und organisatorische Betriebsbereitschaft
            </p>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden flex-col items-end xl:flex">
              <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Benutzergruppe: Admin / Legal / HR</span>
              <span className="max-w-[320px] text-right text-[11px] italic leading-tight text-gray-500">
                Nur fuer autorisierte Admins. Mitarbeitende nutzen diese Ansicht nicht.
              </span>
            </div>
            <div className={`flex items-center gap-2.5 rounded-sm border-2 px-4 py-2.5 shadow-sm ${isGoLiveAllowed ? 'border-emerald-500 bg-emerald-50 text-emerald-700' : 'border-red-500 bg-red-50 text-red-700'}`}>
              <div className={`h-3 w-3 rounded-full ${isGoLiveAllowed ? 'bg-emerald-600' : 'bg-red-600'}`} />
              <span className="text-sm font-black uppercase tracking-[0.05em]">{isGoLiveAllowed ? 'Produktivstart erlaubt' : 'Produktivstart gestoppt'}</span>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto mt-8 max-w-[1440px] space-y-6 px-4 lg:px-8">
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiItem label="Pruefpunkte Gesamt" value={gates.length} icon={Shield} colorClass="text-blue-700" />
          <KpiItem label="Erledigt" value={approvedCount} icon={CheckCircle2} colorClass="text-emerald-600" />
          <KpiItem label="Aktive Stopper" value={blockerCount} icon={ShieldAlert} colorClass="text-red-600" />
          <KpiItem label="Nachweise Gesamt" value={evidenceCount} icon={FileText} colorClass="text-blue-500" />
        </section>

        <section className="overflow-hidden rounded border border-gray-300 border-t-4 border-t-[#005ca5] bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-gray-200 bg-gray-50/50 px-6 py-4">
            <div className="flex items-center gap-2.5">
              <Shield className="h-5 w-5 text-[#005ca5]" />
              <h2 className="text-base font-bold text-gray-900">Darf HRM produktiv starten?</h2>
            </div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400">Sicherheitspruefung</span>
          </div>
          <div className="flex flex-wrap items-start gap-8 p-6 lg:flex-nowrap lg:gap-12">
            <div className="flex-1 space-y-4">
              <p className="max-w-3xl text-sm leading-relaxed text-gray-600">
                {policyQuery.data?.summary ?? gatesQuery.data?.summary ?? 'Der Produktivstart wird aus offenen Stoppern und Freigaben berechnet.'}
              </p>
              <p className="max-w-3xl text-sm leading-relaxed text-gray-600">
                Sobald mindestens ein kritischer Pruefpunkt offen ist, bleibt die Systemampel rot. Normale Mitarbeitende nutzen diese Admin-Seite nicht.
              </p>
              <div className="flex flex-wrap gap-3">
                {blockers.map((gate) => (
                  <span key={gate.id} className="flex items-center gap-2 rounded border border-red-200 bg-red-50 px-3 py-1.5 text-[11px] font-bold uppercase tracking-wide text-red-700">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    {simpleGateTitle(gate)}
                  </span>
                ))}
              </div>
            </div>

            <div className={`flex min-w-full flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed p-8 text-center sm:min-w-[320px] ${isGoLiveAllowed ? 'border-emerald-200 bg-emerald-50' : 'border-red-200 bg-red-50'}`}>
              <div className={`flex h-12 w-12 items-center justify-center rounded-full ${isGoLiveAllowed ? 'bg-emerald-600' : 'bg-red-600'}`}>
                {isGoLiveAllowed ? <Check className="h-7 w-7 text-white" strokeWidth={3} /> : <X className="h-7 w-7 text-white" strokeWidth={3} />}
              </div>
              <h4 className={`text-xl font-black uppercase tracking-tight ${isGoLiveAllowed ? 'text-emerald-700' : 'text-red-700'}`}>
                {isGoLiveAllowed ? 'Freigabe erteilt' : 'Keine Freigabe'}
              </h4>
              <p className="text-xs font-medium text-gray-500">
                {isGoLiveAllowed ? 'Alle kritischen Anforderungen wurden erfuellt.' : `${blockerCount} kritische Pruefpunkte verhindern aktuell die Produktivsetzung.`}
              </p>
            </div>
          </div>
        </section>

        <div className="flex flex-col gap-3 pt-4 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="w-fit border-b-2 border-b-[#005ca5] pb-1 text-lg font-bold text-gray-900">Pruefliste Betriebsbereitschaft</h2>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" className="text-xs font-bold">PDF Export</Button>
            <Button size="sm" className="gap-2 bg-[#005ca5] text-xs font-bold hover:bg-[#004a85]">
              <FilePlus className="h-4 w-4" />
              Neuen Pruefpunkt anlegen
            </Button>
          </div>
        </div>

        <div className="space-y-4">
          {gates.map((gate) => (
            <GateRow
              key={gate.id}
              gate={gate}
              expanded={expandedGateId === gate.id}
              onToggle={() => setExpandedGateId((current) => current === gate.id ? null : gate.id)}
            />
          ))}
        </div>

        <footer className="mt-16 flex items-center justify-between border-t border-gray-300 pt-8 opacity-60">
          <div className="flex gap-8 text-[10px] font-bold uppercase tracking-[0.2em]">
            <span>Valeo NeuroERP</span>
            <span className="hidden sm:inline">System: HR-OPS</span>
          </div>
          <button className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-gray-600">
            <History className="h-3 w-3" />
            System-Logbuch einsehen
          </button>
        </footer>
      </main>
    </div>
  )
}
