/**
 * Contract Routes
 * ISO 27001 Communications Security Compliant
 */

import type { FastifyInstance } from 'fastify';
import { ContractService } from '../../domain/services/contract-service';
import { ContractRepository } from '../../infra/repositories/contract-repository';
import { ContractFilter, ContractSort } from '../../infra/repositories/contract-repository';

// Helper function to get tenant ID
function getTenantId(request: any): string {
  return request.tenantId || request.user?.tenantId || request.headers['x-tenant-id'] || 'default-tenant';
}

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  try {
    const user = request.user || request.session?.user;
    if (!user) {
      const authHeader = request.headers.authorization;
      if (authHeader && authHeader.startsWith('Bearer ')) {
        try {
          const token = authHeader.substring(7);
          const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
          return payload.sub || payload.userId || payload.id || 'system';
        } catch {
          return 'system';
        }
      }
    }
    return user?.id || user?.userId || user?.sub || 'system';
  } catch (error) {
    return 'system';
  }
}

// Security middleware for input validation
function validateContractInput(input: any): void {
  if (!input.contractNo || typeof input.contractNo !== 'string') {
    throw new Error('Invalid contract number');
  }
  if (!input.counterpartyId || typeof input.counterpartyId !== 'string') {
    throw new Error('Invalid counterparty ID');
  }
  if (!input.deliveryWindow || !input.deliveryWindow.from || !input.deliveryWindow.to) {
    throw new Error('Invalid delivery window');
  }
  if (!input.qty || input.qty.contracted <= 0) {
    throw new Error('Invalid quantity');
  }
}

// Authorization middleware
function checkPermission(request: any, action: string, resource: string): void {
  const userId = getAuthenticatedUserId(request);
  if (!userId) {
    throw new Error('Authentication required');
  }
}

