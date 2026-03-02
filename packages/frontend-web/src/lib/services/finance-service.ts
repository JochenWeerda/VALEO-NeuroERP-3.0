/**
 * Finance Service
 * API service for finance operations (Chart of Accounts, Journal Entries, etc.)
 */

import { apiClient } from '../api-client'

// Types
export interface Account {
  id: string
  tenant_id: string
  account_number: string
  account_name: string
  account_type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense'
  category: string
  currency: string
  balance: number
  allow_manual_entries: boolean
  is_active: boolean
  parent_account_id?: string | null
  created_at: string
  updated_at: string
}

export interface AccountHierarchy extends Account {
  children: AccountHierarchy[]
}

export interface AccountCreate {
  tenant_id: string
  account_number: string
  account_name: string
  account_type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense'
  category: string
  currency?: string
  allow_manual_entries?: boolean
  parent_account_id?: string | null
}

export interface AccountUpdate {
  account_name?: string
  account_type?: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense'
  category?: string
  currency?: string
  allow_manual_entries?: boolean
}

export interface JournalEntry {
  id: string
  tenant_id: string
  entry_number: string
  entry_date: string
  posting_date: string
  description: string
  reference?: string
  source: string
  currency: string
  status: string
  total_debit: number
  total_credit: number
  posted_by?: string
  posted_at?: string
  reversal_of?: string
  reversal_date?: string
  created_at: string
  updated_at: string
  lines: JournalEntryLine[]
}

export interface JournalEntryLine {
  id: string
  tenant_id: string
  journal_entry_id: string
  account_id: string
  debit_amount: number
  credit_amount: number
  line_number: number
  description?: string
  tax_code?: string
  tax_amount: number
  cost_center?: string
  profit_center?: string
  segment?: string
  created_at: string
  updated_at: string
}

// ─── Report-Typen ───────────────────────────────────────────────────────────

export interface BalanceSheetItem {
  account_number: string
  account_name: string
  account_type: string
  balance: number
  level: number
}

export interface BalanceSheet {
  period: string
  as_of_date: string
  assets: BalanceSheetItem[]
  liabilities: BalanceSheetItem[]
  equity: BalanceSheetItem[]
  total_assets: number
  total_liabilities: number
  total_equity: number
  is_balanced: boolean
}

export interface ProfitLossItem {
  account_number: string
  account_name: string
  account_type: string
  amount: number
  level: number
}

export interface ProfitLoss {
  period: string
  revenue: ProfitLossItem[]
  expenses: ProfitLossItem[]
  total_revenue: number
  total_expenses: number
  net_income: number
}

export interface BWAItem {
  position: string
  description: string
  current_period: number
  previous_period: number
  year_to_date: number
  percentage: number
}

export interface BWA {
  period: string
  items: BWAItem[]
  total_revenue: number
  total_costs: number
  net_result: number
}

// ─── OP / Dunning / Zahlungen Typen ────────────────────────────────────────

export interface OpenItem {
  id: string
  beleg_nummer: string
  debitor_id?: string
  kreditor_id?: string
  partner_name?: string
  betrag: number
  offen: number
  faellig_am: string
  mahnstufe: number
  waehrung: string
  typ: 'rechnung' | 'gutschrift' | 'anzahlung'
}

export interface DunningNotice {
  id: string
  op_id: string
  debitor_id: string
  mahnstufe: number
  mahn_datum: string
  faelligkeit: string
  betrag: number
  mahngebuehr: number
  status: 'erstellt' | 'versendet' | 'bezahlt' | 'inkasso'
}

export interface PaymentRunItem {
  id: string
  kreditor_id: string
  kreditor_name: string
  betrag: number
  faellig_am: string
  bank_iban: string
  bank_bic: string
  status: 'offen' | 'geplant' | 'ausgefuehrt' | 'storniert'
}

export interface PaymentRun {
  id: string
  lauf_nummer: string
  ausfuehrungs_datum: string
  gesamt_betrag: number
  anzahl_zahlung: number
  status: 'entwurf' | 'freigegeben' | 'ausgefuehrt' | 'storniert'
  positionen: PaymentRunItem[]
}

export interface AccountingPeriod {
  id: string
  periode: string  // YYYY-MM
  bezeichnung: string
  status: 'offen' | 'geschlossen' | 'gesperrt'
  abschluss_datum?: string
}

