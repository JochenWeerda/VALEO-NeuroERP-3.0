/**
 * Change Log REST API Routes
 * Audit Trail Management
 */

import { FastifyInstance } from 'fastify';
import { ChangeLogService } from '../../domain/services/change-log-service';
import { ChangeLogRepository } from '../../infra/repositories/change-log-repository';

// Initialize services
const changeLogRepository = new ChangeLogRepository();
const changeLogService = new ChangeLogService({ changeLogRepository });

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

function getAuthenticatedUserInfo(request: any): {
  userId: string;
  userName?: string;
  userEmail?: string;
  ipAddress?: string;
  userAgent?: string;
} {
  return {
    userId: request.user?.id || 'system',
    userName: request.user?.name,
    userEmail: request.user?.email,
    ipAddress: request.ip,
    userAgent: request.headers['user-agent'],
  };
}

export async function registerChangeLogRoutes(fastify: FastifyInstance) {
  fastify.register(async (changeLogRoutes) => {

    // GET /change-logs - List change logs with filtering
    changeLogRoutes.get('/', {
      schema: {
        description: 'List change logs with filtering',
        tags: ['Change Logs'],
        querystring: {
          type: 'object',
          properties: {
            tenantId: { type: 'string' },
            entityType: { type: 'string' },
            entityId: { type: 'string' },
            action: {
              type: 'string',
              enum: ['CREATE', 'UPDATE', 'DELETE', 'CANCEL', 'AMEND', 'RESTORE'],
            },
            userId: { type: 'string' },
            dateFrom: { type: 'string', format: 'date-time' },
            dateTo: { type: 'string', format: 'date-time' },
            hasReason: { type: 'boolean' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      const filters = {
        tenantId: query.tenantId,
        entityType: query.entityType,
        entityId: query.entityId,
        action: query.action,
        userId: query.userId,
        dateFrom: query.dateFrom ? new Date(query.dateFrom) : undefined,
        dateTo: query.dateTo ? new Date(query.dateTo) : undefined,
        hasReason: query.hasReason,
      };
      try {
        const changeLogs = await changeLogService.getChangeLogs(filters);
        return reply.send({ data: changeLogs });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /change-logs/:id - Get change log by ID
    changeLogRoutes.get('/:id', {
      schema: {
        description: 'Get change log by ID',
        tags: ['Change Logs'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      try {
        const changeLog = await changeLogService.getChangeLog(id);
        if (!changeLog) {
          return reply.status(404).send({ error: 'Change log not found' });
        }
        return reply.send(changeLog);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /change-logs/audit-trail/:entityType/:entityId - Get audit trail for entity
    changeLogRoutes.get('/audit-trail/:entityType/:entityId', {
      schema: {
        description: 'Get audit trail for a specific entity',
        tags: ['Change Logs'],
        params: {
          type: 'object',
          properties: {
            entityType: { type: 'string' },
            entityId: { type: 'string' },
          },
          required: ['entityType', 'entityId'],
        },
        querystring: {
          type: 'object',
          properties: {
            action: { type: 'string' },
            dateFrom: { type: 'string', format: 'date-time' },
            dateTo: { type: 'string', format: 'date-time' },
          },
        },
      },
    }, async (request, reply) => {
      const { entityType, entityId } = request.params as { entityType: string; entityId: string };
      const query = request.query as any;
      const filters = {
        action: query.action,
        dateFrom: query.dateFrom ? new Date(query.dateFrom) : undefined,
        dateTo: query.dateTo ? new Date(query.dateTo) : undefined,
      };
      try {
        const auditTrail = await changeLogService.getAuditTrail(entityType, entityId, filters);
        return reply.send({ data: auditTrail });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /change-logs - Create change log (for manual logging)
    changeLogRoutes.post('/', {
      schema: {
        description: 'Create a change log entry (usually called automatically by services)',
        tags: ['Change Logs'],
        body: {
          type: 'object',
          required: ['tenantId', 'entityType', 'entityId', 'action', 'userId'],
          properties: {
            tenantId: { type: 'string' },
            entityType: { type: 'string' },
            entityId: { type: 'string' },
            action: {
              type: 'string',
              enum: ['CREATE', 'UPDATE', 'DELETE', 'CANCEL', 'AMEND', 'RESTORE'],
            },
            reason: { type: 'string' },
            oldValue: { type: 'object' },
            newValue: { type: 'object' },
            changedFields: { type: 'array', items: { type: 'string' } },
            userId: { type: 'string' },
            userName: { type: 'string' },
            userEmail: { type: 'string' },
            metadata: { type: 'object' },
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      const userInfo = getAuthenticatedUserInfo(request);
      try {
        const changeLog = await changeLogService.logChange({
          ...body,
          userId: body.userId || userInfo.userId,
          userName: body.userName || userInfo.userName,
          userEmail: body.userEmail || userInfo.userEmail,
          ipAddress: body.ipAddress || userInfo.ipAddress,
          userAgent: body.userAgent || userInfo.userAgent,
        });
        return reply.status(201).send(changeLog);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /change-logs/stats - Get change log statistics
    changeLogRoutes.get('/stats', {
      schema: {
        description: 'Get change log statistics',
        tags: ['Change Logs'],
        querystring: {
          type: 'object',
          properties: {
            tenantId: { type: 'string' },
            entityType: { type: 'string' },
            dateFrom: { type: 'string', format: 'date-time' },
            dateTo: { type: 'string', format: 'date-time' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      const filters = {
        tenantId: query.tenantId,
        entityType: query.entityType,
        dateFrom: query.dateFrom ? new Date(query.dateFrom) : undefined,
        dateTo: query.dateTo ? new Date(query.dateTo) : undefined,
      };
      try {
        const total = await changeLogService.countChangeLogs(filters);
        
        // Get counts by action
        const createCount = await changeLogService.countChangeLogs({ ...filters, action: 'CREATE' });
        const updateCount = await changeLogService.countChangeLogs({ ...filters, action: 'UPDATE' });
        const deleteCount = await changeLogService.countChangeLogs({ ...filters, action: 'DELETE' });
        const cancelCount = await changeLogService.countChangeLogs({ ...filters, action: 'CANCEL' });
        const amendCount = await changeLogService.countChangeLogs({ ...filters, action: 'AMEND' });
        const restoreCount = await changeLogService.countChangeLogs({ ...filters, action: 'RESTORE' });

        return reply.send({
          total,
          byAction: {
            CREATE: createCount,
            UPDATE: updateCount,
            DELETE: deleteCount,
            CANCEL: cancelCount,
            AMEND: amendCount,
            RESTORE: restoreCount,
          },
        });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });
  });
}

