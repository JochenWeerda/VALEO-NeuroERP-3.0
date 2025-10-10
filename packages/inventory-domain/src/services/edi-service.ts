/**
 * VALEO NeuroERP 3.0 - EDI Service
 *
 * ANSI X12 EDI transactions for warehouse management integration
 */

import { injectable } from 'inversify';
import { EventBus } from '../infrastructure/event-bus/event-bus';
import { InventoryMetricsService } from '../infrastructure/observability/metrics-service';
import {
  EDI940ReceivedEvent,
  EDI943GeneratedEvent,
  EDI944ReceivedEvent,
  EDI945GeneratedEvent,
  EDI947GeneratedEvent
} from '../core/domain-events/inventory-domain-events';

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
  purposeCode: string; // '00' = New Order, '01' = Cancellation, etc.

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

@injectable()
export class EDIService {
  private readonly metrics = new InventoryMetricsService();
  private readonly transactions: Map<string, EDITransaction> = new Map();
  private readonly segmentSeparator = '~';
  private readonly elementSeparator = '*';
  private readonly subelementSeparator = '>';

  constructor(
    private readonly eventBus: EventBus
  ) {}

  /**
   * Process inbound EDI 940 (Warehouse Shipping Order)
   */
  async processEDI940(rawMessage: string): Promise<EDI940WarehouseShippingOrder> {
    const startTime = Date.now();

    try {
      const transaction = await this.parseEDITransaction(rawMessage, '940', 'inbound');
      const order = this.parseEDI940Data(transaction.transactionData);

      // Process the shipping order
      await this.processWarehouseShippingOrder(order);

      transaction.status = 'processed';
      transaction.processedAt = new Date();

      // Publish event
      await this.publishEDI940ReceivedEvent(order);

      this.metrics.recordDatabaseQueryDuration('edi', '940_processing', (Date.now() - startTime) / 1000);
      this.metrics.incrementEDITransactions('940', 'processed');

      return order;
    } catch (error) {
      this.metrics.incrementErrorCount('edi', '940_processing_failed');
      throw error;
    }
  }

  /**
   * Generate outbound EDI 943 (Warehouse Stock Transfer Shipment Advice)
   */
  async generateEDI943(transferData: {
    warehouseCode: string;
    transferId: string;
    shipmentDate: string;
    carrier: any;
    shipFrom: any;
    shipTo: any;
    items: any[];
  }): Promise<string> {
    const startTime = Date.now();

    try {
      const edi943: EDI943WarehouseStockTransferShipmentAdvice = {
        warehouseCode: transferData.warehouseCode,
        transferId: transferData.transferId,
        shipmentDate: transferData.shipmentDate,
        carrier: transferData.carrier,
        shipFrom: transferData.shipFrom,
        shipTo: transferData.shipTo,
        items: transferData.items
      };

      const rawMessage = this.generateEDI943Message(edi943);
      const transaction = await this.createEDITransaction(rawMessage, '943', 'outbound');

      // Publish event
      await this.publishEDI943GeneratedEvent(edi943);

      this.metrics.recordDatabaseQueryDuration('edi', '943_generation', (Date.now() - startTime) / 1000);

      return rawMessage;
    } catch (error) {
      this.metrics.incrementErrorCount('edi', '943_generation_failed');
      throw error;
    }
  }

  /**
   * Process inbound EDI 944 (Warehouse Stock Transfer Receipt Advice)
   */
  async processEDI944(rawMessage: string): Promise<EDI944WarehouseStockTransferReceiptAdvice> {
    const startTime = Date.now();

    try {
      const transaction = await this.parseEDITransaction(rawMessage, '944', 'inbound');
      const receipt = this.parseEDI944Data(transaction.transactionData);

      // Process the receipt advice
      await this.processTransferReceiptAdvice(receipt);

      transaction.status = 'processed';
      transaction.processedAt = new Date();

      // Publish event
      await this.publishEDI944ReceivedEvent(receipt);

      this.metrics.recordDatabaseQueryDuration('edi', '944_processing', (Date.now() - startTime) / 1000);
      this.metrics.incrementEDITransactions('944', 'processed');

      return receipt;
    } catch (error) {
      this.metrics.incrementErrorCount('edi', '944_processing_failed');
      throw error;
    }
  }

