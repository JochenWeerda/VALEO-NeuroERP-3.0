import { SalesOfferEntity, CreateSalesOfferInput, UpdateSalesOfferInput, SalesOfferStatusType } from '../entities';
import { SalesOfferRepository } from '../../infra/repo';

export interface SalesOfferServiceDependencies {
  salesOfferRepo: SalesOfferRepository;
}

export interface CreateSalesOfferData extends CreateSalesOfferInput {
  tenantId: string;
  offerNumber: string;
}

export interface UpdateSalesOfferData extends UpdateSalesOfferInput {
  tenantId: string;
}

export class SalesOfferService {
  constructor(private deps: SalesOfferServiceDependencies) {}

  async createSalesOffer(data: CreateSalesOfferData): Promise<SalesOfferEntity> {
    // Business validation
    if (data.totalAmount <= 0) {
      throw new Error('Gesamtbetrag muss größer 0 sein');
    }

    if (data.validUntil <= new Date()) {
      throw new Error('Gültigkeitsdatum muss in der Zukunft liegen');
    }

    if (!data.subject.trim()) {
      throw new Error('Betreff ist erforderlich');
    }

    if (!data.description.trim()) {
      throw new Error('Beschreibung ist erforderlich');
    }

    // Check if offer number already exists
    const existingOffer = await this.deps.salesOfferRepo.findByNumber(data.offerNumber, data.tenantId);
    if (existingOffer) {
      throw new Error(`SalesOffer number ${data.offerNumber} already exists`);
    }

    const salesOffer = await this.deps.salesOfferRepo.create(data);
    return salesOffer;
  }

  async getSalesOffer(id: string, tenantId: string): Promise<SalesOfferEntity | null> {
    return this.deps.salesOfferRepo.findById(id, tenantId);
  }

  async getSalesOfferByNumber(offerNumber: string, tenantId: string): Promise<SalesOfferEntity | null> {
    return this.deps.salesOfferRepo.findByNumber(offerNumber, tenantId);
  }

  async updateSalesOffer(id: string, data: UpdateSalesOfferData): Promise<SalesOfferEntity> {
    const existingOffer = await this.deps.salesOfferRepo.findById(id, data.tenantId);
    if (existingOffer === undefined || existingOffer === null) {
      throw new Error(`SalesOffer ${id} not found`);
    }

    // Business validation
    if (data.totalAmount !== undefined && data.totalAmount <= 0) {
      throw new Error('Gesamtbetrag muss größer 0 sein');
    }

    if (data.validUntil !== undefined && data.validUntil <= new Date()) {
      throw new Error('Gültigkeitsdatum muss in der Zukunft liegen');
    }

    if (data.subject !== undefined && !data.subject.trim()) {
      throw new Error('Betreff ist erforderlich');
    }

    if (data.description !== undefined && !data.description.trim()) {
      throw new Error('Beschreibung ist erforderlich');
    }

    const updatedOffer = await this.deps.salesOfferRepo.update(id, data.tenantId, data);

    if (updatedOffer === undefined || updatedOffer === null) {
      throw new Error(`Failed to update sales offer ${id}`);
    }

    return updatedOffer;
  }

  async deleteSalesOffer(id: string, tenantId: string): Promise<boolean> {
    const offer = await this.deps.salesOfferRepo.findById(id, tenantId);
    if (offer === undefined || offer === null) {
      throw new Error(`SalesOffer ${id} not found`);
    }

    // Business rule: only draft offers can be deleted
    if (offer.status !== 'ENTWURF') {
      throw new Error('Only draft offers can be deleted');
    }

    return this.deps.salesOfferRepo.delete(id, tenantId);
  }

  async sendSalesOffer(id: string, tenantId: string): Promise<SalesOfferEntity> {
    const offer = await this.deps.salesOfferRepo.findById(id, tenantId);
    if (offer === undefined || offer === null) {
      throw new Error(`SalesOffer ${id} not found`);
    }

    if (!offer.canBeSent()) {
      throw new Error('SalesOffer cannot be sent in its current state');
    }

    const updatedOffer = await this.deps.salesOfferRepo.updateStatus(id, tenantId, 'VERSENDET');

    if (updatedOffer === undefined || updatedOffer === null) {
      throw new Error(`Failed to send sales offer`);
    }

    return updatedOffer;
  }

