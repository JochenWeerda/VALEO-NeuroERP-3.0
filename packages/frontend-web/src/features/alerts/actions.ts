import { useMcpMutation } from "@/lib/mcp"

type PriceAdjustInput = {
  sku?: string
  deltaPct: number
}

type ReorderInput = {
  sku?: string
  qty: number
}

type NotifySalesInput = {
  topic: string
  message: string
}

type ActionResponse = {
  ok: boolean
}

/**
 * Custom Hook für Alert-Actions
 * Stellt MCP-Mutations für verschiedene Workflows bereit
 */
export function useAlertActions(): {
  priceAdjust: ReturnType<typeof useMcpMutation<PriceAdjustInput, ActionResponse>>
  reorder: ReturnType<typeof useMcpMutation<ReorderInput, ActionResponse>>
  notifySales: ReturnType<typeof useMcpMutation<NotifySalesInput, ActionResponse>>
} {
  // Pricing: Staffelanpassung (oder Basispreis)
  const priceAdjust = useMcpMutation<PriceAdjustInput, ActionResponse>(
    "pricing",
    "adjust"
  )

  // Inventory: Reorder (Nachbestellung anstoßen)
  const reorder = useMcpMutation<ReorderInput, ActionResponse>(
    "inventory",
    "reorder"
  )

  // Sales: Vertrieb informieren
  const notifySales = useMcpMutation<NotifySalesInput, ActionResponse>(
    "sales",
    "notify"
  )

  return { priceAdjust, reorder, notifySales }
}
