/**
 * Batch Traceability Service
 * Complete Traceability Logic based on Odoo stock_agriculture pattern
 */

import { Batch, BatchTraceabilityTree, BatchTraceabilityNode, CreateBatchInput, UpdateBatchInput } from '../entities/batch';
import { BatchRepository, BatchFilter, BatchSort, PaginatedBatchResult } from '../../infra/repositories/batch-repository';

export interface BatchTraceabilityServiceDependencies {
  batchRepository: BatchRepository;
}

export class BatchTraceabilityService {
  constructor(private deps: BatchTraceabilityServiceDependencies) {}

  // ======================================
  // CORE CRUD OPERATIONS
  // ======================================

  async createBatch(
    input: CreateBatchInput,
    createdBy: string
  ): Promise<Batch> {
    // Validate parent batch if provided
    if (input.parentBatchId) {
      const parentBatch = await this.deps.batchRepository.findById(input.parentBatchId);
      if (!parentBatch) {
        throw new Error('Parent batch not found');
      }
      if (parentBatch.status !== 'ACTIVE') {
        throw new Error('Parent batch must be active');
      }
    }

    const batch = new Batch(
      input.batchNumber,
      input.batchType,
      input.initialQuantity,
      input.unitOfMeasure,
      createdBy,
      {
        productId: input.productId,
        originCountry: input.originCountry,
        harvestDate: input.harvestDate,
        expiryDate: input.expiryDate,
        parentBatchId: input.parentBatchId,
        qualityCertificateId: input.qualityCertificateId,
        notes: input.notes,
        customFields: input.customFields
      }
    );

    return await this.deps.batchRepository.create(batch);
  }

  async getBatchById(id: string): Promise<Batch | null> {
    return await this.deps.batchRepository.findById(id);
  }

  async getBatchByNumber(batchNumber: string): Promise<Batch | null> {
    return await this.deps.batchRepository.findByBatchNumber(batchNumber);
  }

  async updateBatch(
    id: string,
    updates: UpdateBatchInput,
    updatedBy: string
  ): Promise<Batch> {
    const batch = await this.getBatchById(id);
    if (!batch) {
      throw new Error('Batch not found');
    }

    batch.updateBasicInfo(updates, updatedBy);
    return await this.deps.batchRepository.update(batch);
  }

  async deleteBatch(id: string): Promise<boolean> {
    const batch = await this.getBatchById(id);
    if (!batch) {
      return false;
    }

    // Check for child batches
    const children = await this.deps.batchRepository.findByParentBatchId(id);
    if (children.length > 0) {
      throw new Error('Cannot delete batch with child batches');
    }

    return await this.deps.batchRepository.delete(id);
  }

  // ======================================
  // TRACEABILITY OPERATIONS
  // ======================================

  async getTraceabilityTree(batchId: string): Promise<BatchTraceabilityTree> {
    const batch = await this.getBatchById(batchId);
    if (!batch) {
      throw new Error('Batch not found');
    }

    // Build tree recursively
    const buildNode = async (currentBatch: Batch): Promise<BatchTraceabilityNode> => {
      const children = await this.deps.batchRepository.findByParentBatchId(currentBatch.id);
      const childNodes = await Promise.all(children.map(child => buildNode(child)));

      return {
        batchId: currentBatch.id,
        batchNumber: currentBatch.batchNumber,
        batchType: currentBatch.batchType,
        productId: currentBatch.productId,
        quantity: currentBatch.remainingQuantity,
        originCountry: currentBatch.originCountry,
        harvestDate: currentBatch.harvestDate,
        parentBatchId: currentBatch.parentBatchId,
        qualityCertificateId: currentBatch.qualityCertificateId,
        createdAt: currentBatch.createdAt,
        children: childNodes.length > 0 ? childNodes : undefined
      };
    };

    const rootNode = await buildNode(batch);

    // Calculate depth and total batches
    const calculateDepth = (node: BatchTraceabilityNode, currentDepth: number = 0): number => {
      if (!node.children || node.children.length === 0) {
        return currentDepth;
      }
      return Math.max(...node.children.map(child => calculateDepth(child, currentDepth + 1)));
    };

    const countBatches = (node: BatchTraceabilityNode): number => {
      let count = 1;
      if (node.children) {
        count += node.children.reduce((sum, child) => sum + countBatches(child), 0);
      }
      return count;
    };

    // Build traceability chain (root to leaf)
    const buildChain = (node: BatchTraceabilityNode, chain: BatchTraceabilityNode[] = []): BatchTraceabilityNode[] => {
      chain.push(node);
      if (node.children && node.children.length > 0) {
        for (const child of node.children) {
          buildChain(child, chain);
        }
      }
      return chain;
    };

    const depth = calculateDepth(rootNode);
    const totalBatches = countBatches(rootNode);
    const traceabilityChain = buildChain(rootNode);

    return {
      root: rootNode,
      depth,
      totalBatches,
      traceabilityChain
    };
  }

