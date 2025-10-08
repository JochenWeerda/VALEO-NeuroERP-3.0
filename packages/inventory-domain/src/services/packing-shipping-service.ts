/**
 * VALEO NeuroERP 3.0 - Packing & Shipping Service
 *
 * GS1 compliant labeling, carrier integration, and shipping management
 */

import { injectable } from 'inversify';
import { EventBus } from '../infrastructure/event-bus/event-bus';
import { InventoryMetricsService } from '../infrastructure/observability/metrics-service';
import {
  PackCompletedEvent,
  PackTaskCreatedEvent,
  ShipmentCreatedEvent,
  ShipmentShippedEvent
} from '../core/domain-events/inventory-domain-events';

export interface PackingTask {
  taskId: string;
  orderId: string;
  shipmentId?: string;
  items: Array<{
    sku: string;
    quantity: number;
    lot?: string;
    serial?: string;
    packedQuantity: number;
  }>;
  status: 'pending' | 'in_progress' | 'completed' | 'short' | 'damaged';
  assignedTo?: string;
  packingStation?: string;
  priority: number;
  estimatedTime: number; // minutes
  actualTime?: number;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  qualityChecks?: Array<{
    checkType: 'quantity' | 'condition' | 'label';
    passed: boolean;
    notes?: string;
    checkedBy: string;
    checkedAt: Date;
  }>;
}

export interface Package {
  packageId: string;
  shipmentId: string;
  packageType: 'box' | 'pallet' | 'crate' | 'envelope';
  sscc: string; // GS1 SSCC
  weight: number;
  dimensions: {
    length: number;
    width: number;
    height: number;
    unit: 'mm' | 'cm' | 'in';
  };
  contents: Array<{
    sku: string;
    quantity: number;
    lot?: string;
    serial?: string;
    value: number;
  }>;
  labels: Array<{
    type: 'sscc' | 'gtin' | 'batch' | 'expiry' | 'shipping';
    format: '1d' | '2d' | 'qr';
    data: string;
    printed: boolean;
    printedAt?: Date;
  }>;
  packedAt: Date;
  packedBy: string;
  qualityStatus: 'pending' | 'passed' | 'failed';
}

export interface Shipment {
  shipmentId: string;
  shipmentNumber: string;
  orderId: string;
  carrier: string;
  serviceType: string;
  trackingNumber?: string;
  status: 'planned' | 'packed' | 'ready' | 'shipped' | 'delivered' | 'returned';
  shipFrom: {
    name: string;
    address: Address;
    contact?: Contact;
  };
  shipTo: {
    name: string;
    address: Address;
    contact?: Contact;
  };
  packages: Package[];
  totalWeight: number;
  totalValue: number;
  shippingCost?: number;
  insuranceValue?: number;
  specialInstructions?: string;
  requiredDeliveryDate?: Date;
  actualDeliveryDate?: Date;
  createdAt: Date;
  packedAt?: Date;
  shippedAt?: Date;
  deliveredAt?: Date;
  carrierEvents?: Array<{
    eventType: string;
    description: string;
    location?: string;
    timestamp: Date;
  }>;
}

export interface Address {
  street1: string;
  street2?: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
}

export interface Contact {
  name: string;
  phone?: string;
  email?: string;
}

export interface CustomsInfo {
  harmonizedCodes: string[];
  totalValue: number;
  currency: string;
}

export interface GS1Label {
  type: 'sscc' | 'gtin' | 'batch' | 'expiry' | 'shipping';
  format: '1d' | '2d' | 'qr';
  data: string;
  humanReadable?: string;
  barcodeData: string;
}

export interface CarrierIntegration {
  carrierId: string;
  name: string;
  apiEndpoint: string;
  apiKey: string;
  supportedServices: string[];
  labelFormats: ('pdf' | 'png' | 'zpl' | 'epl')[];
  trackingCapabilities: boolean;
  active: boolean;
}