  /**
   * Generate outbound EDI 945 (Warehouse Shipping Advice)
   */
  async generateEDI945(shippingData: {
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
  }): Promise<string> {
    const startTime = Date.now();

    try {
      const edi945: EDI945WarehouseShippingAdvice = {
        warehouseCode: shippingData.warehouseCode,
        shipmentId: shippingData.shipmentId,
        shipmentDate: shippingData.shipmentDate,
        carrier: shippingData.carrier,
        shipFrom: shippingData.shipFrom,
        shipTo: shippingData.shipTo,
        items: shippingData.items,
        packaging: shippingData.packaging,
        totalWeight: shippingData.totalWeight,
        totalVolume: shippingData.totalVolume
      };

      const rawMessage = this.generateEDI945Message(edi945);
      const transaction = await this.createEDITransaction(rawMessage, '945', 'outbound');

      // Publish event
      await this.publishEDI945GeneratedEvent(edi945);

      this.metrics.recordDatabaseQueryDuration('edi', '945_generation', (Date.now() - startTime) / 1000);

      return rawMessage;
    } catch (error) {
      this.metrics.incrementErrorCount('edi', '945_generation_failed');
      throw error;
    }
  }

  /**
   * Generate outbound EDI 947 (Warehouse Inventory Adjustment Advice)
   */
  async generateEDI947(adjustmentData: {
    warehouseCode: string;
    adjustmentId: string;
    adjustmentDate: string;
    adjustmentType: string;
    reason: string;
    items: any[];
    totals: any;
  }): Promise<string> {
    const startTime = Date.now();

    try {
      const edi947: EDI947WarehouseInventoryAdjustmentAdvice = {
        warehouseCode: adjustmentData.warehouseCode,
        adjustmentId: adjustmentData.adjustmentId,
        adjustmentDate: adjustmentData.adjustmentDate,
        adjustmentType: adjustmentData.adjustmentType as any,
        reason: adjustmentData.reason,
        items: adjustmentData.items,
        totals: adjustmentData.totals
      };

      const rawMessage = this.generateEDI947Message(edi947);
      const transaction = await this.createEDITransaction(rawMessage, '947', 'outbound');

      // Publish event
      await this.publishEDI947GeneratedEvent(edi947);

      this.metrics.recordDatabaseQueryDuration('edi', '947_generation', (Date.now() - startTime) / 1000);

      return rawMessage;
    } catch (error) {
      this.metrics.incrementErrorCount('edi', '947_generation_failed');
      throw error;
    }
  }

  /**
   * Parse EDI transaction envelope
   */
  private async parseEDITransaction(rawMessage: string, expectedType: string, direction: 'inbound' | 'outbound'): Promise<EDITransaction> {
    // Parse ISA segment
    const isaMatch = rawMessage.match(/ISA\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)~/);
    if (!isaMatch) {
      throw new Error('Invalid EDI message: Missing or malformed ISA segment');
    }

    const isa = {
      authorizationQualifier: isaMatch[1],
      authorizationInfo: isaMatch[2],
      securityQualifier: isaMatch[3],
      securityInfo: isaMatch[4],
      senderId: isaMatch[5],
      senderQualifier: isaMatch[6],
      receiverId: isaMatch[7],
      receiverQualifier: isaMatch[8],
      date: isaMatch[9],
      time: isaMatch[10],
      controlNumber: isaMatch[13],
      version: isaMatch[15]
    };

