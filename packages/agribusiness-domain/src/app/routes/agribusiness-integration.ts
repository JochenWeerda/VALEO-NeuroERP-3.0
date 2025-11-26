/**
 * Agribusiness Integration REST API Routes
 * Cross-Domain Integration & API Management
 */

import { FastifyInstance } from 'fastify';
import { AgribusinessIntegrationService } from '../../domain/services/agribusiness-integration-service';

// Initialize services
const integrationService = new AgribusinessIntegrationService({});

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

export async function registerAgribusinessIntegrationRoutes(fastify: FastifyInstance) {
  fastify.register(async (integrationRoutes) => {

    // Endpoints
    // POST /integration/endpoints - Register endpoint
    integrationRoutes.post('/endpoints', {
      schema: {
        description: 'Register integration endpoint',
        tags: ['Integration'],
        body: {
          type: 'object',
          required: ['name', 'endpointType', 'url', 'authentication'],
          properties: {
            name: { type: 'string' },
            description: { type: 'string' },
            endpointType: { type: 'string', enum: ['REST', 'SOAP', 'GRAPHQL', 'WEBHOOK', 'FTP', 'SFTP'] },
            url: { type: 'string' },
            method: { type: 'string', enum: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'] },
            authentication: {
              type: 'object',
              required: ['type'],
              properties: {
                type: {
                  type: 'string',
                  enum: ['NONE', 'API_KEY', 'BASIC', 'BEARER', 'OAUTH2', 'CUSTOM'],
                },
                apiKey: { type: 'string' },
                apiKeyHeader: { type: 'string' },
                username: { type: 'string' },
                password: { type: 'string' },
                token: { type: 'string' },
                tokenUrl: { type: 'string' },
                clientId: { type: 'string' },
                clientSecret: { type: 'string' },
                customHeaders: { type: 'object' },
              },
            },
            headers: { type: 'object' },
            isActive: { type: 'boolean', default: true },
            timeout: { type: 'integer' },
            retryPolicy: {
              type: 'object',
              properties: {
                maxRetries: { type: 'integer' },
                retryDelay: { type: 'integer' },
                backoffMultiplier: { type: 'number' },
                retryableStatusCodes: { type: 'array', items: { type: 'integer' } },
              },
            },
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      try {
        const endpoint = await integrationService.registerEndpoint(body);
        return reply.status(201).send(endpoint);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /integration/endpoints - List endpoints
    integrationRoutes.get('/endpoints', {
      schema: {
        description: 'List integration endpoints',
        tags: ['Integration'],
        querystring: {
          type: 'object',
          properties: {
            endpointType: { type: 'string' },
            isActive: { type: 'boolean' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      try {
        const endpoints = await integrationService.listEndpoints(query);
        return reply.send({ data: endpoints });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /integration/endpoints/:id - Get endpoint by ID
    integrationRoutes.get('/endpoints/:id', {
      schema: {
        description: 'Get integration endpoint by ID',
        tags: ['Integration'],
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
        const endpoint = await integrationService.getEndpoint(id);
        return reply.send(endpoint);
      } catch (error: any) {
        return reply.status(404).send({ error: error.message });
      }
    });

    // POST /integration/endpoints/:id/test - Test endpoint connection
    integrationRoutes.post('/endpoints/:id/test', {
      schema: {
        description: 'Test endpoint connection',
        tags: ['Integration'],
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
        const result = await integrationService.testEndpoint(id);
        return reply.send(result);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // Mappings
    // POST /integration/mappings - Create mapping
    integrationRoutes.post('/mappings', {
      schema: {
        description: 'Create integration mapping',
        tags: ['Integration'],
        body: {
          type: 'object',
          required: ['name', 'sourceEntity', 'targetEntity', 'fieldMappings'],
          properties: {
            name: { type: 'string' },
            sourceEntity: { type: 'string' },
            targetEntity: { type: 'string' },
            fieldMappings: {
              type: 'array',
              items: {
                type: 'object',
                required: ['sourceField', 'targetField'],
                properties: {
                  sourceField: { type: 'string' },
                  targetField: { type: 'string' },
                  defaultValue: {},
                  required: { type: 'boolean' },
                  transformation: { type: 'string' },
                },
              },
            },
            transformations: {
              type: 'array',
              items: {
                type: 'object',
                required: ['type', 'field', 'expression'],
                properties: {
                  type: { type: 'string', enum: ['MAP', 'FORMAT', 'CALCULATE', 'VALIDATE', 'CUSTOM'] },
                  field: { type: 'string' },
                  expression: { type: 'string' },
                  parameters: { type: 'object' },
                },
              },
            },
            isActive: { type: 'boolean', default: true },
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      try {
        const mapping = await integrationService.createMapping(body);
        return reply.status(201).send(mapping);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /integration/mappings - List mappings
    integrationRoutes.get('/mappings', {
      schema: {
        description: 'List integration mappings',
        tags: ['Integration'],
        querystring: {
          type: 'object',
          properties: {
            sourceEntity: { type: 'string' },
            targetEntity: { type: 'string' },
            isActive: { type: 'boolean' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      try {
        const mappings = await integrationService.listMappings(query);
        return reply.send({ data: mappings });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /integration/mappings/:id - Get mapping by ID
    integrationRoutes.get('/mappings/:id', {
      schema: {
        description: 'Get integration mapping by ID',
        tags: ['Integration'],
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
        const mapping = await integrationService.getMapping(id);
        return reply.send(mapping);
      } catch (error: any) {
        return reply.status(404).send({ error: error.message });
      }
    });

    // POST /integration/mappings/:id/transform - Transform data
    integrationRoutes.post('/mappings/:id/transform', {
      schema: {
        description: 'Transform data using mapping',
        tags: ['Integration'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
        body: {
          type: 'object',
          required: ['data'],
          properties: {
            data: { type: 'object' },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      try {
        const transformed = await integrationService.transformData(id, body.data);
        return reply.send({ data: transformed });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // Sync Jobs
    // POST /integration/sync - Create sync job
    integrationRoutes.post('/sync', {
      schema: {
        description: 'Create integration sync job',
        tags: ['Integration'],
        body: {
          type: 'object',
          required: ['mappingId', 'direction'],
          properties: {
            mappingId: { type: 'string' },
            direction: { type: 'string', enum: ['INBOUND', 'OUTBOUND', 'BIDIRECTIONAL'] },
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      const userId = getAuthenticatedUserId(request);
      try {
        const job = await integrationService.createSyncJob(body.mappingId, body.direction, userId);
        return reply.status(201).send(job);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /integration/sync/:id - Get sync job by ID
    integrationRoutes.get('/sync/:id', {
      schema: {
        description: 'Get sync job by ID',
        tags: ['Integration'],
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
        const job = await integrationService.getSyncJob(id);
        return reply.send(job);
      } catch (error: any) {
        return reply.status(404).send({ error: error.message });
      }
    });

    // Webhooks
    // POST /integration/webhooks - Subscribe to webhook
    integrationRoutes.post('/webhooks', {
      schema: {
        description: 'Subscribe to webhook',
        tags: ['Integration'],
        body: {
          type: 'object',
          required: ['name', 'eventType', 'endpoint', 'method'],
          properties: {
            name: { type: 'string' },
            eventType: { type: 'string' },
            endpoint: { type: 'string' },
            method: { type: 'string', enum: ['POST', 'PUT'] },
            headers: { type: 'object' },
            authentication: { type: 'object' },
            isActive: { type: 'boolean', default: true },
            secret: { type: 'string' },
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      try {
        const webhook = await integrationService.subscribeWebhook(body);
        return reply.status(201).send(webhook);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /integration/webhooks - List webhooks
    integrationRoutes.get('/webhooks', {
      schema: {
        description: 'List webhook subscriptions',
        tags: ['Integration'],
        querystring: {
          type: 'object',
          properties: {
            eventType: { type: 'string' },
            isActive: { type: 'boolean' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      try {
        const webhooks = await integrationService.listWebhooks(query);
        return reply.send({ data: webhooks });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /integration/webhooks/:id - Get webhook by ID
    integrationRoutes.get('/webhooks/:id', {
      schema: {
        description: 'Get webhook subscription by ID',
        tags: ['Integration'],
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
        const webhook = await integrationService.getWebhook(id);
        return reply.send(webhook);
      } catch (error: any) {
        return reply.status(404).send({ error: error.message });
      }
    });
  });
}

