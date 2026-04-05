import { useEffect, useMemo, useState } from 'react'
import {
  Building2,
  ArrowLeftRight,
  Bell,
  BookOpen,
  Calculator,
  Calendar,
  ChevronRight,
  Database,
  FileText,
  Landmark,
  Package,
  Plus,
  Receipt,
  Search,
  Settings,
  ShieldCheck,
  ShoppingCart,
  Sparkles,
  Truck,
  UserCircle2,
  Wallet,
  Warehouse,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { PageSection, PageSurface } from '@/components/patterns/PageSurface'
import { AgentProcessPanel } from '@/components/agent'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  fetchFlowSpineWorkspace,
  getFlowSpineFetchErrorMessage,
  getFlowSpineWorkspaceQueryKey,
  useCreateFlowSpineInstance,
  useExecuteAgentAction,
  useExecuteFlowSpineAction,
  type FlowSpineAction,
  type FlowSpineNode,
} from '@/lib/api/flow-spines'
import { toast } from '@/hooks/use-toast'
import i18n from '@/i18n/config'
import { cn } from '@/lib/utils'
import { useQuery } from '@tanstack/react-query'

const ICONS = {
  ArrowLeftRight,
  BookOpen,
  Calculator,
  Calendar,
  Database,
  FileText,
  Landmark,
  Package,
  Receipt,
  Search,
  ShieldCheck,
  ShoppingCart,
  Sparkles,
  Truck,
  UserCircle2,
  Wallet,
  Warehouse,
  Building2,
} as const

interface FlowSpineWorkspaceProps {
  processKey: string
  instanceId?: string
}

type ProcessEntryMode = {
  value: string
  description: string
}

type ProcessStartConfig = {
  buttonLabel: string
  dialogTitle: string
  dialogDescription: string
  partnerLabel: string
  subjectLabel: string
  labelLabel: string
  labelPlaceholder: string
  submitLabel: string
  explanation: string
  entryModes: ProcessEntryMode[]
  buildHref: (created: {
    instance_id: string
    case_number: string
    label: string
    entry_mode?: string
    customer_name?: string
    partner_name?: string
    subject?: string
  }) => string
}

