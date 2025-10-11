export type ProductStatus = 'active' | 'draft' | 'archived'

export interface PricingTier {
  minQuantityKg: number
  maxQuantityKg?: number
  pricePerKg: number
  validUntil: string
}

export interface SeedQualityMetrics {
  purityPercent: number
  germinationPercent: number
  moisturePercent: number
}

export interface SeedLicense {
  id: string
  name: string
  validUntil: string
  status: ProductStatus
}

export interface SeedProduct {
  id: string
  name: string
  variety: string
  category: string
  season: string
  supplier: string
  status: ProductStatus
  licenseCount: number
  forecastTons: number
  quality: SeedQualityMetrics
  pricing: PricingTier[]
  licenses: SeedLicense[]
  createdAt: string
  updatedAt: string
  notes?: string
}

export interface FertilizerNutrient {
  label: string
  percentage: number
}

export interface FertilizerProduct {
  id: string
  name: string
  productGroup: string
  composition: FertilizerNutrient[]
  supplier: string
  status: ProductStatus
  stockTons: number
  pricing: PricingTier[]
  createdAt: string
  updatedAt: string
}

export interface SeedOrderItem {
  productId: string
  productName: string
  quantityKg: number
  pricePerKg: number
}

export interface SeedOrderPayload {
  customer: string
  season: string
  deliveryDate: string
  paymentTerms: string
  notes?: string
  items: SeedOrderItem[]
}
