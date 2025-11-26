/**
 * Delivery Note Service
 * ISO 27001 Communications Security Compliant
 */

import { DeliveryNote, DeliveryNoteItem, DeliveryNoteStatus, DeliveryNoteItemType } from '../entities/delivery-note';
import { DeliveryNoteRepository, DeliveryNoteFilter, DeliveryNoteSort, PaginatedResult } from '../../infra/repositories/delivery-note-repository';

export interface DeliveryNoteServiceDependencies {
  deliveryNoteRepository: DeliveryNoteRepository;
}

export class DeliveryNoteService {
  constructor(private repository: DeliveryNoteRepository) {}

  /**
   * Create a new delivery note
   */
  async createDeliveryNote(
    customerId: string,
    subject: string,
    description: string,
    deliveryDate: Date,
    shippingAddress: {
      street: string;
      postalCode: string;
      city: string;
      country: string;
    },
    items: Array<{
      itemType: DeliveryNoteItemType;
      articleId?: string;
      description: string;
      quantity: number;
      unitPrice: number;
      discountPercent?: number;
      notes?: string;
    }>,
    createdBy: string,
    options: {
      salesOfferId?: string;
      carrierId?: string;
      trackingNumber?: string;
      notes?: string;
    } = {}
  ): Promise<DeliveryNote> {
    // Validate input
    this.validateCreateInput(customerId, subject, description, deliveryDate, shippingAddress, items, createdBy);

    // Create items
    const deliveryNoteItems = items.map(item =>
      new DeliveryNoteItem(
        '', // Will be set by DeliveryNote constructor
        item.itemType,
        item.description,
        item.quantity,
        item.unitPrice,
        item.discountPercent || 0,
        item.articleId,
        item.notes
      )
    );

    // Create delivery note
    const deliveryNote = new DeliveryNote(
      customerId,
      subject,
      description,
      deliveryDate,
      shippingAddress,
      deliveryNoteItems,
      createdBy,
      options
    );

    // Save to repository
    return await this.repository.create(deliveryNote);
  }

  /**
   * Create delivery note from sales offer
   */
  async createFromSalesOffer(
    salesOfferId: string,
    deliveryDate: Date,
    shippingAddress: {
      street: string;
      postalCode: string;
      city: string;
      country: string;
    },
    createdBy: string,
    options: {
      carrierId?: string;
      trackingNumber?: string;
      notes?: string;
    } = {}
  ): Promise<DeliveryNote> {
    // In a real implementation, this would fetch the sales offer
    // and pre-populate the delivery note with offer data
    // For now, we'll create a basic delivery note structure

    const items = [
      new DeliveryNoteItem(
        '', // Will be set by DeliveryNote
        DeliveryNoteItemType.PRODUCT,
        'Products from sales offer',
        1,
        100, // Would be calculated from sales offer
        0
      )
    ];

    const deliveryNote = new DeliveryNote(
      'customer-from-offer', // Would be fetched from sales offer
      `Delivery for Sales Offer ${salesOfferId}`,
      'Delivery note created from sales offer',
      deliveryDate,
      shippingAddress,
      items,
      createdBy,
      {
        salesOfferId,
        ...options
      }
    );

    return await this.repository.create(deliveryNote);
  }

  /**
   * Update an existing delivery note
   */
  async updateDeliveryNote(
    id: string,
    updates: {
      subject?: string;
      description?: string;
      deliveryDate?: Date;
      shippingAddress?: {
        street: string;
        postalCode: string;
        city: string;
        country: string;
      };
      carrierId?: string;
      trackingNumber?: string;
      notes?: string;
    },
    updatedBy: string
  ): Promise<DeliveryNote> {
    const existingNote = await this.repository.findById(id);
    if (!existingNote) {
      throw new Error(`Delivery note with id ${id} not found`);
    }

    if (!existingNote.canBeModified()) {
      throw new Error('Delivery note cannot be modified in its current status');
    }

    // Create updated note
    const updatedNote = new DeliveryNote(
      existingNote.customerId,
      updates.subject || existingNote.subject,
      updates.description || existingNote.description,
      updates.deliveryDate || existingNote.deliveryDate,
      updates.shippingAddress || existingNote.shippingAddress,
      existingNote.items,
      existingNote.createdBy,
      {
        id: existingNote.id,
        deliveryNoteNumber: existingNote.deliveryNoteNumber,
        salesOfferId: existingNote.salesOfferId,
        carrierId: updates.carrierId !== undefined ? updates.carrierId : existingNote.carrierId,
        trackingNumber: updates.trackingNumber !== undefined ? updates.trackingNumber : existingNote.trackingNumber,
        notes: updates.notes !== undefined ? updates.notes : existingNote.notes,
        status: existingNote.status,
        version: existingNote.version,
        shippedAt: existingNote.shippedAt,
        shippedBy: existingNote.shippedBy,
        deliveredAt: existingNote.deliveredAt,
        deliveredBy: existingNote.deliveredBy,
        createdAt: existingNote.createdAt,
        updatedAt: new Date()
      }
    );

    return await this.repository.update(id, updatedNote);
  }

