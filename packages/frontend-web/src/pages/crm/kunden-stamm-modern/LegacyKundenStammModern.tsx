import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { convertL3MaskToMaskConfig, l3MaskConfig, type L3MaskConfig } from '@/components/mask-builder/adapters/l3-mask-adapter'
import { ObjectPage } from '@/components/mask-builder'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { useCreateCustomer, useCustomers, type Customer } from '@/lib/api/crm'
import { summarizeCustomerOperations } from '@/lib/domain-depth'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import {
  AlertTriangle,
  Brain,
  FileText,
  Shield,
  Sparkles,
  Smartphone,
  Users,
  Wand2,
  Zap,
} from 'lucide-react'

type ResponsiveMode = 'sm' | 'md' | 'lg'
type FocusPanel = 'intent' | 'duplicates' | 'knowledge'

type CustomerFormState = Record<string, string>

function normalize(value: string | undefined): string {
  return (value ?? '').trim().toLowerCase()
}

function buildKnowledgeSummary(data: CustomerFormState, duplicateCount: number): Array<{ label: string; value: string }> {
  const primaryName = data['party.name.primary'] || 'Unbenannter Kunde'
  const segment = data['customer.abc_class'] || 'nicht klassifiziert'
  const group = data['customer.customer_group'] || 'keine Gruppe'
  const accountManager = data['customer.account_manager'] || 'nicht zugewiesen'
  const channel = data['contact.email']
    ? 'E-Mail vorhanden'
    : data['contact.phone_primary']
      ? 'Telefonischer Kontakt'
      : 'Kontaktkanal offen'

  return [
    { label: 'Kundenbild', value: `${primaryName} / Segment ${segment} / Gruppe ${group}` },
    { label: 'Owner', value: accountManager },
    { label: 'Kontaktstatus', value: channel },
    { label: 'Dublettenlage', value: duplicateCount > 0 ? `${duplicateCount} aehnliche Datensaetze pruefen` : 'keine direkte Dublette gefunden' },
  ]
}

function buildNextActions(data: CustomerFormState, duplicates: Customer[]): Array<{ label: string; target: string; reason: string }> {
  const actions: Array<{ label: string; target: string; reason: string }> = []
  if (duplicates.length > 0) {
    actions.push({ label: 'Dublette klaeren', target: '/crm/customers', reason: 'Aehnliche Datensaetze sollten vor dem Speichern geprueft werden.' })
  }
  if (!data['contact.email'] && !data['contact.phone_primary']) {
    actions.push({ label: 'Kontaktdaten vervollstaendigen', target: '/crm/customers', reason: 'Es fehlt ein belastbarer Kontaktkanal fuer Folgeprozesse.' })
  }
  if (!data['customer.account_manager']) {
    actions.push({ label: 'Verantwortung zuweisen', target: '/crm/customers', reason: 'Owner fehlt fuer Vertrieb, Service und Dokumentfreigaben.' })
  }
  if (!data['tax.vat_id']) {
    actions.push({ label: 'Steuerdaten pruefen', target: '/admin/compliance-dashboard', reason: 'USt-ID fehlt oder muss noch validiert werden.' })
  }
  if (actions.length === 0) {
    actions.push({ label: 'Dokumentenpfad starten', target: '/dokumente/ablage', reason: 'Stammdaten sind belastbar und koennen in Vorgangs- und Dokumentraeume uebergehen.' })
  }
  return actions
}

function mapFormStateToCustomerPayload(data: CustomerFormState) {
  const companyName = data['party.name.primary']?.trim() || 'Neuer Kunde'
  return {
    business_partner_id: null,
    customer_number: `CRM-${Date.now().toString().slice(-6)}`,
    name: companyName,
    company_name: companyName,
    email: data['contact.email']?.trim() || undefined,
    phone: data['contact.phone_primary']?.trim() || undefined,
    address: [
      data['address.main.street']?.trim(),
      [data['address.main.postcode']?.trim(), data['address.main.city']?.trim()].filter(Boolean).join(' '),
      data['address.main.country']?.trim(),
    ]
      .filter(Boolean)
      .join(', ') || undefined,
    tax_id: data['tax.vat_id']?.trim() || data['tax.tax_number']?.trim() || undefined,
    credit_limit: 0,
    payment_terms: 30,
    is_active: data['customer.status'] !== 'inactive',
  }
}

