import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate, useSearchParams } from '@/app/routing/typed-router'
import type { CustomerLite } from '@/components/crm/CustomerCombobox'
import { fetchFlowSpineWorkspace, getFlowSpineWorkspaceQueryKey, useCreateFlowSpineInstance, useExecuteAgentAction, useExecuteFlowSpineAction, useFlowSpineLifecycleAction, useFlowSpineInstances, useFlowSpineTimeline, useResumeFlowSpineInstance, useSaveFlowSpineInstance, useFlowSpineCatalogHook, type FlowSpineAction, type FlowSpineLifecycleActionPayload, type FlowSpineNode } from '@/lib/api/flow-spines'
import { useDebounce } from '@/hooks/useDebounce'
import { toast } from '@/hooks/use-toast'
import i18n from '@/i18n/config'
import { useQuery } from '@tanstack/react-query'

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

type LifecycleDialogMode = 'hold' | 'complete' | 'cancel' | 'fail'

type LifecycleDialogState = {
  mode: LifecycleDialogMode
  reasonCategory: string
  reasonCode: string
  reasonNote: string
  businessStatus: string
  blockedUntil: string
}

type FlowSpineViewMode = 'flow' | 'fokus' | 'uebersicht'

export function useFlowSpineWorkspaceRuntime(processKey: string, instanceIdProp?: string) {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const instanceId = processKey ? instanceIdProp || searchParams.get('instanceId') || undefined : undefined
  const activeLang = i18n.resolvedLanguage ?? i18n.language ?? 'de'
  const startConfig = PROCESS_START_CONFIGS[processKey] ?? PROCESS_START_CONFIGS['order-to-cash']
  const workspaceQuery = useQuery({
    enabled: Boolean(processKey),
    queryKey: getFlowSpineWorkspaceQueryKey(processKey, instanceId, activeLang),
    queryFn: () => fetchFlowSpineWorkspace(processKey, instanceId),
    staleTime: 5 * 60_000,        // 5 min — workspace is mostly static
    gcTime: 15 * 60_000,          // keep in cache 15 min after unmount
    retry: false,
    placeholderData: (prev) => prev,  // show stale data while revalidating (no spinner flash)
    refetchOnWindowFocus: false,  // don't refetch when tab regains focus
  })
  const workspace = workspaceQuery.data
  const hasSidebarProcessList =
    Array.isArray(workspace?.left_navigation?.processes) &&
    (workspace.left_navigation?.processes?.length ?? 0) > 0
  /** Katalog nur bei fehlender/leerer Prozessliste — spart Request und vermeidet Doppel-401/Netzwerk-Laerm. */
  const catalogQuery = useFlowSpineCatalogHook({
    enabled:
      workspaceQuery.isSuccess &&
      Boolean(workspace) &&
      !hasSidebarProcessList,
  })
  const [selectedNodeId, setSelectedNodeId] = useState<string>('')

  // New instance dialog state
  const [showNewInstanceDialog, setShowNewInstanceDialog] = useState(false)
  const [newInstanceLabel, setNewInstanceLabel] = useState('')
  const [newInstancePartnerName, setNewInstancePartnerName] = useState('')
  const [newInstanceSubject, setNewInstanceSubject] = useState('')
  const [newInstanceEntryMode, setNewInstanceEntryMode] = useState(startConfig.entryModes[0]?.value ?? 'Direktauftrag')
  const [newInstanceCustomer, setNewInstanceCustomer] = useState<CustomerLite | null>(null)
  const [showAdvancedCustomerSearch, setShowAdvancedCustomerSearch] = useState(false)
  const createInstance = useCreateFlowSpineInstance(processKey)
  const location = useLocation()

  const [instanceSearch, setInstanceSearch] = useState('')
  const debouncedInstanceSearch = useDebounce(instanceSearch, 300)
  const instancesQuery = useFlowSpineInstances(processKey, debouncedInstanceSearch || undefined, workspaceQuery.isSuccess)
  const timelineQuery = useFlowSpineTimeline(processKey, instanceId)
  const saveInstance = useSaveFlowSpineInstance(processKey, instanceId)
  const resumeInstance = useResumeFlowSpineInstance(processKey, instanceId)
  const holdInstance = useFlowSpineLifecycleAction(processKey, instanceId, 'hold')
  const completeInstance = useFlowSpineLifecycleAction(processKey, instanceId, 'complete')
  const cancelInstance = useFlowSpineLifecycleAction(processKey, instanceId, 'cancel')
  const failInstance = useFlowSpineLifecycleAction(processKey, instanceId, 'fail')
  const [lifecycleDialog, setLifecycleDialog] = useState<LifecycleDialogState | null>(null)

  // Action execution hooks
  const executeAction = useExecuteFlowSpineAction()
  const executeAgentAction = useExecuteAgentAction(processKey)

  useEffect(() => {
    setNewInstanceEntryMode(startConfig.entryModes[0]?.value ?? 'Direktauftrag')
    setNewInstanceLabel('')
    setNewInstancePartnerName('')
    setNewInstanceSubject('')
    setNewInstanceCustomer(null)
  }, [startConfig, processKey])

  // Return from "+ Neuen Kunden anlegen" — KundeNeuMaskBuilderPage sendet uns
  // ?newCustomerId=<id>&newCustomerName=<name>&newCustomerNumber=<nr>&openNewInstance=1 zurueck.
  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const newId = params.get('newCustomerId')
    const newName = params.get('newCustomerName')
    const newNumber = params.get('newCustomerNumber') ?? ''
    const reopen = params.get('openNewInstance') === '1'
    if (!processKey || !reopen || !newId || !newName) return

    setNewInstanceCustomer({
      id: newId,
      customer_number: newNumber,
      company_name: newName,
    })
    setNewInstancePartnerName(newName)
    const keepSubject = params.get('subject')
    const keepLabel = params.get('label')
    if (keepSubject) setNewInstanceSubject(keepSubject)
    if (keepLabel) setNewInstanceLabel(keepLabel)
    setShowNewInstanceDialog(true)

    // Query-Params wieder aufraeumen, damit der Effect nicht zweimal feuert.
    const cleaned = new URLSearchParams(location.search)
    cleaned.delete('newCustomerId')
    cleaned.delete('newCustomerName')
    cleaned.delete('newCustomerNumber')
    cleaned.delete('openNewInstance')
    cleaned.delete('subject')
    cleaned.delete('label')
    const cleanedQuery = cleaned.toString()
    navigate(`${location.pathname}${cleanedQuery ? `?${cleanedQuery}` : ''}`, { replace: true })
  }, [location.search, location.pathname, navigate, processKey])

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

  /** Prozessliste: Workspace bevorzugt; falls `left_navigation.processes` fehlt, Katalog (z. B. nach Gateway-Strip). */
  const processNavItems = useMemo(() => {
    const fromWorkspace = workspace?.left_navigation?.processes
    if (Array.isArray(fromWorkspace) && fromWorkspace.length > 0) {
      return fromWorkspace
    }
    const catalog = catalogQuery.data?.processes
    if (Array.isArray(catalog) && catalog.length > 0) {
      return catalog.map((p) => ({
        key: p.key,
        label: p.label,
        route_path: p.route_path,
        active: p.key === processKey,
      }))
    }
    return []
  }, [workspace?.left_navigation?.processes, catalogQuery.data?.processes, processKey])

  // FSX-024: Favoriten und Rollenwechsel sind Aufgaben der AppShell, nicht des
  // Prozessraums. Sie werden hier nicht mehr gerendert; die Backend-Felder
  // bleiben vorerst bestehen, damit die Shell sie uebernehmen kann.

  // FSX-020: Die drei Modi waren beschriftete <span> ohne Wirkung. Jetzt tragen
  // sie echten Zustand — 'fokus' ist dabei der eigentliche Dichte-Hebel: eine
  // Aufgabe, ein Knoten, keine Nebenflaechen.
  const [viewMode, setViewMode] = useState<FlowSpineViewMode>('flow')
  const showNodeDetails = viewMode !== 'uebersicht'
  const showSideFlaechen = viewMode === 'flow'

  // FSX-023: Die Copilot-Spalte stand doppelt zur Mitte und beanspruchte 360 px
  // dauerhaft. Sie bleibt erreichbar, aber eingeklappt, bis jemand sie braucht.
  const [copilotOpen, setCopilotOpen] = useState(false)

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
        return
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
      setNewInstanceCustomer(null)
      const baseHref = startConfig.buildHref(created)
      const hrefWithCustomer =
        processKey === 'order-to-cash' && newInstanceCustomer
          ? `${baseHref}${baseHref.includes('?') ? '&' : '?'}customerId=${encodeURIComponent(newInstanceCustomer.id)}&customerNumber=${encodeURIComponent(newInstanceCustomer.customer_number)}`
          : baseHref
      go(hrefWithCustomer)
    } catch (e) {
      console.error('Create instance failed:', e)
      toast({
        title: 'Fehler',
        description: 'Instanz konnte nicht erstellt werden.',
        variant: 'destructive',
      })
    }
  }

  const openLifecycleDialog = (mode: LifecycleDialogMode) => {
    setLifecycleDialog({
      mode,
      reasonCategory: '',
      reasonCode: '',
      reasonNote: '',
      businessStatus: workspace?.business_status ?? '',
      blockedUntil: '',
    })
  }

  const closeLifecycleDialog = () => setLifecycleDialog(null)

  const handleSaveLifecycle = async (): Promise<void> => {
    if (!instanceId) return
    try {
      await saveInstance.mutateAsync({
        resume_node_id: selectedNode?.id,
        resume_route: `${location.pathname}?instanceId=${instanceId}`,
        resume_payload: {
          selectedNodeId: selectedNode?.id,
          processKey,
          title: workspace?.title,
        },
        business_status: workspace?.business_status,
        action_label: 'Arbeitsstand gespeichert',
      })
      toast({ title: 'Arbeitsstand gespeichert', description: 'Resume-Kontext wurde aktualisiert.' })
    } catch (e) {
      console.error('Save lifecycle failed:', e)
      toast({
        title: 'Fehler',
        description: 'Arbeitsstand konnte nicht gespeichert werden.',
        variant: 'destructive',
      })
    }
  }

  const handleResumeLifecycle = async (): Promise<void> => {
    if (!instanceId) return
    try {
      const result = await resumeInstance.mutateAsync({ action_label: 'Vorgang wieder aufgenommen' })
      toast({ title: 'Vorgang wieder aufgenommen', description: result.case_number })
      const targetRoute = result.resume_target?.route
      if (targetRoute) {
        navigate(targetRoute)
      }
    } catch (e) {
      console.error('Resume lifecycle failed:', e)
      toast({
        title: 'Fehler',
        description: 'Vorgang konnte nicht wieder aufgenommen werden.',
        variant: 'destructive',
      })
    }
  }

  const handleSubmitLifecycleDialog = async (): Promise<void> => {
    if (!instanceId || !lifecycleDialog) return
    const payload: FlowSpineLifecycleActionPayload = {
      node_id: selectedNode?.id,
      business_status: lifecycleDialog.businessStatus.trim() || undefined,
      reason_category: lifecycleDialog.reasonCategory || undefined,
      reason_code: lifecycleDialog.reasonCode.trim() || undefined,
      reason_note: lifecycleDialog.reasonNote.trim() || undefined,
      blocked_until: lifecycleDialog.blockedUntil || undefined,
    }

    const mutationByMode = {
      hold: holdInstance,
      complete: completeInstance,
      cancel: cancelInstance,
      fail: failInstance,
    } as const

    const titleByMode: Record<LifecycleDialogMode, string> = {
      hold: 'Vorgang pausiert',
      complete: 'Vorgang abgeschlossen',
      cancel: 'Vorgang abgebrochen',
      fail: 'Vorgang als gescheitert markiert',
    }

    try {
      await mutationByMode[lifecycleDialog.mode].mutateAsync(payload)
      toast({ title: titleByMode[lifecycleDialog.mode], description: workspace?.case_number || workspace?.instance_label })
      closeLifecycleDialog()
    } catch (_rawErr: unknown) {
      const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      console.error('Lifecycle action failed:', e)
      toast({
        title: 'Fehler',
        description: e?.response?.data?.detail || 'Lifecycle-Aktion konnte nicht ausgefuehrt werden.',
        variant: 'destructive',
      })
    }
  }

  return { processKey, instanceId, navigate, location, startConfig, workspaceQuery, workspace, nodes, selectedNode, processNavItems, viewMode, setViewMode, showNodeDetails, showSideFlaechen, copilotOpen, setCopilotOpen, progressWidth, go, handleAction, handleAgentAction, handleCreateInstance, openLifecycleDialog, closeLifecycleDialog, handleSaveLifecycle, handleResumeLifecycle, handleSubmitLifecycleDialog, setSelectedNodeId, showNewInstanceDialog, setShowNewInstanceDialog, newInstanceLabel, setNewInstanceLabel, newInstancePartnerName, setNewInstancePartnerName, newInstanceSubject, setNewInstanceSubject, newInstanceEntryMode, setNewInstanceEntryMode, newInstanceCustomer, setNewInstanceCustomer, showAdvancedCustomerSearch, setShowAdvancedCustomerSearch, createInstance, executeAction, executeAgentAction, instanceSearch, setInstanceSearch, instancesQuery, timelineQuery, saveInstance, resumeInstance, holdInstance, completeInstance, cancelInstance, failInstance, lifecycleDialog, setLifecycleDialog }
}
export type FlowSpineWorkspaceRuntime = ReturnType<typeof useFlowSpineWorkspaceRuntime>
