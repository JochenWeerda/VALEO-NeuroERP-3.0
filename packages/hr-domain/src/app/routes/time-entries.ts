/**
 * Time Entry Routes for VALEO NeuroERP 3.0 HR Domain
 * REST API endpoints for time tracking
 */

import { FastifyInstance, FastifyReply, FastifyRequest } from 'fastify';
import { z } from 'zod';
import { TimeEntryService } from '../../domain/services/time-entry-service';
import { type AuthContext, hrPermissions, requireHrPermission } from '../middleware/auth';

const MAX_BREAK_MINUTES = 480;
const MAX_PAGE_SIZE = 100;
const MIN_YEAR = 2020;
const MAX_YEAR = 2030;
const MIN_MONTH = 1;
const MAX_MONTH = 12;

const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500
} as const;

const AUTH_REQUIRED = { error: 'Authentication required' } as const;

type AuthenticatedRequest = FastifyRequest & { auth: AuthContext };

function ensureAuth(request: FastifyRequest, reply: FastifyReply): request is AuthenticatedRequest {
  if (!request.auth) {
    reply.code(HTTP_STATUS.UNAUTHORIZED).send(AUTH_REQUIRED);
    return false;
  }
  return true;
}

const CreateTimeEntrySchema = z.object({
  employeeId: z.string().uuid(),
  date: z.string().date(),
  start: z.string().datetime(),
  end: z.string().datetime(),
  breakMinutes: z.number().int().min(0).max(MAX_BREAK_MINUTES).optional(),
  projectId: z.string().uuid().optional(),
  costCenter: z.string().optional(),
  source: z.enum(['Manual', 'Terminal', 'Mobile']).optional()
});

const UpdateTimeEntrySchema = z.object({
  start: z.string().datetime().optional(),
  end: z.string().datetime().optional(),
  breakMinutes: z.number().int().min(0).max(MAX_BREAK_MINUTES).optional(),
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
  pageSize: z.number().int().min(1).max(MAX_PAGE_SIZE).optional(),
  sortBy: z.string().optional(),
  sortOrder: z.enum(['asc', 'desc']).optional()
});