  /**
   * Ship delivery note
   */
  async shipDeliveryNote(
    id: string,
    shippedBy: string,
    carrierId?: string,
    trackingNumber?: string
  ): Promise<DeliveryNote> {
    const existingNote = await this.repository.findById(id);
    if (!existingNote) {
      throw new Error(`Delivery note with id ${id} not found`);
    }

    const shippedNote = existingNote.ship(shippedBy, carrierId, trackingNumber);
    return await this.repository.update(id, shippedNote);
  }

  /**
   * Mark delivery note as delivered
   */
  async deliverDeliveryNote(id: string, deliveredBy: string): Promise<DeliveryNote> {
    const existingNote = await this.repository.findById(id);
    if (!existingNote) {
      throw new Error(`Delivery note with id ${id} not found`);
    }

    const deliveredNote = existingNote.deliver(deliveredBy);
    return await this.repository.update(id, deliveredNote);
  }

  /**
   * Cancel delivery note
   */
  async cancelDeliveryNote(id: string): Promise<DeliveryNote> {
    const existingNote = await this.repository.findById(id);
    if (!existingNote) {
      throw new Error(`Delivery note with id ${id} not found`);
    }

    const cancelledNote = existingNote.cancel();
    return await this.repository.update(id, cancelledNote);
  }

  /**
   * Get delivery note by ID
   */
  async getDeliveryNoteById(id: string): Promise<DeliveryNote | null> {
    return await this.repository.findById(id);
  }

  /**
   * Get delivery note by number
   */
  async getDeliveryNoteByNumber(deliveryNoteNumber: string): Promise<DeliveryNote | null> {
    return await this.repository.findByDeliveryNoteNumber(deliveryNoteNumber);
  }

  /**
   * Get delivery notes by customer
   */
  async getDeliveryNotesByCustomer(customerId: string): Promise<DeliveryNote[]> {
    return await this.repository.findByCustomerId(customerId);
  }

  /**
   * Get delivery notes by sales offer
   */
  async getDeliveryNotesBySalesOffer(salesOfferId: string): Promise<DeliveryNote[]> {
    return await this.repository.findBySalesOfferId(salesOfferId);
  }

  /**
   * List delivery notes with filtering and pagination
   */
  async listDeliveryNotes(
    filter: DeliveryNoteFilter = {},
    sort: DeliveryNoteSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResult<DeliveryNote>> {
    return await this.repository.findAll(filter, sort, page, pageSize);
  }

  /**
   * Get overdue delivery notes
   */
  async getOverdueDeliveryNotes(): Promise<DeliveryNote[]> {
    return await this.repository.findOverdue();
  }

  /**
   * Delete delivery note
   */
  async deleteDeliveryNote(id: string): Promise<boolean> {
    const existingNote = await this.repository.findById(id);
    if (!existingNote) {
      return false;
    }

    if (existingNote.status !== DeliveryNoteStatus.ENTWURF) {
      throw new Error('Only draft delivery notes can be deleted');
    }

    return await this.repository.delete(id);
  }

  /**
   * Get delivery note statistics
   */
  async getDeliveryNoteStatistics(): Promise<{
    total: number;
    byStatus: Record<DeliveryNoteStatus, number>;
    totalValue: number;
    averageValue: number;
    onTimeDeliveryRate: number;
  }> {
    return await this.repository.getStatistics();
  }

  /**
   * Validate business rules for delivery note creation
   */
  private validateCreateInput(
    customerId: string,
    subject: string,
    description: string,
    deliveryDate: Date,
    shippingAddress: {
      street: string;
      postalCode: string;
      city: string;
      country: string;
    },
    items: Array<{
      itemType: DeliveryNoteItemType;
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

    if (!deliveryDate || deliveryDate <= new Date()) {
      throw new Error('Delivery date must be in the future');
    }

    if (!shippingAddress || !shippingAddress.street || !shippingAddress.postalCode || !shippingAddress.city || !shippingAddress.country) {
      throw new Error('Complete shipping address is required');
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
  }
}