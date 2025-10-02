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
    quantityMatch: 'matched' | 'over_invoice' | 'under_invoice' | 'no_receipt';
    priceMatch: 'matched' | 'price_variance' | 'no_match';
    qualityMatch: 'matched' | 'quality_issues' | 'no_receipt';
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
    totalVariance: number;
    variancePercentage: number;
    exceptionsCount: number;
    autoApprovalEligible: boolean;
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
        quantity: number;
        price: number;
        date: number;
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
export declare class ThreeWayMatchEngine {
    private readonly defaultConfig;
    /**
     * Perform 3-way matching between PO, Receipt, and Invoice
     */
    performThreeWayMatch(purchaseOrder: PurchaseOrder, receipt: Receipt, invoice: InvoiceData, config?: Partial<MatchConfiguration>): Promise<MatchResult>;
    /**
     * Perform 2-way matching between PO and Invoice (when no receipt available)
     */
    performTwoWayMatch(purchaseOrder: PurchaseOrder, invoice: InvoiceData, config?: Partial<MatchConfiguration>): Promise<MatchResult>;
    /**
     * Resolve matching exceptions
     */
    resolveException(exceptionId: string, resolution: {
        action: 'approve' | 'reject' | 'adjust' | 'escalate';
        notes?: string;
        adjustedAmount?: number;
        approvedBy: string;
    }): Promise<void>;
    /**
     * Get matching statistics and KPIs
     */
    getMatchingStatistics(dateRange: {
        from: Date;
        to: Date;
    }, filters?: {
        supplierId?: string;
        category?: string;
    }): Promise<{
        totalMatches: number;
        matchedCount: number;
        exceptionCount: number;
        autoApprovedCount: number;
        averageProcessingTime: number;
        topExceptionTypes: Array<{
            type: string;
            count: number;
        }>;
        supplierPerformance: Array<{
            supplierId: string;
            matchRate: number;
            avgVariance: number;
        }>;
    }>;
    private validateMatchInputs;
    private validateTwoWayInputs;
    private matchItems;
    private matchItemsTwoWay;
    private checkQuantityMatch;
    private checkQuantityMatchTwoWay;
    private checkPriceMatch;
    private checkQualityMatch;
    private identifyItemExceptions;
    private identifyItemExceptionsTwoWay;
    private identifyExceptions;
    private determineQuantityMatch;
    private determinePriceMatch;
    private determineQualityMatch;
    private determineOverallStatus;
    private checkAutoApprovalEligibility;
    private calculateVarianceAmount;
    private determineExceptionSeverity;
    private mapExceptionType;
    private getSuggestedResolution;
    private getApproverForSeverity;
    private generateMatchId;
    private generateExceptionId;
}
export default ThreeWayMatchEngine;
//# sourceMappingURL=three-way-match-engine.d.ts.map