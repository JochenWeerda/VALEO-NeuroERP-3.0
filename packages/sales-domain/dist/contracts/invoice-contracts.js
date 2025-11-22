"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InvoiceListResponseContractSchema = exports.InvoiceQueryContractSchema = exports.InvoiceResponseContractSchema = exports.UpdateInvoiceContractSchema = exports.CreateInvoiceContractSchema = exports.InvoiceStatusContractSchema = exports.InvoiceLineContractSchema = void 0;
var zod_1 = require("zod");
var entities_1 = require("../domain/entities");
// OpenAPI schema for Invoice Line
exports.InvoiceLineContractSchema = entities_1.InvoiceLineSchema.openapi({
    description: 'Invoice line item',
    example: {
        id: '550e8400-e29b-41d4-a716-446655440001',
        sku: 'PROD-001',
        name: 'Professional Service Package',
        description: 'Monthly consulting service',
        quantity: 2,
        unitPrice: 1500.00,
        discount: 10,
        totalNet: 2700.00,
        totalGross: 3213.00
    }
});
// OpenAPI schema for Invoice Status
exports.InvoiceStatusContractSchema = zod_1.z.enum([
    entities_1.InvoiceStatus.ISSUED,
    entities_1.InvoiceStatus.PAID,
    entities_1.InvoiceStatus.OVERDUE,
    entities_1.InvoiceStatus.CANCELLED
]).openapi({
    description: 'Invoice status',
    example: entities_1.InvoiceStatus.ISSUED
});
// OpenAPI schema for Create Invoice
exports.CreateInvoiceContractSchema = entities_1.CreateInvoiceInputSchema.openapi({
    description: 'Invoice creation data',
    example: {
        tenantId: 'tenant-001',
        customerId: '550e8400-e29b-41d4-a716-446655440000',
        orderId: '550e8400-e29b-41d4-a716-446655440003',
        invoiceNumber: 'INV-2024-001',
        lines: [
            {
                sku: 'PROD-001',
                name: 'Professional Service Package',
                description: 'Monthly consulting service',
                quantity: 2,
                unitPrice: 1500.00,
                discount: 10
            }
        ],
        dueDate: new Date('2024-02-15T00:00:00.000Z'),
        notes: 'Payment due within 14 days',
        taxRate: 19,
        currency: 'EUR'
    }
});
// OpenAPI schema for Update Invoice
exports.UpdateInvoiceContractSchema = entities_1.UpdateInvoiceInputSchema.openapi({
    description: 'Invoice update data',
    example: {
        status: entities_1.InvoiceStatus.PAID,
        notes: 'Payment received - thank you!'
    }
});
// OpenAPI schema for Invoice Response
exports.InvoiceResponseContractSchema = entities_1.InvoiceSchema.omit({ tenantId: true }).openapi({
    description: 'Invoice information',
    example: {
        id: '550e8400-e29b-41d4-a716-446655440004',
        customerId: '550e8400-e29b-41d4-a716-446655440000',
        orderId: '550e8400-e29b-41d4-a716-446655440003',
        invoiceNumber: 'INV-2024-001',
        lines: [
            {
                id: '550e8400-e29b-41d4-a716-446655440001',
                sku: 'PROD-001',
                name: 'Professional Service Package',
                description: 'Monthly consulting service',
                quantity: 2,
                unitPrice: 1500.00,
                discount: 10,
                totalNet: 2700.00,
                totalGross: 3213.00
            }
        ],
        subtotalNet: 2700.00,
        totalDiscount: 300.00,
        totalNet: 2700.00,
        totalGross: 3213.00,
        taxRate: 19,
        currency: 'EUR',
        dueDate: new Date('2024-02-15T00:00:00.000Z'),
        paidAt: new Date('2024-02-10T14:30:00.000Z'),
        notes: 'Payment due within 14 days',
        status: entities_1.InvoiceStatus.PAID,
        createdAt: new Date('2024-01-01T00:00:00.000Z'),
        updatedAt: new Date('2024-02-10T14:30:00.000Z'),
        version: 2
    }
});
// Query parameters for listing invoices
exports.InvoiceQueryContractSchema = zod_1.z.object({
    customerId: zod_1.z.string().uuid().optional(),
    orderId: zod_1.z.string().uuid().optional(),
    status: zod_1.z.enum([
        entities_1.InvoiceStatus.ISSUED,
        entities_1.InvoiceStatus.PAID,
        entities_1.InvoiceStatus.OVERDUE,
        entities_1.InvoiceStatus.CANCELLED
    ]).optional(),
    search: zod_1.z.string().optional().describe('Search term for invoice number'),
    dueDateFrom: zod_1.z.string().datetime().optional(),
    dueDateTo: zod_1.z.string().datetime().optional(),
    page: zod_1.z.string().transform(Number).optional().default('1'),
    pageSize: zod_1.z.string().transform(Number).optional().default('20')
}).openapi({
    description: 'Query parameters for invoice listing'
});
// Response schema for invoice list
exports.InvoiceListResponseContractSchema = zod_1.z.object({
    data: zod_1.z.array(exports.InvoiceResponseContractSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number()
    })
}).openapi({
    description: 'Paginated invoice list response'
});
