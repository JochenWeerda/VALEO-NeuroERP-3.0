/**
 * Batch Repository Interface for VALEO NeuroERP 3.0 Production Domain
 * Repository interface for batch management with traceability
 */

import type { Batch } from '../entities/batch';

export interface BatchFilters {
  status?: 'Released' | 'Quarantine' | 'Rejected';
  mixOrderId?: string;
  dateFrom?: string;
  dateTo?: string;
  labels?: string[];
  search?: string;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
  filters?: BatchFilters;
}

export interface PaginatedResult<T> {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}

export interface BatchStatistics {
  totalBatches: number;
  releasedBatches: number;
  quarantinedBatches: number;
  rejectedBatches: number;
  totalMassKg: number;
  averageYield: number;
}

export interface TraceabilityData {
  batchId: string;
  batchNumber: string;
  mixOrderId: string;
  recipeId: string;
  inputs: Array<{
    ingredientLotId: string;
    plannedKg: number;
    actualKg: number;
  }>;
  outputs: Array<{
    lotNumber: string;
    qtyKg: number;
    destination: string;
    packing: any; // eslint-disable-line @typescript-eslint/no-explicit-any
  }>;
  parentBatches: string[];
  labels: string[];
}

export interface BatchRepository {
  // Basic CRUD operations
  save(tenantId: string, batch: Batch): Promise<Batch>;
  findById(tenantId: string, id: string): Promise<Batch | null>;
  findByBatchNumber(tenantId: string, batchNumber: string): Promise<Batch | null>;
  findAll(tenantId: string, filters?: BatchFilters): Promise<Batch[]>;
  delete(tenantId: string, id: string): Promise<void>;

  // Pagination support
  findWithPagination(tenantId: string, options: PaginationOptions): Promise<PaginatedResult<Batch>>;

  // Business queries
  findByStatus(tenantId: string, status: Batch['status']): Promise<Batch[]>;
  findByMixOrder(tenantId: string, mixOrderId: string): Promise<Batch[]>;
  findByDateRange(tenantId: string, from: string, to: string): Promise<Batch[]>;
  findByLabel(tenantId: string, label: string): Promise<Batch[]>;
  findReleasedBatches(tenantId: string): Promise<Batch[]>;
  findQuarantinedBatches(tenantId: string): Promise<Batch[]>;
  findRejectedBatches(tenantId: string): Promise<Batch[]>;

  // Traceability queries
  findByInputLot(tenantId: string, ingredientLotId: string): Promise<Batch[]>;
  findByOutputLot(tenantId: string, lotNumber: string): Promise<Batch[]>;
  findParentBatches(tenantId: string, batchId: string): Promise<Batch[]>;
  findChildBatches(tenantId: string, parentBatchId: string): Promise<Batch[]>;
  getTraceabilityData(tenantId: string, batchId: string): Promise<TraceabilityData | null>;
  getTraceabilityByLotNumber(tenantId: string, lotNumber: string): Promise<TraceabilityData | null>;

  // Bulk operations
  bulkSave(tenantId: string, batches: Batch[]): Promise<Batch[]>;
  bulkDelete(tenantId: string, ids: string[]): Promise<void>;
  bulkUpdateStatus(tenantId: string, ids: string[], status: Batch['status']): Promise<void>;

  // Statistics
  getStatistics(tenantId: string, filters?: BatchFilters): Promise<BatchStatistics>;
  getBatchCount(tenantId: string, filters?: BatchFilters): Promise<number>;
  getTotalMassProduced(tenantId: string, filters?: BatchFilters): Promise<number>;
  getAverageYield(tenantId: string, filters?: BatchFilters): Promise<number>;
  getYieldDistribution(tenantId: string, filters?: BatchFilters): Promise<Array<{ range: string; count: number }>>;
}

