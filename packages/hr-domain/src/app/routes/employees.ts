/**
 * Employee Routes for VALEO NeuroERP 3.0 HR Domain
 * REST API endpoints for employee management
 */

import { FastifyInstance, FastifyReply, FastifyRequest } from 'fastify';
import { z } from 'zod';
import { EmployeeService } from '../../domain/services/employee-service';
import { type AuthContext, hrPermissions, requireHrPermission } from '../middleware/auth';

const EMPLOYEE_NUMBER_MAX_LENGTH = 50;
const PERSON_NAME_MAX_LENGTH = 100;
const MAX_PAGE_SIZE = 100;

const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500
} as const;

const AUTHENTICATION_REQUIRED_RESPONSE = { error: 'Authentication required' } as const;

type AuthenticatedRequest = FastifyRequest & { auth: AuthContext };

function ensureAuth(request: FastifyRequest, reply: FastifyReply): request is AuthenticatedRequest {
  if (!request.auth) {
    reply.code(HTTP_STATUS.UNAUTHORIZED).send(AUTHENTICATION_REQUIRED_RESPONSE);
    return false;
  }
  return true;
}

const CreateEmployeeSchema = z.object({
  employeeNumber: z.string().min(1).max(EMPLOYEE_NUMBER_MAX_LENGTH),
  person: z.object({
    firstName: z.string().min(1).max(PERSON_NAME_MAX_LENGTH),
    lastName: z.string().min(1).max(PERSON_NAME_MAX_LENGTH),
    birthDate: z.string().datetime().optional()
  }),
  contact: z.object({
    email: z.string().email().optional(),
    phone: z.string().optional()
  }).optional(),
  employment: z.object({
    hireDate: z.string().datetime(),
    type: z.enum(['Full', 'Part', 'Temp'])
  }),
  org: z.object({
    departmentId: z.string().uuid().optional(),
    position: z.string().optional(),
    managerId: z.string().uuid().optional()
  }).optional(),
  payroll: z.object({
    taxClass: z.string().optional(),
    socialSecurityId: z.string().optional(),
    iban: z.string().optional()
  }).optional(),
  roles: z.array(z.string()).optional()
});

const UpdateEmployeeSchema = z.object({
  contact: z.object({
    email: z.string().email().optional(),
    phone: z.string().optional()
  }).optional(),
  org: z.object({
    departmentId: z.string().uuid().optional(),
    position: z.string().optional(),
    managerId: z.string().uuid().optional()
  }).optional()
});

const EmployeeFiltersSchema = z.object({
  status: z.string().optional(),
  departmentId: z.string().uuid().optional(),
  managerId: z.string().uuid().optional(),
  roleId: z.string().optional(),
  search: z.string().optional(),
  hireDateFrom: z.string().date().optional(),
  hireDateTo: z.string().date().optional(),
  page: z.number().int().min(1).optional(),
  pageSize: z.number().int().min(1).max(MAX_PAGE_SIZE).optional(),
  sortBy: z.string().optional(),
  sortOrder: z.enum(['asc', 'desc']).optional()
});

