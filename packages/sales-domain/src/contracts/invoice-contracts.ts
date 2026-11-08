import { z } from 'zod';
import {
  CreateInvoiceInputSchema,
  InvoiceLineSchema,
  InvoiceSchema,
  InvoiceStatus,
  UpdateInvoiceInputSchema
} from '../domain/entities';

// OpenAPI schema for Invoice Line
export const InvoiceLineContractSchema = InvoiceLineSchema.meta({
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
export const InvoiceStatusContractSchema = z.enum([
  InvoiceStatus.ISSUED,
  InvoiceStatus.PAID,
  InvoiceStatus.OVERDUE,
  InvoiceStatus.CANCELLED
]).meta({
  description: 'Invoice status',
  example: InvoiceStatus.ISSUED
});

// OpenAPI schema for Create Invoice
export const CreateInvoiceContractSchema = CreateInvoiceInputSchema.meta({
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
export const UpdateInvoiceContractSchema = UpdateInvoiceInputSchema.meta({
  description: 'Invoice update data',
  example: {
    status: InvoiceStatus.PAID,
    notes: 'Payment received - thank you!'
  }
});

// OpenAPI schema for Invoice Response
export const InvoiceResponseContractSchema = InvoiceSchema.omit({ tenantId: true }).meta({
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
    status: InvoiceStatus.PAID,
    createdAt: new Date('2024-01-01T00:00:00.000Z'),
    updatedAt: new Date('2024-02-10T14:30:00.000Z'),
    version: 2
  }
});

// Query parameters for listing invoices
export const InvoiceQueryContractSchema = z.object({
  customerId: z.string().guid().optional(),
  orderId: z.string().guid().optional(),
  status: z.enum([
    InvoiceStatus.ISSUED,
    InvoiceStatus.PAID,
    InvoiceStatus.OVERDUE,
    InvoiceStatus.CANCELLED
  ]).optional(),
  search: z.string().optional().describe('Search term for invoice number'),
  dueDateFrom: z.string().datetime().optional(),
  dueDateTo: z.string().datetime().optional(),
  page: z.string().transform(Number).optional().prefault('1'),
  pageSize: z.string().transform(Number).optional().prefault('20')
}).meta({
  description: 'Query parameters for invoice listing'
});

// Response schema for invoice list
export const InvoiceListResponseContractSchema = z.object({
  data: z.array(InvoiceResponseContractSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number()
  })
}).meta({
  description: 'Paginated invoice list response'
});