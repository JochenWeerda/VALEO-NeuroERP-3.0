/**
 * Inventory-Batch Integration Service
 * Integrates agribusiness Batch system with existing Inventory Lot system
 */

import { Batch } from '../entities/batch';
import { BatchTraceabilityService } from './batch-traceability-service';
import { BatchRepository } from '../../infra/repositories/batch-repository';

export interface InventoryBatchIntegrationServiceDependencies {
  batchTraceabilityService: BatchTraceabilityService;
}

/**
 * Integration service to link inventory-domain Lot entities with agribusiness-domain Batch entities
 * This allows the existing inventory system to leverage batch traceability for agribusiness products
 */
export class InventoryBatchIntegrationService {
  constructor(private deps: InventoryBatchIntegrationServiceDependencies) {}

  /**
   * Create a Batch from an existing Lot (inventory-domain)
   * This allows migration and integration of existing lots into the batch traceability system
   */
  async createBatchFromLot(
    lotCode: string,
    lotData: {
      sku: string;
      mfgDate?: Date;
      expDate?: Date;
      originCountry?: string;
      initialQty: number;
      uom: string;
      qualityStatus?: string;
    },
    batchType: 'SEED' | 'CROP' | 'FERTILIZER' | 'FEED' | 'PRODUCT',
    createdBy: string
  ): Promise<Batch> {
    // Create batch with lot code as batch number
    const batch = await this.deps.batchTraceabilityService.createBatch(
      {
        batchNumber: lotCode,
        batchType: batchType,
        productId: lotData.sku,
        originCountry: lotData.originCountry,
        harvestDate: lotData.mfgDate,
        expiryDate: lotData.expDate,
        initialQuantity: lotData.initialQty,
        unitOfMeasure: lotData.uom,
        notes: `Created from inventory lot ${lotCode}. Quality status: ${lotData.qualityStatus || 'unknown'}`
      },
      createdBy
    );

    return batch;
  }

  /**
   * Link an existing Batch to an inventory Lot
   * This creates a bidirectional reference between the systems
   */
  async linkBatchToLot(
    batchId: string,
    lotCode: string
  ): Promise<Batch> {
    const batch = await this.deps.batchTraceabilityService.getBatchById(batchId);
    if (!batch) {
      throw new Error('Batch not found');
    }

    // Update batch with lot reference in custom fields
    const customFields = {
      ...batch.customFields,
      inventoryLotCode: lotCode,
      linkedAt: new Date().toISOString()
    };

    await this.deps.batchTraceabilityService.updateBatch(
      batchId,
      { customFields },
      'system'
    );

    return await this.deps.batchTraceabilityService.getBatchById(batchId) as Batch;
  }

  /**
   * Get batch traceability for a given inventory lot code
   */
  async getBatchTraceabilityForLot(lotCode: string): Promise<Batch | null> {
    // Find batch by lot code (stored in batch number or custom fields)
    const batch = await this.deps.batchTraceabilityService.getBatchByNumber(lotCode);
    if (batch) {
      return batch;
    }

    // If not found by batch number, search in custom fields
    // This would require repository extension, for now return null
    return null;
  }

  /**
   * Sync batch quantities with lot quantities
   * Ensures batch and lot quantities stay in sync
   */
  async syncBatchQuantityWithLot(
    batchId: string,
    lotRemainingQty: number,
    lotAllocatedQty: number
  ): Promise<Batch> {
    const batch = await this.deps.batchTraceabilityService.getBatchById(batchId);
    if (!batch) {
      throw new Error('Batch not found');
    }

    // Calculate difference and adjust
    const qtyDifference = lotRemainingQty - batch.remainingQuantity;
    const allocatedDifference = lotAllocatedQty - batch.allocatedQuantity;

    if (qtyDifference !== 0 || allocatedDifference !== 0) {
      // Update batch to match lot quantities
      // Note: This is a simplified sync - in production, you'd want more sophisticated logic
      const updates: any = {
        customFields: {
          ...batch.customFields,
          syncedFromLot: true,
          syncedAt: new Date().toISOString(),
          lotRemainingQty,
          lotAllocatedQty
        }
      };

      await this.deps.batchTraceabilityService.updateBatch(
        batchId,
        updates,
        'system'
      );
    }

    return await this.deps.batchTraceabilityService.getBatchById(batchId) as Batch;
  }
}
