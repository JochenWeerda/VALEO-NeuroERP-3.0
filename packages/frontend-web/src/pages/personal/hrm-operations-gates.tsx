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
  evidenceType: 'approval_document',
  title: '',
  artifactRef: '',
  submittedBy: '',
  provider: '',
  probeType: 'readiness_check',
  probeResult: 'passed',
  performedBy: '',
  decidedBy: '',
  decisionReason: '',
}

const statusLabel: Record<string, string> = {
  external_evidence_required: 'Evidenz offen',
  evidence_submitted: 'Evidenz eingereicht',
  probe_passed: 'Probe bestanden',
  approved: 'Freigegeben',
  rejected: 'Abgelehnt',
  external_gates_defined: 'Katalog',
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
          push('Evidence gespeichert.')
          update('artifactRef', '')
        },
        onError: (error) => push(getAxiosErrorMessage(error)),
      },
    )
  }

  const recordProbe = (): void => {
    if (!form.provider.trim() || !form.probeType.trim() || !form.performedBy.trim()) {
      push('Bitte Provider, Probe-Typ und Pruefer angeben.')
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
        onSuccess: () => push('Probe gespeichert.'),
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
        onSuccess: () => push(decision === 'approve' ? 'Gate freigegeben.' : 'Gate abgelehnt.'),
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
          Evidence
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-evidence-type`}>Typ</Label>
          <Input id={`${gate.id}-evidence-type`} value={form.evidenceType} onChange={(event) => update('evidenceType', event.target.value)} />
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-title`}>Titel</Label>
          <Input id={`${gate.id}-title`} value={form.title} onChange={(event) => update('title', event.target.value)} />
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-artifact`}>Artefakt-Referenz</Label>
          <Input id={`${gate.id}-artifact`} value={form.artifactRef} onChange={(event) => update('artifactRef', event.target.value)} placeholder="dms://hrm/..." />
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-submitted-by`}>Eingereicht von</Label>
          <Input id={`${gate.id}-submitted-by`} value={form.submittedBy} onChange={(event) => update('submittedBy', event.target.value)} />
        </div>
        <Button onClick={createEvidence} disabled={busy} className="w-full gap-2">
          <FileCheck2 className="h-4 w-4" />
          Evidence speichern
        </Button>
      </div>

      <div className="space-y-3 rounded-md border p-3">
        <div className="flex items-center gap-2 text-sm font-medium">
          <PlugZap className="h-4 w-4" />
          Probe
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-provider`}>Provider</Label>
          <Input id={`${gate.id}-provider`} value={form.provider} onChange={(event) => update('provider', event.target.value)} />
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-probe-type`}>Probe-Typ</Label>
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
          <Label htmlFor={`${gate.id}-performed-by`}>Geprueft von</Label>
          <Input id={`${gate.id}-performed-by`} value={form.performedBy} onChange={(event) => update('performedBy', event.target.value)} />
        </div>
        <Button onClick={recordProbe} disabled={busy} className="w-full gap-2" variant="outline">
          <PlugZap className="h-4 w-4" />
          Probe speichern
        </Button>
      </div>

      <div className="space-y-3 rounded-md border p-3">
        <div className="flex items-center gap-2 text-sm font-medium">
          <ShieldCheck className="h-4 w-4" />
          Entscheidung
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-decided-by`}>Entschieden von</Label>
          <Input id={`${gate.id}-decided-by`} value={form.decidedBy} onChange={(event) => update('decidedBy', event.target.value)} />
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${gate.id}-reason`}>Grund</Label>
          <Textarea id={`${gate.id}-reason`} value={form.decisionReason} onChange={(event) => update('decisionReason', event.target.value)} rows={5} />
        </div>
        <div className="grid gap-2 sm:grid-cols-2">
          <Button onClick={() => decide('approve')} disabled={busy || gate.evidenceCount < 1} className="gap-2">
            <CheckCircle2 className="h-4 w-4" />
            Freigeben
          </Button>
          <Button onClick={() => decide('reject')} disabled={busy} variant="destructive" className="gap-2">
            <XCircle className="h-4 w-4" />
            Ablehnen
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
            <CardTitle className="text-base">{gate.title}</CardTitle>
            <div className="flex flex-wrap gap-2">
              <Badge variant={statusVariant(gate.status)}>{statusLabel[gate.status] ?? gate.status}</Badge>
              {gate.goLiveBlocking ? <Badge variant="destructive">Go-live Blocker</Badge> : <Badge variant="outline">Nicht blockierend</Badge>}
              <Badge variant="outline">{gate.ownerRole}</Badge>
            </div>
          </div>
          <div className="grid min-w-56 gap-1 text-sm text-muted-foreground">
            <span>Evidence: {gate.evidenceCount}</span>
            <span>Letzte Probe: {gate.lastProbeStatus ?? '-'}</span>
            <span>Freigabe: {gate.approvedBy ? `${gate.approvedBy}, ${formatDate(gate.approvedAt)}` : '-'}</span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 lg:grid-cols-3">
          <div>
            <h3 className="mb-2 text-sm font-medium">Evidenzpflichten</h3>
            <ul className="space-y-1 text-sm text-muted-foreground">
              {gate.evidenceRequired.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="mb-2 text-sm font-medium">Abnahme</h3>
            <ul className="space-y-1 text-sm text-muted-foreground">
              {gate.acceptanceCriteria.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="mb-2 text-sm font-medium">Audit</h3>
            <div className="flex flex-wrap gap-2">
              {gate.auditTrail.map((item) => (
                <Badge key={item} variant="outline">{item}</Badge>
              ))}
            </div>
            {gate.latestEvidenceRef ? <p className="mt-3 break-all text-sm text-muted-foreground">{gate.latestEvidenceRef}</p> : null}
            {gate.rejectionReason ? <p className="mt-3 text-sm text-red-700">{gate.rejectionReason}</p> : null}
          </div>
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
          <h1 className="text-3xl font-bold">HRM-Freigaben</h1>
          <p className="text-muted-foreground">Betriebsfreigaben, Evidenz und Go-live-Blocker</p>
        </div>
        <Badge variant={policyQuery.data?.goLiveAllowed ? 'default' : 'destructive'} className="w-fit gap-2 px-3 py-2">
          {policyQuery.data?.goLiveAllowed ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
          {policyQuery.data?.goLiveAllowed ? 'Go-live freigegeben' : 'Go-live blockiert'}
        </Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gates</CardTitle>
          </CardHeader>
          <CardContent><span className="text-2xl font-bold">{gates.length}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Freigegeben</CardTitle>
          </CardHeader>
          <CardContent><span className="text-2xl font-bold text-green-700">{approvedCount}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Blocker</CardTitle>
          </CardHeader>
          <CardContent><span className="text-2xl font-bold text-red-700">{blockerCount}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Evidence</CardTitle>
          </CardHeader>
          <CardContent><span className="text-2xl font-bold">{evidenceCount}</span></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Go-live Policy</CardTitle>
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
