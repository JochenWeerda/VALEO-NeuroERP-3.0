/**
 * VALEO NeuroERP 3.0 - Inventory Control Service
 *
 * Perpetual inventory management with lot/serial traceability
 */

import { injectable } from 'inversify';
import { EventBus } from '../infrastructure/event-bus/event-bus';
import { InventoryMetricsService } from '../infrastructure/observability/metrics-service';
import {
  InventoryAdjustedEvent,
  LotConsumedEvent,
  LotCreatedEvent,
  ReservationCreatedEvent,
  ReservationReleasedEvent
} from '../core/domain-events/inventory-domain-events';
import { Sku } from '../core/entities/sku';
import { Lot } from '../core/entities/lot';

export interface InventoryRecord {
  sku: string;
  location: string;
  lot?: string;
  serial?: string;
  quantity: number;
  allocatedQty: number;
  availableQty: number;
  unitCost?: number;
  totalValue?: number;
  lastCount?: Date;
  lastMovement: Date;
}

export interface InventoryAdjustment {
  adjustmentId: string;
  sku: string;
  location: string;
  lot?: string;
  serial?: string;
  adjustmentQty: number;
  reason: 'cycle_count' | 'damage' | 'theft' | 'correction' | 'return' | 'transfer';
  reference?: string;
  approvedBy: string;
  notes?: string;
  createdAt: Date;
}

export interface InventoryReservation {
  reservationId: string;
  sku: string;
  location: string;
  lot?: string;
  serial?: string;
  quantity: number;
  reservedFor: string; // Order/Shipment ID
  reservationType: 'sales_order' | 'transfer' | 'production' | 'allocation';
  priority: number;
  expiresAt?: Date;
  createdAt: Date;
  status: 'active' | 'fulfilled' | 'expired' | 'cancelled';
}

export interface LotTraceability {
  lotCode: string;
  sku: string;
  supplier: string;
  supplierLot?: string;
  mfgDate?: Date;
  expDate?: Date;
  receivedDate: Date;
  currentQty: number;
  totalReceived: number;
  totalConsumed: number;
  locations: Array<{
    location: string;
    quantity: number;
    lastMovement: Date;
  }>;
  transactions: Array<{
    transactionId: string;
    type: 'receipt' | 'consumption' | 'adjustment' | 'transfer';
    quantity: number;
    location: string;
    reference: string;
    timestamp: Date;
  }>;
}

export interface SerialTraceability {
  serialNumber: string;
  sku: string;
  lot?: string;
  currentLocation?: string;
  status: 'available' | 'reserved' | 'shipped' | 'returned' | 'scrapped';
  transactions: Array<{
    transactionId: string;
    type: string;
    fromLocation?: string;
    toLocation?: string;
    reference: string;
    timestamp: Date;
  }>;
  customFields?: Record<string, any>;
}

@injectable()
export class InventoryControlService {
  private readonly metrics = new InventoryMetricsService();

  constructor(
    private readonly eventBus: EventBus
  ) {}

  /**
   * Get current inventory levels
   */
  async getInventoryLevels(sku?: string, location?: string): Promise<InventoryRecord[]> {
    const startTime = Date.now();

    try {
      // In real implementation, query database
      const records = await this.queryInventoryRecords(sku, location);

      this.metrics.recordDatabaseQueryDuration('inventory.levels', (Date.now() - startTime) / 1000, { sku: sku || '', location: location || '' });

      return records;
    } catch (error) {
      this.metrics.incrementErrorCount('inventory.query_failed', { error: 'query_error' });
      throw error;
    }
  }