    // Parse GS segment
    const gsMatch = rawMessage.match(/GS\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)~/);
    if (!gsMatch) {
      throw new Error('Invalid EDI message: Missing or malformed GS segment');
    }

    const gs = {
      functionalId: gsMatch[1],
      applicationSender: gsMatch[2],
      applicationReceiver: gsMatch[3],
      date: gsMatch[4],
      time: gsMatch[5],
      groupControlNumber: gsMatch[6],
      responsibleAgency: gsMatch[7],
      version: gsMatch[8]
    };

    // Validate transaction type
    if (gs.functionalId !== expectedType) {
      throw new Error(`Invalid transaction type: Expected ${expectedType}, got ${gs.functionalId}`);
    }

    const transaction: EDITransaction = {
      transactionId: `edi_${expectedType}_${Date.now()}`,
      transactionType: expectedType as any,
      direction,
      status: 'received',
      isa,
      gs,
      transactionData: this.parseTransactionData(rawMessage),
      rawMessage,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.transactions.set(transaction.transactionId, transaction);
    return transaction;
  }

  /**
   * Create EDI transaction record
   */
  private async createEDITransaction(rawMessage: string, type: string, direction: 'inbound' | 'outbound'): Promise<EDITransaction> {
    const transaction: EDITransaction = {
      transactionId: `edi_${type}_${Date.now()}`,
      transactionType: type as any,
      direction,
      status: 'processing',
      isa: {} as any, // Would be populated from configuration
      gs: {} as any,
      transactionData: {},
      rawMessage,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.transactions.set(transaction.transactionId, transaction);
    return transaction;
  }

  /**
   * Parse transaction-specific data
   */
  private parseTransactionData(rawMessage: string): Record<string, any> {
    // Parse ST, BEG, N1, PO1, etc. segments based on transaction type
    const data: Record<string, any> = {};

    // Extract ST segment (Transaction Set Header)
    const stMatch = rawMessage.match(/ST\*([^*]+)\*([^*]+)~/);
    if (stMatch) {
      data.transactionSet = {
        id: stMatch[1],
        controlNumber: stMatch[2]
      };
    }

    return data;
  }

  /**
   * Parse EDI 940 data
   */
  private parseEDI940Data(data: Record<string, any>): EDI940WarehouseShippingOrder {
    // Parse W05 (Warehouse Order Header), N1 (Name), G62 (Date/Time), etc.
    return {
      warehouseCode: 'WH001',
      depotCode: 'DEP001',
      shipmentId: 'SHIP001',
      purposeCode: '00',
      shipTo: {
        name: 'Customer Name',
        address: ['Address Line 1', 'Address Line 2'],
        city: 'City',
        state: 'State',
        zipCode: '12345',
        country: 'US'
      },
      carrier: {
        scac: 'SCAC',
        name: 'Carrier Name',
        serviceLevel: 'GND'
      },
      items: [
        {
          lineNumber: '1',
          sku: 'SKU001',
          quantity: 100,
          uom: 'EA',
          description: 'Item Description'
        }
      ],
      routing: 'ROUTING'
    };
  }

  /**
   * Parse EDI 944 data
   */
  private parseEDI944Data(data: Record<string, any>): EDI944WarehouseStockTransferReceiptAdvice {
    return {
      warehouseCode: 'WH001',
      transferId: 'TRANS001',
      receiptDate: new Date().toISOString().split('T')[0],
      carrier: {
        scac: 'SCAC',
        name: 'Carrier Name',
        proNumber: 'PRO001'
      },
      shipFrom: {
        name: 'Ship From Name',
        address: ['Address Line 1'],
        city: 'City',
        state: 'State',
        zipCode: '12345'
      },
      items: [
        {
          sku: 'SKU001',
          quantityOrdered: 100,
          quantityReceived: 95,
          uom: 'EA',
          condition: 'good'
        }
      ],
      discrepancies: [
        {
          sku: 'SKU001',
          expectedQuantity: 100,
          receivedQuantity: 95,
          reason: 'Shortage'
        }
      ]
    };
  }

  /**
   * Generate EDI 943 message
   */
  private generateEDI943Message(data: EDI943WarehouseStockTransferShipmentAdvice): string {
    const segments: string[] = [];

    // ISA/GS headers would be added here
    segments.push(`ST*943*0001${this.segmentSeparator}`);
    segments.push(`W19*${data.warehouseCode}*${data.transferId}*${data.shipmentDate}${this.segmentSeparator}`);
    // Add N1, G62, TD3, etc. segments
    segments.push(`SE*3*0001${this.segmentSeparator}`);
    // GE/IEA trailers would be added here

    return segments.join('');
  }

  /**
   * Generate EDI 945 message
   */
  private generateEDI945Message(data: EDI945WarehouseShippingAdvice): string {
    const segments: string[] = [];

    segments.push(`ST*945*0001${this.segmentSeparator}`);
    segments.push(`W06*${data.warehouseCode}*${data.shipmentId}*${data.shipmentDate}${this.segmentSeparator}`);
    // Add N1, G62, TD3, etc. segments
    segments.push(`SE*5*0001${this.segmentSeparator}`);

    return segments.join('');
  }

  /**
   * Generate EDI 947 message
   */
  private generateEDI947Message(data: EDI947WarehouseInventoryAdjustmentAdvice): string {
    const segments: string[] = [];

    segments.push(`ST*947*0001${this.segmentSeparator}`);
    segments.push(`W20*${data.warehouseCode}*${data.adjustmentId}*${data.adjustmentDate}${this.segmentSeparator}`);
    // Add N1, G62, LX, W21, etc. segments
    segments.push(`SE*4*0001${this.segmentSeparator}`);

    return segments.join('');
  }

  // Business logic methods

  private async processWarehouseShippingOrder(order: EDI940WarehouseShippingOrder): Promise<void> {
    // Create picking tasks, allocate inventory, etc.
    // eslint-disable-next-line no-console
    console.log(`Processing warehouse shipping order: ${order.shipmentId}`);
  }

  private async processTransferReceiptAdvice(receipt: EDI944WarehouseStockTransferReceiptAdvice): Promise<void> {
    // Update inventory, handle discrepancies, etc.
    // eslint-disable-next-line no-console
    console.log(`Processing transfer receipt advice: ${receipt.transferId}`);
  }

  // Event publishing methods
  private async publishEDI940ReceivedEvent(order: EDI940WarehouseShippingOrder): Promise<void> {
    const event: EDI940ReceivedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.edi.940.received',
      aggregateId: order.shipmentId,
      aggregateType: 'EDI940WarehouseShippingOrder',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      shipmentId: order.shipmentId,
      warehouseCode: order.warehouseCode,
      itemCount: order.items.length,
      totalQuantity: order.items.reduce((sum, item) => sum + item.quantity, 0)
    };

    await this.eventBus.publish(event);
  }

  private async publishEDI943GeneratedEvent(advice: EDI943WarehouseStockTransferShipmentAdvice): Promise<void> {
    const event: EDI943GeneratedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.edi.943.generated',
      aggregateId: advice.transferId,
      aggregateType: 'EDI943WarehouseStockTransferShipmentAdvice',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      transferId: advice.transferId,
      warehouseCode: advice.warehouseCode,
      itemCount: advice.items.length,
      totalQuantity: advice.items.reduce((sum, item) => sum + item.quantity, 0)
    };

    await this.eventBus.publish(event);
  }

  private async publishEDI944ReceivedEvent(receipt: EDI944WarehouseStockTransferReceiptAdvice): Promise<void> {
    const event: EDI944ReceivedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.edi.944.received',
      aggregateId: receipt.transferId,
      aggregateType: 'EDI944WarehouseStockTransferReceiptAdvice',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      transferId: receipt.transferId,
      warehouseCode: receipt.warehouseCode,
      itemCount: receipt.items.length,
      totalReceived: receipt.items.reduce((sum, item) => sum + item.quantityReceived, 0),
      discrepancies: receipt.discrepancies.length
    };

    await this.eventBus.publish(event);
  }

  private async publishEDI945GeneratedEvent(advice: EDI945WarehouseShippingAdvice): Promise<void> {
    const event: EDI945GeneratedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.edi.945.generated',
      aggregateId: advice.shipmentId,
      aggregateType: 'EDI945WarehouseShippingAdvice',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      shipmentId: advice.shipmentId,
      warehouseCode: advice.warehouseCode,
      itemCount: advice.items.length,
      totalWeight: advice.totalWeight,
      totalVolume: advice.totalVolume
    };

    await this.eventBus.publish(event);
  }

  private async publishEDI947GeneratedEvent(advice: EDI947WarehouseInventoryAdjustmentAdvice): Promise<void> {
    const event: EDI947GeneratedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.edi.947.generated',
      aggregateId: advice.adjustmentId,
      aggregateType: 'EDI947WarehouseInventoryAdjustmentAdvice',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      adjustmentId: advice.adjustmentId,
      warehouseCode: advice.warehouseCode,
      itemCount: advice.items.length,
      netAdjustment: advice.totals.netAdjustment,
      adjustmentType: advice.adjustmentType
    };

    await this.eventBus.publish(event);
  }
}