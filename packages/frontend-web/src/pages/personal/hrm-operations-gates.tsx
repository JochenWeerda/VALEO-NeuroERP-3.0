import { useMemo, useState } from 'react'
import {
  AlertTriangle,
  ArrowRight,
  BriefcaseBusiness,
  Calendar,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  ClipboardCheck,
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

type RoleFocus = 'all' | 'hr' | 'payroll' | 'it' | 'privacy' | 'legal' | 'management'

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

const templateByGate: Record<string, { label: string; path: string }> = {
  'eau-communication': { label: 'eAU-Freigabeprotokoll', path: 'docs/hrm-go-live-templates/10_eau_freigabeprotokoll.md' },
  'datev-payroll': { label: 'DATEV-/Payroll-Abnahme', path: 'docs/hrm-go-live-templates/11_datev_payroll_abnahme.md' },
  'office-sso-connectors': { label: 'Office-/SSO-Abnahme', path: 'docs/hrm-go-live-templates/12_office_sso_abnahme.md' },
  'documents-esign': { label: 'DMS-/E-Signatur-Abnahme', path: 'docs/hrm-go-live-templates/13_dms_esignatur_rendering_abnahme.md' },
  'privacy-contracts': { label: 'AVV-/DPA-Pruefprotokoll', path: 'docs/hrm-go-live-templates/05_avv_dpa_pruefprotokoll.md' },
  'works-council-dsfa': { label: 'DSFA-/Reporting-Freigabe', path: 'docs/hrm-go-live-templates/06_dsfa_vorpruefung.md' },
  'retention-legal': { label: 'Retention- und Loeschkonzept', path: 'docs/hrm-go-live-templates/09_retention_loeschkonzept.md' },
}

const gatePresets: Record<string, { evidenceTypes: string[]; probeTypes: string[]; provider: string }> = {
  'eau-communication': {
    evidenceTypes: ['eAU-Testprotokoll', 'Rollenpruefung', 'Fehlerprozess', 'Datenschutzfreigabe'],
    probeTypes: ['Testabruf eAU', 'Zertifikatspruefung', 'Rollenpruefung', 'Auditlog-Pruefung'],
    provider: 'eAU-Kommunikation',
  },
  'datev-payroll': {
    evidenceTypes: ['Testexport', 'Steuerberaterfreigabe', 'Lohnartenmapping', 'Kostenstellenmapping'],
    probeTypes: ['DATEV-Testexport', 'Importpruefung Steuerberater', 'Monatsabschlussprobe'],
    provider: 'DATEV/Payroll',
  },
  'office-sso-connectors': {
    evidenceTypes: ['SSO-Test', 'MFA-Nachweis', 'Rollenmapping', 'Deprovisioning-Test'],
    probeTypes: ['SSO-Login', 'MFA-Challenge', 'Rollenmapping', 'Leaver-Test'],
    provider: 'Identity Provider',
  },
  'documents-esign': {
    evidenceTypes: ['PDF-Test', 'DMS-Ablage', 'Signaturtest', 'Dokumentklassenpruefung'],
    probeTypes: ['LibreOffice-Rendering', 'DMS-Ablage', 'E-Signatur-Rueckmeldung'],
    provider: 'DMS/E-Signatur',
  },
  'privacy-contracts': {
    evidenceTypes: ['AVV/DPA', 'TOM-Nachweis', 'Subprozessorenliste', 'Datenexportnachweis'],
    probeTypes: ['AVV-Pruefung', 'Subprozessorenreview', 'Datenexporttest'],
    provider: 'Anbieterregister',
  },
  'works-council-dsfa': {
    evidenceTypes: ['Betriebsratsstatus', 'DSFA-Vorpruefung', 'Reporting-Freigabe', 'KI-Assistenzfreigabe'],
    probeTypes: ['DSFA-Pruefung', 'Reporting-Zweckpruefung', 'Freigabecheck'],
    provider: 'HR/Datenschutz',
  },
  'retention-legal': {
    evidenceTypes: ['Loeschkonzept', 'Dokumentklassenfreigabe', 'Legal-Freigabe', 'Loeschlauf-Protokoll'],
    probeTypes: ['Retention-Regelpruefung', 'Auskunftsexport', 'Loeschlauf-Stichprobe'],
    provider: 'Legal/HR',
  },
}

const roleProfiles: Array<{ id: RoleFocus; label: string; description: string }> = [
  { id: 'all', label: 'Alle', description: 'Gesamtbild fuer Koordination und Go-live' },
  { id: 'hr', label: 'HR', description: 'Personalprozesse, Akten, Reporting und Vorlagen' },
  { id: 'payroll', label: 'Payroll', description: 'eAU, DATEV, Lohn und Monatsabschluss' },
  { id: 'it', label: 'IT', description: 'SSO, MFA, DMS, technische Tests und Audit' },
  { id: 'privacy', label: 'Datenschutz', description: 'AVV, DSFA, TOMs und Zweckbindung' },
  { id: 'legal', label: 'Legal', description: 'Retention, Dokumentklassen und Vertragsfreigaben' },
  { id: 'management', label: 'Leitung', description: 'Startentscheidung, Blocker und Restrisiken' },
]

const gateRoles: Record<string, RoleFocus[]> = {
  'eau-communication': ['hr', 'payroll', 'privacy'],
  'datev-payroll': ['payroll', 'hr', 'management'],
  'office-sso-connectors': ['it', 'privacy'],
  'documents-esign': ['hr', 'it', 'legal'],
  'privacy-contracts': ['privacy', 'it', 'management'],
  'works-council-dsfa': ['hr', 'privacy', 'management'],
  'retention-legal': ['legal', 'hr', 'privacy', 'management'],
}

function gateMatchesRole(gate: HrmOperationsGate, role: RoleFocus): boolean {
  return role === 'all' || gateRoles[gate.id]?.includes(role) || false
}

function nextAction(gate: HrmOperationsGate): string {
  if (gate.status === 'approved') return 'Kein Sofortbedarf. Beim naechsten Regeltermin erneut pruefen.'
  if (gate.status === 'rejected') return 'Klaeren, warum der Punkt zurueckgewiesen wurde, und einen neuen Nachweis einreichen.'
  if (gate.evidenceCount < 1) return 'Den fehlenden Nachweis als Datei, Link oder Aktenzeichen eintragen.'
  if (!gate.lastProbeStatus || gate.lastProbeStatus === 'failed' || gate.lastProbeStatus === 'not_configured') return 'Den fachlichen oder technischen Test nachtragen.'
  if (gate.status === 'probe_passed' || gate.status === 'evidence_submitted') return 'Die verantwortliche Person soll den Punkt freigeben oder zurueckweisen.'
  return 'Pruefen, welcher Nachweis noch fehlt.'
}

function taskItems(gate: HrmOperationsGate): Array<{ label: string; done: boolean; hint: string }> {
  const probeDone = gate.lastProbeStatus === 'passed' || gate.lastProbeStatus === 'manual'
  return [
    {
      label: 'Nachweis hinterlegen',
      done: gate.evidenceCount > 0,
      hint: gate.evidenceCount > 0 ? `${gate.evidenceCount} Nachweis(e) vorhanden` : 'Vorlage nutzen und DMS-Link oder Aktenzeichen eintragen',
    },
    {
      label: 'Fachlichen Test dokumentieren',
      done: probeDone,
      hint: gate.lastProbeStatus ? `Letzter Test: ${probeLabel[gate.lastProbeStatus] ?? gate.lastProbeStatus}` : 'Testart auswaehlen und Ergebnis speichern',
    },
    {
      label: 'Freigabeentscheidung treffen',
      done: gate.status === 'approved',
      hint: gate.status === 'approved' ? `Freigegeben durch ${gate.approvedBy ?? 'verantwortliche Person'}` : 'Nachweis und Test pruefen, dann freigeben oder zurueckweisen',
    },
  ]
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
  const preset = gatePresets[gate.id] ?? {
    evidenceTypes: [defaultForm.evidenceType],
    probeTypes: [defaultForm.probeType],
    provider: simpleGateTitle(gate),
  }
  const [form, setForm] = useState<GateFormState>({
    ...defaultForm,
    evidenceType: preset.evidenceTypes[0] ?? defaultForm.evidenceType,
    title: `${simpleGateTitle(gate)} Nachweis`,
    provider: preset.provider,
    probeType: preset.probeTypes[0] ?? defaultForm.probeType,
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
  const template = templateByGate[gate.id]

  return (
    <div className="flex flex-col gap-4">
      {template ? (
        <a
          href={`/${template.path}`}
          target="_blank"
          rel="noreferrer"
          className="flex items-center justify-between rounded border border-blue-200 bg-blue-50 px-3 py-2 text-xs font-bold text-blue-800 hover:bg-blue-100"
        >
          <span className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Vorlage oeffnen: {template.label}
          </span>
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      ) : null}

      <div className="rounded border border-gray-200 bg-white p-4 shadow-sm">
        <h4 className="mb-4 border-b pb-2 text-xs font-bold uppercase text-gray-800">1. Nachweis ablegen</h4>
        <div className="space-y-4">
          <div>
            <Label className="mb-1 block text-[10px] font-bold uppercase text-gray-400" htmlFor={`${gate.id}-evidence-type`}>Art des Nachweises</Label>
            <select
              id={`${gate.id}-evidence-type`}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={form.evidenceType}
              onChange={(event) => update('evidenceType', event.target.value)}
            >
              {preset.evidenceTypes.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
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
              <select
                id={`${gate.id}-probe-type`}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={form.probeType}
                onChange={(event) => update('probeType', event.target.value)}
              >
                {preset.probeTypes.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
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

function GateTaskPlan({ gate }: { gate: HrmOperationsGate }): JSX.Element {
  return (
    <div className="rounded border border-gray-200 bg-white p-4 shadow-sm">
      <h4 className="mb-4 flex items-center gap-2 border-b pb-2 text-xs font-bold uppercase text-gray-700">
        <ClipboardCheck className="h-3.5 w-3.5 text-[#005ca5]" />
        Arbeitsplan
      </h4>
      <div className="space-y-3">
        {taskItems(gate).map((item, index) => (
          <div key={item.label} className="flex items-start gap-3">
            <div className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-[11px] font-black ${item.done ? 'border-emerald-500 bg-emerald-50 text-emerald-700' : 'border-gray-300 bg-gray-50 text-gray-500'}`}>
              {item.done ? <Check className="h-3.5 w-3.5" /> : index + 1}
            </div>
            <div className="min-w-0">
              <p className="text-[13px] font-bold text-gray-800">{item.label}</p>
              <p className="text-[12px] leading-relaxed text-gray-500">{item.hint}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function AuditTimeline({ gate }: { gate: HrmOperationsGate }): JSX.Element {
  const entries = [
    gate.latestEvidenceRef ? { label: 'Nachweis hinterlegt', detail: gate.latestEvidenceRef, tone: 'blue' } : null,
    gate.lastProbeStatus ? { label: 'Test dokumentiert', detail: `${probeLabel[gate.lastProbeStatus] ?? gate.lastProbeStatus}${gate.lastProbeAt ? ` am ${formatDate(gate.lastProbeAt)}` : ''}`, tone: gate.lastProbeStatus === 'passed' ? 'emerald' : 'amber' } : null,
    gate.status === 'approved' ? { label: 'Freigegeben', detail: `${gate.approvedBy ?? 'Verantwortliche Person'}${gate.approvedAt ? ` am ${formatDate(gate.approvedAt)}` : ''}`, tone: 'emerald' } : null,
    gate.status === 'rejected' ? { label: 'Zurueckgewiesen', detail: gate.rejectionReason ?? 'Kommentar pruefen', tone: 'red' } : null,
  ].filter(Boolean) as Array<{ label: string; detail: string; tone: 'blue' | 'emerald' | 'amber' | 'red' }>

  const dotClass: Record<string, string> = {
    blue: 'bg-blue-600',
    emerald: 'bg-emerald-600',
    amber: 'bg-amber-500',
    red: 'bg-red-600',
  }

  return (
    <div className="rounded border border-gray-200 bg-white p-4 shadow-sm">
      <h4 className="mb-4 border-b pb-2 text-xs font-bold uppercase text-gray-700">Audit-Zeitleiste</h4>
      {entries.length > 0 ? (
        <div className="space-y-3">
          {entries.map((entry) => (
            <div key={`${entry.label}-${entry.detail}`} className="flex gap-3">
              <span className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${dotClass[entry.tone]}`} />
              <div className="min-w-0">
                <p className="text-[13px] font-bold text-gray-800">{entry.label}</p>
                <p className="break-words text-[12px] text-gray-500">{entry.detail}</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-[13px] text-gray-500">Noch keine Nachweise, Tests oder Entscheidungen protokolliert.</p>
      )}
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
                <GateTaskPlan gate={gate} />
                <AuditTimeline gate={gate} />
              </div>

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
  const [roleFocus, setRoleFocus] = useState<RoleFocus>('all')
  const [expandedGateId, setExpandedGateId] = useState<string | null>(null)
  const visibleGates = useMemo(() => gates.filter((gate) => gateMatchesRole(gate, roleFocus)), [gates, roleFocus])
  const approvedCount = gates.filter((gate) => gate.status === 'approved').length
  const evidenceCount = gates.reduce((sum, gate) => sum + gate.evidenceCount, 0)
  const blockerCount = policyQuery.data?.blockerCount ?? gates.filter((gate) => gate.goLiveBlocking && gate.status !== 'approved').length
  const isGoLiveAllowed = policyQuery.data?.goLiveAllowed ?? blockerCount === 0
  const blockers = policyQuery.data?.blockers ?? gates.filter((gate) => gate.goLiveBlocking && gate.status !== 'approved')
  const selectedRole = roleProfiles.find((profile) => profile.id === roleFocus) ?? roleProfiles[0]

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

        <section className="rounded border border-gray-200 bg-white p-4 shadow-sm">
          <div className="mb-3 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="flex items-center gap-2 text-base font-bold text-gray-900">
                <BriefcaseBusiness className="h-4 w-4 text-[#005ca5]" />
                Rollenfokus
              </h2>
              <p className="text-[12px] text-gray-500">{selectedRole.description}</p>
            </div>
            <span className="text-[11px] font-bold uppercase tracking-wide text-gray-400">
              {visibleGates.length} von {gates.length} Pruefpunkten sichtbar
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {roleProfiles.map((profile) => (
              <button
                key={profile.id}
                type="button"
                onClick={() => {
                  setRoleFocus(profile.id)
                  setExpandedGateId(null)
                }}
                className={`rounded border px-3 py-1.5 text-xs font-bold transition ${roleFocus === profile.id ? 'border-[#005ca5] bg-blue-50 text-[#005ca5]' : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'}`}
                title={profile.description}
              >
                {profile.label}
              </button>
            ))}
          </div>
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
          <div className="grid border-t border-gray-100 bg-gray-50/60 md:grid-cols-3">
            <div className="border-b border-gray-100 p-4 md:border-b-0 md:border-r">
              <p className="text-[10px] font-bold uppercase tracking-wide text-gray-400">Management-Entscheidung</p>
              <p className="mt-1 text-sm font-bold text-gray-800">{isGoLiveAllowed ? 'Freigabe kann vorbereitet werden' : 'Freigabe aktuell nicht moeglich'}</p>
            </div>
            <div className="border-b border-gray-100 p-4 md:border-b-0 md:border-r">
              <p className="text-[10px] font-bold uppercase tracking-wide text-gray-400">Naechster Fokus</p>
              <p className="mt-1 text-sm font-bold text-gray-800">{blockers[0] ? simpleGateTitle(blockers[0]) : 'Regelpruefung terminieren'}</p>
            </div>
            <div className="p-4">
              <p className="text-[10px] font-bold uppercase tracking-wide text-gray-400">Vorlage Entscheidung</p>
              <a href="/docs/hrm-go-live-templates/16_geschaeftsfuehrungsfreigabe.md" target="_blank" rel="noreferrer" className="mt-1 inline-flex items-center gap-1 text-sm font-bold text-[#005ca5] hover:underline">
                Geschaeftsfuehrungsfreigabe oeffnen
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
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
          {visibleGates.map((gate) => (
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