const PROCESS_START_CONFIGS: Record<string, ProcessStartConfig> = {
  'order-to-cash': {
    buttonLabel: 'Neuer Vorgang',
    dialogTitle: 'Neuen Vertriebsvorgang starten',
    dialogDescription: 'Zuerst Vorgang anlegen, dann den eigentlichen Auftrag in der Standardmaske erfassen.',
    partnerLabel: 'Kunde oder Interessent',
    subjectLabel: 'Vorgang / Thema',
    labelLabel: 'Interne Bezeichnung (optional)',
    labelPlaceholder: 'z.B. Fruehjahrsaktion Nord / Schnellauftrag',
    submitLabel: 'Vorgang anlegen',
    explanation: 'Zuerst entsteht ein Vorgang mit eigener Vorgangsnummer. Die eigentliche Auftragsnummer wird erst beim Speichern des Belegs im Backend aus dem Nummernkreis vergeben.',
    entryModes: [
      { value: 'Direktauftrag', description: 'Sofort in die Auftragserfassung wechseln.' },
      { value: 'Kundenanfrage', description: 'Vorgang anlegen und Daten schrittweise erfassen.' },
      { value: 'Angebot', description: 'Bestehendes Angebot als Ausgangspunkt nutzen.' },
    ],
    buildHref: (created) => {
      const query = new URLSearchParams({
        workflowProcess: 'order-to-cash',
        workflowInstanceId: created.instance_id,
        workflowCase: created.case_number,
        workflowLabel: created.label,
        entryMode: created.entry_mode ?? 'Direktauftrag',
      })
      if (created.customer_name || created.partner_name) query.set('customerName', created.customer_name ?? created.partner_name ?? '')
      if (created.subject) query.set('subject', created.subject)
      return `/sales/order-editor?${query.toString()}`
    },
  },
  'procure-to-pay': {
    buttonLabel: 'Neuen Beschaffungsvorgang starten',
    dialogTitle: 'Neue Beschaffung starten',
    dialogDescription: 'Bedarf oder Lieferantenbezug erfassen und dann in die Bestellmaske uebergeben.',
    partnerLabel: 'Lieferant / Partner',
    subjectLabel: 'Bedarf / Thema',
    labelLabel: 'Interne Referenz (optional)',
    labelPlaceholder: 'z.B. Saisonbedarf Nord / Rahmenabruf',
    submitLabel: 'Beschaffungsvorgang anlegen',
    explanation: 'Im Flow entsteht zuerst der Beschaffungsvorgang. Lieferant, Positionen, Mengen, Preise, Incoterms und Termine werden in der Bestellmaske gepflegt.',
    entryModes: [
      { value: 'Direktbestellung', description: 'Sofort in die Bestellanlage wechseln.' },
      { value: 'Bedarfsmeldung', description: 'Aus internem Bedarf oder Bestellvorschlag starten.' },
      { value: 'Rahmenabruf', description: 'Auf Basis eines bestehenden Vertrags abrufen.' },
    ],
    buildHref: (created) => {
      const query = new URLSearchParams({
        workflowProcess: 'procure-to-pay',
        workflowInstanceId: created.instance_id,
        workflowCase: created.case_number,
        workflowLabel: created.label,
        entryMode: created.entry_mode ?? 'Direktbestellung',
      })
      if (created.partner_name || created.customer_name) query.set('partnerName', created.partner_name ?? created.customer_name ?? '')
      if (created.subject) query.set('subject', created.subject)
      return `/einkauf/bestellungen/neu?${query.toString()}`
    },
  },
  'inventory-to-settlement': {
    buttonLabel: 'Neuen Lagerfall starten',
    dialogTitle: 'Neuen Lager- und Versandvorgang starten',
    dialogDescription: 'Welle oder Versandfall anlegen und in die operative Bestands- oder Verladeansicht uebergeben.',
    partnerLabel: 'Kunde / Rampe / Bereich',
    subjectLabel: 'Welle / Thema',
    labelLabel: 'Interne Referenz (optional)',
    labelPlaceholder: 'z.B. Welle Nord / Rampenwechsel',
    submitLabel: 'Lagerfall anlegen',
    explanation: 'Im Flow wird der operative Fall sichtbar gemacht. Bestandsdaten, Rampen und reale Versandbewegungen werden in den Lager- und Verlade-Masken gepflegt.',
    entryModes: [
      { value: 'Kommissionierwelle', description: 'Startet aus einer neuen Welle oder Prioritaetsliste.' },
      { value: 'Versandfall', description: 'Fokus auf Rampe, ETA und Verladung.' },
      { value: 'Bestandsklaerung', description: 'Fokus auf Bestand, Charge oder Inventurdifferenz.' },
    ],
    buildHref: (created) => {
      const query = new URLSearchParams({
        workflowProcess: 'inventory-to-settlement',
        workflowInstanceId: created.instance_id,
        workflowCase: created.case_number,
        workflowLabel: created.label,
        entryMode: created.entry_mode ?? 'Kommissionierwelle',
      })
      if (created.partner_name || created.customer_name) query.set('partnerName', created.partner_name ?? created.customer_name ?? '')
      if (created.subject) query.set('subject', created.subject)
      return `/lager/bestandsuebersicht?${query.toString()}`
    },
  },
  'harvest-to-settlement': {
    buttonLabel: 'Neue Ernteinstanz starten',
    dialogTitle: 'Neue Ernteannahme starten',
    dialogDescription: 'Anlieferer, Kampagne oder Charge erfassen und direkt in die Ernte-Annahmemaske wechseln.',
    partnerLabel: 'Anlieferer / Landwirt',
    subjectLabel: 'Charge / Kampagne / Thema',
    labelLabel: 'Interne Referenz (optional)',
    labelPlaceholder: 'z.B. Erntefenster Nord / Weizen KW32',
    submitLabel: 'Erntevorgang anlegen',
    explanation: 'Der Flow bildet den Kampagnenfall ab. Gewichte, Qualitaet, Trocknung, Silo und Settlement entstehen in den Standardmasken der Annahme.',
    entryModes: [
      { value: 'Ernteannahme', description: 'Direkter Einstieg in Annahme und Wiegeschein.' },
      { value: 'Trocknungsfall', description: 'Fokus auf Feuchte, Trockner und Silo.' },
      { value: 'Nachabrechnung', description: 'Rueckrechnung oder nachgelagerte Korrektur.' },
    ],
    buildHref: (created) => {
      const query = new URLSearchParams({
        workflowProcess: 'harvest-to-settlement',
        workflowInstanceId: created.instance_id,
        workflowCase: created.case_number,
        workflowLabel: created.label,
        entryMode: created.entry_mode ?? 'Ernteannahme',
      })
      if (created.partner_name || created.customer_name) query.set('partnerName', created.partner_name ?? created.customer_name ?? '')
      if (created.subject) query.set('subject', created.subject)
      return `/agrar/ernte-annahme-erfassung?${query.toString()}`
    },
  },
  'contract-to-settlement': {
    buttonLabel: 'Neuen Kontraktfall starten',
    dialogTitle: 'Neuen Kontrakt- und Abrechnungsfall starten',
    dialogDescription: 'Kontraktkontext aufbauen und danach in die Kontraktmaske oder Annahme uebergeben.',
    partnerLabel: 'Kunde / Lieferant',
    subjectLabel: 'Kontrakt / Thema',
    labelLabel: 'Interne Referenz (optional)',
    labelPlaceholder: 'z.B. Mais Vertrag 2026 / Nachtrag',
    submitLabel: 'Kontraktfall anlegen',
    explanation: 'Kontraktdaten, Mengenstaffeln, Preise und Konditionen gehoeren in die Kontraktmaske. Der Flow steuert danach Annahme, Qualitaet und Settlement.',
    entryModes: [
      { value: 'Neukontrakt', description: 'Neuen Kontrakt anlegen.' },
      { value: 'Annahme zu Kontrakt', description: 'Bestehenden Kontrakt mit Lieferung verbinden.' },
      { value: 'Nachtrag / Korrektur', description: 'Preis-, Mengen- oder Konditionsaenderung pflegen.' },
    ],
    buildHref: (created) => {
      const query = new URLSearchParams({
        workflowProcess: 'contract-to-settlement',
        workflowInstanceId: created.instance_id,
        workflowCase: created.case_number,
        workflowLabel: created.label,
        entryMode: created.entry_mode ?? 'Neukontrakt',
      })
      if (created.partner_name || created.customer_name) query.set('partnerName', created.partner_name ?? created.customer_name ?? '')
      if (created.subject) query.set('subject', created.subject)
      return `/kontrakte/neu?${query.toString()}`
    },
  },
  'complaint-to-resolution': {
    buttonLabel: 'Neue Reklamation starten',
    dialogTitle: 'Neue Reklamation starten',
    dialogDescription: 'Kunde und Reklamationsanlass erfassen, dann in den Reklamationsarbeitsplatz uebergeben.',
    partnerLabel: 'Kunde / Ansprechpartner',
    subjectLabel: 'Reklamationsanlass',
    labelLabel: 'Interne Referenz (optional)',
    labelPlaceholder: 'z.B. Charge 553 / Schaeden Nord',
    submitLabel: 'Reklamationsfall anlegen',
    explanation: 'Der Flow startet den Fall. Erfassung, Anhange, CRM-Zuordnung und Kulanzentscheidung werden in Reklamation, CRM und DMS gepflegt.',
    entryModes: [
      { value: 'Kundenreklamation', description: 'Fall direkt aus Kundenmeldung eroeffnen.' },
      { value: 'Interne Qualitaetsabweichung', description: 'Interne Abweichung mit DMS- und Audit-Bezug.' },
      { value: 'Kulanzpruefung', description: 'Bestehenden Fall fuer Freigabe vorbereiten.' },
    ],
    buildHref: (created) => {
      const query = new URLSearchParams({
        workflowProcess: 'complaint-to-resolution',
        workflowInstanceId: created.instance_id,
        workflowCase: created.case_number,
        workflowLabel: created.label,
        entryMode: created.entry_mode ?? 'Kundenreklamation',
      })
      if (created.partner_name || created.customer_name) query.set('partnerName', created.partner_name ?? created.customer_name ?? '')
      if (created.subject) query.set('subject', created.subject)
      return `/qualitaet/reklamationen?${query.toString()}`
    },
  },
  'service-to-customer': {
    buttonLabel: 'Neuen Servicefall starten',
    dialogTitle: 'Neuen Servicefall starten',
    dialogDescription: 'Kundenbezug und Servicethema erfassen und in die Service-Anfragen uebergeben.',
    partnerLabel: 'Kunde / Standort',
    subjectLabel: 'Serviceanliegen',
    labelLabel: 'Interne Referenz (optional)',
    labelPlaceholder: 'z.B. Spreizer Wartung Nord / Stoerung Feldrand',
    submitLabel: 'Servicefall anlegen',
    explanation: 'Im Flow entsteht der Servicefall. Ticketdaten, Termine, Disposition und Rueckmeldung werden in den Service- und Aktivitaetsmasken gepflegt.',
    entryModes: [
      { value: 'Stoerung', description: 'Akuter Servicefall mit schneller Priorisierung.' },
      { value: 'Wartung', description: 'Planbare Wartung oder wiederkehrender Service.' },
      { value: 'Beratung vor Ort', description: 'Termin oder Einsatz ohne Stoerung.' },
    ],
    buildHref: (created) => {
      const query = new URLSearchParams({
        workflowProcess: 'service-to-customer',
        workflowInstanceId: created.instance_id,
        workflowCase: created.case_number,
        workflowLabel: created.label,
        entryMode: created.entry_mode ?? 'Stoerung',
      })
      if (created.partner_name || created.customer_name) query.set('partnerName', created.partner_name ?? created.customer_name ?? '')
      if (created.subject) query.set('subject', created.subject)
      return `/service/anfragen?${query.toString()}`
    },
  },
  'finance-to-close': {
    buttonLabel: 'Neuen Abschlussfall starten',
    dialogTitle: 'Neuen Finance-to-Close-Fall starten',
    dialogDescription: 'Periode und Abschlusskontext erfassen und ins Abschluss-Cockpit uebergeben.',
    partnerLabel: 'Periode / Bereich',
    subjectLabel: 'Abschlussanlass',
    labelLabel: 'Interne Referenz (optional)',
    labelPlaceholder: 'z.B. Monatsabschluss 03/2026 / Sonderthema',
    submitLabel: 'Abschlussfall anlegen',
    explanation: 'Der Flow bildet den Abschlussfall. Buchungen, Abstimmungen, Meldungen und Sign-off passieren in den Finanzmasken.',
    entryModes: [
      { value: 'Monatsabschluss', description: 'Startet den regulaeren Periodenabschluss.' },
      { value: 'Quartalsabschluss', description: 'Mit Reporting- und Freigabefokus.' },
      { value: 'Sonderabschluss', description: 'Ausnahmefall oder Nachbearbeitung.' },
    ],
    buildHref: (created) => {
      const query = new URLSearchParams({
        workflowProcess: 'finance-to-close',
        workflowInstanceId: created.instance_id,
        workflowCase: created.case_number,
        workflowLabel: created.label,
        entryMode: created.entry_mode ?? 'Monatsabschluss',
      })
      if (created.partner_name || created.customer_name) query.set('partnerName', created.partner_name ?? created.customer_name ?? '')
      if (created.subject) query.set('subject', created.subject)
      return `/fibu/abschluss-cockpit?${query.toString()}`
    },
  },
  'compliance-to-report': {
    buttonLabel: 'Neuen Reportingfall starten',
    dialogTitle: 'Neuen Compliance- und Reportingfall starten',
    dialogDescription: 'Reportingkontext erfassen und in CO2-, EUDR- oder ESG-Reporting uebergeben.',
    partnerLabel: 'Report / Organisationseinheit',
    subjectLabel: 'Melde- oder Reportingthema',
    labelLabel: 'Interne Referenz (optional)',
    labelPlaceholder: 'z.B. CO2 Q2 / EUDR Batch Nord',
    submitLabel: 'Reportingfall anlegen',
    explanation: 'Der Flow fasst den Reportingfall. Datenqualitaet, Validierung, Freigabe und Publikation erfolgen in den Fachcockpits fuer Nachhaltigkeit und Compliance.',
    entryModes: [
      { value: 'CO2 Reporting', description: 'Klimabilanz und Nachhaltigkeitsdaten konsolidieren.' },
      { value: 'EUDR / Herkunft', description: 'Herkunftsnachweise und Ausnahmen steuern.' },
      { value: 'ESG Report', description: 'Managementreporting vorbereiten.' },
    ],
    buildHref: (created) => {
      const query = new URLSearchParams({
        workflowProcess: 'compliance-to-report',
        workflowInstanceId: created.instance_id,
        workflowCase: created.case_number,
        workflowLabel: created.label,
        entryMode: created.entry_mode ?? 'CO2 Reporting',
      })
      if (created.partner_name || created.customer_name) query.set('partnerName', created.partner_name ?? created.customer_name ?? '')
      if (created.subject) query.set('subject', created.subject)
      return `/nachhaltigkeit/co2-bilanz?${query.toString()}`
    },
  },
}

