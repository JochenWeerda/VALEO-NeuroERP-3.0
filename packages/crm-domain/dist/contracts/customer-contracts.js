"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CustomerListResponseContractSchema = exports.CustomerQueryContractSchema = exports.CustomerResponseContractSchema = exports.UpdateCustomerContractSchema = exports.CreateCustomerContractSchema = exports.CustomerStatusContractSchema = exports.AddressContractSchema = void 0;
const zod_1 = require("zod");
const entities_1 = require("../domain/entities");
// OpenAPI schema for Address
exports.AddressContractSchema = zod_1.z.object({
    street: zod_1.z.string(),
    city: zod_1.z.string(),
    postalCode: zod_1.z.string(),
    country: zod_1.z.string(),
    state: zod_1.z.string().optional()
}).openapi({
    description: 'Physical address information',
    example: {
        street: '123 Main St',
        city: 'New York',
        postalCode: '10001',
        country: 'US',
        state: 'NY'
    }
});
// OpenAPI schema for Customer Status
exports.CustomerStatusContractSchema = zod_1.z.enum([entities_1.CustomerStatus.ACTIVE, entities_1.CustomerStatus.PROSPECT, entities_1.CustomerStatus.BLOCKED]).openapi({
    description: 'Customer status',
    example: entities_1.CustomerStatus.ACTIVE
});
// OpenAPI schema for Create Customer
exports.CreateCustomerContractSchema = entities_1.CreateCustomerInputSchema.openapi({
    description: 'Customer creation data',
    example: {
        number: 'CUST-001',
        name: 'Acme Corporation',
        vatId: 'US123456789',
        billingAddress: {
            street: '123 Main St',
            city: 'New York',
            postalCode: '10001',
            country: 'US',
            state: 'NY'
        },
        shippingAddresses: [],
        email: 'contact@acme.com',
        phone: '+1-555-0123',
        tags: ['enterprise', 'technology'],
        status: entities_1.CustomerStatus.PROSPECT,
        ownerUserId: '550e8400-e29b-41d4-a716-446655440000'
    }
});
// OpenAPI schema for Update Customer
exports.UpdateCustomerContractSchema = entities_1.UpdateCustomerInputSchema.openapi({
    description: 'Customer update data',
    example: {
        name: 'Updated Company Name',
        status: entities_1.CustomerStatus.ACTIVE,
        tags: ['enterprise', 'technology', 'premium']
    }
});
// OpenAPI schema for Customer Response
exports.CustomerResponseContractSchema = entities_1.CustomerSchema.omit({ tenantId: true }).openapi({
    description: 'Customer information',
    example: {
        id: '550e8400-e29b-41d4-a716-446655440000',
        number: 'CUST-001',
        name: 'Acme Corporation',
        vatId: 'US123456789',
        billingAddress: {
            street: '123 Main St',
            city: 'New York',
            postalCode: '10001',
            country: 'US',
            state: 'NY'
        },
        shippingAddresses: [],
        email: 'contact@acme.com',
        phone: '+1-555-0123',
        tags: ['enterprise', 'technology'],
        status: entities_1.CustomerStatus.ACTIVE,
        ownerUserId: '550e8400-e29b-41d4-a716-446655440000',
        createdAt: new Date('2024-01-01T00:00:00.000Z'),
        updatedAt: new Date('2024-01-01T00:00:00.000Z'),
        version: 1
    }
});
// Query parameters for listing customers
exports.CustomerQueryContractSchema = zod_1.z.object({
    search: zod_1.z.string().optional().describe('Search term for name or number'),
    status: zod_1.z.enum([entities_1.CustomerStatus.ACTIVE, entities_1.CustomerStatus.PROSPECT, entities_1.CustomerStatus.BLOCKED]).optional(),
    tags: zod_1.z.string().optional().describe('Comma-separated list of tags'),
    ownerUserId: zod_1.z.string().uuid().optional(),
    page: zod_1.z.string().transform(Number).optional().default('1'),
    pageSize: zod_1.z.string().transform(Number).optional().default('20')
}).openapi({
    description: 'Query parameters for customer listing'
});
// Response schema for customer list
exports.CustomerListResponseContractSchema = zod_1.z.object({
    data: zod_1.z.array(exports.CustomerResponseContractSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number()
    })
}).openapi({
    description: 'Paginated customer list response'
});
//# sourceMappingURL=customer-contracts.js.map