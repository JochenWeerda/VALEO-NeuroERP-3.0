import { FastifyInstance } from 'fastify';
import { BatchTraceabilityService } from '../../domain/services/batch-traceability-service';
import { BatchRepository } from '../../infra/repositories/batch-repository';
import { BatchFilter, BatchSort } from '../../infra/repositories/batch-repository';

// Initialize services
const batchRepository = new BatchRepository();
const batchTraceabilityService = new BatchTraceabilityService({ batchRepository });

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

export async function registerBatchRoutes(fastify: FastifyInstance) {
  fastify.register(async (batchRoutes) => {
    
    // GET /batches - List batches with filtering and pagination
    batchRoutes.get('/', {
      schema: {
        description: 'List batches with pagination and filtering',
        tags: ['Batches'],
        querystring: {
          type: 'object',
          properties: {
            batchNumber: { type: 'string' },
            batchType: { type: 'string', enum: ['SEED', 'CROP', 'FERTILIZER', 'FEED', 'PRODUCT'] },
            productId: { type: 'string' },
            originCountry: { type: 'string' },
            status: { type: 'string', enum: ['ACTIVE', 'ON_HOLD', 'BLOCKED', 'EXPIRED', 'CONSUMED'] },
            parentBatchId: { type: 'string' },
            qualityCertificateId: { type: 'string' },
            expired: { type: 'boolean' },
            expiringSoon: { type: 'boolean' },
            search: { type: 'string' },
            page: { type: 'integer', minimum: 1, default: 1 },
            pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
            sortField: { type: 'string', enum: ['createdAt', 'updatedAt', 'harvestDate', 'expiryDate', 'batchNumber', 'status'], default: 'createdAt' },
            sortDirection: { type: 'string', enum: ['asc', 'desc'], default: 'desc' }
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
                  totalPages: { type: 'integer' },
                  hasNext: { type: 'boolean' },
                  hasPrev: { type: 'boolean' }
                },
              },
            },
          },
        },
      },
    }, async (request, reply) => {
      try {
        const query = request.query as any;
        const filter: BatchFilter = {};
        const sort: BatchSort = { 
          field: query.sortField || 'createdAt', 
          direction: query.sortDirection || 'desc' 
        };

        if (query.batchNumber) filter.batchNumber = query.batchNumber;
        if (query.batchType) filter.batchType = query.batchType as any;
        if (query.productId) filter.productId = query.productId;
        if (query.originCountry) filter.originCountry = query.originCountry;
        if (query.status) filter.status = query.status as any;
        if (query.parentBatchId) filter.parentBatchId = query.parentBatchId;
        if (query.qualityCertificateId) filter.qualityCertificateId = query.qualityCertificateId;
        if (query.expired) filter.expired = query.expired;
        if (query.expiringSoon) filter.expiringSoon = query.expiringSoon;
        if (query.search) filter.search = query.search;

        const page = parseInt(query.page) || 1;
        const pageSize = Math.min(parseInt(query.pageSize) || 20, 100);

        const result = await batchTraceabilityService.listBatches(filter, sort, page, pageSize);

        return {
          data: result.items.map(batch => batch.toJSON()),
          pagination: {
            page: result.page,
            pageSize: result.pageSize,
            total: result.total,
            totalPages: result.totalPages,
            hasNext: result.hasNext,
            hasPrev: result.hasPrev
          }
        };
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // POST /batches - Create new batch
    batchRoutes.post('/', {
      schema: {
        description: 'Create a new batch',
        tags: ['Batches'],
        body: {
          type: 'object',
          required: ['batchNumber', 'batchType', 'initialQuantity', 'unitOfMeasure'],
          properties: {
            batchNumber: { type: 'string' },
            batchType: { type: 'string', enum: ['SEED', 'CROP', 'FERTILIZER', 'FEED', 'PRODUCT'] },
            productId: { type: 'string' },
            originCountry: { type: 'string' },
            harvestDate: { type: 'string', format: 'date' },
            expiryDate: { type: 'string', format: 'date' },
            parentBatchId: { type: 'string' },
            qualityCertificateId: { type: 'string' },
            initialQuantity: { type: 'number', minimum: 0 },
            unitOfMeasure: { type: 'string' },
            notes: { type: 'string' },
            customFields: { type: 'object' }
          },
        },
        response: {
          201: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const body = request.body as any;
        const createdBy = getAuthenticatedUserId(request);

        const batch = await batchTraceabilityService.createBatch(
          {
            batchNumber: body.batchNumber,
            batchType: body.batchType,
            productId: body.productId,
            originCountry: body.originCountry,
            harvestDate: body.harvestDate ? new Date(body.harvestDate) : undefined,
            expiryDate: body.expiryDate ? new Date(body.expiryDate) : undefined,
            parentBatchId: body.parentBatchId,
            qualityCertificateId: body.qualityCertificateId,
            initialQuantity: body.initialQuantity,
            unitOfMeasure: body.unitOfMeasure,
            notes: body.notes,
            customFields: body.customFields
          },
          createdBy
        );

        return reply.code(201).send({
          id: batch.id,
          batchNumber: batch.batchNumber,
          status: batch.status,
          createdAt: batch.createdAt.toISOString()
        });
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /batches/:id - Get batch by ID
    batchRoutes.get('/:id', {
      schema: {
        description: 'Get batch by ID',
        tags: ['Batches'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        response: {
          200: { type: 'object' },
          404: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const batch = await batchTraceabilityService.getBatchById(id);

        if (!batch) {
          return reply.code(404).send({ error: 'Batch not found' });
        }

        return batch.toJSON();
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // PATCH /batches/:id - Update batch
    batchRoutes.patch('/:id', {
      schema: {
        description: 'Update batch (active only)',
        tags: ['Batches'],
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
            batchNumber: { type: 'string' },
            originCountry: { type: 'string' },
            harvestDate: { type: 'string', format: 'date' },
            expiryDate: { type: 'string', format: 'date' },
            qualityCertificateId: { type: 'string' },
            notes: { type: 'string' },
            customFields: { type: 'object' }
          }
        },
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const body = request.body as any;
        const updatedBy = getAuthenticatedUserId(request);

        const updates: any = {};
        if (body.batchNumber !== undefined) updates.batchNumber = body.batchNumber;
        if (body.originCountry !== undefined) updates.originCountry = body.originCountry;
        if (body.harvestDate !== undefined) updates.harvestDate = new Date(body.harvestDate);
        if (body.expiryDate !== undefined) updates.expiryDate = new Date(body.expiryDate);
        if (body.qualityCertificateId !== undefined) updates.qualityCertificateId = body.qualityCertificateId;
        if (body.notes !== undefined) updates.notes = body.notes;
        if (body.customFields !== undefined) updates.customFields = body.customFields;

        const batch = await batchTraceabilityService.updateBatch(id, updates, updatedBy);

        return {
          id: batch.id,
          batchNumber: batch.batchNumber,
          status: batch.status,
          updatedAt: batch.updatedAt.toISOString(),
          version: batch.version
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // DELETE /batches/:id - Delete batch
    batchRoutes.delete('/:id', {
      schema: {
        description: 'Delete batch (no child batches)',
        tags: ['Batches'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        response: {
          204: { type: 'null' },
          404: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const success = await batchTraceabilityService.deleteBatch(id);

        if (!success) {
          return reply.code(404).send({ error: 'Batch not found' });
        }

        return reply.code(204).send();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /batches/:id/traceability-tree - Get complete traceability tree
    batchRoutes.get('/:id/traceability-tree', {
      schema: {
        description: 'Get complete traceability tree for batch',
        tags: ['Batches'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const tree = await batchTraceabilityService.getTraceabilityTree(id);
        return tree;
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /batches/:id/traceability-chain - Get traceability chain (upstream)
    batchRoutes.get('/:id/traceability-chain', {
      schema: {
        description: 'Get traceability chain from root to batch',
        tags: ['Batches'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        response: {
          200: { type: 'array' },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const chain = await batchTraceabilityService.getTraceabilityChain(id);
        return chain.map(batch => batch.toJSON());
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /batches/:id/children - Get child batches
    batchRoutes.get('/:id/children', {
      schema: {
        description: 'Get child batches',
        tags: ['Batches'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        response: {
          200: { type: 'array' },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const children = await batchTraceabilityService.getChildBatches(id);
        return children.map(batch => batch.toJSON());
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // POST /batches/:id/allocate - Allocate quantity from batch
    batchRoutes.post('/:id/allocate', {
      schema: {
        description: 'Allocate quantity from batch',
        tags: ['Batches'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        body: {
          type: 'object',
          required: ['quantity'],
          properties: {
            quantity: { type: 'number', minimum: 0.01 }
          }
        },
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const body = request.body as any;
        const batch = await batchTraceabilityService.allocateBatch(id, body.quantity);
        return batch.toJSON();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /batches/:id/consume - Consume quantity from batch
    batchRoutes.post('/:id/consume', {
      schema: {
        description: 'Consume quantity from batch',
        tags: ['Batches'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        body: {
          type: 'object',
          required: ['quantity'],
          properties: {
            quantity: { type: 'number', minimum: 0.01 }
          }
        },
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const body = request.body as any;
        const batch = await batchTraceabilityService.consumeBatch(id, body.quantity);
        return batch.toJSON();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /batches/:id/hold - Put batch on hold
    batchRoutes.post('/:id/hold', {
      schema: {
        description: 'Put batch on hold',
        tags: ['Batches'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        body: {
          type: 'object',
          required: ['reason'],
          properties: {
            reason: { type: 'string' }
          }
        },
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const body = request.body as any;
        const batch = await batchTraceabilityService.putBatchOnHold(id, body.reason);
        return batch.toJSON();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /batches/:id/block - Block batch
    batchRoutes.post('/:id/block', {
      schema: {
        description: 'Block batch',
        tags: ['Batches'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        body: {
          type: 'object',
          required: ['reason'],
          properties: {
            reason: { type: 'string' }
          }
        },
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const body = request.body as any;
        const batch = await batchTraceabilityService.blockBatch(id, body.reason);
        return batch.toJSON();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /batches/statistics - Get batch statistics
    batchRoutes.get('/statistics', {
      schema: {
        description: 'Get batch statistics',
        tags: ['Batches'],
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const statistics = await batchTraceabilityService.getBatchStatistics();
        return statistics;
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /batches/expired - Get expired batches
    batchRoutes.get('/expired', {
      schema: {
        description: 'Get expired batches',
        tags: ['Batches'],
        response: {
          200: { type: 'array' },
        },
      },
    }, async (request, reply) => {
      try {
        const batches = await batchTraceabilityService.getExpiredBatches();
        return batches.map(batch => batch.toJSON());
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /batches/expiring-soon - Get batches expiring soon
    batchRoutes.get('/expiring-soon', {
      schema: {
        description: 'Get batches expiring soon',
        tags: ['Batches'],
        querystring: {
          type: 'object',
          properties: {
            days: { type: 'integer', minimum: 1, default: 30 }
          }
        },
        response: {
          200: { type: 'array' },
        },
      },
    }, async (request, reply) => {
      try {
        const query = request.query as any;
        const days = parseInt(query.days) || 30;
        const batches = await batchTraceabilityService.getExpiringSoonBatches(days);
        return batches.map(batch => batch.toJSON());
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

  }, { prefix: '/batches' });
}