function toneClasses(tone: string): string {
  switch (tone) {
    case 'ok':
      return 'border-emerald-500/50 bg-emerald-500/12 text-emerald-200'
    case 'warning':
      return 'border-amber-500/50 bg-amber-500/12 text-amber-100'
    case 'critical':
      return 'border-rose-500/60 bg-rose-500/12 text-rose-100'
    case 'active':
      return 'border-indigo-400/70 bg-indigo-400/15 text-indigo-100 shadow-[0_0_40px_rgba(99,102,241,0.28)]'
    default:
      return 'border-slate-500/40 bg-slate-500/10 text-slate-200'
  }
}

export function FlowSpineWorkspace({ processKey, instanceId }: FlowSpineWorkspaceProps): JSX.Element {
  const navigate = useNavigate()
  const activeLang = i18n.resolvedLanguage ?? i18n.language ?? 'de'
  const startConfig = PROCESS_START_CONFIGS[processKey] ?? PROCESS_START_CONFIGS['order-to-cash']
  const workspaceQuery = useQuery({
    queryKey: getFlowSpineWorkspaceQueryKey(processKey, instanceId, activeLang),
    queryFn: () => fetchFlowSpineWorkspace(processKey, instanceId),
    staleTime: 5 * 60_000,        // 5 min — workspace is mostly static
    gcTime: 15 * 60_000,          // keep in cache 15 min after unmount
    retry: false,
    placeholderData: (prev) => prev,  // show stale data while revalidating (no spinner flash)
    refetchOnWindowFocus: false,  // don't refetch when tab regains focus
  })
  const workspace = workspaceQuery.data
  const [selectedNodeId, setSelectedNodeId] = useState<string>('')

  // New instance dialog state
  const [showNewInstanceDialog, setShowNewInstanceDialog] = useState(false)
  const [newInstanceLabel, setNewInstanceLabel] = useState('')
  const [newInstancePartnerName, setNewInstancePartnerName] = useState('')
  const [newInstanceSubject, setNewInstanceSubject] = useState('')
  const [newInstanceEntryMode, setNewInstanceEntryMode] = useState(startConfig.entryModes[0]?.value ?? 'Direktauftrag')
  const createInstance = useCreateFlowSpineInstance(processKey)

  // Action execution hooks
  const executeAction = useExecuteFlowSpineAction()
  const executeAgentAction = useExecuteAgentAction(processKey)

  useEffect(() => {
    setNewInstanceEntryMode(startConfig.entryModes[0]?.value ?? 'Direktauftrag')
    setNewInstanceLabel('')
    setNewInstancePartnerName('')
    setNewInstanceSubject('')
  }, [startConfig, processKey])

  useEffect(() => {
    if (workspace?.focus_node_id) {
      setSelectedNodeId(workspace.focus_node_id)
    }
  }, [workspace?.focus_node_id])

  const nodes: FlowSpineNode[] = useMemo(
    () => (Array.isArray(workspace?.nodes) ? workspace.nodes : []),
    [workspace?.nodes],
  )

  const selectedNode = useMemo(
    () => nodes.find((node) => node.id === selectedNodeId) ?? nodes[0],
    [selectedNodeId, nodes],
  )

  const completedCount = useMemo(() => nodes.filter((node) => node.status === 'ok').length, [nodes])
  const progressWidth = nodes.length
    ? `${(Math.max(1, completedCount + (selectedNode ? 1 : 0)) / nodes.length) * 100}%`
    : '0%'

  const go = (href: string): void => {
    navigate(href)
  }

  const handleAction = async (action: FlowSpineAction): Promise<void> => {
    if (action.api_path) {
      try {
        await executeAction.mutateAsync({ apiPath: action.api_path })
        toast({ title: 'Aktion ausgeführt', description: action.label })
      } catch (e) {
        console.error('Action failed:', e)
        toast({
          title: 'Fehler',
          description: `Aktion "${action.label}" konnte nicht ausgeführt werden.`,
          variant: 'destructive',
        })
      }
    }
    if (action.href) {
      go(action.href)
    }
  }

  const handleAgentAction = async (action: string): Promise<void> => {
    try {
      await executeAgentAction.mutateAsync({
        action,
        node_id: selectedNode?.id,
      })
      toast({ title: 'Agent-Aktion ausgeführt', description: action })
    } catch (e) {
      console.error('Agent action failed:', e)
      toast({
        title: 'Fehler',
        description: `Agent-Aktion "${action}" konnte nicht ausgeführt werden.`,
        variant: 'destructive',
      })
    }
  }

  const handleCreateInstance = async (): Promise<void> => {
    const trimmedLabel = newInstanceLabel.trim()
    const trimmedPartnerName = newInstancePartnerName.trim()
    const trimmedSubject = newInstanceSubject.trim()
    if (!trimmedLabel && !trimmedPartnerName && !trimmedSubject) return
    try {
      const created = await createInstance.mutateAsync({
        label: trimmedLabel || undefined,
        customer_name: processKey === 'order-to-cash' ? trimmedPartnerName || undefined : undefined,
        partner_name: processKey !== 'order-to-cash' ? trimmedPartnerName || undefined : undefined,
        subject: trimmedSubject || undefined,
        entry_mode: newInstanceEntryMode,
      })
      toast({ title: 'Vorgang erstellt', description: created.label })
      setShowNewInstanceDialog(false)
      setNewInstanceLabel('')
      setNewInstancePartnerName('')
      setNewInstanceSubject('')
      setNewInstanceEntryMode(startConfig.entryModes[0]?.value ?? 'Direktauftrag')
      go(startConfig.buildHref(created))
    } catch (e) {
      console.error('Create instance failed:', e)
      toast({
        title: 'Fehler',
        description: 'Instanz konnte nicht erstellt werden.',
        variant: 'destructive',
      })
    }
  }

  if (workspaceQuery.isLoading) {
    return (
      <PageSurface
        data-page-surface={`flow-spine-${processKey}`}
        className="bg-[radial-gradient(circle_at_top_left,_rgba(99,102,241,0.12),_transparent_28%),linear-gradient(180deg,#08101f,#0d1528)]"
      >
        <PageSection className="overflow-hidden border-white/10 bg-slate-950/70 p-0">
          {/* Header skeleton */}
          <div className="flex h-16 items-center justify-between border-b border-white/5 px-5 gap-4">
            <div className="h-4 w-48 rounded-full bg-white/10 animate-pulse" />
            <div className="h-8 flex-1 max-w-xl rounded-lg bg-white/5 animate-pulse" />
            <div className="h-8 w-32 rounded-lg bg-white/10 animate-pulse" />
          </div>
          {/* 3-column body skeleton */}
          <div className="grid min-h-[720px] grid-cols-[220px_minmax(0,1fr)_360px]">
            {/* Left nav skeleton */}
            <div className="border-r border-white/5 bg-slate-950/45 p-4 space-y-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-10 rounded-2xl bg-white/5 animate-pulse" style={{ animationDelay: `${i * 60}ms` }} />
              ))}
            </div>
            {/* Main content skeleton */}
            <div className="bg-[linear-gradient(180deg,rgba(15,23,42,0.35),rgba(15,23,42,0.15))] p-6 space-y-6">
              <div className="h-8 w-72 rounded-full bg-white/10 animate-pulse" />
              <div className="rounded-[28px] border border-white/10 bg-white/[0.03] p-8">
                {/* Node circles */}
                <div className="flex justify-around mb-8">
                  {Array.from({ length: 6 }).map((_, i) => (
                    <div key={i} className="flex flex-col items-center gap-3">
                      <div className="h-16 w-16 rounded-full bg-white/10 animate-pulse" style={{ animationDelay: `${i * 80}ms` }} />
                      <div className="h-3 w-16 rounded-full bg-white/10 animate-pulse" />
                    </div>
                  ))}
                </div>
                {/* Detail cards */}
                <div className="grid gap-5 xl:grid-cols-[1fr_300px]">
                  <div className="h-48 rounded-2xl bg-white/5 animate-pulse" />
                  <div className="h-48 rounded-2xl bg-white/5 animate-pulse" style={{ animationDelay: '100ms' }} />
                </div>
              </div>
            </div>
            {/* Right panel skeleton */}
            <div className="border-l border-white/5 bg-slate-950/45 p-5 space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-12 rounded-2xl bg-white/5 animate-pulse" style={{ animationDelay: `${i * 70}ms` }} />
              ))}
            </div>
          </div>
        </PageSection>
      </PageSurface>
    )
  }

  if (workspaceQuery.isError) {
    const detail = getFlowSpineFetchErrorMessage(workspaceQuery.error)
    return (
      <PageSurface data-page-surface={`flow-spine-${processKey}`}>
        <PageSection title="Flow Spine nicht verfuegbar" description="Der Prozessraum konnte nicht geladen werden.">
          <div className="space-y-3 rounded-2xl border border-destructive/30 bg-destructive/10 px-4 py-6 text-sm">
            <p className="font-medium text-destructive">{detail}</p>
            <p className="text-muted-foreground">
              Erwartet wird{' '}
              <code className="rounded bg-muted px-1 py-0.5 text-xs">
                GET /api/v1/process/flow-spines/{processKey}
              </code>{' '}
              mit JSON-Feld <code className="rounded bg-muted px-1 py-0.5 text-xs">nodes</code>. Lokal: FastAPI
              starten (z.&nbsp;B. Port 8000) und sicherstellen, dass Vite{' '}
              <code className="rounded bg-muted px-1 py-0.5 text-xs">/api/v1</code> dorthin proxied oder{' '}
              <code className="rounded bg-muted px-1 py-0.5 text-xs">VITE_API_BASE_URL</code> korrekt ist.
            </p>
          </div>
        </PageSection>
      </PageSurface>
    )
  }

  if (!workspace || nodes.length === 0 || !selectedNode) {
    return (
      <PageSurface data-page-surface={`flow-spine-${processKey}`}>
        <PageSection title="Flow Spine nicht verfuegbar" description="Der Prozessraum konnte nicht geladen werden.">
          <div className="rounded-2xl border border-destructive/30 bg-destructive/10 px-4 py-6 text-sm text-destructive">
            Ungueltige oder leere Workspace-Daten (nodes). Bitte Backend-Vertrag pruefen.
          </div>
        </PageSection>
      </PageSurface>
    )
  }

  return (
    <PageSurface
      data-page-surface={`flow-spine-${processKey}`}
      className="bg-[radial-gradient(circle_at_top_left,_rgba(99,102,241,0.12),_transparent_28%),linear-gradient(180deg,#08101f,#0d1528)]"
    >
      <PageSection className="overflow-hidden border-white/10 bg-slate-950/70 p-0 shadow-2xl shadow-indigo-950/20">
        <header className="flex h-16 items-center justify-between border-b border-white/5 px-5">
          <div className="flex items-center gap-4">
            <div className="text-sm font-semibold tracking-wide text-slate-100">{workspace.breadcrumb[0]}</div>
            <div className="text-sm text-slate-400">
              {workspace.breadcrumb[1]} <span className="px-2 text-slate-600">/</span> <span className="font-semibold text-slate-100">{workspace.instance_label}</span>
            </div>
          </div>
          <div className="relative w-full max-w-xl">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <Input aria-label="Globale Suche" placeholder={workspace.search_placeholder} className="border-white/10 bg-white/5 pl-9 text-slate-100 placeholder:text-slate-500" />
          </div>
          <div className="flex items-center gap-3">
            <Button
              size="sm"
              variant="outline"
              className="border-indigo-400/30 bg-indigo-500/10 text-indigo-200 hover:bg-indigo-500/20"
              onClick={() => setShowNewInstanceDialog(true)}
            >
              <Plus className="mr-1.5 h-3.5 w-3.5" />
              {startConfig.buttonLabel}
            </Button>
            <div className="flex rounded-xl bg-white/5 p-1 text-xs">
              {['Flow', 'Fokus', 'Uebersicht'].map((mode) => (
                <span key={mode} className={cn('rounded-lg px-3 py-1.5 text-slate-400', workspace.mode === mode && 'bg-indigo-500/30 text-indigo-100')}>
                  {mode}
                </span>
              ))}
            </div>
            <Bell className="h-4 w-4 text-slate-300" />
            <Settings className="h-4 w-4 text-slate-300" />
            <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-slate-100">
              <UserCircle2 className="h-5 w-5 text-slate-300" />
              <span>{workspace.user_role}</span>
            </div>
          </div>
        </header>

        <div className="grid min-h-[720px] grid-cols-[220px_minmax(0,1fr)_360px]">
          <aside className="border-r border-white/5 bg-slate-950/45 p-4">
            <div className="mb-6">
              <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Prozesse</p>
              <div className="space-y-2">
                {workspace.left_navigation.processes.map((process) => (
                  <button
                    key={process.key}
                    onClick={() => go(process.route_path)}
                    className={cn(
                      'flex w-full items-center justify-between rounded-2xl px-3 py-3 text-left text-sm transition',
                      process.active ? 'bg-indigo-500/12 text-indigo-100 ring-1 ring-indigo-400/20' : 'text-slate-300 hover:bg-white/5 hover:text-white',
                    )}
                  >
                    <span>{process.label}</span>
                    <ChevronRight className="h-4 w-4" />
                  </button>
                ))}
              </div>
            </div>
            {[
              { title: 'Favoriten', items: workspace.left_navigation.favorites },
              { title: 'Letzte Vorgaenge', items: workspace.left_navigation.recent_items },
            ].map((section) => (
              <div key={section.title} className="mb-6">
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">{section.title}</p>
                <div className="space-y-2 text-sm text-slate-300">
                  {section.items.map((item) => (
                    <div key={item} className="rounded-2xl border border-white/5 bg-white/[0.03] px-3 py-3">{item}</div>
                  ))}
                </div>
              </div>
            ))}
            <div>
              <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Rollenwechsel</p>
              <div className="space-y-2">
                {workspace.left_navigation.role_switches.map((role) => (
                  <Button key={role} variant="outline" className="w-full justify-start border-white/10 bg-white/5 text-slate-200 hover:bg-white/10">
                    {role}
                  </Button>
                ))}
              </div>
            </div>
          </aside>

          <main className="bg-[linear-gradient(180deg,rgba(15,23,42,0.35),rgba(15,23,42,0.15))] p-6">
            <div className="mb-6 flex items-start justify-between gap-4">
              <div>
                <h1 className="text-3xl font-bold tracking-tight text-white">{workspace.title}</h1>
                <p className="mt-1 max-w-3xl text-sm text-slate-400">{workspace.subtitle}</p>
              </div>
              <div className="flex items-center gap-2">
                {workspace.badges.map((badge) => (
                  <Badge key={badge.label} className={cn('hover:bg-transparent', badge.tone === 'ok' ? 'bg-emerald-500/15 text-emerald-200' : 'bg-amber-500/15 text-amber-100')}>
                    {badge.label}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="rounded-[28px] border border-white/10 bg-white/[0.03] p-8">
              <div className="relative mb-8">
                <div className="absolute left-8 right-8 top-10 h-[2px] rounded-full bg-white/10" />
                <div className="absolute left-8 top-10 h-[2px] rounded-full bg-gradient-to-r from-emerald-400 via-indigo-400 to-amber-400" style={{ width: progressWidth }} />
                <div className={cn('relative grid gap-4', nodes.length === 4 ? 'grid-cols-4' : nodes.length === 5 ? 'grid-cols-5' : 'grid-cols-6')}>
                  {nodes.map((node) => {
                    const Icon = ICONS[node.icon as keyof typeof ICONS] ?? Sparkles
                    const active = node.id === selectedNode.id
                    return (
                      <button key={node.id} onClick={() => setSelectedNodeId(node.id)} className={cn('rounded-3xl p-3 text-center transition', active ? 'scale-[1.03]' : 'hover:-translate-y-1')}>
                        <div className={cn('mx-auto flex h-16 w-16 items-center justify-center rounded-full border', toneClasses(node.status), active && 'h-20 w-20')}>
                          <Icon className="h-6 w-6" />
                        </div>
                        <div className="mt-3 text-sm font-semibold text-slate-100">{node.label}</div>
                        <div className="text-xs text-slate-500">{node.metric}</div>
                        <div className="text-[11px] text-slate-400">{node.submetric}</div>
                      </button>
                    )
                  })}
                </div>
              </div>

              <div className="grid gap-5 xl:grid-cols-[1fr_300px]">
                <div className="grid gap-5">
                  <div className="grid gap-5 xl:grid-cols-[1.2fr_280px]">
                    <Card className="border-white/10 bg-slate-950/50 text-slate-100">
                      <CardHeader className="flex flex-row items-start justify-between gap-4">
                        <div>
                          <CardTitle className="text-xl">Status Details: {selectedNode.label}</CardTitle>
                          <p className="mt-1 text-sm text-slate-400">{selectedNode.insight}</p>
                        </div>
                        <Badge className={cn('border px-2.5 py-1 text-xs', toneClasses(selectedNode.status))}>{selectedNode.status.toUpperCase()}</Badge>
                      </CardHeader>
                      <CardContent className="grid gap-4 md:grid-cols-2">
                        {selectedNode.detail_rows.map((row) => (
                          <div key={row.label} className="space-y-1">
                            <div className="text-xs uppercase tracking-[0.18em] text-slate-500">{row.label}</div>
                            <div className="text-sm font-medium text-slate-100">{row.value}</div>
                          </div>
                        ))}
                      </CardContent>
                    </Card>

                    <Card className="border-white/10 bg-white/[0.06] text-slate-100">
                      <CardHeader>
                        <CardTitle className="text-sm uppercase tracking-[0.2em] text-slate-400">KPI Health Score</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="mb-3 text-5xl font-bold text-white">{selectedNode.kpis[0]?.value ?? '92%'}</div>
                        <div className="mb-4 h-2 rounded-full bg-white/10">
                          <div className="h-2 rounded-full bg-indigo-400" style={{ width: '92%' }} />
                        </div>
                        <div className="text-sm text-slate-400">Prozesseffizienz liegt sichtbar ueber dem Quartalsdurchschnitt.</div>
                      </CardContent>
                    </Card>
                  </div>

                  <div className="grid gap-4 lg:grid-cols-4">
                    <Card className="border-white/10 bg-white/[0.03] text-slate-100">
                      <CardHeader><CardTitle className="text-sm">KPIs</CardTitle></CardHeader>
                      <CardContent className="space-y-2 text-sm">{selectedNode.kpis.map((kpi) => <div key={kpi.label} className="flex justify-between gap-3"><span className="text-slate-400">{kpi.label}</span><span>{kpi.value}</span></div>)}</CardContent>
                    </Card>
                    <Card className="border-white/10 bg-white/[0.03] text-slate-100">
                      <CardHeader><CardTitle className="text-sm">Dokumente</CardTitle></CardHeader>
                      <CardContent className="space-y-2 text-sm">{selectedNode.documents.map((doc) => <button key={doc.label} onClick={() => go(doc.href)} className="flex w-full items-center gap-2 text-left text-slate-300 hover:text-white"><FileText className="h-4 w-4 text-slate-500" />{doc.label}</button>)}</CardContent>
                    </Card>
                    <Card className="border-white/10 bg-white/[0.03] text-slate-100">
                      <CardHeader><CardTitle className="text-sm">Aktionen</CardTitle></CardHeader>
                      <CardContent className="space-y-3">
                        {selectedNode.actions.map((action) => (
                          <Button
                            key={action.label}
                            onClick={() => void handleAction(action)}
                            disabled={executeAction.isPending}
                            variant={action.variant === 'primary' ? 'default' : 'outline'}
                            className={cn('w-full justify-between', action.variant === 'primary' ? 'bg-indigo-500 text-white hover:bg-indigo-400' : 'border-white/10 bg-white/5 text-slate-200 hover:bg-white/10')}
                          >
                            {action.label}
                            <ChevronRight className="h-4 w-4" />
                          </Button>
                        ))}
                      </CardContent>
                    </Card>
                    <Card className="border-indigo-400/20 bg-indigo-500/10 text-slate-100">
                      <CardHeader><CardTitle className="text-sm">Agent</CardTitle></CardHeader>
                      <CardContent className="space-y-3 text-sm">
                        <div className="font-semibold text-white">{selectedNode.agent.headline}</div>
                        <p className="text-slate-300">{selectedNode.agent.message}</p>
                        <ul className="space-y-1 text-xs text-slate-300">{selectedNode.agent.reasons.map((reason) => <li key={reason}>- {reason}</li>)}</ul>
                      </CardContent>
                    </Card>
                  </div>
                </div>

                <div className="space-y-4">
                  <AgentProcessPanel domain={workspace.right_panel.domain} className="max-w-none border-white/10 bg-slate-950/50" />
                  <Card className="border-white/10 bg-slate-950/50 text-slate-100">
                    <CardHeader><CardTitle className="text-lg">Linked Modules</CardTitle></CardHeader>
                    <CardContent className="space-y-3">
                      {workspace.right_panel.linked_modules.map((module) => (
                        <button
                          key={module.label}
                          onClick={() => {
                            if (module.api_path) {
                              void executeAction.mutateAsync({ apiPath: module.api_path })
                            }
                            if (module.href) go(module.href)
                          }}
                          className="flex w-full items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-slate-200 hover:bg-white/5"
                        >
                          <span>{module.label}</span>
                          <ChevronRight className="h-4 w-4 text-slate-500" />
                        </button>
                      ))}
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>

            <div className="mt-6 grid gap-4 lg:grid-cols-3">
              {workspace.footer_cards.map((card) => {
                const isNextSteps =
                  /schritt/i.test(card.title) || /naechste/i.test(card.title)
                return (
                <Card key={card.title} className="border-white/10 bg-slate-950/45 text-slate-100">
                  <CardHeader>
                    <CardTitle className="text-base">{card.title}</CardTitle>
                    {isNextSteps ? (
                      <CardDescription className="text-slate-400">
                        Orientierung — keine Navigation; die Punkte sind als Checkliste gemeint.
                      </CardDescription>
                    ) : null}
                  </CardHeader>
                  <CardContent className="text-sm text-slate-300">
                    <ul
                      className={
                        isNextSteps
                          ? 'list-disc space-y-1.5 pl-5 marker:text-slate-500'
                          : 'space-y-2'
                      }
                    >
                      {card.items.map((item) => (
                        <li
                          key={item}
                          className={isNextSteps ? 'leading-snug' : 'rounded-2xl border border-white/10 px-4 py-3'}
                        >
                          {item}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )})}
            </div>
          </main>

          <aside className="border-l border-white/5 bg-slate-950/45 p-5">
            <div className="mb-4 text-sm font-semibold text-slate-100">AI Copilot</div>
            <Tabs defaultValue="agent" className="flex h-full flex-col">
              <TabsList className="grid w-full grid-cols-4 bg-white/5">
                <TabsTrigger value="agent">Agent</TabsTrigger>
                <TabsTrigger value="actions">Aktionen</TabsTrigger>
                <TabsTrigger value="docs">Docs</TabsTrigger>
                <TabsTrigger value="kpis">KPIs</TabsTrigger>
              </TabsList>
              <TabsContent value="agent" className="mt-4 space-y-4">
                <Card className="border-white/10 bg-white/[0.03] text-slate-100">
                  <CardHeader><CardTitle className="text-base">{selectedNode.agent.headline}</CardTitle></CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    <p>{selectedNode.agent.message}</p>
                    <div className="space-y-1 text-xs text-slate-300">{selectedNode.agent.reasons.map((reason) => <div key={reason}>- {reason}</div>)}</div>
                    <div className="grid grid-cols-3 gap-2">
                      {selectedNode.agent.actions.map((action) => (
                        <Button
                          key={action}
                          size="sm"
                          disabled={executeAgentAction.isPending}
                          onClick={() => void handleAgentAction(action)}
                          variant={action === 'Uebernehmen' ? 'default' : 'outline'}
                          className={cn(action === 'Uebernehmen' ? 'bg-white text-slate-900 hover:bg-white/90' : 'border-white/10 bg-white/5 text-white hover:bg-white/10')}
                        >
                          {action}
                        </Button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
              <TabsContent value="actions" className="mt-4 space-y-3">
                {selectedNode.actions.map((action) => (
                  <Button
                    key={action.label}
                    onClick={() => void handleAction(action)}
                    disabled={executeAction.isPending}
                    className={cn('w-full justify-between', action.variant === 'primary' ? 'bg-indigo-500 text-white hover:bg-indigo-400' : 'border-white/10 bg-white/5 text-slate-200 hover:bg-white/10')}
                    variant={action.variant === 'primary' ? 'default' : 'outline'}
                  >
                    {action.label}
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                ))}
              </TabsContent>
              <TabsContent value="docs" className="mt-4 space-y-3">
                {selectedNode.documents.concat(workspace.right_panel.resources).map((doc) => (
                  <button
                    key={`${doc.label}-${doc.href}`}
                    onClick={() => go(doc.href)}
                    className="flex w-full items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-left text-sm text-slate-200 hover:bg-white/5"
                  >
                    <span className="flex items-center gap-2"><FileText className="h-4 w-4 text-slate-500" />{doc.label}</span>
                    <ChevronRight className="h-4 w-4 text-slate-500" />
                  </button>
                ))}
              </TabsContent>
              <TabsContent value="kpis" className="mt-4 space-y-3">
                {selectedNode.kpis.map((kpi) => (
                  <div key={kpi.label} className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                    <div className="text-xs uppercase tracking-[0.2em] text-slate-500">{kpi.label}</div>
                    <div className="mt-2 text-lg font-semibold text-white">{kpi.value}</div>
                  </div>
                ))}
              </TabsContent>
            </Tabs>
          </aside>
        </div>
      </PageSection>

      {/* Neue Instanz Dialog */}
      <Dialog open={showNewInstanceDialog} onOpenChange={setShowNewInstanceDialog}>
          <DialogContent className="border-white/10 bg-slate-900 text-slate-100">
          <DialogHeader>
            <DialogTitle>{startConfig.dialogTitle}</DialogTitle>
            <DialogDescription className="text-slate-400">{startConfig.dialogDescription}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="grid gap-3 md:grid-cols-3">
              {startConfig.entryModes.map((mode) => (
                    <button
                      key={mode.value}
                      type="button"
                      onClick={() => setNewInstanceEntryMode(mode.value)}
                      className={cn(
                        'rounded-2xl border px-4 py-3 text-left text-sm transition',
                        newInstanceEntryMode === mode.value
                          ? 'border-indigo-400/60 bg-indigo-500/15 text-indigo-100'
                          : 'border-white/10 bg-white/5 text-slate-300 hover:bg-white/10',
                      )}
                    >
                      <div className="font-medium">{mode.value}</div>
                      <div className="mt-1 text-xs text-slate-400">{mode.description}</div>
                    </button>
                  ))}
            </div>
            <div className="space-y-2">
              <Label htmlFor="instance-partner" className="text-slate-300">{startConfig.partnerLabel}</Label>
              <div className="relative">
                <Building2 className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <Input
                  id="instance-partner"
                  value={newInstancePartnerName}
                  onChange={(e) => setNewInstancePartnerName(e.target.value)}
                  placeholder="z.B. Agrarhandel Nord eG"
                  className="border-white/10 bg-white/5 pl-9 text-slate-100 placeholder:text-slate-500"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="instance-subject" className="text-slate-300">{startConfig.subjectLabel}</Label>
              <Input
                id="instance-subject"
                value={newInstanceSubject}
                onChange={(e) => setNewInstanceSubject(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') void handleCreateInstance() }}
                placeholder="z.B. Themenbeschreibung oder operative Referenz"
                className="border-white/10 bg-white/5 text-slate-100 placeholder:text-slate-500"
              />
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-slate-300">
              <div className="font-medium text-slate-100">Praxislogik</div>
              <div className="mt-1">{startConfig.explanation}</div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="instance-label" className="text-slate-300">{startConfig.labelLabel}</Label>
              <Input
                id="instance-label"
                value={newInstanceLabel}
                onChange={(e) => setNewInstanceLabel(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') void handleCreateInstance() }}
                placeholder={startConfig.labelPlaceholder}
                className="border-white/10 bg-white/5 text-slate-100 placeholder:text-slate-500"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => { setShowNewInstanceDialog(false); setNewInstanceLabel(''); setNewInstancePartnerName(''); setNewInstanceSubject(''); setNewInstanceEntryMode(startConfig.entryModes[0]?.value ?? 'Direktauftrag') }}
              className="border-white/10 bg-white/5 text-slate-200 hover:bg-white/10"
            >
              Abbrechen
            </Button>
            <Button
              onClick={() => void handleCreateInstance()}
              disabled={(!newInstanceLabel.trim() && !newInstancePartnerName.trim() && !newInstanceSubject.trim()) || createInstance.isPending}
              className="bg-indigo-500 text-white hover:bg-indigo-400"
            >
              {createInstance.isPending ? 'Wird erstellt...' : startConfig.submitLabel}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </PageSurface>
  )
}

export default FlowSpineWorkspace
