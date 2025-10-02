import { FastifyInstance } from 'fastify';
import { ScheduleRepository } from '../../infra/repo/schedule-repository';
import { SchedulingService } from '../../domain/services/scheduling-service';
import { NoOpEventPublisher } from '../../infra/messaging/publisher';
import { ScheduleEntity } from '../../domain/entities';

export async function registerScheduleRoutes(
  fastify: FastifyInstance,
  scheduleRepository: ScheduleRepository
) {
  const eventPublisher = new NoOpEventPublisher();
  const schedulingService = new SchedulingService(scheduleRepository, eventPublisher, {
    maxRetries: 3,
    defaultTimezone: 'Europe/Berlin',
    enableBackfill: false,
  });

  // Create schedule
  fastify.post('/schedules', {
    schema: {
      description: 'Create a new schedule',
      tags: ['schedules'],
      body: {
        type: 'object',
        required: ['tenantId', 'name', 'trigger', 'target'],
        properties: {
          tenantId: { type: 'string' },
          name: { type: 'string' },
          description: { type: 'string' },
          tz: { type: 'string', default: 'Europe/Berlin' },
          trigger: {
            type: 'object',
            required: ['type'],
            properties: {
              type: { type: 'string', enum: ['CRON', 'RRULE', 'FIXED_DELAY', 'ONE_SHOT'] },
              cron: { type: 'string' },
              rrule: { type: 'string' },
              delaySec: { type: 'number' },
              startAt: { type: 'string', format: 'date-time' },
            },
          },
          target: {
            type: 'object',
            required: ['kind'],
            properties: {
              kind: { type: 'string', enum: ['EVENT', 'HTTP', 'QUEUE'] },
              eventTopic: { type: 'string' },
              http: {
                type: 'object',
                properties: {
                  url: { type: 'string' },
                  method: { type: 'string', enum: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] },
                  headers: { type: 'object' },
                  hmacKeyRef: { type: 'string' },
                },
              },
              queue: {
                type: 'object',
                properties: {
                  topic: { type: 'string' },
                },
              },
            },
          },
          payload: { type: 'object' },
          calendar: {
            type: 'object',
            properties: {
              holidaysCode: { type: 'string' },
              businessDaysOnly: { type: 'boolean' },
            },
          },
          enabled: { type: 'boolean', default: true },
        },
      },
      response: {
        201: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            tenantId: { type: 'string' },
            name: { type: 'string' },
            enabled: { type: 'boolean' },
            createdAt: { type: 'string', format: 'date-time' },
          },
        },
      },
    },
    handler: async (request, reply) => {
      const body = request.body as any;

      try {
        const schedule = new ScheduleEntity({
          tenantId: body.tenantId,
          name: body.name,
          description: body.description,
          tz: body.tz || 'Europe/Berlin',
          trigger: body.trigger,
          target: body.target,
          payload: body.payload,
          calendar: body.calendar,
          enabled: body.enabled ?? true,
        });

        // Calculate next fire time
        const nextFireAt = await schedulingService.calculateNextFireTime(schedule);

        const created = await scheduleRepository.create(
          scheduleRepository.toDatabaseRecord({
            ...schedule,
            nextFireAt: nextFireAt || undefined,
          } as ScheduleEntity)
        );

        reply.code(201).send({
          id: created.id,
          tenantId: created.tenantId,
          name: created.name,
          enabled: created.enabled,
          createdAt: created.createdAt.toISOString(),
        });
      } catch (error) {
        reply.code(400).send({
          error: error instanceof Error ? error.message : 'Invalid schedule configuration',
        });
      }
    },
  });

  // Get schedule by ID
  fastify.get('/schedules/:id', {
    schema: {
      description: 'Get schedule by ID',
      tags: ['schedules'],
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { type: 'string' },
        },
      },
      response: {
        200: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            tenantId: { type: 'string' },
            name: { type: 'string' },
            description: { type: 'string' },
            tz: { type: 'string' },
            trigger: { type: 'object' },
            target: { type: 'object' },
            enabled: { type: 'boolean' },
            nextFireAt: { type: 'string', format: 'date-time' },
            lastFireAt: { type: 'string', format: 'date-time' },
            createdAt: { type: 'string', format: 'date-time' },
            updatedAt: { type: 'string', format: 'date-time' },
            version: { type: 'number' },
          },
        },
      },
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };

      const schedule = await scheduleRepository.findById(id);
      if (!schedule) {
        return reply.code(404).send({ error: 'Schedule not found' });
      }

      reply.send({
        id: schedule.id,
        tenantId: schedule.tenantId,
        name: schedule.name,
        description: schedule.description,
        tz: schedule.tz,
        trigger: schedule.trigger,
        target: schedule.target,
        enabled: schedule.enabled,
        nextFireAt: schedule.nextFireAt?.toISOString(),
        lastFireAt: schedule.lastFireAt?.toISOString(),
        createdAt: schedule.createdAt.toISOString(),
        updatedAt: schedule.updatedAt.toISOString(),
        version: schedule.version,
      });
    },
  });

  // List schedules
  fastify.get('/schedules', {
    schema: {
      description: 'List schedules with pagination',
      tags: ['schedules'],
      querystring: {
        type: 'object',
        properties: {
          tenantId: { type: 'string' },
          enabled: { type: 'boolean' },
          page: { type: 'integer', minimum: 1, default: 1 },
          pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
        },
      },
      response: {
        200: {
          type: 'object',
          properties: {
            data: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  tenantId: { type: 'string' },
                  name: { type: 'string' },
                  enabled: { type: 'boolean' },
                  nextFireAt: { type: 'string', format: 'date-time' },
                  createdAt: { type: 'string', format: 'date-time' },
                },
              },
            },
            pagination: {
              type: 'object',
              properties: {
                page: { type: 'integer' },
                pageSize: { type: 'integer' },
                total: { type: 'integer' },
                totalPages: { type: 'integer' },
              },
            },
          },
        },
      },
    },
    handler: async (request, reply) => {
      const query = request.query as any;
      const page = query.page || 1;
      const pageSize = query.pageSize || 20;

      const result = await scheduleRepository.findByTenant(query.tenantId || '', {
        enabled: query.enabled,
        page,
        pageSize,
      });

      reply.send({
        data: result.data.map(schedule => ({
          id: schedule.id,
          tenantId: schedule.tenantId,
          name: schedule.name,
          enabled: schedule.enabled,
          nextFireAt: schedule.nextFireAt?.toISOString(),
          createdAt: schedule.createdAt.toISOString(),
        })),
        pagination: result.pagination,
      });
    },
  });

  // Update schedule
  fastify.patch('/schedules/:id', {
    schema: {
      description: 'Update schedule',
      tags: ['schedules'],
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { type: 'string' },
        },
      },
      body: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          description: { type: 'string' },
          enabled: { type: 'boolean' },
          trigger: { type: 'object' },
          target: { type: 'object' },
          payload: { type: 'object' },
          calendar: { type: 'object' },
        },
      },
      response: {
        200: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            updatedAt: { type: 'string', format: 'date-time' },
          },
        },
      },
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };
      const updates = request.body as any;

      try {
        await scheduleRepository.update(id, updates);
        const updated = await scheduleRepository.findById(id);

        if (!updated) {
          return reply.code(404).send({ error: 'Schedule not found' });
        }

        reply.send({
          id: updated.id,
          updatedAt: updated.updatedAt.toISOString(),
        });
      } catch (error) {
        reply.code(400).send({
          error: error instanceof Error ? error.message : 'Update failed',
        });
      }
    },
  });

  // Delete schedule
  fastify.delete('/schedules/:id', {
    schema: {
      description: 'Delete schedule',
      tags: ['schedules'],
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { type: 'string' },
        },
      },
      response: {
        204: { type: 'null' },
      },
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };

      const deleted = await scheduleRepository.delete(id);
      if (!deleted) {
        return reply.code(404).send({ error: 'Schedule not found' });
      }

      reply.code(204).send();
    },
  });

  // Enable/disable schedule
  fastify.patch('/schedules/:id/enabled', {
    schema: {
      description: 'Enable or disable schedule',
      tags: ['schedules'],
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { type: 'string' },
        },
      },
      body: {
        type: 'object',
        required: ['enabled'],
        properties: {
          enabled: { type: 'boolean' },
        },
      },
      response: {
        200: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            enabled: { type: 'boolean' },
            nextFireAt: { type: 'string', format: 'date-time' },
          },
        },
      },
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };
      const { enabled } = request.body as { enabled: boolean };

      try {
        await schedulingService.setScheduleEnabled(id, enabled);
        const schedule = await scheduleRepository.findById(id);

        if (!schedule) {
          return reply.code(404).send({ error: 'Schedule not found' });
        }

        reply.send({
          id: schedule.id,
          enabled: schedule.enabled,
          nextFireAt: schedule.nextFireAt?.toISOString(),
        });
      } catch (error) {
        reply.code(400).send({
          error: error instanceof Error ? error.message : 'Operation failed',
        });
      }
    },
  });

  // Validate schedule
  fastify.post('/schedules/validate', {
    schema: {
      description: 'Validate schedule configuration',
      tags: ['schedules'],
      body: {
        type: 'object',
        required: ['tenantId', 'name', 'trigger', 'target'],
        properties: {
          tenantId: { type: 'string' },
          name: { type: 'string' },
          description: { type: 'string' },
          tz: { type: 'string', default: 'Europe/Berlin' },
          trigger: { type: 'object' },
          target: { type: 'object' },
          payload: { type: 'object' },
          calendar: { type: 'object' },
          enabled: { type: 'boolean', default: true },
        },
      },
      response: {
        200: {
          type: 'object',
          properties: {
            valid: { type: 'boolean' },
            errors: {
              type: 'array',
              items: { type: 'string' },
            },
          },
        },
      },
    },
    handler: async (request, reply) => {
      const body = request.body as any;

      try {
        const schedule = new ScheduleEntity({
          tenantId: body.tenantId,
          name: body.name,
          description: body.description,
          tz: body.tz || 'Europe/Berlin',
          trigger: body.trigger,
          target: body.target,
          payload: body.payload,
          calendar: body.calendar,
          enabled: body.enabled ?? true,
        });

        const validation = await schedulingService.validateSchedule(schedule);
        reply.send(validation);
      } catch (error) {
        reply.send({
          valid: false,
          errors: [error instanceof Error ? error.message : 'Validation failed'],
        });
      }
    },
  });
}