export function registerTimeEntryRoutes(fastify: FastifyInstance, timeEntryService: TimeEntryService): void {
  fastify.post('/hr/api/v1/time-entries', {
    preHandler: [requireHrPermission(hrPermissions.TIME_WRITE)],
    schema: {
      description: 'Create a new time entry',
      tags: ['time-entries'],
      body: CreateTimeEntrySchema,
      response: {
        [HTTP_STATUS.CREATED]: {
          description: 'Time entry created successfully',
          type: 'object'
        },
        [HTTP_STATUS.BAD_REQUEST]: {
          description: 'Invalid input data',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Body: z.infer<typeof CreateTimeEntrySchema> }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const { auth } = request;
      const timeEntry = await timeEntryService.createTimeEntry({
        tenantId: auth.tenantId,
        createdBy: auth.userId,
        ...request.body
      });

      reply.code(HTTP_STATUS.CREATED).send(timeEntry);
    } catch (error) {
      request.log.error({ err: error }, 'Error creating time entry');
      reply.code(HTTP_STATUS.BAD_REQUEST).send({ error: error instanceof Error ? error.message : 'Failed to create time entry' });
    }
  });

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
        [HTTP_STATUS.OK]: {
          description: 'Time entry details',
          type: 'object'
        },
        [HTTP_STATUS.NOT_FOUND]: {
          description: 'Time entry not found',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const timeEntry = await timeEntryService.getTimeEntry(request.auth.tenantId, request.params.id);
      reply.send(timeEntry);
    } catch (error) {
      request.log.error({ err: error }, 'Error getting time entry');
      reply.code(HTTP_STATUS.NOT_FOUND).send({ error: error instanceof Error ? error.message : 'Time entry not found' });
    }
  });

  fastify.get('/hr/api/v1/time-entries', {
    preHandler: [requireHrPermission(hrPermissions.TIME_READ)],
    schema: {
      description: 'List time entries with filtering and pagination',
      tags: ['time-entries'],
      querystring: TimeEntryFiltersSchema,
      response: {
        [HTTP_STATUS.OK]: {
          description: 'List of time entries or paginated result',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Querystring: z.infer<typeof TimeEntryFiltersSchema> }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const { auth } = request;
      const { page, pageSize, sortBy, sortOrder, ...filters } = request.query;
      const hasPagination = page !== undefined && pageSize !== undefined;

      const result = hasPagination
        ? await timeEntryService.listTimeEntries(auth.tenantId, filters, {
            page,
            pageSize,
            sortBy,
            sortOrder,
            filters
          })
        : await timeEntryService.listTimeEntries(auth.tenantId, filters);

      reply.send(result);
    } catch (error) {
      request.log.error({ err: error }, 'Error listing time entries');
      reply.code(HTTP_STATUS.INTERNAL_SERVER_ERROR).send({ error: 'Failed to list time entries' });
    }
  });

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
        [HTTP_STATUS.OK]: {
          description: 'Time entry updated successfully',
          type: 'object'
        },
        [HTTP_STATUS.NOT_FOUND]: {
          description: 'Time entry not found',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { id: string }; Body: z.infer<typeof UpdateTimeEntrySchema> }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const timeEntry = await timeEntryService.updateTimeEntry({
        tenantId: request.auth.tenantId,
        timeEntryId: request.params.id,
        updates: request.body,
        updatedBy: request.auth.userId
      });

      reply.send(timeEntry);
    } catch (error) {
      request.log.error({ err: error }, 'Error updating time entry');
      reply.code(HTTP_STATUS.NOT_FOUND).send({ error: error instanceof Error ? error.message : 'Time entry not found' });
    }
  });

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
        [HTTP_STATUS.OK]: {
          description: 'Time entry approved',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const timeEntry = await timeEntryService.approveTimeEntry({
        tenantId: request.auth.tenantId,
        timeEntryId: request.params.id,
        approvedBy: request.auth.userId
      });

      reply.send(timeEntry);
    } catch (error) {
      request.log.error({ err: error }, 'Error approving time entry');
      reply.code(HTTP_STATUS.BAD_REQUEST).send({ error: error instanceof Error ? error.message : 'Failed to approve time entry' });
    }
  });

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
        [HTTP_STATUS.OK]: {
          description: 'Time entry rejected',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { id: string }; Body: { reason?: string } }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const timeEntry = await timeEntryService.rejectTimeEntry({
        tenantId: request.auth.tenantId,
        timeEntryId: request.params.id,
        rejectedBy: request.auth.userId,
        reason: request.body.reason
      });

      reply.send(timeEntry);
    } catch (error) {
      request.log.error({ err: error }, 'Error rejecting time entry');
      reply.code(HTTP_STATUS.BAD_REQUEST).send({ error: error instanceof Error ? error.message : 'Failed to reject time entry' });
    }
  });

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
        [HTTP_STATUS.OK]: {
          description: 'Employee time entries',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { employeeId: string }; Querystring: { from?: string; to?: string } }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const entries = await timeEntryService.getEmployeeTimeEntries(
        request.auth.tenantId,
        request.params.employeeId,
        request.query.from,
        request.query.to
      );

      reply.send(entries);
    } catch (error) {
      request.log.error({ err: error }, 'Error getting employee time entries');
      reply.code(HTTP_STATUS.INTERNAL_SERVER_ERROR).send({ error: 'Failed to get employee time entries' });
    }
  });

  fastify.get('/hr/api/v1/time-entries/pending', {
    preHandler: [requireHrPermission(hrPermissions.TIME_APPROVE)],
    schema: {
      description: 'Get time entries pending approval',
      tags: ['time-entries'],
      response: {
        [HTTP_STATUS.OK]: {
          description: 'Time entries pending approval',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const pendingEntries = await timeEntryService.getPendingApprovals(request.auth.tenantId);
      reply.send(pendingEntries);
    } catch (error) {
      request.log.error({ err: error }, 'Error getting pending approvals');
      reply.code(HTTP_STATUS.INTERNAL_SERVER_ERROR).send({ error: 'Failed to get pending approvals' });
    }
  });

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
        [HTTP_STATUS.OK]: {
          description: 'Employee time summary',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { employeeId: string }; Querystring: { from: string; to: string } }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const summary = await timeEntryService.getEmployeeTimeSummary(
        request.auth.tenantId,
        request.params.employeeId,
        request.query.from,
        request.query.to
      );

      reply.send(summary);
    } catch (error) {
      request.log.error({ err: error }, 'Error getting employee time summary');
      reply.code(HTTP_STATUS.INTERNAL_SERVER_ERROR).send({ error: 'Failed to get employee time summary' });
    }
  });

  fastify.get('/hr/api/v1/employees/:employeeId/monthly-summary/:year/:month', {
    preHandler: [requireHrPermission(hrPermissions.TIME_READ)],
    schema: {
      description: 'Get monthly time summary for a specific employee',
      tags: ['time-entries'],
      params: {
        type: 'object',
        properties: {
          employeeId: { type: 'string', format: 'uuid' },
          year: { type: 'number', minimum: MIN_YEAR, maximum: MAX_YEAR },
          month: { type: 'number', minimum: MIN_MONTH, maximum: MAX_MONTH }
        },
        required: ['employeeId', 'year', 'month']
      },
      response: {
        [HTTP_STATUS.OK]: {
          description: 'Monthly time summary',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { employeeId: string; year: string; month: string } }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const summary = await timeEntryService.getMonthlySummary(
        request.auth.tenantId,
        request.params.employeeId,
        Number.parseInt(request.params.year, 10),
        Number.parseInt(request.params.month, 10)
      );

      reply.send(summary);
    } catch (error) {
      request.log.error({ err: error }, 'Error getting monthly summary');
      reply.code(HTTP_STATUS.INTERNAL_SERVER_ERROR).send({ error: 'Failed to get monthly summary' });
    }
  });

  fastify.get('/hr/api/v1/employees/:employeeId/yearly-summary/:year', {
    preHandler: [requireHrPermission(hrPermissions.TIME_READ)],
    schema: {
      description: 'Get yearly time summary for a specific employee',
      tags: ['time-entries'],
      params: {
        type: 'object',
        properties: {
          employeeId: { type: 'string', format: 'uuid' },
          year: { type: 'number', minimum: MIN_YEAR, maximum: MAX_YEAR }
        },
        required: ['employeeId', 'year']
      },
      response: {
        [HTTP_STATUS.OK]: {
          description: 'Yearly time summary',
          type: 'object'
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { employeeId: string; year: string } }>, reply: FastifyReply): Promise<void> => {
    if (!ensureAuth(request, reply)) {
      return;
    }

    try {
      const summary = await timeEntryService.getYearlySummary(
        request.auth.tenantId,
        request.params.employeeId,
        Number.parseInt(request.params.year, 10)
      );

      reply.send(summary);
    } catch (error) {
      request.log.error({ err: error }, 'Error getting yearly summary');
      reply.code(HTTP_STATUS.INTERNAL_SERVER_ERROR).send({ error: 'Failed to get yearly summary' });
    }
  });
}
