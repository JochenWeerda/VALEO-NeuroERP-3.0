/**
 * Sales Offer Service
 * ISO 27001 Communications Security Compliant
 */

import { SalesOffer, SalesOfferItem, SalesOfferStatus, SalesOfferItemType } from '../entities/sales-offer';
import { SalesOfferRepository, SalesOfferFilter, SalesOfferSort, PaginatedResult } from '../../infra/repositories/sales-offer-repository';

export interface SalesOfferServiceDependencies {
  salesOfferRepository: SalesOfferRepository;
}

export class SalesOfferService {
  constructor(private repository: SalesOfferRepository) {}

  /**
   * Create a new sales offer
   */
  async createSalesOffer(
    customerId: string,
    subject: string,
    description: string,
    validUntil: Date,
    items: Array<{
      itemType: SalesOfferItemType;
      articleId?: string;
      description: string;
      quantity: number;
      unitPrice: number;
      discountPercent?: number;
      notes?: string;
    }>,
    createdBy: string,
    options: {
      customerInquiryId?: string;
      contactPerson?: string;
      deliveryDate?: Date;
      paymentTerms?: string;
      currency?: string;
      taxRate?: number;
      notes?: string;
    } = {}
  ): Promise<SalesOffer> {
    // Validate input
    this.validateCreateInput(customerId, subject, description, validUntil, items, createdBy);

    // Create items
    const salesOfferItems = items.map(item =>
      new SalesOfferItem(
        '', // Will be set by SalesOffer constructor
        item.itemType,
        item.description,
        item.quantity,
        item.unitPrice,
        item.discountPercent || 0,
        item.articleId,
        item.notes
      )
    );

    // Create offer
    const offer = new SalesOffer(
      customerId,
      subject,
      description,
      validUntil,
      salesOfferItems,
      createdBy,
      options
    );

    // Save to repository
    return await this.repository.create(offer);
  }

  /**
   * Update an existing sales offer
   */
  async updateSalesOffer(
    id: string,
    updates: {
      subject?: string;
      description?: string;
      validUntil?: Date;
      contactPerson?: string;
      deliveryDate?: Date;
      paymentTerms?: string;
      currency?: string;
      taxRate?: number;
      notes?: string;
    },
    updatedBy: string
  ): Promise<SalesOffer> {
    const existingOffer = await this.repository.findById(id);
    if (!existingOffer) {
      throw new Error(`Sales offer with id ${id} not found`);
    }

    if (!existingOffer.canBeModified()) {
      throw new Error('Sales offer cannot be modified in its current status');
    }

    // Create updated offer
    const updatedOffer = new SalesOffer(
      existingOffer.customerId,
      updates.subject || existingOffer.subject,
      updates.description || existingOffer.description,
      updates.validUntil || existingOffer.validUntil,
      existingOffer.items,
      existingOffer.createdBy,
      {
        id: existingOffer.id,
        offerNumber: existingOffer.offerNumber,
        customerInquiryId: existingOffer.customerInquiryId || undefined,
        contactPerson: updates.contactPerson !== undefined ? updates.contactPerson : (existingOffer.contactPerson || undefined),
        deliveryDate: updates.deliveryDate !== undefined ? updates.deliveryDate : (existingOffer.deliveryDate || undefined),
        paymentTerms: updates.paymentTerms !== undefined ? updates.paymentTerms : (existingOffer.paymentTerms || undefined),
        currency: updates.currency || existingOffer.currency,
        taxRate: updates.taxRate !== undefined ? updates.taxRate : existingOffer.taxRate,
        notes: updates.notes !== undefined ? updates.notes : existingOffer.notes,
        status: existingOffer.status,
        version: existingOffer.version,
        sentAt: existingOffer.sentAt,
        sentBy: existingOffer.sentBy,
        acceptedAt: existingOffer.acceptedAt,
        acceptedBy: existingOffer.acceptedBy,
        rejectedAt: existingOffer.rejectedAt,
        rejectedBy: existingOffer.rejectedBy,
        rejectionReason: existingOffer.rejectionReason,
        createdAt: existingOffer.createdAt,
        updatedAt: new Date()
      }
    );

    return await this.repository.update(id, updatedOffer);
  }