export function registerEmployeeRoutes(fastify: FastifyInstance, employeeService: EmployeeService): void {
  fastify.post('/hr/api/v1/employees', {
    preHandler: [requireHrPermission(hrPermissions.EMPLOYEE_WRITE)],
    schema: {
      description: 'Create a new employee',
      tags: ['employees'],
      body: CreateEmployeeSchema,
      response: {
        [HTTP_STATUS.CREATED]: {
          description: 'Employee created successfully',
          type: 'object'
        },
        [HTTP_STATUS.BAD_REQUEST]: {
          description: 'Invalid input data',
          type: 'object'
        },
        [HTTP_STATUS.UNAUTHORIZED]: {
          description: 'Unauthorized',
          type: 'object'
        },
        [HTTP_STATUS.FORBIDDEN]: {
          description: 'Insufficient permissions',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Body: z.infer<typeof CreateEmployeeSchema> }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const { auth } = request;
      const employee = await employeeService.createEmployee({
        tenantId: auth.tenantId,
        createdBy: auth.userId,
        ...request.body
      });

      reply.code(HTTP_STATUS.CREATED).send(employee);
    } catch (error) {
      request.log.error({ err: error }, 'Error creating employee');
      reply.code(HTTP_STATUS.BAD_REQUEST).send({ error: error instanceof Error ? error.message : 'Failed to create employee' });
    }
  });

  fastify.get('/hr/api/v1/employees/:id', {
    preHandler: [requireHrPermission(hrPermissions.EMPLOYEE_READ)],
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
        [HTTP_STATUS.OK]: {
          description: 'Employee details',
          type: 'object'
        },
        [HTTP_STATUS.NOT_FOUND]: {
          description: 'Employee not found',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const employee = await employeeService.getEmployee(request.auth.tenantId, request.params.id);
      reply.send(employee);
    } catch (error) {
      request.log.error({ err: error }, 'Error getting employee');
      reply.code(HTTP_STATUS.NOT_FOUND).send({ error: error instanceof Error ? error.message : 'Employee not found' });
    }
  });

  fastify.get('/hr/api/v1/employees', {
    preHandler: [requireHrPermission(hrPermissions.EMPLOYEE_READ)],
    schema: {
      description: 'List employees with filtering and pagination',
      tags: ['employees'],
      querystring: EmployeeFiltersSchema,
      response: {
        [HTTP_STATUS.OK]: {
          description: 'List of employees',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Querystring: z.infer<typeof EmployeeFiltersSchema> }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const { auth } = request;
      const { page, pageSize, sortBy, sortOrder, ...filters } = request.query;
      const hasPagination = page !== undefined && pageSize !== undefined;

      const result = hasPagination
        ? await employeeService.listEmployees(auth.tenantId, filters, {
            page,
            pageSize,
            sortBy,
            sortOrder,
            filters
          })
        : await employeeService.listEmployees(auth.tenantId, filters);

      reply.send(result);
    } catch (error) {
      request.log.error({ err: error }, 'Error listing employees');
      reply.code(HTTP_STATUS.INTERNAL_SERVER_ERROR).send({ error: 'Failed to list employees' });
    }
  });

  fastify.patch('/hr/api/v1/employees/:id', {
    preHandler: [requireHrPermission(hrPermissions.EMPLOYEE_WRITE)],
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
        [HTTP_STATUS.OK]: {
          description: 'Employee updated successfully',
          type: 'object'
        },
        [HTTP_STATUS.NOT_FOUND]: {
          description: 'Employee not found',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { id: string }; Body: z.infer<typeof UpdateEmployeeSchema> }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const employee = await employeeService.updateEmployee({
        tenantId: request.auth.tenantId,
        employeeId: request.params.id,
        updates: request.body,
        updatedBy: request.auth.userId
      });

      reply.send(employee);
    } catch (error) {
      request.log.error({ err: error }, 'Error updating employee');
      reply.code(HTTP_STATUS.NOT_FOUND).send({ error: error instanceof Error ? error.message : 'Employee not found' });
    }
  });

  fastify.post('/hr/api/v1/employees/:id/roles', {
    preHandler: [requireHrPermission(hrPermissions.EMPLOYEE_WRITE)],
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
        [HTTP_STATUS.OK]: {
          description: 'Role assigned successfully',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { id: string }; Body: { roleId: string } }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const employee = await employeeService.assignRole({
        tenantId: request.auth.tenantId,
        employeeId: request.params.id,
        roleId: request.body.roleId,
        updatedBy: request.auth.userId
      });

      reply.send(employee);
    } catch (error) {
      request.log.error({ err: error }, 'Error assigning role');
      reply.code(HTTP_STATUS.BAD_REQUEST).send({ error: error instanceof Error ? error.message : 'Failed to assign role' });
    }
  });

  fastify.delete('/hr/api/v1/employees/:id/roles/:roleId', {
    preHandler: [requireHrPermission(hrPermissions.EMPLOYEE_WRITE)],
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
        [HTTP_STATUS.OK]: {
          description: 'Role removed successfully',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { id: string; roleId: string } }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const employee = await employeeService.removeRole({
        tenantId: request.auth.tenantId,
        employeeId: request.params.id,
        roleId: request.params.roleId,
        updatedBy: request.auth.userId
      });

      reply.send(employee);
    } catch (error) {
      request.log.error({ err: error }, 'Error removing role');
      reply.code(HTTP_STATUS.BAD_REQUEST).send({ error: error instanceof Error ? error.message : 'Failed to remove role' });
    }
  });

  fastify.post('/hr/api/v1/employees/:id/deactivate', {
    preHandler: [requireHrPermission(hrPermissions.EMPLOYEE_WRITE)],
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
        [HTTP_STATUS.OK]: {
          description: 'Employee deactivated successfully',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { id: string }; Body: { reason?: string; terminationDate?: string } }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const employee = await employeeService.deactivateEmployee({
        tenantId: request.auth.tenantId,
        employeeId: request.params.id,
        reason: request.body.reason,
        terminationDate: request.body.terminationDate,
        updatedBy: request.auth.userId
      });

      reply.send(employee);
    } catch (error) {
      request.log.error({ err: error }, 'Error deactivating employee');
      reply.code(HTTP_STATUS.BAD_REQUEST).send({ error: error instanceof Error ? error.message : 'Failed to deactivate employee' });
    }
  });

  fastify.post('/hr/api/v1/employees/:id/reactivate', {
    preHandler: [requireHrPermission(hrPermissions.EMPLOYEE_WRITE)],
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
        [HTTP_STATUS.OK]: {
          description: 'Employee reactivated successfully',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const employee = await employeeService.reactivateEmployee(
        request.auth.tenantId,
        request.params.id,
        request.auth.userId
      );

      reply.send(employee);
    } catch (error) {
      request.log.error({ err: error }, 'Error reactivating employee');
      reply.code(HTTP_STATUS.BAD_REQUEST).send({ error: error instanceof Error ? error.message : 'Failed to reactivate employee' });
    }
  });

  fastify.get('/hr/api/v1/employees/statistics', {
    preHandler: [requireHrPermission(hrPermissions.EMPLOYEE_READ)],
    schema: {
      description: 'Get employee statistics',
      tags: ['employees'],
      response: {
        [HTTP_STATUS.OK]: {
          description: 'Employee statistics',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const statistics = await employeeService.getEmployeeStatistics(request.auth.tenantId);
      reply.send(statistics);
    } catch (error) {
      request.log.error({ err: error }, 'Error getting employee statistics');
      reply.code(HTTP_STATUS.INTERNAL_SERVER_ERROR).send({ error: 'Failed to get employee statistics' });
    }
  });
}