function LegacyKundenStammModern(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const intentRef = useRef<HTMLDivElement | null>(null)
  const [maskConfig] = useState(convertL3MaskToMaskConfig())
  const l3Config = l3MaskConfig as unknown as L3MaskConfig
  const [aiEnabled] = useState(l3Config.ai?.enabled || false)
  const [responsiveMode, setResponsiveMode] = useState<ResponsiveMode>('lg')
  const [activePanel, setActivePanel] = useState<FocusPanel>('intent')

  const [customerData, setCustomerData] = useState<CustomerFormState>({
    'party.name.primary': '',
    'party.name.additional1': '',
    'party.name.additional2': '',
    'contact.salutation': '',
    'contact.letter_salutation': '',
    'contact.phone_primary': '',
    'contact.phone_secondary': '',
    'contact.email': '',
    'contact.homepage': '',
    'address.main.street': '',
    'address.main.postcode': '',
    'address.main.city': '',
    'address.main.country': 'DE',
    'tax.vat_id': '',
    'tax.tax_number': '',
    'customer.status': 'active',
    'customer.account_manager': '',
    'customer.abc_class': '',
    'customer.customer_group': '',
  })

  const customerSearch = customerData['party.name.primary']?.trim() || customerData['contact.email']?.trim() || undefined
  const customersQuery = useCustomers({ search: customerSearch, is_active: true })
  const createCustomer = useCreateCustomer()

  const duplicateCandidates = useMemo(() => {
    const items = customersQuery.data.items ?? []
    const name = normalize(customerData['party.name.primary'])
    const email = normalize(customerData['contact.email'])
    const phone = normalize(customerData['contact.phone_primary'])
    return items.filter((item) => {
      const itemName = normalize(item.name)
      const itemEmail = normalize(item.email)
      const itemPhone = normalize(item.phone)
      return Boolean(
        (name && itemName.includes(name)) ||
          (email && itemEmail === email) ||
          (phone && itemPhone === phone),
      )
    }).slice(0, 5)
  }, [customerData, customersQuery.data.items])

  const knowledgeSummary = useMemo(
    () => buildKnowledgeSummary(customerData, duplicateCandidates.length),
    [customerData, duplicateCandidates.length],
  )
  const nextActions = useMemo(
    () => buildNextActions(customerData, duplicateCandidates),
    [customerData, duplicateCandidates],
  )
  const customerOps = useMemo(
    () =>
      summarizeCustomerOperations({
        duplicateCount: duplicateCandidates.length,
        hasOwner: Boolean(customerData['customer.account_manager']),
        hasReachableContact: Boolean(customerData['contact.email'] || customerData['contact.phone_primary']),
        nextActions: nextActions.length,
      }),
    [customerData, duplicateCandidates.length, nextActions.length],
  )

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth
      if (width < 640) setResponsiveMode('sm')
      else if (width < 1024) setResponsiveMode('md')
      else setResponsiveMode('lg')
    }
    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        setActivePanel('intent')
        intentRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const handleIntentAction = async (actionId: string) => {
    switch (actionId) {
      case 'gen_letter_salutation': {
        const salutation = customerData['contact.salutation'] || 'Herr/Frau'
        const name = customerData['party.name.primary'] || ''
        setCustomerData((prev) => ({
          ...prev,
          'contact.letter_salutation': `${salutation} ${name}`.trim(),
        }))
        setActivePanel('intent')
        break
      }
      case 'validate_vat': {
        const vatId = customerData['tax.vat_id']
        if (!vatId) {
          toast({ title: 'Keine USt-ID', description: 'Bitte zuerst eine USt-ID erfassen.', variant: 'destructive' })
          return
        }
        try {
          const res = await apiClient.get<{ valid: boolean; error?: string }>(`/api/v1/vies/validate/${encodeURIComponent(vatId)}`)
          const result = res.data
          toast({
            title: result.valid ? 'USt-ID gueltig' : 'USt-ID ungueltig',
            description: result.valid ? `USt-ID ${vatId} wurde validiert.` : result.error || 'Validierung fehlgeschlagen.',
            variant: result.valid ? 'default' : 'destructive',
          })
        } catch {
          toast({ title: 'Validierung fehlgeschlagen', description: 'VIES-Pruefung war nicht erreichbar.', variant: 'destructive' })
        }
        break
      }
      case 'detect_duplicates':
        setActivePanel('duplicates')
        toast({
          title: 'Dublettenpruefung aktualisiert',
          description: duplicateCandidates.length > 0 ? `${duplicateCandidates.length} aehnliche Datensaetze gefunden.` : 'Keine direkten Dubletten gefunden.',
        })
        break
      case 'summarize_customer':
        setActivePanel('knowledge')
        toast({ title: 'Kundenkontext verdichtet', description: 'Wissens- und Naechste-Aktion-Sicht wurde aktualisiert.' })
        break
      default:
        break
    }
  }

  const saveCustomer = async () => {
    await createCustomer.mutateAsync(mapFormStateToCustomerPayload(customerData))
    toast({ title: 'Gespeichert', description: 'Kundendaten wurden als CRM-Datensatz angelegt.' })
    navigate('/crm/customers')
  }

  const operationalStatus = normalizeOperationalStatus(customerOps.ownershipRisk)

  return (
    <div className="container mx-auto space-y-6 p-6">
      <OperationalCaseHeader
        title="Kunden-Stamm"
        status={operationalStatus}
        blocker={duplicateCandidates.length > 0 ? `${duplicateCandidates.length} Dublettenkandidat(en)` : null}
        nextAction={customerOps.nextAction}
        caseLabel="CRM"
      />
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Kunden-Stamm Modern</h1>
          <p className="text-muted-foreground">Mask Builder, CRM-Assistenz und professionelle Folgewege in einem Arbeitsplatz.</p>
        </div>
        <div className="flex gap-2">
          {aiEnabled && (
            <Badge variant="secondary" className="gap-2">
              <Sparkles className="h-4 w-4" />
              AI aktiviert
            </Badge>
          )}
          <Badge variant="outline" className="gap-1">
            <Smartphone className="h-4 w-4" />
            {responsiveMode.toUpperCase()}
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-sm font-medium"><Zap className="h-4 w-4 text-yellow-500" />Responsive UI</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            {responsiveMode === 'sm' && 'Mobile: 1 Spalte, schnelle Folgeaktionen.'}
            {responsiveMode === 'md' && 'Tablet: 2 Spalten, Assistenz und Dubletten nebeneinander.'}
            {responsiveMode === 'lg' && 'Desktop: voller CRM-Arbeitsplatz mit Seitenpanel.'}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-sm font-medium"><Wand2 className="h-4 w-4 text-purple-500" />AI-Assistenz</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">Briefanrede, Dublettencheck und Wissensverdichtung liegen direkt am Stamm.</CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-sm font-medium"><Shield className="h-4 w-4 text-green-500" />Validierung</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">USt-ID, Ownership und Pflichtdaten lassen sich vor Folgeprozessen absichern.</CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-sm font-medium"><Users className="h-4 w-4 text-blue-500" />Folgewege</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">Dokumente, Service und Vertrieb sind als naechste Aktionen schon am Kunden sichtbar.</CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Ownership-Risiko</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-lg font-semibold">{customerOps.ownershipRisk}</div>
            <div className="mt-1 text-sm text-muted-foreground">Dubletten, Owner und Kontaktkanal werden als gemeinsamer Arbeitszustand bewertet.</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Naechste Aktion</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm font-semibold">{customerOps.nextAction}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Folgeobjekte bereit</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-lg font-semibold">{nextActions.length}</div>
            <div className="mt-1 text-sm text-muted-foreground">Vertrieb, Service, Dokumente und Compliance sind direkt ansteuerbar.</div>
          </CardContent>
        </Card>
      </div>

      {aiEnabled && (
        <Card ref={intentRef}>
          <CardHeader>
            <CardTitle className="text-sm font-medium">AI-Schnellaktionen</CardTitle>
            <CardDescription>⌘/Ctrl+K springt hierher. Aktionen schalten den passenden Assistenzraum frei.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {(l3Config.ai?.intentBar?.actions ?? []).map((action) => (
              <Button key={action.id} variant={activePanel === 'intent' && action.id === 'gen_letter_salutation' ? 'default' : 'outline'} size="sm" onClick={() => void handleIntentAction(action.id)}>
                {action.label}
              </Button>
            ))}
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">
        <Card>
          <CardHeader>
            <CardTitle>{maskConfig.title}</CardTitle>
            <CardDescription>{maskConfig.subtitle}</CardDescription>
          </CardHeader>
          <CardContent>
            <ObjectPage
              config={maskConfig}
              data={customerData}
              onChange={(data) => setCustomerData(data as CustomerFormState)}
              onSave={saveCustomer}
              onCancel={() => navigate('/crm/customers')}
            />
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card className={activePanel === 'duplicates' ? 'ring-2 ring-primary/40' : undefined}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base"><AlertTriangle className="h-4 w-4" />Dublettensicht</CardTitle>
              <CardDescription>Aktive CRM-Datensaetze mit gleichem Namen, Kontakt oder E-Mail.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {duplicateCandidates.length === 0 ? (
                <p className="text-sm text-muted-foreground">Keine direkten Dubletten gefunden.</p>
              ) : (
                duplicateCandidates.map((item) => (
                  <div key={item.id} className="rounded border p-3 text-sm">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="font-medium">{item.name}</div>
                        <div className="text-muted-foreground">{item.customer_number}</div>
                      </div>
                      <Badge variant="outline">{item.analytics?.segment ?? 'offen'}</Badge>
                    </div>
                    <div className="mt-2 text-muted-foreground">{item.email || item.phone || 'Kein Kontaktkanal'}</div>
                  </div>
                ))
              )}
              <Button variant="outline" className="w-full" onClick={() => navigate('/crm/customers')}>
                Dubletten im CRM pruefen
              </Button>
            </CardContent>
          </Card>

          <Card className={activePanel === 'knowledge' ? 'ring-2 ring-primary/40' : undefined}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base"><Brain className="h-4 w-4" />Wissenspanel</CardTitle>
              <CardDescription>Verdichteter Kundenkontext fuer Vertrieb, Service und Dokumentpfade.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {knowledgeSummary.map((entry) => (
                <div key={entry.label}>
                  <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{entry.label}</div>
                  <div className="text-sm">{entry.value}</div>
                </div>
              ))}
              <Separator />
              <div className="space-y-2">
                <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Naechste Aktionen</div>
                {nextActions.map((action) => (
                  <button
                    key={action.label}
                    type="button"
                    onClick={() => navigate(action.target)}
                    className="w-full rounded border p-3 text-left transition-colors hover:bg-muted"
                  >
                    <div className="font-medium">{action.label}</div>
                    <div className="text-xs text-muted-foreground">{action.reason}</div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base"><FileText className="h-4 w-4" />Folgepfade</CardTitle>
              <CardDescription>Direkte Anschlussstellen in Dokumente, Service und Vertrieb.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-2">
              <Button variant="outline" onClick={() => navigate('/dokumente/ablage')}>Dokumentraum oeffnen</Button>
              <Button variant="outline" onClick={() => navigate('/service/anfragen')}>Service-Faelle ansehen</Button>
              <Button variant="outline" onClick={() => navigate('/sales/angebote-liste')}>Angebote und Vertriebslage</Button>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={() => navigate('/crm/customers')}>Abbrechen</Button>
        <Button onClick={() => void saveCustomer()} disabled={createCustomer.isPending}>Speichern</Button>
      </div>
    </div>
  )
}

export default LegacyKundenStammModern
