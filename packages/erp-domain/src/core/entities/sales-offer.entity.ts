import { CustomerInquiry } from './customer-inquiry.entity'

export enum SalesOfferStatus {
  ENTWURF = 'ENTWURF',
  VERSENDET = 'VERSENDET',
  ANGENOMMEN = 'ANGENOMMEN',
  ABGELEHNT = 'ABGELEHNT',
  ABGELAUFEN = 'ABGELAUFEN'
}

export class SalesOffer {
  constructor(
    public readonly id: string,
    public readonly offerNumber: string,
    public readonly customerInquiryId: string,
    public readonly customerId: string,
    public readonly subject: string,
    public readonly description: string,
    public readonly totalAmount: number,
    public readonly currency: string,
    public readonly validUntil: Date,
    public readonly status: SalesOfferStatus,
    public readonly tenantId: string,
    public readonly contactPerson?: string,
    public readonly deliveryDate?: Date,
    public readonly paymentTerms?: string,
    public readonly notes?: string,
    public readonly version: number = 0,
    public readonly createdAt: Date = new Date(),
    public readonly updatedAt: Date = new Date(),
    public readonly deletedAt?: Date
  ) {}

  static createFromCustomerInquiry(
    customerInquiry: CustomerInquiry,
    data: {
      offerNumber: string
      totalAmount: number
      validUntil: Date
      deliveryDate?: Date
      paymentTerms?: string
      notes?: string
    }
  ): SalesOffer {
    return new SalesOffer(
      '', // ID wird generiert
      data.offerNumber,
      customerInquiry.id,
      customerInquiry.customerId,
      customerInquiry.subject,
      customerInquiry.description,
      data.totalAmount,
      customerInquiry.currency,
      data.validUntil,
      SalesOfferStatus.ENTWURF,
      customerInquiry.tenantId,
      customerInquiry.contactPerson,
      data.deliveryDate,
      data.paymentTerms,
      data.notes
    )
  }

  static create(data: {
    offerNumber: string
    customerInquiryId: string
    customerId: string
    subject: string
    description: string
    totalAmount: number
    currency: string
    validUntil: Date
    tenantId: string
    contactPerson?: string
    deliveryDate?: Date
    paymentTerms?: string
    notes?: string
  }): SalesOffer {
    return new SalesOffer(
      '', // ID wird generiert
      data.offerNumber,
      data.customerInquiryId,
      data.customerId,
      data.subject,
      data.description,
      data.totalAmount,
      data.currency,
      data.validUntil,
      SalesOfferStatus.ENTWURF,
      data.tenantId,
      data.contactPerson,
      data.deliveryDate,
      data.paymentTerms,
      data.notes
    )
  }

  versenden(): SalesOffer {
    if (this.status !== SalesOfferStatus.ENTWURF) {
      throw new Error('Nur Entwürfe können versendet werden')
    }
    return new SalesOffer(
      this.id,
      this.offerNumber,
      this.customerInquiryId,
      this.customerId,
      this.subject,
      this.description,
      this.totalAmount,
      this.currency,
      this.validUntil,
      SalesOfferStatus.VERSENDET,
      this.tenantId,
      this.contactPerson,
      this.deliveryDate,
      this.paymentTerms,
      this.notes,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  annehmen(): SalesOffer {
    if (this.status !== SalesOfferStatus.VERSENDET) {
      throw new Error('Nur versendete Angebote können angenommen werden')
    }
    return new SalesOffer(
      this.id,
      this.offerNumber,
      this.customerInquiryId,
      this.customerId,
      this.subject,
      this.description,
      this.totalAmount,
      this.currency,
      this.validUntil,
      SalesOfferStatus.ANGENOMMEN,
      this.tenantId,
      this.contactPerson,
      this.deliveryDate,
      this.paymentTerms,
      this.notes,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  ablehnen(): SalesOffer {
    if (this.status === SalesOfferStatus.ABGELEHNT || this.status === SalesOfferStatus.ANGENOMMEN) {
      throw new Error('Angebot kann nicht mehr abgelehnt werden')
    }
    return new SalesOffer(
      this.id,
      this.offerNumber,
      this.customerInquiryId,
      this.customerId,
      this.subject,
      this.description,
      this.totalAmount,
      this.currency,
      this.validUntil,
      SalesOfferStatus.ABGELEHNT,
      this.tenantId,
      this.contactPerson,
      this.deliveryDate,
      this.paymentTerms,
      this.notes,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  ablaufen(): SalesOffer {
    if (this.status !== SalesOfferStatus.VERSENDET) {
      throw new Error('Nur versendete Angebote können ablaufen')
    }
    return new SalesOffer(
      this.id,
      this.offerNumber,
      this.customerInquiryId,
      this.customerId,
      this.subject,
      this.description,
      this.totalAmount,
      this.currency,
      this.validUntil,
      SalesOfferStatus.ABGELAUFEN,
      this.tenantId,
      this.contactPerson,
      this.deliveryDate,
      this.paymentTerms,
      this.notes,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  istAbgelaufen(): boolean {
    return new Date() > this.validUntil && this.status === SalesOfferStatus.VERSENDET
  }

  getTageBisAblauf(): number | null {
    if (this.status !== SalesOfferStatus.VERSENDET) return null
    const diffTime = this.validUntil.getTime() - new Date().getTime()
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  }

  kannAngenommenWerden(): boolean {
    return this.status === SalesOfferStatus.VERSENDET && !this.istAbgelaufen()
  }

  istGueltig(): boolean {
    return this.status === SalesOfferStatus.VERSENDET && !this.istAbgelaufen()
  }
}