  /**
   * Add item to sales offer
   */
  async addItemToOffer(
    offerId: string,
    item: {
      itemType: SalesOfferItemType;
      articleId?: string;
      description: string;
      quantity: number;
      unitPrice: number;
      discountPercent?: number;
      notes?: string;
    }
  ): Promise<SalesOffer> {
    const existingOffer = await this.repository.findById(offerId);
    if (!existingOffer) {
      throw new Error(`Sales offer with id ${offerId} not found`);
    }

    if (!existingOffer.canBeModified()) {
      throw new Error('Items cannot be added to offers that are not in draft status');
    }

    const newItem = new SalesOfferItem(
      offerId,
      item.itemType,
      item.description,
      item.quantity,
      item.unitPrice,
      item.discountPercent || 0,
      item.articleId,
      item.notes
    );

    const updatedOffer = existingOffer.addItem(newItem);
    return await this.repository.update(offerId, updatedOffer);
  }

  /**
   * Update item in sales offer
   */
  async updateOfferItem(
    offerId: string,
    itemId: string,
    updates: {
      quantity?: number;
      discountPercent?: number;
      notes?: string;
    }
  ): Promise<SalesOffer> {
    const existingOffer = await this.repository.findById(offerId);
    if (!existingOffer) {
      throw new Error(`Sales offer with id ${offerId} not found`);
    }

    if (!existingOffer.canBeModified()) {
      throw new Error('Items cannot be updated in offers that are not in draft status');
    }

    const existingItem = existingOffer.items.find(item => item.id === itemId);
    if (!existingItem) {
      throw new Error(`Item with id ${itemId} not found in offer`);
    }

    let updatedItem = existingItem;
    if (updates.quantity !== undefined) {
      updatedItem = updatedItem.updateQuantity(updates.quantity);
    }
    if (updates.discountPercent !== undefined) {
      updatedItem = updatedItem.updateDiscount(updates.discountPercent);
    }
    if (updates.notes !== undefined) {
      // Create new item with updated notes
      updatedItem = new SalesOfferItem(
        existingItem.offerId,
        existingItem.itemType,
        existingItem.description,
        updatedItem.quantity,
        updatedItem.unitPrice,
        updatedItem.discountPercent,
        existingItem.articleId,
        updates.notes,
        existingItem.id
      );
    }

    const updatedOffer = existingOffer.updateItem(updatedItem);
    return await this.repository.update(offerId, updatedOffer);
  }

  /**
   * Remove item from sales offer
   */
  async removeItemFromOffer(offerId: string, itemId: string): Promise<SalesOffer> {
    const existingOffer = await this.repository.findById(offerId);
    if (!existingOffer) {
      throw new Error(`Sales offer with id ${offerId} not found`);
    }

    if (!existingOffer.canBeModified()) {
      throw new Error('Items cannot be removed from offers that are not in draft status');
    }

    const updatedOffer = existingOffer.removeItem(itemId);
    return await this.repository.update(offerId, updatedOffer);
  }

  /**
   * Send sales offer to customer
   */
  async sendSalesOffer(offerId: string, sentBy: string): Promise<SalesOffer> {
    const existingOffer = await this.repository.findById(offerId);
    if (!existingOffer) {
      throw new Error(`Sales offer with id ${offerId} not found`);
    }

    if (existingOffer.items.length === 0) {
      throw new Error('Cannot send offer without items');
    }

    const sentOffer = existingOffer.send(sentBy);
    return await this.repository.update(offerId, sentOffer);
  }

  /**
   * Accept sales offer
   */
  async acceptSalesOffer(offerId: string, acceptedBy: string): Promise<SalesOffer> {
    const existingOffer = await this.repository.findById(offerId);
    if (!existingOffer) {
      throw new Error(`Sales offer with id ${offerId} not found`);
    }

    const acceptedOffer = existingOffer.accept(acceptedBy);
    return await this.repository.update(offerId, acceptedOffer);
  }

  /**
   * Reject sales offer
   */
  async rejectSalesOffer(offerId: string, rejectedBy: string, reason: string): Promise<SalesOffer> {
    const existingOffer = await this.repository.findById(offerId);
    if (!existingOffer) {
      throw new Error(`Sales offer with id ${offerId} not found`);
    }

    const rejectedOffer = existingOffer.reject(rejectedBy, reason);
    return await this.repository.update(offerId, rejectedOffer);
  }

  /**
   * Get sales offer by ID
   */
  async getSalesOfferById(id: string): Promise<SalesOffer | null> {
    return await this.repository.findById(id);
  }

  /**
   * Get sales offer by offer number
   */
  async getSalesOfferByNumber(offerNumber: string): Promise<SalesOffer | null> {
    return await this.repository.findByOfferNumber(offerNumber);
  }

  /**
   * Get sales offers by customer
   */
  async getSalesOffersByCustomer(customerId: string): Promise<SalesOffer[]> {
    return await this.repository.findByCustomerId(customerId);
  }

