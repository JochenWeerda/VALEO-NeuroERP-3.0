/**
 * VALEO NeuroERP 3.0 - Packing & Shipping Service
 *
 * GS1 compliant labeling, carrier integration, and shipping management
 */
import { EventBus } from '../infrastructure/event-bus/event-bus';
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
    estimatedTime: number;
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
    sscc: string;
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
export declare class PackingShippingService {
    private readonly eventBus;
    private readonly metrics;
    private carriers;
    constructor(eventBus: EventBus);
    /**
     * Create packing task from order
     */
    createPackingTask(orderId: string, packingStation?: string): Promise<PackingTask>;
    /**
     * Start packing task
     */
    startPackingTask(taskId: string, packerId: string): Promise<void>;
    /**
     * Complete packing task with package details
     */
    completePackingTask(taskId: string, packages: Omit<Package, 'packageId' | 'packedAt' | 'packedBy'>[]): Promise<Package[]>;
    /**
     * Create shipment from packages
     */
    createShipment(orderId: string, packages: Package[], carrier: string, shipTo: Shipment['shipTo'], options?: {
        serviceType?: string;
        requiredDeliveryDate?: Date;
        insuranceValue?: number;
        specialInstructions?: string;
    }): Promise<Shipment>;
    /**
     * Ship shipment with carrier integration
     */
    shipShipment(shipmentId: string): Promise<string>;
    /**
     * Generate GS1 labels for package
     */
    generatePackageLabels(pkg: Package): Promise<Package['labels']>;
    /**
     * Get shipment tracking information
     */
    getShipmentTracking(shipmentId: string): Promise<Shipment['carrierEvents']>;
    /**
     * Generate shipping manifest
     */
    generateShippingManifest(shipmentId: string): Promise<{
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
            customsInfo?: {
                harmonizedCodes: Array<{
                    sku: string;
                    code: string;
                    description: string;
                }>;
                totalValue: number;
                currency: string;
            };
        };
    }>;
    private validatePackages;
    private generateSSCC;
    private calculateGS1CheckDigit;
    private estimatePackingTime;
    private getOrderDetails;
    private findPackingTask;
    private findShipment;
    private getGTINForSKU;
    private getShipFromAddress;
    private generateShippingLabels;
    private createCarrierShipment;
    private getCarrierTracking;
    private isInternationalShipment;
    private generateCustomsInfo;
    private getCarrierForTask;
    private initializeDefaultCarriers;
    private publishPackTaskCreatedEvent;
    private publishPackCompletedEvent;
    private publishShipmentCreatedEvent;
    private publishShipmentShippedEvent;
}
//# sourceMappingURL=packing-shipping-service.d.ts.map