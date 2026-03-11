export interface Stock {
  sku: string
  name: string
  qty: number
  uom: string
  location?: string
}

export type AdjustReason = "counting" | "damage" | "shrinkage" | "other"

export interface AdjustInput {
  sku: string
  delta: number
  reason: AdjustReason
}

export interface PutawayInput {
  sku: string
  qty: number
  fromLocation: string
  toLocation: string
}
