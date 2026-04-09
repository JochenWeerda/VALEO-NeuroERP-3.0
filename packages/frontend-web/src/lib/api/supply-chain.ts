import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type SupplyChainOverview = {
  waitingInbound: number
  weighingTickets: number
  openWeighingTickets: number
  charges: number
  blockedCharges: number
  freightLetters: number
  freightInTransit: number
  chargeArticles: string[]
  activeVehiclePlates: string[]
}

export function useSupplyChainOverview() {
  return useQuery({
    queryKey: ['supply-chain', 'overview'],
    queryFn: async (): Promise<SupplyChainOverview> => {
      const [queueRes, weighingRes, chargesRes, freightRes] = await Promise.all([
        apiClient.get<{ items: Array<{ kennzeichen?: string | null }> }>('/api/v1/annahme/warteschlange'),
        apiClient.get<{ items: Array<{ ticket_number: string; status: string; vehicle_plate?: string | null }> }>('/api/v1/weighing-tickets?limit=100'),
        apiClient.get<{ items: Array<{ artikel: string; status: string }> }>('/api/v1/chargen'),
        apiClient.get<Array<{ nummer: string; status: string; kennzeichen?: string | null }>>('/api/v1/logistik/frachtbriefe'),
      ])

      const waiting = queueRes.data.items ?? []
      const weighings = weighingRes.data.items ?? []
      const charges = chargesRes.data.items ?? []
      const freight = freightRes.data ?? []
      const activeVehiclePlates = Array.from(
        new Set(
          [
            ...waiting.map((item) => item.kennzeichen).filter(Boolean),
            ...weighings.map((item) => item.vehicle_plate).filter(Boolean),
            ...freight.map((item) => item.kennzeichen).filter(Boolean),
          ].map((item) => String(item)),
        ),
      )

      return {
        waitingInbound: waiting.length,
        weighingTickets: weighings.length,
        openWeighingTickets: weighings.filter((item) => item.status !== 'closed').length,
        charges: charges.length,
        blockedCharges: charges.filter((item) => item.status === 'gesperrt' || item.status === 'in-pruefung').length,
        freightLetters: freight.length,
        freightInTransit: freight.filter((item) => item.status === 'unterwegs').length,
        chargeArticles: Array.from(new Set(charges.map((item) => item.artikel).filter(Boolean))).slice(0, 6),
        activeVehiclePlates,
      }
    },
    initialData: {
      waitingInbound: 0,
      weighingTickets: 0,
      openWeighingTickets: 0,
      charges: 0,
      blockedCharges: 0,
      freightLetters: 0,
      freightInTransit: 0,
      chargeArticles: [],
      activeVehiclePlates: [],
    } satisfies SupplyChainOverview,
    staleTime: 30_000,
  })
}
