/**
 * Sales Offer Repository
 * ISO 27001 Communications Security Compliant
 */

import { SalesOffer, SalesOfferItem, SalesOfferStatus } from '../../domain/entities/sales-offer';

export interface SalesOfferFilter {
  customerId?: string;
  status?: SalesOfferStatus;
  customerInquiryId?: string;
  validFrom?: Date;
  validTo?: Date;
  createdBy?: string;
  sentBy?: string;
  acceptedBy?: string;
  rejectedBy?: string;
}

export interface SalesOfferSort {
  field: 'createdAt' | 'updatedAt' | 'validUntil' | 'totalAmount' | 'offerNumber';
  direction: 'asc' | 'desc';
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export class SalesOfferRepository {
  private offers: Map<string, SalesOffer> = new Map();
  private items: Map<string, SalesOfferItem[]> = new Map();

  /**
   * Create a new sales offer
   */
  async create(offer: SalesOffer): Promise<SalesOffer> {
    // Validate offer data
    this.validateOffer(offer);

    // Store offer
    this.offers.set(offer.id, offer);

    // Store items
    this.items.set(offer.id, [...offer.items]);

    return offer;
  }

  /**
   * Update an existing sales offer
   */
  async update(id: string, offer: SalesOffer): Promise<SalesOffer> {
    if (!this.offers.has(id)) {
      throw new Error(`Sales offer with id ${id} not found`);
    }

    // Validate offer data
    this.validateOffer(offer);

    // Store updated offer
    this.offers.set(id, offer);

    // Store updated items
    this.items.set(id, [...offer.items]);

    return offer;
  }

  /**
   * Find sales offer by ID
   */
  async findById(id: string): Promise<SalesOffer | null> {
    return this.offers.get(id) || null;
  }

  /**
   * Find sales offer by offer number
   */
  async findByOfferNumber(offerNumber: string): Promise<SalesOffer | null> {
    for (const offer of this.offers.values()) {
      if (offer.offerNumber === offerNumber) {
        return offer;
      }
    }
    return null;
  }

  /**
   * Find sales offers by customer ID
   */
  async findByCustomerId(customerId: string): Promise<SalesOffer[]> {
    const result: SalesOffer[] = [];
    for (const offer of this.offers.values()) {
      if (offer.customerId === customerId) {
        result.push(offer);
      }
    }
    return result;
  }

  /**
   * Find sales offers by customer inquiry ID
   */
  async findByCustomerInquiryId(customerInquiryId: string): Promise<SalesOffer[]> {
    const result: SalesOffer[] = [];
    for (const offer of this.offers.values()) {
      if (offer.customerInquiryId === customerInquiryId) {
        result.push(offer);
      }
    }
    return result;
  }

  /**
   * Find all sales offers with filtering and pagination
   */
  async findAll(
    filter: SalesOfferFilter = {},
    sort: SalesOfferSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResult<SalesOffer>> {
    let offers = Array.from(this.offers.values());

    // Apply filters
    offers = this.applyFilters(offers, filter);

    // Apply sorting
    offers = this.applySorting(offers, sort);

    // Apply pagination
    const total = offers.length;
    const totalPages = Math.ceil(total / pageSize);
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const paginatedOffers = offers.slice(startIndex, endIndex);

    return {
      items: paginatedOffers,
      total,
      page,
      pageSize,
      totalPages,
      hasNext: page < totalPages,
      hasPrev: page > 1
    };
  }

  /**
   * Find expired sales offers
   */
  async findExpired(): Promise<SalesOffer[]> {
    const now = new Date();
    const result: SalesOffer[] = [];

    for (const offer of this.offers.values()) {
      if (offer.validUntil < now && offer.status === SalesOfferStatus.VERSENDET) {
        // Create expired version
        const expiredOffer = new SalesOffer(
          offer.customerId,
          offer.subject,
          offer.description,
          offer.validUntil,
          offer.items,
          offer.createdBy,
          {
            id: offer.id,
            offerNumber: offer.offerNumber,
            customerInquiryId: offer.customerInquiryId || undefined,
            contactPerson: offer.contactPerson || undefined,
            deliveryDate: offer.deliveryDate || undefined,
            paymentTerms: offer.paymentTerms || undefined,
            currency: offer.currency,
            taxRate: offer.taxRate,
            notes: offer.notes || undefined,
            status: SalesOfferStatus.ABGELAUFEN,
            version: offer.version,
            sentAt: offer.sentAt || undefined,
            sentBy: offer.sentBy || undefined,
            acceptedAt: offer.acceptedAt || undefined,
            acceptedBy: offer.acceptedBy || undefined,
            rejectedAt: offer.rejectedAt || undefined,
            rejectedBy: offer.rejectedBy || undefined,
            rejectionReason: offer.rejectionReason || undefined,
            createdAt: offer.createdAt,
            updatedAt: new Date()
          }
        );
        result.push(expiredOffer);
      }
    }

    return result;
  }

  /**
   * Find valid (active) sales offers
   */
  async findValid(): Promise<SalesOffer[]> {
    const now = new Date();
    const result: SalesOffer[] = [];

    for (const offer of this.offers.values()) {
      if (offer.validUntil >= now && offer.status === SalesOfferStatus.VERSENDET) {
        result.push(offer);
      }
    }

    return result;
  }

  /**
   * Delete sales offer by ID
   */
  async delete(id: string): Promise<boolean> {
    if (!this.offers.has(id)) {
      return false;
    }

    this.offers.delete(id);
    this.items.delete(id);
    return true;
  }

  /**
   * Get sales offer statistics
   */
  async getStatistics(): Promise<{
    total: number;
    byStatus: Record<SalesOfferStatus, number>;
    totalValue: number;
    averageValue: number;
    conversionRate: number;
  }> {
    const offers = Array.from(this.offers.values());
    const byStatus: Record<SalesOfferStatus, number> = {
      [SalesOfferStatus.ENTWURF]: 0,
      [SalesOfferStatus.VERSENDET]: 0,
      [SalesOfferStatus.ANGEnommen]: 0,
      [SalesOfferStatus.ABGELEHNT]: 0,
      [SalesOfferStatus.ABGELAUFEN]: 0
    };

    let totalValue = 0;
    let acceptedCount = 0;

    for (const offer of offers) {
      byStatus[offer.status]++;
      totalValue += offer.totalAmount;

      if (offer.status === SalesOfferStatus.ANGEnommen) {
        acceptedCount++;
      }
    }

    const conversionRate = offers.length > 0 ? (acceptedCount / offers.length) * 100 : 0;

    return {
      total: offers.length,
      byStatus,
      totalValue,
      averageValue: offers.length > 0 ? totalValue / offers.length : 0,
      conversionRate
    };
  }

  /**
   * Check if offer exists
   */
  async exists(id: string): Promise<boolean> {
    return this.offers.has(id);
  }

  /**
   * Get items for a specific offer
   */
  async getItems(offerId: string): Promise<SalesOfferItem[]> {
    return this.items.get(offerId) || [];
  }

  private validateOffer(offer: SalesOffer): void {
    if (!offer.customerId) {
      throw new Error('Customer ID is required');
    }

    if (!offer.subject || offer.subject.trim().length === 0) {
      throw new Error('Subject is required');
    }

    if (!offer.description || offer.description.trim().length === 0) {
      throw new Error('Description is required');
    }

    if (!offer.validUntil || offer.validUntil <= new Date()) {
      throw new Error('Valid until date must be in the future');
    }

    if (!offer.items || offer.items.length === 0) {
      throw new Error('At least one item is required');
    }

    if (!offer.createdBy) {
      throw new Error('Created by is required');
    }

    // Validate items
    for (const item of offer.items) {
      if (!item.description || item.description.trim().length === 0) {
        throw new Error('Item description is required');
      }

      if (item.quantity <= 0) {
        throw new Error('Item quantity must be positive');
      }

      if (item.unitPrice < 0) {
        throw new Error('Item unit price cannot be negative');
      }

      if (item.discountPercent < 0 || item.discountPercent > 100) {
        throw new Error('Item discount percent must be between 0 and 100');
      }
    }
  }

  private applyFilters(offers: SalesOffer[], filter: SalesOfferFilter): SalesOffer[] {
    return offers.filter(offer => {
      if (filter.customerId && offer.customerId !== filter.customerId) {
        return false;
      }

      if (filter.status && offer.status !== filter.status) {
        return false;
      }

      if (filter.customerInquiryId && offer.customerInquiryId !== filter.customerInquiryId) {
        return false;
      }

      if (filter.validFrom && offer.validUntil < filter.validFrom) {
        return false;
      }

      if (filter.validTo && offer.validUntil > filter.validTo) {
        return false;
      }

      if (filter.createdBy && offer.createdBy !== filter.createdBy) {
        return false;
      }

      if (filter.sentBy && offer.sentBy !== filter.sentBy) {
        return false;
      }

      if (filter.acceptedBy && offer.acceptedBy !== filter.acceptedBy) {
        return false;
      }

      if (filter.rejectedBy && offer.rejectedBy !== filter.rejectedBy) {
        return false;
      }

      return true;
    });
  }

  private applySorting(offers: SalesOffer[], sort: SalesOfferSort): SalesOffer[] {
    return offers.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sort.field) {
        case 'createdAt':
          aValue = a.createdAt;
          bValue = b.createdAt;
          break;
        case 'updatedAt':
          aValue = a.updatedAt;
          bValue = b.updatedAt;
          break;
        case 'validUntil':
          aValue = a.validUntil;
          bValue = b.validUntil;
          break;
        case 'totalAmount':
          aValue = a.totalAmount;
          bValue = b.totalAmount;
          break;
        case 'offerNumber':
          aValue = a.offerNumber;
          bValue = b.offerNumber;
          break;
        default:
          return 0;
      }

      if (aValue < bValue) {
        return sort.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sort.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }
}