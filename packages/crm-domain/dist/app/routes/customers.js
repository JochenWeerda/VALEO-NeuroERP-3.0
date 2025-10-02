"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerCustomerRoutes = registerCustomerRoutes;
const zod_1 = require("zod");
const contracts_1 = require("../../contracts");
// Request/Response schemas
const CreateCustomerRequestSchema = contracts_1.CreateCustomerContractSchema;
const UpdateCustomerRequestSchema = contracts_1.UpdateCustomerContractSchema;
const CustomerResponseSchema = contracts_1.CustomerResponseContractSchema;
const CustomerListResponseSchema = contracts_1.CustomerListResponseContractSchema;
// Register customer routes
async function registerCustomerRoutes(fastify, services) {
    const { customerService } = services;
    // POST /customers - Create a new customer
    fastify.post('/customers', {
        schema: {
            description: 'Create a new customer',
            tags: ['Customers'],
            summary: 'Create customer',
            body: CreateCustomerRequestSchema,
            response: {
                201: CustomerResponseSchema,
                400: zod_1.z.object({
                    error: zod_1.z.string(),
                    message: zod_1.z.string(),
                    code: zod_1.z.string()
                }),
                409: zod_1.z.object({
                    error: zod_1.z.string(),
                    message: zod_1.z.string(),
                    code: zod_1.z.string()
                })
            },
            security: [{ bearerAuth: [] }]
        }
    }, async (request, reply) => {
        try {
            const customerData = request.body;
            const context = request.routeContext;
            const customer = await customerService.createCustomer({
                ...customerData,
                tenantId: 'default-tenant' // TODO: Get from JWT token
            });
            reply.code(201).send(customer.toJSON());
        }
        catch (error) {
            request.log.error('Error creating customer:', error);
            if (error.message?.includes('already exists')) {
                reply.code(409).send({
                    error: 'Conflict',
                    message: error.message,
                    code: 'CUSTOMER_ALREADY_EXISTS'
                });
            }
            else {
                reply.code(400).send({
                    error: 'Bad Request',
                    message: error.message,
                    code: 'INVALID_CUSTOMER_DATA'
                });
            }
        }
    });
    // GET /customers/:id - Get customer by ID
    fastify.get('/customers/:id', {
        schema: {
            description: 'Get customer by ID',
            tags: ['Customers'],
            summary: 'Get customer',
            params: zod_1.z.object({
                id: zod_1.z.string().uuid()
            }),
            response: {
                200: CustomerResponseSchema,
                404: zod_1.z.object({
                    error: zod_1.z.string(),
                    message: zod_1.z.string(),
                    code: zod_1.z.string()
                })
            },
            security: [{ bearerAuth: [] }]
        }
    }, async (request, reply) => {
        try {
            const { id } = request.params;
            const context = request.routeContext;
            const customer = await customerService.getCustomer(id, 'default-tenant'); // TODO: Get from JWT token
            if (!customer) {
                reply.code(404).send({
                    error: 'Not Found',
                    message: `Customer ${id} not found`,
                    code: 'CUSTOMER_NOT_FOUND'
                });
                return;
            }
            reply.send(customer.toJSON());
        }
        catch (error) {
            request.log.error('Error getting customer:', error);
            reply.code(500).send({
                error: 'Internal Server Error',
                message: 'Failed to retrieve customer',
                code: 'INTERNAL_ERROR'
            });
        }
    });
    // GET /customers - List customers with filtering and pagination
    fastify.get('/customers', {
        schema: {
            description: 'List customers with filtering and pagination',
            tags: ['Customers'],
            summary: 'List customers',
            querystring: contracts_1.CustomerQueryContractSchema,
            response: {
                200: CustomerListResponseSchema
            },
            security: [{ bearerAuth: [] }]
        }
    }, async (request, reply) => {
        try {
            const query = request.query;
            const context = request.routeContext;
            // Parse pagination
            const page = Number(query.page) || 1;
            const pageSize = Number(query.pageSize) || 20;
            // Parse filters
            const filters = {};
            if (query.search)
                filters.search = query.search;
            if (query.status)
                filters.status = query.status;
            if (query.ownerUserId)
                filters.ownerUserId = query.ownerUserId;
            const result = await customerService.searchCustomers('default-tenant', // TODO: Get from JWT token
            filters, { page, pageSize });
            reply.send({
                data: result.data.map(customer => customer.toJSON()),
                pagination: result.pagination
            });
        }
        catch (error) {
            request.log.error('Error listing customers:', error);
            reply.code(500).send({
                error: 'Internal Server Error',
                message: 'Failed to retrieve customers',
                code: 'INTERNAL_ERROR'
            });
        }
    });
    // PATCH /customers/:id - Update customer
    fastify.patch('/customers/:id', {
        schema: {
            description: 'Update customer',
            tags: ['Customers'],
            summary: 'Update customer',
            params: zod_1.z.object({
                id: zod_1.z.string().uuid()
            }),
            body: UpdateCustomerRequestSchema,
            response: {
                200: CustomerResponseSchema,
                404: zod_1.z.object({
                    error: zod_1.z.string(),
                    message: zod_1.z.string(),
                    code: zod_1.z.string()
                }),
                400: zod_1.z.object({
                    error: zod_1.z.string(),
                    message: zod_1.z.string(),
                    code: zod_1.z.string()
                })
            },
            security: [{ bearerAuth: [] }]
        }
    }, async (request, reply) => {
        try {
            const { id } = request.params;
            const updateData = request.body;
            const context = request.routeContext;
            const customer = await customerService.updateCustomer(id, {
                ...updateData,
                tenantId: 'default-tenant' // TODO: Get from JWT token
            });
            reply.send(customer.toJSON());
        }
        catch (error) {
            request.log.error('Error updating customer:', error);
            if (error.message?.includes('not found')) {
                reply.code(404).send({
                    error: 'Not Found',
                    message: error.message,
                    code: 'CUSTOMER_NOT_FOUND'
                });
            }
            else {
                reply.code(400).send({
                    error: 'Bad Request',
                    message: error.message,
                    code: 'INVALID_UPDATE_DATA'
                });
            }
        }
    });
    // DELETE /customers/:id - Delete customer
    fastify.delete('/customers/:id', {
        schema: {
            description: 'Delete customer',
            tags: ['Customers'],
            summary: 'Delete customer',
            params: zod_1.z.object({
                id: zod_1.z.string().uuid()
            }),
            response: {
                204: zod_1.z.null(),
                404: zod_1.z.object({
                    error: zod_1.z.string(),
                    message: zod_1.z.string(),
                    code: zod_1.z.string()
                }),
                400: zod_1.z.object({
                    error: zod_1.z.string(),
                    message: zod_1.z.string(),
                    code: zod_1.z.string()
                })
            },
            security: [{ bearerAuth: [] }]
        }
    }, async (request, reply) => {
        try {
            const { id } = request.params;
            const context = request.routeContext;
            await customerService.deleteCustomer(id, 'default-tenant'); // TODO: Get from JWT token
            reply.code(204).send();
        }
        catch (error) {
            request.log.error('Error deleting customer:', error);
            if (error.message?.includes('not found')) {
                reply.code(404).send({
                    error: 'Not Found',
                    message: error.message,
                    code: 'CUSTOMER_NOT_FOUND'
                });
            }
            else {
                reply.code(400).send({
                    error: 'Bad Request',
                    message: error.message,
                    code: 'DELETE_FAILED'
                });
            }
        }
    });
    // POST /customers/:id/status - Change customer status
    fastify.post('/customers/:id/status', {
        schema: {
            description: 'Change customer status',
            tags: ['Customers'],
            summary: 'Change customer status',
            params: zod_1.z.object({
                id: zod_1.z.string().uuid()
            }),
            body: zod_1.z.object({
                status: zod_1.z.enum(['Active', 'Prospect', 'Blocked'])
            }),
            response: {
                200: CustomerResponseSchema,
                404: zod_1.z.object({
                    error: zod_1.z.string(),
                    message: zod_1.z.string(),
                    code: zod_1.z.string()
                }),
                400: zod_1.z.object({
                    error: zod_1.z.string(),
                    message: zod_1.z.string(),
                    code: zod_1.z.string()
                })
            },
            security: [{ bearerAuth: [] }]
        }
    }, async (request, reply) => {
        try {
            const { id } = request.params;
            const { status } = request.body;
            const context = request.routeContext;
            const customer = await customerService.changeCustomerStatus(id, 'default-tenant', // TODO: Get from JWT token
            status);
            reply.send(customer.toJSON());
        }
        catch (error) {
            request.log.error('Error changing customer status:', error);
            if (error.message?.includes('not found')) {
                reply.code(404).send({
                    error: 'Not Found',
                    message: error.message,
                    code: 'CUSTOMER_NOT_FOUND'
                });
            }
            else {
                reply.code(400).send({
                    error: 'Bad Request',
                    message: error.message,
                    code: 'INVALID_STATUS_TRANSITION'
                });
            }
        }
    });
    // POST /customers/:id/tags - Add tag to customer
    fastify.post('/customers/:id/tags', {
        schema: {
            description: 'Add tag to customer',
            tags: ['Customers'],
            summary: 'Add customer tag',
            params: zod_1.z.object({
                id: zod_1.z.string().uuid()
            }),
            body: zod_1.z.object({
                tag: zod_1.z.string().min(1)
            }),
            response: {
                200: CustomerResponseSchema,
                404: zod_1.z.object({
                    error: zod_1.z.string(),
                    message: zod_1.z.string(),
                    code: zod_1.z.string()
                })
            },
            security: [{ bearerAuth: [] }]
        }
    }, async (request, reply) => {
        try {
            const { id } = request.params;
            const { tag } = request.body;
            const context = request.routeContext;
            const customer = await customerService.addTag(id, 'default-tenant', // TODO: Get from JWT token
            tag);
            reply.send(customer.toJSON());
        }
        catch (error) {
            request.log.error('Error adding customer tag:', error);
            if (error.message?.includes('not found')) {
                reply.code(404).send({
                    error: 'Not Found',
                    message: error.message,
                    code: 'CUSTOMER_NOT_FOUND'
                });
            }
            else {
                reply.code(500).send({
                    error: 'Internal Server Error',
                    message: 'Failed to add tag',
                    code: 'INTERNAL_ERROR'
                });
            }
        }
    });
    // DELETE /customers/:id/tags/:tag - Remove tag from customer
    fastify.delete('/customers/:id/tags/:tag', {
        schema: {
            description: 'Remove tag from customer',
            tags: ['Customers'],
            summary: 'Remove customer tag',
            params: zod_1.z.object({
                id: zod_1.z.string().uuid(),
                tag: zod_1.z.string().min(1)
            }),
            response: {
                200: CustomerResponseSchema,
                404: zod_1.z.object({
                    error: zod_1.z.string(),
                    message: zod_1.z.string(),
                    code: zod_1.z.string()
                })
            },
            security: [{ bearerAuth: [] }]
        }
    }, async (request, reply) => {
        try {
            const { id, tag } = request.params;
            const context = request.routeContext;
            const customer = await customerService.removeTag(id, 'default-tenant', // TODO: Get from JWT token
            tag);
            reply.send(customer.toJSON());
        }
        catch (error) {
            request.log.error('Error removing customer tag:', error);
            if (error.message?.includes('not found')) {
                reply.code(404).send({
                    error: 'Not Found',
                    message: error.message,
                    code: 'CUSTOMER_NOT_FOUND'
                });
            }
            else {
                reply.code(500).send({
                    error: 'Internal Server Error',
                    message: 'Failed to remove tag',
                    code: 'INTERNAL_ERROR'
                });
            }
        }
    });
}
//# sourceMappingURL=customers.js.map