  /**
   * Get sales offers by customer inquiry
   */
  async getSalesOffersByInquiry(customerInquiryId: string): Promise<SalesOffer[]> {
    return await this.repository.findByCustomerInquiryId(customerInquiryId);
  }

  /**
   * List sales offers with filtering and pagination
   */
  async listSalesOffers(
    filter: SalesOfferFilter = {},
    sort: SalesOfferSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResult<SalesOffer>> {
    return await this.repository.findAll(filter, sort, page, pageSize);
  }

  /**
   * Get expired sales offers
   */
  async getExpiredSalesOffers(): Promise<SalesOffer[]> {
    return await this.repository.findExpired();
  }

  /**
   * Get valid sales offers
   */
  async getValidSalesOffers(): Promise<SalesOffer[]> {
    return await this.repository.findValid();
  }

  /**
   * Delete sales offer
   */
  async deleteSalesOffer(id: string): Promise<boolean> {
    const existingOffer = await this.repository.findById(id);
    if (!existingOffer) {
      return false;
    }

    if (existingOffer.status !== SalesOfferStatus.ENTWURF) {
      throw new Error('Only draft offers can be deleted');
    }

    return await this.repository.delete(id);
  }

  /**
   * Get sales offer statistics
   */
  async getSalesOfferStatistics(): Promise<{
    total: number;
    byStatus: Record<SalesOfferStatus, number>;
    totalValue: number;
    averageValue: number;
    conversionRate: number;
  }> {
    return await this.repository.getStatistics();
  }

  /**
   * Create sales offer from customer inquiry
   */
  async createOfferFromInquiry(
    customerInquiryId: string,
    offerData: {
      offerNumber: string;
      totalAmount: number;
      validUntil: Date;
      deliveryDate?: Date;
      paymentTerms?: string;
      notes?: string;
    },
    createdBy: string
  ): Promise<SalesOffer> {
    // In a real implementation, this would fetch the customer inquiry
    // and pre-populate the offer with inquiry data
    // For now, we'll create a basic offer structure

    const items = [
      new SalesOfferItem(
        '', // Will be set by SalesOffer
        SalesOfferItemType.SERVICE,
        'Services based on customer inquiry',
        1,
        offerData.totalAmount,
        0
      )
    ];

    const offer = new SalesOffer(
      'customer-from-inquiry', // Would be fetched from inquiry
      `Offer for Inquiry ${customerInquiryId}`,
      'Sales offer created from customer inquiry',
      offerData.validUntil,
      items,
      createdBy,
      {
        offerNumber: offerData.offerNumber,
        customerInquiryId,
        ...(offerData.deliveryDate && { deliveryDate: offerData.deliveryDate }),
        ...(offerData.paymentTerms && { paymentTerms: offerData.paymentTerms }),
        ...(offerData.notes && { notes: offerData.notes })
      }
    );

    return await this.repository.create(offer);
  }

  /**
   * Validate business rules for sales offer creation
   */
  private validateCreateInput(
    customerId: string,
    subject: string,
    description: string,
    validUntil: Date,
    items: Array<{
      itemType: SalesOfferItemType;
      articleId?: string;
      description: string;
      quantity: number;
      unitPrice: number;
      discountPercent?: number;
      notes?: string;
    }>,
    createdBy: string
  ): void {
    if (!customerId || customerId.trim().length === 0) {
      throw new Error('Customer ID is required');
    }

    if (!subject || subject.trim().length === 0) {
      throw new Error('Subject is required');
    }

    if (!description || description.trim().length === 0) {
      throw new Error('Description is required');
    }

    if (!validUntil || validUntil <= new Date()) {
      throw new Error('Valid until date must be in the future');
    }

    if (!items || items.length === 0) {
      throw new Error('At least one item is required');
    }

    if (!createdBy || createdBy.trim().length === 0) {
      throw new Error('Created by is required');
    }

    // Validate items
    for (const item of items) {
      if (!item.description || item.description.trim().length === 0) {
        throw new Error('Item description is required');
      }

      if (item.quantity <= 0) {
        throw new Error('Item quantity must be positive');
      }

      if (item.unitPrice < 0) {
        throw new Error('Item unit price cannot be negative');
      }

      if (item.discountPercent !== undefined && (item.discountPercent < 0 || item.discountPercent > 100)) {
        throw new Error('Item discount percent must be between 0 and 100');
      }
    }

    // Business rule: Valid until should not be more than 1 year in the future
    const oneYearFromNow = new Date();
    oneYearFromNow.setFullYear(oneYearFromNow.getFullYear() + 1);

    if (validUntil > oneYearFromNow) {
      throw new Error('Valid until date cannot be more than 1 year in the future');
    }
  }
}