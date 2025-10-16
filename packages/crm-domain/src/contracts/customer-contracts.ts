import { z } from 'zod';
import {
  CustomerSchema,
  CreateCustomerInputSchema,
  UpdateCustomerInputSchema,
  AddressSchema,
  CustomerStatus
} from '../domain/entities';

// OpenAPI schema for Address
export const AddressContractSchema = z.object({
  street: z.string(),
  city: z.string(),
  postalCode: z.string(),
  country: z.string(),
  state: z.string().optional()
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
export const CustomerStatusContractSchema = z.enum([CustomerStatus.ACTIVE, CustomerStatus.PROSPECT, CustomerStatus.BLOCKED]).openapi({
  description: 'Customer status',
  example: CustomerStatus.ACTIVE
});

// OpenAPI schema for Create Customer
export const CreateCustomerContractSchema = CreateCustomerInputSchema.openapi({
  description: 'Customer creation data',
  example: {
    tenantId: 'default',
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
    status: CustomerStatus.PROSPECT,
    ownerUserId: '550e8400-e29b-41d4-a716-446655440000'
  }
});

// OpenAPI schema for Update Customer
export const UpdateCustomerContractSchema = UpdateCustomerInputSchema.openapi({
  description: 'Customer update data',
  example: {
    name: 'Updated Company Name',
    status: CustomerStatus.ACTIVE,
    tags: ['enterprise', 'technology', 'premium']
  }
});

// OpenAPI schema for Customer Response
export const CustomerResponseContractSchema = CustomerSchema.omit({ tenantId: true }).openapi({
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
    status: CustomerStatus.ACTIVE,
    ownerUserId: '550e8400-e29b-41d4-a716-446655440000',
    createdAt: new Date('2024-01-01T00:00:00.000Z'),
    updatedAt: new Date('2024-01-01T00:00:00.000Z'),
    version: 1
  }
});

// Query parameters for listing customers
export const CustomerQueryContractSchema = z.object({
  search: z.string().optional().describe('Search term for name or number'),
  status: z.enum([CustomerStatus.ACTIVE, CustomerStatus.PROSPECT, CustomerStatus.BLOCKED]).optional(),
  tags: z.string().optional().describe('Comma-separated list of tags'),
  ownerUserId: z.string().uuid().optional(),
  page: z.string().transform(Number).optional().default('1'),
  pageSize: z.string().transform(Number).optional().default('20')
}).openapi({
  description: 'Query parameters for customer listing'
});

// Response schema for customer list
export const CustomerListResponseContractSchema = z.object({
  data: z.array(CustomerResponseContractSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number()
  })
}).openapi({
  description: 'Paginated customer list response'
});