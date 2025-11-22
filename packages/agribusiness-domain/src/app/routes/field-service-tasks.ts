/**
 * Mobile Field Service REST API Routes
 * Task Management for Field Operations
 */

import { FastifyInstance } from 'fastify';
import { MobileFieldServiceService } from '../../domain/services/mobile-field-service-service';
import { FieldServiceTaskRepository } from '../../infra/repositories/field-service-task-repository';

// Initialize services
const taskRepository = new FieldServiceTaskRepository();
const mobileFieldService = new MobileFieldServiceService({ taskRepository });

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

function getAuthenticatedUserName(request: any): string {
  return request.user?.name || request.user?.email || 'System';
}

export async function registerFieldServiceTaskRoutes(fastify: FastifyInstance) {
  fastify.register(async (taskRoutes) => {

    // GET /field-service-tasks - List tasks with filtering and pagination
    taskRoutes.get('/', {
      schema: {
        description: 'List field service tasks with pagination and filtering',
        tags: ['Field Service Tasks'],
        querystring: {
          type: 'object',
          properties: {
            taskNumber: { type: 'string' },
            taskType: { type: 'string', enum: ['INSPECTION', 'HARVEST', 'PLANTING', 'TREATMENT', 'SAMPLE_COLLECTION', 'EQUIPMENT_MAINTENANCE', 'TRAINING', 'AUDIT', 'OTHER'] },
            status: { type: 'string', enum: ['DRAFT', 'SCHEDULED', 'IN_PROGRESS', 'ON_HOLD', 'COMPLETED', 'CANCELLED', 'REQUIRES_REVIEW'] },
            priority: { type: 'string', enum: ['LOW', 'MEDIUM', 'HIGH', 'URGENT'] },
            assignedToId: { type: 'string' },
            farmerId: { type: 'string' },
            scheduledStartDateFrom: { type: 'string', format: 'date-time' },
            scheduledStartDateTo: { type: 'string', format: 'date-time' },
            relatedBatchId: { type: 'string' },
            relatedContractId: { type: 'string' },
            isBillable: { type: 'boolean' },
            requiresReview: { type: 'boolean' },
            tags: { type: 'array', items: { type: 'string' } },
            search: { type: 'string' },
            page: { type: 'integer', minimum: 1, default: 1 },
            pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
            sortField: { type: 'string', enum: ['createdAt', 'updatedAt', 'scheduledStartDate', 'priority', 'status'], default: 'scheduledStartDate' },
            sortDirection: { type: 'string', enum: ['asc', 'desc'], default: 'asc' },
          },
        },
        response: {
          200: {
            type: 'object',
            properties: {
              data: { type: 'array' },
              pagination: {
                type: 'object',
                properties: {
                  page: { type: 'integer' },
                  pageSize: { type: 'integer' },
                  total: { type: 'integer' },
                },
              },
            },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      const filters = {
        taskNumber: query.taskNumber,
        taskType: query.taskType,
        status: query.status,
        priority: query.priority,
        assignedToId: query.assignedToId,
        farmerId: query.farmerId,
        scheduledStartDateFrom: query.scheduledStartDateFrom ? new Date(query.scheduledStartDateFrom) : undefined,
        scheduledStartDateTo: query.scheduledStartDateTo ? new Date(query.scheduledStartDateTo) : undefined,
        relatedBatchId: query.relatedBatchId,
        relatedContractId: query.relatedContractId,
        isBillable: query.isBillable,
        requiresReview: query.requiresReview,
        tags: query.tags,
        search: query.search,
      };
      const pagination = {
        page: query.page || 1,
        pageSize: query.pageSize || 20,
      };
      const sort = {
        field: query.sortField || 'scheduledStartDate',
        direction: query.sortDirection || 'asc',
      } as any;

      const result = await mobileFieldService.listTasks(filters, pagination, sort);
      return reply.send({
        data: result.data,
        pagination: {
          page: result.page,
          pageSize: result.pageSize,
          total: result.total,
        },
      });
    });

    // GET /field-service-tasks/:id - Get task by ID
    taskRoutes.get('/:id', {
      schema: {
        description: 'Get field service task by ID',
        tags: ['Field Service Tasks'],
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
        const task = await mobileFieldService.getTaskById(id);
        return reply.send(task);
      } catch (error: any) {
        return reply.status(404).send({ error: error.message });
      }
    });

    // POST /field-service-tasks - Create new task
    taskRoutes.post('/', {
      schema: {
        description: 'Create a new field service task',
        tags: ['Field Service Tasks'],
        body: {
          type: 'object',
          required: ['title', 'taskType', 'assignedToId', 'assignedToName', 'location', 'scheduledStartDate'],
          properties: {
            title: { type: 'string' },
            description: { type: 'string' },
            taskType: { type: 'string', enum: ['INSPECTION', 'HARVEST', 'PLANTING', 'TREATMENT', 'SAMPLE_COLLECTION', 'EQUIPMENT_MAINTENANCE', 'TRAINING', 'AUDIT', 'OTHER'] },
            priority: { type: 'string', enum: ['LOW', 'MEDIUM', 'HIGH', 'URGENT'] },
            assignedToId: { type: 'string' },
            assignedToName: { type: 'string' },
            farmerId: { type: 'string' },
            farmerName: { type: 'string' },
            location: {
              type: 'object',
              required: ['name', 'address', 'city', 'postalCode', 'country', 'latitude', 'longitude'],
              properties: {
                name: { type: 'string' },
                address: { type: 'string' },
                city: { type: 'string' },
                postalCode: { type: 'string' },
                country: { type: 'string' },
                latitude: { type: 'number' },
                longitude: { type: 'number' },
                accuracy: { type: 'number' },
              },
            },
            scheduledStartDate: { type: 'string', format: 'date-time' },
            scheduledEndDate: { type: 'string', format: 'date-time' },
            estimatedDuration: { type: 'integer' },
            checklist: { type: 'array' },
            relatedBatchId: { type: 'string' },
            relatedContractId: { type: 'string' },
            tags: { type: 'array', items: { type: 'string' } },
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      const userId = getAuthenticatedUserId(request);
      const userName = getAuthenticatedUserName(request);
      try {
        const taskInput = {
          ...body,
          scheduledStartDate: new Date(body.scheduledStartDate),
          scheduledEndDate: body.scheduledEndDate ? new Date(body.scheduledEndDate) : undefined,
        };
        const task = await mobileFieldService.createTask(taskInput, userId, userName);
        return reply.status(201).send(task);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // PUT /field-service-tasks/:id - Update task
    taskRoutes.put('/:id', {
      schema: {
        description: 'Update field service task',
        tags: ['Field Service Tasks'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
        body: {
          type: 'object',
          properties: {
            title: { type: 'string' },
            description: { type: 'string' },
            taskType: { type: 'string' },
            priority: { type: 'string' },
            status: { type: 'string' },
            assignedToId: { type: 'string' },
            assignedToName: { type: 'string' },
            scheduledStartDate: { type: 'string', format: 'date-time' },
            scheduledEndDate: { type: 'string', format: 'date-time' },
            actualStartDate: { type: 'string', format: 'date-time' },
            actualEndDate: { type: 'string', format: 'date-time' },
            estimatedDuration: { type: 'integer' },
            actualDuration: { type: 'integer' },
            weatherCondition: { type: 'string', enum: ['SUNNY', 'CLOUDY', 'RAINY', 'WINDY', 'FOGGY', 'STORMY'] },
            temperature: { type: 'number' },
            notes: { type: 'string' },
            checklist: { type: 'array' },
            tags: { type: 'array', items: { type: 'string' } },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      const userId = getAuthenticatedUserId(request);
      try {
        const updateInput = {
          ...body,
          scheduledStartDate: body.scheduledStartDate ? new Date(body.scheduledStartDate) : undefined,
          scheduledEndDate: body.scheduledEndDate ? new Date(body.scheduledEndDate) : undefined,
          actualStartDate: body.actualStartDate ? new Date(body.actualStartDate) : undefined,
          actualEndDate: body.actualEndDate ? new Date(body.actualEndDate) : undefined,
        };
        const task = await mobileFieldService.updateTask(id, updateInput, userId);
        return reply.send(task);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /field-service-tasks/:id/start - Start task
    taskRoutes.post('/:id/start', {
      schema: {
        description: 'Start a field service task',
        tags: ['Field Service Tasks'],
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
        const task = await mobileFieldService.startTask(id);
        return reply.send(task);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /field-service-tasks/:id/complete - Complete task
    taskRoutes.post('/:id/complete', {
      schema: {
        description: 'Complete a field service task',
        tags: ['Field Service Tasks'],
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
      const userId = getAuthenticatedUserId(request);
      try {
        const task = await mobileFieldService.completeTask(id, userId);
        return reply.send(task);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /field-service-tasks/:id/cancel - Cancel task
    taskRoutes.post('/:id/cancel', {
      schema: {
        description: 'Cancel a field service task',
        tags: ['Field Service Tasks'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
        body: {
          type: 'object',
          properties: {
            reason: { type: 'string' },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      try {
        const task = await mobileFieldService.cancelTask(id, body.reason);
        return reply.send(task);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /field-service-tasks/:id/notes - Add note to task
    taskRoutes.post('/:id/notes', {
      schema: {
        description: 'Add note to field service task',
        tags: ['Field Service Tasks'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
        body: {
          type: 'object',
          required: ['content'],
          properties: {
            content: { type: 'string' },
            isInternal: { type: 'boolean', default: false },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      const userId = getAuthenticatedUserId(request);
      const userName = getAuthenticatedUserName(request);
      try {
        const task = await mobileFieldService.addNote(id, body.content, userId, userName, body.isInternal || false);
        return reply.send(task);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /field-service-tasks/:id/attachments - Add attachment to task
    taskRoutes.post('/:id/attachments', {
      schema: {
        description: 'Add attachment to field service task',
        tags: ['Field Service Tasks'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
        body: {
          type: 'object',
          required: ['fileName', 'fileType', 'fileSize', 'url'],
          properties: {
            fileName: { type: 'string' },
            fileType: { type: 'string' },
            fileSize: { type: 'integer' },
            url: { type: 'string' },
            description: { type: 'string' },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      const userId = getAuthenticatedUserId(request);
      try {
        const attachment = {
          ...body,
          uploadedBy: userId,
        };
        const task = await mobileFieldService.addAttachment(id, attachment);
        return reply.send(task);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /field-service-tasks/:id/measurements - Add measurement to task
    taskRoutes.post('/:id/measurements', {
      schema: {
        description: 'Add measurement to field service task',
        tags: ['Field Service Tasks'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
        body: {
          type: 'object',
          required: ['type', 'value', 'unit'],
          properties: {
            type: { type: 'string' },
            value: { type: 'number' },
            unit: { type: 'string' },
            location: {
              type: 'object',
              properties: {
                latitude: { type: 'number' },
                longitude: { type: 'number' },
              },
            },
            notes: { type: 'string' },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      const userId = getAuthenticatedUserId(request);
      try {
        const measurement = {
          ...body,
          recordedBy: userId,
        };
        const task = await mobileFieldService.addMeasurement(id, measurement);
        return reply.send(task);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /field-service-tasks/:id/checklist/:itemId/complete - Complete checklist item
    taskRoutes.post('/:id/checklist/:itemId/complete', {
      schema: {
        description: 'Complete a checklist item',
        tags: ['Field Service Tasks'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            itemId: { type: 'string' },
          },
          required: ['id', 'itemId'],
        },
        body: {
          type: 'object',
          properties: {
            notes: { type: 'string' },
          },
        },
      },
    }, async (request, reply) => {
      const { id, itemId } = request.params as { id: string; itemId: string };
      const body = request.body as any;
      const userId = getAuthenticatedUserId(request);
      try {
        const task = await mobileFieldService.completeChecklistItem(id, itemId, userId, body.notes);
        return reply.send(task);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /field-service-tasks/user/:userId - Get tasks for user
    taskRoutes.get('/user/:userId', {
      schema: {
        description: 'Get field service tasks assigned to a user',
        tags: ['Field Service Tasks'],
        params: {
          type: 'object',
          properties: {
            userId: { type: 'string' },
          },
          required: ['userId'],
        },
        querystring: {
          type: 'object',
          properties: {
            status: { type: 'string' },
            page: { type: 'integer', minimum: 1, default: 1 },
            pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
          },
        },
      },
    }, async (request, reply) => {
      const { userId } = request.params as { userId: string };
      const query = request.query as any;
      const filters = {
        status: query.status,
      };
      const pagination = {
        page: query.page || 1,
        pageSize: query.pageSize || 20,
      };
      try {
        const result = await mobileFieldService.getTasksForUser(userId, filters, pagination);
        return reply.send({
          data: result.data,
          pagination: {
            page: pagination.page,
            pageSize: pagination.pageSize,
            total: result.total,
          },
        });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /field-service-tasks/farmer/:farmerId - Get tasks for farmer
    taskRoutes.get('/farmer/:farmerId', {
      schema: {
        description: 'Get field service tasks for a farmer',
        tags: ['Field Service Tasks'],
        params: {
          type: 'object',
          properties: {
            farmerId: { type: 'string' },
          },
          required: ['farmerId'],
        },
        querystring: {
          type: 'object',
          properties: {
            status: { type: 'string' },
            page: { type: 'integer', minimum: 1, default: 1 },
            pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
          },
        },
      },
    }, async (request, reply) => {
      const { farmerId } = request.params as { farmerId: string };
      const query = request.query as any;
      const filters = {
        status: query.status,
      };
      const pagination = {
        page: query.page || 1,
        pageSize: query.pageSize || 20,
      };
      try {
        const result = await mobileFieldService.getTasksForFarmer(farmerId, filters, pagination);
        return reply.send({
          data: result.data,
          pagination: {
            page: pagination.page,
            pageSize: pagination.pageSize,
            total: result.total,
          },
        });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /field-service-tasks/stats - Get task statistics
    taskRoutes.get('/stats', {
      schema: {
        description: 'Get field service task statistics',
        tags: ['Field Service Tasks'],
        querystring: {
          type: 'object',
          properties: {
            assignedToId: { type: 'string' },
            farmerId: { type: 'string' },
            status: { type: 'string' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      const filters = {
        assignedToId: query.assignedToId,
        farmerId: query.farmerId,
        status: query.status,
      };
      try {
        const stats = await mobileFieldService.getTaskStats(filters);
        return reply.send(stats);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /field-service-tasks/:id/review - Mark task for review
    taskRoutes.post('/:id/review', {
      schema: {
        description: 'Mark task as requiring review',
        tags: ['Field Service Tasks'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
        body: {
          type: 'object',
          properties: {
            reason: { type: 'string' },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      try {
        const task = await mobileFieldService.markForReview(id, body.reason);
        return reply.send(task);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /field-service-tasks/:id/sync - Sync task from mobile app
    taskRoutes.post('/:id/sync', {
      schema: {
        description: 'Sync task from mobile app',
        tags: ['Field Service Tasks'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
        body: {
          type: 'object',
          required: ['mobileAppVersion'],
          properties: {
            mobileAppVersion: { type: 'string' },
            updates: { type: 'object' },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      try {
        const task = await mobileFieldService.syncFromMobile(id, body.updates || {}, body.mobileAppVersion);
        return reply.send(task);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });
  });
}

