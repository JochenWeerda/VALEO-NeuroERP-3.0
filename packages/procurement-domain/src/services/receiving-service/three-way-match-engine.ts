import { injectable } from 'inversify';
import { PurchaseOrder } from '../../core/entities/purchase-order';
import { Receipt } from '../../core/entities/receipt';

export interface InvoiceData {
  invoiceId: string;
  invoiceNumber: string;
  supplierId: string;
  purchaseOrderId: string;
  invoiceDate: Date;
  dueDate: Date;
  currency: string;
  subtotal: number;
  taxTotal: number;
  discountTotal: number;
  totalAmount: number;
  items: Array<{
    purchaseOrderItemId: string;
    sku: string;
    description: string;
    quantity: number;
    unitPrice: number;
    lineTotal: number;
    taxCode?: string;
    taxRate?: number;
  }>;
  attachments?: string[];
  notes?: string;
}

export interface MatchResult {
  matchId: string;
  purchaseOrderId: string;
  receiptId?: string;
  invoiceId: string;
  matchType: 'two_way' | 'three_way';
  overallStatus: 'matched' | 'partial_match' | 'exceptions' | 'no_match';

  // Matching Results
  quantityMatch: 'matched' | 'over_invoice' | 'under_invoice' | 'no_receipt';
  priceMatch: 'matched' | 'price_variance' | 'no_match';
  qualityMatch: 'matched' | 'quality_issues' | 'no_receipt';

  // Detailed Results
  itemMatches: Array<{
    purchaseOrderItemId: string;
    receiptItemId?: string;
    invoiceItemId: string;
    quantityMatch: boolean;
    priceMatch: boolean;
    qualityMatch: boolean;
    exceptions: string[];
    varianceAmount: number;
  }>;

  // Summary
  totalVariance: number;
  variancePercentage: number;
  exceptionsCount: number;
  autoApprovalEligible: boolean;

  // Processing Information
  matchedAt: Date;
  matchedBy: 'auto' | 'manual';
  processingNotes?: string;
}

export interface MatchException {
  exceptionId: string;
  matchId: string;
  exceptionType: 'quantity_mismatch' | 'price_variance' | 'quality_issue' | 'missing_receipt' | 'duplicate_invoice' | 'invalid_tax' | 'expired_contract';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  affectedItems: string[];
  suggestedResolution: string;
  requiresApproval: boolean;
  approverRole?: string;
  createdAt: Date;
  resolvedAt?: Date;
  resolvedBy?: string;
  resolutionNotes?: string;
}

export interface MatchConfiguration {
  tolerance: {
    quantity: number; // percentage (e.g., 5 for 5%)
    price: number;    // percentage (e.g., 2 for 2%)
    date: number;     // days (e.g., 7 for 7 days)
  };
  autoApproval: {
    enabled: boolean;
    maxVariancePercentage: number;
    requiresReceipt: boolean;
    restrictedCategories: string[];
  };
  escalation: {
    lowVarianceApprover: string;
    mediumVarianceApprover: string;
    highVarianceApprover: string;
    criticalVarianceApprover: string;
  };
}

@injectable()
export class ThreeWayMatchEngine {
  private readonly defaultConfig: MatchConfiguration = {
    tolerance: {
      quantity: 5, // 5%
      price: 2,    // 2%
      date: 7      // 7 days
    },
    autoApproval: {
      enabled: true,
      maxVariancePercentage: 5,
      requiresReceipt: true,
      restrictedCategories: ['IT Hardware', 'Software Licenses']
    },
    escalation: {
      lowVarianceApprover: 'Procurement Specialist',
      mediumVarianceApprover: 'Procurement Manager',
      highVarianceApprover: 'Finance Manager',
      criticalVarianceApprover: 'CFO'
    }
  };

