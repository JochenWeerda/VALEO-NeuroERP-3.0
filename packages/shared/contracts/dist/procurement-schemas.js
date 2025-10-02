"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RFQ = exports.PurchaseRequisition = exports.PurchaseOrder = exports.Supplier = void 0;
const zod_1 = require("zod");
const shared_schemas_1 = require("./shared-schemas");
// Procurement-specific schemas
// Supplier
exports.Supplier = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Basic information
    name: zod_1.z.string().min(1),
    code: zod_1.z.string().optional(),
    // Contact details
    contactInfo: shared_schemas_1.ContactInfo,
    // Business details
    taxId: zod_1.z.string().optional(),
    paymentTerms: zod_1.z.number().int().positive().default(30), // Days
    // Status
    status: zod_1.z.enum(['ACTIVE', 'INACTIVE', 'SUSPENDED']),
    isPreferred: zod_1.z.boolean().default(false),
    // Metadata
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime()
});
// Purchase order
exports.PurchaseOrder = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Order identification
    orderNumber: zod_1.z.string(),
    supplierId: shared_schemas_1.UUID,
    // Order details
    orderDate: zod_1.z.string().datetime(),
    requestedDeliveryDate: zod_1.z.string().datetime().optional(),
    actualDeliveryDate: zod_1.z.string().datetime().optional(),
    // Financial details
    subtotal: shared_schemas_1.Money,
    taxAmount: shared_schemas_1.Money,
    total: shared_schemas_1.Money,
    currency: zod_1.z.string().default('EUR'),
    // Status
    status: zod_1.z.enum(['DRAFT', 'SENT', 'CONFIRMED', 'PARTIALLY_RECEIVED', 'RECEIVED', 'CANCELLED']),
    // Line items
    lineItems: zod_1.z.array(zod_1.z.object({
        id: shared_schemas_1.UUID,
        itemId: zod_1.z.string(),
        description: zod_1.z.string(),
        quantity: zod_1.z.number().positive(),
        unitPrice: shared_schemas_1.Money,
        totalPrice: shared_schemas_1.Money,
        receivedQuantity: zod_1.z.number().nonnegative().default(0)
    })),
    // Metadata
    createdBy: zod_1.z.string(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime()
});
// Purchase requisition
exports.PurchaseRequisition = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Request details
    title: zod_1.z.string(),
    description: zod_1.z.string(),
    requestedBy: zod_1.z.string(),
    // Urgency
    priority: zod_1.z.enum(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
    requiredBy: zod_1.z.string().datetime(),
    // Financial
    estimatedCost: shared_schemas_1.Money,
    budgetCode: zod_1.z.string().optional(),
    // Status
    status: zod_1.z.enum(['DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', 'ORDERED']),
    // Items
    items: zod_1.z.array(zod_1.z.object({
        description: zod_1.z.string(),
        quantity: zod_1.z.number().positive(),
        estimatedUnitPrice: shared_schemas_1.Money,
        category: zod_1.z.string().optional()
    })),
    // Approval workflow
    approvals: zod_1.z.array(zod_1.z.object({
        approverId: zod_1.z.string(),
        status: zod_1.z.enum(['PENDING', 'APPROVED', 'REJECTED']),
        comments: zod_1.z.string().optional(),
        approvedAt: zod_1.z.string().datetime().optional()
    })).default([]),
    // Metadata
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime()
});
// RFQ (Request for Quotation)
exports.RFQ = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // RFQ details
    title: zod_1.z.string(),
    description: zod_1.z.string(),
    // Items
    items: zod_1.z.array(zod_1.z.object({
        id: shared_schemas_1.UUID,
        description: zod_1.z.string(),
        quantity: zod_1.z.number().positive(),
        unitOfMeasure: zod_1.z.string(),
        specifications: zod_1.z.record(zod_1.z.any()).optional()
    })),
    // Suppliers
    supplierIds: zod_1.z.array(shared_schemas_1.UUID),
    // Timeline
    responseDeadline: zod_1.z.string().datetime(),
    validUntil: zod_1.z.string().datetime(),
    // Status
    status: zod_1.z.enum(['DRAFT', 'PUBLISHED', 'CLOSED', 'CANCELLED']),
    // Responses
    responses: zod_1.z.array(zod_1.z.object({
        supplierId: shared_schemas_1.UUID,
        submittedAt: zod_1.z.string().datetime(),
        totalAmount: shared_schemas_1.Money,
        lineItems: zod_1.z.array(zod_1.z.object({
            itemId: shared_schemas_1.UUID,
            unitPrice: shared_schemas_1.Money,
            totalPrice: shared_schemas_1.Money,
            leadTimeDays: zod_1.z.number().int().positive()
        })),
        notes: zod_1.z.string().optional()
    })).default([]),
    // Metadata
    createdBy: zod_1.z.string(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime()
});
//# sourceMappingURL=procurement-schemas.js.map