  /**
   * Adjust inventory quantity
   */
  async adjustInventory(adjustment: Omit<InventoryAdjustment, 'adjustmentId' | 'createdAt'>): Promise<InventoryAdjustment> {
    const startTime = Date.now();

    try {
      // Validate adjustment
      await this.validateInventoryAdjustment(adjustment);

      const fullAdjustment: InventoryAdjustment = {
        ...adjustment,
        adjustmentId: `adj_${Date.now()}`,
        createdAt: new Date()
      };

      // Apply adjustment to inventory
      await this.applyInventoryAdjustment(fullAdjustment);

      // Publish event
      await this.publishInventoryAdjustedEvent(fullAdjustment);

      this.metrics.recordDatabaseQueryDuration('inventory.adjustment', (Date.now() - startTime) / 1000, { sku: adjustment.sku, reason: adjustment.reason });

      return fullAdjustment;
    } catch (error) {
      this.metrics.incrementErrorCount('inventory.adjustment_failed', { error: 'adjustment_error' });
      throw error;
    }
  }

  /**
   * Create inventory reservation
   */
  async createReservation(reservation: Omit<InventoryReservation, 'reservationId' | 'createdAt' | 'status'>): Promise<InventoryReservation> {
    const startTime = Date.now();

    try {
      // Check availability
      const available = await this.checkInventoryAvailability(
        reservation.sku,
        reservation.location,
        reservation.quantity,
        reservation.lot,
        reservation.serial
      );

      if (!available) {
        throw new Error('Insufficient inventory for reservation');
      }

      const fullReservation: InventoryReservation = {
        ...reservation,
        reservationId: `res_${Date.now()}`,
        createdAt: new Date(),
        status: 'active'
      };

      // Create reservation
      await this.persistReservation(fullReservation);

      // Update allocated quantity
      await this.updateAllocatedQuantity(
        reservation.sku,
        reservation.location,
        reservation.lot,
        reservation.serial,
        reservation.quantity
      );

      // Publish event
      await this.publishReservationCreatedEvent(fullReservation);

      this.metrics.recordDatabaseQueryDuration('inventory.reservation', (Date.now() - startTime) / 1000, { sku: reservation.sku, location: reservation.location });

      return fullReservation;
    } catch (error) {
      this.metrics.incrementErrorCount('inventory.reservation_failed', { error: 'reservation_error' });
      throw error;
    }
  }

  /**
   * Release inventory reservation
   */
  async releaseReservation(reservationId: string, releasedQty?: number): Promise<void> {
    const startTime = Date.now();

    try {
      const reservation = await this.getReservation(reservationId);
      if (!reservation) {
        throw new Error(`Reservation ${reservationId} not found`);
      }

      const quantityToRelease = releasedQty || reservation.quantity;

      // Update reservation status
      if (quantityToRelease >= reservation.quantity) {
        reservation.status = 'fulfilled';
      }

      // Release allocated quantity
      await this.updateAllocatedQuantity(
        reservation.sku,
        reservation.location,
        reservation.lot,
        reservation.serial,
        -quantityToRelease
      );

      // Persist changes
      await this.updateReservation(reservation);

      // Publish event
      await this.publishReservationReleasedEvent(reservation, quantityToRelease);

      this.metrics.recordDatabaseQueryDuration('inventory.release', (Date.now() - startTime) / 1000, { sku: reservation.sku, location: reservation.location });
    } catch (error) {
      this.metrics.incrementErrorCount('inventory.release_failed', { error: 'release_error' });
      throw error;
    }
  }

  /**
   * Get lot traceability information
   */
  async getLotTraceability(lotCode: string): Promise<LotTraceability | null> {
    const startTime = Date.now();

    try {
      const traceability = await this.buildLotTraceability(lotCode);

      this.metrics.recordDatabaseQueryDuration('inventory.lot_traceability', (Date.now() - startTime) / 1000, { lotCode });

      return traceability;
    } catch (error) {
      this.metrics.incrementErrorCount('inventory.traceability_failed', { error: 'traceability_error' });
      throw error;
    }
  }

  /**
   * Get serial number traceability
   */
  async getSerialTraceability(serialNumber: string): Promise<SerialTraceability | null> {
    const startTime = Date.now();

    try {
      const traceability = await this.buildSerialTraceability(serialNumber);

      this.metrics.recordDatabaseQueryDuration('inventory.serial_traceability', (Date.now() - startTime) / 1000, { serialNumber });

      return traceability;
    } catch (error) {
      this.metrics.incrementErrorCount('inventory.traceability_failed', { error: 'traceability_error' });
      throw error;
    }
  }

