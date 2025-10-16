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
  created_at: string
  updated_at: string
}

export interface AccountCreate {
  tenant_id: string
  account_number: string
  account_name: string
  account_type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense'
  category: string
  currency?: string
  allow_manual_entries?: boolean
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
    }>('/api/v1/finance/chart-of-accounts/', { params })
    return response.data
  },

  async getAccount(id: string) {
    const response = await apiClient.get<{ data: Account }>(`/api/v1/finance/chart-of-accounts/${id}`)
    return response.data.data
  },

  async createAccount(data: AccountCreate) {
    const response = await apiClient.post<{ data: Account }>('/api/v1/finance/chart-of-accounts/', data)
    return response.data.data
  },

  async updateAccount(id: string, data: AccountUpdate) {
    const response = await apiClient.put<{ data: Account }>(`/api/v1/finance/chart-of-accounts/${id}`, data)
    return response.data.data
  },

  async deleteAccount(id: string) {
    await apiClient.delete(`/api/v1/finance/chart-of-accounts/${id}`)
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
    }>('/api/v1/finance/journal-entries/', { params })
    return response.data
  },

  async getJournalEntry(id: string) {
    const response = await apiClient.get<{ data: JournalEntry }>(`/api/v1/finance/journal-entries/${id}`)
    return response.data.data
  },

  async createJournalEntry(data: Omit<JournalEntry, 'id' | 'created_at' | 'updated_at' | 'lines'> & {
    lines: Omit<JournalEntryLine, 'id' | 'tenant_id' | 'journal_entry_id' | 'created_at' | 'updated_at'>[]
  }) {
    const response = await apiClient.post<{ data: JournalEntry }>('/api/v1/finance/journal-entries/', data)
    return response.data.data
  },

  async updateJournalEntry(id: string, data: Partial<Pick<JournalEntry, 'entry_date' | 'posting_date' | 'description' | 'reference'>>) {
    const response = await apiClient.put<{ data: JournalEntry }>(`/api/v1/finance/journal-entries/${id}`, data)
    return response.data.data
  },

  async postJournalEntry(id: string) {
    const response = await apiClient.post<{ data: JournalEntry }>(`/api/v1/finance/journal-entries/${id}/post`)
    return response.data.data
  },

  async deleteJournalEntry(id: string) {
    await apiClient.delete(`/api/v1/finance/journal-entries/${id}`)
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
  }
}