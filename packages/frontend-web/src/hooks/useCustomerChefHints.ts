import { useQuery } from '@tanstack/react-query'
import { fetchCustomerChefHints, type CustomerChefHints } from '@/lib/crm/fetch-customer-chef-hints'

export function useCustomerChefHints(opts: {
  customerNumber: string | undefined | null
  crmCustomerId: string | undefined | null
  chefanweisungFromCustomer?: string | null
  enabled?: boolean
}): {
  data: CustomerChefHints | undefined
  isLoading: boolean
  isError: boolean
} {
  const enabled =
    opts.enabled !== false &&
    Boolean(opts.crmCustomerId?.trim() || opts.customerNumber?.trim())

  const q = useQuery({
    queryKey: [
      'customer-chef-hints',
      opts.crmCustomerId ?? '',
      opts.customerNumber ?? '',
      opts.chefanweisungFromCustomer ?? '',
    ],
    queryFn: () =>
      fetchCustomerChefHints({
        customerNumber: opts.customerNumber,
        crmCustomerId: opts.crmCustomerId,
        chefanweisungFromCustomer: opts.chefanweisungFromCustomer,
      }),
    enabled,
    staleTime: 60_000,
  })

  return {
    data: q.data,
    isLoading: q.isLoading,
    isError: q.isError,
  }
}
