/**
 * Agribusiness Workflow REST API Routes
 * Automated Workflows & Notifications
 */

import { FastifyInstance } from 'fastify';
import { AgribusinessWorkflowService } from '../../domain/services/agribusiness-workflow-service';

// Mock notification service (would be replaced with actual implementation)
class MockNotificationService {
  async sendEmail(to: string, subject: string, body: string): Promise<void> {
    console.log(`[MOCK] Sending email to ${to}: ${subject}`);
  }

  async sendSMS(to: string, message: string): Promise<void> {
    console.log(`[MOCK] Sending SMS to ${to}: ${message}`);
  }

  async sendPushNotification(userId: string, title: string, message: string): Promise<void> {
    console.log(`[MOCK] Sending push to ${userId}: ${title} - ${message}`);
  }
}

// Mock event publisher (would be replaced with actual implementation)
class MockEventPublisher {
  async publish(event: string, data: any): Promise<void> {
    console.log(`[MOCK] Publishing event ${event}:`, data);
  }
}

// Initialize services
const notificationService = new MockNotificationService();
const eventPublisher = new MockEventPublisher();

const workflowService = new AgribusinessWorkflowService({
  notificationService,
  eventPublisher,
});

export async function registerAgribusinessWorkflowRoutes(fastify: FastifyInstance) {
  fastify.register(async (workflowRoutes) => {

    // GET /workflows - List workflow rules
    workflowRoutes.get('/', {
      schema: {
        description: 'List workflow rules',
        tags: ['Workflows'],
      },
    }, async (request, reply) => {
      try {
        const rules = await workflowService.getWorkflowRules();
        return reply.send({ data: rules });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /workflows/:id - Get workflow rule by ID
    workflowRoutes.get('/:id', {
      schema: {
        description: 'Get workflow rule by ID',
        tags: ['Workflows'],
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
        const rule = await workflowService.getWorkflowRule(id);
        if (!rule) {
          return reply.status(404).send({ error: 'Workflow rule not found' });
        }
        return reply.send(rule);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /workflows - Create workflow rule
    workflowRoutes.post('/', {
      schema: {
        description: 'Create a new workflow rule',
        tags: ['Workflows'],
        body: {
          type: 'object',
          required: ['name', 'trigger', 'actions'],
          properties: {
            name: { type: 'string' },
            description: { type: 'string' },
            trigger: {
              type: 'object',
              required: ['type'],
              properties: {
                type: {
                  type: 'string',
                  enum: [
                    'BATCH_CREATED',
                    'BATCH_EXPIRING',
                    'CONTRACT_SIGNED',
                    'CONTRACT_FULFILLMENT_THRESHOLD',
                    'CERTIFICATION_EXPIRING',
                    'TASK_COMPLETED',
                    'FARMER_REGISTERED',
                    'QUALITY_SCORE_BELOW',
                    'SCHEDULED',
                  ],
                },
                batchType: { type: 'string' },
                daysBeforeExpiry: { type: 'integer' },
                contractType: { type: 'string' },
                threshold: { type: 'number' },
                taskType: { type: 'string' },
                cron: { type: 'string' },
              },
            },
            conditions: {
              type: 'array',
              items: {
                type: 'object',
                required: ['field', 'operator', 'value'],
                properties: {
                  field: { type: 'string' },
                  operator: {
                    type: 'string',
                    enum: ['equals', 'not_equals', 'greater_than', 'less_than', 'contains', 'in'],
                  },
                  value: {},
                },
              },
            },
            actions: {
              type: 'array',
              items: {
                type: 'object',
                required: ['type'],
                properties: {
                  type: {
                    type: 'string',
                    enum: [
                      'SEND_EMAIL',
                      'SEND_SMS',
                      'SEND_PUSH',
                      'CREATE_TASK',
                      'UPDATE_STATUS',
                      'PUBLISH_EVENT',
                      'ASSIGN_TO_USER',
                    ],
                  },
                  to: { type: 'string' },
                  template: { type: 'string' },
                  data: { type: 'object' },
                  userId: { type: 'string' },
                  title: { type: 'string' },
                  message: { type: 'string' },
                  taskData: { type: 'object' },
                  entityType: { type: 'string' },
                  entityId: { type: 'string' },
                  status: { type: 'string' },
                  event: { type: 'string' },
                },
              },
            },
            isActive: { type: 'boolean', default: true },
            priority: { type: 'integer', default: 0 },
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      try {
        const rule = await workflowService.registerWorkflowRule({
          name: body.name,
          description: body.description,
          trigger: body.trigger,
          conditions: body.conditions || [],
          actions: body.actions,
          isActive: body.isActive !== undefined ? body.isActive : true,
          priority: body.priority || 0,
        });
        return reply.status(201).send(rule);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // PUT /workflows/:id - Update workflow rule
    workflowRoutes.put('/:id', {
      schema: {
        description: 'Update workflow rule',
        tags: ['Workflows'],
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
            name: { type: 'string' },
            description: { type: 'string' },
            trigger: { type: 'object' },
            conditions: { type: 'array' },
            actions: { type: 'array' },
            isActive: { type: 'boolean' },
            priority: { type: 'integer' },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      try {
        const rule = await workflowService.updateWorkflowRule(id, body);
        return reply.send(rule);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // DELETE /workflows/:id - Delete workflow rule
    workflowRoutes.delete('/:id', {
      schema: {
        description: 'Delete workflow rule',
        tags: ['Workflows'],
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
        await workflowService.deleteWorkflowRule(id);
        return reply.status(204).send();
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /workflows/execute - Manually execute workflow (for testing)
    workflowRoutes.post('/execute', {
      schema: {
        description: 'Manually execute workflow (for testing)',
        tags: ['Workflows'],
        body: {
          type: 'object',
          required: ['trigger', 'context'],
          properties: {
            trigger: {
              type: 'object',
              required: ['type'],
              properties: {
                type: { type: 'string' },
                batchType: { type: 'string' },
                daysBeforeExpiry: { type: 'integer' },
                contractType: { type: 'string' },
                threshold: { type: 'number' },
                taskType: { type: 'string' },
                cron: { type: 'string' },
              },
            },
            context: { type: 'object' },
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      try {
        await workflowService.executeWorkflows(body.trigger, body.context);
        return reply.send({ success: true, message: 'Workflow executed' });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });
  });
}