  async getTraceabilityChain(batchId: string): Promise<Batch[]> {
    return await this.deps.batchRepository.getTraceabilityChain(batchId);
  }

  async getUpstreamTraceability(batchId: string): Promise<Batch[]> {
    // Get all parent batches (from root to current)
    return await this.deps.batchRepository.getTraceabilityChain(batchId);
  }

  async getDownstreamTraceability(batchId: string): Promise<Batch[]> {
    // Get all child batches (from current to leaves)
    return await this.deps.batchRepository.getTraceabilityTree(batchId);
  }

  // ======================================
  // BATCH OPERATIONS
  // ======================================

  async allocateBatch(batchId: string, quantity: number): Promise<Batch> {
    const batch = await this.getBatchById(batchId);
    if (!batch) {
      throw new Error('Batch not found');
    }

    batch.allocate(quantity);
    return await this.deps.batchRepository.update(batch);
  }

  async deallocateBatch(batchId: string, quantity: number): Promise<Batch> {
    const batch = await this.getBatchById(batchId);
    if (!batch) {
      throw new Error('Batch not found');
    }

    batch.deallocate(quantity);
    return await this.deps.batchRepository.update(batch);
  }

  async consumeBatch(batchId: string, quantity: number): Promise<Batch> {
    const batch = await this.getBatchById(batchId);
    if (!batch) {
      throw new Error('Batch not found');
    }

    batch.consume(quantity);
    return await this.deps.batchRepository.update(batch);
  }

  async putBatchOnHold(batchId: string, reason: string): Promise<Batch> {
    const batch = await this.getBatchById(batchId);
    if (!batch) {
      throw new Error('Batch not found');
    }

    batch.putOnHold(reason);
    return await this.deps.batchRepository.update(batch);
  }

  async releaseBatchHold(batchId: string): Promise<Batch> {
    const batch = await this.getBatchById(batchId);
    if (!batch) {
      throw new Error('Batch not found');
    }

    batch.releaseHold();
    return await this.deps.batchRepository.update(batch);
  }

  async blockBatch(batchId: string, reason: string): Promise<Batch> {
    const batch = await this.getBatchById(batchId);
    if (!batch) {
      throw new Error('Batch not found');
    }

    batch.block(reason);
    return await this.deps.batchRepository.update(batch);
  }

  // ======================================
  // QUERY METHODS
  // ======================================

  async listBatches(
    filter: BatchFilter = {},
    sort: BatchSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedBatchResult> {
    return await this.deps.batchRepository.list(filter, sort, page, pageSize);
  }

  async getBatchesByProduct(productId: string): Promise<Batch[]> {
    return await this.deps.batchRepository.findByProductId(productId);
  }

  async getBatchesByStatus(status: string): Promise<Batch[]> {
    return await this.deps.batchRepository.findByStatus(status as any);
  }

  async getExpiredBatches(): Promise<Batch[]> {
    return await this.deps.batchRepository.findExpiredBatches();
  }

  async getExpiringSoonBatches(days: number = 30): Promise<Batch[]> {
    return await this.deps.batchRepository.findExpiringSoonBatches(days);
  }

  async getChildBatches(parentBatchId: string): Promise<Batch[]> {
    return await this.deps.batchRepository.findByParentBatchId(parentBatchId);
  }

  // ======================================
  // BUSINESS INTELLIGENCE & ANALYTICS
  // ======================================

  async getBatchStatistics(): Promise<{
    total: number;
    byStatus: Record<string, number>;
    byType: Record<string, number>;
    expiredCount: number;
    expiringSoonCount: number;
    totalQuantity: number;
    allocatedQuantity: number;
    availableQuantity: number;
  }> {
    return await this.deps.batchRepository.getStatistics();
  }
}