// API Functions
export const financeService = {
  // Chart of Accounts
  async getAccounts(params?: {
    tenant_id?: string
    search?: string
    skip?: number
    limit?: number
  }) {
    const response = await apiClient.get<{
      items: Account[]
      total: number
      page: number
      size: number
      pages: number
      has_next: boolean
      has_prev: boolean
    }>('/api/v1/chart-of-accounts/', { params })
    return response.data
  },

  async getAccountsHierarchy(params?: {
    tenant_id?: string
    account_type?: string
  }): Promise<AccountHierarchy[]> {
    const response = await apiClient.get<AccountHierarchy[]>('/api/v1/accounts/hierarchy', { params })
    return response.data
  },

  async getAccount(id: string) {
    const response = await apiClient.get<{ data: Account }>(`/api/v1/chart-of-accounts/${id}`)
    return response.data.data
  },

  async createAccount(data: AccountCreate) {
    const response = await apiClient.post<{ data: Account }>('/api/v1/chart-of-accounts/', data)
    return response.data.data
  },

  async updateAccount(id: string, data: AccountUpdate) {
    const response = await apiClient.put<{ data: Account }>(`/api/v1/chart-of-accounts/${id}`, data)
    return response.data.data
  },

  async deleteAccount(id: string) {
    await apiClient.delete(`/api/v1/chart-of-accounts/${id}`)
  },

  // Journal Entries
  async getJournalEntries(params?: {
    tenant_id?: string
    search?: string
    status?: string
    skip?: number
    limit?: number
  }) {
    const response = await apiClient.get<{
      items: JournalEntry[]
      total: number
      page: number
      size: number
      pages: number
      has_next: boolean
      has_prev: boolean
    }>('/api/v1/journal-entries/', { params })
    return response.data
  },

  async getJournalEntry(id: string) {
    const response = await apiClient.get<{ data: JournalEntry }>(`/api/v1/journal-entries/${id}`)
    return response.data.data
  },

  async createJournalEntry(data: Omit<JournalEntry, 'id' | 'created_at' | 'updated_at' | 'lines'> & {
    lines: Omit<JournalEntryLine, 'id' | 'tenant_id' | 'journal_entry_id' | 'created_at' | 'updated_at'>[]
  }) {
    const response = await apiClient.post<{ data: JournalEntry }>('/api/v1/journal-entries/', data)
    return response.data.data
  },

  async updateJournalEntry(id: string, data: Partial<Pick<JournalEntry, 'entry_date' | 'posting_date' | 'description' | 'reference'>>) {
    const response = await apiClient.put<{ data: JournalEntry }>(`/api/v1/journal-entries/${id}`, data)
    return response.data.data
  },

  async postJournalEntry(id: string) {
    const response = await apiClient.post<{ data: JournalEntry }>(`/api/v1/journal-entries/${id}/post`)
    return response.data.data
  },

  async deleteJournalEntry(id: string) {
    await apiClient.delete(`/api/v1/journal-entries/${id}`)
  },

  async reverseJournalEntry(id: string, reason: string) {
    const response = await apiClient.post<{
      message: string
      original_entry_id: string
      reversal_entry_id: string
    }>(`/api/v1/journal-entries/${id}/reverse`, null, {
      params: { reason },
    })
    return response.data
  },

  // Utility functions
  getAccountTypeLabel(type: string): string {
    const labels = {
      asset: 'Aktiva',
      liability: 'Passiva',
      equity: 'Eigenkapital',
      revenue: 'Erlöse',
      expense: 'Aufwendungen'
    }
    return labels[type as keyof typeof labels] || type
  },

  getAccountCategoryLabel(category: string): string {
    const labels = {
      current_assets: 'Umlaufvermögen',
      fixed_assets: 'Anlagevermögen',
      current_liabilities: 'Kurzfristige Verbindlichkeiten',
      long_term_liabilities: 'Langfristige Verbindlichkeiten',
      equity: 'Eigenkapital',
      revenue: 'Erlöse',
      cost_of_goods_sold: 'Wareneinsatz',
      operating_expenses: 'Betriebliche Aufwendungen',
      other_expenses: 'Sonstige Aufwendungen'
    }
    return labels[category as keyof typeof labels] || category
  },

  formatCurrency(amount: number, currency = 'EUR'): string {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency
    }).format(amount)
  },

  validateJournalEntry(lines: JournalEntryLine[]): { isValid: boolean; errors: string[] } {
    const errors: string[] = []
    let totalDebit = 0
    let totalCredit = 0

    if (lines.length < 2) {
      errors.push('Buchung muss mindestens 2 Zeilen haben')
    }

    lines.forEach((line, index) => {
      if (line.debit_amount > 0 && line.credit_amount > 0) {
        errors.push(`Zeile ${index + 1}: Soll und Haben können nicht beide gefüllt sein`)
      }
      if (line.debit_amount === 0 && line.credit_amount === 0) {
        errors.push(`Zeile ${index + 1}: Mindestens Soll oder Haben muss gefüllt sein`)
      }

      totalDebit += line.debit_amount
      totalCredit += line.credit_amount
    })

    if (Math.abs(totalDebit - totalCredit) > 0.01) {
      errors.push(`Buchung ist nicht ausgeglichen. Soll: ${totalDebit}, Haben: ${totalCredit}`)
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  },

  // ─── Reports ─────────────────────────────────────────────────────────────

  async getBilanz(params: { period: string; tenant_id?: string }): Promise<BalanceSheet> {
    const p = new URLSearchParams({ period: params.period, tenant_id: params.tenant_id || 'system' })
    const response = await apiClient.get<BalanceSheet>(`/api/v1/finance/financial-reports/balance-sheet?${p}`)
    return response.data
  },

  async getGuV(params: { period: string; tenant_id?: string }): Promise<ProfitLoss> {
    const p = new URLSearchParams({ period: params.period, tenant_id: params.tenant_id || 'system' })
    const response = await apiClient.get<ProfitLoss>(`/api/v1/finance/financial-reports/profit-loss?${p}`)
    return response.data
  },

  async getBwa(params: { period: string; tenant_id?: string }): Promise<BWA> {
    const p = new URLSearchParams({ period: params.period, tenant_id: params.tenant_id || 'system' })
    const response = await apiClient.get<BWA>(`/api/v1/finance/financial-reports/bwa?${p}`)
    return response.data
  },

  // ─── Offene Posten ───────────────────────────────────────────────────────

  async getOffenePostenDebitoren(params?: { tenant_id?: string; skip?: number; limit?: number }): Promise<{ items: OpenItem[]; total: number }> {
    const response = await apiClient.get<{ items: OpenItem[]; total: number }>(
      '/api/v1/finance/open-items', { params: { typ: 'debitor', ...(params || {}) } }
    )
    return response.data
  },

  async getOffenePostenKreditoren(params?: { tenant_id?: string; skip?: number; limit?: number }): Promise<{ items: OpenItem[]; total: number }> {
    const response = await apiClient.get<{ items: OpenItem[]; total: number }>(
      '/api/v1/finance/open-items', { params: { typ: 'kreditor', ...(params || {}) } }
    )
    return response.data
  },

  // ─── Mahnwesen ───────────────────────────────────────────────────────────

  async getMahnungen(params?: { status?: string; skip?: number; limit?: number }): Promise<{ items: DunningNotice[]; total: number }> {
    const response = await apiClient.get<{ items: DunningNotice[]; total: number }>(
      '/api/v1/finance/dunning', { params }
    )
    return response.data
  },

  async createMahnung(data: Partial<DunningNotice>): Promise<DunningNotice> {
    const response = await apiClient.post<DunningNotice>('/api/v1/finance/dunning', data)
    return response.data
  },

  async sendMahnung(id: string): Promise<void> {
    await apiClient.post(`/api/v1/finance/dunning/${id}/send`, null)
  },

  // ─── Zahlungsläufe ───────────────────────────────────────────────────────

  async getZahlungslaeufe(params?: { status?: string; skip?: number; limit?: number }): Promise<{ items: PaymentRun[]; total: number }> {
    const response = await apiClient.get<{ items: PaymentRun[]; total: number }>(
      '/api/v1/finance/payment-runs', { params }
    )
    return response.data
  },

  async createZahlungslauf(data: Partial<PaymentRun>): Promise<PaymentRun> {
    const response = await apiClient.post<PaymentRun>('/api/v1/finance/payment-runs', data)
    return response.data
  },

  async executeZahlungslauf(id: string): Promise<PaymentRun> {
    const response = await apiClient.post<PaymentRun>(`/api/v1/finance/payment-runs/${id}/execute`, null)
    return response.data
  },

  // ─── Perioden ────────────────────────────────────────────────────────────

  async getPerioden(params?: { status?: string }): Promise<AccountingPeriod[]> {
    const response = await apiClient.get<AccountingPeriod[]>('/api/v1/finance/periods', { params })
    return response.data
  },

  async closePeriode(id: string): Promise<AccountingPeriod> {
    const response = await apiClient.post<AccountingPeriod>(`/api/v1/finance/periods/${id}/close`, null)
    return response.data
  },
}