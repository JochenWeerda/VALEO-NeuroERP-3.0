/**
 * Article Service
 * API service for Article/Product management
 */

import { apiClient } from '../api-client'

// Types
export interface Article {
  id: string
  tenant_id: string
  article_number: string
  name: string
  description?: string
  description2?: string
  short_description?: string
  suchbegriff?: string
  matchcode2?: string
  hersteller?: string
  herkunftsland?: string
  naehrwertangaben?: string
  mhd_erforderlich: boolean
  lagerartikel: boolean
  mehrwertsteuer_prozent?: number
  warengruppe?: string
  gefahrgutklasse?: string
  gefahrgut_un_nummer?: string
  gefahrgut_verpackungsgruppe?: string
  gefahrgut_anhaenge?: string
  lagerorte: string[]
  chargenpflicht: boolean
  qs_pruefung_erforderlich: boolean
  zolltarifnummer?: string
  bio_kennzeichnung: boolean
  gmp_plus_relevanz: boolean
  lieferantennummer?: string
  // Extended labeling fields
  kennzeichnung_bio?: string
  kennzeichnung_vegan?: string
  kennzeichnung_vegetarisch?: string
  kennzeichnung_allergene?: string
  kennzeichnung_herkunft?: string
  // Storage fields
  lager_min_temperatur?: number
  lager_max_temperatur?: number
  lager_lagerdauer_tage?: number
  lager_zentral?: boolean
  lager_silo?: boolean
  // Analysis fields
  analyse_protein?: number
  analyse_feuchtigkeit?: number
  analyse_schadex?: number
  analyse_fremdstoffe?: number
  analyse_sonstiges?: string
  // Search filter fields
  ean_code?: string
  alt_ean_code?: string
  lieferanten_artikelnummer?: string
  kunden_artikelnummer?: string
  verwendungszweck?: string
  nachhaltige_biomasse?: boolean
  pool_artikel?: boolean
  // Discount/Surcharge fields
  rabatt_auftrag_rechnung?: number
  rabatt_lose?: number
  rabatt_selbstabholer?: number
  zu_abschlag_1_code?: string
  zu_abschlag_1_prozent?: number
  zu_abschlag_2_code?: string
  zu_abschlag_2_prozent?: number
  berechne_zu_abschlag_auf_netto?: boolean
  einfuegen_summe_nach_zu_abschlag?: boolean
  // Discount flags
  skontofaehig?: boolean
  warenrueckverguetung?: boolean
  bonus_faehig?: boolean
  rabattfaehig?: boolean
  // Basic fields
  unit: string
  category: string
  subcategory?: string
  barcode?: string
  supplier_number?: string
  customer_article_number?: string
  purchase_price?: number
  sales_price: number
  currency: string
  min_stock?: number
  max_stock?: number
  weight?: number
  dimensions?: string
  current_stock: number
  reserved_stock: number
  available_stock: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ArticleCreate {
  tenant_id: string
  article_number: string
  name: string
  description?: string
  description2?: string
  short_description?: string
  suchbegriff?: string
  matchcode2?: string
  hersteller?: string
  herkunftsland?: string
  naehrwertangaben?: string
  mhd_erforderlich?: boolean
  lagerartikel?: boolean
  mehrwertsteuer_prozent?: number
  warengruppe?: string
  gefahrgutklasse?: string
  lagerorte?: string[]
  chargenpflicht?: boolean
  qs_pruefung_erforderlich?: boolean
  zolltarifnummer?: string
  bio_kennzeichnung?: boolean
  gmp_plus_relevanz?: boolean
  lieferantennummer?: string
  unit: string
  category: string
  subcategory?: string
  barcode?: string
  supplier_number?: string
  customer_article_number?: string
  purchase_price?: number
  sales_price: number
  currency?: string
  min_stock?: number
  max_stock?: number
  weight?: number
  dimensions?: string
  // Additional fields for extended article data
  gefahrgut_un_nummer?: string
  gefahrgut_verpackungsgruppe?: string
  gefahrgut_anhaenge?: string
  kennzeichnung_bio?: string
  kennzeichnung_vegan?: string
  kennzeichnung_vegetarisch?: string
  kennzeichnung_allergene?: string
  kennzeichnung_herkunft?: string
  lager_min_temperatur?: number
  lager_max_temperatur?: number
  lager_lagerdauer_tage?: number
  lager_zentral?: boolean
  lager_silo?: boolean
  analyse_protein?: number
  analyse_feuchtigkeit?: number
  analyse_schadex?: number
  analyse_fremdstoffe?: number
  analyse_sonstiges?: string
  // Search filter fields
  ean_code?: string
  alt_ean_code?: string
  lieferanten_artikelnummer?: string
  kunden_artikelnummer?: string
  verwendungszweck?: string
  nachhaltige_biomasse?: boolean
  pool_artikel?: boolean
  // Discount/Surcharge fields
  rabatt_auftrag_rechnung?: number
  rabatt_lose?: number
  rabatt_selbstabholer?: number
  zu_abschlag_1_code?: string
  zu_abschlag_1_prozent?: number
  zu_abschlag_2_code?: string
  zu_abschlag_2_prozent?: number
  berechne_zu_abschlag_auf_netto?: boolean
  einfuegen_summe_nach_zu_abschlag?: boolean
  // Discount flags
  skontofaehig?: boolean
  warenrueckverguetung?: boolean
  bonus_faehig?: boolean
  rabattfaehig?: boolean
}

export interface ArticleUpdate {
  article_number?: string
  name?: string
  description?: string
  description2?: string
  short_description?: string
  suchbegriff?: string
  matchcode2?: string
  hersteller?: string
  herkunftsland?: string
  naehrwertangaben?: string
  mhd_erforderlich?: boolean
  lagerartikel?: boolean
  mehrwertsteuer_prozent?: number
  warengruppe?: string
  gefahrgutklasse?: string
  lagerorte?: string[]
  chargenpflicht?: boolean
  qs_pruefung_erforderlich?: boolean
  zolltarifnummer?: string
  bio_kennzeichnung?: boolean
  gmp_plus_relevanz?: boolean
  lieferantennummer?: string
  unit?: string
  category?: string
  subcategory?: string
  barcode?: string
  supplier_number?: string
  customer_article_number?: string
  purchase_price?: number
  sales_price?: number
  currency?: string
  min_stock?: number
  max_stock?: number
  weight?: number
  dimensions?: string
  is_active?: boolean
  // Additional fields for extended article data
  gefahrgut_un_nummer?: string
  gefahrgut_verpackungsgruppe?: string
  gefahrgut_anhaenge?: string
  kennzeichnung_bio?: string
  kennzeichnung_vegan?: string
  kennzeichnung_vegetarisch?: string
  kennzeichnung_allergene?: string
  kennzeichnung_herkunft?: string
  lager_min_temperatur?: number
  lager_max_temperatur?: number
  lager_lagerdauer_tage?: number
  lager_zentral?: boolean
  lager_silo?: boolean
 Analyse_protein?: number
  analyse_feuchtigkeit?: number
  analyse_schadex?: number
  analyse_fremdstoffe?: number
  analyse_sonstiges?: string
}

export interface ArticlesResponse {
  items: Article[]
  total: number
  page: number
  size: number
  pages: number
  has_next: boolean
  has_prev: boolean
}

// API Functions
export const articleService = {
  async getArticles(params?: {
    search?: string
    limit?: number
    offset?: number
    tenant_id?: string
  }) {
    const queryParams = {
      search: params?.search,
      limit: params?.limit,
      skip: params?.offset,
      tenant_id: params?.tenant_id,
    }
    const response = await apiClient.get<ArticlesResponse>('/api/v1/articles', { params: queryParams })
    return response.data
  },

  async getArticle(id: string) {
    const response = await apiClient.get<Article>(`/api/v1/articles/${id}`)
    return response.data
  },

  async createArticle(data: ArticleCreate) {
    const response = await apiClient.post<Article>('/api/v1/articles', data)
    return response.data
  },

  async updateArticle(id: string, data: ArticleUpdate) {
    const response = await apiClient.put<Article>(`/api/v1/articles/${id}`, data)
    return response.data
  },

  async deleteArticle(id: string) {
    await apiClient.delete(`/api/v1/articles/${id}`)
  },

  async searchArticles(q: string, limit?: number, tenant_id?: string) {
    const params = { q, limit, tenant_id }
    const response = await apiClient.get<Article[]>('/api/v1/articles/search', { params })
    return response.data
  },

  async getArticleSuppliers(articleId: string, tenant_id?: string) {
    const params = { tenant_id }
    const response = await apiClient.get<{ items: ArticleSupplier[] }>(`/api/v1/articles/${articleId}/suppliers`, { params })
    return response.data.items
  },

  async getArticleDiscounts(articleId: string, tenant_id?: string) {
    const params = { tenant_id }
    const response = await apiClient.get<{ items: ArticleDiscount[] }>(`/api/v1/articles/${articleId}/discounts`, { params })
    return response.data.items
  },

  async getArticlePrices(articleId: string, tenant_id?: string) {
    const params = { tenant_id }
    const response = await apiClient.get<{ items: ArticlePrice[] }>(`/api/v1/articles/${articleId}/prices`, { params })
    return response.data.items
  },

  async getArticleDocuments(articleId: string, tenant_id?: string) {
    const params = { tenant_id }
    const response = await apiClient.get<{ items: ArticleDocument[] }>(`/api/v1/articles/${articleId}/documents`, { params })
    return response.data.items
  },

  async getArticleStock(articleId: string, branch_id?: string, tenant_id?: string) {
    const params = { branch_id, tenant_id }
    const response = await apiClient.get<Record<string, unknown>>(`/api/v1/articles/${articleId}/stock`, { params })
    return response.data
  },

  async getArticleStockMovements(articleId: string, params?: {
    from_date?: string
    to_date?: string
    warehouse_id?: string
    skip?: number
    limit?: number
    tenant_id?: string
  }) {
    const response = await apiClient.get<Record<string, unknown>>(`/api/v1/articles/${articleId}/stock-movements`, { params })
    return response.data
  },

  // Nutrient Compositions (Düngemittel-Zusammensetzung)
  async getNutrientCompositions(params?: {
    search?: string
    limit?: number
    offset?: number
    tenant_id?: string
  }) {
    const queryParams = {
      search: params?.search,
      limit: params?.limit,
      skip: params?.offset,
      tenant_id: params?.tenant_id,
    }
    const response = await apiClient.get<Record<string, unknown>>('/api/v1/nutrient-compositions', { params: queryParams })
    return response.data
  },

  async getNutrientComposition(id: string) {
    const response = await apiClient.get<Record<string, unknown>>(`/api/v1/nutrient-compositions/${id}`)
    return response.data
  },

  async createNutrientComposition(data: Record<string, unknown>) {
    const response = await apiClient.post<Record<string, unknown>>('/api/v1/nutrient-compositions', data)
    return response.data
  },

  async updateNutrientComposition(id: string, data: Record<string, unknown>) {
    const response = await apiClient.put<Record<string, unknown>>(`/api/v1/nutrient-compositions/${id}`, data)
    return response.data
  },

  async deleteNutrientComposition(id: string) {
    await apiClient.delete(`/api/v1/nutrient-compositions/${id}`)
  },

  async searchNutrientCompositions(q: string, limit?: number, tenant_id?: string) {
    const params = { q, limit, tenant_id }
    const response = await apiClient.get<Record<string, unknown>>('/api/v1/nutrient-compositions/search', { params })
    return response.data
  }
}

// ============================================================================
// Additional Types for Extended Article Features
// ============================================================================

export interface ArticleSupplier {
  id: string
  article_id: string
  partner_id: string
  supplier_number: string
  supplier_name: string
  supplier_article_number?: string
  purchase_price?: number
  price_valid_from?: string
  price_valid_to?: string
  lead_time_days?: number
  min_order_quantity?: number
  is_preferred: boolean
  created_at: string
  updated_at: string
}

export interface ArticleDiscount {
  id: string
  article_id: string
  partner_id?: string
  discount_percent: number
  valid_from?: string
  valid_to?: string
  discount_list_number?: string
  customer_name?: string
  created_at: string
  updated_at: string
}

export interface ArticlePrice {
  id: string
  article_id: string
  price_net: number
  price_incl_freight?: number
  price_unit?: string
  valid_from?: string
  valid_to?: string
  customer_name?: string
  partner_id?: string
  created_at: string
  updated_at: string
}

export interface ArticleDocument {
  id: string
  article_id: string
  document_id: string
  document_name: string
  document_type: string
  file_path?: string
  created_at: string
}

export interface ArticleSearchResult {
  id: string
  article_number: string
  name: string
  category?: string
  warengruppe?: string
  unit?: string
  sales_price?: number
  current_stock?: number
}
