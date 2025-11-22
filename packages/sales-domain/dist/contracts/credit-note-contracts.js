"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CreditNoteListResponseContractSchema = exports.CreditNoteQueryContractSchema = exports.CreditNoteResponseContractSchema = exports.UpdateCreditNoteContractSchema = exports.CreateCreditNoteContractSchema = exports.CreditNoteStatusContractSchema = exports.CreditNoteLineContractSchema = void 0;
var zod_1 = require("zod");
var entities_1 = require("../domain/entities");
// OpenAPI schema for Credit Note Line
exports.CreditNoteLineContractSchema = entities_1.CreditNoteLineSchema.openapi({
    description: 'Credit note line item',
    example: {
        id: '550e8400-e29b-41d4-a716-446655440001',
        sku: 'PROD-001',
        name: 'Professional Service Package',
        description: 'Monthly consulting service',
        quantity: 1,
        unitPrice: 1500.00,
        discount: 10,
        totalNet: 1350.00,
        totalGross: 1606.50
    }
});
// OpenAPI schema for Credit Note Status
exports.CreditNoteStatusContractSchema = zod_1.z.enum([
    entities_1.CreditNoteStatus.ISSUED,
    entities_1.CreditNoteStatus.SETTLED
]).openapi({
    description: 'Credit note status',
    example: entities_1.CreditNoteStatus.ISSUED
});
// OpenAPI schema for Create Credit Note
exports.CreateCreditNoteContractSchema = entities_1.CreateCreditNoteInputSchema.openapi({
    description: 'Credit note creation data',
    example: {
        tenantId: 'tenant-001',
        customerId: '550e8400-e29b-41d4-a716-446655440000',
        invoiceId: '550e8400-e29b-41d4-a716-446655440004',
        creditNumber: 'CN-2024-001',
        lines: [
            {
                sku: 'PROD-001',
                name: 'Professional Service Package',
                description: 'Monthly consulting service - partial refund',
                quantity: 1,
                unitPrice: 1500.00,
                discount: 10
            }
        ],
        reason: 'Service not delivered as agreed',
        notes: 'Customer dissatisfaction with delivery timeline',
        taxRate: 19,
        currency: 'EUR'
    }
});
// OpenAPI schema for Update Credit Note
exports.UpdateCreditNoteContractSchema = entities_1.UpdateCreditNoteInputSchema.openapi({
    description: 'Credit note update data',
    example: {
        status: entities_1.CreditNoteStatus.SETTLED,
        notes: 'Credit processed and applied to customer account'
    }
});
// OpenAPI schema for Credit Note Response
exports.CreditNoteResponseContractSchema = entities_1.CreditNoteSchema.omit({ tenantId: true }).openapi({
    description: 'Credit note information',
    example: {
        id: '550e8400-e29b-41d4-a716-446655440005',
        customerId: '550e8400-e29b-41d4-a716-446655440000',
        invoiceId: '550e8400-e29b-41d4-a716-446655440004',
        creditNumber: 'CN-2024-001',
        lines: [
            {
                id: '550e8400-e29b-41d4-a716-446655440001',
                sku: 'PROD-001',
                name: 'Professional Service Package',
                description: 'Monthly consulting service - partial refund',
                quantity: 1,
                unitPrice: 1500.00,
                discount: 10,
                totalNet: 1350.00,
                totalGross: 1606.50
            }
        ],
        subtotalNet: 1350.00,
        totalDiscount: 150.00,
        totalNet: 1350.00,
        totalGross: 1606.50,
        taxRate: 19,
        currency: 'EUR',
        reason: 'Service not delivered as agreed',
        notes: 'Customer dissatisfaction with delivery timeline',
        status: entities_1.CreditNoteStatus.SETTLED,
        settledAt: new Date('2024-02-12T10:00:00.000Z'),
        createdAt: new Date('2024-02-10T00:00:00.000Z'),
        updatedAt: new Date('2024-02-12T10:00:00.000Z'),
        version: 2
    }
});
// Query parameters for listing credit notes
exports.CreditNoteQueryContractSchema = zod_1.z.object({
    customerId: zod_1.z.string().uuid().optional(),
    invoiceId: zod_1.z.string().uuid().optional(),
    status: zod_1.z.enum([
        entities_1.CreditNoteStatus.ISSUED,
        entities_1.CreditNoteStatus.SETTLED
    ]).optional(),
    search: zod_1.z.string().optional().describe('Search term for credit note number'),
    page: zod_1.z.string().transform(Number).optional().default('1'),
    pageSize: zod_1.z.string().transform(Number).optional().default('20')
}).openapi({
    description: 'Query parameters for credit note listing'
});
// Response schema for credit note list
exports.CreditNoteListResponseContractSchema = zod_1.z.object({
    data: zod_1.z.array(exports.CreditNoteResponseContractSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number()
    })
}).openapi({
    description: 'Paginated credit note list response'
});