  /**
   * Process inventory movement (transfer between locations)
   */
  async processInventoryMovement(
    sku: string,
    fromLocation: string,
    toLocation: string,
    quantity: number,
    lot?: string,
    serial?: string,
    reason = 'transfer'
  ): Promise<void> {
    const startTime = Date.now();

    try {
      // Validate movement
      await this.validateInventoryMovement(sku, fromLocation, toLocation, quantity, lot, serial);

      // Create adjustment for source location (negative)
      await this.adjustInventory({
        sku,
        location: fromLocation,
        lot,
        serial,
        adjustmentQty: -quantity,
        reason: reason as any,
        approvedBy: 'system',
        notes: `Transfer to ${toLocation}`
      });

      // Create adjustment for destination location (positive)
      await this.adjustInventory({
        sku,
        location: toLocation,
        lot,
        serial,
        adjustmentQty: quantity,
        reason: reason as any,
        approvedBy: 'system',
        notes: `Transfer from ${fromLocation}`
      });

      this.metrics.recordDatabaseQueryDuration('inventory.movement', (Date.now() - startTime) / 1000, { sku, fromLocation, toLocation });
    } catch (error) {
      this.metrics.incrementErrorCount('inventory.movement_failed', { error: 'movement_error' });
      throw error;
    }
  }

  /**
   * Get inventory valuation
   */
  async getInventoryValuation(sku?: string, location?: string): Promise<{
    totalValue: number;
    totalQuantity: number;
    averageCost: number;
    byLocation: Array<{ location: string; value: number; quantity: number }>;
    bySku: Array<{ sku: string; value: number; quantity: number }>;
  }> {
    const startTime = Date.now();

    try {
      const records = await this.getInventoryLevels(sku, location);

      const valuation = {
        totalValue: 0,
        totalQuantity: 0,
        averageCost: 0,
        byLocation: new Map<string, { value: number; quantity: number }>(),
        bySku: new Map<string, { value: number; quantity: number }>()
      };

      for (const record of records) {
        const value = (record.unitCost || 0) * record.quantity;
        valuation.totalValue += value;
        valuation.totalQuantity += record.quantity;

        // By location
        const locStats = valuation.byLocation.get(record.location) || { value: 0, quantity: 0 };
        locStats.value += value;
        locStats.quantity += record.quantity;
        valuation.byLocation.set(record.location, locStats);

        // By SKU
        const skuStats = valuation.bySku.get(record.sku) || { value: 0, quantity: 0 };
        skuStats.value += value;
        skuStats.quantity += record.quantity;
        valuation.bySku.set(record.sku, skuStats);
      }

      valuation.averageCost = valuation.totalQuantity > 0 ? valuation.totalValue / valuation.totalQuantity : 0;

      this.metrics.recordDatabaseQueryDuration('inventory.valuation', (Date.now() - startTime) / 1000, { sku: sku || 'all', location: location || 'all' });

      return {
        ...valuation,
        byLocation: Array.from(valuation.byLocation.entries()).map(([location, stats]) => ({ location, ...stats })),
        bySku: Array.from(valuation.bySku.entries()).map(([sku, stats]) => ({ sku, ...stats }))
      };
    } catch (error) {
      this.metrics.incrementErrorCount('inventory.valuation_failed', { error: 'valuation_error' });
      throw error;
    }
  }

  /**
   * Get inventory aging report
   */
  async getInventoryAging(days = 90): Promise<Array<{
    sku: string;
    location: string;
    lot?: string;
    quantity: number;
    ageInDays: number;
    value: number;
  }>> {
    const startTime = Date.now();

    try {
      const records = await this.getInventoryLevels();
      const aging: Array<{
        sku: string;
        location: string;
        lot?: string;
        quantity: number;
        ageInDays: number;
        value: number;
      }> = [];

      for (const record of records) {
        const ageInDays = Math.floor((Date.now() - record.lastMovement.getTime()) / (1000 * 60 * 60 * 24));

        if (ageInDays >= days) {
          aging.push({
            sku: record.sku,
            location: record.location,
            lot: record.lot,
            quantity: record.quantity,
            ageInDays,
            value: (record.unitCost || 0) * record.quantity
          });
        }
      }

      // Sort by age (oldest first)
      aging.sort((a, b) => b.ageInDays - a.ageInDays);

      this.metrics.recordDatabaseQueryDuration('inventory.aging', (Date.now() - startTime) / 1000, {});

      return aging;
    } catch (error) {
      this.metrics.incrementErrorCount('inventory.aging_failed', { error: 'aging_error' });
      throw error;
    }
  }

