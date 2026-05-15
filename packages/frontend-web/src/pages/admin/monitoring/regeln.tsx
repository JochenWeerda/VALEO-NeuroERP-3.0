import { useMemo, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'
import {
  useCreateMonitoringChannel,
  useCreateMonitoringRule,
  useCreateSchedulerJob,
  useDeleteMonitoringChannel,
  useDeleteMonitoringRule,
  useDeleteSchedulerJob,
  useMonitoringChannels,
  useMonitoringRules,
  useSchedulerJobs,
} from '@/lib/api/admin'
import { toast } from '@/hooks/use-toast'

function splitCsv(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

type MonitoringRulesRole = 'admin' | 'betrieb' | 'security' | 'leitung'

const monitoringRulesRoles = [
  {
    id: 'admin',
    label: 'Admin',
    description: 'Regeln, Alarmkanaele und Scheduler-Jobs technisch pflegen.',
  },
  {
    id: 'betrieb',
    label: 'Betrieb',
    description: 'Regeln so steuern, dass Stoerungen rechtzeitig und passend gemeldet werden.',
  },
  {
    id: 'security',
    label: 'Security',
    description: 'Kritische Regeln und Eskalationskanaele auf Nachweis und Risiko pruefen.',
  },
  {
    id: 'leitung',
    label: 'Leitung',
    description: 'Betriebsbereitschaft der Ueberwachung und offene Luecken bewerten.',
  },
] satisfies Array<{ id: MonitoringRulesRole; label: string; description: string }>

export default function MonitoringRegelnPage(): JSX.Element {
  const { data: rules = [] } = useMonitoringRules()
  const { data: channels = [] } = useMonitoringChannels()
  const { data: jobs = [] } = useSchedulerJobs()
  const [roleFocus, setRoleFocus] = useState<MonitoringRulesRole>('admin')

  const createRule = useCreateMonitoringRule()
  const deleteRule = useDeleteMonitoringRule()
  const createChannel = useCreateMonitoringChannel()
  const deleteChannel = useDeleteMonitoringChannel()
  const createJob = useCreateSchedulerJob()
  const deleteJob = useDeleteSchedulerJob()

  const [ruleCode, setRuleCode] = useState('')
  const [ruleName, setRuleName] = useState('')
  const [ruleMetric, setRuleMetric] = useState('')
  const [ruleLevel, setRuleLevel] = useState<'critical' | 'warning' | 'info'>('warning')
  const [ruleThreshold, setRuleThreshold] = useState('')
  const [ruleOperator, setRuleOperator] = useState<'gt' | 'gte' | 'lt' | 'lte' | 'eq' | 'neq'>('gte')
  const [ruleChannels, setRuleChannels] = useState('')

  const [channelCode, setChannelCode] = useState('')
  const [channelName, setChannelName] = useState('')
  const [channelType, setChannelType] = useState<'email' | 'sms' | 'webhook' | 'chatops'>('email')
  const [channelTarget, setChannelTarget] = useState('')

  const [jobCode, setJobCode] = useState('')
  const [jobName, setJobName] = useState('')
  const [jobCron, setJobCron] = useState('0 2 * * *')
  const [jobProcess, setJobProcess] = useState('nightly-report')
  const [jobChannels, setJobChannels] = useState('')

  const channelCodeList = useMemo(() => channels.map((item) => item.code), [channels])
  const hasRule = rules.length > 0
  const hasChannel = channels.length > 0
  const hasJob = jobs.length > 0
  const monitoringReady = hasRule && hasChannel && hasJob
  const rulesAction = !hasRule
    ? 'Mindestens eine Monitoring-Regel anlegen, damit relevante Betriebsereignisse erkannt werden.'
    : !hasChannel
      ? 'Alarmkanal anlegen und in Regeln oder Jobs verwenden.'
      : !hasJob
        ? 'Scheduler-Job anlegen, wenn wiederkehrende Pruefungen oder Berichte automatisch laufen sollen.'
        : 'Regeln, Kanaele und Jobs sind vorhanden. Naechste Aenderung mit Grund und Nachweis dokumentieren.'

  const onCreateRule = async () => {
    if (!ruleCode || !ruleName || !ruleMetric) {
      toast({ title: 'Pflichtfelder fehlen', description: 'Code, Name und Metric sind erforderlich.', variant: 'destructive' })
      return
    }
    try {
      await createRule.mutateAsync({
        code: ruleCode,
        name: ruleName,
        metric: ruleMetric,
        level: ruleLevel,
        threshold: ruleThreshold ? Number(ruleThreshold) : null,
        operator: ruleOperator,
        active: true,
        escalation_minutes: 30,
        channel_ids: splitCsv(ruleChannels),
      })
      setRuleCode('')
      setRuleName('')
      setRuleMetric('')
      setRuleThreshold('')
      setRuleChannels('')
      toast({ title: 'Monitoring-Regel angelegt' })
    } catch (error) {
      toast({ title: 'Anlegen fehlgeschlagen', description: String(error), variant: 'destructive' })
    }
  }

  const onCreateChannel = async () => {
    if (!channelCode || !channelName || !channelTarget) {
      toast({ title: 'Pflichtfelder fehlen', description: 'Code, Name und Ziel sind erforderlich.', variant: 'destructive' })
      return
    }
    try {
      await createChannel.mutateAsync({
        code: channelCode,
        name: channelName,
        channel_type: channelType,
        target: channelTarget,
        active: true,
      })
      setChannelCode('')
      setChannelName('')
      setChannelTarget('')
      toast({ title: 'Alarmkanal angelegt' })
    } catch (error) {
      toast({ title: 'Anlegen fehlgeschlagen', description: String(error), variant: 'destructive' })
    }
  }

  const onCreateJob = async () => {
    if (!jobCode || !jobName || !jobCron || !jobProcess) {
      toast({ title: 'Pflichtfelder fehlen', description: 'Code, Name, Cron und Prozess sind erforderlich.', variant: 'destructive' })
      return
    }
    try {
      await createJob.mutateAsync({
        code: jobCode,
        name: jobName,
        cron: jobCron,
        process: jobProcess,
        active: true,
        retry_max: 3,
        timeout_seconds: 300,
        channel_ids: splitCsv(jobChannels),
      })
      setJobCode('')
      setJobName('')
      setJobCron('0 2 * * *')
      setJobProcess('nightly-report')
      setJobChannels('')
      toast({ title: 'Scheduler-Job angelegt' })
    } catch (error) {
      toast({ title: 'Anlegen fehlgeschlagen', description: String(error), variant: 'destructive' })
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Monitoring-Regeln</h1>
        <p className="text-muted-foreground">Alert-Regeln, Alarmkanaele und Scheduler-Jobs nachvollziehbar administrieren.</p>
      </div>

      <RoleFocusBar
        roles={monitoringRulesRoles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={rules.length + channels.length + jobs.length}
        totalCount={rules.length + channels.length + jobs.length}
        title="Arbeitsrolle fuer Monitoring-Regeln"
      />

      <ManagementDecisionPanel
        decision={{
          allowed: monitoringReady,
          allowedLabel: 'Ueberwachung bereit',
          blockedLabel: 'Ueberwachung unvollstaendig',
          summary: monitoringReady
            ? 'Monitoring-Regeln, Alarmkanaele und Scheduler-Jobs sind vorhanden. Die Ueberwachung kann technisch betrieben und fachlich nachgewiesen werden.'
            : 'Fuer eine betriebsfaehige Ueberwachung muessen mindestens Regeln, Alarmkanaele und wiederkehrende Jobs vorhanden sein. Fehlende Bausteine verhindern verlaessliche Eskalation.',
          blockerCount: [hasRule, hasChannel, hasJob].filter((value) => !value).length,
          nextFocus: rulesAction,
          template: {
            label: 'Monitoring-Regel-Freigabe',
            href: '/docs/monitoring/monitoring-regel-freigabe.md',
          },
        }}
      />

      <div className="grid gap-4 xl:grid-cols-[1.15fr_1fr_1fr]">
        <OperationalTaskPlan
          title="Regelbetriebsplan"
          items={[
            {
              label: 'Regel definieren',
              done: hasRule,
              hint: hasRule ? `${rules.length} Regel(n) vorhanden.` : 'Eine Metrik, ein Grenzwert und ein Level werden benoetigt.',
            },
            {
              label: 'Alarmkanal verbinden',
              done: hasChannel,
              hint: hasChannel ? `${channels.length} Kanal/Kanaele vorhanden.` : 'Ohne Kanal erreicht ein Alert keinen Verantwortlichen.',
            },
            {
              label: 'Wiederkehrende Pruefung planen',
              done: hasJob,
              hint: hasJob ? `${jobs.length} Scheduler-Job(s) vorhanden.` : 'Jobs machen Pruefungen und Berichte wiederholbar.',
            },
            {
              label: 'Aenderung nachweisen',
              done: monitoringReady,
              hint: 'Regelaenderungen sollten mit Anlass, Owner und Wirkung dokumentiert werden.',
            },
          ]}
        />
        <NextActionPanel action={rulesAction} tone={monitoringReady ? 'emerald' : 'amber'} />
        <div className="space-y-3">
          <EvidenceTemplateLink
            link={{
              label: 'Monitoring-Aenderungsnachweis',
              href: '/docs/monitoring/monitoring-aenderungsnachweis.md',
            }}
          />
          <CrudCapabilityChecklist
            capabilities={[
              { key: 'create', label: 'Anlegen', available: true, hint: 'Regeln, Kanaele und Jobs koennen angelegt werden.' },
              { key: 'read', label: 'Lesen', available: true, hint: 'Vorhandene Regeln, Kanaele und Jobs sind sichtbar.' },
              { key: 'delete', label: 'Loeschen', available: true, hint: 'Nicht mehr benoetigte Eintraege koennen entfernt werden.' },
              { key: 'evidence', label: 'Nachweis', available: monitoringReady, hint: 'Bei vollstaendiger Ueberwachung ist ein Freigabenachweis sinnvoll.' },
            ]}
          />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Alert-Regeln</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Label htmlFor="rule-code">Code</Label>
            <Input id="rule-code" value={ruleCode} onChange={(e) => setRuleCode(e.target.value)} placeholder="stock-critical" />
            <Label htmlFor="rule-name">Name</Label>
            <Input id="rule-name" value={ruleName} onChange={(e) => setRuleName(e.target.value)} placeholder="Lagerbestand kritisch" />
            <Label htmlFor="rule-metric">Metric</Label>
            <Input id="rule-metric" value={ruleMetric} onChange={(e) => setRuleMetric(e.target.value)} placeholder="inventory.low_stock_count" />
            <div className="grid grid-cols-2 gap-2">
              <select
                aria-label="Alert-Level"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={ruleLevel}
                onChange={(e) => setRuleLevel(e.target.value as 'critical' | 'warning' | 'info')}
              >
                <option value="critical">Kritisch</option>
                <option value="warning">Warnung</option>
                <option value="info">Info</option>
              </select>
              <select
                aria-label="Vergleich"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={ruleOperator}
                onChange={(e) => setRuleOperator(e.target.value as 'gt' | 'gte' | 'lt' | 'lte' | 'eq' | 'neq')}
              >
                <option value="gt">groesser als</option>
                <option value="gte">groesser/gleich</option>
                <option value="lt">kleiner als</option>
                <option value="lte">kleiner/gleich</option>
                <option value="eq">gleich</option>
                <option value="neq">ungleich</option>
              </select>
            </div>
            <Input value={ruleThreshold} onChange={(e) => setRuleThreshold(e.target.value)} placeholder="Threshold (z.B. 1)" />
            <Input value={ruleChannels} onChange={(e) => setRuleChannels(e.target.value)} placeholder="Channel-IDs CSV" />
            <Button className="w-full" onClick={onCreateRule} disabled={createRule.isPending}>
              Regel anlegen
            </Button>
            <div className="space-y-2 pt-2">
              {rules.map((item) => (
                <div key={item.id} className="flex items-center justify-between rounded border p-2">
                  <div>
                    <div className="font-medium">{item.name}</div>
                    <div className="text-xs text-muted-foreground">{item.code} · {item.metric}</div>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => deleteRule.mutate(item.id)}>Loeschen</Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Alarmkanaele</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input value={channelCode} onChange={(e) => setChannelCode(e.target.value)} placeholder="ops-email" />
            <Input value={channelName} onChange={(e) => setChannelName(e.target.value)} placeholder="Ops E-Mail" />
            <select
              aria-label="Kanaltyp"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={channelType}
              onChange={(e) => setChannelType(e.target.value as 'email' | 'sms' | 'webhook' | 'chatops')}
            >
              <option value="email">E-Mail</option>
              <option value="sms">SMS</option>
              <option value="webhook">Webhook</option>
              <option value="chatops">ChatOps</option>
            </select>
            <Input value={channelTarget} onChange={(e) => setChannelTarget(e.target.value)} placeholder="ops@example.org / webhook-url" />
            <Button className="w-full" onClick={onCreateChannel} disabled={createChannel.isPending}>
              Kanal anlegen
            </Button>
            <div className="space-y-2 pt-2">
              {channels.map((item) => (
                <div key={item.id} className="flex items-center justify-between rounded border p-2">
                  <div>
                    <div className="font-medium">{item.name}</div>
                    <div className="text-xs text-muted-foreground">{item.code} · {item.channel_type}</div>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => deleteChannel.mutate(item.id)}>Loeschen</Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Scheduler-Jobs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input value={jobCode} onChange={(e) => setJobCode(e.target.value)} placeholder="nightly-reports" />
            <Input value={jobName} onChange={(e) => setJobName(e.target.value)} placeholder="Nightly Reports" />
            <Input value={jobCron} onChange={(e) => setJobCron(e.target.value)} placeholder="0 2 * * *" />
            <Input value={jobProcess} onChange={(e) => setJobProcess(e.target.value)} placeholder="nightly-report" />
            <Input value={jobChannels} onChange={(e) => setJobChannels(e.target.value)} placeholder={`Kanaele CSV (${channelCodeList.join(', ')})`} />
            <Button className="w-full" onClick={onCreateJob} disabled={createJob.isPending}>
              Job anlegen
            </Button>
            <div className="space-y-2 pt-2">
              {jobs.map((item) => (
                <div key={item.id} className="flex items-center justify-between rounded border p-2">
                  <div>
                    <div className="font-medium">{item.name}</div>
                    <div className="text-xs text-muted-foreground">{item.code} · {item.cron}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{item.active ? 'aktiv' : 'inaktiv'}</Badge>
                    <Button variant="ghost" size="sm" onClick={() => deleteJob.mutate(item.id)}>Loeschen</Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
