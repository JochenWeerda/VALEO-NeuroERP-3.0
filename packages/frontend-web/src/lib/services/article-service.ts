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
  suchbegriff?: string
  hersteller?: string
  herkunftsland?: string
  naehrwertangaben?: string
  mhd_erforderlich: boolean
  lagerartikel: boolean
  mehrwertsteuer_prozent?: number
  warengruppe?: string
  gefahrgutklasse?: string
  lagerorte: string[]
  chargenpflicht: boolean
  qs_pruefung_erforderlich: boolean
  zolltarifnummer?: string
  bio_kennzeichnung: boolean
  gmp_plus_relevanz: boolean
  lieferantennummer?: string
  unit: string
  category: string
  subcategory?: string
  barcode?: string
  supplier_number?: string
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
  suchbegriff?: string
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
  purchase_price?: number
  sales_price: number
  currency?: string
  min_stock?: number
  max_stock?: number
  weight?: number
  dimensions?: string
}

export interface ArticleUpdate {
  article_number?: string
  name?: string
  description?: string
  suchbegriff?: string
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
  purchase_price?: number
  sales_price?: number
  currency?: string
  min_stock?: number
  max_stock?: number
  weight?: number
  dimensions?: string
  is_active?: boolean
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
  }
}