  // Private helper methods

  private async queryInventoryRecords(sku?: string, location?: string): Promise<InventoryRecord[]> {
    // Mock implementation - would query database
    return [
      {
        sku: sku || 'WIDGET-001',
        location: location || 'A-01-01-01',
        lot: 'LOT-001',
        quantity: 100,
        allocatedQty: 10,
        availableQty: 90,
        unitCost: 10.50,
        totalValue: 1050.00,
        lastMovement: new Date()
      }
    ];
  }

  private async validateInventoryAdjustment(adjustment: Omit<InventoryAdjustment, 'adjustmentId' | 'createdAt'>): Promise<void> {
    // Validate SKU exists
    const skuExists = await this.skuExists(adjustment.sku);
    if (!skuExists) {
      throw new Error(`SKU ${adjustment.sku} does not exist`);
    }

    // Validate location exists
    const locationExists = await this.locationExists(adjustment.location);
    if (!locationExists) {
      throw new Error(`Location ${adjustment.location} does not exist`);
    }

    // Validate lot/serial if provided
    if (adjustment.lot) {
      const lotExists = await this.lotExists(adjustment.lot, adjustment.sku);
      if (!lotExists) {
        throw new Error(`Lot ${adjustment.lot} does not exist for SKU ${adjustment.sku}`);
      }
    }

    if (adjustment.serial) {
      const serialExists = await this.serialExists(adjustment.serial, adjustment.sku);
      if (!serialExists) {
        throw new Error(`Serial ${adjustment.serial} does not exist for SKU ${adjustment.sku}`);
      }
    }
  }

  private async applyInventoryAdjustment(adjustment: InventoryAdjustment): Promise<void> {
    // Mock implementation - would update database
    // eslint-disable-next-line no-console
    console.log('Applying inventory adjustment:', adjustment.adjustmentId);
  }

  private async checkInventoryAvailability(
    sku: string,
    location: string,
    quantity: number,
    lot?: string,
    serial?: string
  ): Promise<boolean> {
    const records = await this.getInventoryLevels(sku, location);
    const relevantRecords = records.filter(record => {
      if (lot && record.lot !== lot) return false;
      if (serial && record.serial !== serial) return false;
      return true;
    });

    const totalAvailable = relevantRecords.reduce((sum, record) => sum + record.availableQty, 0);
    return totalAvailable >= quantity;
  }

  private async persistReservation(reservation: InventoryReservation): Promise<void> {
    // Mock implementation
    // eslint-disable-next-line no-console
    console.log('Persisting reservation:', reservation.reservationId);
  }

  private async updateAllocatedQuantity(
    sku: string,
    location: string,
    lot: string | undefined,
    serial: string | undefined,
    quantity: number
  ): Promise<void> {
    // Mock implementation
    // eslint-disable-next-line no-console
    console.log('Updating allocated quantity for', sku, location, quantity);
  }

  private async getReservation(reservationId: string): Promise<InventoryReservation | null> {
    // Mock implementation
    return {
      reservationId,
      sku: 'WIDGET-001',
      location: 'A-01-01-01',
      quantity: 10,
      reservedFor: 'ORDER-123',
      reservationType: 'sales_order',
      priority: 1,
      createdAt: new Date(),
      status: 'active'
    };
  }

  private async updateReservation(reservation: InventoryReservation): Promise<void> {
    // Mock implementation
    // eslint-disable-next-line no-console
    console.log('Updating reservation:', reservation.reservationId);
  }

