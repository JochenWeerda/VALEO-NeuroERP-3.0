/** Canonical bank API amounts are decimal strings; missing evidence is null. */
export type BankAccountPayload = {
  account_number: string
  bank_name: string
  iban: string | null
  bic: string | null
  currency: string
  is_active: boolean
  gl_account_id: string | null
}
export type BankAccount = BankAccountPayload & {
  id: string
  tenant_id: string
  balance: string | null
}
export type BankLedgerOption = { id: string; account_number: string; account_name: string }
export type BankComparison = {
  bank_statement_balance: string | null
  accounting_balance: string | null
  difference: string | null
  is_balanced: boolean
  statement_date: string
  comparison_date: string
  currency: string
  ledger_account_id: string | null
  bank_balance_state: 'BANK_PROVIDED' | 'CSV_SYNTHETIC'
  accounting_state: 'AVAILABLE' | 'MAPPING_REQUIRED' | 'NO_POSTED_ENTRIES'
}
export type BankReconciliationResult = {
  statement_id: string
  bank_account_id: string
  balance_comparison: BankComparison
  line_counts: { total: number; matched: number; unmatched: number; partial: number; unknown: number }
  comparison_state: 'INCOMPLETE' | 'DIFFERENCES' | 'BALANCES_EQUAL'
  total_differences: number
  differences: unknown[]
  can_be_booked: false
  differences_offset: number
  differences_limit: number
}
