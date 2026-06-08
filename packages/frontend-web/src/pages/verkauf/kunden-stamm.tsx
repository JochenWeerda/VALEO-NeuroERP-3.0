import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from '@/app/routing/react-router-compat'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/hooks/use-toast'
import { Copy, Save, User } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'
import {
  businessPartnerService,
  type Address,
  type AddressPayload,
  type BillingConfigPayload,
  type BusinessPartnerEnvelope,
  type CpdAccount,
  type CpdAccountPayload,
  type DiscountItem,
  type DiscountItemPayload,
  type PriceAgreement,
  type PriceAgreementPayload,
  type Instruction,
  type InstructionPayload,
  type BpContact,
  type BpContactPayload,
  EMPTY_TAB23_STAMMDATEN,
  type Tab23Stammdaten,
} from '@/lib/services/business-partner-service'
import { getAxiosErrorMessage } from '@/lib/api-client'

type KundeData = {
  id: string
  kundennummer: string
  name: string
  name_2: string
  land: string
  strasse: string
  hausnummer: string
  plz: string
  ort: string
  email: string
  telefon: string
  mobil: string
  fax: string
  website: string
  ust_id: string
  steuernummer: string
  zahlungsziel: string
  kreditlimit: number
  status: 'active' | 'inactive' | 'blocked'
  fax_blocked: boolean
  tab23: Tab23Stammdaten
}

type DiscountForm = {
  article_number: string
  description: string
  discount_percent: number
  valid_from: string
  valid_to: string
  discount_list_number: string
  source_type: '' | 'import' | 'batch' | 'internal'
}

type PriceAgreementForm = {
  article_number: string
  description: string
  valid_from: string
  valid_to: string
  price_net: number
  price_incl_freight: number
  price_unit: string
  discount_allowed: boolean
  special_freight: number
  payment_condition: string
  source_type: '' | 'import' | 'batch' | 'internal'
  operator_name: string
}

type AddressForm = {
  address_type: 'customer' | 'invoice' | 'shipping' | 'postal'
  name_1: string
  name_2: string
  name_3: string
  street: string
  house_number: string
  postal_code: string
  city: string
  country: string
  po_box: string
  po_box_postal_code: string
  po_box_city: string
  phone: string
  fax: string
  email: string
  website: string
  salutation: string
  brief_salutation: string
  free_field_1: string
  free_field_2: string
  free_field_3: string
  area_code: string
  is_default: boolean
}

type BillingConfigForm = {
  customer_group: string
  customer_type: '' | 'standard' | 'organ' | 'group_internal'
  account_statement_print: boolean
  account_statement_separate: boolean
  account_statement_reprint: boolean
  last_account_statement_number: number
  account_balance: number
  settlement_mode: '' | 'single' | 'collective'
  admin_overhead_surcharge_percent: number
  invoice_number_range: string
  bonus_eligible: boolean
  self_billing_sales: boolean
  self_billing_purchase: boolean
  vat_optimizer: boolean
}

type CpdForm = {
  cpd_customer_number: string
  debtor_account: string
  name_1: string
  street: string
  house_number: string
  postal_code: string
  city: string
  country: string
  phone_1: string
  email: string
  invoice_type: string
  collective_invoice: boolean
  invoice_form_template: string
  cash_discount_percent: number
  cash_discount_days: number
  payment_target_days: number
}

type DiscountFormErrors = Partial<Record<keyof DiscountForm, string>>
type PriceAgreementFormErrors = Partial<Record<keyof PriceAgreementForm, string>>

const DEFAULT_DISCOUNT_FORM: DiscountForm = {
  article_number: '',
  description: '',
  discount_percent: 0,
  valid_from: '',
  valid_to: '',
  discount_list_number: '',
  source_type: '',
}

const DEFAULT_PRICE_FORM: PriceAgreementForm = {
  article_number: '',
  description: '',
  valid_from: '',
  valid_to: '',
  price_net: 0,
  price_incl_freight: 0,
  price_unit: 't',
  discount_allowed: true,
  special_freight: 0,
  payment_condition: '',
  source_type: '',
  operator_name: '',
}

const DEFAULT_ADDRESS_FORM: AddressForm = {
  address_type: 'customer',
  name_1: '',
  name_2: '',
  name_3: '',
  street: '',
  house_number: '',
  postal_code: '',
  city: '',
  country: 'DE',
  po_box: '',
  po_box_postal_code: '',
  po_box_city: '',
  phone: '',
  fax: '',
  email: '',
  website: '',
  salutation: '',
  brief_salutation: '',
  free_field_1: '',
  free_field_2: '',
  free_field_3: '',
  area_code: '',
  is_default: false,
}

const DEFAULT_BILLING_FORM: BillingConfigForm = {
  customer_group: '',
  customer_type: '',
  account_statement_print: false,
  account_statement_separate: false,
  account_statement_reprint: false,
  last_account_statement_number: 0,
  account_balance: 0,
  settlement_mode: '',
  admin_overhead_surcharge_percent: 0,
  invoice_number_range: '',
  bonus_eligible: false,
  self_billing_sales: false,
  self_billing_purchase: false,
  vat_optimizer: false,
}

const DEFAULT_CPD_FORM: CpdForm = {
  cpd_customer_number: '',
  debtor_account: '',
  name_1: '',
  street: '',
  house_number: '',
  postal_code: '',
  city: '',
  country: 'DE',
  phone_1: '',
  email: '',
  invoice_type: '',
  collective_invoice: false,
  invoice_form_template: '',
  cash_discount_percent: 0,
  cash_discount_days: 0,
  payment_target_days: 0,
}

const DEFAULT_KUNDE: KundeData = {
  id: '',
  kundennummer: '',
  name: '',
  name_2: '',
  land: 'DE',
  strasse: '',
  hausnummer: '',
  plz: '',
  ort: '',
  email: '',
  telefon: '',
  mobil: '',
  fax: '',
  website: '',
  ust_id: '',
  steuernummer: '',
  zahlungsziel: '',
  kreditlimit: 0,
  status: 'active',
  fax_blocked: false,
  tab23: { ...EMPTY_TAB23_STAMMDATEN },
}

type InstructionFormState = {
  instruction_text: string
  instruction_priority: InstructionPayload['instruction_priority']
  valid_from: string
  valid_to: string
}

const DEFAULT_INSTRUCTION_FORM: InstructionFormState = {
  instruction_text: '',
  instruction_priority: 'normal',
  valid_from: '',
  valid_to: '',
}

const DEFAULT_CONTACT_FORM: BpContactPayload = {
  priority: 0,
  salutation: null,
  brief_salutation: null,
  title: null,
  first_name: null,
  last_name: '',
  position: null,
  department: null,
  phone_1: null,
  phone_2: null,
  mobile: null,
  email: null,
  street: null,
  postal_code: null,
  city: null,
  birth_date: null,
  hobbies: null,
  info_1: null,
  info_2: null,
  invoice_email_recipient: false,
  reminder_email_recipient: false,
  contact_type: 'other',
  cad_system: null,
  software_systems: [],
  is_data_protection_officer: false,
  created_by: 'ui',
  updated_by: 'ui',
}

function toInstructionPayload(form: InstructionFormState): InstructionPayload {
  return {
    instruction_text: form.instruction_text,
    instruction_priority: form.instruction_priority,
    valid_from: form.valid_from || null,
    valid_to: form.valid_to || null,
    created_by: 'ui',
    updated_by: 'ui',
  }
}

function instructionToForm(row: Instruction): InstructionFormState {
  return {
    instruction_text: row.instruction_text,
    instruction_priority: row.instruction_priority,
    valid_from: row.valid_from ? String(row.valid_from).slice(0, 10) : '',
    valid_to: row.valid_to ? String(row.valid_to).slice(0, 10) : '',
  }
}

function contactToFormPayload(c: BpContact): BpContactPayload {
  return {
    priority: c.priority,
    salutation: c.salutation ?? null,
    brief_salutation: c.brief_salutation ?? null,
    title: c.title ?? null,
    first_name: c.first_name ?? null,
    last_name: c.last_name,
    position: c.position ?? null,
    department: c.department ?? null,
    phone_1: c.phone_1 ?? null,
    phone_2: c.phone_2 ?? null,
    mobile: c.mobile ?? null,
    email: c.email ?? null,
    street: c.street ?? null,
    postal_code: c.postal_code ?? null,
    city: c.city ?? null,
    birth_date: c.birth_date ?? null,
    hobbies: c.hobbies ?? null,
    info_1: c.info_1 ?? null,
    info_2: c.info_2 ?? null,
    invoice_email_recipient: c.invoice_email_recipient,
    reminder_email_recipient: c.reminder_email_recipient,
    contact_type: c.contact_type,
    cad_system: c.cad_system ?? null,
    software_systems: c.software_systems ?? [],
    is_data_protection_officer: c.is_data_protection_officer,
    created_by: 'ui',
    updated_by: 'ui',
  }
}

function mergeTab23FromBp(bp: BusinessPartnerEnvelope['business_partner']): Tab23Stammdaten {
  const t: Tab23Stammdaten = { ...EMPTY_TAB23_STAMMDATEN }
  const raw = bp.legacy_customer_fields?.tab_23
  if (raw && typeof raw === 'object') {
    for (const key of Object.keys(EMPTY_TAB23_STAMMDATEN) as (keyof Tab23Stammdaten)[]) {
      const v = (raw as Record<string, unknown>)[key]
      if (v != null && String(v) !== '') t[key] = String(v)
    }
  }
  const leg = bp.legacy_customer_fields
  if (leg?.customer_group && !t.customer_group) t.customer_group = String(leg.customer_group)
  if (leg?.operation_number && !t.farm_operation_number) t.farm_operation_number = String(leg.operation_number)
  if (leg?.salutation && !t.salutation) t.salutation = String(leg.salutation)
  const mem = leg?.membership_entry_date
  if (mem && !t.customer_since) t.customer_since = String(mem).slice(0, 10)
  if (bp.core_identity.state && !t.federal_state) t.federal_state = String(bp.core_identity.state)
  const agr = bp.agrar_extension as { farm_number?: string | null }
  if (agr?.farm_number && !t.farm_operation_number) t.farm_operation_number = String(agr.farm_number)
  const gdpr = bp.gdpr as { contact_block_reason?: string | null }
  if (gdpr?.contact_block_reason && !t.block_reason) t.block_reason = String(gdpr.contact_block_reason)
  const m = bp.marketing_consent as { marketing_segment?: string | null }
  if (m?.marketing_segment && !t.abc_status) t.abc_status = String(m.marketing_segment)
  const log = bp.logistics as { loading_requirements?: string | null }
  if (log?.loading_requirements && !t.dispatcher) t.dispatcher = String(log.loading_requirements)
  if (bp.finance.debtor_account && !t.debtor_account) t.debtor_account = String(bp.finance.debtor_account)
  if (bp.finance.creditor_account && !t.main_account) t.main_account = String(bp.finance.creditor_account)
  return t
}