  /**
   * Perform 3-way matching between PO, Receipt, and Invoice
   */
  async performThreeWayMatch(
    purchaseOrder: PurchaseOrder,
    receipt: Receipt,
    invoice: InvoiceData,
    config: Partial<MatchConfiguration> = {}
  ): Promise<MatchResult> {
    const effectiveConfig = { ...this.defaultConfig, ...config };

    // Validate inputs
    this.validateMatchInputs(purchaseOrder, receipt, invoice);

    // Perform detailed matching
    const itemMatches = await this.matchItems(purchaseOrder, receipt, invoice, effectiveConfig);
    const exceptions = this.identifyExceptions(itemMatches, effectiveConfig);

    // Calculate overall results
    const quantityMatch = this.determineQuantityMatch(itemMatches);
    const priceMatch = this.determinePriceMatch(itemMatches, effectiveConfig);
    const qualityMatch = this.determineQualityMatch(receipt);

    const overallStatus = this.determineOverallStatus(quantityMatch, priceMatch, qualityMatch, exceptions);
    const totalVariance = itemMatches.reduce((sum, match) => sum + Math.abs(match.varianceAmount), 0);
    const variancePercentage = purchaseOrder.totalAmount > 0 ? (totalVariance / purchaseOrder.totalAmount) * 100 : 0;

    const autoApprovalEligible = this.checkAutoApprovalEligibility(
      overallStatus,
      variancePercentage,
      exceptions,
      effectiveConfig
    );

    return {
      matchId: this.generateMatchId(),
      purchaseOrderId: purchaseOrder.id,
      receiptId: receipt.id,
      invoiceId: invoice.invoiceId,
      matchType: 'three_way',
      overallStatus,
      quantityMatch,
      priceMatch,
      qualityMatch,
      itemMatches,
      totalVariance,
      variancePercentage,
      exceptionsCount: exceptions.length,
      autoApprovalEligible,
      matchedAt: new Date(),
      matchedBy: 'auto'
    };
  }

  /**
   * Perform 2-way matching between PO and Invoice (when no receipt available)
   */
  async performTwoWayMatch(
    purchaseOrder: PurchaseOrder,
    invoice: InvoiceData,
    config: Partial<MatchConfiguration> = {}
  ): Promise<MatchResult> {
    const effectiveConfig = { ...this.defaultConfig, ...config };

    // Validate inputs
    this.validateTwoWayInputs(purchaseOrder, invoice);

    // Perform matching without receipt
    const itemMatches = await this.matchItemsTwoWay(purchaseOrder, invoice, effectiveConfig);
    const exceptions = this.identifyExceptions(itemMatches, effectiveConfig);

    // Calculate results
    const quantityMatch = this.determineQuantityMatch(itemMatches);
    const priceMatch = this.determinePriceMatch(itemMatches, effectiveConfig);
    const qualityMatch = 'no_receipt' as const;

    const overallStatus = this.determineOverallStatus(quantityMatch, priceMatch, qualityMatch, exceptions);
    const totalVariance = itemMatches.reduce((sum, match) => sum + Math.abs(match.varianceAmount), 0);
    const variancePercentage = purchaseOrder.totalAmount > 0 ? (totalVariance / purchaseOrder.totalAmount) * 100 : 0;

    const autoApprovalEligible = this.checkAutoApprovalEligibility(
      overallStatus,
      variancePercentage,
      exceptions,
      effectiveConfig
    );

    return {
      matchId: this.generateMatchId(),
      purchaseOrderId: purchaseOrder.id,
      invoiceId: invoice.invoiceId,
      matchType: 'two_way',
      overallStatus,
      quantityMatch,
      priceMatch,
      qualityMatch,
      itemMatches,
      totalVariance,
      variancePercentage,
      exceptionsCount: exceptions.length,
      autoApprovalEligible,
      matchedAt: new Date(),
      matchedBy: 'auto'
    };
  }

  /**
   * Resolve matching exceptions
   */
  async resolveException(
    exceptionId: string,
    resolution: {
      action: 'approve' | 'reject' | 'adjust' | 'escalate';
      notes?: string;
      adjustedAmount?: number;
      approvedBy: string;
    }
  ): Promise<void> {
    // In production, this would update the exception record in database
    console.log(`Resolving exception ${exceptionId} with action: ${resolution.action}`);
  }

  /**
   * Get matching statistics and KPIs
   */
  async getMatchingStatistics(
    dateRange: { from: Date; to: Date },
    filters?: { supplierId?: string; category?: string }
  ): Promise<{
    totalMatches: number;
    matchedCount: number;
    exceptionCount: number;
    autoApprovedCount: number;
    averageProcessingTime: number;
    topExceptionTypes: Array<{ type: string; count: number }>;
    supplierPerformance: Array<{ supplierId: string; matchRate: number; avgVariance: number }>;
  }> {
    // Mock statistics - in production, query from database
    return {
      totalMatches: 1250,
      matchedCount: 1100,
      exceptionCount: 150,
      autoApprovedCount: 950,
      averageProcessingTime: 2.3, // minutes
      topExceptionTypes: [
        { type: 'price_variance', count: 65 },
        { type: 'quantity_mismatch', count: 45 },
        { type: 'quality_issue', count: 25 },
        { type: 'missing_receipt', count: 15 }
      ],
      supplierPerformance: [
        { supplierId: 'supplier-a', matchRate: 98, avgVariance: 0.5 },
        { supplierId: 'supplier-b', matchRate: 95, avgVariance: 1.2 },
        { supplierId: 'supplier-c', matchRate: 92, avgVariance: 2.1 }
      ]
    };
  }

