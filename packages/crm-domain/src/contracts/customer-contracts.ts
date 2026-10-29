import { z } from 'zod';
import {
  AddressSchema,
  CreateCustomerInputSchema,
  CustomerSchema,
  CustomerStatus,
  UpdateCustomerInputSchema
} from '../domain/entities';

// OpenAPI schema for Address
export const AddressContractSchema = z.object({
  street: z.string(),
  city: z.string(),
  postalCode: z.string(),
  country: z.string(),
  state: z.string().optional()
}).meta({
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
export const CustomerStatusContractSchema = z.enum([CustomerStatus.ACTIVE, CustomerStatus.PROSPECT, CustomerStatus.BLOCKED]).meta({
  description: 'Customer status',
  example: CustomerStatus.ACTIVE
});

// OpenAPI schema for Create Customer
export const CreateCustomerContractSchema = CreateCustomerInputSchema.meta({
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
export const UpdateCustomerContractSchema = UpdateCustomerInputSchema.meta({
  description: 'Customer update data',
  example: {
    name: 'Updated Company Name',
    status: CustomerStatus.ACTIVE,
    tags: ['enterprise', 'technology', 'premium']
  }
});

// OpenAPI schema for Customer Response
export const CustomerResponseContractSchema = CustomerSchema.omit({ tenantId: true }).meta({
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
  ownerUserId: z.string().guid().optional(),
  page: z.string().transform(Number).optional().prefault('1'),
  pageSize: z.string().transform(Number).optional().prefault('20')
}).meta({
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
}).meta({
  description: 'Paginated customer list response'
});