/**
 * VALEO NeuroERP 3.0 - Receiving Service
 *
 * Handles inbound operations: ASN processing, dock management, quality control
 */

import { injectable } from 'inversify';
import { EventBus } from '../infrastructure/event-bus/event-bus';
import { InventoryMetricsService } from '../infrastructure/observability/metrics-service';
import { GoodsReceivedEvent, ReceivingMismatchEvent } from '../core/domain-events/inventory-domain-events';

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

export interface QuantityMismatch {
  lineId: string;
  sku: string;
  expected: number;
  received: number;
  variance: number;
}

// Constants
const QUANTITY_TOLERANCE_PERCENT = 0.05;
const MOCK_DOCK_UTILIZATION = 0.85;
const MOCK_AVERAGE_RECEIVING_TIME = 45;
const MOCK_QA_PASS_RATE = 0.96;
const MOCK_MISMATCH_RATE = 0.03;
const HTTP_OK_STATUS = 200;
const MS_TO_SECONDS = 1000;

export interface QualityCriterion {
  criterion: string;
  expected: string;
  actual: string;
  pass: boolean;
  notes?: string;
}

@injectable()
export class ReceivingService {
  private readonly metrics = new InventoryMetricsService();

  constructor(
    private readonly eventBus: EventBus
  ) {}

  /**
   * Process ASN (Advance Shipping Notice)
   */
  async processASN(asn: ASN): Promise<ASN> {
    const startTime = Date.now();

    try {
      // Validate ASN
      this.validateASN(asn);

      // Update ASN status
      asn.status = 'scheduled';

      // Schedule dock appointment if not provided
      if (!asn.dock) {
        asn.dock = await this.scheduleDockAppointment(asn);
      }

      this.metrics.recordApiResponseTime('receiving.validate_asn', (Date.now() - startTime) / MS_TO_SECONDS, { asnId: asn.asnId });

      return asn;
    } catch (error) {
      this.metrics.incrementErrorCount('receiving.asn_processing', { error: 'validation_failed' });
      throw error;
    }
  }

  /**
   * Start receiving process when truck arrives
   */
  async startReceiving(asnId: string, dock: string, carrierInfo: { driverName?: string; vehicleNumber?: string }): Promise<DockAppointment> {
    const _startTime = Date.now();

    try {
      // Find ASN
      const asn = await this.getASN(asnId);
      if (!asn) {
        throw new Error(`ASN ${asnId} not found`);
      }

      // Create dock appointment
      const appointment: DockAppointment = {
        appointmentId: `appt_${Date.now()}`,
        asnId,
        dock,
        scheduledTime: asn.expectedArrival,
        actualArrival: new Date(),
        status: 'receiving',
        carrier: asn.carrier,
        ...carrierInfo
      };

      // Update ASN status
      asn.status = 'receiving';
      asn.dock = dock;

      (this.metrics as any).recordApiResponseTime('POST', '/receiving/start', HTTP_OK_STATUS);

      return appointment;
    } catch (error) {
      this.metrics.incrementErrorCount('receiving.start_receiving', { error: 'start_receiving_error' });
      throw error;
    }
  }

  /**
   * Receive goods and perform quality inspection
   */
  async receiveGoods(
    asnId: string,
    receivedLines: Array<{
      lineId: string;
      receivedQty: number;
      lot?: string;
      serial?: string;
      condition: 'good' | 'damaged' | 'expired';
      qaRequired: boolean;
    }>
  ): Promise<{ received: ASNLine[]; mismatches: QuantityMismatch[] }> {
    const startTime = Date.now();

    try {
      const asn = await this.getASN(asnId);
      if (!asn) {
        throw new Error(`ASN ${asnId} not found`);
      }

      const received: ASNLine[] = [];
      const mismatches: any[] = [];

      for (const receivedLine of receivedLines) {
        const asnLine = asn.lines.find(line => line.lineId === receivedLine.lineId);
        if (!asnLine) {
          throw new Error(`ASN line ${receivedLine.lineId} not found`);
        }

        // Update received quantity
        asnLine.receivedQty = receivedLine.receivedQty;
      asnLine.lot = receivedLine.lot || asnLine.lot;
      asnLine.serial = receivedLine.serial || asnLine.serial;

        // Check for quantity mismatch
        if (Math.abs((asnLine.receivedQty || 0) - asnLine.expectedQty) > asnLine.expectedQty * QUANTITY_TOLERANCE_PERCENT) { // 5% tolerance
          mismatches.push({
            lineId: receivedLine.lineId,
            sku: asnLine.sku,
            expected: asnLine.expectedQty,
            received: asnLine.receivedQty,
            variance: ((asnLine.receivedQty || 0) - asnLine.expectedQty) / asnLine.expectedQty * 100
          });
        }

        // Perform quality inspection if required
        if (receivedLine.qaRequired) {
          const qaResult = await this.performQualityInspection(asnId, asnLine);
          asnLine.qaStatus = qaResult.result === 'pass' ? 'passed' : qaResult.result === 'fail' ? 'failed' : 'pending';
          asnLine.qaNotes = qaResult.notes;
        } else {
          asnLine.qaStatus = 'passed'; // Auto-pass if no QA required
        }

        received.push(asnLine);
      }

      // Publish events
      await this.publishGoodsReceivedEvent(asn, received);

      if (mismatches.length > 0) {
        await this.publishReceivingMismatchEvent(asn, mismatches);
      }

      // Update ASN status
      asn.status = 'completed';

      this.metrics.recordApiResponseTime('receiving.process_goods', (Date.now() - startTime) / MS_TO_SECONDS, { asnId: asnId });

      return { received, mismatches };
    } catch (error) {
      this.metrics.incrementErrorCount('receiving.goods_receipt', { error: 'processing_failed' });
      throw error;
    }
  }

