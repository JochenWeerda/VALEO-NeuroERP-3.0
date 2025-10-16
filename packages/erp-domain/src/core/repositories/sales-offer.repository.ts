import { SalesOffer } from '../entities/sales-offer.entity'
import { SalesOfferStatus } from '../entities/sales-offer.entity'

export interface SalesOfferRepository {
  save(salesOffer: SalesOffer): Promise<SalesOffer>
  findById(id: string, tenantId: string): Promise<SalesOffer | null>
  findByNumber(number: string, tenantId: string): Promise<SalesOffer | null>
  findByTenant(tenantId: string, options?: {
    status?: SalesOfferStatus
    customerId?: string
    limit?: number
    offset?: number
  }): Promise<SalesOffer[]>
  findByCustomerInquiryId(customerInquiryId: string, tenantId: string): Promise<SalesOffer[]>
  findExpired(tenantId: string): Promise<SalesOffer[]>
  findValid(tenantId: string): Promise<SalesOffer[]>
  update(salesOffer: SalesOffer): Promise<SalesOffer>
  delete(id: string, tenantId: string): Promise<void>
  countByTenant(tenantId: string, status?: SalesOfferStatus): Promise<number>
}