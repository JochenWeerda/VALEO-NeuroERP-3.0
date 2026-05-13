import { useMemo, useState } from 'react'
import { AlertTriangle, CheckCircle2, FileCheck2, PlugZap, ShieldCheck, XCircle } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
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
  external_evidence_required: 'Nachweis fehlt',
  evidence_submitted: 'Nachweis liegt vor',
  probe_passed: 'Test bestanden',
  approved: 'Erledigt',
  rejected: 'Zurueckgewiesen',
  external_gates_defined: 'Vorbereitet',
}

function statusVariant(status: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  if (status === 'approved') return 'default'
  if (status === 'rejected') return 'destructive'
  if (status === 'probe_passed' || status === 'evidence_submitted') return 'secondary'
  return 'outline'
}

function formatDate(value?: string | null): string {
  if (!value) return '-'
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString('de-DE')
}

function nextAction(gate: HrmOperationsGate): string {
  if (gate.status === 'approved') return 'Kein Sofortbedarf. Beim naechsten Regeltermin erneut pruefen.'
  if (gate.status === 'rejected') return 'Klaeren, warum der Punkt zurueckgewiesen wurde, und einen neuen Nachweis einreichen.'
  if (gate.evidenceCount < 1) return 'Den fehlenden Nachweis oder die Freigabe als Datei, Link oder Aktenzeichen eintragen.'
  if (!gate.lastProbeStatus || gate.lastProbeStatus === 'failed' || gate.lastProbeStatus === 'not_configured') return 'Den fachlichen oder technischen Test nachtragen.'
  if (gate.status === 'probe_passed' || gate.status === 'evidence_submitted') return 'Die verantwortliche Person soll den Punkt freigeben oder zurueckweisen.'
  return 'Pruefen, welcher Nachweis noch fehlt.'
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

function GateActions({ gate }: { gate: HrmOperationsGate }): JSX.Element {
  const { push } = useToast()
  const evidenceMutation = useCreateHrmOperationsGateEvidence(gate.id)
  const probeMutation = useRecordHrmOperationsGateProbe(gate.id)
  const decisionMutation = useDecideHrmOperationsGate(gate.id)
  const [form, setForm] = useState<GateFormState>({
    ...defaultForm,
    title: `${gate.title} Nachweis`,
    provider: gate.title.split(' ')[0] || gate.id,
  })

  const update = <K extends keyof GateFormState>(key: K, value: GateFormState[K]): void => {
    setForm((current) => ({ ...current, [key]: value }))
  }

  const createEvidence = (): void => {
    if (!form.title.trim() || !form.artifactRef.trim() || !form.submittedBy.trim()) {
      push('Bitte Titel, Artefakt-Referenz und Einreicher angeben.')
      return
    }
    evidenceMutation.mutate(
      {
        evidenceType: form.evidenceType.trim(),
        title: form.title.trim(),
        artifactRef: form.artifactRef.trim(),
        submittedBy: form.submittedBy.trim(),
        metadata: { gateTitle: gate.title },
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
        details: { gateTitle: gate.title },
      },
      {
        onSuccess: () => push('Test gespeichert.'),
        onError: (error) => push(getAxiosErrorMessage(error)),
      },
    )
  }

  const decide = (decision: 'approve' | 'reject'): void => {
    if (!form.decidedBy.trim()) {
      push('Bitte Entscheider angeben.')
      return
    }
    if (decision === 'reject' && !form.decisionReason.trim()) {
      push('Bitte Ablehnungsgrund angeben.')
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
    <div className="grid gap-4 lg:grid-cols-3">
      <div className="space-y-3 rounded-md border p-3">
        <div className="flex items-center gap-2 text-sm font-medium">
          <FileCheck2 className="h-4 w-4" />
          Nachweis ablegen
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-evidence-type`}>Art des Nachweises</Label>
          <Input id={`${gate.id}-evidence-type`} value={form.evidenceType} onChange={(event) => update('evidenceType', event.target.value)} />
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-title`}>Titel</Label>
          <Input id={`${gate.id}-title`} value={form.title} onChange={(event) => update('title', event.target.value)} />
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-artifact`}>Ablageort, Link oder Aktenzeichen</Label>
          <Input id={`${gate.id}-artifact`} value={form.artifactRef} onChange={(event) => update('artifactRef', event.target.value)} placeholder="dms://hrm/..." />
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-submitted-by`}>Eingetragen von</Label>
          <Input id={`${gate.id}-submitted-by`} value={form.submittedBy} onChange={(event) => update('submittedBy', event.target.value)} />
        </div>
        <Button onClick={createEvidence} disabled={busy} className="w-full gap-2">
          <FileCheck2 className="h-4 w-4" />
          Nachweis speichern
        </Button>
      </div>

      <div className="space-y-3 rounded-md border p-3">
        <div className="flex items-center gap-2 text-sm font-medium">
          <PlugZap className="h-4 w-4" />
          Test eintragen
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-provider`}>System oder Anbieter</Label>
          <Input id={`${gate.id}-provider`} value={form.provider} onChange={(event) => update('provider', event.target.value)} />
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-probe-type`}>Was wurde geprueft?</Label>
          <Input id={`${gate.id}-probe-type`} value={form.probeType} onChange={(event) => update('probeType', event.target.value)} />
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-probe-result`}>Ergebnis</Label>
          <select
            id={`${gate.id}-probe-result`}
            className="w-full rounded-md border border-input bg-background px-3 py-2"
            value={form.probeResult}
            onChange={(event) => update('probeResult', event.target.value as GateFormState['probeResult'])}
          >
            <option value="passed">Bestanden</option>
            <option value="failed">Fehlgeschlagen</option>
            <option value="manual">Manuell geprueft</option>
            <option value="not_configured">Nicht konfiguriert</option>
          </select>
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-performed-by`}>Getestet von</Label>
          <Input id={`${gate.id}-performed-by`} value={form.performedBy} onChange={(event) => update('performedBy', event.target.value)} />
        </div>
        <Button onClick={recordProbe} disabled={busy} className="w-full gap-2" variant="outline">
          <PlugZap className="h-4 w-4" />
          Test speichern
        </Button>
      </div>

      <div className="space-y-3 rounded-md border p-3">
        <div className="flex items-center gap-2 text-sm font-medium">
          <ShieldCheck className="h-4 w-4" />
          Freigabe
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-decided-by`}>Freigegeben oder zurueckgewiesen von</Label>
          <Input id={`${gate.id}-decided-by`} value={form.decidedBy} onChange={(event) => update('decidedBy', event.target.value)} />
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-reason`}>Kommentar</Label>
          <Textarea id={`${gate.id}-reason`} value={form.decisionReason} onChange={(event) => update('decisionReason', event.target.value)} rows={5} />
        </div>
        <div className="grid gap-2 sm:grid-cols-2">
          <Button onClick={() => decide('approve')} disabled={busy || gate.evidenceCount < 1} className="gap-2">
            <CheckCircle2 className="h-4 w-4" />
            Als erledigt freigeben
          </Button>
          <Button onClick={() => decide('reject')} disabled={busy} variant="destructive" className="gap-2">
            <XCircle className="h-4 w-4" />
            Zurueckweisen
          </Button>
        </div>
      </div>
    </div>
  )
}

