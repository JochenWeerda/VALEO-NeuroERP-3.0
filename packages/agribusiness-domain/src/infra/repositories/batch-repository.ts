/**
 * Batch Repository
 * Complete CRUD operations for Batch entities with Traceability support
 */

import { Batch, BatchStatus, BatchType } from '../../domain/entities/batch';

export interface BatchFilter {
  batchNumber?: string;
  batchType?: BatchType;
  productId?: string;
  originCountry?: string;
  status?: BatchStatus;
  parentBatchId?: string;
  qualityCertificateId?: string;
  harvestDateFrom?: Date;
  harvestDateTo?: Date;
  expiryDateFrom?: Date;
  expiryDateTo?: Date;
  expired?: boolean;
  expiringSoon?: boolean;
  search?: string; // Search in batchNumber, notes
}

export interface BatchSort {
  field: 'createdAt' | 'updatedAt' | 'harvestDate' | 'expiryDate' | 'batchNumber' | 'status';
  direction: 'asc' | 'desc';
}

export interface PaginatedBatchResult {
  items: Batch[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export class BatchRepository {
  private batches: Map<string, Batch> = new Map();

  async create(batch: Batch): Promise<Batch> {
    // Check for duplicate batch number
    const existing = await this.findByBatchNumber(batch.batchNumber);
    if (existing && existing.id !== batch.id) {
      throw new Error(`Batch number ${batch.batchNumber} already exists`);
    }

    this.batches.set(batch.id, batch);
    return batch;
  }

  async findById(id: string): Promise<Batch | null> {
    return this.batches.get(id) || null;
  }

  async findByBatchNumber(batchNumber: string): Promise<Batch | null> {
    for (const batch of this.batches.values()) {
      if (batch.batchNumber === batchNumber) {
        return batch;
      }
    }
    return null;
  }

  async update(batch: Batch): Promise<Batch> {
    if (!this.batches.has(batch.id)) {
      throw new Error('Batch not found');
    }

    // Check for duplicate batch number (excluding current batch)
    const existing = await this.findByBatchNumber(batch.batchNumber);
    if (existing && existing.id !== batch.id) {
      throw new Error(`Batch number ${batch.batchNumber} already exists`);
    }

    this.batches.set(batch.id, batch);
    return batch;
  }

  async delete(id: string): Promise<boolean> {
    return this.batches.delete(id);
  }

  async findByProductId(productId: string): Promise<Batch[]> {
    const batches: Batch[] = [];
    for (const batch of this.batches.values()) {
      if (batch.productId === productId) {
        batches.push(batch);
      }
    }
    return batches.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async findByParentBatchId(parentBatchId: string): Promise<Batch[]> {
    const batches: Batch[] = [];
    for (const batch of this.batches.values()) {
      if (batch.parentBatchId === parentBatchId) {
        batches.push(batch);
      }
    }
    return batches.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async findByStatus(status: BatchStatus): Promise<Batch[]> {
    const batches: Batch[] = [];
    for (const batch of this.batches.values()) {
      if (batch.status === status) {
        batches.push(batch);
      }
    }
    return batches.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async findExpiredBatches(): Promise<Batch[]> {
    const batches: Batch[] = [];
    for (const batch of this.batches.values()) {
      if (batch.isExpired()) {
        batches.push(batch);
      }
    }
    return batches.sort((a, b) => {
      const aExpiry = a.expiryDate?.getTime() || 0;
      const bExpiry = b.expiryDate?.getTime() || 0;
      return aExpiry - bExpiry;
    });
  }

  async findExpiringSoonBatches(days: number = 30): Promise<Batch[]> {
    const batches: Batch[] = [];
    for (const batch of this.batches.values()) {
      if (batch.isExpiringSoon(days)) {
        batches.push(batch);
      }
    }
    return batches.sort((a, b) => {
      const aExpiry = a.expiryDate?.getTime() || 0;
      const bExpiry = b.expiryDate?.getTime() || 0;
      return aExpiry - bExpiry;
    });
  }

  async getTraceabilityChain(batchId: string): Promise<Batch[]> {
    const chain: Batch[] = [];
    let currentBatch = await this.findById(batchId);

    if (!currentBatch) {
      return chain;
    }

    // Build chain from root to current batch
    const visited = new Set<string>();
    const buildChain = async (batch: Batch): Promise<void> => {
      if (visited.has(batch.id)) {
        return; // Prevent circular references
      }
      visited.add(batch.id);

      if (batch.parentBatchId) {
        const parent = await this.findById(batch.parentBatchId);
        if (parent) {
          await buildChain(parent);
        }
      }

      chain.push(batch);
    };

    await buildChain(currentBatch);
    return chain;
  }

  async getTraceabilityTree(batchId: string): Promise<Batch[]> {
    const tree: Batch[] = [];
    const rootBatch = await this.findById(batchId);

    if (!rootBatch) {
      return tree;
    }

    const buildTree = async (batch: Batch): Promise<void> => {
      tree.push(batch);
      const children = await this.findByParentBatchId(batch.id);
      for (const child of children) {
        await buildTree(child);
      }
    };

    await buildTree(rootBatch);
    return tree;
  }

  async list(
    filter: BatchFilter = {},
    sort: BatchSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedBatchResult> {
    let filteredBatches = Array.from(this.batches.values());

    // Apply filters
    if (filter.batchNumber) {
      filteredBatches = filteredBatches.filter(batch => 
        batch.batchNumber.toLowerCase().includes(filter.batchNumber!.toLowerCase())
      );
    }

    if (filter.batchType) {
      filteredBatches = filteredBatches.filter(batch => batch.batchType === filter.batchType);
    }

    if (filter.productId) {
      filteredBatches = filteredBatches.filter(batch => batch.productId === filter.productId);
    }

    if (filter.originCountry) {
      filteredBatches = filteredBatches.filter(batch => batch.originCountry === filter.originCountry);
    }

    if (filter.status) {
      filteredBatches = filteredBatches.filter(batch => batch.status === filter.status);
    }

    if (filter.parentBatchId) {
      filteredBatches = filteredBatches.filter(batch => batch.parentBatchId === filter.parentBatchId);
    }

    if (filter.qualityCertificateId) {
      filteredBatches = filteredBatches.filter(batch => batch.qualityCertificateId === filter.qualityCertificateId);
    }

    if (filter.harvestDateFrom) {
      filteredBatches = filteredBatches.filter(batch => 
        batch.harvestDate && batch.harvestDate >= filter.harvestDateFrom!
      );
    }

    if (filter.harvestDateTo) {
      filteredBatches = filteredBatches.filter(batch => 
        batch.harvestDate && batch.harvestDate <= filter.harvestDateTo!
      );
    }

    if (filter.expiryDateFrom) {
      filteredBatches = filteredBatches.filter(batch => 
        batch.expiryDate && batch.expiryDate >= filter.expiryDateFrom!
      );
    }

    if (filter.expiryDateTo) {
      filteredBatches = filteredBatches.filter(batch => 
        batch.expiryDate && batch.expiryDate <= filter.expiryDateTo!
      );
    }

    if (filter.expired === true) {
      filteredBatches = filteredBatches.filter(batch => batch.isExpired());
    }

    if (filter.expiringSoon === true) {
      filteredBatches = filteredBatches.filter(batch => batch.isExpiringSoon());
    }

    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      filteredBatches = filteredBatches.filter(batch => 
        batch.batchNumber.toLowerCase().includes(searchLower) ||
        (batch.notes && batch.notes.toLowerCase().includes(searchLower))
      );
    }

    // Apply sorting
    filteredBatches.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sort.field) {
        case 'createdAt':
          aValue = a.createdAt.getTime();
          bValue = b.createdAt.getTime();
          break;
        case 'updatedAt':
          aValue = a.updatedAt.getTime();
          bValue = b.updatedAt.getTime();
          break;
        case 'harvestDate':
          aValue = a.harvestDate?.getTime() || 0;
          bValue = b.harvestDate?.getTime() || 0;
          break;
        case 'expiryDate':
          aValue = a.expiryDate?.getTime() || 0;
          bValue = b.expiryDate?.getTime() || 0;
          break;
        case 'batchNumber':
          aValue = a.batchNumber;
          bValue = b.batchNumber;
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
    const total = filteredBatches.length;
    const totalPages = Math.ceil(total / pageSize);
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const items = filteredBatches.slice(startIndex, endIndex);

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

  async getStatistics(): Promise<{
    total: number;
    byStatus: Record<BatchStatus, number>;
    byType: Record<BatchType, number>;
    expiredCount: number;
    expiringSoonCount: number;
    totalQuantity: number;
    allocatedQuantity: number;
    availableQuantity: number;
  }> {
    const allBatches = Array.from(this.batches.values());
    const total = allBatches.length;

    const byStatus: Record<BatchStatus, number> = {
      'ACTIVE': 0,
      'ON_HOLD': 0,
      'BLOCKED': 0,
      'EXPIRED': 0,
      'CONSUMED': 0
    };

    const byType: Record<BatchType, number> = {
      'SEED': 0,
      'CROP': 0,
      'FERTILIZER': 0,
      'FEED': 0,
      'PRODUCT': 0
    };

    let expiredCount = 0;
    let expiringSoonCount = 0;
    let totalQuantity = 0;
    let allocatedQuantity = 0;

    for (const batch of allBatches) {
      byStatus[batch.status]++;
      byType[batch.batchType]++;
      
      if (batch.isExpired()) expiredCount++;
      if (batch.isExpiringSoon()) expiringSoonCount++;
      
      totalQuantity += batch.remainingQuantity;
      allocatedQuantity += batch.allocatedQuantity;
    }

    return {
      total,
      byStatus,
      byType,
      expiredCount,
      expiringSoonCount,
      totalQuantity,
      allocatedQuantity,
      availableQuantity: totalQuantity - allocatedQuantity
    };
  }

  async isBatchNumberUnique(batchNumber: string, excludeId?: string): Promise<boolean> {
    for (const batch of this.batches.values()) {
      if (batch.batchNumber === batchNumber && batch.id !== excludeId) {
        return false;
      }
    }
    return true;
  }
}