// Constants
const GS1_COMPANY_PREFIX = '123456789'; // Example company prefix
const SSCC_SERIAL_REF_LENGTH = 9;
const DECIMAL_BASE = 10;
const GS1_WEIGHT_ODD_POSITION = 3;
const DEFAULT_PRIORITY = 5;
const BASE_PACKING_TIME = 5; // minutes
const PACKING_TIME_PER_ITEM = 2; // minutes per item
const PACKING_TIME_PER_UNIT = 0.5; // minutes per unit
const RANDOM_BASE = 36;
const RANDOM_ID_START = 2;
const RANDOM_ID_LENGTH = 9;
const HOURS_TO_MS = 60 * 60 * 1000;
const MINUTES_TO_MS = 60 * 1000;
const SSCC_PREFIX = '003';
const MS_TO_SECONDS = 1000;
const PICKED_UP_OFFSET_HOURS = 2;
const IN_TRANSIT_OFFSET_HOURS = 1;

@injectable()
export class PackingShippingService {
  private readonly metrics = new InventoryMetricsService();
  private readonly carriers: Map<string, CarrierIntegration> = new Map();

  constructor(
    private readonly eventBus: EventBus
  ) {
    this.initializeDefaultCarriers();
  }

  /**
   * Create packing task from order
   */
  async createPackingTask(orderId: string, packingStation?: string): Promise<PackingTask> {
    const startTime = Date.now();

    try {
      const orderDetails = await this.getOrderDetails(orderId);
      if (orderDetails == null) {
        throw new Error(`Order ${orderId} not found`);
      }

      const task: PackingTask = {
        taskId: `pack_${Date.now()}`,
        orderId,
        items: orderDetails.lines.map((line: { sku: string; quantity: number; lot?: string; serial?: string }) => ({
          sku: line.sku,
          quantity: line.quantity,
          lot: line.lot,
          serial: line.serial,
          packedQuantity: 0
        })),
        status: 'pending',
        packingStation: packingStation ?? '',
        priority: orderDetails.priority ?? DEFAULT_PRIORITY,
        estimatedTime: this.estimatePackingTime(orderDetails.lines),
        createdAt: new Date()
      };

      // Publish event
      await this.publishPackTaskCreatedEvent(task);

      this.metrics.recordDatabaseQueryDuration('packing.task_creation', (Date.now() - startTime) / MS_TO_SECONDS, { orderId });
      this.metrics.incrementPackTasks('packing.created', { orderId });

      return task;
    } catch (error) {
      this.metrics.incrementErrorCount('packing.task_creation_failed', { error: 'task_creation_error' });
      throw error;
    }
  }

  /**
   * Start packing task
   */
  async startPackingTask(taskId: string, packerId: string): Promise<void> {
    const task = await this.findPackingTask(taskId);
    if (task == null) {
      throw new Error(`Packing task ${taskId} not found`);
    }

    if (task.status !== 'pending') {
      throw new Error(`Task ${taskId} is not in pending status`);
    }

    task.status = 'in_progress';
    task.assignedTo = packerId;
    task.startedAt = new Date();
  }

  /**
   * Complete packing task with package details
   */
  async completePackingTask(
    taskId: string,
    packages: Omit<Package, 'packageId' | 'packedAt' | 'packedBy'>[]
  ): Promise<Package[]> {
    const startTime = Date.now();
    const task = await this.findPackingTask(taskId);

    if (task == null) {
      throw new Error(`Packing task ${taskId} not found`);
    }

    if (task.status !== 'in_progress') {
      throw new Error(`Task ${taskId} is not in progress`);
    }

    // Validate packages against task items
    await this.validatePackages(task, packages as Package[]);

    // Generate SSCC and labels for each package
    const completedPackages: Package[] = [];
    for (const pkg of packages) {
      const packageWithId: Package = {
        ...pkg,
        packageId: `pkg_${Date.now()}_${Math.random().toString(RANDOM_BASE).substr(RANDOM_ID_START, RANDOM_ID_LENGTH)}`,
        sscc: this.generateSSCC(),
        labels: await this.generatePackageLabels(pkg as Package),
        packedAt: new Date(),
        packedBy: task.assignedTo ?? 'unknown'
      };

      completedPackages.push(packageWithId);
    }

    // Update task
    task.status = 'completed';
    task.completedAt = new Date();
    task.actualTime = task.startedAt != null ?
      (task.completedAt.getTime() - task.startedAt.getTime()) / MINUTES_TO_MS : undefined;

    // Publish event
    await this.publishPackCompletedEvent(task, completedPackages);

    this.metrics.recordDatabaseQueryDuration('packing.task_completion', (Date.now() - startTime) / MS_TO_SECONDS, { taskId });
    this.metrics.incrementPackTasks('packing.completed', { taskId });

    return completedPackages;
  }

