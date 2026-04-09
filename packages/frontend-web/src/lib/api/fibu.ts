/**
 * Finanzbuchhaltung API Client
 * TanStack Query Hooks für alle Fibu-Endpoints
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type OffenerPosten = {
  id: string
  rechnungsnr: string
  datum: string
  faelligkeit: string
  betrag: number
  offen: number
  kunde_id?: string
  kunde_name?: string
  lieferant_id?: string
  lieferant_name?: string
  skonto_prozent?: number
  skonto_bis?: string
  mahn_stufe?: number
  zahlbar?: boolean
}

export type Buchung = {
  id: string
  belegnr: string
  datum: string
  soll_konto: string
  haben_konto: string
  betrag: number
  text: string
  belegart: string
}

export type Konto = {
  id: string
  kontonummer: string
  bezeichnung: string
  kontoart: string
  typ: string
  saldo: number
}

export type Anlage = {
  id: string
  anlagennr: string
  bezeichnung: string
  anschaffung: string
  anschaffungswert: number
  nutzungsdauer: number
  afa_satz: number
  kumulierte_afa: number
  buchwert: number
}

export type FibuCockpitReadModel = {
  tenant_id: string
  schema_version: number
  master_data: {
    dunning_parameters_ready: boolean
    interest_groups_ready: boolean
    connector_profile_count: number
    connector_profiles: Array<{
      connector_type: string
      profile_count: number
      latest_version: number
      updated_at?: string | null
    }>
  }
  dunning: {
    open_items: number
    overdue_items: number
    overdue_amount: number
    dunning_items: number
  }
  interest: {
    candidate_count: number
    candidate_amount: number
  }
  creditor: {
    open_items: number
    payable_items: number
    open_amount: number
    overdue_amount: number
  }
  tax: {
    vat_return_count: number
    validated_count: number
    approved_count: number
    submitted_count: number
    latest_period?: string | null
    latest_submission_at?: string | null
    e_bilanz_ready: boolean
    e_clearing_ready: boolean
  }
  exports: Array<{
    kind: string
    count: number
    record_count: number
    latest_created_at?: string | null
    has_artifacts: boolean
  }>
  annual_close: {
    open_item_count: number
    overdue_item_count: number
    recent_journal_entries: number
    latest_vat_period?: string | null
    ready_for_year_close: boolean
  }
  revision: {
    recent_journal_entries: number
    last_entry_date?: string | null
    export_runs: number
  }
}

export type AccountingPeriod = {
  id: string
  tenant_id: string
  period: string
  status: 'OPEN' | 'CLOSED' | 'ADJUSTING'
  start_date: string
  end_date: string
  closed_at?: string | null
  closed_by?: string | null
  metadata: Record<string, unknown>
}

export type FibuConnectorProfile = {
  id: string
  tenant_id: string
  connector_type: 'PAYROLL' | 'ASSET_LEDGER'
  name: string
  is_default: boolean
  settings: Record<string, unknown>
  mapping: Record<string, unknown>
  version: number
  created_at?: string | null
  updated_at?: string | null
  created_by?: string | null
  updated_by?: string | null
}

// ========== QUERY KEYS ==========

export const fibuKeys = {
  all: ['fibu'] as const,
  debitoren: () => [...fibuKeys.all, 'debitoren'] as const,
  kreditoren: () => [...fibuKeys.all, 'kreditoren'] as const,
  buchungen: () => [...fibuKeys.all, 'buchungen'] as const,
  konten: () => [...fibuKeys.all, 'konten'] as const,
  anlagen: () => [...fibuKeys.all, 'anlagen'] as const,
  bilanz: () => [...fibuKeys.all, 'bilanz'] as const,
  guv: () => [...fibuKeys.all, 'guv'] as const,
  bwa: () => [...fibuKeys.all, 'bwa'] as const,
  opVerwaltung: () => [...fibuKeys.all, 'op-verwaltung'] as const,
  stats: () => [...fibuKeys.all, 'stats'] as const,
  cockpit: () => [...fibuKeys.all, 'cockpit'] as const,
  periods: () => [...fibuKeys.all, 'periods'] as const,
  connectorProfiles: (connectorType: 'PAYROLL' | 'ASSET_LEDGER') => [...fibuKeys.all, 'connector-profiles', connectorType] as const,
}

const EMPTY_RECORD: Record<string, unknown> = {}

// ========== HOOKS ==========

// Debitoren Offene Posten
export function useDebitoren(filters?: { ueberfaellig?: boolean; mahn_stufe?: number }) {
  return useQuery({
    queryKey: [...fibuKeys.debitoren(), filters],
    queryFn: async () => {
      const params = new URLSearchParams({ typ: 'debitor' })
      if (filters?.mahn_stufe !== undefined) params.append('mahnstufe', String(filters.mahn_stufe))
      const response = await apiClient.get<{ items: OffenerPosten[]; total: number }>(
        `/api/v1/finance/open-items?${params.toString()}`
      )
      return response.data.items ?? []
    },
    initialData: [],
  })
}

export function useMahnen() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      // Erstellt eine neue Mahnung für den offenen Posten
      const response = await apiClient.post(`/api/v1/finance/dunning`, { op_id: id })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fibuKeys.debitoren() })
    },
  })
}

// Kreditoren Offene Posten
export function useKreditoren(filters?: { zahlbar?: boolean }) {
  return useQuery({
    queryKey: [...fibuKeys.kreditoren(), filters],
    queryFn: async () => {
      const params = new URLSearchParams({ typ: 'kreditor' })
      if (filters?.zahlbar !== undefined) params.append('zahlbar', String(filters.zahlbar))
      const response = await apiClient.get<{ items: OffenerPosten[]; total: number }>(
        `/api/v1/finance/open-items?${params.toString()}`
      )
      return response.data.items ?? []
    },
    initialData: [],
  })
}

export function useZahlungslauf() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (ids: string[]) => {
      const response = await apiClient.post('/api/v1/finance/payment-runs', { op_ids: ids })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fibuKeys.kreditoren() })
      queryClient.invalidateQueries({ queryKey: fibuKeys.opVerwaltung() })
    },
  })
}

// Buchungen (Journal Entries)
export function useBuchungen(filters?: { datum_von?: string; datum_bis?: string; belegart?: string }) {
  return useQuery({
    queryKey: [...fibuKeys.buchungen(), filters],
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (filters?.datum_von) params.entry_date_from = filters.datum_von
      if (filters?.datum_bis) params.entry_date_to = filters.datum_bis
      if (filters?.belegart) params.source = filters.belegart
      const response = await apiClient.get<{ items: any[]; total: number }>(
        '/api/v1/journal-entries', { params }
      )
      return (response.data.items ?? []).map((e: any): Buchung => ({
        id: e.id,
        belegnr: e.entry_number,
        datum: e.posting_date || e.entry_date,
        soll_konto: e.lines?.[0]?.account_id ?? '',
        haben_konto: e.lines?.[1]?.account_id ?? '',
        betrag: Number(e.total_debit || 0),
        text: e.description,
        belegart: e.source || 'MAN',
      }))
    },
    initialData: [],
  })
}

export function useCreateBuchung() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (buchung: Omit<Buchung, 'id'>) => {
      const response = await apiClient.post<{ data: any }>('/api/v1/journal-entries', buchung)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fibuKeys.buchungen() })
      queryClient.invalidateQueries({ queryKey: fibuKeys.konten() })
    },
  })
}

// Kontenplan
export function useKonten(filters?: { typ?: string }) {
  return useQuery({
    queryKey: [...fibuKeys.konten(), filters],
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (filters?.typ) params.account_type = filters.typ
      const response = await apiClient.get<{ items: any[]; total: number }>(
        '/api/v1/chart-of-accounts', { params }
      )
      return (response.data.items ?? []).map((a: any): Konto => ({
        id: a.id,
        kontonummer: a.account_number,
        bezeichnung: a.account_name,
        kontoart: a.category ?? '',
        typ: a.account_type,
        saldo: Number(a.balance ?? 0),
      }))
    },
    initialData: [],
  })
}

export function useKonto(kontonummer: string) {
  return useQuery({
    queryKey: [...fibuKeys.konten(), kontonummer],
    queryFn: async () => {
      const response = await apiClient.get<{ items: any[] }>(
        `/api/v1/chart-of-accounts?account_number=${kontonummer}`
      )
      const a = response.data.items?.[0]
      if (!a) throw new Error(`Konto ${kontonummer} nicht gefunden`)
      return { id: a.id, kontonummer: a.account_number, bezeichnung: a.account_name,
        kontoart: a.category ?? '', typ: a.account_type, saldo: Number(a.balance ?? 0) } as Konto
    },
    enabled: !!kontonummer,
    initialData: null,
  })
}

// Anlagen — kein Backend-Endpoint vorhanden
export function useAnlagen() {
  return useQuery({
    queryKey: fibuKeys.anlagen(),
    queryFn: async () => {
      const response = await apiClient.get<Anlage[]>('/api/v1/finance/fixed-assets')
      return response.data
    },
    initialData: [],
  })
}

export function useCreateAnlage() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (anlage: Omit<Anlage, 'id' | 'kumulierte_afa' | 'buchwert'>) => {
      const response = await apiClient.post<Anlage>('/api/v1/finance/fixed-assets', anlage)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fibuKeys.anlagen() })
    },
  })
}

export function useAfaBerechnung(id: string, jahr = 2025) {
  return useQuery({
    queryKey: [...fibuKeys.anlagen(), id, 'afa', jahr],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/finance/fixed-assets/${id}/depreciation?year=${jahr}`)
      return response.data
    },
    enabled: !!id,
    initialData: null,
  })
}

// Bilanz
export function useBilanz(stichtag = '2024-12-31') {
  return useQuery({
    queryKey: [...fibuKeys.bilanz(), stichtag],
    queryFn: async () => {
      const period = stichtag.substring(0, 7) // YYYY-MM
      const response = await apiClient.get(
        `/api/v1/finance/financial-reports/balance-sheet?period=${period}`
      )
      return response.data
    },
    initialData: EMPTY_RECORD,
  })
}

// GuV
export function useGuV(periode = '2024') {
  return useQuery({
    queryKey: [...fibuKeys.guv(), periode],
    queryFn: async () => {
      const response = await apiClient.get(
        `/api/v1/finance/financial-reports/profit-loss?period=${periode}`
      )
      return response.data
    },
    initialData: EMPTY_RECORD,
  })
}

// BWA
export function useBWA(monat = 10, jahr = 2025) {
  return useQuery({
    queryKey: [...fibuKeys.bwa(), monat, jahr],
    queryFn: async () => {
      const period = `${jahr}-${String(monat).padStart(2, '0')}`
      const response = await apiClient.get(
        `/api/v1/finance/financial-reports/bwa?period=${period}`
      )
      return response.data
    },
    initialData: EMPTY_RECORD,
  })
}

// OP-Verwaltung
export function useOPVerwaltung() {
  return useQuery({
    queryKey: fibuKeys.opVerwaltung(),
    queryFn: async () => {
      const response = await apiClient.get<{ items: OffenerPosten[]; total: number }>(
        '/api/v1/finance/open-items'
      )
      return response.data.items ?? []
    },
    initialData: [],
  })
}

// Stats — kein Backend-Endpoint vorhanden
export function useFibuStats() {
  return useQuery({
    queryKey: fibuKeys.stats(),
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/finance/stats')
      return response.data
    },
    initialData: EMPTY_RECORD,
  })
}

export function useFibuCockpit() {
  return useQuery({
    queryKey: fibuKeys.cockpit(),
    queryFn: async () => {
      const response = await apiClient.get<FibuCockpitReadModel>('/api/v1/finance/followup/fibu/cockpit')
      return response.data
    },
    initialData: {
      tenant_id: '',
      schema_version: 1,
      master_data: {
        dunning_parameters_ready: false,
        interest_groups_ready: false,
        connector_profile_count: 0,
        connector_profiles: [],
      },
      dunning: {
        open_items: 0,
        overdue_items: 0,
        overdue_amount: 0,
        dunning_items: 0,
      },
      interest: {
        candidate_count: 0,
        candidate_amount: 0,
      },
      creditor: {
        open_items: 0,
        payable_items: 0,
        open_amount: 0,
        overdue_amount: 0,
      },
      tax: {
        vat_return_count: 0,
        validated_count: 0,
        approved_count: 0,
        submitted_count: 0,
        latest_period: null,
        latest_submission_at: null,
        e_bilanz_ready: false,
        e_clearing_ready: false,
      },
      exports: [],
      annual_close: {
        open_item_count: 0,
        overdue_item_count: 0,
        recent_journal_entries: 0,
        latest_vat_period: null,
        ready_for_year_close: false,
      },
      revision: {
        recent_journal_entries: 0,
        last_entry_date: null,
        export_runs: 0,
      },
    } satisfies FibuCockpitReadModel,
    staleTime: 60 * 1000,
  })
}

export function useAccountingPeriods(status?: 'OPEN' | 'CLOSED' | 'ADJUSTING') {
  return useQuery({
    queryKey: [...fibuKeys.periods(), status ?? 'all'],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (status) {
        params.set('status', status)
      }
      const suffix = params.size > 0 ? `?${params.toString()}` : ''
      const response = await apiClient.get<AccountingPeriod[]>(`/api/v1/finance/periods/${suffix}`)
      return Array.isArray(response.data) ? response.data : []
    },
    initialData: [],
  })
}

export function useFibuConnectorProfiles(connectorType: 'PAYROLL' | 'ASSET_LEDGER') {
  return useQuery({
    queryKey: fibuKeys.connectorProfiles(connectorType),
    queryFn: async () => {
      const response = await apiClient.get<FibuConnectorProfile[]>(
        `/api/v1/connectors/profiles?type=${connectorType}`
      )
      return Array.isArray(response.data) ? response.data : []
    },
    initialData: [],
  })
}

// DATEV Export — kein Backend-Endpoint vorhanden
export function useDATEVExport() {
  return useMutation({
    mutationFn: async (params: { typ: string; datum_von?: string; datum_bis?: string }) => {
      const searchParams = new URLSearchParams({ typ: params.typ })
      if (params.datum_von) searchParams.append('datum_von', params.datum_von)
      if (params.datum_bis) searchParams.append('datum_bis', params.datum_bis)
      const response = await apiClient.get(`/api/v1/finance/export/datev?${searchParams.toString()}`)
      return response.data
    },
  })
}

// ── Extended Types ──────────────────────────────────────────────────────

export type Kreditlinie = {
  id: string; kunde: string; kundennr: string; limit: number; ausgenutzt: number; verfuegbar: number
  bonitaet: 'A' | 'B' | 'C' | 'D'; zahlungsziel: number; offenePosten: number; ueberfaellig: number
  status: 'aktiv' | 'gesperrt' | 'ueberzogen'
}

export type Sicherheit = {
  id: string; typ: 'abtretung' | 'sicherungseigentum' | 'buergschaft' | 'pfandrecht'
  kunde: string; kundennr: string; gegenstand: string; wert: number
  datumErstellung: string; gueltigBis?: string; status: 'aktiv' | 'abgelaufen' | 'freigegeben'
  kreditlinie: number; ausgenutzt: number
}

export type Verbindlichkeit = {
  id: string; rechnungsNr: string; lieferant: string; rechnungsDatum: string; faelligAm: string
  betrag: number; offen: number; status: 'offen' | 'teilbezahlt' | 'bezahlt' | 'skontofaehig'
}

export type Zahlungsvorschlag = {
  id: string; rechnungsNr: string; lieferant: string; betrag: number; faelligAm: string
  skonto: number; skontoBis: string; vorschlag: 'skonto' | 'faellig' | 'spaeter'; prioritaet: number
}

export type HauptbuchBuchung = {
  id: string; datum: string; belegnummer: string; konto: string; text: string; soll: number; haben: number
}

export type AnlageDetail = {
  id: string; anlagennr: string; bezeichnung: string; anschaffung: string; anschaffungswert: number
  nutzungsdauer: number; afaSatz: number; kumulierteAfa: number; buchwert: number
}

export type DebitOP = {
  id: string; rechnungsnr: string; kunde: string; kundennr: string; datum: string; faelligkeit: string
  betrag: number; offen: number; ueberfaellig: boolean; mahnStufe: number
}

export type KreditOP = {
  id: string; rechnungsnr: string; lieferant: string; lieferantennr: string; datum: string; faelligkeit: string
  betrag: number; offen: number; skonto: number; skontoBis: string; zahlbar: boolean
}

// ── Extended Hooks ──────────────────────────────────────────────────────

export function useAnlagenDetail() {
  return useQuery({
    queryKey: [...fibuKeys.anlagen(), 'detail'],
    queryFn: async () => {
      const response = await apiClient.get<AnlageDetail[]>('/api/v1/finance/fixed-assets/detail')
      return response.data
    },
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function useDebitorenOP() {
  return useQuery({
    queryKey: [...fibuKeys.debitoren(), 'op'],
    queryFn: async () => {
      const response = await apiClient.get<{ items: any[]; total: number }>(
        '/api/v1/finance/open-items?typ=debitor'
      )
      return (response.data.items ?? []).map((item: any): DebitOP => ({
        id: item.id,
        rechnungsnr: item.beleg_nummer ?? item.rechnungsnr ?? '',
        kunde: item.partner_name ?? item.kunde_name ?? '',
        kundennr: item.debitor_id ?? '',
        datum: item.faellig_am ?? '',
        faelligkeit: item.faellig_am ?? '',
        betrag: Number(item.betrag ?? 0),
        offen: Number(item.offen ?? 0),
        ueberfaellig: new Date(item.faellig_am) < new Date(),
        mahnStufe: Number(item.mahnstufe ?? 0),
      }))
    },
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function useKreditorenOP() {
  return useQuery({
    queryKey: [...fibuKeys.kreditoren(), 'op'],
    queryFn: async () => {
      const response = await apiClient.get<{ items: any[]; total: number }>(
        '/api/v1/finance/open-items?typ=kreditor'
      )
      return (response.data.items ?? []).map((item: any): KreditOP => ({
        id: item.id,
        rechnungsnr: item.beleg_nummer ?? item.rechnungsnr ?? '',
        lieferant: item.partner_name ?? item.lieferant_name ?? '',
        lieferantennr: item.kreditor_id ?? '',
        datum: item.faellig_am ?? '',
        faelligkeit: item.faellig_am ?? '',
        betrag: Number(item.betrag ?? 0),
        offen: Number(item.offen ?? 0),
        skonto: 0,
        skontoBis: '',
        zahlbar: true,
      }))
    },
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export { useHauptbuchBuchungen as useHauptbuch }

export function useHauptbuchBuchungen() {
  return useQuery({
    queryKey: [...fibuKeys.buchungen(), 'hauptbuch'],
    queryFn: async () => {
      const response = await apiClient.get<{ items: any[]; total: number }>('/api/v1/journal-entries')
      return (response.data.items ?? []).map((e: any): HauptbuchBuchung => ({
        id: e.id,
        datum: e.posting_date || e.entry_date,
        belegnummer: e.entry_number,
        konto: e.lines?.[0]?.account_id ?? '',
        text: e.description,
        soll: Number(e.total_debit ?? 0),
        haben: Number(e.total_credit ?? 0),
      }))
    },
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function useKreditlinien() {
  return useQuery({
    queryKey: [...fibuKeys.all, 'kreditlinien'],
    queryFn: async () => {
      const response = await apiClient.get<Kreditlinie[]>('/api/v1/finance/credit-limits')
      return response.data
    },
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function useSicherheiten() {
  return useQuery({
    queryKey: [...fibuKeys.all, 'sicherheiten'],
    queryFn: async () => {
      const response = await apiClient.get<Sicherheit[]>('/api/v1/finance/collaterals')
      return response.data
    },
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function useVerbindlichkeiten() {
  return useQuery({
    queryKey: [...fibuKeys.all, 'verbindlichkeiten'],
    queryFn: async () => {
      const response = await apiClient.get<{ items: any[]; total: number }>(
        '/api/v1/finance/open-items?typ=kreditor'
      )
      return (response.data.items ?? []).map((item: any): Verbindlichkeit => ({
        id: item.id,
        rechnungsNr: item.beleg_nummer ?? '',
        lieferant: item.partner_name ?? '',
        rechnungsDatum: item.faellig_am ?? '',
        faelligAm: item.faellig_am ?? '',
        betrag: Number(item.betrag ?? 0),
        offen: Number(item.offen ?? 0),
        status: Number(item.offen ?? 0) === 0 ? 'bezahlt' : 'offen',
      }))
    },
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

export function useZahlungsvorschlaege() {
  return useQuery({
    queryKey: [...fibuKeys.all, 'zahlungsvorschlaege'],
    queryFn: async () => {
      const response = await apiClient.get<Zahlungsvorschlag[]>('/api/v1/finance/payment-suggestions')
      return response.data
    },
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}

// ── UStVA / ELSTER (VAT Return) ────────────────────────────────────────────

export type VATReturn = {
  id: string
  period: string
  return_type: string
  taxpayer_name: string
  tax_id?: string
  vat_id?: string
  total_sales_net: number
  total_input_tax: number
  total_output_tax: number
  vat_payable: number
  positions: Array<{
    position_code: string
    description: string
    net_amount: number
    tax_amount: number
    tax_rate: number
  }>
  status: 'draft' | 'calculated' | 'validated' | 'submitted'
  calculated_at?: string
  validated_at?: string
  submitted_at?: string
  notes?: string
  created_at: string
  updated_at: string
}

export const vatReturnKeys = {
  all: ['fibu', 'vat-return'] as const,
  list: (period?: string) => [...vatReturnKeys.all, period ?? 'all'] as const,
}

export function useVATReturns(period?: string, tenantId = 'system') {
  return useQuery({
    queryKey: vatReturnKeys.list(period),
    queryFn: async () => {
      const params = new URLSearchParams({ tenant_id: tenantId })
      if (period) params.append('period', period)
      const response = await apiClient.get<VATReturn[]>(
        `/api/v1/finance/vat-return?${params.toString()}`
      )
      return Array.isArray(response.data) ? response.data : []
    },
    initialData: [],
  })
}

export function useCalculateVATReturn() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (params: { period: string; tenant_id?: string }) => {
      const response = await apiClient.post<VATReturn>(
        '/api/v1/finance/vat-return/calculate',
        { period: params.period, tenant_id: params.tenant_id ?? 'system' }
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: vatReturnKeys.all })
    },
  })
}

/** ELSTER-XML herunterladen (nutzt apiClient → Auth wird automatisch mitgesendet). */
export async function downloadELSTERXml(returnId: string, period: string, tenantId = 'system'): Promise<void> {
  const url = `/api/v1/finance/vat-return/${returnId}/elster-xml?tenant_id=${tenantId}`
  const res = await apiClient.get<Blob>(url, { responseType: 'blob' } as Record<string, unknown>)
  const blob = res.data as unknown as Blob
  const disposition = (res as { headers?: Record<string, string> }).headers?.['content-disposition']
  const filename = disposition?.match(/filename="?([^";\n]+)"?/)?.[1] ?? `UStVA_${period}_ELSTER.xml`
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = filename
  a.click()
  URL.revokeObjectURL(a.href)
}
