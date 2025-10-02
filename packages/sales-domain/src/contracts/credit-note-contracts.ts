import { z } from 'zod';
import {
  CreditNoteSchema,
  CreateCreditNoteInputSchema,
  UpdateCreditNoteInputSchema,
  CreditNoteLineSchema,
  CreditNoteStatus
} from '../domain/entities';

// OpenAPI schema for Credit Note Line
export const CreditNoteLineContractSchema = CreditNoteLineSchema.openapi({
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
export const CreditNoteStatusContractSchema = z.enum([
  CreditNoteStatus.ISSUED,
  CreditNoteStatus.SETTLED
]).openapi({
  description: 'Credit note status',
  example: CreditNoteStatus.ISSUED
});

// OpenAPI schema for Create Credit Note
export const CreateCreditNoteContractSchema = CreateCreditNoteInputSchema.openapi({
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
export const UpdateCreditNoteContractSchema = UpdateCreditNoteInputSchema.openapi({
  description: 'Credit note update data',
  example: {
    status: CreditNoteStatus.SETTLED,
    notes: 'Credit processed and applied to customer account'
  }
});

// OpenAPI schema for Credit Note Response
export const CreditNoteResponseContractSchema = CreditNoteSchema.omit({ tenantId: true }).openapi({
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
    status: CreditNoteStatus.SETTLED,
    settledAt: new Date('2024-02-12T10:00:00.000Z'),
    createdAt: new Date('2024-02-10T00:00:00.000Z'),
    updatedAt: new Date('2024-02-12T10:00:00.000Z'),
    version: 2
  }
});

// Query parameters for listing credit notes
export const CreditNoteQueryContractSchema = z.object({
  customerId: z.string().uuid().optional(),
  invoiceId: z.string().uuid().optional(),
  status: z.enum([
    CreditNoteStatus.ISSUED,
    CreditNoteStatus.SETTLED
  ]).optional(),
  search: z.string().optional().describe('Search term for credit note number'),
  page: z.string().transform(Number).optional().default('1'),
  pageSize: z.string().transform(Number).optional().default('20')
}).openapi({
  description: 'Query parameters for credit note listing'
});

// Response schema for credit note list
export const CreditNoteListResponseContractSchema = z.object({
  data: z.array(CreditNoteResponseContractSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number()
  })
}).openapi({
  description: 'Paginated credit note list response'
});