  async acceptSalesOffer(id: string, tenantId: string): Promise<SalesOfferEntity> {
    const offer = await this.deps.salesOfferRepo.findById(id, tenantId);
    if (offer === undefined || offer === null) {
      throw new Error(`SalesOffer ${id} not found`);
    }

    if (!offer.kannAngenommenWerden()) {
      throw new Error('SalesOffer cannot be accepted in its current state');
    }

    const updatedOffer = await this.deps.salesOfferRepo.updateStatus(id, tenantId, 'ANGENOMMEN');

    if (updatedOffer === undefined || updatedOffer === null) {
      throw new Error(`Failed to accept sales offer`);
    }

    return updatedOffer;
  }

  async rejectSalesOffer(id: string, tenantId: string): Promise<SalesOfferEntity> {
    const offer = await this.deps.salesOfferRepo.findById(id, tenantId);
    if (offer === undefined || offer === null) {
      throw new Error(`SalesOffer ${id} not found`);
    }

    if (offer.status === 'ANGENOMMEN' || offer.status === 'ABGELAUFEN') {
      throw new Error('SalesOffer kann nicht mehr abgelehnt werden');
    }

    const updatedOffer = await this.deps.salesOfferRepo.updateStatus(id, tenantId, 'ABGELEHNT');

    if (updatedOffer === undefined || updatedOffer === null) {
      throw new Error(`Failed to reject sales offer`);
    }

    return updatedOffer;
  }

  async expireSalesOffer(id: string, tenantId: string): Promise<SalesOfferEntity> {
    const offer = await this.deps.salesOfferRepo.findById(id, tenantId);
    if (offer === undefined || offer === null) {
      throw new Error(`SalesOffer ${id} not found`);
    }

    if (offer.status === 'ABGELAUFEN' || offer.status === 'ABGELEHNT' || offer.status === 'ANGENOMMEN') {
      return offer; // Already in terminal state
    }

    const updatedOffer = await this.deps.salesOfferRepo.updateStatus(id, tenantId, 'ABGELAUFEN');

    if (updatedOffer === undefined || updatedOffer === null) {
      throw new Error(`Failed to expire sales offer`);
    }

    return updatedOffer;
  }

  async searchSalesOffers(
    tenantId: string,
    filters: {
      customerId?: string;
      status?: SalesOfferStatusType;
      search?: string;
      validUntilFrom?: Date;
      validUntilTo?: Date;
    } = {},
    pagination: { page: number; pageSize: number } = { page: 1, pageSize: 20 }
  ) {
    return this.deps.salesOfferRepo.findAll(tenantId, filters, pagination);
  }

  async getSalesOffersByCustomer(
    customerId: string,
    tenantId: string,
    filters: {
      status?: SalesOfferStatusType;
      search?: string;
      validUntilFrom?: Date;
      validUntilTo?: Date;
    } = {},
    pagination: { page: number; pageSize: number } = { page: 1, pageSize: 20 }
  ) {
    return this.deps.salesOfferRepo.findByCustomerId(customerId, tenantId, filters, pagination);
  }

  async getSalesOffersByCustomerInquiry(
    customerInquiryId: string,
    tenantId: string
  ): Promise<SalesOfferEntity[]> {
    return this.deps.salesOfferRepo.findByCustomerInquiryId(customerInquiryId, tenantId);
  }

  async getExpiringSoon(tenantId: string, daysAhead: number = 7): Promise<SalesOfferEntity[]> {
    return this.deps.salesOfferRepo.getExpiringSoon(tenantId, daysAhead);
  }

  async getExpiredOffers(tenantId: string): Promise<SalesOfferEntity[]> {
    return this.deps.salesOfferRepo.getExpired(tenantId);
  }
}