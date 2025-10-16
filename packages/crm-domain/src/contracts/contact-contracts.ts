import { z } from 'zod';
// @ts-ignore - zod-openapi module
import { zodOpenapi } from 'zod-openapi';
import {
  ContactSchema,
  CreateContactInputSchema,
  UpdateContactInputSchema
} from '../domain/entities';

// OpenAPI schema for Create Contact
export const CreateContactContractSchema = zodOpenapi(
  CreateContactInputSchema,
  {
    description: 'Contact creation data',
    example: {
      customerId: '550e8400-e29b-41d4-a716-446655440000',
      firstName: 'John',
      lastName: 'Doe',
      role: 'CEO',
      email: 'john.doe@acme.com',
      phone: '+1-555-0123',
      isPrimary: true,
      notes: 'Main point of contact for enterprise deals'
    }
  }
);

// OpenAPI schema for Update Contact
export const UpdateContactContractSchema = zodOpenapi(
  UpdateContactInputSchema,
  {
    description: 'Contact update data',
    example: {
      role: 'CTO',
      phone: '+1-555-0124',
      isPrimary: false
    }
  }
);

// OpenAPI schema for Contact Response
export const ContactResponseContractSchema = zodOpenapi(
  ContactSchema.omit({ tenantId: true }),
  {
    description: 'Contact information',
    example: {
      id: '550e8400-e29b-41d4-a716-446655440001',
      customerId: '550e8400-e29b-41d4-a716-446655440000',
      firstName: 'John',
      lastName: 'Doe',
      role: 'CEO',
      email: 'john.doe@acme.com',
      phone: '+1-555-0123',
      isPrimary: true,
      notes: 'Main point of contact for enterprise deals',
      createdAt: '2024-01-01T00:00:00.000Z',
      updatedAt: '2024-01-01T00:00:00.000Z',
      version: 1
    }
  }
);