export async function registerContractRoutes(fastify: FastifyInstance) {
  // Initialize services (simplified for now)
  const repository = new ContractRepository('default-tenant');
  const contractService = new ContractService(repository);

  // Base path for contracts
  fastify.register(async (contractRoutes) => {
    // GET /contracts - List contracts
    contractRoutes.get('/', {
      schema: {
        description: 'List contracts with pagination and filtering',
        tags: ['Contracts'],
        querystring: {
          type: 'object',
          properties: {
            counterpartyId: { type: 'string' },
            status: { type: 'string', enum: ['Draft', 'Active', 'PartiallyFulfilled', 'Fulfilled', 'Cancelled', 'Defaulted'] },
            type: { type: 'string', enum: ['Buy', 'Sell'] },
            commodity: { type: 'string', enum: ['WHEAT', 'BARLEY', 'RAPESEED', 'SOYMEAL', 'COMPOUND_FEED', 'FERTILIZER'] },
            page: { type: 'integer', minimum: 1, default: 1 },
            pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
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
                },
              },
            },
          },
        },
      },
    }, async (request, reply) => {
      try {
        const query = request.query as any;
        const filter: ContractFilter = {
          tenantId: getTenantId(request)
        };

        if (query.counterpartyId) filter.counterpartyId = query.counterpartyId;
        if (query.status) filter.status = query.status;
        if (query.type) filter.type = query.type;
        if (query.commodity) filter.commodity = query.commodity;

        const sort: ContractSort = { field: 'createdAt', direction: 'desc' };
        const page = parseInt(query.page) || 1;
        const pageSize = Math.min(parseInt(query.pageSize) || 20, 100);

        const result = await contractService.getContracts(filter, sort, page, pageSize);

        return {
          data: result.items.map(contract => ({
            id: contract.id,
            contractNo: contract.contractNo,
            type: contract.type,
            commodity: contract.commodity,
            counterpartyId: contract.counterpartyId,
            status: contract.status,
            qty: contract.qty,
            deliveryWindow: {
              from: contract.deliveryWindow.from.toISOString(),
              to: contract.deliveryWindow.to.toISOString()
            },
            createdAt: contract.createdAt.toISOString(),
            updatedAt: contract.updatedAt.toISOString()
          })),
          pagination: {
            page: result.page,
            pageSize: result.pageSize,
            total: result.total,
            totalPages: result.totalPages,
            hasNext: page < result.totalPages,
            hasPrev: page > 1
          }
        };
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // POST /contracts - Create contract
    contractRoutes.post('/', {
      schema: {
        description: 'Create a new contract',
        tags: ['Contracts'],
        body: {
          type: 'object',
          required: ['contractNo', 'type', 'commodity', 'counterpartyId', 'deliveryWindow', 'qty', 'pricing', 'delivery'],
          properties: {
            contractNo: { type: 'string' },
            type: { type: 'string', enum: ['Buy', 'Sell'] },
            commodity: { type: 'string', enum: ['WHEAT', 'BARLEY', 'RAPESEED', 'SOYMEAL', 'COMPOUND_FEED', 'FERTILIZER'] },
            counterpartyId: { type: 'string' },
            incoterm: { type: 'string' },
            deliveryWindow: {
              type: 'object',
              required: ['from', 'to'],
              properties: {
                from: { type: 'string', format: 'date-time' },
                to: { type: 'string', format: 'date-time' }
              }
            },
            qty: {
              type: 'object',
              required: ['unit', 'contracted'],
              properties: {
                unit: { type: 'string', enum: ['t', 'mt'] },
                contracted: { type: 'number', minimum: 0 },
                tolerance: { type: 'number' }
              }
            },
            pricing: {
              type: 'object',
              required: ['mode'],
              properties: {
                mode: { type: 'string', enum: ['FORWARD_CASH', 'BASIS', 'HTA', 'DEFERRED', 'MIN_PRICE', 'FIXED', 'INDEXED'] },
                referenceMarket: { type: 'string' },
                futuresMonth: { type: 'string' },
                basis: { type: 'number' }
              }
            },
            delivery: {
              type: 'object',
              required: ['shipmentType'],
              properties: {
                shipmentType: { type: 'string', enum: ['Spot', 'Window', 'CallOff'] },
                parity: { type: 'string' }
              }
            }
          },
        },
        response: {
          201: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        checkPermission(request, 'create', 'contract');

        const body = request.body as any;
        validateContractInput(body);

        const createdBy = getAuthenticatedUserId(request);
        const contract = await contractService.createContract({
          tenantId: getTenantId(request),
          contractNo: body.contractNo,
          type: body.type,
          commodity: body.commodity,
          counterpartyId: body.counterpartyId,
          incoterm: body.incoterm,
          deliveryWindow: {
            from: new Date(body.deliveryWindow.from),
            to: new Date(body.deliveryWindow.to)
          },
          qty: body.qty,
          pricing: body.pricing,
          delivery: body.delivery,
          createdBy
        });

        return reply.code(201).send({
          id: contract.id,
          contractNo: contract.contractNo,
          status: contract.status,
          createdAt: contract.createdAt.toISOString()
        });
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /contracts/:id - Get contract by ID
    contractRoutes.get('/:id', {
      schema: {
        description: 'Get contract by ID',
        tags: ['Contracts'],
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
        const tenantId = getTenantId(request);
        const contract = await contractService.getContractById(id, tenantId);

        if (!contract) {
          return reply.code(404).send({ error: 'Contract not found' });
        }

        return {
          id: contract.id,
          contractNo: contract.contractNo,
          type: contract.type,
          commodity: contract.commodity,
          counterpartyId: contract.counterpartyId,
          incoterm: contract.incoterm,
          deliveryWindow: {
            from: contract.deliveryWindow.from.toISOString(),
            to: contract.deliveryWindow.to.toISOString()
          },
          qty: contract.qty,
          pricing: contract.pricing,
          delivery: contract.delivery,
          status: contract.status,
          createdAt: contract.createdAt.toISOString(),
          updatedAt: contract.updatedAt.toISOString(),
          version: contract.version
        };
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // PATCH /contracts/:id - Update contract
    contractRoutes.patch('/:id', {
      schema: {
        description: 'Update contract',
        tags: ['Contracts'],
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
            incoterm: { type: 'string' },
            deliveryWindow: {
              type: 'object',
              properties: {
                from: { type: 'string', format: 'date-time' },
                to: { type: 'string', format: 'date-time' }
              }
            },
            qty: {
              type: 'object',
              properties: {
                unit: { type: 'string', enum: ['t', 'mt'] },
                contracted: { type: 'number', minimum: 0 },
                tolerance: { type: 'number' }
              }
            },
            pricing: {
              type: 'object',
              properties: {
                mode: { type: 'string', enum: ['FORWARD_CASH', 'BASIS', 'HTA', 'DEFERRED', 'MIN_PRICE', 'FIXED', 'INDEXED'] },
                referenceMarket: { type: 'string' },
                futuresMonth: { type: 'string' },
                basis: { type: 'number' }
              }
            },
            delivery: {
              type: 'object',
              properties: {
                shipmentType: { type: 'string', enum: ['Spot', 'Window', 'CallOff'] },
                parity: { type: 'string' }
              }
            }
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

        const updates: any = {};
        if (body.incoterm !== undefined) updates.incoterm = body.incoterm;
        if (body.deliveryWindow) {
          updates.deliveryWindow = {
            from: new Date(body.deliveryWindow.from),
            to: new Date(body.deliveryWindow.to)
          };
        }
        if (body.qty) updates.qty = body.qty;
        if (body.pricing) updates.pricing = body.pricing;
        if (body.delivery) updates.delivery = body.delivery;

        const updatedBy = getAuthenticatedUserId(request);
        const contract = await contractService.updateContract(id, updates, updatedBy);

        return {
          id: contract.id,
          contractNo: contract.contractNo,
          status: contract.status,
          updatedAt: contract.updatedAt.toISOString(),
          version: contract.version
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // DELETE /contracts/:id - Delete contract
    contractRoutes.delete('/:id', {
      schema: {
        description: 'Delete contract',
        tags: ['Contracts'],
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
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const tenantId = getTenantId(request);
        const deletedBy = getAuthenticatedUserId(request);
        const success = await contractService.deleteContract(id, tenantId, 'Contract deleted via API', deletedBy);

        if (!success) {
          return reply.code(404).send({ error: 'Contract not found' });
        }

        return reply.code(204).send();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /contracts/:id/activate - Activate contract
    contractRoutes.post('/:id/activate', {
      schema: {
        description: 'Activate contract',
        tags: ['Contracts'],
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
        const activatedBy = getAuthenticatedUserId(request);
        const tenantId = getTenantId(request);
        const contract = await contractService.activateContract(id, activatedBy, tenantId);

        return {
          id: contract.id,
          contractNo: contract.contractNo,
          status: contract.status,
          activatedAt: contract.updatedAt.toISOString()
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /contracts/:id/cancel - Cancel contract
    contractRoutes.post('/:id/cancel', {
      schema: {
        description: 'Cancel contract',
        tags: ['Contracts'],
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
        const cancelledBy = getAuthenticatedUserId(request);
        const tenantId = getTenantId(request);
        const body = request.body as any;
        const contract = await contractService.cancelContract(id, cancelledBy, tenantId, body?.reason);

        return {
          id: contract.id,
          contractNo: contract.contractNo,
          status: contract.status,
          cancelledAt: contract.updatedAt.toISOString()
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /contracts/:id/amendments - Create amendment
    contractRoutes.post('/:id/amendments', {
      schema: {
        description: 'Create contract amendment',
        tags: ['Contracts'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        body: {
          type: 'object',
          required: ['type', 'reason', 'changes'],
          properties: {
            type: { type: 'string', enum: ['QtyChange', 'WindowChange', 'PriceRuleChange', 'CounterpartyChange', 'DeliveryTermsChange', 'Other'] },
            reason: { type: 'string' },
            changes: { type: 'object' },
            notes: { type: 'string' }
          },
        },
        response: {
          201: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const body = request.body as any;
        const createdBy = getAuthenticatedUserId(request);
        const tenantId = getTenantId(request);

        const amendment = await contractService.createAmendment({
          contractId: id,
          tenantId,
          type: body.type,
          reason: body.reason,
          changes: body.changes,
          notes: body.notes,
          createdBy
        });

        return reply.code(201).send({
          id: amendment.id,
          contractId: amendment.contractId,
          type: amendment.type,
          status: amendment.status,
          createdAt: amendment.createdAt.toISOString()
        });
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /contracts/:id/amendments - Get contract amendments
    contractRoutes.get('/:id/amendments', {
      schema: {
        description: 'Get contract amendments',
        tags: ['Contracts'],
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
        const tenantId = getTenantId(request);
        const amendments = await contractService.getContractAmendments(id, tenantId);

        return amendments.map(amendment => ({
          id: amendment.id,
          contractId: amendment.contractId,
          type: amendment.type,
          reason: amendment.reason,
          status: amendment.status,
          approvedBy: amendment.approvedBy,
          approvedAt: amendment.approvedAt?.toISOString(),
          createdAt: amendment.createdAt.toISOString(),
          updatedAt: amendment.updatedAt.toISOString()
        }));
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /contracts/statistics - Get contract statistics
    contractRoutes.get('/statistics', {
      schema: {
        description: 'Get contract statistics',
        tags: ['Contracts'],
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const tenantId = getTenantId(request);
        const repository = new ContractRepository(tenantId);
        const statistics = await repository.getStatistics(tenantId);
        return statistics;
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // POST /contracts/:id/generate-document - Generate contract document
    contractRoutes.post('/:id/generate-document', {
      schema: {
        description: 'Generate contract document',
        tags: ['Contracts'],
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
            templateKey: { type: 'string', default: 'contract-template' }
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
        const userId = getAuthenticatedUserId(request);
        const tenantId = getTenantId(request);

        const document = await contractService.generateContractDocument(
          id,
          body?.templateKey || 'contract-template',
          userId,
          tenantId
        );

        return {
          documentId: document.id,
          status: document.status,
          createdAt: document.createdAt
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /contracts/:id/document - Get contract document URL
    contractRoutes.get('/:id/document', {
      schema: {
        description: 'Get contract document download URL',
        tags: ['Contracts'],
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
        const tenantId = getTenantId(request);

        const documentUrl = await contractService.getContractDocumentUrl(id, tenantId);

        if (!documentUrl) {
          return reply.code(404).send({ error: 'Contract document not found' });
        }

        return { documentUrl };
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // POST /contracts/:id/deliveries - Record a delivery
    contractRoutes.post('/:id/deliveries', {
      schema: {
        description: 'Record a delivery against a contract',
        tags: ['Contracts'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        body: {
          type: 'object',
          required: ['qty'],
          properties: {
            qty: { type: 'number', minimum: 0 },
            deliveryNote: { type: 'string' },
            batchNumbers: { type: 'array', items: { type: 'string' } },
            storageLocation: { type: 'string' },
            qualityData: {
              type: 'object',
              properties: {
                score: { type: 'number', minimum: 0, maximum: 100 },
                issues: { type: 'array', items: { type: 'string' } }
              }
            }
          }
        },
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const deliveryData = request.body as any;
        const userId = getAuthenticatedUserId(request);
        const tenantId = getTenantId(request);

        const fulfilment = await contractService.recordDelivery(id, deliveryData, userId, tenantId);

        return {
          fulfilment: fulfilment.getFulfilmentSummary(),
          timeline: fulfilment.timeline.slice(-5) // Last 5 events
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /contracts/:id/delivery-schedule - Add delivery schedule item
    contractRoutes.post('/:id/delivery-schedule', {
      schema: {
        description: 'Add a delivery schedule item to a contract',
        tags: ['Contracts'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        body: {
          type: 'object',
          required: ['plannedDate', 'qty'],
          properties: {
            plannedDate: { type: 'string', format: 'date-time' },
            qty: { type: 'number', minimum: 0 }
          }
        },
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const scheduleData = request.body as any;
        const userId = getAuthenticatedUserId(request);
        const tenantId = getTenantId(request);

        const fulfilment = await contractService.addDeliverySchedule(id, {
          plannedDate: new Date(scheduleData.plannedDate),
          qty: scheduleData.qty
        }, userId, tenantId);

        return {
          deliverySchedule: fulfilment.deliverySchedule,
          summary: fulfilment.getFulfilmentSummary()
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /contracts/:id/fulfilment - Get contract fulfilment summary
    contractRoutes.get('/:id/fulfilment', {
      schema: {
        description: 'Get contract fulfilment summary and tracking information',
        tags: ['Contracts'],
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
        const tenantId = getTenantId(request);

        const fulfilmentSummary = await contractService.getContractFulfilmentSummary(id, tenantId);

        if (!fulfilmentSummary) {
          return reply.code(404).send({ error: 'Fulfilment data not found' });
        }

        return fulfilmentSummary;
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

  }, { prefix: '/contracts' });
}