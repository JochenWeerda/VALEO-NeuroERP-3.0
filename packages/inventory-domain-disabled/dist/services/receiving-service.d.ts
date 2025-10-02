/**
 * VALEO NeuroERP 3.0 - Receiving Service
 *
 * Handles inbound operations: ASN processing, dock management, quality control
 */
import { EventBus } from '../infrastructure/event-bus/event-bus';
export interface ASN {
    asnId: string;
    poId: string;
    supplierId: string;
    carrier: string;
    expectedArrival: Date;
    lines: ASNLine[];
    status: 'scheduled' | 'in_transit' | 'arrived' | 'receiving' | 'completed' | 'cancelled';
    dock?: string;
    notes?: string;
}
export interface ASNLine {
    lineId: string;
    sku: string;
    gtin?: string;
    expectedQty: number;
    uom: string;
    lot?: string;
    serial?: string;
    expDate?: Date;
    mfgDate?: Date;
    receivedQty?: number;
    qaStatus?: 'pending' | 'passed' | 'failed';
    qaNotes?: string;
}
export interface DockAppointment {
    appointmentId: string;
    asnId: string;
    dock: string;
    scheduledTime: Date;
    actualArrival?: Date;
    status: 'scheduled' | 'arrived' | 'receiving' | 'completed';
    carrier: string;
    driverName?: string;
    vehicleNumber?: string;
}
export interface QualityInspection {
    inspectionId: string;
    asnId: string;
    lineId: string;
    sku: string;
    lot?: string;
    serial?: string;
    quantity: number;
    inspectionType: 'visual' | 'measurement' | 'functional' | 'documentation';
    criteria: QualityCriterion[];
    result: 'pass' | 'fail' | 'conditional';
    notes?: string;
    inspectedBy: string;
    inspectedAt: Date;
}
export interface QualityCriterion {
    criterion: string;
    expected: string;
    actual: string;
    pass: boolean;
    notes?: string;
}
export declare class ReceivingService {
    private readonly eventBus;
    private readonly metrics;
    constructor(eventBus: EventBus);
    /**
     * Process ASN (Advance Shipping Notice)
     */
    processASN(asn: ASN): Promise<ASN>;
    /**
     * Start receiving process when truck arrives
     */
    startReceiving(asnId: string, dock: string, carrierInfo: {
        driverName?: string;
        vehicleNumber?: string;
    }): Promise<DockAppointment>;
    /**
     * Receive goods and perform quality inspection
     */
    receiveGoods(asnId: string, receivedLines: Array<{
        lineId: string;
        receivedQty: number;
        lot?: string;
        serial?: string;
        condition: 'good' | 'damaged' | 'expired';
        qaRequired: boolean;
    }>): Promise<{
        received: ASNLine[];
        mismatches: any[];
    }>;
    /**
     * Perform quality inspection
     */
    private performQualityInspection;
    /**
     * Schedule dock appointment
     */
    private scheduleDockAppointment;
    /**
     * Get ASN by ID (mock implementation)
     */
    private getASN;
    /**
     * Store quality inspection (mock implementation)
     */
    private storeQualityInspection;
    /**
     * Publish goods received event
     */
    private publishGoodsReceivedEvent;
    /**
     * Publish receiving mismatch event
     */
    private publishReceivingMismatchEvent;
    /**
     * Validate ASN structure
     */
    private validateASN;
    /**
     * Get receiving metrics
     */
    getMetrics(): {
        dockUtilization: number;
        averageReceivingTime: number;
        qaPassRate: number;
        mismatchRate: number;
    };
}
//# sourceMappingURL=receiving-service.d.ts.map