/**
 * Delivery Note Repository
 * ISO 27001 Communications Security Compliant
 */

import { DeliveryNote, DeliveryNoteStatus } from '../../domain/entities/delivery-note';

export interface DeliveryNoteFilter {
  customerId?: string;
  salesOfferId?: string;
  status?: DeliveryNoteStatus;
  deliveryDateFrom?: Date;
  deliveryDateTo?: Date;
  shipped?: boolean;
  delivered?: boolean;
  overdue?: boolean;
}

export interface DeliveryNoteSort {
  field: 'createdAt' | 'deliveryDate' | 'deliveryNoteNumber' | 'totalAmount';
  direction: 'asc' | 'desc';
}

export interface PaginatedResult<T> {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface DeliveryNoteRepository {
  create(deliveryNote: DeliveryNote): Promise<DeliveryNote>;
  update(id: string, deliveryNote: DeliveryNote): Promise<DeliveryNote>;
  delete(id: string): Promise<boolean>;
  findById(id: string): Promise<DeliveryNote | null>;
  findByDeliveryNoteNumber(deliveryNoteNumber: string): Promise<DeliveryNote | null>;
  findByCustomerId(customerId: string): Promise<DeliveryNote[]>;
  findBySalesOfferId(salesOfferId: string): Promise<DeliveryNote[]>;
  findAll(
    filter: DeliveryNoteFilter,
    sort: DeliveryNoteSort,
    page: number,
    pageSize: number
  ): Promise<PaginatedResult<DeliveryNote>>;
  findOverdue(): Promise<DeliveryNote[]>;
  getStatistics(): Promise<{
    total: number;
    byStatus: Record<DeliveryNoteStatus, number>;
    totalValue: number;
    averageValue: number;
    onTimeDeliveryRate: number;
  }>;
}