/**
 * Sales Service
 * API service for Sales operations (Offers, Orders, Invoices, Deliveries)
 */

import { apiClient } from '../api-client'

// Types
export interface Offer {
  id: string
  offerNumber: string
  customerId: string
  customerName: string
  items: Array<{
    articleId: string
    articleName: string
    quantity: number
    unitPrice: number
    totalPrice: number
  }>
  totalAmount: number
  validUntil: string
  status: 'draft' | 'sent' | 'accepted' | 'rejected' | 'expired'
  createdAt: string
  updatedAt: string
}

export interface Order {
  id: string
  orderNumber: string
  customerId: string
  customerName: string
  items: Array<{
    articleId: string
    articleName: string
    quantity: number
    unitPrice: number
    totalPrice: number
  }>
  totalAmount: number
  orderDate: string
  deliveryDate?: string
  status: 'draft' | 'confirmed' | 'in_production' | 'ready' | 'delivered' | 'cancelled'
  createdAt: string
  updatedAt: string
}

export interface Invoice {
  id: string
  invoiceNumber: string
  customerId: string
  customerName: string
  orderId?: string
  items: Array<{
    articleId: string
    articleName: string
    quantity: number
    unitPrice: number
    totalPrice: number
  }>
  totalAmount: number
  invoiceDate: string
  dueDate: string
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled'
  createdAt: string
  updatedAt: string
}

export interface Delivery {
  id: string
  deliveryNumber: string
  customerId: string
  customerName: string
  orderId?: string
  items: Array<{
    articleId: string
    articleName: string
    quantity: number
    deliveredQuantity: number
  }>
  deliveryDate: string
  deliveryNote?: string
  status: 'planned' | 'loading' | 'in_transit' | 'delivered' | 'cancelled'
  createdAt: string
  updatedAt: string
}

// API Functions
export const salesService = {
  // Offers
  async getOffers(params?: { search?: string; status?: string; limit?: number; offset?: number }) {
    const response = await apiClient.get<{ data: Offer[]; total: number }>('/api/v1/sales/offers', { params })
    return response.data
  },

  async getOffer(id: string) {
    const response = await apiClient.get<{ data: Offer }>(`/api/v1/sales/offers/${id}`)
    return response.data.data
  },

  async createOffer(data: Omit<Offer, 'id' | 'createdAt' | 'updatedAt'>) {
    const response = await apiClient.post<{ data: Offer }>('/api/v1/sales/offers', data)
    return response.data.data
  },

  async updateOffer(id: string, data: Partial<Omit<Offer, 'id' | 'createdAt' | 'updatedAt'>>) {
    const response = await apiClient.put<{ data: Offer }>(`/api/v1/sales/offers/${id}`, data)
    return response.data.data
  },

  async deleteOffer(id: string) {
    await apiClient.delete(`/api/v1/sales/offers/${id}`)
  },

  // Orders
  async getOrders(params?: { search?: string; status?: string; limit?: number; offset?: number }) {
    const response = await apiClient.get<{ data: Order[]; total: number }>('/api/v1/sales/orders', { params })
    return response.data
  },

  async getOrder(id: string) {
    const response = await apiClient.get<{ data: Order }>(`/api/v1/sales/orders/${id}`)
    return response.data.data
  },

  async createOrder(data: Omit<Order, 'id' | 'createdAt' | 'updatedAt'>) {
    const response = await apiClient.post<{ data: Order }>('/api/v1/sales/orders', data)
    return response.data.data
  },

  async updateOrder(id: string, data: Partial<Omit<Order, 'id' | 'createdAt' | 'updatedAt'>>) {
    const response = await apiClient.put<{ data: Order }>(`/api/v1/sales/orders/${id}`, data)
    return response.data.data
  },

  async deleteOrder(id: string) {
    await apiClient.delete(`/api/v1/sales/orders/${id}`)
  },

  // Invoices
  async getInvoices(params?: { search?: string; status?: string; limit?: number; offset?: number }) {
    const response = await apiClient.get<{ data: Invoice[]; total: number }>('/api/v1/sales/invoices', { params })
    return response.data
  },

  async getInvoice(id: string) {
    const response = await apiClient.get<{ data: Invoice }>(`/api/v1/sales/invoices/${id}`)
    return response.data.data
  },

  async createInvoice(data: Omit<Invoice, 'id' | 'createdAt' | 'updatedAt'>) {
    const response = await apiClient.post<{ data: Invoice }>('/api/v1/sales/invoices', data)
    return response.data.data
  },

  async updateInvoice(id: string, data: Partial<Omit<Invoice, 'id' | 'createdAt' | 'updatedAt'>>) {
    const response = await apiClient.put<{ data: Invoice }>(`/api/v1/sales/invoices/${id}`, data)
    return response.data.data
  },

  async deleteInvoice(id: string) {
    await apiClient.delete(`/api/v1/sales/invoices/${id}`)
  },

  // Deliveries
  async getDeliveries(params?: { search?: string; status?: string; limit?: number; offset?: number }) {
    const response = await apiClient.get<{ data: Delivery[]; total: number }>('/api/v1/sales/deliveries', { params })
    return response.data
  },

  async getDelivery(id: string) {
    const response = await apiClient.get<{ data: Delivery }>(`/api/v1/sales/deliveries/${id}`)
    return response.data.data
  },

  async createDelivery(data: Omit<Delivery, 'id' | 'createdAt' | 'updatedAt'>) {
    const response = await apiClient.post<{ data: Delivery }>('/api/v1/sales/deliveries', data)
    return response.data.data
  },

  async updateDelivery(id: string, data: Partial<Omit<Delivery, 'id' | 'createdAt' | 'updatedAt'>>) {
    const response = await apiClient.put<{ data: Delivery }>(`/api/v1/sales/deliveries/${id}`, data)
    return response.data.data
  },

  async deleteDelivery(id: string) {
    await apiClient.delete(`/api/v1/sales/deliveries/${id}`)
  },
}