  // Private methods

  private validateMatchInputs(po: PurchaseOrder, receipt: Receipt, invoice: InvoiceData): void {
    if (po.id !== invoice.purchaseOrderId) {
      throw new Error('Invoice does not match purchase order');
    }

    if (receipt.header.purchaseOrderId !== po.id) {
      throw new Error('Receipt does not match purchase order');
    }

    if (receipt.header.supplierId !== invoice.supplierId) {
      throw new Error('Receipt and invoice supplier mismatch');
    }
  }

  private validateTwoWayInputs(po: PurchaseOrder, invoice: InvoiceData): void {
    if (po.id !== invoice.purchaseOrderId) {
      throw new Error('Invoice does not match purchase order');
    }
  }

  private async matchItems(
    po: PurchaseOrder,
    receipt: Receipt,
    invoice: InvoiceData,
    config: MatchConfiguration
  ): Promise<MatchResult['itemMatches']> {
    const matches: MatchResult['itemMatches'] = [];

    for (const poItem of po.items) {
      // Find corresponding receipt item
      const receiptItem = receipt.items.find(ri => ri.purchaseOrderItemId === poItem.id);

      // Find corresponding invoice item
      const invoiceItem = invoice.items.find(ii => ii.purchaseOrderItemId === poItem.id);

      if (!invoiceItem) {
        matches.push({
          purchaseOrderItemId: poItem.id,
          invoiceItemId: '',
          quantityMatch: false,
          priceMatch: false,
          qualityMatch: !!receiptItem,
          exceptions: ['Invoice item not found'],
          varianceAmount: poItem.lineTotal
        });
        continue;
      }

      const quantityMatch = this.checkQuantityMatch(poItem, receiptItem, invoiceItem, config);
      const priceMatch = this.checkPriceMatch(poItem, invoiceItem, config);
      const qualityMatch = this.checkQualityMatch(receiptItem);

      const exceptions = this.identifyItemExceptions(poItem, receiptItem, invoiceItem, config);
      const varianceAmount = this.calculateVarianceAmount(poItem, invoiceItem);

      matches.push({
        purchaseOrderItemId: poItem.id,
        ...(receiptItem?.id && { receiptItemId: receiptItem.id }),
        invoiceItemId: invoiceItem.purchaseOrderItemId,
        quantityMatch,
        priceMatch,
        qualityMatch,
        exceptions,
        varianceAmount
      });
    }

    return matches;
  }

  private async matchItemsTwoWay(
    po: PurchaseOrder,
    invoice: InvoiceData,
    config: MatchConfiguration
  ): Promise<MatchResult['itemMatches']> {
    const matches: MatchResult['itemMatches'] = [];

    for (const poItem of po.items) {
      const invoiceItem = invoice.items.find(ii => ii.purchaseOrderItemId === poItem.id);

      if (!invoiceItem) {
        matches.push({
          purchaseOrderItemId: poItem.id,
          invoiceItemId: '',
          quantityMatch: false,
          priceMatch: false,
          qualityMatch: false,
          exceptions: ['Invoice item not found'],
          varianceAmount: poItem.lineTotal
        });
        continue;
      }

      const quantityMatch = this.checkQuantityMatchTwoWay(poItem, invoiceItem, config);
      const priceMatch = this.checkPriceMatch(poItem, invoiceItem, config);
      const qualityMatch = false; // No receipt for quality check

      const exceptions = this.identifyItemExceptionsTwoWay(poItem, invoiceItem, config);
      const varianceAmount = this.calculateVarianceAmount(poItem, invoiceItem);

      matches.push({
        purchaseOrderItemId: poItem.id,
        invoiceItemId: invoiceItem.purchaseOrderItemId,
        quantityMatch,
        priceMatch,
        qualityMatch,
        exceptions,
        varianceAmount
      });
    }

    return matches;
  }

