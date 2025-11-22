/**
 * Delivery Note Repository
 * Complete CRUD operations for Delivery Notes
 */

import { DeliveryNote, DeliveryNoteStatus } from '../../domain/entities/delivery-note';

export interface DeliveryNoteFilter {
  customerId?: string;
  orderId?: string;
  status?: DeliveryNoteStatus;
  carrierName?: string;
  plannedDeliveryDateFrom?: Date;
  plannedDeliveryDateTo?: Date;
  actualDeliveryDateFrom?: Date;
  actualDeliveryDateTo?: Date;
  createdBy?: string;
  overdue?: boolean;
  trackingNumber?: string;
  search?: string; // Search in deliveryNoteNumber, orderId, carrier info
}

export interface DeliveryNoteSort {
  field: 'createdAt' | 'updatedAt' | 'plannedDeliveryDate' | 'actualDeliveryDate' | 'totalAmount' | 'deliveryNoteNumber' | 'status';
  direction: 'asc' | 'desc';
}

export interface PaginatedDeliveryNoteResult {
  items: DeliveryNote[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export class DeliveryNoteRepository {
  private deliveryNotes: Map<string, DeliveryNote> = new Map();

  async create(deliveryNote: DeliveryNote): Promise<DeliveryNote> {
    this.deliveryNotes.set(deliveryNote.id, deliveryNote);
    return deliveryNote;
  }

  async findById(id: string): Promise<DeliveryNote | null> {
    return this.deliveryNotes.get(id) || null;
  }

  async findByDeliveryNoteNumber(deliveryNoteNumber: string): Promise<DeliveryNote | null> {
    for (const deliveryNote of this.deliveryNotes.values()) {
      if (deliveryNote.deliveryNoteNumber === deliveryNoteNumber) {
        return deliveryNote;
      }
    }
    return null;
  }

  async update(deliveryNote: DeliveryNote): Promise<DeliveryNote> {
    if (!this.deliveryNotes.has(deliveryNote.id)) {
      throw new Error('Delivery note not found');
    }
    this.deliveryNotes.set(deliveryNote.id, deliveryNote);
    return deliveryNote;
  }

  async delete(id: string): Promise<boolean> {
    return this.deliveryNotes.delete(id);
  }

  async findByOrderId(orderId: string): Promise<DeliveryNote[]> {
    const deliveryNotes: DeliveryNote[] = [];
    for (const deliveryNote of this.deliveryNotes.values()) {
      if (deliveryNote.orderId === orderId) {
        deliveryNotes.push(deliveryNote);
      }
    }
    return deliveryNotes.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async list(
    filter: DeliveryNoteFilter = {},
    sort: DeliveryNoteSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedDeliveryNoteResult> {
    let filteredDeliveryNotes = Array.from(this.deliveryNotes.values());

    // Apply filters
    if (filter.customerId) {
      filteredDeliveryNotes = filteredDeliveryNotes.filter(dn => dn.customerId === filter.customerId);
    }

    if (filter.orderId) {
      filteredDeliveryNotes = filteredDeliveryNotes.filter(dn => dn.orderId === filter.orderId);
    }

    if (filter.status) {
      filteredDeliveryNotes = filteredDeliveryNotes.filter(dn => dn.status === filter.status);
    }

    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      filteredDeliveryNotes = filteredDeliveryNotes.filter(dn => 
        dn.deliveryNoteNumber.toLowerCase().includes(searchLower) ||
        dn.orderId.toLowerCase().includes(searchLower)
      );
    }

    // Apply sorting
    filteredDeliveryNotes.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sort.field) {
        case 'createdAt':
          aValue = a.createdAt.getTime();
          bValue = b.createdAt.getTime();
          break;
        case 'plannedDeliveryDate':
          aValue = a.plannedDeliveryDate.getTime();
          bValue = b.plannedDeliveryDate.getTime();
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        default:
          aValue = a.createdAt.getTime();
          bValue = b.createdAt.getTime();
      }

      if (sort.direction === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    // Apply pagination
    const total = filteredDeliveryNotes.length;
    const totalPages = Math.ceil(total / pageSize);
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const items = filteredDeliveryNotes.slice(startIndex, endIndex);

    return {
      items,
      total,
      page,
      pageSize,
      totalPages,
      hasNext: page < totalPages,
      hasPrev: page > 1
    };
  }
}