  /**
   * Create shipment from packages
   */
  async createShipment(
    orderId: string,
    packages: Package[],
    carrier: string,
    shipTo: Shipment['shipTo'],
    options?: {
      serviceType?: string;
      requiredDeliveryDate?: Date;
      insuranceValue?: number;
      specialInstructions?: string;
    }
  ): Promise<Shipment> {
    const startTime = Date.now();

    try {
      const shipment: Shipment = {
        shipmentId: `ship_${Date.now()}`,
        shipmentNumber: `SH${Date.now()}`,
        orderId,
        carrier,
        serviceType: options?.serviceType ?? 'standard',
        status: 'planned',
        shipFrom: await this.getShipFromAddress(),
        shipTo,
        packages,
        totalWeight: packages.reduce((sum, pkg) => sum + pkg.weight, 0),
        totalValue: packages.reduce((sum, pkg) =>
          sum + pkg.contents.reduce((pkgSum, item) => pkgSum + item.value, 0), 0
        ),
        insuranceValue: options?.insuranceValue,
        specialInstructions: options?.specialInstructions,
        requiredDeliveryDate: options?.requiredDeliveryDate,
        createdAt: new Date()
      };

      // Generate shipping labels
      await this.generateShippingLabels(shipment);

      // Publish event
      await this.publishShipmentCreatedEvent(shipment);

      this.metrics.recordDatabaseQueryDuration('shipping.shipment_creation', (Date.now() - startTime) / MS_TO_SECONDS, { orderId });

      return shipment;
    } catch (error) {
      this.metrics.incrementErrorCount('shipping.shipment_creation_failed', { error: 'shipment_creation_error' });
      throw error;
    }
  }

  /**
   * Ship shipment with carrier integration
   */
  async shipShipment(shipmentId: string): Promise<string> {
    const startTime = Date.now();
    const shipment = await this.findShipment(shipmentId);

    if (shipment == null) {
      throw new Error(`Shipment ${shipmentId} not found`);
    }

    if (shipment.status !== 'ready') {
      throw new Error(`Shipment ${shipmentId} is not ready for shipping`);
    }

    try {
      // Get carrier integration
      const carrier = this.carriers.get(shipment.carrier);
      if (carrier == null) {
        throw new Error(`Carrier ${shipment.carrier} not configured`);
      }

      // Create shipment with carrier
      const trackingNumber = await this.createCarrierShipment(shipment, carrier);

      // Update shipment
      shipment.trackingNumber = trackingNumber;
      shipment.status = 'shipped';
      shipment.shippedAt = new Date();

      // Publish event
      await this.publishShipmentShippedEvent(shipment);

      this.metrics.recordDatabaseQueryDuration('shipping.carrier_integration', (Date.now() - startTime) / MS_TO_SECONDS, { carrier: carrier.carrierId });

      return trackingNumber;
    } catch (error) {
      this.metrics.incrementErrorCount('shipping.carrier_integration_failed', { error: 'carrier_integration_error' });
      throw error;
    }
  }

  /**
   * Generate GS1 labels for package
   */
  async generatePackageLabels(pkg: Package): Promise<Package['labels']> {
    const labels: Package['labels'] = [];

    // SSCC label
    labels.push({
      type: 'sscc',
      format: '1d',
      data: pkg.sscc,
      printed: false
    });

    // GTIN labels for each item
    for (const item of pkg.contents) {
      const gtin = await this.getGTINForSKU(item.sku);
      if (gtin != null) {
        labels.push({
          type: 'gtin',
          format: '1d',
          data: gtin,
          printed: false
        });
      }
    }

    // Batch/lot labels
    const lots = Array.from(new Set(pkg.contents.map(item => item.lot).filter(lot => lot != null)));
    for (const lot of lots) {
      if (lot != null) {
        labels.push({
          type: 'batch',
          format: '1d',
          data: lot,
          printed: false
        });
      }
    }

    return labels;
  }