  /**
   * Perform quality inspection
   */
  private async performQualityInspection(asnId: string, asnLine: ASNLine): Promise<{ result: 'pass' | 'fail' | 'conditional'; notes?: string }> {
    // In a real implementation, this would involve:
    // - Visual inspection criteria
    // - Measurement checks
    // - Documentation verification
    // - Sampling for lab testing

    const inspection: QualityInspection = {
      inspectionId: `qa_${Date.now()}`,
      asnId,
      lineId: asnLine.lineId,
      sku: asnLine.sku,
        lot: asnLine.lot,
        serial: asnLine.serial,
      quantity: asnLine.receivedQty || 0,
      inspectionType: 'visual',
      criteria: [
        {
          criterion: 'Packaging integrity',
          expected: 'Intact',
          actual: 'Intact',
          pass: true
        },
        {
          criterion: 'Product condition',
          expected: 'No damage',
          actual: 'No visible damage',
          pass: true
        }
      ],
      result: 'pass',
      inspectedBy: 'system', // In real implementation, get from auth context
      inspectedAt: new Date()
    };

    // Store inspection results (would be in database)
    this.storeQualityInspection(inspection);

    return {
      result: inspection.result,
      notes: inspection.notes
    };
  }

  /**
   * Schedule dock appointment
   */
  private async scheduleDockAppointment(asn: ASN): Promise<string> {
    // Simple dock scheduling logic
    // In production, this would consider:
    // - Dock availability
    // - ASN priority
    // - Carrier preferences
    // - Time slot optimization

    const availableDocks = ['DOCK-01', 'DOCK-02', 'DOCK-03', 'DOCK-04'];
    return availableDocks[Math.floor(Math.random() * availableDocks.length)];
  }

  /**
   * Get ASN by ID (mock implementation)
   */
  private async getASN(asnId: string): Promise<ASN | null> {
    // In real implementation, fetch from database
    // This is a mock for demonstration
    return {
      asnId,
      poId: 'PO-12345',
      supplierId: 'SUP-001',
      carrier: 'DHL',
      expectedArrival: new Date(),
      status: 'arrived',
      lines: [
        {
          lineId: 'line_1',
          sku: 'WIDGET-001',
          expectedQty: 100,
          uom: 'EA'
        }
      ]
    };
  }

  /**
   * Store quality inspection (mock implementation)
   */
  private storeQualityInspection(inspection: QualityInspection): void {
    // In real implementation, persist to database
    // Logging removed as per lint rules
  }

  /**
   * Publish goods received event
   */
  private async publishGoodsReceivedEvent(asn: ASN, receivedLines: ASNLine[]): Promise<void> {
    const event: GoodsReceivedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.goods.received',
      type: 'inventory.goods.received',
      aggregateId: asn.asnId,
      aggregateType: 'ASN',
      eventVersion: 1,
      occurredOn: new Date(),
      occurredAt: new Date(),
      aggregateVersion: 1,
      tenantId: 'default', // In real implementation, get from context
      asnId: asn.asnId,
      poId: asn.poId,
      dock: asn.dock || 'UNKNOWN',
      lines: receivedLines.map(line => ({
        sku: line.sku,
        gtin: line.gtin,
        qty: line.receivedQty || 0,
        uom: line.uom,
        lot: line.lot,
        expDate: line.expDate,
        qualityStatus: line.qaStatus || 'pending'
      }))
    };

    await this.eventBus.publish(event);
  }

  /**
   * Publish receiving mismatch event
   */
  private async publishReceivingMismatchEvent(asn: ASN, mismatches: QuantityMismatch[]): Promise<void> {
    const event: ReceivingMismatchEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.receiving.mismatch',
      type: 'inventory.receiving.mismatch',
      occurredAt: new Date(),
      aggregateVersion: 1,
      aggregateId: asn.asnId,
      aggregateType: 'ASN',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      asnId: asn.asnId,
      poId: asn.poId,
      discrepancies: mismatches.map(mismatch => ({
        sku: mismatch.sku,
        expectedQty: mismatch.expected,
        receivedQty: mismatch.received,
        reason: `Quantity variance: ${mismatch.variance.toFixed(2)}%`
      }))
    };

    await this.eventBus.publish(event);
  }

  /**
   * Validate ASN structure
   */
  private validateASN(asn: ASN): void {
    if (!asn.asnId || !asn.poId || !asn.supplierId) {
      throw new Error('ASN must have asnId, poId, and supplierId');
    }

    if (!asn.lines || asn.lines.length === 0) {
      throw new Error('ASN must have at least one line');
    }

    for (const line of asn.lines) {
      if (!line.sku || line.expectedQty <= 0) {
        throw new Error(`Invalid ASN line: ${line.lineId}`);
      }
    }
  }

  /**
   * Get receiving metrics
   */
  getMetrics(): {
    dockUtilization: number;
    averageReceivingTime: number;
    qaPassRate: number;
    mismatchRate: number;
  } {
    // In real implementation, calculate from actual data
    return {
      dockUtilization: MOCK_DOCK_UTILIZATION,
      averageReceivingTime: MOCK_AVERAGE_RECEIVING_TIME, // minutes
      qaPassRate: MOCK_QA_PASS_RATE,
      mismatchRate: MOCK_MISMATCH_RATE
    };
  }
}