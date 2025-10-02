"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContactResponseContractSchema = exports.UpdateContactContractSchema = exports.CreateContactContractSchema = void 0;
const zod_openapi_1 = require("zod-openapi");
const entities_1 = require("../domain/entities");
// OpenAPI schema for Create Contact
exports.CreateContactContractSchema = (0, zod_openapi_1.zodOpenapi)(entities_1.CreateContactInputSchema, {
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
exports.UpdateContactContractSchema = (0, zod_openapi_1.zodOpenapi)(entities_1.UpdateContactInputSchema, {
    description: 'Contact update data',
    example: {
        role: 'CTO',
        phone: '+1-555-0124',
        isPrimary: false
    }
});
// OpenAPI schema for Contact Response
exports.ContactResponseContractSchema = (0, zod_openapi_1.zodOpenapi)(entities_1.ContactSchema.omit({ tenantId: true }), {
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
//# sourceMappingURL=contact-contracts.js.map