  private checkQuantityMatch(
    poItem: any,
    receiptItem: any,
    invoiceItem: any,
    config: MatchConfiguration
  ): boolean {
    if (!receiptItem) return false;

    const tolerance = config.tolerance.quantity / 100;
    const maxVariance = poItem.quantityOrdered * tolerance;

    const quantityVariance = Math.abs(invoiceItem.quantity - receiptItem.quantityReceived);
    return quantityVariance <= maxVariance;
  }

  private checkQuantityMatchTwoWay(
    poItem: any,
    invoiceItem: any,
    config: MatchConfiguration
  ): boolean {
    const tolerance = config.tolerance.quantity / 100;
    const maxVariance = poItem.quantityOrdered * tolerance;

    const quantityVariance = Math.abs(invoiceItem.quantity - poItem.quantityOrdered);
    return quantityVariance <= maxVariance;
  }

  private checkPriceMatch(poItem: any, invoiceItem: any, config: MatchConfiguration): boolean {
    const tolerance = config.tolerance.price / 100;
    const maxVariance = poItem.unitPrice * tolerance;

    const priceVariance = Math.abs(invoiceItem.unitPrice - poItem.unitPrice);
    return priceVariance <= maxVariance;
  }

  private checkQualityMatch(receiptItem: any): boolean {
    if (!receiptItem) return false;
    return receiptItem.inspectionStatus === 'passed' || receiptItem.inspectionStatus === 'conditional';
  }

  private identifyItemExceptions(
    poItem: any,
    receiptItem: any,
    invoiceItem: any,
    config: MatchConfiguration
  ): string[] {
    const exceptions: string[] = [];

    // Quantity checks
    if (!this.checkQuantityMatch(poItem, receiptItem, invoiceItem, config)) {
      exceptions.push('Quantity mismatch between PO, receipt, and invoice');
    }

    // Price checks
    if (!this.checkPriceMatch(poItem, invoiceItem, config)) {
      exceptions.push('Price variance exceeds tolerance');
    }

    // Quality checks
    if (!this.checkQualityMatch(receiptItem)) {
      exceptions.push('Quality inspection failed');
    }

    // Date checks
    if (receiptItem && Math.abs(invoiceItem.deliveryDate?.getTime() - receiptItem.deliveryDate?.getTime()) > config.tolerance.date * 24 * 60 * 60 * 1000) {
      exceptions.push('Delivery date variance');
    }

    return exceptions;
  }

  private identifyItemExceptionsTwoWay(
    poItem: any,
    invoiceItem: any,
    config: MatchConfiguration
  ): string[] {
    const exceptions: string[] = [];

    if (!this.checkQuantityMatchTwoWay(poItem, invoiceItem, config)) {
      exceptions.push('Quantity mismatch between PO and invoice');
    }

    if (!this.checkPriceMatch(poItem, invoiceItem, config)) {
      exceptions.push('Price variance exceeds tolerance');
    }

    exceptions.push('No receipt available for verification');

    return exceptions;
  }

  private identifyExceptions(
    itemMatches: MatchResult['itemMatches'],
    config: MatchConfiguration
  ): MatchException[] {
    const exceptions: MatchException[] = [];

    for (const match of itemMatches) {
      for (const exception of match.exceptions) {
        const severity = this.determineExceptionSeverity(exception, match.varianceAmount, config);

        exceptions.push({
          exceptionId: this.generateExceptionId(),
          matchId: '', // Would be set when creating match result
          exceptionType: this.mapExceptionType(exception),
          severity,
          description: exception,
          affectedItems: [match.purchaseOrderItemId],
          suggestedResolution: this.getSuggestedResolution(exception),
          requiresApproval: severity === 'high' || severity === 'critical',
          approverRole: this.getApproverForSeverity(severity, config),
          createdAt: new Date()
        });
      }
    }

    return exceptions;
  }

  private determineQuantityMatch(itemMatches: MatchResult['itemMatches']): MatchResult['quantityMatch'] {
    const allMatched = itemMatches.every(m => m.quantityMatch);
    const anyOverInvoice = itemMatches.some(m => !m.quantityMatch && m.exceptions.some(e => e.includes('over')));
    const anyUnderInvoice = itemMatches.some(m => !m.quantityMatch && m.exceptions.some(e => e.includes('under')));

    if (allMatched) return 'matched';
    if (anyOverInvoice) return 'over_invoice';
    if (anyUnderInvoice) return 'under_invoice';
    return 'no_receipt';
  }

