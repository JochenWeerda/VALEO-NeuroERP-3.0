import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type SalesEligibility = {
  linked: boolean
  partner_id?: string
  allowed_order: boolean
  allowed_delivery: boolean
  allowed_invoice: boolean
  reasons: string[]
}

export function useCustomerSalesEligibility(crmCustomerId: string | undefined | null): {
  data: SalesEligibility | undefined
  isLoading: boolean
} {
  const q = useQuery({
    queryKey: ['customer-sales-eligibility', crmCustomerId ?? ''],
    queryFn: async () => {
      const res = await apiClient.get<SalesEligibility>(
        `/api/v1/crm/customers/${crmCustomerId}/sales-eligibility`,
      )
      return res.data
    },
    enabled: Boolean(crmCustomerId?.trim()),
    staleTime: 30_000,
  })
  return { data: q.data, isLoading: q.isLoading }
}
