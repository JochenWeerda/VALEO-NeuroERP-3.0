/**
 * Time Entry Routes for VALEO NeuroERP 3.0 HR Domain
 * REST API endpoints for time tracking
 */

import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { z } from 'zod';
import { TimeEntryService } from '../../domain/services/time-entry-service';
import { requireHrPermission, hrPermissions } from '../middleware/auth';

// Request/Response schemas
const CreateTimeEntrySchema = z.object({
  employeeId: z.string().uuid(),
  date: z.string().date(),
  start: z.string().datetime(),
  end: z.string().datetime(),
  breakMinutes: z.number().int().min(0).max(480).optional(),
  projectId: z.string().uuid().optional(),
  costCenter: z.string().optional(),
  source: z.enum(['Manual', 'Terminal', 'Mobile']).optional()
});

const UpdateTimeEntrySchema = z.object({
  start: z.string().datetime().optional(),
  end: z.string().datetime().optional(),
  breakMinutes: z.number().int().min(0).max(480).optional(),
  projectId: z.string().uuid().optional(),
  costCenter: z.string().optional()
});

const TimeEntryFiltersSchema = z.object({
  employeeId: z.string().uuid().optional(),
  projectId: z.string().uuid().optional(),
  costCenter: z.string().optional(),
  status: z.enum(['Draft', 'Approved', 'Rejected']).optional(),
  source: z.enum(['Manual', 'Terminal', 'Mobile']).optional(),
  dateFrom: z.string().date().optional(),
  dateTo: z.string().date().optional(),
  approvedBy: z.string().uuid().optional(),
  page: z.number().int().min(1).optional(),
  pageSize: z.number().int().min(1).max(100).optional(),
  sortBy: z.string().optional(),
  sortOrder: z.enum(['asc', 'desc']).optional()
});