  /**
   * Get shipment tracking information
   */
  async getShipmentTracking(shipmentId: string): Promise<Shipment['carrierEvents']> {
    const shipment = await this.findShipment(shipmentId);
    if (shipment == null) {
      throw new Error(`Shipment ${shipmentId} not found`);
    }

    if (shipment.trackingNumber == null) {
      return [];
    }

    const carrier = this.carriers.get(shipment.carrier);
    if (carrier == null || carrier.trackingCapabilities !== true) {
      return shipment.carrierEvents ?? [];
    }

    // Get tracking from carrier API
    const trackingEvents = await this.getCarrierTracking(shipment.trackingNumber, carrier);

    // Update shipment with latest events
    shipment.carrierEvents = trackingEvents;

    // Check if delivered
    const deliveredEvent = trackingEvents.find(event => event.eventType === 'delivered');
    if (deliveredEvent != null && shipment.status !== 'delivered') {
      shipment.status = 'delivered';
      shipment.deliveredAt = deliveredEvent.timestamp;
    }

    return trackingEvents;
  }

  /**
   * Generate shipping manifest
   */
  async generateShippingManifest(shipmentId: string): Promise<{
    shipment: Shipment;
    manifest: {
      totalPackages: number;
      totalWeight: number;
      totalValue: number;
      packageDetails: Array<{
        packageId: string;
        sscc: string;
        weight: number;
        contents: Package['contents'];
      }>;
      customsInfo?: CustomsInfo;
    };
  }> {
    const shipment = await this.findShipment(shipmentId);
    if (shipment == null) {
      throw new Error(`Shipment ${shipmentId} not found`);
    }

    const manifest = {
      totalPackages: shipment.packages.length,
      totalWeight: shipment.totalWeight,
      totalValue: shipment.totalValue,
      packageDetails: shipment.packages.map(pkg => ({
        packageId: pkg.packageId,
        sscc: pkg.sscc,
        weight: pkg.weight,
        contents: pkg.contents
      }))
    };

    // Add customs information if international
    if (this.isInternationalShipment(shipment)) {
      (manifest as { customsInfo?: CustomsInfo }).customsInfo = await this.generateCustomsInfo(shipment);
    }

    return { shipment, manifest };
  }

  // Private helper methods

  private async validatePackages(task: PackingTask, packages: Package[]): Promise<void> {
    const packedItems = new Map<string, number>();

    // Count packed quantities
    for (const pkg of packages) {
      for (const item of pkg.contents) {
        const key = `${item.sku}-${item.lot ?? ''}-${item.serial ?? ''}`;
        packedItems.set(key, (packedItems.get(key) ?? 0) + item.quantity);
      }
    }

    // Validate against task requirements
    for (const requiredItem of task.items) {
      const key = `${requiredItem.sku}-${requiredItem.lot ?? ''}-${requiredItem.serial ?? ''}`;
      const packedQty = packedItems.get(key) ?? 0;

      if (packedQty !== requiredItem.quantity) {
        throw new Error(`Quantity mismatch for ${requiredItem.sku}: required ${requiredItem.quantity}, packed ${packedQty}`);
      }
    }
  }

  private generateSSCC(): string {
    // Generate GS1 SSCC (Serial Shipping Container Code)
    // Format: (00) + Extension digit + GS1 Company Prefix + Serial Reference
    const companyPrefix = GS1_COMPANY_PREFIX; // Example
    const serialRef = Date.now().toString().slice(-SSCC_SERIAL_REF_LENGTH); // 9 digits
    const sscc = `${SSCC_PREFIX}${companyPrefix}${serialRef}`;

    // Calculate check digit
    const checkDigit = this.calculateGS1CheckDigit(sscc);
    return sscc + checkDigit;
  }

  private calculateGS1CheckDigit(data: string): number {
    let sum = 0;
    for (let i = data.length - 1; i >= 0; i--) {
      const digit = parseInt(data[i], DECIMAL_BASE);
      sum += i % 2 === 0 ? digit * GS1_WEIGHT_ODD_POSITION : digit;
    }
    const remainder = sum % DECIMAL_BASE;
    return remainder === 0 ? 0 : DECIMAL_BASE - remainder;
  }

