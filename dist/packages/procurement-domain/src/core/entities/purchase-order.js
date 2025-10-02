"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PurchaseOrder = exports.PurchaseOrderType = exports.PurchaseOrderStatus = void 0;
const crypto_1 = require("crypto");
var PurchaseOrderStatus;
(function (PurchaseOrderStatus) {
    PurchaseOrderStatus["DRAFT"] = "draft";
    PurchaseOrderStatus["PENDING_APPROVAL"] = "pending_approval";
    PurchaseOrderStatus["APPROVED"] = "approved";
    PurchaseOrderStatus["SENT_TO_SUPPLIER"] = "sent_to_supplier";
    PurchaseOrderStatus["CONFIRMED"] = "confirmed";
    PurchaseOrderStatus["PARTIALLY_RECEIVED"] = "partially_received";
    PurchaseOrderStatus["RECEIVED"] = "received";
    PurchaseOrderStatus["INVOICED"] = "invoiced";
    PurchaseOrderStatus["PAID"] = "paid";
    PurchaseOrderStatus["CANCELLED"] = "cancelled";
    PurchaseOrderStatus["CLOSED"] = "closed";
})(PurchaseOrderStatus || (exports.PurchaseOrderStatus = PurchaseOrderStatus = {}));
var PurchaseOrderType;
(function (PurchaseOrderType) {
    PurchaseOrderType["STANDARD"] = "standard";
    PurchaseOrderType["BLANKET"] = "blanket";
    PurchaseOrderType["CONTRACT"] = "contract";
    PurchaseOrderType["RELEASE"] = "release";
})(PurchaseOrderType || (exports.PurchaseOrderType = PurchaseOrderType = {}));
class PurchaseOrder {
    id;
    purchaseOrderNumber;
    revision;
    status;
    type;
    // Header Information
    header;
    // Items
    items;
    // Terms and Conditions
    terms;
    // Financial Summary
    subtotal;
    taxTotal;
    discountTotal;
    shippingTotal;
    totalAmount;
    currency;
    // Status Tracking
    approvalStatus;
    approvalDate;
    approvedBy;
    sentToSupplierDate;
    supplierConfirmationDate;
    supplierNotes;
    // Fulfillment Tracking
    totalOrdered;
    totalReceived;
    totalInvoiced;
    totalCancelled;
    // References and Links
    requisitionId;
    contractId;
    relatedDocuments; // Invoice IDs, receipt IDs, etc.
    // Audit and Compliance
    createdBy;
    lastModifiedBy;
    tenantId;
    // System Fields
    createdAt;
    updatedAt;
    version;
    constructor(props) {
        this.id = props.id || (0, crypto_1.randomUUID)();
        this.purchaseOrderNumber = props.purchaseOrderNumber || this.generatePurchaseOrderNumber();
        this.revision = 1;
        this.status = PurchaseOrderStatus.DRAFT;
        this.type = props.type || PurchaseOrderType.STANDARD;
        this.header = props.header;
        this.items = props.items;
        this.terms = props.terms;
        this.requisitionId = props.requisitionId || undefined;
        this.contractId = props.contractId || undefined;
        this.relatedDocuments = [];
        this.createdBy = props.createdBy;
        this.lastModifiedBy = props.createdBy;
        this.tenantId = props.tenantId;
        this.createdAt = new Date();
        this.updatedAt = new Date();
        this.version = 1;
        this.approvalStatus = 'pending';
        // Initialize financial summary
        this.calculateFinancialSummary();
        // Initialize fulfillment tracking
        this.initializeFulfillmentTracking();
    }
    // Business Logic Methods
    submitForApproval() {
        if (this.status !== PurchaseOrderStatus.DRAFT) {
            throw new Error('Only draft purchase orders can be submitted for approval');
        }
        if (this.items.length === 0) {
            throw new Error('Purchase order must have at least one item');
        }
        this.status = PurchaseOrderStatus.PENDING_APPROVAL;
        this.updatedAt = new Date();
        this.version++;
    }
    approve(approvedBy) {
        if (this.status !== PurchaseOrderStatus.PENDING_APPROVAL) {
            throw new Error('Purchase order must be pending approval');
        }
        this.approvalStatus = 'approved';
        this.approvalDate = new Date();
        this.approvedBy = approvedBy;
        this.status = PurchaseOrderStatus.APPROVED;
        this.updatedAt = new Date();
        this.version++;
    }
    reject(rejectionReason) {
        if (this.status !== PurchaseOrderStatus.PENDING_APPROVAL) {
            throw new Error('Purchase order must be pending approval');
        }
        this.approvalStatus = 'rejected';
        this.status = PurchaseOrderStatus.CANCELLED;
        this.updatedAt = new Date();
        this.version++;
    }
    sendToSupplier() {
        if (this.status !== PurchaseOrderStatus.APPROVED) {
            throw new Error('Purchase order must be approved before sending to supplier');
        }
        this.status = PurchaseOrderStatus.SENT_TO_SUPPLIER;
        this.sentToSupplierDate = new Date();
        this.updatedAt = new Date();
        this.version++;
    }
    confirmBySupplier(confirmationNotes) {
        if (this.status !== PurchaseOrderStatus.SENT_TO_SUPPLIER) {
            throw new Error('Purchase order must be sent to supplier before confirmation');
        }
        this.status = PurchaseOrderStatus.CONFIRMED;
        this.supplierConfirmationDate = new Date();
        this.supplierNotes = confirmationNotes || undefined;
        this.updatedAt = new Date();
        this.version++;
    }
    recordReceipt(receipts) {
        if (![PurchaseOrderStatus.CONFIRMED, PurchaseOrderStatus.PARTIALLY_RECEIVED].includes(this.status)) {
            throw new Error('Purchase order must be confirmed or partially received');
        }
        for (const receipt of receipts) {
            const item = this.items.find(i => i.id === receipt.itemId);
            if (!item) {
                throw new Error(`Item ${receipt.itemId} not found in purchase order`);
            }
            if (item.quantityReceived + receipt.quantityReceived > item.quantityOrdered) {
                throw new Error(`Cannot receive more than ordered quantity for item ${receipt.itemId}`);
            }
            item.quantityReceived += receipt.quantityReceived;
        }
        // Update related documents
        this.relatedDocuments.push(...receipts.map(r => r.receiptId));
        // Update status
        this.updateFulfillmentStatus();
        this.updatedAt = new Date();
        this.version++;
    }
    recordInvoice(invoiceId, invoicedItems) {
        for (const invoiceItem of invoicedItems) {
            const item = this.items.find(i => i.id === invoiceItem.itemId);
            if (!item) {
                throw new Error(`Item ${invoiceItem.itemId} not found in purchase order`);
            }
            if (item.quantityInvoiced + invoiceItem.quantityInvoiced > item.quantityOrdered) {
                throw new Error(`Cannot invoice more than ordered quantity for item ${invoiceItem.itemId}`);
            }
            item.quantityInvoiced += invoiceItem.quantityInvoiced;
        }
        // Update related documents
        this.relatedDocuments.push(invoiceId);
        // Update status
        if (this.totalInvoiced === this.totalOrdered) {
            this.status = PurchaseOrderStatus.INVOICED;
        }
        this.updatedAt = new Date();
        this.version++;
    }
    recordPayment(paymentId) {
        if (this.status !== PurchaseOrderStatus.INVOICED) {
            throw new Error('Purchase order must be invoiced before payment');
        }
        this.status = PurchaseOrderStatus.PAID;
        this.relatedDocuments.push(paymentId);
        this.updatedAt = new Date();
        this.version++;
    }
    close() {
        if (![PurchaseOrderStatus.RECEIVED, PurchaseOrderStatus.PAID].includes(this.status)) {
            throw new Error('Purchase order must be received or paid before closing');
        }
        this.status = PurchaseOrderStatus.CLOSED;
        this.updatedAt = new Date();
        this.version++;
    }
    cancel(reason) {
        if ([PurchaseOrderStatus.CLOSED, PurchaseOrderStatus.CANCELLED].includes(this.status)) {
            throw new Error('Cannot cancel closed or already cancelled purchase order');
        }
        // Cancel remaining quantities
        for (const item of this.items) {
            item.quantityCancelled = item.quantityOrdered - item.quantityReceived - item.quantityInvoiced;
        }
        this.status = PurchaseOrderStatus.CANCELLED;
        this.updateFulfillmentTracking();
        this.updatedAt = new Date();
        this.version++;
    }
    revise(revisionReason, revisedBy) {
        const revisedPO = new PurchaseOrder({
            purchaseOrderNumber: this.purchaseOrderNumber,
            header: { ...this.header },
            items: this.items.map(item => ({ ...item })),
            terms: { ...this.terms },
            ...(this.requisitionId && { requisitionId: this.requisitionId }),
            ...(this.contractId && { contractId: this.contractId }),
            createdBy: this.createdBy,
            tenantId: this.tenantId
        });
        revisedPO.revision = this.revision + 1;
        revisedPO.status = PurchaseOrderStatus.DRAFT;
        revisedPO.lastModifiedBy = revisedBy;
        return revisedPO;
    }
    // Analysis and Reporting Methods
    getFulfillmentStatus() {
        const fulfillmentRate = this.totalOrdered > 0 ? this.totalReceived / this.totalOrdered : 0;
        // Check if delivery is on time (simplified)
        const onTimeDelivery = this.items.every(item => item.quantityReceived >= item.quantityOrdered ||
            new Date() <= item.deliveryDate);
        return {
            totalOrdered: this.totalOrdered,
            totalReceived: this.totalReceived,
            totalInvoiced: this.totalInvoiced,
            totalCancelled: this.totalCancelled,
            fulfillmentRate,
            onTimeDelivery,
            qualityIssues: false // Would be determined by quality inspections
        };
    }
    getFinancialSummary() {
        const outstandingAmount = this.totalAmount - (this.totalInvoiced * (this.totalAmount / this.totalOrdered));
        return {
            subtotal: this.subtotal,
            taxTotal: this.taxTotal,
            discountTotal: this.discountTotal,
            shippingTotal: this.shippingTotal,
            totalAmount: this.totalAmount,
            currency: this.currency,
            outstandingAmount
        };
    }
    getDeliverySchedule() {
        return this.items.map(item => {
            let status = 'pending';
            if (item.quantityReceived === 0) {
                status = new Date() > item.deliveryDate ? 'overdue' : 'pending';
            }
            else if (item.quantityReceived < item.quantityOrdered) {
                status = 'partial';
            }
            else {
                status = 'complete';
            }
            return {
                itemId: item.id,
                itemName: item.name,
                deliveryDate: item.deliveryDate,
                quantityOrdered: item.quantityOrdered,
                quantityReceived: item.quantityReceived,
                status
            };
        });
    }
    isOverdue() {
        return this.items.some(item => item.quantityReceived < item.quantityOrdered &&
            new Date() > item.deliveryDate);
    }
    getDaysToDelivery() {
        if (this.items.length === 0)
            return 0;
        const earliestDelivery = this.items.reduce((earliest, item) => item.deliveryDate < earliest ? item.deliveryDate : earliest, this.items[0]?.deliveryDate || new Date());
        return Math.ceil((earliestDelivery.getTime() - Date.now()) / (24 * 60 * 60 * 1000));
    }
    // Validation Methods
    validateForApproval() {
        const errors = [];
        const warnings = [];
        // Basic validations
        if (!this.purchaseOrderNumber) {
            errors.push('Purchase order number is required');
        }
        if (this.items.length === 0) {
            errors.push('Purchase order must have at least one item');
        }
        // Header validations
        if (!this.header.buyer.contactEmail) {
            errors.push('Buyer contact email is required');
        }
        if (!this.header.supplier.contactEmail) {
            errors.push('Supplier contact email is required');
        }
        // Item validations
        for (let i = 0; i < this.items.length; i++) {
            const item = this.items[i];
            if (item && item.quantity <= 0) {
                errors.push(`Item ${i + 1}: Quantity must be greater than 0`);
            }
            if (item && item.unitPrice < 0) {
                errors.push(`Item ${i + 1}: Unit price cannot be negative`);
            }
            if (item && item.deliveryDate < new Date()) {
                warnings.push(`Item ${i + 1}: Delivery date is in the past`);
            }
            if (item && !item.accountCode) {
                warnings.push(`Item ${i + 1}: Account code not specified`);
            }
        }
        // Financial validations
        if (this.totalAmount <= 0) {
            errors.push('Total amount must be greater than 0');
        }
        // Contract validations
        if (this.contractId) {
            // Would validate against contract terms
            warnings.push('Contract terms validation not implemented');
        }
        return {
            isValid: errors.length === 0,
            errors,
            warnings
        };
    }
    // Private helper methods
    generatePurchaseOrderNumber() {
        const timestamp = Date.now().toString().slice(-6);
        const random = Math.random().toString(36).substring(2, 5).toUpperCase();
        return `PO-${timestamp}-${random}`;
    }
    calculateFinancialSummary() {
        this.subtotal = this.items.reduce((sum, item) => sum + item.lineTotal, 0);
        this.taxTotal = this.items.reduce((sum, item) => sum + (item.taxAmount || 0), 0);
        this.discountTotal = 0; // Would be calculated based on terms
        this.shippingTotal = 0; // Would be calculated based on shipping terms
        this.totalAmount = this.subtotal + this.taxTotal - this.discountTotal + this.shippingTotal;
        this.currency = this.items[0]?.currency || 'EUR';
    }
    initializeFulfillmentTracking() {
        this.totalOrdered = this.items.reduce((sum, item) => sum + item.quantityOrdered, 0);
        this.totalReceived = 0;
        this.totalInvoiced = 0;
        this.totalCancelled = 0;
    }
    updateFulfillmentStatus() {
        this.updateFulfillmentTracking();
        if (this.totalReceived === 0) {
            // Status unchanged
        }
        else if (this.totalReceived < this.totalOrdered) {
            this.status = PurchaseOrderStatus.PARTIALLY_RECEIVED;
        }
        else if (this.totalReceived === this.totalOrdered) {
            this.status = PurchaseOrderStatus.RECEIVED;
        }
    }
    updateFulfillmentTracking() {
        this.totalOrdered = this.items.reduce((sum, item) => sum + item.quantityOrdered, 0);
        this.totalReceived = this.items.reduce((sum, item) => sum + item.quantityReceived, 0);
        this.totalInvoiced = this.items.reduce((sum, item) => sum + item.quantityInvoiced, 0);
        this.totalCancelled = this.items.reduce((sum, item) => sum + item.quantityCancelled, 0);
    }
    updateTimestamp() {
        this.updatedAt = new Date();
        this.version++;
    }
}
exports.PurchaseOrder = PurchaseOrder;
