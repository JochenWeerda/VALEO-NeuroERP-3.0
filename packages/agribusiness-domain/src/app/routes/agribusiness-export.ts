/**
 * Agribusiness Export/Import REST API Routes
 * Data Export & Import Management
 */

import { FastifyInstance } from 'fastify';
import { AgribusinessExportService } from '../../domain/services/agribusiness-export-service';

// Initialize services
const exportService = new AgribusinessExportService({});

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

export async function registerAgribusinessExportRoutes(fastify: FastifyInstance) {
  fastify.register(async (exportRoutes) => {

    // POST /export - Create export job
    exportRoutes.post('/', {
      schema: {
        description: 'Create a new export job',
        tags: ['Export/Import'],
        body: {
          type: 'object',
          required: ['entityType', 'format'],
          properties: {
            entityType: {
              type: 'string',
              enum: ['FARMER', 'BATCH', 'CONTRACT', 'TASK', 'CERTIFICATE', 'AUDIT'],
            },
            format: { type: 'string', enum: ['CSV', 'JSON', 'EXCEL', 'PDF', 'XML'] },
            includeHeaders: { type: 'boolean', default: true },
            dateFormat: { type: 'string' },
            delimiter: { type: 'string' },
            includeMetadata: { type: 'boolean', default: false },
            filters: { type: 'object' },
            fields: { type: 'array', items: { type: 'string' } },
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      const userId = getAuthenticatedUserId(request);
      try {
        const job = await exportService.createExportJob(
          body.entityType,
          {
            format: body.format,
            includeHeaders: body.includeHeaders,
            dateFormat: body.dateFormat,
            delimiter: body.delimiter,
            includeMetadata: body.includeMetadata,
            filters: body.filters,
            fields: body.fields,
          },
          userId
        );
        return reply.status(201).send(job);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /export - List export jobs
    exportRoutes.get('/', {
      schema: {
        description: 'List export jobs',
        tags: ['Export/Import'],
        querystring: {
          type: 'object',
          properties: {
            entityType: { type: 'string' },
            status: { type: 'string', enum: ['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'] },
            createdBy: { type: 'string' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      try {
        const jobs = await exportService.listExportJobs(query);
        return reply.send({ data: jobs });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /export/:id - Get export job by ID
    exportRoutes.get('/:id', {
      schema: {
        description: 'Get export job by ID',
        tags: ['Export/Import'],
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
        const job = await exportService.getExportJob(id);
        return reply.send(job);
      } catch (error: any) {
        return reply.status(404).send({ error: error.message });
      }
    });

  // Import routes
  fastify.register(async (importRoutes) => {
    // POST /import - Create import job
    importRoutes.post('/', {
      schema: {
        description: 'Create a new import job',
        tags: ['Export/Import'],
        body: {
          type: 'object',
          required: ['entityType', 'fileName', 'fileUrl', 'fileSize'],
          properties: {
            entityType: {
              type: 'string',
              enum: ['FARMER', 'BATCH', 'CONTRACT', 'TASK', 'CERTIFICATE'],
            },
            fileName: { type: 'string' },
            fileUrl: { type: 'string' },
            fileSize: { type: 'integer' },
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      const userId = getAuthenticatedUserId(request);
      try {
        const job = await exportService.createImportJob(
          body.entityType,
          body.fileName,
          body.fileUrl,
          body.fileSize,
          userId
        );
        return reply.status(201).send(job);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /import - List import jobs
    importRoutes.get('/', {
      schema: {
        description: 'List import jobs',
        tags: ['Export/Import'],
        querystring: {
          type: 'object',
          properties: {
            entityType: { type: 'string' },
            status: {
              type: 'string',
              enum: ['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'PARTIALLY_COMPLETED'],
            },
            createdBy: { type: 'string' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      try {
        const jobs = await exportService.listImportJobs(query);
        return reply.send({ data: jobs });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /import/:id - Get import job by ID
    importRoutes.get('/:id', {
      schema: {
        description: 'Get import job by ID',
        tags: ['Export/Import'],
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
        const job = await exportService.getImportJob(id);
        return reply.send(job);
      } catch (error: any) {
        return reply.status(404).send({ error: error.message });
      }
    });

    // Import routes
    // POST /import - Create import job
    exportRoutes.post('/import', {
      schema: {
        description: 'Create a new import job',
        tags: ['Export/Import'],
        body: {
          type: 'object',
          required: ['entityType', 'fileName', 'fileUrl', 'fileSize'],
          properties: {
            entityType: {
              type: 'string',
              enum: ['FARMER', 'BATCH', 'CONTRACT', 'TASK', 'CERTIFICATE'],
            },
            fileName: { type: 'string' },
            fileUrl: { type: 'string' },
            fileSize: { type: 'integer' },
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      const userId = getAuthenticatedUserId(request);
      try {
        const job = await exportService.createImportJob(
          body.entityType,
          body.fileName,
          body.fileUrl,
          body.fileSize,
          userId
        );
        return reply.status(201).send(job);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /import - List import jobs
    exportRoutes.get('/import', {
      schema: {
        description: 'List import jobs',
        tags: ['Export/Import'],
        querystring: {
          type: 'object',
          properties: {
            entityType: { type: 'string' },
            status: {
              type: 'string',
              enum: ['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'PARTIALLY_COMPLETED'],
            },
            createdBy: { type: 'string' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      try {
        const jobs = await exportService.listImportJobs(query);
        return reply.send({ data: jobs });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /import/:id - Get import job by ID
    exportRoutes.get('/import/:id', {
      schema: {
        description: 'Get import job by ID',
        tags: ['Export/Import'],
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
        const job = await exportService.getImportJob(id);
        return reply.send(job);
      } catch (error: any) {
        return reply.status(404).send({ error: error.message });
      }
    });
  });
}

