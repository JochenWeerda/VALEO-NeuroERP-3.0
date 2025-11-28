/**
 * Kundenportal API Service
 * 
 * Verbindet das Frontend mit dem Portal-Backend für:
 * - Produkte mit Kontrakt/Vorkauf-Informationen
 * - Bestellungen
 * - Kontrakte & Vorkäufe
 */

import { apiClient } from '../api-client'

// ============================================
// Typen (entsprechen Backend-Schemas)
// ============================================

export type ContractStatus = 'NONE' | 'ACTIVE' | 'LOW' | 'EXHAUSTED'
export type OrderStatus = 'DRAFT' | 'SUBMITTED' | 'CONFIRMED' | 'IN_PROGRESS' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED'
export type PriceSource = 'LIST' | 'CONTRACT' | 'PRE_PURCHASE' | 'PROMO'

export interface LastOrderInfo {
  datum: string
  menge: number
  unit: string
}

export interface PortalProduct {
  id: string
  artikelnummer: string
  name: string
  kategorie: string
  beschreibung?: string
  einheit: string
  
  // Preise
  preis: number // Listenpreis
  rabattPreis?: number // Aktionspreis
  
  // Verfügbarkeit
  verfuegbar: boolean
  bestand: number
  
  // Zertifikate
  zertifikate: string[]
  
  // Letzte Bestellung
  letzteBestellung?: LastOrderInfo
  
  // Kontrakt-Informationen
  contractStatus: ContractStatus
  contractPrice?: number
  contractTotalQty?: number
  contractRemainingQty?: number
  
  // Vorkauf-Informationen
  isPrePurchase: boolean
  prePurchasePrice?: number
  prePurchaseTotalQty?: number
  prePurchaseRemainingQty?: number
}

export interface PortalProductList {
  items: PortalProduct[]
  total: number
  page: number
  size: number
  has_contracts: number
  has_pre_purchases: number
}

export interface OrderItem {
  article_id: string
  quantity: number
}

export interface OrderCreate {
  items: OrderItem[]
  delivery_address?: string
  delivery_date_requested?: string
  customer_notes?: string
}

export interface OrderItemResponse {
  id: string
  article_id: string
  artikel_nummer: string
  name: string
  quantity: number
  einheit: string
  unit_price: number
  total_price: number
  price_source: PriceSource
  quantity_from_credit: number
  quantity_at_list_price: number
}

export interface OrderResponse {
  id: string
  order_number: string
  order_date: string
  status: OrderStatus
  customer_id: string
  customer_name: string
  items: OrderItemResponse[]
  total_net: number
  total_gross: number
  delivery_address?: string
  delivery_date_requested?: string
  customer_notes?: string
  created_at: string
}

export interface OrderListItem {
  id: string
  order_number: string
  order_date: string
  status: OrderStatus
  item_count: number
  total_net: number
  main_article: string
}

export interface Contract {
  id: string
  contract_number: string
  article_name: string
  article_number: string
  contract_price: number
  list_price: number
  unit: string
  total_quantity: number
  remaining_quantity: number
  status: ContractStatus
  valid_until: string
}

export interface PrePurchase {
  id: string
  pre_purchase_number: string
  article_name: string
  article_number: string
  pre_purchase_price: number
  current_list_price: number
  unit: string
  total_quantity: number
  remaining_quantity: number
  payment_date: string
  valid_until?: string
}

// ============================================
// API Funktionen
// ============================================

const TENANT_ID = import.meta.env.VITE_TENANT_ID || 'system'

/**
 * Transformiert snake_case zu camelCase für Frontend-Kompatibilität
 */
