"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderListResponseContractSchema = exports.OrderQueryContractSchema = exports.OrderResponseContractSchema = exports.UpdateOrderContractSchema = exports.CreateOrderContractSchema = exports.OrderStatusContractSchema = exports.OrderLineContractSchema = void 0;
var zod_1 = require("zod");
var zod_openapi_1 = require("zod-openapi");
(0, zod_openapi_1.extendZodWithOpenApi)(zod_1.z);
var entities_1 = require("../domain/entities");
// OpenAPI schema for Order Line
exports.OrderLineContractSchema = entities_1.OrderLineSchema.openapi({
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
exports.OrderStatusContractSchema = zod_1.z.enum([
    entities_1.OrderStatus.DRAFT,
    entities_1.OrderStatus.CONFIRMED,
    entities_1.OrderStatus.INVOICED,
    entities_1.OrderStatus.CANCELLED
]).openapi({
    description: 'Order status',
    example: entities_1.OrderStatus.CONFIRMED
});
// OpenAPI schema for Create Order
exports.CreateOrderContractSchema = entities_1.CreateOrderInputSchema.openapi({
    description: 'Order creation data',
    example: {
        tenantId: 'tenant-001',
        status: entities_1.OrderStatus.DRAFT,
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
exports.UpdateOrderContractSchema = entities_1.UpdateOrderInputSchema.openapi({
    description: 'Order update data',
    example: {
        status: entities_1.OrderStatus.CONFIRMED,
        expectedDeliveryDate: new Date('2024-07-15T00:00:00.000Z')
    }
});
// OpenAPI schema for Order Response
exports.OrderResponseContractSchema = entities_1.OrderSchema.omit({ tenantId: true }).openapi({
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
        expectedDeliveryDate: new Date('2024-06-30T00:00:00.000Z'),
        notes: 'Rush order - client needs delivery by end of month',
        status: entities_1.OrderStatus.CONFIRMED,
        createdAt: new Date('2024-01-01T00:00:00.000Z'),
        updatedAt: new Date('2024-01-01T00:00:00.000Z'),
        version: 1
    }
});
// Query parameters for listing orders
exports.OrderQueryContractSchema = zod_1.z.object({
    customerId: zod_1.z.string().uuid().optional(),
    status: zod_1.z.enum([
        entities_1.OrderStatus.DRAFT,
        entities_1.OrderStatus.CONFIRMED,
        entities_1.OrderStatus.INVOICED,
        entities_1.OrderStatus.CANCELLED
    ]).optional(),
    search: zod_1.z.string().optional().describe('Search term for order number or customer'),
    expectedDeliveryDateFrom: zod_1.z.string().datetime().optional(),
    expectedDeliveryDateTo: zod_1.z.string().datetime().optional(),
    page: zod_1.z.string().transform(Number).optional().default('1'),
    pageSize: zod_1.z.string().transform(Number).optional().default('20')
}).openapi({
    description: 'Query parameters for order listing'
});
// Response schema for order list
exports.OrderListResponseContractSchema = zod_1.z.object({
    data: zod_1.z.array(exports.OrderResponseContractSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number()
    })
}).openapi({
    description: 'Paginated order list response'
});
