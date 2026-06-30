export interface ProductRankItem {
  article?: string
  revenue?: number
  quantity?: number
}

export interface CustomerRankItem {
  customerId?: string
  totalRevenue?: number
}

export interface ReportDashboardData {
  totalRevenue?: number
  conversionRates?: { inquiryToOffer?: number; offerToOrder?: number; orderToInvoice?: number }
  topCustomers?: CustomerRankItem[]
  customerAcquisitionTrends?: Record<string, number>
  topProductsByRevenue?: ProductRankItem[]
  topProductsByQuantity?: ProductRankItem[]
  revenue?: { total?: number; paid?: number; outstanding?: number }
  outstandingPayments?: { current?: number; overdue30Days?: number; overdue60Days?: number; overdue90Days?: number }
  revenueTrends?: Record<string, number>
  orderVolumeTrends?: Record<string, number>
}
