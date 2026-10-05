import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useTenant } from '@/hooks/useTenant'
import type { BankAccount, BankLedgerOption } from './bank-contracts'

export function useBankOptions() {
  const { tenantId } = useTenant()
  return useQuery({
    queryKey: ['finance', 'bank-options', tenantId],
    queryFn: async () => (await apiClient.get<BankAccount[]>('/api/v1/finance/bank-accounts', {
      params: { is_active: true, limit: 500 },
    })).data,
  })
}

export function useBankLedgerOptions() {
  const { tenantId } = useTenant()
  return useQuery({
    queryKey: ['finance', 'bank-ledger-options', tenantId],
    queryFn: async () => (await apiClient.get<BankLedgerOption[]>('/api/v1/finance/bank-accounts/ledger-options', {
      params: { limit: 200 },
    })).data,
  })
}
