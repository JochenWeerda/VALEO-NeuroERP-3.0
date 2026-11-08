import { z } from 'zod';
import {
  ContactSchema,
  CreateContactInputSchema,
  UpdateContactInputSchema
} from '../domain/entities';

// OpenAPI schema for Create Contact
export const CreateContactContractSchema = CreateContactInputSchema.meta({
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
});

// OpenAPI schema for Update Contact
export const UpdateContactContractSchema = UpdateContactInputSchema.meta({
  description: 'Contact update data',
  example: {
    role: 'CTO',
    phone: '+1-555-0124',
    isPrimary: false
  }
});

// OpenAPI schema for Contact Response
export const ContactResponseContractSchema = ContactSchema.omit({ tenantId: true }).meta({
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
});