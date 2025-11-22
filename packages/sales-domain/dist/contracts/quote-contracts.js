"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.QuoteListResponseContractSchema = exports.QuoteQueryContractSchema = exports.QuoteResponseContractSchema = exports.UpdateQuoteContractSchema = exports.CreateQuoteContractSchema = exports.QuoteStatusContractSchema = exports.QuoteLineContractSchema = void 0;
var zod_1 = require("zod");
var zod_openapi_1 = require("zod-openapi");
(0, zod_openapi_1.extendZodWithOpenApi)(zod_1.z);
var entities_1 = require("../domain/entities");
// OpenAPI schema for Quote Line
exports.QuoteLineContractSchema = entities_1.QuoteLineSchema.openapi({
    description: 'Quote line item',
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
// OpenAPI schema for Quote Status
exports.QuoteStatusContractSchema = zod_1.z.enum([
    entities_1.QuoteStatus.DRAFT,
    entities_1.QuoteStatus.SENT,
    entities_1.QuoteStatus.ACCEPTED,
    entities_1.QuoteStatus.REJECTED,
    entities_1.QuoteStatus.EXPIRED
]).openapi({
    description: 'Quote status',
    example: entities_1.QuoteStatus.SENT
});
// OpenAPI schema for Create Quote
exports.CreateQuoteContractSchema = entities_1.CreateQuoteInputSchema.openapi({
    description: 'Quote creation data',
    example: {
        status: entities_1.QuoteStatus.DRAFT,
        tenantId: '550e8400-e29b-41d4-a716-446655440000',
        customerId: '550e8400-e29b-41d4-a716-446655440000',
        quoteNumber: 'QT-2024-001',
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
        taxRate: 19,
        currency: 'EUR',
        validUntil: new Date('2024-12-31T23:59:59.000Z'),
        notes: 'This quote is valid for 30 days'
    }
});
// OpenAPI schema for Update Quote
exports.UpdateQuoteContractSchema = entities_1.UpdateQuoteInputSchema.openapi({
    description: 'Quote update data',
    example: {
        status: entities_1.QuoteStatus.SENT,
        notes: 'Updated quote with new terms'
    }
});
// OpenAPI schema for Quote Response
exports.QuoteResponseContractSchema = entities_1.QuoteSchema.omit({ tenantId: true }).openapi({
    description: 'Quote information',
    example: {
        id: '550e8400-e29b-41d4-a716-446655440002',
        customerId: '550e8400-e29b-41d4-a716-446655440000',
        quoteNumber: 'QT-2024-001',
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
        validUntil: new Date('2024-12-31T23:59:59.000Z'),
        notes: 'This quote is valid for 30 days',
        status: entities_1.QuoteStatus.SENT,
        createdAt: new Date('2024-01-01T00:00:00.000Z'),
        updatedAt: new Date('2024-01-01T00:00:00.000Z'),
        version: 1
    }
});
// Query parameters for listing quotes
exports.QuoteQueryContractSchema = zod_1.z.object({
    customerId: zod_1.z.string().uuid().optional(),
    status: zod_1.z.enum([
        entities_1.QuoteStatus.DRAFT,
        entities_1.QuoteStatus.SENT,
        entities_1.QuoteStatus.ACCEPTED,
        entities_1.QuoteStatus.REJECTED,
        entities_1.QuoteStatus.EXPIRED
    ]).optional(),
    search: zod_1.z.string().optional().describe('Search term for quote number or customer'),
    validUntilFrom: zod_1.z.string().datetime().optional(),
    validUntilTo: zod_1.z.string().datetime().optional(),
    page: zod_1.z.string().transform(Number).optional().default('1'),
    pageSize: zod_1.z.string().transform(Number).optional().default('20')
}).openapi({
    description: 'Query parameters for quote listing'
});
// Response schema for quote list
exports.QuoteListResponseContractSchema = zod_1.z.object({
    data: zod_1.z.array(exports.QuoteResponseContractSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number()
    })
}).openapi({
    description: 'Paginated quote list response'
});