  private estimatePackingTime(items: Array<{ sku: string; quantity: number; lot?: string; serial?: string }>): number {
    const baseTime = BASE_PACKING_TIME; // minutes
    const itemsFactor = items.length * PACKING_TIME_PER_ITEM; // minutes per item
    const quantityFactor = items.reduce((sum, item) => sum + item.quantity, 0) * PACKING_TIME_PER_UNIT; // minutes per unit
    return Math.ceil(baseTime + itemsFactor + quantityFactor);
  }

  private async getOrderDetails(orderId: string): Promise<{ orderId: string; priority: number; lines: Array<{ sku: string; quantity: number; lot?: string; serial?: string }> }> {
    // TODO: Implement actual order repository call
    // This should fetch order details from the order domain service
    throw new Error(`Order details retrieval not implemented for order: ${orderId}`);
  }

  private async findPackingTask(taskId: string): Promise<PackingTask | null> {
    // TODO: Implement actual packing task repository call
    // This should fetch packing task from database
    throw new Error(`Packing task retrieval not implemented for task: ${taskId}`);
  }

  private async findShipment(shipmentId: string): Promise<Shipment | null> {
    // TODO: Implement actual shipment repository call
    // This should fetch shipment from database
    throw new Error(`Shipment retrieval not implemented for shipment: ${shipmentId}`);
  }

  private async getGTINForSKU(sku: string): Promise<string | null> {
    // Mock GTIN lookup
    const gtinMap: Record<string, string> = {
      'WIDGET-001': '01234567890123',
      'GADGET-002': '09876543210987'
    };
    return gtinMap[sku] ?? null;
  }

  private async getShipFromAddress(): Promise<Shipment['shipFrom']> {
    // TODO: Implement actual warehouse configuration service call
    // This should fetch warehouse address from configuration
    throw new Error('Ship-from address retrieval not implemented');
  }

  private async generateShippingLabels(shipment: Shipment): Promise<void> {
    // Generate carrier-specific shipping labels
    const carrier = this.carriers.get(shipment.carrier);
    if (carrier == null) return;

    // Implementation would generate actual labels via carrier API
    // no console per lint rules
  }

  private async createCarrierShipment(_shipment: Shipment, _carrier: CarrierIntegration): Promise<string> {
    // Mock carrier API integration
    return `TRK${Date.now()}`;
  }

  private async getCarrierTracking(_trackingNumber: string, _carrier: CarrierIntegration): Promise<Shipment['carrierEvents']> {
    // Mock tracking API
    return [
      {
        eventType: 'picked_up',
        description: 'Package picked up',
        location: 'Warehouse',
        timestamp: new Date(Date.now() - PICKED_UP_OFFSET_HOURS * HOURS_TO_MS)
      },
      {
        eventType: 'in_transit',
        description: 'In transit to destination',
        location: 'Distribution Center',
        timestamp: new Date(Date.now() - IN_TRANSIT_OFFSET_HOURS * HOURS_TO_MS)
      }
    ];
  }

  private isInternationalShipment(shipment: Shipment): boolean {
    return shipment.shipFrom.address.country !== shipment.shipTo.address.country;
  }

  private async generateCustomsInfo(shipment: Shipment): Promise<CustomsInfo> {
    // Generate customs information for international shipments
    return {
      harmonizedCodes: [],
      totalValue: shipment.totalValue,
      currency: 'EUR'
    };
  }

  private async getCarrierForTask(task: PackingTask): Promise<string> {
    // Try to get carrier from associated shipment
    if (task.shipmentId != null) {
      const shipment = await this.findShipment(task.shipmentId);
      if (shipment != null) {
        return shipment.carrier;
      }
    }
    
    // Fallback to default carrier
    return 'UPS';
  }