  private determinePriceMatch(
    itemMatches: MatchResult['itemMatches'],
    config: MatchConfiguration
  ): MatchResult['priceMatch'] {
    const totalVariance = itemMatches.reduce((sum, m) => sum + Math.abs(m.varianceAmount), 0);
    const avgVariance = itemMatches.length > 0 ? totalVariance / itemMatches.length : 0;
    const tolerance = config.tolerance.price / 100;

    if (avgVariance <= tolerance) return 'matched';
    return 'price_variance';
  }

  private determineQualityMatch(receipt: Receipt): MatchResult['qualityMatch'] {
    const qualityMetrics = receipt.getQualityMetrics();
    if (qualityMetrics.overallPassRate >= 95) return 'matched';
    if (qualityMetrics.overallPassRate >= 80) return 'quality_issues';
    return 'quality_issues';
  }

  private determineOverallStatus(
    quantityMatch: MatchResult['quantityMatch'],
    priceMatch: MatchResult['priceMatch'],
    qualityMatch: MatchResult['qualityMatch'],
    exceptions: MatchException[]
  ): MatchResult['overallStatus'] {
    const hasCriticalExceptions = exceptions.some(e => e.severity === 'critical');
    const hasHighExceptions = exceptions.some(e => e.severity === 'high');

    if (hasCriticalExceptions) return 'exceptions';
    if (hasHighExceptions) return 'exceptions';

    const allMatched = quantityMatch === 'matched' &&
                      priceMatch === 'matched' &&
                      qualityMatch === 'matched';

    if (allMatched && exceptions.length === 0) return 'matched';
    if (exceptions.length > 0) return 'partial_match';
    return 'exceptions';
  }

  private checkAutoApprovalEligibility(
    overallStatus: MatchResult['overallStatus'],
    variancePercentage: number,
    exceptions: MatchException[],
    config: MatchConfiguration
  ): boolean {
    if (!config.autoApproval.enabled) return false;
    if (overallStatus === 'exceptions') return false;
    if (variancePercentage > config.autoApproval.maxVariancePercentage) return false;
    if (exceptions.some(e => e.requiresApproval)) return false;

    return true;
  }

  private calculateVarianceAmount(poItem: any, invoiceItem: any): number {
    const poAmount = poItem.quantityOrdered * poItem.unitPrice;
    const invoiceAmount = invoiceItem.quantity * invoiceItem.unitPrice;
    return invoiceAmount - poAmount;
  }

  private determineExceptionSeverity(
    exception: string,
    varianceAmount: number,
    config: MatchConfiguration
  ): 'low' | 'medium' | 'high' | 'critical' {
    if (exception.includes('quality') && varianceAmount > config.tolerance.price) {
      return 'critical';
    }
    if (exception.includes('price') && Math.abs(varianceAmount) > 1000) {
      return 'high';
    }
    if (exception.includes('quantity') || exception.includes('missing')) {
      return 'medium';
    }
    return 'low';
  }

  private mapExceptionType(exception: string): MatchException['exceptionType'] {
    if (exception.includes('quantity')) return 'quantity_mismatch';
    if (exception.includes('price')) return 'price_variance';
    if (exception.includes('quality')) return 'quality_issue';
    if (exception.includes('receipt')) return 'missing_receipt';
    if (exception.includes('tax')) return 'invalid_tax';
    return 'duplicate_invoice';
  }

  private getSuggestedResolution(exception: string): string {
    if (exception.includes('quantity')) return 'Verify delivered quantities and adjust invoice';
    if (exception.includes('price')) return 'Review pricing and approve variance or request correction';
    if (exception.includes('quality')) return 'Inspect goods and determine acceptance criteria';
    if (exception.includes('receipt')) return 'Obtain receipt documentation or perform 2-way match';
    return 'Review and resolve manually';
  }

  private getApproverForSeverity(severity: string, config: MatchConfiguration): string {
    switch (severity) {
      case 'low': return config.escalation.lowVarianceApprover;
      case 'medium': return config.escalation.mediumVarianceApprover;
      case 'high': return config.escalation.highVarianceApprover;
      case 'critical': return config.escalation.criticalVarianceApprover;
      default: return config.escalation.mediumVarianceApprover;
    }
  }

  private generateMatchId(): string {
    return `match_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateExceptionId(): string {
    return `exc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

export default ThreeWayMatchEngine;