function toForm(envelope: BusinessPartnerEnvelope): KundeData {
  const bp = envelope.business_partner
  const leg = bp.legacy_customer_fields
  return {
    id: String(bp.core_identity.partner_id ?? ''),
    kundennummer: bp.core_identity.partner_number,
    name: bp.core_identity.name_1,
    name_2: String(bp.core_identity.name_2 ?? ''),
    land: String(bp.core_identity.country ?? 'DE'),
    strasse: String(bp.core_identity.street ?? ''),
    hausnummer: String(bp.core_identity.house_number ?? ''),
    plz: String(bp.core_identity.postal_code ?? ''),
    ort: String(bp.core_identity.city ?? ''),
    email: String(bp.contact_data.email ?? ''),
    telefon: String(bp.contact_data.phone ?? ''),
    mobil: String(bp.contact_data.mobile ?? ''),
    fax: String(bp.contact_data.fax ?? ''),
    website: String(bp.contact_data.website ?? ''),
    ust_id: String(bp.finance.vat_id ?? ''),
    steuernummer: String(bp.finance.tax_number ?? ''),
    zahlungsziel: String(bp.finance.payment_terms_id ?? ''),
    kreditlimit: Number(bp.finance.credit_limit ?? 0),
    status: bp.core_identity.status,
    fax_blocked: Boolean(leg?.fax_blocked),
    tab23: mergeTab23FromBp(bp),
  }
}

const DEFAULT_MARKETING_CONSENT: Record<string, unknown> = {
  email_opt_in: false,
  email_opt_in_timestamp: null,
  sms_opt_in: false,
  sms_opt_in_timestamp: null,
  whatsapp_opt_in: false,
  whatsapp_opt_in_timestamp: null,
  newsletter_opt_in: false,
  newsletter_language: null,
  flyer_subscription: false,
  flyer_delivery_type: null,
  marketing_segment: null,
}

const DEFAULT_GDPR: Record<string, unknown> = {
  privacy_policy_accepted: false,
  privacy_policy_version: null,
  privacy_policy_accepted_at: null,
  data_processing_agreement_signed: false,
  data_retention_until: null,
  contact_block_reason: null,
  anonymized_at: null,
}

const DEFAULT_AGRAR: Record<string, unknown> = {
  farm_number: null,
  eu_farm_id: null,
  harvest_year_default: null,
  qs_certificate_number: null,
  qs_valid_until: null,
  bio_certified: false,
  bio_certificate_valid_until: null,
  contract_group: null,
  default_silo_location: null,
}

const DEFAULT_LOGISTICS: Record<string, unknown> = {
  default_route_id: null,
  preferred_carrier_id: null,
  loading_requirements: null,
}

function mergePayload(form: KundeData, base: BusinessPartnerEnvelope | null): BusinessPartnerEnvelope {
  const b = base?.business_partner
  const legBase = (b?.legacy_customer_fields ?? {}) as Record<string, unknown>
  const legacy_customer_fields = {
    ...legBase,
    customer_group: form.tab23.customer_group || null,
    operation_number: form.tab23.farm_operation_number || null,
    fax_blocked: form.fax_blocked,
    salutation: form.tab23.salutation || null,
    membership_entry_date: form.tab23.customer_since || null,
    tab_23: {
      ...form.tab23,
      vat_id: form.ust_id,
      tax_number: form.steuernummer,
    },
  }
  const agrar = { ...DEFAULT_AGRAR, ...(typeof b?.agrar_extension === 'object' && b.agrar_extension ? b.agrar_extension : {}), farm_number: form.tab23.farm_operation_number || null }
  const logistics = { ...DEFAULT_LOGISTICS, ...(typeof b?.logistics === 'object' && b.logistics ? b.logistics : {}), loading_requirements: form.tab23.dispatcher || null }
  const marketing_consent = {
    ...DEFAULT_MARKETING_CONSENT,
    ...(typeof b?.marketing_consent === 'object' && b.marketing_consent ? b.marketing_consent : {}),
    marketing_segment: form.tab23.abc_status || null,
  }
  const gdpr = {
    ...DEFAULT_GDPR,
    ...(typeof b?.gdpr === 'object' && b.gdpr ? b.gdpr : {}),
    contact_block_reason: form.tab23.block_reason || null,
  }
  return {
    business_partner: {
      core_identity: {
        partner_id: form.id || undefined,
        partner_number: form.kundennummer,
        matchcode: form.name,
        name_1: form.name,
        name_2: form.name_2 || null,
        legal_form: b?.core_identity.legal_form ?? null,
        street: form.strasse || null,
        house_number: form.hausnummer || null,
        postal_code: form.plz || null,
        city: form.ort || null,
        country: form.land || 'DE',
        state: form.tab23.federal_state || null,
        language: b?.core_identity.language ?? 'de',
        status: form.status,
      },
      roles: b?.roles ?? {
        is_customer: true,
        is_supplier: false,
        is_carrier: false,
        is_employee: false,
        is_service_provider: false,
      },
      contact_data: {
        phone: form.telefon || null,
        mobile: form.mobil || null,
        email: form.email || null,
        website: form.website || null,
        fax: form.fax || null,
      },
      banking: b?.banking ?? {
        iban: null,
        bic: null,
        bank_name: null,
        sepa_mandate_reference: null,
        sepa_mandate_signed_at: null,
      },
      finance: {
        debtor_account: form.tab23.debtor_account || null,
        creditor_account: form.tab23.main_account || null,
        tax_number: form.steuernummer || null,
        vat_id: form.ust_id || null,
        tax_type: b?.finance.tax_type ?? 'standard',
        payment_terms_id: form.zahlungsziel || null,
        credit_limit: form.kreditlimit,
        dunning_level: b?.finance.dunning_level ?? 0,
        blocked_for_delivery: b?.finance.blocked_for_delivery ?? false,
        blocked_for_invoice: b?.finance.blocked_for_invoice ?? false,
      },
      agrar_extension: agrar,
      logistics,
      marketing_consent,
      gdpr,
      legacy_customer_fields,
      audit: {
        created_by: b?.audit.created_by ?? 'ui',
        updated_by: 'ui',
        created_at: b?.audit.created_at ?? null,
        updated_at: b?.audit.updated_at ?? null,
      },
    },
  }
}

function generateCustomerNumber(): string {
  const year = new Date().getFullYear()
  const seq = Date.now().toString(36).toUpperCase().slice(-4)
  return `K-${year}-${seq}`
}

