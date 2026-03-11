export interface PriceTier {
  minQty: number
  net: number
}

export interface PriceItem {
  sku: string
  name: string
  currency: string
  unit: string
  baseNet: number
  tiers: PriceTier[]
}
