/**
 * VALEO NeuroERP 3.0 - EDI Service
 *
 * ANSI X12 EDI transactions for warehouse management integration
 */
import { EventBus } from '../infrastructure/event-bus/event-bus';
export interface EDITransaction {
    transactionId: string;
    transactionType: '940' | '943' | '944' | '945' | '947';
    direction: 'inbound' | 'outbound';
    status: 'received' | 'processing' | 'processed' | 'error' | 'acknowledged';
    isa: {
        authorizationQualifier: string;
        authorizationInfo: string;
        securityQualifier: string;
        securityInfo: string;
        senderId: string;
        senderQualifier: string;
        receiverId: string;
        receiverQualifier: string;
        date: string;
        time: string;
        controlNumber: string;
        version: string;
    };
    gs: {
        functionalId: string;
        applicationSender: string;
        applicationReceiver: string;
        date: string;
        time: string;
        groupControlNumber: string;
        responsibleAgency: string;
        version: string;
    };
    transactionData: Record<string, any>;
    rawMessage: string;
    processedAt?: Date;
    acknowledgedAt?: Date;
    errorMessage?: string;
    createdAt: Date;
    updatedAt: Date;
}
export interface EDI940WarehouseShippingOrder {
    warehouseCode: string;
    depotCode: string;
    shipmentId: string;
    purposeCode: string;
    shipTo: {
        name: string;
        address: string[];
        city: string;
        state: string;
        zipCode: string;
        country: string;
    };
    carrier: {
        scac: string;
        name: string;
        serviceLevel: string;
    };
    items: Array<{
        lineNumber: string;
        sku: string;
        quantity: number;
        uom: string;
        description: string;
        lot?: string;
        serial?: string;
        shipDate?: string;
        cancelDate?: string;
    }>;
    routing: string;
    specialServices?: string[];
    notes?: string[];
}
export interface EDI943WarehouseStockTransferShipmentAdvice {
    warehouseCode: string;
    transferId: string;
    shipmentDate: string;
    carrier: {
        scac: string;
        name: string;
        proNumber: string;
    };
    shipFrom: {
        name: string;
        address: string[];
        city: string;
        state: string;
        zipCode: string;
    };
    shipTo: {
        name: string;
        address: string[];
        city: string;
        state: string;
        zipCode: string;
    };
    items: Array<{
        sku: string;
        quantity: number;
        uom: string;
        lot?: string;
        serial?: string;
        description: string;
    }>;
    totalWeight?: number;
    totalVolume?: number;
}
export interface EDI944WarehouseStockTransferReceiptAdvice {
    warehouseCode: string;
    transferId: string;
    receiptDate: string;
    carrier: {
        scac: string;
        name: string;
        proNumber: string;
    };
    shipFrom: {
        name: string;
        address: string[];
        city: string;
        state: string;
        zipCode: string;
    };
    items: Array<{
        sku: string;
        quantityOrdered: number;
        quantityReceived: number;
        quantityDamaged?: number;
        uom: string;
        lot?: string;
        serial?: string;
        condition: 'good' | 'damaged' | 'expired';
        notes?: string;
    }>;
    discrepancies: Array<{
        sku: string;
        expectedQuantity: number;
        receivedQuantity: number;
        reason: string;
    }>;
}
export interface EDI945WarehouseShippingAdvice {
    warehouseCode: string;
    shipmentId: string;
    shipmentDate: string;
    carrier: {
        scac: string;
        name: string;
        proNumber: string;
        bolNumber?: string;
    };
    shipFrom: {
        name: string;
        address: string[];
        city: string;
        state: string;
        zipCode: string;
    };
    shipTo: {
        name: string;
        address: string[];
        city: string;
        state: string;
        zipCode: string;
    };
    items: Array<{
        sku: string;
        quantity: number;
        uom: string;
        lot?: string;
        serial?: string;
        description: string;
        weight?: number;
        volume?: number;
    }>;
    packaging: Array<{
        type: string;
        quantity: number;
        weight: number;
        dimensions: {
            length: number;
            width: number;
            height: number;
        };
    }>;
    totalWeight: number;
    totalVolume: number;
    specialHandling?: string[];
}
export interface EDI947WarehouseInventoryAdjustmentAdvice {
    warehouseCode: string;
    adjustmentId: string;
    adjustmentDate: string;
    adjustmentType: 'increase' | 'decrease' | 'reset';
    reason: string;
    items: Array<{
        sku: string;
        previousQuantity: number;
        adjustedQuantity: number;
        adjustmentAmount: number;
        uom: string;
        lot?: string;
        serial?: string;
        reason: string;
        authorizedBy: string;
    }>;
    totals: {
        totalItems: number;
        totalValueChange: number;
        netAdjustment: number;
    };
}
export declare class EDIService {
    private readonly eventBus;
    private readonly metrics;
    private transactions;
    private readonly segmentSeparator;
    private readonly elementSeparator;
    private readonly subelementSeparator;
    constructor(eventBus: EventBus);
    /**
     * Process inbound EDI 940 (Warehouse Shipping Order)
     */
    processEDI940(rawMessage: string): Promise<EDI940WarehouseShippingOrder>;
    /**
     * Generate outbound EDI 943 (Warehouse Stock Transfer Shipment Advice)
     */
    generateEDI943(transferData: {
        warehouseCode: string;
        transferId: string;
        shipmentDate: string;
        carrier: any;
        shipFrom: any;
        shipTo: any;
        items: any[];
    }): Promise<string>;
    /**
     * Process inbound EDI 944 (Warehouse Stock Transfer Receipt Advice)
     */
    processEDI944(rawMessage: string): Promise<EDI944WarehouseStockTransferReceiptAdvice>;
    /**
     * Generate outbound EDI 945 (Warehouse Shipping Advice)
     */
    generateEDI945(shippingData: {
        warehouseCode: string;
        shipmentId: string;
        shipmentDate: string;
        carrier: any;
        shipFrom: any;
        shipTo: any;
        items: any[];
        packaging: any[];
        totalWeight: number;
        totalVolume: number;
    }): Promise<string>;
    /**
     * Generate outbound EDI 947 (Warehouse Inventory Adjustment Advice)
     */
    generateEDI947(adjustmentData: {
        warehouseCode: string;
        adjustmentId: string;
        adjustmentDate: string;
        adjustmentType: string;
        reason: string;
        items: any[];
        totals: any;
    }): Promise<string>;
    /**
     * Parse EDI transaction envelope
     */
    private parseEDITransaction;
    /**
     * Create EDI transaction record
     */
    private createEDITransaction;
    /**
     * Parse transaction-specific data
     */
    private parseTransactionData;
    /**
     * Parse EDI 940 data
     */
    private parseEDI940Data;
    /**
     * Parse EDI 944 data
     */
    private parseEDI944Data;
    /**
     * Generate EDI 943 message
     */
    private generateEDI943Message;
    /**
     * Generate EDI 945 message
     */
    private generateEDI945Message;
    /**
     * Generate EDI 947 message
     */
    private generateEDI947Message;
    private processWarehouseShippingOrder;
    private processTransferReceiptAdvice;
    private publishEDI940ReceivedEvent;
    private publishEDI943GeneratedEvent;
    private publishEDI944ReceivedEvent;
    private publishEDI945GeneratedEvent;
    private publishEDI947GeneratedEvent;
}
//# sourceMappingURL=edi-service.d.ts.map