  private initializeDefaultCarriers(): void {
    const carriers: CarrierIntegration[] = [
      {
        carrierId: 'ups',
        name: 'UPS',
        apiEndpoint: 'https://api.ups.com',
        apiKey: process.env.UPS_API_KEY ?? '',
        supportedServices: ['ground', 'air', 'express'],
        labelFormats: ['pdf', 'png', 'zpl'],
        trackingCapabilities: true,
        active: true
      },
      {
        carrierId: 'fedex',
        name: 'FedEx',
        apiEndpoint: 'https://api.fedex.com',
        apiKey: process.env.FEDEX_API_KEY ?? '',
        supportedServices: ['ground', 'express', 'overnight'],
        labelFormats: ['pdf', 'png', 'zpl'],
        trackingCapabilities: true,
        active: true
      },
      {
        carrierId: 'dhl',
        name: 'DHL',
        apiEndpoint: 'https://api.dhl.com',
        apiKey: process.env.DHL_API_KEY ?? '',
        supportedServices: ['ground', 'express', 'international'],
        labelFormats: ['pdf', 'png', 'zpl'],
        trackingCapabilities: true,
        active: true
      }
    ];

    carriers.forEach(carrier => this.carriers.set(carrier.carrierId, carrier));
  }

  // Event publishing methods
  private async publishPackTaskCreatedEvent(task: PackingTask): Promise<void> {
    const event: PackTaskCreatedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.pack.created',
      type: 'inventory.pack.created',
      aggregateId: task.taskId,
      aggregateType: 'PackingTask',
      eventVersion: 1,
      occurredOn: new Date(),
      occurredAt: new Date(),
      aggregateVersion: 1,
      tenantId: 'default',
      orderId: task.orderId,
      shipmentId: task.shipmentId ?? '',
      items: task.items.map(item => ({
        sku: item.sku,
        quantity: item.quantity,
        lot: item.lot,
        serial: item.serial
      }))
    };

    await this.eventBus.publish(event);
  }

  private async publishPackCompletedEvent(task: PackingTask, packages: Package[]): Promise<void> {
    const event: PackCompletedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.pack.completed',
      type: 'inventory.pack.completed',
      aggregateId: task.taskId,
      aggregateType: 'PackingTask',
      eventVersion: 1,
      occurredOn: new Date(),
      occurredAt: new Date(),
      aggregateVersion: 1,
      tenantId: 'default',
      orderId: task.orderId,
      shipmentId: task.shipmentId ?? '',
      packedBy: task.assignedTo ?? 'unknown',
      weight: packages.reduce((sum, pkg) => sum + pkg.weight, 0),
      dimensions: {
        length: Math.max(...packages.map(p => p.dimensions.length)),
        width: Math.max(...packages.map(p => p.dimensions.width)),
        height: packages.reduce((sum, pkg) => sum + pkg.dimensions.height, 0)
      },
      carrier: await this.getCarrierForTask(task)
    };

    await this.eventBus.publish(event);
  }

  private async publishShipmentCreatedEvent(shipment: Shipment): Promise<void> {
    const event: ShipmentCreatedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.shipment.created',
      type: 'inventory.shipment.created',
      aggregateId: shipment.shipmentId,
      aggregateType: 'Shipment',
      eventVersion: 1,
      occurredOn: new Date(),
      occurredAt: new Date(),
      aggregateVersion: 1,
      tenantId: 'default',
      shipmentId: shipment.shipmentId,
      orderId: shipment.orderId,
      carrier: shipment.carrier,
      trackingNumber: shipment.trackingNumber,
      items: shipment.packages.flatMap(pkg =>
        pkg.contents.map(item => ({
          sku: item.sku,
          quantity: item.quantity,
          lot: item.lot,
          serial: item.serial
        }))
      )
    };

    await this.eventBus.publish(event);
  }

  private async publishShipmentShippedEvent(shipment: Shipment): Promise<void> {
    if (shipment.trackingNumber == null || shipment.shippedAt == null) {
      throw new Error('Cannot publish shipment shipped event without tracking number and shipped date');
    }

    const event: ShipmentShippedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.shipment.shipped',
      type: 'inventory.shipment.shipped',
      aggregateId: shipment.shipmentId,
      aggregateType: 'Shipment',
      eventVersion: 1,
      occurredOn: new Date(),
      occurredAt: new Date(),
      aggregateVersion: 1,
      tenantId: 'default',
      shipmentId: shipment.shipmentId,
      orderId: shipment.orderId,
      carrier: shipment.carrier,
      trackingNumber: shipment.trackingNumber,
      shippedAt: shipment.shippedAt,
      shippedBy: 'system'
    };

    await this.eventBus.publish(event);
  }
}