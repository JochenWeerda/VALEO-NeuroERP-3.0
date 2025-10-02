/**
 * Employee Routes for VALEO NeuroERP 3.0 HR Domain
 * REST API endpoints for employee management
 */

import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { z } from 'zod';
import { EmployeeService } from '../../domain/services/employee-service';
import { requireHrPermission, hrPermissions } from '../middleware/auth';

// Request/Response schemas
const CreateEmployeeSchema = z.object({
  employeeNumber: z.string().min(1).max(50),
  person: z.object({
    firstName: z.string().min(1).max(100),
    lastName: z.string().min(1).max(100),
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
  pageSize: z.number().int().min(1).max(100).optional(),
  sortBy: z.string().optional(),
  sortOrder: z.enum(['asc', 'desc']).optional()
});

export function registerEmployeeRoutes(fastify: FastifyInstance, employeeService: EmployeeService) {
  // Create employee
  fastify.post('/hr/api/v1/employees', {
    preHandler: [requireHrPermission(hrPermissions.EMPLOYEE_WRITE)],
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
  }, async (request: FastifyRequest<{ Body: z.infer<typeof CreateEmployeeSchema> }>, reply: FastifyReply) => {
    try {
      const employee = await employeeService.createEmployee({
        tenantId: request.auth!.tenantId,
        createdBy: request.auth!.userId,
        ...request.body
      });

      return reply.code(201).send(employee);
    } catch (error) {
      console.error('Error creating employee:', error);
      return reply.code(400).send({ error: error instanceof Error ? error.message : 'Failed to create employee' });
    }
  });

  // Get employee by ID
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
  }, async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply) => {
    try {
      const employee = await employeeService.getEmployee(request.auth!.tenantId, request.params.id);
      return reply.send(employee);
    } catch (error) {
      console.error('Error getting employee:', error);
      return reply.code(404).send({ error: error instanceof Error ? error.message : 'Employee not found' });
    }
  });

  // List employees
  fastify.get('/hr/api/v1/employees', {
    preHandler: [requireHrPermission(hrPermissions.EMPLOYEE_READ)],
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
  }, async (request: FastifyRequest<{ Querystring: z.infer<typeof EmployeeFiltersSchema> }>, reply: FastifyReply) => {
    try {
      const { page, pageSize, sortBy, sortOrder, ...filters } = request.query;
      
      let result;
      if (page && pageSize) {
        result = await employeeService.listEmployees(request.auth!.tenantId, filters, {
          page,
          pageSize,
          sortBy,
          sortOrder,
          filters
        });
      } else {
        result = await employeeService.listEmployees(request.auth!.tenantId, filters);
      }

      return reply.send(result);
    } catch (error) {
      console.error('Error listing employees:', error);
      return reply.code(500).send({ error: 'Failed to list employees' });
    }
  });

  // Update employee
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
  }, async (request: FastifyRequest<{ 
    Params: { id: string }, 
    Body: z.infer<typeof UpdateEmployeeSchema> 
  }>, reply: FastifyReply) => {
    try {
      const employee = await employeeService.updateEmployee({
        tenantId: request.auth!.tenantId,
        employeeId: request.params.id,
        updates: request.body,
        updatedBy: request.auth!.userId
      });

      return reply.send(employee);
    } catch (error) {
      console.error('Error updating employee:', error);
      return reply.code(404).send({ error: error instanceof Error ? error.message : 'Employee not found' });
    }
  });

  // Assign role to employee
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
        200: {
          description: 'Role assigned successfully',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ 
    Params: { id: string }, 
    Body: { roleId: string } 
  }>, reply: FastifyReply) => {
    try {
      const employee = await employeeService.assignRole({
        tenantId: request.auth!.tenantId,
        employeeId: request.params.id,
        roleId: request.body.roleId,
        updatedBy: request.auth!.userId
      });

      return reply.send(employee);
    } catch (error) {
      console.error('Error assigning role:', error);
      return reply.code(400).send({ error: error instanceof Error ? error.message : 'Failed to assign role' });
    }
  });

  // Remove role from employee
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
        200: {
          description: 'Role removed successfully',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ 
    Params: { id: string, roleId: string } 
  }>, reply: FastifyReply) => {
    try {
      const employee = await employeeService.removeRole({
        tenantId: request.auth!.tenantId,
        employeeId: request.params.id,
        roleId: request.params.roleId,
        updatedBy: request.auth!.userId
      });

      return reply.send(employee);
    } catch (error) {
      console.error('Error removing role:', error);
      return reply.code(400).send({ error: error instanceof Error ? error.message : 'Failed to remove role' });
    }
  });

  // Deactivate employee
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
        200: {
          description: 'Employee deactivated successfully',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ 
    Params: { id: string }, 
    Body: { reason?: string, terminationDate?: string } 
  }>, reply: FastifyReply) => {
    try {
      const employee = await employeeService.deactivateEmployee({
        tenantId: request.auth!.tenantId,
        employeeId: request.params.id,
        reason: request.body.reason,
        terminationDate: request.body.terminationDate,
        updatedBy: request.auth!.userId
      });

      return reply.send(employee);
    } catch (error) {
      console.error('Error deactivating employee:', error);
      return reply.code(400).send({ error: error instanceof Error ? error.message : 'Failed to deactivate employee' });
    }
  });

  // Reactivate employee
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
        200: {
          description: 'Employee reactivated successfully',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply) => {
    try {
      const employee = await employeeService.reactivateEmployee(
        request.auth!.tenantId,
        request.params.id,
        request.auth!.userId
      );

      return reply.send(employee);
    } catch (error) {
      console.error('Error reactivating employee:', error);
      return reply.code(400).send({ error: error instanceof Error ? error.message : 'Failed to reactivate employee' });
    }
  });

  // Get employee statistics
  fastify.get('/hr/api/v1/employees/statistics', {
    preHandler: [requireHrPermission(hrPermissions.EMPLOYEE_READ)],
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
  }, async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const statistics = await employeeService.getEmployeeStatistics(request.auth!.tenantId);
      return reply.send(statistics);
    } catch (error) {
      console.error('Error getting employee statistics:', error);
      return reply.code(500).send({ error: 'Failed to get employee statistics' });
    }
  });
}

