import { z } from 'zod';
import { extendZodWithOpenApi } from 'zod-openapi';

extendZodWithOpenApi(z);
import {
  OrderSchema,
  CreateOrderInputSchema,
  UpdateOrderInputSchema,
  OrderLineSchema,
  OrderStatus
} from '../domain/entities';

// OpenAPI schema for Order Line
export const OrderLineContractSchema = OrderLineSchema.openapi({
  description: 'Order line item',
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

// OpenAPI schema for Order Status
export const OrderStatusContractSchema = z.enum([
  OrderStatus.DRAFT,
  OrderStatus.CONFIRMED,
  OrderStatus.INVOICED,
  OrderStatus.CANCELLED
]).openapi({
  description: 'Order status',
  example: OrderStatus.CONFIRMED
});

// OpenAPI schema for Create Order
export const CreateOrderContractSchema = CreateOrderInputSchema.openapi({
  description: 'Order creation data',
  example: {
    customerId: '550e8400-e29b-41d4-a716-446655440000',
    orderNumber: 'ORD-2024-001',
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
    expectedDeliveryDate: new Date('2024-06-30T00:00:00.000Z'),
    notes: 'Rush order - client needs delivery by end of month',
    taxRate: 19,
    currency: 'EUR'
  }
});

// OpenAPI schema for Update Order
export const UpdateOrderContractSchema = UpdateOrderInputSchema.openapi({
  description: 'Order update data',
  example: {
    status: OrderStatus.CONFIRMED,
    expectedDeliveryDate: '2024-07-15T00:00:00.000Z'
  }
});

// OpenAPI schema for Order Response
export const OrderResponseContractSchema = OrderSchema.omit({ tenantId: true }).openapi({
  description: 'Order information',
  example: {
    id: '550e8400-e29b-41d4-a716-446655440003',
    customerId: '550e8400-e29b-41d4-a716-446655440000',
    orderNumber: 'ORD-2024-001',
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
    expectedDeliveryDate: '2024-06-30T00:00:00.000Z',
    notes: 'Rush order - client needs delivery by end of month',
    status: OrderStatus.CONFIRMED,
    createdAt: '2024-01-01T00:00:00.000Z',
    updatedAt: '2024-01-01T00:00:00.000Z',
    version: 1
  }
});

// Query parameters for listing orders
export const OrderQueryContractSchema = z.object({
  customerId: z.string().uuid().optional(),
  status: z.enum([
    OrderStatus.DRAFT,
    OrderStatus.CONFIRMED,
    OrderStatus.INVOICED,
    OrderStatus.CANCELLED
  ]).optional(),
  search: z.string().optional().describe('Search term for order number or customer'),
  expectedDeliveryDateFrom: z.string().datetime().optional(),
  expectedDeliveryDateTo: z.string().datetime().optional(),
  page: z.string().transform(Number).optional().default('1'),
  pageSize: z.string().transform(Number).optional().default('20')
}).openapi({
  description: 'Query parameters for order listing'
});

// Response schema for order list
export const OrderListResponseContractSchema = z.object({
  data: z.array(OrderResponseContractSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number()
  })
}).openapi({
  description: 'Paginated order list response'
});