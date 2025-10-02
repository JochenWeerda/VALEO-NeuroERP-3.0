import { z } from 'zod';
import { extendZodWithOpenApi } from 'zod-openapi';

extendZodWithOpenApi(z);
import {
  QuoteSchema,
  CreateQuoteInputSchema,
  UpdateQuoteInputSchema,
  QuoteLineSchema,
  QuoteStatus
} from '../domain/entities';

// OpenAPI schema for Quote Line
export const QuoteLineContractSchema = QuoteLineSchema.openapi({
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
export const QuoteStatusContractSchema = z.enum([
  QuoteStatus.DRAFT,
  QuoteStatus.SENT,
  QuoteStatus.ACCEPTED,
  QuoteStatus.REJECTED,
  QuoteStatus.EXPIRED
]).openapi({
  description: 'Quote status',
  example: QuoteStatus.SENT
});

// OpenAPI schema for Create Quote
export const CreateQuoteContractSchema = CreateQuoteInputSchema.openapi({
  description: 'Quote creation data',
  example: {
    status: QuoteStatus.DRAFT,
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
export const UpdateQuoteContractSchema = UpdateQuoteInputSchema.openapi({
  description: 'Quote update data',
  example: {
    status: QuoteStatus.SENT,
    notes: 'Updated quote with new terms'
  }
});

// OpenAPI schema for Quote Response
export const QuoteResponseContractSchema = QuoteSchema.omit({ tenantId: true }).openapi({
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
    status: QuoteStatus.SENT,
    createdAt: new Date('2024-01-01T00:00:00.000Z'),
    updatedAt: new Date('2024-01-01T00:00:00.000Z'),
    version: 1
  }
});

// Query parameters for listing quotes
export const QuoteQueryContractSchema = z.object({
  customerId: z.string().uuid().optional(),
  status: z.enum([
    QuoteStatus.DRAFT,
    QuoteStatus.SENT,
    QuoteStatus.ACCEPTED,
    QuoteStatus.REJECTED,
    QuoteStatus.EXPIRED
  ]).optional(),
  search: z.string().optional().describe('Search term for quote number or customer'),
  validUntilFrom: z.string().datetime().optional(),
  validUntilTo: z.string().datetime().optional(),
  page: z.string().transform(Number).optional().default('1'),
  pageSize: z.string().transform(Number).optional().default('20')
}).openapi({
  description: 'Query parameters for quote listing'
});

// Response schema for quote list
export const QuoteListResponseContractSchema = z.object({
  data: z.array(QuoteResponseContractSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number()
  })
}).openapi({
  description: 'Paginated quote list response'
});