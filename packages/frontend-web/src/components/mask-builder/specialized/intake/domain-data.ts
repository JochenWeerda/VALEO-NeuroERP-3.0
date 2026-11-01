import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/hooks/useAuth'
import { auth } from '@/lib/auth'
import { tenantFromToken } from '@/lib/tenant-from-token'
import { apiClient } from '@/lib/api-client'
import { inventoryExtraKeys, type LKWEintrag } from '@/lib/api/inventory'
import type { AgrarContract, WeighingTicket } from '@/lib/api/weighing-tickets'
import type { SupplyChainOverview } from '@/lib/api/supply-chain'

export function useDomainIdentity() {
  const { user } = useAuth()
  return { tenantId: tenantFromToken(auth.getAccessToken()), actor: user?.sub }
}

export function useDomainQueue() {
  const identity = useDomainIdentity()
  return useQuery({ queryKey: [...inventoryExtraKeys.warteschlange(), identity], enabled: Boolean(identity.tenantId && identity.actor),
    queryFn: async () => (await apiClient.get<{ items: LKWEintrag[]; total: number }>('/api/v1/annahme/warteschlange')).data, refetchInterval: 30000 })
}
export function useDomainQueueEntry(id: string | undefined) {
  const identity = useDomainIdentity()
  return useQuery({ queryKey: [...inventoryExtraKeys.warteschlange(), identity, id], enabled: Boolean(id && identity.tenantId && identity.actor),
    queryFn: async () => (await apiClient.get<LKWEintrag>(`/api/v1/annahme/warteschlange/${encodeURIComponent(id!)}`)).data })
}
export function useDomainTickets() {
  const identity = useDomainIdentity()
  return useQuery({ queryKey: ['weighing-tickets', identity, { limit: 100 }], enabled: Boolean(identity.tenantId && identity.actor),
    queryFn: async () => (await apiClient.get<{ items: WeighingTicket[] }>('/api/v1/weighing-tickets?limit=100')).data })
}
export function useDomainContracts() {
  const identity = useDomainIdentity()
  return useQuery({ queryKey: ['agrar-contracts', 'open', identity], enabled: Boolean(identity.tenantId && identity.actor),
    queryFn: async () => (await apiClient.get<{ items: AgrarContract[] }>('/api/v1/agrar/contracts?status=open&limit=100')).data.items })
}
export function useDomainSupplyChain() {
  const identity = useDomainIdentity()
  return useQuery({ queryKey: ['supply-chain', 'overview', identity], enabled: Boolean(identity.tenantId && identity.actor), queryFn: async (): Promise<SupplyChainOverview> => {
    const [queue, tickets, charges, freight] = await Promise.all([
      apiClient.get<{ items: LKWEintrag[] }>('/api/v1/annahme/warteschlange'),
      apiClient.get<{ items: WeighingTicket[] }>('/api/v1/weighing-tickets?limit=100'),
      apiClient.get<{ items: Array<{ artikel: string; status: string }> }>('/api/v1/chargen'),
      apiClient.get<Array<{ status: string; kennzeichen?: string | null }>>('/api/v1/logistik/frachtbriefe'),
    ])
    const waiting = queue.data.items, weighing = tickets.data.items, lots = charges.data.items, transport = freight.data
    return { waitingInbound: waiting.length, weighingTickets: weighing.length,
      openWeighingTickets: weighing.filter(ticket => ticket.status !== 'closed').length,
      charges: lots.length, blockedCharges: lots.filter(lot => ['gesperrt', 'in-pruefung'].includes(lot.status)).length,
      freightLetters: transport.length, freightInTransit: transport.filter(row => row.status === 'unterwegs').length,
      chargeArticles: [...new Set(lots.map(lot => lot.artikel).filter(Boolean))].slice(0, 6),
      activeVehiclePlates: [...new Set([...waiting.map(row => row.kennzeichen), ...weighing.map(row => row.vehicle_plate), ...transport.map(row => row.kennzeichen)].filter((plate): plate is string => Boolean(plate)))],
    }
  } })
}