export default function KundenStammPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams<{ id?: string }>()
  const [searchParams, setSearchParams] = useSearchParams()
  const { toast } = useToast()

  const isNew = !id || id === 'neu'
  const [kunde, setKunde] = useState<KundeData>(() => ({
    ...DEFAULT_KUNDE,
    kundennummer: generateCustomerNumber(),
  }))
  const partnerId = kunde.id || (isNew ? '' : String(id))
  const [editingDiscountId, setEditingDiscountId] = useState<string | null>(null)
  const [editingPriceId, setEditingPriceId] = useState<string | null>(null)
  const [discountForm, setDiscountForm] = useState<DiscountForm>(DEFAULT_DISCOUNT_FORM)
  const [priceForm, setPriceForm] = useState<PriceAgreementForm>(DEFAULT_PRICE_FORM)
  const [addressForm, setAddressForm] = useState<AddressForm>(DEFAULT_ADDRESS_FORM)
  const [billingForm, setBillingForm] = useState<BillingConfigForm>(DEFAULT_BILLING_FORM)
  const [cpdForm, setCpdForm] = useState<CpdForm>(DEFAULT_CPD_FORM)
  const [editingAddressId, setEditingAddressId] = useState<string | null>(null)
  const [editingCpdId, setEditingCpdId] = useState<string | null>(null)
  const [instructionForm, setInstructionForm] = useState<InstructionFormState>(DEFAULT_INSTRUCTION_FORM)
  const [editingInstructionId, setEditingInstructionId] = useState<string | null>(null)
  const [contactForm, setContactForm] = useState<BpContactPayload>(DEFAULT_CONTACT_FORM)
  const [editingContactId, setEditingContactId] = useState<string | null>(null)
  const [discountErrors, setDiscountErrors] = useState<DiscountFormErrors>({})
  const [priceErrors, setPriceErrors] = useState<PriceAgreementFormErrors>({})

  const detailQuery = useQuery({
    queryKey: ['business-partner', id],
    queryFn: async () => businessPartnerService.get(String(id)),
    enabled: !isNew,
  })

  const vorlageId = searchParams.get('vorlage')
  const vorlageQuery = useQuery({
    queryKey: ['business-partner-vorlage', vorlageId],
    queryFn: async () => businessPartnerService.get(String(vorlageId)),
    enabled: isNew && Boolean(vorlageId),
  })
  const vorlageAppliedRef = useRef(false)

  const initialName = searchParams.get('initialName') ?? ''
  const returnTo = searchParams.get('returnTo') ?? ''
  const initialNameAppliedRef = useRef(false)

  useEffect(() => {
    if (!isNew || !initialName || initialNameAppliedRef.current) return
    initialNameAppliedRef.current = true
    setKunde((p) => (p.name ? p : { ...p, name: initialName }))
  }, [isNew, initialName])

  useEffect(() => {
    if (!vorlageId) vorlageAppliedRef.current = false
  }, [vorlageId])

  useEffect(() => {
    if (detailQuery.data) {
      setKunde(toForm(detailQuery.data))
    }
  }, [detailQuery.data])

  useEffect(() => {
    if (!isNew || !vorlageId || !vorlageQuery.data || vorlageAppliedRef.current) return
    vorlageAppliedRef.current = true
    const merged = toForm(vorlageQuery.data)
    setKunde({
      ...merged,
      id: '',
      kundennummer: generateCustomerNumber(),
    })
    toast({
      title: 'Vorlage übernommen',
      description: 'Kundennummer wurde neu vergeben — Daten prüfen und speichern.',
    })
    setSearchParams(
      (p) => {
        p.delete('vorlage')
        return p
      },
      { replace: true },
    )
  }, [isNew, vorlageId, vorlageQuery.data, setSearchParams, toast])

  const discountItemsQuery = useQuery({
    queryKey: ['business-partner-discount-items', partnerId],
    queryFn: async () => businessPartnerService.listDiscountItems(partnerId),
    enabled: Boolean(partnerId),
  })

  const priceAgreementsQuery = useQuery({
    queryKey: ['business-partner-price-agreements', partnerId],
    queryFn: async () => businessPartnerService.listPriceAgreements(partnerId),
    enabled: Boolean(partnerId),
  })

  const addressesQuery = useQuery({
    queryKey: ['business-partner-addresses', partnerId],
    queryFn: async () => businessPartnerService.listAddresses(partnerId),
    enabled: Boolean(partnerId),
  })

  const billingConfigQuery = useQuery({
    queryKey: ['business-partner-billing-config', partnerId],
    queryFn: async () => {
      try {
        return await businessPartnerService.getBillingConfig(partnerId)
      } catch {
        return null
      }
    },
    enabled: Boolean(partnerId),
  })

  const cpdAccountsQuery = useQuery({
    queryKey: ['business-partner-cpd-accounts', partnerId],
    queryFn: async () => businessPartnerService.listCpdAccounts(partnerId),
    enabled: Boolean(partnerId),
  })

  const instructionsQuery = useQuery({
    queryKey: ['business-partner-instructions', partnerId],
    queryFn: async () => businessPartnerService.listInstructions(partnerId),
    enabled: Boolean(partnerId),
  })

  const contactsQuery = useQuery({
    queryKey: ['business-partner-contacts', partnerId],
    queryFn: async () => businessPartnerService.listContacts(partnerId),
    enabled: Boolean(partnerId),
  })

  useEffect(() => {
    if (!billingConfigQuery.data) return
    const bc = billingConfigQuery.data
    setBillingForm({
      customer_group: bc.customer_group ?? '',
      customer_type: (bc.customer_type ?? '') as BillingConfigForm['customer_type'],
      account_statement_print: bc.account_statement_print,
      account_statement_separate: bc.account_statement_separate,
      account_statement_reprint: bc.account_statement_reprint,
      last_account_statement_number: Number(bc.last_account_statement_number ?? 0),
      account_balance: Number(bc.account_balance ?? 0),
      settlement_mode: (bc.settlement_mode ?? '') as BillingConfigForm['settlement_mode'],
      admin_overhead_surcharge_percent: Number(bc.admin_overhead_surcharge_percent ?? 0),
      invoice_number_range: bc.invoice_number_range ?? '',
      bonus_eligible: bc.bonus_eligible,
      self_billing_sales: bc.self_billing_sales,
      self_billing_purchase: bc.self_billing_purchase,
      vat_optimizer: bc.vat_optimizer,
    })
  }, [billingConfigQuery.data])

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = mergePayload(kunde, isNew ? null : detailQuery.data ?? null)
      if (isNew) {
        return businessPartnerService.create(payload)
      }
      return businessPartnerService.update(String(id), payload)
    },
    onSuccess: (saved) => {
      const partnerId = saved.business_partner.core_identity.partner_id
      const partnerName = saved.business_partner.core_identity.name_1 ?? ''
      const partnerNumber = saved.business_partner.core_identity.partner_number ?? ''
      toast({
        title: 'Kunde gespeichert',
        description: `${partnerName} wurde gespeichert.`,
      })
      if (isNew && returnTo && partnerId) {
        const [path, existingQuery = ''] = returnTo.split('?')
        const params = new URLSearchParams(existingQuery)
        params.set('newCustomerId', partnerId)
        if (partnerName) params.set('newCustomerName', partnerName)
        if (partnerNumber) params.set('newCustomerNumber', partnerNumber)
        params.set('openNewInstance', '1')
        navigate(`${path}?${params.toString()}`, { replace: true })
        return
      }
      if (partnerId) {
        navigate(`/verkauf/kunde/${partnerId}`)
      }
    },
    onError: (error) => {
      toast({
        title: 'Fehler beim Speichern',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    },
  })

  const discountMutation = useMutation({
    mutationFn: async () => {
      if (!partnerId) throw new Error('Kunde zuerst speichern')
      const payload: DiscountItemPayload = {
        article_number: discountForm.article_number,
        description: discountForm.description || null,
        discount_percent: Number(discountForm.discount_percent || 0),
        valid_from: discountForm.valid_from || null,
        valid_to: discountForm.valid_to || null,
        discount_list_number: discountForm.discount_list_number || null,
        source_type: discountForm.source_type || null,
        updated_by: 'ui',
        created_by: 'ui',
      }
      if (editingDiscountId) {
        return businessPartnerService.updateDiscountItem(partnerId, editingDiscountId, payload)
      }
      return businessPartnerService.createDiscountItem(partnerId, payload)
    },
    onSuccess: () => {
      setDiscountForm(DEFAULT_DISCOUNT_FORM)
      setEditingDiscountId(null)
      setDiscountErrors({})
      void discountItemsQuery.refetch()
      toast({ title: 'Rabattliste gespeichert' })
    },
    onError: (error) => {
      toast({ title: 'Fehler bei Rabattliste', description: getAxiosErrorMessage(error), variant: 'destructive' })
    },
  })

  const deleteDiscountMutation = useMutation({
    mutationFn: async (itemId: string) => {
      if (!partnerId) throw new Error('Kunde zuerst speichern')
      return businessPartnerService.deleteDiscountItem(partnerId, itemId)
    },
    onSuccess: () => {
      void discountItemsQuery.refetch()
      toast({ title: 'Rabatt-Eintrag geloescht' })
    },
  })

  const instructionMutation = useMutation({
    mutationFn: async () => {
      if (!partnerId) throw new Error('Kunde zuerst speichern')
      const payload = toInstructionPayload(instructionForm)
      if (editingInstructionId) {
        return businessPartnerService.updateInstruction(partnerId, editingInstructionId, payload)
      }
      return businessPartnerService.createInstruction(partnerId, payload)
    },
    onSuccess: () => {
      setInstructionForm(DEFAULT_INSTRUCTION_FORM)
      setEditingInstructionId(null)
      void instructionsQuery.refetch()
      toast({ title: 'Chef-Anweisung gespeichert' })
    },
    onError: (error) => {
      toast({ title: 'Fehler Chef-Anweisung', description: getAxiosErrorMessage(error), variant: 'destructive' })
    },
  })

  const deleteInstructionMutation = useMutation({
    mutationFn: async (instructionId: string) => {
      if (!partnerId) throw new Error('Kunde zuerst speichern')
      return businessPartnerService.deleteInstruction(partnerId, instructionId)
    },
    onSuccess: () => {
      void instructionsQuery.refetch()
      toast({ title: 'Chef-Anweisung geloescht' })
    },
  })

  const contactMutation = useMutation({
    mutationFn: async () => {
      if (!partnerId) throw new Error('Kunde zuerst speichern')
      if (!contactForm.last_name?.trim()) throw new Error('Nachname ist erforderlich')
      if (editingContactId) {
        return businessPartnerService.updateContact(partnerId, editingContactId, contactForm)
      }
      return businessPartnerService.createContact(partnerId, contactForm)
    },
    onSuccess: () => {
      setContactForm(DEFAULT_CONTACT_FORM)
      setEditingContactId(null)
      void contactsQuery.refetch()
      toast({ title: 'Ansprechpartner gespeichert' })
    },
    onError: (error) => {
      toast({ title: 'Fehler Ansprechpartner', description: getAxiosErrorMessage(error), variant: 'destructive' })
    },
  })

  const deleteContactMutation = useMutation({
    mutationFn: async (contactId: string) => {
      if (!partnerId) throw new Error('Kunde zuerst speichern')
      return businessPartnerService.deleteContact(partnerId, contactId)
    },
    onSuccess: () => {
      void contactsQuery.refetch()
      toast({ title: 'Ansprechpartner geloescht' })
    },
  })

  const priceMutation = useMutation({
    mutationFn: async () => {
      if (!partnerId) throw new Error('Kunde zuerst speichern')
      const payload: PriceAgreementPayload = {
        article_number: priceForm.article_number,
        description: priceForm.description || null,
        valid_from: priceForm.valid_from || null,
        valid_to: priceForm.valid_to || null,
        price_net: Number(priceForm.price_net || 0),
        price_incl_freight: Number(priceForm.price_incl_freight || 0),
        price_unit: priceForm.price_unit || null,
        discount_allowed: priceForm.discount_allowed,
        special_freight: Number(priceForm.special_freight || 0),
        payment_condition: priceForm.payment_condition || null,
        source_type: priceForm.source_type || null,
        operator_name: priceForm.operator_name || null,
        operator_date: new Date().toISOString(),
        updated_by: 'ui',
        created_by: 'ui',
      }
      if (editingPriceId) {
        return businessPartnerService.updatePriceAgreement(partnerId, editingPriceId, payload)
      }
      return businessPartnerService.createPriceAgreement(partnerId, payload)
    },
    onSuccess: () => {
      setPriceForm(DEFAULT_PRICE_FORM)
      setEditingPriceId(null)
      setPriceErrors({})
      void priceAgreementsQuery.refetch()
      toast({ title: 'Preisvereinbarung gespeichert' })
    },
    onError: (error) => {
      toast({ title: 'Fehler bei Preisvereinbarung', description: getAxiosErrorMessage(error), variant: 'destructive' })
    },
  })

  const deletePriceMutation = useMutation({
    mutationFn: async (agreementId: string) => {
      if (!partnerId) throw new Error('Kunde zuerst speichern')
      return businessPartnerService.deletePriceAgreement(partnerId, agreementId)
    },
    onSuccess: () => {
      void priceAgreementsQuery.refetch()
      toast({ title: 'Preisvereinbarung geloescht' })
    },
  })

  const addressMutation = useMutation({
    mutationFn: async () => {
      if (!partnerId) throw new Error('Kunde zuerst speichern')
      const payload: AddressPayload = {
        address_type: addressForm.address_type,
        name_1: addressForm.name_1 || null,
        name_2: addressForm.name_2 || null,
        name_3: addressForm.name_3 || null,
        street: addressForm.street || null,
        house_number: addressForm.house_number || null,
        postal_code: addressForm.postal_code || null,
        city: addressForm.city || null,
        country: addressForm.country || null,
        po_box: addressForm.po_box || null,
        po_box_postal_code: addressForm.po_box_postal_code || null,
        po_box_city: addressForm.po_box_city || null,
        phone: addressForm.phone || null,
        fax: addressForm.fax || null,
        email: addressForm.email || null,
        website: addressForm.website || null,
        salutation: addressForm.salutation || null,
        brief_salutation: addressForm.brief_salutation || null,
        free_field_1: addressForm.free_field_1 || null,
        free_field_2: addressForm.free_field_2 || null,
        free_field_3: addressForm.free_field_3 || null,
        area_code: addressForm.area_code || null,
        is_default: addressForm.is_default,
        created_by: 'ui',
        updated_by: 'ui',
      }
      if (editingAddressId) {
        return businessPartnerService.updateAddress(partnerId, editingAddressId, payload)
      }
      return businessPartnerService.createAddress(partnerId, payload)
    },
    onSuccess: () => {
      setAddressForm(DEFAULT_ADDRESS_FORM)
      setEditingAddressId(null)
      void addressesQuery.refetch()
      toast({ title: 'Anschrift gespeichert' })
    },
  })

  const deleteAddressMutation = useMutation({
    mutationFn: async (addressId: string) => {
      if (!partnerId) throw new Error('Kunde zuerst speichern')
      return businessPartnerService.deleteAddress(partnerId, addressId)
    },
    onSuccess: () => {
      void addressesQuery.refetch()
      toast({ title: 'Anschrift geloescht' })
    },
  })

  const billingMutation = useMutation({
    mutationFn: async () => {
      if (!partnerId) throw new Error('Kunde zuerst speichern')
      const payload: BillingConfigPayload = {
        customer_group: billingForm.customer_group || null,
        customer_type: billingForm.customer_type || null,
        account_statement_print: billingForm.account_statement_print,
        account_statement_separate: billingForm.account_statement_separate,
        account_statement_reprint: billingForm.account_statement_reprint,
        last_account_statement_number: billingForm.last_account_statement_number,
        last_account_statement_date: null,
        account_balance: billingForm.account_balance,
        print_ad_text: false,
        shipping_expenses_enabled: false,
        settlement_mode: billingForm.settlement_mode || null,
        admin_overhead_surcharge_percent: billingForm.admin_overhead_surcharge_percent,
        invoice_number_range: billingForm.invoice_number_range || null,
        bonus_eligible: billingForm.bonus_eligible,
        self_billing_sales: billingForm.self_billing_sales,
        self_billing_purchase: billingForm.self_billing_purchase,
        remarkable_claim: false,
        vat_optimizer: billingForm.vat_optimizer,
        created_by: 'ui',
        updated_by: 'ui',
      }
      return businessPartnerService.putBillingConfig(partnerId, payload)
    },
    onSuccess: () => {
      void billingConfigQuery.refetch()
      toast({ title: 'Rechnung/Kontoauszug gespeichert' })
    },
  })

  const cpdMutation = useMutation({
    mutationFn: async () => {
      if (!partnerId) throw new Error('Kunde zuerst speichern')
      const payload: CpdAccountPayload = {
        ...cpdForm,
        search_term: cpdForm.name_1,
        name_2: null,
        name_3: null,
        po_box: null,
        po_box_city: null,
        phone_2: null,
        fax: null,
        salutation: null,
        brief_salutation: null,
        website: null,
        branch_office: null,
        cost_center: null,
        sales_representative: null,
        area_code: null,
        created_by: 'ui',
        updated_by: 'ui',
      }
      if (editingCpdId) {
        return businessPartnerService.updateCpdAccount(partnerId, editingCpdId, payload)
      }
      return businessPartnerService.createCpdAccount(partnerId, payload)
    },
    onSuccess: () => {
      setCpdForm(DEFAULT_CPD_FORM)
      setEditingCpdId(null)
      void cpdAccountsQuery.refetch()
      toast({ title: 'CPD-Konto gespeichert' })
    },
  })

  const deleteCpdMutation = useMutation({
    mutationFn: async (accountId: string) => {
      if (!partnerId) throw new Error('Kunde zuerst speichern')
      return businessPartnerService.deleteCpdAccount(partnerId, accountId)
    },
    onSuccess: () => {
      void cpdAccountsQuery.refetch()
      toast({ title: 'CPD-Konto geloescht' })
    },
  })

  const loadDiscountForEdit = (item: DiscountItem) => {
    setEditingDiscountId(item.id)
    setDiscountForm({
      article_number: item.article_number,
      description: item.description ?? '',
      discount_percent: Number(item.discount_percent ?? 0),
      valid_from: item.valid_from ? item.valid_from.slice(0, 10) : '',
      valid_to: item.valid_to ? item.valid_to.slice(0, 10) : '',
      discount_list_number: item.discount_list_number ?? '',
      source_type: (item.source_type as DiscountForm['source_type']) ?? '',
    })
  }

  const loadPriceForEdit = (agreement: PriceAgreement) => {
    setEditingPriceId(agreement.id)
    setPriceForm({
      article_number: agreement.article_number,
      description: agreement.description ?? '',
      valid_from: agreement.valid_from ? agreement.valid_from.slice(0, 10) : '',
      valid_to: agreement.valid_to ? agreement.valid_to.slice(0, 10) : '',
      price_net: Number(agreement.price_net ?? 0),
      price_incl_freight: Number(agreement.price_incl_freight ?? 0),
      price_unit: agreement.price_unit ?? 't',
      discount_allowed: agreement.discount_allowed,
      special_freight: Number(agreement.special_freight ?? 0),
      payment_condition: agreement.payment_condition ?? '',
      source_type: (agreement.source_type as PriceAgreementForm['source_type']) ?? '',
      operator_name: agreement.operator_name ?? '',
    })
  }

  const loadAddressForEdit = (item: Address) => {
    setEditingAddressId(item.id)
    setAddressForm({
      address_type: item.address_type,
      name_1: item.name_1 ?? '',
      name_2: item.name_2 ?? '',
      name_3: item.name_3 ?? '',
      street: item.street ?? '',
      house_number: item.house_number ?? '',
      postal_code: item.postal_code ?? '',
      city: item.city ?? '',
      country: item.country ?? 'DE',
      po_box: item.po_box ?? '',
      po_box_postal_code: item.po_box_postal_code ?? '',
      po_box_city: item.po_box_city ?? '',
      phone: item.phone ?? '',
      fax: item.fax ?? '',
      email: item.email ?? '',
      website: item.website ?? '',
      salutation: item.salutation ?? '',
      brief_salutation: item.brief_salutation ?? '',
      free_field_1: item.free_field_1 ?? '',
      free_field_2: item.free_field_2 ?? '',
      free_field_3: item.free_field_3 ?? '',
      area_code: item.area_code ?? '',
      is_default: item.is_default,
    })
  }

  const loadCpdForEdit = (item: CpdAccount) => {
    setEditingCpdId(item.id)
    setCpdForm({
      cpd_customer_number: item.cpd_customer_number,
      debtor_account: item.debtor_account ?? '',
      name_1: item.name_1,
      street: item.street ?? '',
      house_number: item.house_number ?? '',
      postal_code: item.postal_code ?? '',
      city: item.city ?? '',
      country: item.country ?? 'DE',
      phone_1: item.phone_1 ?? '',
      email: item.email ?? '',
      invoice_type: item.invoice_type ?? '',
      collective_invoice: item.collective_invoice,
      invoice_form_template: item.invoice_form_template ?? '',
      cash_discount_percent: Number(item.cash_discount_percent ?? 0),
      cash_discount_days: Number(item.cash_discount_days ?? 0),
      payment_target_days: Number(item.payment_target_days ?? 0),
    })
  }

  const validateDiscountForm = (form: DiscountForm): DiscountFormErrors => {
    const errors: DiscountFormErrors = {}
    if (!form.article_number.trim()) errors.article_number = 'Artikel-Nr. ist erforderlich.'
    if (Number.isNaN(form.discount_percent) || form.discount_percent < 0 || form.discount_percent > 100) {
      errors.discount_percent = 'Rabatt muss zwischen 0 und 100 liegen.'
    }
    if (form.valid_from && form.valid_to && form.valid_to < form.valid_from) {
      errors.valid_to = 'Gueltig bis darf nicht vor Gueltig ab liegen.'
    }
    return errors
  }

  const validatePriceForm = (form: PriceAgreementForm): PriceAgreementFormErrors => {
    const errors: PriceAgreementFormErrors = {}
    if (!form.article_number.trim()) errors.article_number = 'Artikel-Nr. ist erforderlich.'
    if (!form.price_unit.trim()) errors.price_unit = 'Einheit ist erforderlich.'
    if (Number.isNaN(form.price_net) || form.price_net < 0) errors.price_net = 'Preis netto darf nicht negativ sein.'
    if (Number.isNaN(form.price_incl_freight) || form.price_incl_freight < 0) errors.price_incl_freight = 'Preis inkl. Fracht darf nicht negativ sein.'
    if (Number.isNaN(form.special_freight) || form.special_freight < 0) errors.special_freight = 'Sonderfracht darf nicht negativ sein.'
    if (form.valid_from && form.valid_to && form.valid_to < form.valid_from) {
      errors.valid_to = 'Gueltig bis darf nicht vor Gueltig ab liegen.'
    }
    return errors
  }

  const statusBadge = useMemo(() => {
    if (kunde.status === 'active') {
      return { label: 'Aktiv', variant: 'outline' as const }
    }
    if (kunde.status === 'inactive') {
      return { label: 'Inaktiv', variant: 'secondary' as const }
    }
    return { label: 'Gesperrt', variant: 'destructive' as const }
  }, [kunde.status])

  if (detailQuery.isError) {
    return <ErrorState error={detailQuery.error as Error} onRetry={() => { void detailQuery.refetch() }} />
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <User className="h-8 w-8" />
            <div>
              <h1 className="text-3xl font-bold">{kunde.name || 'Neuer Kunde'}</h1>
              <p className="text-muted-foreground">Kundennummer: {kunde.kundennummer}</p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          {!isNew && kunde.id ? (
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate(`/verkauf/kunde/neu?vorlage=${encodeURIComponent(kunde.id)}`)}
              disabled={saveMutation.isPending}
            >
              <Copy className="h-4 w-4 mr-2" />
              Als Vorlage für Neuanlage
            </Button>
          ) : null}
          <Button variant="outline" onClick={() => navigate('/verkauf/kunden-liste')} disabled={saveMutation.isPending}>
            Zurueck
          </Button>
          <Button
            className="gap-2"
            onClick={() => {
              void saveMutation.mutateAsync()
            }}
            disabled={saveMutation.isPending || detailQuery.isLoading}
          >
            <Save className="h-4 w-4" />
            {saveMutation.isPending ? 'Speichere...' : 'Speichern'}
          </Button>
        </div>
      </div>

      <Tabs defaultValue="stammdaten">
        <TabsList>
          <TabsTrigger value="stammdaten">Stammdaten</TabsTrigger>
          <TabsTrigger value="konditionen">Konditionen</TabsTrigger>
          <TabsTrigger value="tab21">Chef-Anweisung</TabsTrigger>
          <TabsTrigger value="tab22">Ansprechpartner</TabsTrigger>
          <TabsTrigger value="tab23">Tab 23 Anschriften</TabsTrigger>
          <TabsTrigger value="tab24">Tab 24 Rechnung/Kontoauszug</TabsTrigger>
          <TabsTrigger value="tab25">Tab 25 CPD-Konto</TabsTrigger>
          <TabsTrigger value="rabatte">Rabatt-Listen</TabsTrigger>
          <TabsTrigger value="preise">Preisvereinbarungen</TabsTrigger>
          <TabsTrigger value="historie">Historie</TabsTrigger>
        </TabsList>

        <TabsContent value="stammdaten">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Unternehmensdaten</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Firmenname (Zeile 1)</Label>
                  <Input value={kunde.name} onChange={(e) => setKunde((prev) => ({ ...prev, name: e.target.value }))} />
                </div>
                <div>
                  <Label>Name Zeile 2</Label>
                  <Input value={kunde.name_2} onChange={(e) => setKunde((prev) => ({ ...prev, name_2: e.target.value }))} />
                </div>
                <div>
                  <Label>Name Zeile 3 (Tab 23)</Label>
                  <Input
                    value={kunde.tab23.name_3}
                    onChange={(e) =>
                      setKunde((prev) => ({ ...prev, tab23: { ...prev.tab23, name_3: e.target.value } }))
                    }
                  />
                </div>
                <div>
                  <Label>Status</Label>
                  <div className="mt-2">
                    <Badge variant={statusBadge.variant}>{statusBadge.label}</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Adresse und Kontakt</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 grid-cols-4">
                  <div className="col-span-3">
                    <Label>Strasse</Label>
                    <Input value={kunde.strasse} onChange={(e) => setKunde((prev) => ({ ...prev, strasse: e.target.value }))} />
                  </div>
                  <div className="col-span-1">
                    <Label>Nr.</Label>
                    <Input
                      value={kunde.hausnummer}
                      onChange={(e) => setKunde((prev) => ({ ...prev, hausnummer: e.target.value }))}
                    />
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <Label>PLZ</Label>
                    <Input value={kunde.plz} onChange={(e) => setKunde((prev) => ({ ...prev, plz: e.target.value }))} />
                  </div>
                  <div>
                    <Label>Ort</Label>
                    <Input value={kunde.ort} onChange={(e) => setKunde((prev) => ({ ...prev, ort: e.target.value }))} />
                  </div>
                  <div>
                    <Label>Land (ISO)</Label>
                    <Input value={kunde.land} onChange={(e) => setKunde((prev) => ({ ...prev, land: e.target.value }))} />
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label>Anrede (Tab 23)</Label>
                    <Input
                      value={kunde.tab23.salutation}
                      onChange={(e) =>
                        setKunde((prev) => ({ ...prev, tab23: { ...prev.tab23, salutation: e.target.value } }))
                      }
                    />
                  </div>
                  <div>
                    <Label>Briefanrede (Tab 23)</Label>
                    <Input
                      value={kunde.tab23.brief_salutation}
                      onChange={(e) =>
                        setKunde((prev) => ({ ...prev, tab23: { ...prev.tab23, brief_salutation: e.target.value } }))
                      }
                    />
                  </div>
                </div>
                <div>
                  <Label>E-Mail</Label>
                  <Input value={kunde.email} onChange={(e) => setKunde((prev) => ({ ...prev, email: e.target.value }))} />
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label>Telefon</Label>
                    <Input value={kunde.telefon} onChange={(e) => setKunde((prev) => ({ ...prev, telefon: e.target.value }))} />
                  </div>
                  <div>
                    <Label>Mobil</Label>
                    <Input value={kunde.mobil} onChange={(e) => setKunde((prev) => ({ ...prev, mobil: e.target.value }))} />
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label>Fax</Label>
                    <Input value={kunde.fax} onChange={(e) => setKunde((prev) => ({ ...prev, fax: e.target.value }))} />
                  </div>
                  <div>
                    <Label>Web</Label>
                    <Input value={kunde.website} onChange={(e) => setKunde((prev) => ({ ...prev, website: e.target.value }))} />
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <Label>Postfach</Label>
                    <Input
                      value={kunde.tab23.po_box}
                      onChange={(e) =>
                        setKunde((prev) => ({ ...prev, tab23: { ...prev.tab23, po_box: e.target.value } }))
                      }
                    />
                  </div>
                  <div>
                    <Label>Postfach-PLZ</Label>
                    <Input
                      value={kunde.tab23.po_box_postal_code}
                      onChange={(e) =>
                        setKunde((prev) => ({ ...prev, tab23: { ...prev.tab23, po_box_postal_code: e.target.value } }))
                      }
                    />
                  </div>
                  <div>
                    <Label>Postfach-Ort</Label>
                    <Input
                      value={kunde.tab23.po_box_city}
                      onChange={(e) =>
                        setKunde((prev) => ({ ...prev, tab23: { ...prev.tab23, po_box_city: e.target.value } }))
                      }
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card className="mt-6 border-dashed border-primary/30">
            <CardHeader>
              <CardTitle>Tab 23 — Klassifikation, Konten, Freifelder</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-3">
              {(
                [
                  ['region_code', 'Region / Gebietscode'],
                  ['state_name', 'Bundesland (Text)'],
                  ['federal_state', 'Bundesland (Kuerzel → Kernzustand)'],
                  ['customer_since', 'Kunde seit', 'date'],
                  ['debtor_account', 'Debitoren-Konto'],
                  ['main_account', 'Hauptkonto (Kreditor)'],
                  ['dispatcher', 'Disponent (Logistik-Hinweis)'],
                  ['sales_representative', 'Vertriebsbeauftragter'],
                  ['farm_operation_number', 'Betriebsnummer (Landwirtschaft)'],
                  ['customer_group', 'Kundengruppe'],
                  ['block_reason', 'Sperrgrund / Hinweis'],
                  ['info_4', 'Info-Feld 4'],
                  ['info_5', 'Info-Feld 5'],
                  ['info_6', 'Info-Feld 6'],
                  ['free_field_1', 'Freifeld 1'],
                  ['free_field_2', 'Freifeld 2'],
                  ['free_field_3', 'Freifeld 3'],
                ] as const
              ).map(([key, label, typ]) => (
                <div key={key}>
                  <Label>{label}</Label>
                  <Input
                    type={typ === 'date' ? 'date' : 'text'}
                    value={(kunde.tab23 as Record<string, string>)[key]}
                    onChange={(e) =>
                      setKunde((prev) => ({
                        ...prev,
                        tab23: { ...prev.tab23, [key]: e.target.value },
                      }))
                    }
                  />
                </div>
              ))}
              <div>
                <Label>ABC-Status (→ Marketing-Segment)</Label>
                <select
                  className="w-full rounded-md border px-3 py-2 text-sm"
                  value={kunde.tab23.abc_status}
                  onChange={(e) =>
                    setKunde((prev) => ({ ...prev, tab23: { ...prev.tab23, abc_status: e.target.value } }))
                  }
                >
                  <option value="">—</option>
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="C">C</option>
                </select>
              </div>
              <div className="flex items-center gap-2 pt-7">
                <input
                  id="fax_blocked"
                  type="checkbox"
                  checked={kunde.fax_blocked}
                  onChange={(e) => setKunde((prev) => ({ ...prev, fax_blocked: e.target.checked }))}
                />
                <Label htmlFor="fax_blocked">Fax gesperrt (Legacy)</Label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="konditionen">
          <Card>
            <CardHeader>
              <CardTitle>Zahlung und Steuer</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div>
                <Label>USt-IdNr.</Label>
                <Input value={kunde.ust_id} onChange={(e) => setKunde((prev) => ({ ...prev, ust_id: e.target.value }))} />
              </div>
              <div>
                <Label>Steuernummer</Label>
                <Input
                  value={kunde.steuernummer}
                  onChange={(e) => setKunde((prev) => ({ ...prev, steuernummer: e.target.value }))}
                />
              </div>
              <div>
                <Label>Zahlungsziel (ID/Code)</Label>
                <Input
                  value={kunde.zahlungsziel}
                  onChange={(e) => setKunde((prev) => ({ ...prev, zahlungsziel: e.target.value }))}
                />
              </div>
              <div>
                <Label>Kreditlimit (EUR)</Label>
                <Input
                  type="number"
                  value={kunde.kreditlimit}
                  onChange={(e) => setKunde((prev) => ({ ...prev, kreditlimit: Number(e.target.value || 0) }))}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tab21">
          <Card>
            <CardHeader>
              <CardTitle>Chef-Anweisung (Tab 21)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {!partnerId && (
                <p className="text-sm text-muted-foreground">Kunde zuerst speichern, dann Eintraege pflegen.</p>
              )}
              {partnerId && (
                <>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="md:col-span-2">
                      <Label>Text</Label>
                      <Textarea
                        rows={5}
                        value={instructionForm.instruction_text}
                        onChange={(e) => setInstructionForm((p) => ({ ...p, instruction_text: e.target.value }))}
                      />
                    </div>
                    <div>
                      <Label>Prioritaet</Label>
                      <select
                        className="w-full rounded-md border px-3 py-2 text-sm"
                        value={instructionForm.instruction_priority}
                        onChange={(e) =>
                          setInstructionForm((p) => ({
                            ...p,
                            instruction_priority: e.target.value as InstructionPayload['instruction_priority'],
                          }))
                        }
                      >
                        <option value="low">niedrig</option>
                        <option value="normal">normal</option>
                        <option value="high">hoch</option>
                        <option value="critical">kritisch</option>
                      </select>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <Label>gueltig ab</Label>
                        <Input
                          type="date"
                          value={instructionForm.valid_from}
                          onChange={(e) => setInstructionForm((p) => ({ ...p, valid_from: e.target.value }))}
                        />
                      </div>
                      <div>
                        <Label>gueltig bis</Label>
                        <Input
                          type="date"
                          value={instructionForm.valid_to}
                          onChange={(e) => setInstructionForm((p) => ({ ...p, valid_to: e.target.value }))}
                        />
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2 md:col-span-2">
                      <Button
                        type="button"
                        onClick={() => void instructionMutation.mutateAsync()}
                        disabled={instructionMutation.isPending || !instructionForm.instruction_text.trim()}
                      >
                        {editingInstructionId ? 'Aktualisieren' : 'Hinzufuegen'}
                      </Button>
                      {editingInstructionId && (
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => {
                            setEditingInstructionId(null)
                            setInstructionForm(DEFAULT_INSTRUCTION_FORM)
                          }}
                        >
                          Abbrechen
                        </Button>
                      )}
                    </div>
                  </div>
                  <div className="overflow-x-auto rounded border">
                    <table className="w-full text-sm">
                      <thead className="bg-muted/40">
                        <tr>
                          <th className="px-3 py-2 text-left">Prioritaet</th>
                          <th className="px-3 py-2 text-left">Text</th>
                          <th className="px-3 py-2 text-left">Aktion</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(instructionsQuery.data ?? []).map((row) => (
                          <tr key={row.id} className="border-t">
                            <td className="px-3 py-2">{row.instruction_priority}</td>
                            <td className="px-3 py-2 max-w-md truncate" title={row.instruction_text}>
                              {row.instruction_text}
                            </td>
                            <td className="px-3 py-2 space-x-2">
                              <Button
                                type="button"
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  setEditingInstructionId(row.id)
                                  setInstructionForm(instructionToForm(row))
                                }}
                              >
                                Bearbeiten
                              </Button>
                              <Button
                                type="button"
                                size="sm"
                                variant="destructive"
                                onClick={() => void deleteInstructionMutation.mutateAsync(row.id)}
                                disabled={deleteInstructionMutation.isPending}
                              >
                                Loeschen
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tab22">
          <Card>
            <CardHeader>
              <CardTitle>Ansprechpartner (Tab 22)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {!partnerId && (
                <p className="text-sm text-muted-foreground">Kunde zuerst speichern, dann Ansprechpartner erfassen.</p>
              )}
              {partnerId && (
                <>
                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <Label>Anrede</Label>
                      <Input
                        value={contactForm.salutation ?? ''}
                        onChange={(e) => setContactForm((p) => ({ ...p, salutation: e.target.value || null }))}
                      />
                    </div>
                    <div>
                      <Label>Vorname</Label>
                      <Input
                        value={contactForm.first_name ?? ''}
                        onChange={(e) => setContactForm((p) => ({ ...p, first_name: e.target.value || null }))}
                      />
                    </div>
                    <div>
                      <Label>Nachname *</Label>
                      <Input
                        value={contactForm.last_name}
                        onChange={(e) => setContactForm((p) => ({ ...p, last_name: e.target.value }))}
                      />
                    </div>
                    <div>
                      <Label>Position</Label>
                      <Input
                        value={contactForm.position ?? ''}
                        onChange={(e) => setContactForm((p) => ({ ...p, position: e.target.value || null }))}
                      />
                    </div>
                    <div>
                      <Label>Abteilung</Label>
                      <Input
                        value={contactForm.department ?? ''}
                        onChange={(e) => setContactForm((p) => ({ ...p, department: e.target.value || null }))}
                      />
                    </div>
                    <div>
                      <Label>Typ</Label>
                      <select
                        className="w-full rounded-md border px-3 py-2 text-sm"
                        value={contactForm.contact_type}
                        onChange={(e) =>
                          setContactForm((p) => ({
                            ...p,
                            contact_type: e.target.value as BpContactPayload['contact_type'],
                          }))
                        }
                      >
                        <option value="main">Haupt</option>
                        <option value="billing">Rechnung</option>
                        <option value="logistics">Logistik</option>
                        <option value="sales">Vertrieb</option>
                        <option value="other">sonstige</option>
                      </select>
                    </div>
                    <div>
                      <Label>Telefon</Label>
                      <Input
                        value={contactForm.phone_1 ?? ''}
                        onChange={(e) => setContactForm((p) => ({ ...p, phone_1: e.target.value || null }))}
                      />
                    </div>
                    <div>
                      <Label>Mobil</Label>
                      <Input
                        value={contactForm.mobile ?? ''}
                        onChange={(e) => setContactForm((p) => ({ ...p, mobile: e.target.value || null }))}
                      />
                    </div>
                    <div>
                      <Label>E-Mail</Label>
                      <Input
                        value={contactForm.email ?? ''}
                        onChange={(e) => setContactForm((p) => ({ ...p, email: e.target.value || null }))}
                      />
                    </div>
                    <div className="flex items-center gap-4 md:col-span-3">
                      <label className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={contactForm.invoice_email_recipient}
                          onChange={(e) => setContactForm((p) => ({ ...p, invoice_email_recipient: e.target.checked }))}
                        />
                        Rechnungs-E-Mail
                      </label>
                      <label className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={contactForm.reminder_email_recipient}
                          onChange={(e) => setContactForm((p) => ({ ...p, reminder_email_recipient: e.target.checked }))}
                        />
                        Mahn-E-Mail
                      </label>
                    </div>
                    <div className="flex flex-wrap gap-2 md:col-span-3">
                      <Button
                        type="button"
                        onClick={() => void contactMutation.mutateAsync()}
                        disabled={contactMutation.isPending}
                      >
                        {editingContactId ? 'Aktualisieren' : 'Hinzufuegen'}
                      </Button>
                      {editingContactId && (
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => {
                            setEditingContactId(null)
                            setContactForm(DEFAULT_CONTACT_FORM)
                          }}
                        >
                          Abbrechen
                        </Button>
                      )}
                    </div>
                  </div>
                  <div className="overflow-x-auto rounded border">
                    <table className="w-full text-sm">
                      <thead className="bg-muted/40">
                        <tr>
                          <th className="px-3 py-2 text-left">Name</th>
                          <th className="px-3 py-2 text-left">Typ</th>
                          <th className="px-3 py-2 text-left">Kontakt</th>
                          <th className="px-3 py-2 text-left">Aktion</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(contactsQuery.data ?? []).map((c) => (
                          <tr key={c.id} className="border-t">
                            <td className="px-3 py-2">
                              {[c.first_name, c.last_name].filter(Boolean).join(' ') || c.last_name}
                            </td>
                            <td className="px-3 py-2">{c.contact_type}</td>
                            <td className="px-3 py-2">
                              {[c.phone_1, c.mobile, c.email].filter(Boolean).join(' · ') || '—'}
                            </td>
                            <td className="px-3 py-2 space-x-2">
                              <Button
                                type="button"
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  setEditingContactId(c.id)
                                  setContactForm(contactToFormPayload(c))
                                }}
                              >
                                Bearbeiten
                              </Button>
                              <Button
                                type="button"
                                size="sm"
                                variant="destructive"
                                onClick={() => void deleteContactMutation.mutateAsync(c.id)}
                                disabled={deleteContactMutation.isPending}
                              >
                                Loeschen
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tab23">
          <Card>
            <CardHeader>
              <CardTitle>Anschriften (normalisiert)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {!partnerId && <p className="text-sm text-muted-foreground">Kunde zuerst speichern, dann Anschriften pflegen.</p>}
              {partnerId && (
                <>
                  <p className="text-xs text-muted-foreground">
                    Entspricht Tab 23 Zusatzfeldern je Anschriftenzeile (Name 2/3, Postfach, Freifelder, Gebietscode).
                  </p>
                  <div className="grid gap-4 md:grid-cols-4">
                    <div>
                      <Label>Typ</Label>
                      <select
                        className="w-full rounded-md border px-3 py-2 text-sm"
                        value={addressForm.address_type}
                        onChange={(e) => setAddressForm((p) => ({ ...p, address_type: e.target.value as AddressForm['address_type'] }))}
                      >
                        <option value="customer">Kundenanschrift</option>
                        <option value="invoice">Rechnungsanschrift</option>
                        <option value="shipping">Lieferanschrift</option>
                        <option value="postal">Postfach</option>
                      </select>
                    </div>
                    <div>
                      <Label>Name 1</Label>
                      <Input value={addressForm.name_1} onChange={(e) => setAddressForm((p) => ({ ...p, name_1: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Name 2</Label>
                      <Input value={addressForm.name_2} onChange={(e) => setAddressForm((p) => ({ ...p, name_2: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Name 3</Label>
                      <Input value={addressForm.name_3} onChange={(e) => setAddressForm((p) => ({ ...p, name_3: e.target.value }))} />
                    </div>
                    <div className="md:col-span-2">
                      <Label>Strasse</Label>
                      <Input value={addressForm.street} onChange={(e) => setAddressForm((p) => ({ ...p, street: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Nr.</Label>
                      <Input value={addressForm.house_number} onChange={(e) => setAddressForm((p) => ({ ...p, house_number: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Gebietscode</Label>
                      <Input value={addressForm.area_code} onChange={(e) => setAddressForm((p) => ({ ...p, area_code: e.target.value }))} />
                    </div>
                    <div>
                      <Label>PLZ</Label>
                      <Input value={addressForm.postal_code} onChange={(e) => setAddressForm((p) => ({ ...p, postal_code: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Ort</Label>
                      <Input value={addressForm.city} onChange={(e) => setAddressForm((p) => ({ ...p, city: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Land</Label>
                      <Input value={addressForm.country} onChange={(e) => setAddressForm((p) => ({ ...p, country: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Postfach</Label>
                      <Input value={addressForm.po_box} onChange={(e) => setAddressForm((p) => ({ ...p, po_box: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Postfach-PLZ</Label>
                      <Input value={addressForm.po_box_postal_code} onChange={(e) => setAddressForm((p) => ({ ...p, po_box_postal_code: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Postfach-Ort</Label>
                      <Input value={addressForm.po_box_city} onChange={(e) => setAddressForm((p) => ({ ...p, po_box_city: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Anrede</Label>
                      <Input value={addressForm.salutation} onChange={(e) => setAddressForm((p) => ({ ...p, salutation: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Briefanrede</Label>
                      <Input value={addressForm.brief_salutation} onChange={(e) => setAddressForm((p) => ({ ...p, brief_salutation: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Telefon</Label>
                      <Input value={addressForm.phone} onChange={(e) => setAddressForm((p) => ({ ...p, phone: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Fax</Label>
                      <Input value={addressForm.fax} onChange={(e) => setAddressForm((p) => ({ ...p, fax: e.target.value }))} />
                    </div>
                    <div>
                      <Label>E-Mail</Label>
                      <Input value={addressForm.email} onChange={(e) => setAddressForm((p) => ({ ...p, email: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Web</Label>
                      <Input value={addressForm.website} onChange={(e) => setAddressForm((p) => ({ ...p, website: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Freifeld 1</Label>
                      <Input value={addressForm.free_field_1} onChange={(e) => setAddressForm((p) => ({ ...p, free_field_1: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Freifeld 2</Label>
                      <Input value={addressForm.free_field_2} onChange={(e) => setAddressForm((p) => ({ ...p, free_field_2: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Freifeld 3</Label>
                      <Input value={addressForm.free_field_3} onChange={(e) => setAddressForm((p) => ({ ...p, free_field_3: e.target.value }))} />
                    </div>
                    <div className="flex items-center gap-2 pt-8">
                      <input
                        id="addr_default"
                        type="checkbox"
                        checked={addressForm.is_default}
                        onChange={(e) => setAddressForm((p) => ({ ...p, is_default: e.target.checked }))}
                      />
                      <Label htmlFor="addr_default">Standard</Label>
                    </div>
                    <div className="flex items-end gap-2 md:col-span-3">
                      <Button onClick={() => void addressMutation.mutateAsync()} disabled={addressMutation.isPending}>
                        {editingAddressId ? 'Aktualisieren' : 'Hinzufuegen'}
                      </Button>
                      {editingAddressId && (
                        <Button
                          variant="outline"
                          onClick={() => {
                            setEditingAddressId(null)
                            setAddressForm(DEFAULT_ADDRESS_FORM)
                          }}
                        >
                          Abbrechen
                        </Button>
                      )}
                    </div>
                  </div>

                  <div className="overflow-x-auto rounded border">
                    <table className="w-full text-sm">
                      <thead className="bg-muted/40">
                        <tr>
                          <th className="px-3 py-2 text-left">Typ</th>
                          <th className="px-3 py-2 text-left">Name</th>
                          <th className="px-3 py-2 text-left">Adresse</th>
                          <th className="px-3 py-2 text-left">Kontakt</th>
                          <th className="px-3 py-2 text-left">Aktion</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(addressesQuery.data ?? []).map((item) => (
                          <tr key={item.id} className="border-t">
                            <td className="px-3 py-2">{item.address_type}</td>
                            <td className="px-3 py-2">{item.name_1 || '-'}</td>
                            <td className="px-3 py-2">{[item.street, item.house_number, item.postal_code, item.city].filter(Boolean).join(' ') || '-'}</td>
                            <td className="px-3 py-2">{item.email || item.phone || '-'}</td>
                            <td className="px-3 py-2 space-x-2">
                              <Button size="sm" variant="outline" onClick={() => loadAddressForEdit(item)}>Bearbeiten</Button>
                              <Button size="sm" variant="outline" onClick={() => deleteAddressMutation.mutate(item.id)}>Loeschen</Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tab24">
          <Card>
            <CardHeader>
              <CardTitle>Rechnung/Kontoauszug (normalisiert)</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-4">
              {!partnerId && <p className="text-sm text-muted-foreground">Kunde zuerst speichern.</p>}
              {partnerId && (
                <>
                  <div>
                    <Label>Kunden-Gruppe</Label>
                    <Input value={billingForm.customer_group} onChange={(e) => setBillingForm((p) => ({ ...p, customer_group: e.target.value }))} />
                  </div>
                  <div>
                    <Label>Kundentyp</Label>
                    <select
                      className="w-full rounded-md border px-3 py-2 text-sm"
                      value={billingForm.customer_type}
                      onChange={(e) => setBillingForm((p) => ({ ...p, customer_type: e.target.value as BillingConfigForm['customer_type'] }))}
                    >
                      <option value="">-</option>
                      <option value="standard">standard</option>
                      <option value="organ">organ</option>
                      <option value="group_internal">group_internal</option>
                    </select>
                  </div>
                  <div>
                    <Label>Letzte Auszugs-Nr.</Label>
                    <Input type="number" value={billingForm.last_account_statement_number} onChange={(e) => setBillingForm((p) => ({ ...p, last_account_statement_number: Number(e.target.value || 0) }))} />
                  </div>
                  <div>
                    <Label>Saldo</Label>
                    <Input type="number" step="0.01" value={billingForm.account_balance} onChange={(e) => setBillingForm((p) => ({ ...p, account_balance: Number(e.target.value || 0) }))} />
                  </div>
                  <div>
                    <Label>Settlement</Label>
                    <select
                      className="w-full rounded-md border px-3 py-2 text-sm"
                      value={billingForm.settlement_mode}
                      onChange={(e) => setBillingForm((p) => ({ ...p, settlement_mode: e.target.value as BillingConfigForm['settlement_mode'] }))}
                    >
                      <option value="">-</option>
                      <option value="single">single</option>
                      <option value="collective">collective</option>
                    </select>
                  </div>
                  <div>
                    <Label>VWG-Aufschlag %</Label>
                    <Input type="number" step="0.01" value={billingForm.admin_overhead_surcharge_percent} onChange={(e) => setBillingForm((p) => ({ ...p, admin_overhead_surcharge_percent: Number(e.target.value || 0) }))} />
                  </div>
                  <div>
                    <Label>Rechnungsnummernkreis</Label>
                    <Input value={billingForm.invoice_number_range} onChange={(e) => setBillingForm((p) => ({ ...p, invoice_number_range: e.target.value }))} />
                  </div>
                  <div className="space-y-2 pt-7">
                    <label className="flex items-center gap-2"><input type="checkbox" checked={billingForm.account_statement_print} onChange={(e) => setBillingForm((p) => ({ ...p, account_statement_print: e.target.checked }))} /> Kontoauszug drucken</label>
                    <label className="flex items-center gap-2"><input type="checkbox" checked={billingForm.account_statement_separate} onChange={(e) => setBillingForm((p) => ({ ...p, account_statement_separate: e.target.checked }))} /> getrennt</label>
                    <label className="flex items-center gap-2"><input type="checkbox" checked={billingForm.account_statement_reprint} onChange={(e) => setBillingForm((p) => ({ ...p, account_statement_reprint: e.target.checked }))} /> Nachdruck</label>
                    <label className="flex items-center gap-2"><input type="checkbox" checked={billingForm.bonus_eligible} onChange={(e) => setBillingForm((p) => ({ ...p, bonus_eligible: e.target.checked }))} /> Bonusberechtigt</label>
                    <label className="flex items-center gap-2"><input type="checkbox" checked={billingForm.self_billing_sales} onChange={(e) => setBillingForm((p) => ({ ...p, self_billing_sales: e.target.checked }))} /> Selbstabrechner Verkauf</label>
                    <label className="flex items-center gap-2"><input type="checkbox" checked={billingForm.self_billing_purchase} onChange={(e) => setBillingForm((p) => ({ ...p, self_billing_purchase: e.target.checked }))} /> Selbstabrechner Zukauf</label>
                    <label className="flex items-center gap-2"><input type="checkbox" checked={billingForm.vat_optimizer} onChange={(e) => setBillingForm((p) => ({ ...p, vat_optimizer: e.target.checked }))} /> USt-Optierer</label>
                  </div>
                  <div className="flex items-end">
                    <Button onClick={() => void billingMutation.mutateAsync()} disabled={billingMutation.isPending}>Speichern</Button>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tab25">
          <Card>
            <CardHeader>
              <CardTitle>CPD-Konto (normalisiert)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {!partnerId && <p className="text-sm text-muted-foreground">Kunde zuerst speichern, dann CPD anlegen.</p>}
              {partnerId && (
                <>
                  <div className="grid gap-4 md:grid-cols-5">
                    <div>
                      <Label>CPD Kunden-Nr.</Label>
                      <Input value={cpdForm.cpd_customer_number} onChange={(e) => setCpdForm((p) => ({ ...p, cpd_customer_number: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Debitorenkonto</Label>
                      <Input value={cpdForm.debtor_account} onChange={(e) => setCpdForm((p) => ({ ...p, debtor_account: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Name 1</Label>
                      <Input value={cpdForm.name_1} onChange={(e) => setCpdForm((p) => ({ ...p, name_1: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Strasse</Label>
                      <Input value={cpdForm.street} onChange={(e) => setCpdForm((p) => ({ ...p, street: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Nr.</Label>
                      <Input value={cpdForm.house_number} onChange={(e) => setCpdForm((p) => ({ ...p, house_number: e.target.value }))} />
                    </div>
                    <div>
                      <Label>PLZ</Label>
                      <Input value={cpdForm.postal_code} onChange={(e) => setCpdForm((p) => ({ ...p, postal_code: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Ort</Label>
                      <Input value={cpdForm.city} onChange={(e) => setCpdForm((p) => ({ ...p, city: e.target.value }))} />
                    </div>
                    <div>
                      <Label>E-Mail</Label>
                      <Input value={cpdForm.email} onChange={(e) => setCpdForm((p) => ({ ...p, email: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Telefon</Label>
                      <Input value={cpdForm.phone_1} onChange={(e) => setCpdForm((p) => ({ ...p, phone_1: e.target.value }))} />
                    </div>
                    <div className="flex items-end gap-2">
                      <Button onClick={() => void cpdMutation.mutateAsync()} disabled={cpdMutation.isPending}>
                        {editingCpdId ? 'Aktualisieren' : 'Hinzufuegen'}
                      </Button>
                      {editingCpdId && (
                        <Button
                          variant="outline"
                          onClick={() => {
                            setEditingCpdId(null)
                            setCpdForm(DEFAULT_CPD_FORM)
                          }}
                        >
                          Abbrechen
                        </Button>
                      )}
                    </div>
                  </div>

                  <div className="overflow-x-auto rounded border">
                    <table className="w-full text-sm">
                      <thead className="bg-muted/40">
                        <tr>
                          <th className="px-3 py-2 text-left">CPD-Nr.</th>
                          <th className="px-3 py-2 text-left">Name</th>
                          <th className="px-3 py-2 text-left">Ort</th>
                          <th className="px-3 py-2 text-left">Debitor</th>
                          <th className="px-3 py-2 text-left">Aktion</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(cpdAccountsQuery.data ?? []).map((item) => (
                          <tr key={item.id} className="border-t">
                            <td className="px-3 py-2">{item.cpd_customer_number}</td>
                            <td className="px-3 py-2">{item.name_1}</td>
                            <td className="px-3 py-2">{[item.postal_code, item.city].filter(Boolean).join(' ') || '-'}</td>
                            <td className="px-3 py-2">{item.debtor_account || '-'}</td>
                            <td className="px-3 py-2 space-x-2">
                              <Button size="sm" variant="outline" onClick={() => loadCpdForEdit(item)}>Bearbeiten</Button>
                              <Button size="sm" variant="outline" onClick={() => deleteCpdMutation.mutate(item.id)}>Loeschen</Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="historie">
          <Card>
            <CardContent className="pt-6">
              <p className="text-muted-foreground">Historie wird in einem separaten Schritt angebunden.</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rabatte">
          <Card>
            <CardHeader>
              <CardTitle>Rabatt-Listen (normalisiert)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {!partnerId && (
                <p className="text-sm text-muted-foreground">Kunde zuerst speichern, dann Rabatte bearbeiten.</p>
              )}
              {partnerId && (
                <>
                  <div className="grid gap-4 md:grid-cols-4">
                    <div>
                      <Label>Artikel-Nr.</Label>
                      <Input value={discountForm.article_number} onChange={(e) => {
                        const value = e.target.value
                        setDiscountForm((p) => ({ ...p, article_number: value }))
                        if (discountErrors.article_number) setDiscountErrors((prev) => ({ ...prev, article_number: undefined }))
                      }} />
                      {discountErrors.article_number && <p className="text-xs text-destructive mt-1">{discountErrors.article_number}</p>}
                    </div>
                    <div>
                      <Label>Bezeichnung</Label>
                      <Input value={discountForm.description} onChange={(e) => setDiscountForm((p) => ({ ...p, description: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Rabatt %</Label>
                      <Input type="number" step="0.01" min={0} max={100} value={discountForm.discount_percent} onChange={(e) => {
                        const value = Number(e.target.value || 0)
                        setDiscountForm((p) => ({ ...p, discount_percent: value }))
                        if (discountErrors.discount_percent) setDiscountErrors((prev) => ({ ...prev, discount_percent: undefined }))
                      }} />
                      {discountErrors.discount_percent && <p className="text-xs text-destructive mt-1">{discountErrors.discount_percent}</p>}
                    </div>
                    <div>
                      <Label>Gueltig bis</Label>
                      <Input type="date" value={discountForm.valid_to} onChange={(e) => {
                        const value = e.target.value
                        setDiscountForm((p) => ({ ...p, valid_to: value }))
                        if (discountErrors.valid_to) setDiscountErrors((prev) => ({ ...prev, valid_to: undefined }))
                      }} />
                      {discountErrors.valid_to && <p className="text-xs text-destructive mt-1">{discountErrors.valid_to}</p>}
                    </div>
                    <div>
                      <Label>Gueltig ab</Label>
                      <Input type="date" value={discountForm.valid_from} onChange={(e) => setDiscountForm((p) => ({ ...p, valid_from: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Rabatt-Liste</Label>
                      <Input value={discountForm.discount_list_number} onChange={(e) => setDiscountForm((p) => ({ ...p, discount_list_number: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Typ</Label>
                      <select
                        className="w-full rounded-md border px-3 py-2 text-sm"
                        value={discountForm.source_type}
                        onChange={(e) => setDiscountForm((p) => ({ ...p, source_type: e.target.value as DiscountForm['source_type'] }))}
                      >
                        <option value="">-</option>
                        <option value="internal">internal</option>
                        <option value="batch">batch</option>
                        <option value="import">import</option>
                      </select>
                    </div>
                    <div className="flex items-end gap-2">
                      <Button
                        onClick={() => {
                          const errors = validateDiscountForm(discountForm)
                          setDiscountErrors(errors)
                          if (Object.keys(errors).length > 0) {
                            toast({ title: 'Validierungsfehler', description: 'Bitte Eingaben im Rabatt-Tab pruefen.', variant: 'destructive' })
                            return
                          }
                          void discountMutation.mutateAsync()
                        }}
                        disabled={discountMutation.isPending}
                      >
                        {editingDiscountId ? 'Aktualisieren' : 'Hinzufuegen'}
                      </Button>
                      {editingDiscountId && (
                        <Button
                          variant="outline"
                          onClick={() => {
                            setEditingDiscountId(null)
                            setDiscountForm(DEFAULT_DISCOUNT_FORM)
                            setDiscountErrors({})
                          }}
                        >
                          Abbrechen
                        </Button>
                      )}
                    </div>
                  </div>

                  <div className="overflow-x-auto rounded border">
                    <table className="w-full text-sm">
                      <thead className="bg-muted/40">
                        <tr>
                          <th className="px-3 py-2 text-left">Artikel</th>
                          <th className="px-3 py-2 text-left">Bezeichnung</th>
                          <th className="px-3 py-2 text-left">Rabatt %</th>
                          <th className="px-3 py-2 text-left">Bis</th>
                          <th className="px-3 py-2 text-left">Aktion</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(discountItemsQuery.data ?? []).map((item) => (
                          <tr key={item.id} className="border-t">
                            <td className="px-3 py-2">{item.article_number}</td>
                            <td className="px-3 py-2">{item.description || '-'}</td>
                            <td className="px-3 py-2">{item.discount_percent}</td>
                            <td className="px-3 py-2">{item.valid_to ? item.valid_to.slice(0, 10) : '-'}</td>
                            <td className="px-3 py-2 space-x-2">
                              <Button size="sm" variant="outline" onClick={() => loadDiscountForEdit(item)}>Bearbeiten</Button>
                              <Button size="sm" variant="outline" onClick={() => deleteDiscountMutation.mutate(item.id)}>Loeschen</Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="preise">
          <Card>
            <CardHeader>
              <CardTitle>Preisvereinbarungen (normalisiert)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {!partnerId && (
                <p className="text-sm text-muted-foreground">Kunde zuerst speichern, dann Preisvereinbarungen bearbeiten.</p>
              )}
              {partnerId && (
                <>
                  <div className="grid gap-4 md:grid-cols-4">
                    <div>
                      <Label>Artikel-Nr.</Label>
                      <Input value={priceForm.article_number} onChange={(e) => {
                        const value = e.target.value
                        setPriceForm((p) => ({ ...p, article_number: value }))
                        if (priceErrors.article_number) setPriceErrors((prev) => ({ ...prev, article_number: undefined }))
                      }} />
                      {priceErrors.article_number && <p className="text-xs text-destructive mt-1">{priceErrors.article_number}</p>}
                    </div>
                    <div>
                      <Label>Bezeichnung</Label>
                      <Input value={priceForm.description} onChange={(e) => setPriceForm((p) => ({ ...p, description: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Preis netto</Label>
                      <Input type="number" step="0.0001" min={0} value={priceForm.price_net} onChange={(e) => {
                        const value = Number(e.target.value || 0)
                        setPriceForm((p) => ({ ...p, price_net: value }))
                        if (priceErrors.price_net) setPriceErrors((prev) => ({ ...prev, price_net: undefined }))
                      }} />
                      {priceErrors.price_net && <p className="text-xs text-destructive mt-1">{priceErrors.price_net}</p>}
                    </div>
                    <div>
                      <Label>Preis inkl. Fracht</Label>
                      <Input type="number" step="0.0001" min={0} value={priceForm.price_incl_freight} onChange={(e) => {
                        const value = Number(e.target.value || 0)
                        setPriceForm((p) => ({ ...p, price_incl_freight: value }))
                        if (priceErrors.price_incl_freight) setPriceErrors((prev) => ({ ...prev, price_incl_freight: undefined }))
                      }} />
                      {priceErrors.price_incl_freight && <p className="text-xs text-destructive mt-1">{priceErrors.price_incl_freight}</p>}
                    </div>
                    <div>
                      <Label>Gueltig ab</Label>
                      <Input type="date" value={priceForm.valid_from} onChange={(e) => setPriceForm((p) => ({ ...p, valid_from: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Gueltig bis</Label>
                      <Input type="date" value={priceForm.valid_to} onChange={(e) => {
                        const value = e.target.value
                        setPriceForm((p) => ({ ...p, valid_to: value }))
                        if (priceErrors.valid_to) setPriceErrors((prev) => ({ ...prev, valid_to: undefined }))
                      }} />
                      {priceErrors.valid_to && <p className="text-xs text-destructive mt-1">{priceErrors.valid_to}</p>}
                    </div>
                    <div>
                      <Label>Einheit</Label>
                      <Input value={priceForm.price_unit} onChange={(e) => {
                        const value = e.target.value
                        setPriceForm((p) => ({ ...p, price_unit: value }))
                        if (priceErrors.price_unit) setPriceErrors((prev) => ({ ...prev, price_unit: undefined }))
                      }} />
                      {priceErrors.price_unit && <p className="text-xs text-destructive mt-1">{priceErrors.price_unit}</p>}
                    </div>
                    <div>
                      <Label>Sonderfracht</Label>
                      <Input type="number" step="0.0001" min={0} value={priceForm.special_freight} onChange={(e) => {
                        const value = Number(e.target.value || 0)
                        setPriceForm((p) => ({ ...p, special_freight: value }))
                        if (priceErrors.special_freight) setPriceErrors((prev) => ({ ...prev, special_freight: undefined }))
                      }} />
                      {priceErrors.special_freight && <p className="text-xs text-destructive mt-1">{priceErrors.special_freight}</p>}
                    </div>
                    <div>
                      <Label>Zahlungsbedingung</Label>
                      <Input value={priceForm.payment_condition} onChange={(e) => setPriceForm((p) => ({ ...p, payment_condition: e.target.value }))} />
                    </div>
                    <div>
                      <Label>Typ</Label>
                      <select
                        className="w-full rounded-md border px-3 py-2 text-sm"
                        value={priceForm.source_type}
                        onChange={(e) => setPriceForm((p) => ({ ...p, source_type: e.target.value as PriceAgreementForm['source_type'] }))}
                      >
                        <option value="">-</option>
                        <option value="internal">internal</option>
                        <option value="batch">batch</option>
                        <option value="import">import</option>
                      </select>
                    </div>
                    <div>
                      <Label>Bediener</Label>
                      <Input value={priceForm.operator_name} onChange={(e) => setPriceForm((p) => ({ ...p, operator_name: e.target.value }))} />
                    </div>
                    <div className="flex items-end gap-2">
                      <Button
                        onClick={() => {
                          const errors = validatePriceForm(priceForm)
                          setPriceErrors(errors)
                          if (Object.keys(errors).length > 0) {
                            toast({ title: 'Validierungsfehler', description: 'Bitte Eingaben im Preis-Tab pruefen.', variant: 'destructive' })
                            return
                          }
                          void priceMutation.mutateAsync()
                        }}
                        disabled={priceMutation.isPending}
                      >
                        {editingPriceId ? 'Aktualisieren' : 'Hinzufuegen'}
                      </Button>
                      {editingPriceId && (
                        <Button
                          variant="outline"
                          onClick={() => {
                            setEditingPriceId(null)
                            setPriceForm(DEFAULT_PRICE_FORM)
                            setPriceErrors({})
                          }}
                        >
                          Abbrechen
                        </Button>
                      )}
                    </div>
                  </div>

                  <div className="overflow-x-auto rounded border">
                    <table className="w-full text-sm">
                      <thead className="bg-muted/40">
                        <tr>
                          <th className="px-3 py-2 text-left">Artikel</th>
                          <th className="px-3 py-2 text-left">Preis netto</th>
                          <th className="px-3 py-2 text-left">Preis inkl. Fracht</th>
                          <th className="px-3 py-2 text-left">Bis</th>
                          <th className="px-3 py-2 text-left">Aktion</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(priceAgreementsQuery.data ?? []).map((item) => (
                          <tr key={item.id} className="border-t">
                            <td className="px-3 py-2">{item.article_number}</td>
                            <td className="px-3 py-2">{item.price_net ?? '-'}</td>
                            <td className="px-3 py-2">{item.price_incl_freight ?? '-'}</td>
                            <td className="px-3 py-2">{item.valid_to ? item.valid_to.slice(0, 10) : '-'}</td>
                            <td className="px-3 py-2 space-x-2">
                              <Button size="sm" variant="outline" onClick={() => loadPriceForEdit(item)}>Bearbeiten</Button>
                              <Button size="sm" variant="outline" onClick={() => deletePriceMutation.mutate(item.id)}>Loeschen</Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