function transformProduct(item: Record<string, unknown>): PortalProduct {
  return {
    id: item.id as string,
    artikelnummer: (item.artikel_nummer || item.artikelnummer) as string,
    name: item.name as string,
    kategorie: item.kategorie as string,
    beschreibung: item.beschreibung as string | undefined,
    einheit: item.einheit as string,
    preis: Number(item.listenpreis || item.preis),
    rabattPreis: item.aktionspreis ? Number(item.aktionspreis) : (item.rabattPreis ? Number(item.rabattPreis) : undefined),
    verfuegbar: Boolean(item.verfuegbar),
    bestand: Number(item.bestand || 0),
    zertifikate: (item.zertifikate || []) as string[],
    letzteBestellung: item.letzte_bestellung || item.letzteBestellung
      ? {
          datum: (item.letzte_bestellung as Record<string, unknown>)?.datum as string || 
                 (item.letzteBestellung as Record<string, unknown>)?.datum as string,
          menge: Number((item.letzte_bestellung as Record<string, unknown>)?.menge || 
                        (item.letzteBestellung as Record<string, unknown>)?.menge),
          unit: (item.letzte_bestellung as Record<string, unknown>)?.unit as string ||
                (item.letzteBestellung as Record<string, unknown>)?.unit as string ||
                item.einheit as string
        }
      : undefined,
    contractStatus: (item.contract_status || item.contractStatus || 'NONE') as ContractStatus,
    contractPrice: item.contract_price !== undefined ? Number(item.contract_price) : 
                   item.contractPrice !== undefined ? Number(item.contractPrice) : undefined,
    contractTotalQty: item.contract_total_qty !== undefined ? Number(item.contract_total_qty) :
                      item.contractTotalQty !== undefined ? Number(item.contractTotalQty) : undefined,
    contractRemainingQty: item.contract_remaining_qty !== undefined ? Number(item.contract_remaining_qty) :
                          item.contractRemainingQty !== undefined ? Number(item.contractRemainingQty) : undefined,
    isPrePurchase: Boolean(item.is_pre_purchase || item.isPrePurchase),
    prePurchasePrice: item.pre_purchase_price !== undefined ? Number(item.pre_purchase_price) :
                      item.prePurchasePrice !== undefined ? Number(item.prePurchasePrice) : undefined,
    prePurchaseTotalQty: item.pre_purchase_total_qty !== undefined ? Number(item.pre_purchase_total_qty) :
                         item.prePurchaseTotalQty !== undefined ? Number(item.prePurchaseTotalQty) : undefined,
    prePurchaseRemainingQty: item.pre_purchase_remaining_qty !== undefined ? Number(item.pre_purchase_remaining_qty) :
                             item.prePurchaseRemainingQty !== undefined ? Number(item.prePurchaseRemainingQty) : undefined,
  }
}

/**
 * Lädt Produkte für das Kundenportal
 */
export async function getPortalProducts(options?: {
  kategorie?: string
  search?: string
  skip?: number
  limit?: number
}): Promise<PortalProductList> {
  try {
    const params = new URLSearchParams({
      tenant_id: TENANT_ID,
      ...(options?.kategorie && options.kategorie !== 'alle' ? { kategorie: options.kategorie } : {}),
      ...(options?.search ? { search: options.search } : {}),
      ...(options?.skip ? { skip: String(options.skip) } : {}),
      ...(options?.limit ? { limit: String(options.limit) } : {}),
    })
    
    const response = await apiClient.get<PortalProductList>(`/api/v1/portal/products?${params}`)
    
    // Transformiere Produkte für Frontend
    return {
      ...response.data,
      items: response.data.items.map(item => transformProduct(item as unknown as Record<string, unknown>))
    }
  } catch (error) {
    // Fallback: Leere Liste bei API-Fehler (Mock-Daten werden im Frontend verwendet)
    return {
      items: [],
      total: 0,
      page: 1,
      size: 50,
      has_contracts: 0,
      has_pre_purchases: 0
    }
  }
}

/**
 * Erstellt eine neue Bestellung
 */
export async function createOrder(order: OrderCreate): Promise<OrderResponse> {
  const params = new URLSearchParams({ tenant_id: TENANT_ID })
  const response = await apiClient.post<OrderResponse>(`/api/v1/portal/orders?${params}`, order)
  return response.data
}

/**
 * Lädt Bestellungen des Kunden
 */
export async function getOrders(options?: {
  status?: OrderStatus
  skip?: number
  limit?: number
}): Promise<{ items: OrderListItem[]; total: number }> {
  try {
    const params = new URLSearchParams({
      tenant_id: TENANT_ID,
      ...(options?.status ? { status_filter: options.status } : {}),
      ...(options?.skip ? { skip: String(options.skip) } : {}),
      ...(options?.limit ? { limit: String(options.limit) } : {}),
    })
    
    const response = await apiClient.get<{ items: OrderListItem[]; total: number }>(`/api/v1/portal/orders?${params}`)
    return response.data
  } catch {
    return { items: [], total: 0 }
  }
}

/**
 * Lädt Details einer Bestellung
 */
export async function getOrder(orderId: string): Promise<OrderResponse | null> {
  try {
    const params = new URLSearchParams({ tenant_id: TENANT_ID })
    const response = await apiClient.get<OrderResponse>(`/api/v1/portal/orders/${orderId}?${params}`)
    return response.data
  } catch {
    return null
  }
}

/**
 * Lädt aktive Kontrakte des Kunden
 */
export async function getContracts(): Promise<Contract[]> {
  try {
    const params = new URLSearchParams({ tenant_id: TENANT_ID })
    const response = await apiClient.get<Contract[]>(`/api/v1/portal/contracts?${params}`)
    return response.data
  } catch {
    return []
  }
}

/**
 * Lädt Vorkauf-Guthaben des Kunden
 */
export async function getPrePurchases(): Promise<PrePurchase[]> {
  try {
    const params = new URLSearchParams({ tenant_id: TENANT_ID })
    const response = await apiClient.get<PrePurchase[]>(`/api/v1/portal/pre-purchases?${params}`)
    return response.data
  } catch {
    return []
  }
}

// Export als Objekt für einfachen Import
export const portalService = {
  getProducts: getPortalProducts,
  createOrder,
  getOrders,
  getOrder,
  getContracts,
  getPrePurchases,
}

export default portalService

