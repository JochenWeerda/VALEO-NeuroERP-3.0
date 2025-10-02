export type ReceiptId = string & {
    readonly __brand: 'ReceiptId';
};
export type ReceiptItemId = string & {
    readonly __brand: 'ReceiptItemId';
};
export declare enum ReceiptStatus {
    DRAFT = "draft",
    RECEIVED = "received",
    INSPECTED = "inspected",
    ACCEPTED = "accepted",
    REJECTED = "rejected",
    PARTIALLY_ACCEPTED = "partially_accepted",
    RETURNED = "returned",
    CANCELLED = "cancelled"
}
export declare enum InspectionStatus {
    PENDING = "pending",
    PASSED = "passed",
    FAILED = "failed",
    CONDITIONAL = "conditional"
}
export declare enum QualityIssueType {
    DAMAGED = "damaged",
    WRONG_ITEM = "wrong_item",
    SHORT_QUANTITY = "short_quantity",
    POOR_QUALITY = "poor_quality",
    MISSING_DOCUMENTATION = "missing_documentation",
    EXPIRED = "expired",
    CONTAMINATED = "contaminated",
    OTHER = "other"
}
export interface ReceiptItem {
    id: ReceiptItemId;
    purchaseOrderItemId: string;
    sku: string;
    name: string;
    description: string;
    quantityOrdered: number;
    quantityReceived: number;
    quantityAccepted: number;
    quantityRejected: number;
    quantityReturned: number;
    inspectionStatus: InspectionStatus;
    qualityIssues: Array<{
        type: QualityIssueType;
        severity: 'minor' | 'major' | 'critical';
        description: string;
        quantityAffected: number;
    }>;
    packagingIntact: boolean;
    documentationComplete: boolean;
    serialNumbers?: string[];
    batchNumbers?: string[];
    expiryDates?: Date[];
    receivedLocation: string;
    storageLocation?: string;
    handlingInstructions?: string;
    unitPrice: number;
    lineTotal: number;
    currency: string;
    receiverNotes?: string;
    inspectorNotes?: string;
    supplierNotes?: string;
}
export interface ReceiptHeader {
    receiptNumber: string;
    receiptDate: Date;
    receivedBy: string;
    receiverName: string;
    supplierId: string;
    supplierName: string;
    supplierDeliveryNote?: string;
    carrierName?: string;
    carrierTrackingNumber?: string;
    purchaseOrderId: string;
    purchaseOrderNumber: string;
    receivingLocation: string;
    locationName: string;
    inspectedBy?: string;
    inspectedAt?: Date;
    inspectionMethod: 'visual' | 'detailed' | 'sampled' | 'automated';
}
export interface QualityInspection {
    inspectionId: string;
    itemId: ReceiptItemId;
    inspectorId: string;
    inspectorName: string;
    inspectionDate: Date;
    inspectionMethod: 'aql' | 'full' | 'automated' | 'supplier_certified';
    sampleSize?: number;
    acceptanceLevel?: number;
    rejectionLevel?: number;
    overallResult: InspectionStatus;
    passRate: number;
    findings: Array<{
        criterion: string;
        result: 'pass' | 'fail';
        severity: 'minor' | 'major' | 'critical';
        notes?: string;
    }>;
    actions: Array<{
        action: string;
        responsible: string;
        dueDate: Date;
        priority: 'low' | 'medium' | 'high';
    }>;
    photos?: string[];
    certificates?: string[];
    testResults?: Record<string, any>;
}
export declare class Receipt {
    readonly id: ReceiptId;
    receiptNumber: string;
    status: ReceiptStatus;
    header: ReceiptHeader;
    items: ReceiptItem[];
    inspections: QualityInspection[];
    totalItems: number;
    totalQuantityReceived: number;
    totalQuantityAccepted: number;
    totalQuantityRejected: number;
    totalQuantityReturned: number;
    totalValue: number;
    currency: string;
    processingNotes?: string;
    urgent: boolean;
    requiresFollowUp: boolean;
    relatedDocuments: string[];
    readonly tenantId: string;
    readonly createdAt: Date;
    updatedAt: Date;
    createdBy: string;
    lastModifiedBy: string;
    constructor(props: {
        id?: ReceiptId;
        receiptNumber?: string;
        header: ReceiptHeader;
        items: ReceiptItem[];
        tenantId: string;
        createdBy: string;
        urgent?: boolean;
    });
    markAsReceived(): void;
    startInspection(inspectionMethod?: 'visual' | 'detailed' | 'sampled' | 'automated'): void;
    completeInspection(inspection: QualityInspection): void;
    acceptReceipt(notes?: string): void;
    rejectReceipt(reason: string, returnItems?: Array<{
        itemId: ReceiptItemId;
        quantity: number;
    }>): void;
    partiallyAccept(acceptances: Array<{
        itemId: ReceiptItemId;
        quantityAccepted: number;
        notes?: string;
    }>): void;
    returnItems(returnItems: Array<{
        itemId: ReceiptItemId;
        quantity: number;
        reason: string;
    }>): void;
    cancel(reason?: string): void;
    getQualityMetrics(): {
        overallPassRate: number;
        criticalIssues: number;
        majorIssues: number;
        minorIssues: number;
        itemsInspected: number;
        itemsPassed: number;
        itemsFailed: number;
    };
    getReceiptSummary(): {
        totalItems: number;
        totalQuantityReceived: number;
        totalQuantityAccepted: number;
        totalQuantityRejected: number;
        totalValue: number;
        currency: string;
        hasQualityIssues: boolean;
        requiresAction: boolean;
    };
    getProcessingTime(): {
        timeToReceive: number;
        timeToInspect: number;
        timeToComplete: number;
        isDelayed: boolean;
    };
    validateForCompletion(): {
        isValid: boolean;
        errors: string[];
        warnings: string[];
    };
    private generateReceiptNumber;
    private calculateSummary;
    private updateStatus;
    updateTimestamp(): void;
}
//# sourceMappingURL=receipt.d.ts.map