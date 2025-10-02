/**
 * VALEO NeuroERP 3.0 - Inventory Control Service
 *
 * Perpetual inventory management with lot/serial traceability
 */
import { EventBus } from '../infrastructure/event-bus/event-bus';
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
    reservedFor: string;
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
export declare class InventoryControlService {
    private readonly eventBus;
    private readonly metrics;
    constructor(eventBus: EventBus);
    /**
     * Get current inventory levels
     */
    getInventoryLevels(sku?: string, location?: string): Promise<InventoryRecord[]>;
    /**
     * Adjust inventory quantity
     */
    adjustInventory(adjustment: Omit<InventoryAdjustment, 'adjustmentId' | 'createdAt'>): Promise<InventoryAdjustment>;
    /**
     * Create inventory reservation
     */
    createReservation(reservation: Omit<InventoryReservation, 'reservationId' | 'createdAt' | 'status'>): Promise<InventoryReservation>;
    /**
     * Release inventory reservation
     */
    releaseReservation(reservationId: string, releasedQty?: number): Promise<void>;
    /**
     * Get lot traceability information
     */
    getLotTraceability(lotCode: string): Promise<LotTraceability | null>;
    /**
     * Get serial number traceability
     */
    getSerialTraceability(serialNumber: string): Promise<SerialTraceability | null>;
    /**
     * Process inventory movement (transfer between locations)
     */
    processInventoryMovement(sku: string, fromLocation: string, toLocation: string, quantity: number, lot?: string, serial?: string, reason?: string): Promise<void>;
    /**
     * Get inventory valuation
     */
    getInventoryValuation(sku?: string, location?: string): Promise<{
        totalValue: number;
        totalQuantity: number;
        averageCost: number;
        byLocation: Array<{
            location: string;
            value: number;
            quantity: number;
        }>;
        bySku: Array<{
            sku: string;
            value: number;
            quantity: number;
        }>;
    }>;
    /**
     * Get inventory aging report
     */
    getInventoryAging(days?: number): Promise<Array<{
        sku: string;
        location: string;
        lot?: string;
        quantity: number;
        ageInDays: number;
        value: number;
    }>>;
    private queryInventoryRecords;
    private validateInventoryAdjustment;
    private applyInventoryAdjustment;
    private checkInventoryAvailability;
    private persistReservation;
    private updateAllocatedQuantity;
    private getReservation;
    private updateReservation;
    private buildLotTraceability;
    private buildSerialTraceability;
    private validateInventoryMovement;
    private skuExists;
    private locationExists;
    private lotExists;
    private serialExists;
    private publishInventoryAdjustedEvent;
    private publishReservationCreatedEvent;
    private publishReservationReleasedEvent;
}
//# sourceMappingURL=inventory-control-service.d.ts.map