  private async buildLotTraceability(lotCode: string): Promise<LotTraceability | null> {
    // Mock implementation
    return {
      lotCode,
      sku: 'WIDGET-001',
      supplier: 'SUPPLIER-001',
      supplierLot: 'SUP-LOT-001',
      mfgDate: new Date('2024-01-01'),
      expDate: new Date('2025-01-01'),
      receivedDate: new Date('2024-01-15'),
      currentQty: 85,
      totalReceived: 100,
      totalConsumed: 15,
      locations: [
        { location: 'A-01-01-01', quantity: 85, lastMovement: new Date() }
      ],
      transactions: [
        {
          transactionId: 'txn_001',
          type: 'receipt',
          quantity: 100,
          location: 'RECEIVING',
          reference: 'ASN-001',
          timestamp: new Date('2024-01-15')
        }
      ]
    };
  }

  private async buildSerialTraceability(serialNumber: string): Promise<SerialTraceability | null> {
    // Mock implementation
    return {
      serialNumber,
      sku: 'WIDGET-001',
      lot: 'LOT-001',
      currentLocation: 'A-01-01-01',
      status: 'available',
      transactions: [
        {
          transactionId: 'txn_001',
          type: 'receipt',
          reference: 'ASN-001',
          timestamp: new Date('2024-01-15')
        }
      ]
    };
  }

  private async validateInventoryMovement(
    sku: string,
    fromLocation: string,
    toLocation: string,
    quantity: number,
    lot?: string,
    serial?: string
  ): Promise<void> {
    // Check source availability
    const available = await this.checkInventoryAvailability(sku, fromLocation, quantity, lot, serial);
    if (!available) {
      throw new Error('Insufficient inventory in source location');
    }

    // Check destination exists
    const destExists = await this.locationExists(toLocation);
    if (!destExists) {
      throw new Error(`Destination location ${toLocation} does not exist`);
    }
  }

  // Mock validation methods
  private async skuExists(sku: string): Promise<boolean> {
    return true; // Mock
  }

  private async locationExists(location: string): Promise<boolean> {
    return true; // Mock
  }

  private async lotExists(lot: string, sku: string): Promise<boolean> {
    return true; // Mock
  }

  private async serialExists(serial: string, sku: string): Promise<boolean> {
    return true; // Mock
  }

  // Event publishing methods
  private async publishInventoryAdjustedEvent(adjustment: InventoryAdjustment): Promise<void> {
    const event: InventoryAdjustedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.adjusted',
      type: 'inventory.adjusted',
      occurredAt: new Date(),
      aggregateVersion: 1,
      aggregateId: adjustment.adjustmentId,
      aggregateType: 'InventoryAdjustment',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      sku: adjustment.sku,
      location: adjustment.location,
      lot: adjustment.lot,
      serial: adjustment.serial,
      adjustmentQty: adjustment.adjustmentQty,
      reason: adjustment.reason,
      approvedBy: adjustment.approvedBy
    };

    await this.eventBus.publish(event);
  }

  private async publishReservationCreatedEvent(reservation: InventoryReservation): Promise<void> {
    const event: ReservationCreatedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.reservation.created',
      type: 'inventory.reservation.created',
      occurredAt: new Date(),
      aggregateVersion: 1,
      aggregateId: reservation.reservationId,
      aggregateType: 'InventoryReservation',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      sku: reservation.sku,
      location: reservation.location,
      lot: reservation.lot,
      serial: reservation.serial,
      quantity: reservation.quantity,
      reservedFor: reservation.reservedFor,
      reservationType: reservation.reservationType
    };

    await this.eventBus.publish(event);
  }

  private async publishReservationReleasedEvent(reservation: InventoryReservation, releasedQty: number): Promise<void> {
    const event: ReservationReleasedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.reservation.released',
      type: 'inventory.reservation.released',
      occurredAt: new Date(),
      aggregateVersion: 1,
      aggregateId: reservation.reservationId,
      aggregateType: 'InventoryReservation',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      reservationId: reservation.reservationId,
      releasedQty,
      reason: 'fulfilled'
    };

    await this.eventBus.publish(event);
  }
}