"use strict";
/**
 * Employee Routes for VALEO NeuroERP 3.0 HR Domain
 * REST API endpoints for employee management
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerEmployeeRoutes = registerEmployeeRoutes;
const zod_1 = require("zod");
const auth_1 = require("../middleware/auth");
// Request/Response schemas
const CreateEmployeeSchema = zod_1.z.object({
    employeeNumber: zod_1.z.string().min(1).max(50),
    person: zod_1.z.object({
        firstName: zod_1.z.string().min(1).max(100),
        lastName: zod_1.z.string().min(1).max(100),
        birthDate: zod_1.z.string().datetime().optional()
    }),
    contact: zod_1.z.object({
        email: zod_1.z.string().email().optional(),
        phone: zod_1.z.string().optional()
    }).optional(),
    employment: zod_1.z.object({
        hireDate: zod_1.z.string().datetime(),
        type: zod_1.z.enum(['Full', 'Part', 'Temp'])
    }),
    org: zod_1.z.object({
        departmentId: zod_1.z.string().uuid().optional(),
        position: zod_1.z.string().optional(),
        managerId: zod_1.z.string().uuid().optional()
    }).optional(),
    payroll: zod_1.z.object({
        taxClass: zod_1.z.string().optional(),
        socialSecurityId: zod_1.z.string().optional(),
        iban: zod_1.z.string().optional()
    }).optional(),
    roles: zod_1.z.array(zod_1.z.string()).optional()
});
const UpdateEmployeeSchema = zod_1.z.object({
    contact: zod_1.z.object({
        email: zod_1.z.string().email().optional(),
        phone: zod_1.z.string().optional()
    }).optional(),
    org: zod_1.z.object({
        departmentId: zod_1.z.string().uuid().optional(),
        position: zod_1.z.string().optional(),
        managerId: zod_1.z.string().uuid().optional()
    }).optional()
});
const EmployeeFiltersSchema = zod_1.z.object({
    status: zod_1.z.string().optional(),
    departmentId: zod_1.z.string().uuid().optional(),
    managerId: zod_1.z.string().uuid().optional(),
    roleId: zod_1.z.string().optional(),
    search: zod_1.z.string().optional(),
    hireDateFrom: zod_1.z.string().date().optional(),
    hireDateTo: zod_1.z.string().date().optional(),
    page: zod_1.z.number().int().min(1).optional(),
    pageSize: zod_1.z.number().int().min(1).max(100).optional(),
    sortBy: zod_1.z.string().optional(),
    sortOrder: zod_1.z.enum(['asc', 'desc']).optional()
});
function registerEmployeeRoutes(fastify, employeeService) {
    // Create employee
    fastify.post('/hr/api/v1/employees', {
        preHandler: [(0, auth_1.requireHrPermission)(auth_1.hrPermissions.EMPLOYEE_WRITE)],
        schema: {
            description: 'Create a new employee',
            tags: ['employees'],
            body: CreateEmployeeSchema,
            response: {
                201: {
                    description: 'Employee created successfully',
                    type: 'object'
                },
                400: {
                    description: 'Invalid input data',
                    type: 'object'
                },
                401: {
                    description: 'Unauthorized',
                    type: 'object'
                },
                403: {
                    description: 'Insufficient permissions',
                    type: 'object'
                }
            }
        }
    }, async (request, reply) => {
        try {
            const employee = await employeeService.createEmployee({
                tenantId: request.auth.tenantId,
                createdBy: request.auth.userId,
                ...request.body
            });
            return reply.code(201).send(employee);
        }
        catch (error) {
            console.error('Error creating employee:', error);
            return reply.code(400).send({ error: error instanceof Error ? error.message : 'Failed to create employee' });
        }
    });
    // Get employee by ID
    fastify.get('/hr/api/v1/employees/:id', {
        preHandler: [(0, auth_1.requireHrPermission)(auth_1.hrPermissions.EMPLOYEE_READ)],
        schema: {
            description: 'Get employee by ID',
            tags: ['employees'],
            params: {
                type: 'object',
                properties: {
                    id: { type: 'string', format: 'uuid' }
                },
                required: ['id']
            },
            response: {
                200: {
                    description: 'Employee details',
                    type: 'object'
                },
                404: {
                    description: 'Employee not found',
                    type: 'object'
                }
            }
        }
    }, async (request, reply) => {
        try {
            const employee = await employeeService.getEmployee(request.auth.tenantId, request.params.id);
            return reply.send(employee);
        }
        catch (error) {
            console.error('Error getting employee:', error);
            return reply.code(404).send({ error: error instanceof Error ? error.message : 'Employee not found' });
        }
    });
    // List employees
    fastify.get('/hr/api/v1/employees', {
        preHandler: [(0, auth_1.requireHrPermission)(auth_1.hrPermissions.EMPLOYEE_READ)],
        schema: {
            description: 'List employees with filtering and pagination',
            tags: ['employees'],
            querystring: EmployeeFiltersSchema,
            response: {
                200: {
                    description: 'List of employees',
                    type: 'object'
                }
            }
        }
    }, async (request, reply) => {
        try {
            const { page, pageSize, sortBy, sortOrder, ...filters } = request.query;
            let result;
            if (page && pageSize) {
                result = await employeeService.listEmployees(request.auth.tenantId, filters, {
                    page,
                    pageSize,
                    sortBy,
                    sortOrder,
                    filters
                });
            }
            else {
                result = await employeeService.listEmployees(request.auth.tenantId, filters);
            }
            return reply.send(result);
        }
        catch (error) {
            console.error('Error listing employees:', error);
            return reply.code(500).send({ error: 'Failed to list employees' });
        }
    });
    // Update employee
    fastify.patch('/hr/api/v1/employees/:id', {
        preHandler: [(0, auth_1.requireHrPermission)(auth_1.hrPermissions.EMPLOYEE_WRITE)],
        schema: {
            description: 'Update employee',
            tags: ['employees'],
            params: {
                type: 'object',
                properties: {
                    id: { type: 'string', format: 'uuid' }
                },
                required: ['id']
            },
            body: UpdateEmployeeSchema,
            response: {
                200: {
                    description: 'Employee updated successfully',
                    type: 'object'
                },
                404: {
                    description: 'Employee not found',
                    type: 'object'
                }
            }
        }
    }, async (request, reply) => {
        try {
            const employee = await employeeService.updateEmployee({
                tenantId: request.auth.tenantId,
                employeeId: request.params.id,
                updates: request.body,
                updatedBy: request.auth.userId
            });
            return reply.send(employee);
        }
        catch (error) {
            console.error('Error updating employee:', error);
            return reply.code(404).send({ error: error instanceof Error ? error.message : 'Employee not found' });
        }
    });
    // Assign role to employee
    fastify.post('/hr/api/v1/employees/:id/roles', {
        preHandler: [(0, auth_1.requireHrPermission)(auth_1.hrPermissions.EMPLOYEE_WRITE)],
        schema: {
            description: 'Assign role to employee',
            tags: ['employees'],
            params: {
                type: 'object',
                properties: {
                    id: { type: 'string', format: 'uuid' }
                },
                required: ['id']
            },
            body: {
                type: 'object',
                properties: {
                    roleId: { type: 'string' }
                },
                required: ['roleId']
            },
            response: {
                200: {
                    description: 'Role assigned successfully',
                    type: 'object'
                }
            }
        }
    }, async (request, reply) => {
        try {
            const employee = await employeeService.assignRole({
                tenantId: request.auth.tenantId,
                employeeId: request.params.id,
                roleId: request.body.roleId,
                updatedBy: request.auth.userId
            });
            return reply.send(employee);
        }
        catch (error) {
            console.error('Error assigning role:', error);
            return reply.code(400).send({ error: error instanceof Error ? error.message : 'Failed to assign role' });
        }
    });
    // Remove role from employee
    fastify.delete('/hr/api/v1/employees/:id/roles/:roleId', {
        preHandler: [(0, auth_1.requireHrPermission)(auth_1.hrPermissions.EMPLOYEE_WRITE)],
        schema: {
            description: 'Remove role from employee',
            tags: ['employees'],
            params: {
                type: 'object',
                properties: {
                    id: { type: 'string', format: 'uuid' },
                    roleId: { type: 'string' }
                },
                required: ['id', 'roleId']
            },
            response: {
                200: {
                    description: 'Role removed successfully',
                    type: 'object'
                }
            }
        }
    }, async (request, reply) => {
        try {
            const employee = await employeeService.removeRole({
                tenantId: request.auth.tenantId,
                employeeId: request.params.id,
                roleId: request.params.roleId,
                updatedBy: request.auth.userId
            });
            return reply.send(employee);
        }
        catch (error) {
            console.error('Error removing role:', error);
            return reply.code(400).send({ error: error instanceof Error ? error.message : 'Failed to remove role' });
        }
    });
    // Deactivate employee
    fastify.post('/hr/api/v1/employees/:id/deactivate', {
        preHandler: [(0, auth_1.requireHrPermission)(auth_1.hrPermissions.EMPLOYEE_WRITE)],
        schema: {
            description: 'Deactivate employee',
            tags: ['employees'],
            params: {
                type: 'object',
                properties: {
                    id: { type: 'string', format: 'uuid' }
                },
                required: ['id']
            },
            body: {
                type: 'object',
                properties: {
                    reason: { type: 'string' },
                    terminationDate: { type: 'string', format: 'date-time' }
                }
            },
            response: {
                200: {
                    description: 'Employee deactivated successfully',
                    type: 'object'
                }
            }
        }
    }, async (request, reply) => {
        try {
            const employee = await employeeService.deactivateEmployee({
                tenantId: request.auth.tenantId,
                employeeId: request.params.id,
                reason: request.body.reason,
                terminationDate: request.body.terminationDate,
                updatedBy: request.auth.userId
            });
            return reply.send(employee);
        }
        catch (error) {
            console.error('Error deactivating employee:', error);
            return reply.code(400).send({ error: error instanceof Error ? error.message : 'Failed to deactivate employee' });
        }
    });
    // Reactivate employee
    fastify.post('/hr/api/v1/employees/:id/reactivate', {
        preHandler: [(0, auth_1.requireHrPermission)(auth_1.hrPermissions.EMPLOYEE_WRITE)],
        schema: {
            description: 'Reactivate employee',
            tags: ['employees'],
            params: {
                type: 'object',
                properties: {
                    id: { type: 'string', format: 'uuid' }
                },
                required: ['id']
            },
            response: {
                200: {
                    description: 'Employee reactivated successfully',
                    type: 'object'
                }
            }
        }
    }, async (request, reply) => {
        try {
            const employee = await employeeService.reactivateEmployee(request.auth.tenantId, request.params.id, request.auth.userId);
            return reply.send(employee);
        }
        catch (error) {
            console.error('Error reactivating employee:', error);
            return reply.code(400).send({ error: error instanceof Error ? error.message : 'Failed to reactivate employee' });
        }
    });
    // Get employee statistics
    fastify.get('/hr/api/v1/employees/statistics', {
        preHandler: [(0, auth_1.requireHrPermission)(auth_1.hrPermissions.EMPLOYEE_READ)],
        schema: {
            description: 'Get employee statistics',
            tags: ['employees'],
            response: {
                200: {
                    description: 'Employee statistics',
                    type: 'object'
                }
            }
        }
    }, async (request, reply) => {
        try {
            const statistics = await employeeService.getEmployeeStatistics(request.auth.tenantId);
            return reply.send(statistics);
        }
        catch (error) {
            console.error('Error getting employee statistics:', error);
            return reply.code(500).send({ error: 'Failed to get employee statistics' });
        }
    });
}
//# sourceMappingURL=employees.js.map