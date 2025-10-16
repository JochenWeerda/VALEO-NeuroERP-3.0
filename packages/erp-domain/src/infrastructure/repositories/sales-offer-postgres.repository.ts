import { injectable } from 'inversify'
import { PrismaClient } from '@prisma/client'
import { SalesOffer } from '../../core/entities/sales-offer.entity'
import { SalesOfferRepository } from '../../core/repositories/sales-offer.repository'
import { SalesOfferStatus } from '../../core/entities/sales-offer.entity'

@injectable()
export class SalesOfferPostgresRepository implements SalesOfferRepository {
  constructor(private prisma: PrismaClient) {}

  async save(salesOffer: SalesOffer): Promise<SalesOffer> {
    const data = {
      id: salesOffer.id,
      offerNumber: salesOffer.offerNumber,
      customerInquiryId: salesOffer.customerInquiryId,
      customerId: salesOffer.customerId,
      subject: salesOffer.subject,
      description: salesOffer.description,
      totalAmount: salesOffer.totalAmount,
      currency: salesOffer.currency,
      validUntil: salesOffer.validUntil,
      status: salesOffer.status,
      tenantId: salesOffer.tenantId,
      contactPerson: salesOffer.contactPerson,
      deliveryDate: salesOffer.deliveryDate,
      paymentTerms: salesOffer.paymentTerms,
      notes: salesOffer.notes,
      version: salesOffer.version,
      createdAt: salesOffer.createdAt,
      updatedAt: salesOffer.updatedAt,
      deletedAt: salesOffer.deletedAt
    }

    const saved = await (this.prisma as any).salesOffer.upsert({
      where: { id: salesOffer.id },
      update: data,
      create: data
    })

    return this.mapToEntity(saved)
  }

  async findById(id: string, tenantId: string): Promise<SalesOffer | null> {
    const result = await (this.prisma as any).salesOffer.findFirst({
      where: {
        id,
        tenantId,
        deletedAt: null
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByNumber(number: string, tenantId: string): Promise<SalesOffer | null> {
    const result = await (this.prisma as any).salesOffer.findFirst({
      where: {
        offerNumber: number,
        tenantId,
        deletedAt: null
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByTenant(tenantId: string, options?: {
    status?: SalesOfferStatus
    customerId?: string
    limit?: number
    offset?: number
  }): Promise<SalesOffer[]> {
    const where: any = {
      tenantId,
      deletedAt: null
    }

    if (options?.status) where.status = options.status
    if (options?.customerId) where.customerId = options.customerId

    const results = await (this.prisma as any).salesOffer.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: options?.limit || 50,
      skip: options?.offset || 0
    })

    return results.map(this.mapToEntity)
  }

  async findByCustomerInquiryId(customerInquiryId: string, tenantId: string): Promise<SalesOffer[]> {
    const results = await (this.prisma as any).salesOffer.findMany({
      where: {
        customerInquiryId,
        tenantId,
        deletedAt: null
      },
      orderBy: { createdAt: 'desc' }
    })

    return results.map(this.mapToEntity)
  }

  async findExpired(tenantId: string): Promise<SalesOffer[]> {
    const results = await (this.prisma as any).salesOffer.findMany({
      where: {
        tenantId,
        validUntil: { lt: new Date() },
        status: SalesOfferStatus.VERSENDET,
        deletedAt: null
      },
      orderBy: { validUntil: 'asc' }
    })

    return results.map(this.mapToEntity)
  }

  async findValid(tenantId: string): Promise<SalesOffer[]> {
    const results = await (this.prisma as any).salesOffer.findMany({
      where: {
        tenantId,
        validUntil: { gte: new Date() },
        status: SalesOfferStatus.VERSENDET,
        deletedAt: null
      },
      orderBy: { validUntil: 'asc' }
    })

    return results.map(this.mapToEntity)
  }

  async update(salesOffer: SalesOffer): Promise<SalesOffer> {
    const data = {
      offerNumber: salesOffer.offerNumber,
      customerInquiryId: salesOffer.customerInquiryId,
      customerId: salesOffer.customerId,
      subject: salesOffer.subject,
      description: salesOffer.description,
      totalAmount: salesOffer.totalAmount,
      currency: salesOffer.currency,
      validUntil: salesOffer.validUntil,
      status: salesOffer.status,
      contactPerson: salesOffer.contactPerson,
      deliveryDate: salesOffer.deliveryDate,
      paymentTerms: salesOffer.paymentTerms,
      notes: salesOffer.notes,
      version: salesOffer.version,
      updatedAt: salesOffer.updatedAt,
      deletedAt: salesOffer.deletedAt
    }

    const updated = await (this.prisma as any).salesOffer.update({
      where: { id: salesOffer.id },
      data
    })

    return this.mapToEntity(updated)
  }

  async delete(id: string, tenantId: string): Promise<void> {
    await (this.prisma as any).salesOffer.update({
      where: { id },
      data: { deletedAt: new Date() }
    })
  }

  async countByTenant(tenantId: string, status?: SalesOfferStatus): Promise<number> {
    const where: any = {
      tenantId,
      deletedAt: null
    }

    if (status) where.status = status

    return (this.prisma as any).salesOffer.count({ where })
  }

  private mapToEntity(data: any): SalesOffer {
    return new SalesOffer(
      data.id,
      data.offerNumber,
      data.customerInquiryId,
      data.customerId,
      data.subject,
      data.description,
      data.totalAmount,
      data.currency,
      data.validUntil,
      data.status,
      data.tenantId,
      data.contactPerson,
      data.deliveryDate,
      data.paymentTerms,
      data.notes,
      data.version,
      data.createdAt,
      data.updatedAt,
      data.deletedAt
    )
  }
}