function GatePanel({ gate }: { gate: HrmOperationsGate }): JSX.Element {
  return (
    <Card>
      <CardHeader className="space-y-3">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div className="space-y-1">
            <CardTitle className="text-base">{simpleGateTitle(gate)}</CardTitle>
            <p className="max-w-3xl text-sm text-muted-foreground">{gatePurpose(gate)}</p>
            <div className="flex flex-wrap gap-2">
              <Badge variant={statusVariant(gate.status)}>{statusLabel[gate.status] ?? gate.status}</Badge>
              {gate.goLiveBlocking ? <Badge variant="destructive">Stoppt Produktivstart</Badge> : <Badge variant="outline">Hinweis</Badge>}
              <Badge variant="outline">Zustaendig: {gate.ownerRole}</Badge>
            </div>
          </div>
          <div className="grid min-w-56 gap-1 text-sm text-muted-foreground">
            <span>Nachweise: {gate.evidenceCount}</span>
            <span>Letzter Test: {gate.lastProbeStatus ?? '-'}</span>
            <span>Freigabe: {gate.approvedBy ? `${gate.approvedBy}, ${formatDate(gate.approvedAt)}` : '-'}</span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 lg:grid-cols-3">
          <div>
            <h3 className="mb-2 text-sm font-medium">Was muss vorliegen?</h3>
            <ul className="space-y-1 text-sm text-muted-foreground">
              {gate.evidenceRequired.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="mb-2 text-sm font-medium">Wann ist es erledigt?</h3>
            <ul className="space-y-1 text-sm text-muted-foreground">
              {gate.acceptanceCriteria.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="mb-2 text-sm font-medium">Was wird protokolliert?</h3>
            <div className="flex flex-wrap gap-2">
              {gate.auditTrail.map((item) => (
                <Badge key={item} variant="outline">{item}</Badge>
              ))}
            </div>
            {gate.latestEvidenceRef ? <p className="mt-3 break-all text-sm text-muted-foreground">{gate.latestEvidenceRef}</p> : null}
            {gate.rejectionReason ? <p className="mt-3 text-sm text-red-700">{gate.rejectionReason}</p> : null}
          </div>
        </div>
        <div className="rounded-md border border-dashed p-3">
          <h3 className="text-sm font-medium">Naechste Aktion</h3>
          <p className="mt-1 text-sm text-muted-foreground">{nextAction(gate)}</p>
        </div>
        <GateActions gate={gate} />
      </CardContent>
    </Card>
  )
}

export default function HrmOperationsGatesPage(): JSX.Element {
  const gatesQuery = useHrmOperationsGates()
  const policyQuery = useHrmOperationsGoLivePolicy()
  const gates = useMemo(() => gatesQuery.data?.gates ?? [], [gatesQuery.data?.gates])
  const approvedCount = gates.filter((gate) => gate.status === 'approved').length
  const evidenceCount = gates.reduce((sum, gate) => sum + gate.evidenceCount, 0)
  const blockerCount = policyQuery.data?.blockerCount ?? gates.filter((gate) => gate.goLiveBlocking && gate.status !== 'approved').length

  if (gatesQuery.isLoading && gates.length === 0) {
    return (
      <div className="space-y-4 p-3 md:p-6">
        <Skeleton className="h-10 w-80" />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((item) => <Skeleton key={item} className="h-24" />)}
        </div>
        <Skeleton className="h-96" />
      </div>
    )
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold">HR-Freigaben vor Start</h1>
          <p className="text-muted-foreground">Was vor dem Produktivstart der Personalprozesse noch fehlt</p>
        </div>
        <Badge variant={policyQuery.data?.goLiveAllowed ? 'default' : 'destructive'} className="w-fit gap-2 px-3 py-2">
          {policyQuery.data?.goLiveAllowed ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
          {policyQuery.data?.goLiveAllowed ? 'Produktivstart erlaubt' : 'Produktivstart gestoppt'}
        </Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pruefpunkte</CardTitle>
          </CardHeader>
          <CardContent><span className="text-2xl font-bold">{gates.length}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Erledigt</CardTitle>
          </CardHeader>
          <CardContent><span className="text-2xl font-bold text-green-700">{approvedCount}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Stopper</CardTitle>
          </CardHeader>
          <CardContent><span className="text-2xl font-bold text-red-700">{blockerCount}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Nachweise</CardTitle>
          </CardHeader>
          <CardContent><span className="text-2xl font-bold">{evidenceCount}</span></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Darf HRM produktiv starten?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-muted-foreground">{policyQuery.data?.summary ?? gatesQuery.data?.summary ?? '-'}</p>
          <div className="flex flex-wrap gap-2">
            {(policyQuery.data?.blockers ?? []).map((gate) => (
              <Badge key={gate.id} variant="outline">{gate.title}</Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {gates.map((gate) => <GatePanel key={gate.id} gate={gate} />)}
      </div>
    </div>
  )
}