export function registerTimeEntryRoutes(fastify: FastifyInstance, timeEntryService: TimeEntryService) {
  // Create time entry
  fastify.post('/hr/api/v1/time-entries', {
    preHandler: [requireHrPermission(hrPermissions.TIME_WRITE)],
    schema: {
      description: 'Create a new time entry',
      tags: ['time-entries'],
      body: CreateTimeEntrySchema,
      response: {
        201: {
          description: 'Time entry created successfully',
          type: 'object'
        },
        400: {
          description: 'Invalid input data',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Body: z.infer<typeof CreateTimeEntrySchema> }>, reply: FastifyReply) => {
    try {
      const timeEntry = await timeEntryService.createTimeEntry({
        tenantId: request.auth!.tenantId,
        createdBy: request.auth!.userId,
        ...request.body
      });

      return reply.code(201).send(timeEntry);
    } catch (error) {
      console.error('Error creating time entry:', error);
      return reply.code(400).send({ error: error instanceof Error ? error.message : 'Failed to create time entry' });
    }
  });

  // Get time entry by ID
  fastify.get('/hr/api/v1/time-entries/:id', {
    preHandler: [requireHrPermission(hrPermissions.TIME_READ)],
    schema: {
      description: 'Get time entry by ID',
      tags: ['time-entries'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' }
        },
        required: ['id']
      },
      response: {
        200: {
          description: 'Time entry details',
          type: 'object'
        },
        404: {
          description: 'Time entry not found',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply) => {
    try {
      const timeEntry = await timeEntryService.getTimeEntry(request.auth!.tenantId, request.params.id);
      return reply.send(timeEntry);
    } catch (error) {
      console.error('Error getting time entry:', error);
      return reply.code(404).send({ error: error instanceof Error ? error.message : 'Time entry not found' });
    }
  });

  // List time entries
  fastify.get('/hr/api/v1/time-entries', {
    preHandler: [requireHrPermission(hrPermissions.TIME_READ)],
    schema: {
      description: 'List time entries with filtering and pagination',
      tags: ['time-entries'],
      querystring: TimeEntryFiltersSchema,
      response: {
        200: {
          description: 'List of time entries',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Querystring: z.infer<typeof TimeEntryFiltersSchema> }>, reply: FastifyReply) => {
    try {
      const { page, pageSize, sortBy, sortOrder, ...filters } = request.query;
      
      let result;
      if (page && pageSize) {
        result = await timeEntryService.listTimeEntries(request.auth!.tenantId, filters, {
          page,
          pageSize,
          sortBy,
          sortOrder,
          filters
        });
      } else {
        result = await timeEntryService.listTimeEntries(request.auth!.tenantId, filters);
      }

      return reply.send(result);
    } catch (error) {
      console.error('Error listing time entries:', error);
      return reply.code(500).send({ error: 'Failed to list time entries' });
    }
  });

  // Update time entry
  fastify.patch('/hr/api/v1/time-entries/:id', {
    preHandler: [requireHrPermission(hrPermissions.TIME_WRITE)],
    schema: {
      description: 'Update time entry',
      tags: ['time-entries'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' }
        },
        required: ['id']
      },
      body: UpdateTimeEntrySchema,
      response: {
        200: {
          description: 'Time entry updated successfully',
          type: 'object'
        },
        404: {
          description: 'Time entry not found',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ 
    Params: { id: string }, 
    Body: z.infer<typeof UpdateTimeEntrySchema> 
  }>, reply: FastifyReply) => {
    try {
      const timeEntry = await timeEntryService.updateTimeEntry({
        tenantId: request.auth!.tenantId,
        timeEntryId: request.params.id,
        updates: request.body,
        updatedBy: request.auth!.userId
      });

      return reply.send(timeEntry);
    } catch (error) {
      console.error('Error updating time entry:', error);
      return reply.code(404).send({ error: error instanceof Error ? error.message : 'Time entry not found' });
    }
  });

  // Approve time entry
  fastify.post('/hr/api/v1/time-entries/:id/approve', {
    preHandler: [requireHrPermission(hrPermissions.TIME_APPROVE)],
    schema: {
      description: 'Approve time entry',
      tags: ['time-entries'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' }
        },
        required: ['id']
      },
      response: {
        200: {
          description: 'Time entry approved successfully',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply) => {
    try {
      const timeEntry = await timeEntryService.approveTimeEntry({
        tenantId: request.auth!.tenantId,
        timeEntryId: request.params.id,
        approvedBy: request.auth!.userId
      });

      return reply.send(timeEntry);
    } catch (error) {
      console.error('Error approving time entry:', error);
      return reply.code(400).send({ error: error instanceof Error ? error.message : 'Failed to approve time entry' });
    }
  });

  // Reject time entry
  fastify.post('/hr/api/v1/time-entries/:id/reject', {
    preHandler: [requireHrPermission(hrPermissions.TIME_APPROVE)],
    schema: {
      description: 'Reject time entry',
      tags: ['time-entries'],
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
          reason: { type: 'string' }
        }
      },
      response: {
        200: {
          description: 'Time entry rejected successfully',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ 
    Params: { id: string }, 
    Body: { reason?: string } 
  }>, reply: FastifyReply) => {
    try {
      const timeEntry = await timeEntryService.rejectTimeEntry({
        tenantId: request.auth!.tenantId,
        timeEntryId: request.params.id,
        rejectedBy: request.auth!.userId,
        reason: request.body.reason
      });

      return reply.send(timeEntry);
    } catch (error) {
      console.error('Error rejecting time entry:', error);
      return reply.code(400).send({ error: error instanceof Error ? error.message : 'Failed to reject time entry' });
    }
  });

  // Get employee time entries
  fastify.get('/hr/api/v1/employees/:employeeId/time-entries', {
    preHandler: [requireHrPermission(hrPermissions.TIME_READ)],
    schema: {
      description: 'Get time entries for a specific employee',
      tags: ['time-entries'],
      params: {
        type: 'object',
        properties: {
          employeeId: { type: 'string', format: 'uuid' }
        },
        required: ['employeeId']
      },
      querystring: {
        type: 'object',
        properties: {
          from: { type: 'string', format: 'date' },
          to: { type: 'string', format: 'date' }
        }
      },
      response: {
        200: {
          description: 'Employee time entries',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ 
    Params: { employeeId: string }, 
    Querystring: { from?: string, to?: string } 
  }>, reply: FastifyReply) => {
    try {
      const timeEntries = await timeEntryService.getEmployeeTimeEntries(
        request.auth!.tenantId,
        request.params.employeeId,
        request.query.from,
        request.query.to
      );

      return reply.send(timeEntries);
    } catch (error) {
      console.error('Error getting employee time entries:', error);
      return reply.code(500).send({ error: 'Failed to get employee time entries' });
    }
  });

  // Get pending approvals
  fastify.get('/hr/api/v1/time-entries/pending', {
    preHandler: [requireHrPermission(hrPermissions.TIME_APPROVE)],
    schema: {
      description: 'Get time entries pending approval',
      tags: ['time-entries'],
      response: {
        200: {
          description: 'Time entries pending approval',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const pendingEntries = await timeEntryService.getPendingApprovals(request.auth!.tenantId);
      return reply.send(pendingEntries);
    } catch (error) {
      console.error('Error getting pending approvals:', error);
      return reply.code(500).send({ error: 'Failed to get pending approvals' });
    }
  });

  // Get employee time summary
  fastify.get('/hr/api/v1/employees/:employeeId/time-summary', {
    preHandler: [requireHrPermission(hrPermissions.TIME_READ)],
    schema: {
      description: 'Get time summary for a specific employee',
      tags: ['time-entries'],
      params: {
        type: 'object',
        properties: {
          employeeId: { type: 'string', format: 'uuid' }
        },
        required: ['employeeId']
      },
      querystring: {
        type: 'object',
        properties: {
          from: { type: 'string', format: 'date' },
          to: { type: 'string', format: 'date' }
        },
        required: ['from', 'to']
      },
      response: {
        200: {
          description: 'Employee time summary',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ 
    Params: { employeeId: string }, 
    Querystring: { from: string, to: string } 
  }>, reply: FastifyReply) => {
    try {
      const summary = await timeEntryService.getEmployeeTimeSummary(
        request.auth!.tenantId,
        request.params.employeeId,
        request.query.from,
        request.query.to
      );

      return reply.send(summary);
    } catch (error) {
      console.error('Error getting employee time summary:', error);
      return reply.code(500).send({ error: 'Failed to get employee time summary' });
    }
  });

  // Get monthly summary
  fastify.get('/hr/api/v1/employees/:employeeId/monthly-summary/:year/:month', {
    preHandler: [requireHrPermission(hrPermissions.TIME_READ)],
    schema: {
      description: 'Get monthly time summary for a specific employee',
      tags: ['time-entries'],
      params: {
        type: 'object',
        properties: {
          employeeId: { type: 'string', format: 'uuid' },
          year: { type: 'number', minimum: 2020, maximum: 2030 },
          month: { type: 'number', minimum: 1, maximum: 12 }
        },
        required: ['employeeId', 'year', 'month']
      },
      response: {
        200: {
          description: 'Monthly time summary',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ 
    Params: { employeeId: string, year: string, month: string } 
  }>, reply: FastifyReply) => {
    try {
      const summary = await timeEntryService.getMonthlySummary(
        request.auth!.tenantId,
        request.params.employeeId,
        parseInt(request.params.year),
        parseInt(request.params.month)
      );

      return reply.send(summary);
    } catch (error) {
      console.error('Error getting monthly summary:', error);
      return reply.code(500).send({ error: 'Failed to get monthly summary' });
    }
  });

  // Get yearly summary
  fastify.get('/hr/api/v1/employees/:employeeId/yearly-summary/:year', {
    preHandler: [requireHrPermission(hrPermissions.TIME_READ)],
    schema: {
      description: 'Get yearly time summary for a specific employee',
      tags: ['time-entries'],
      params: {
        type: 'object',
        properties: {
          employeeId: { type: 'string', format: 'uuid' },
          year: { type: 'number', minimum: 2020, maximum: 2030 }
        },
        required: ['employeeId', 'year']
      },
      response: {
        200: {
          description: 'Yearly time summary',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ 
    Params: { employeeId: string, year: string } 
  }>, reply: FastifyReply) => {
    try {
      const summary = await timeEntryService.getYearlySummary(
        request.auth!.tenantId,
        request.params.employeeId,
        parseInt(request.params.year)
      );

      return reply.send(summary);
    } catch (error) {
      console.error('Error getting yearly summary:', error);
      return reply.code(500).send({ error: 'Failed to get yearly summary' });
    }
  });
}

