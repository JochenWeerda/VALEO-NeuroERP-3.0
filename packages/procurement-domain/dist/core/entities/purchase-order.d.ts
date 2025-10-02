export type PurchaseOrderId = string & {
    readonly __brand: 'PurchaseOrderId';
};
export type PurchaseOrderItemId = string & {
    readonly __brand: 'PurchaseOrderItemId';
};
export declare enum PurchaseOrderStatus {
    DRAFT = "draft",
    PENDING_APPROVAL = "pending_approval",
    APPROVED = "approved",
    SENT_TO_SUPPLIER = "sent_to_supplier",
    CONFIRMED = "confirmed",
    PARTIALLY_RECEIVED = "partially_received",
    RECEIVED = "received",
    INVOICED = "invoiced",
    PAID = "paid",
    CANCELLED = "cancelled",
    CLOSED = "closed"
}
export declare enum PurchaseOrderType {
    STANDARD = "standard",
    BLANKET = "blanket",
    CONTRACT = "contract",
    RELEASE = "release"
}
export interface PurchaseOrderItem {
    id: PurchaseOrderItemId;
    requisitionItemId?: string;
    catalogItemId?: string;
    lineNumber: number;
    sku: string;
    name: string;
    description: string;
    category: string;
    quantity: number;
    unitOfMeasure: string;
    unitPrice: number;
    lineTotal: number;
    currency: string;
    deliveryDate: Date;
    shipToLocation: string;
    taxCode?: string;
    taxRate?: number;
    taxAmount?: number;
    accountCode?: string;
    costCenter?: string;
    project?: string;
    quantityOrdered: number;
    quantityReceived: number;
    quantityInvoiced: number;
    quantityCancelled: number;
    specifications: Record<string, any>;
    notes?: string;
}
export interface PurchaseOrderTerms {
    paymentTerms: string;
    paymentMethod: string;
    shippingTerms: string;
    deliveryTerms: string;
    warrantyTerms?: string;
    returnPolicy?: string;
    insurance?: string;
    packaging?: string;
    discountTerms?: string;
    penaltyTerms?: string;
    bonusTerms?: string;
    governingLaw?: string;
    disputeResolution?: string;
}
export interface PurchaseOrderHeader {
    purchaseOrderNumber: string;
    revision: number;
    orderDate: Date;
    requiredDeliveryDate: Date;
    buyer: {
        companyId: string;
        companyName: string;
        contactName: string;
        contactEmail: string;
        contactPhone?: string;
        address: {
            street: string;
            city: string;
            state: string;
            postalCode: string;
            country: string;
        };
    };
    supplier: {
        supplierId: string;
        supplierName: string;
        contactName: string;
        contactEmail: string;
        contactPhone?: string;
        address: {
            street: string;
            city: string;
            state: string;
            postalCode: string;
            country: string;
        };
    };
    requisitionId?: string;
    contractId?: string;
    projectId?: string;
    costCenter?: string;
    shipTo: {
        locationId: string;
        locationName: string;
        address: {
            street: string;
            city: string;
            state: string;
            postalCode: string;
            country: string;
        };
        contactName?: string;
        contactPhone?: string;
    };
    billTo: {
        locationId: string;
        locationName: string;
        address: {
            street: string;
            city: string;
            state: string;
            postalCode: string;
            country: string;
        };
    };
}
export declare class PurchaseOrder {
    readonly id: PurchaseOrderId;
    purchaseOrderNumber: string;
    revision: number;
    status: PurchaseOrderStatus;
    type: PurchaseOrderType;
    header: PurchaseOrderHeader;
    items: PurchaseOrderItem[];
    terms: PurchaseOrderTerms;
    subtotal: number;
    taxTotal: number;
    discountTotal: number;
    shippingTotal: number;
    totalAmount: number;
    currency: string;
    approvalStatus: 'pending' | 'approved' | 'rejected';
    approvalDate?: Date;
    approvedBy?: string;
    sentToSupplierDate?: Date;
    supplierConfirmationDate?: Date;
    supplierNotes?: string;
    totalOrdered: number;
    totalReceived: number;
    totalInvoiced: number;
    totalCancelled: number;
    requisitionId?: string;
    contractId?: string;
    relatedDocuments: string[];
    createdBy: string;
    lastModifiedBy: string;
    readonly tenantId: string;
    readonly createdAt: Date;
    updatedAt: Date;
    version: number;
    constructor(props: {
        id?: PurchaseOrderId;
        purchaseOrderNumber?: string;
        type?: PurchaseOrderType;
        header: PurchaseOrderHeader;
        items: PurchaseOrderItem[];
        terms: PurchaseOrderTerms;
        requisitionId?: string;
        contractId?: string;
        createdBy: string;
        tenantId: string;
    });
    submitForApproval(): void;
    approve(approvedBy: string): void;
    reject(rejectionReason?: string): void;
    sendToSupplier(): void;
    confirmBySupplier(confirmationNotes?: string): void;
    recordReceipt(receipts: Array<{
        itemId: PurchaseOrderItemId;
        quantityReceived: number;
        receiptDate: Date;
        receiptId: string;
    }>): void;
    recordInvoice(invoiceId: string, invoicedItems: Array<{
        itemId: PurchaseOrderItemId;
        quantityInvoiced: number;
    }>): void;
    recordPayment(paymentId: string): void;
    close(): void;
    cancel(reason?: string): void;
    revise(revisionReason: string, revisedBy: string): PurchaseOrder;
    getFulfillmentStatus(): {
        totalOrdered: number;
        totalReceived: number;
        totalInvoiced: number;
        totalCancelled: number;
        fulfillmentRate: number;
        onTimeDelivery: boolean;
        qualityIssues: boolean;
    };
    getFinancialSummary(): {
        subtotal: number;
        taxTotal: number;
        discountTotal: number;
        shippingTotal: number;
        totalAmount: number;
        currency: string;
        outstandingAmount: number;
    };
    getDeliverySchedule(): Array<{
        itemId: string;
        itemName: string;
        deliveryDate: Date;
        quantityOrdered: number;
        quantityReceived: number;
        status: 'pending' | 'partial' | 'complete' | 'overdue';
    }>;
    isOverdue(): boolean;
    getDaysToDelivery(): number;
    validateForApproval(): {
        isValid: boolean;
        errors: string[];
        warnings: string[];
    };
    private generatePurchaseOrderNumber;
    private calculateFinancialSummary;
    private initializeFulfillmentTracking;
    private updateFulfillmentStatus;
    private updateFulfillmentTracking;
    updateTimestamp(): void;
}
//# sourceMappingURL=purchase-order.d.ts.map