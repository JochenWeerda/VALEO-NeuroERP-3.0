import { FastifyInstance } from 'fastify';
import { CommodityContractService } from '../../domain/services/commodity-contract-service';
import { CommodityContractRepository } from '../../infra/repositories/commodity-contract-repository';
import { CommodityContractFilter, CommodityContractSort } from '../../infra/repositories/commodity-contract-repository';

// Initialize services
const commodityContractRepository = new CommodityContractRepository();
const commodityContractService = new CommodityContractService({ commodityContractRepository });

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

export async function registerCommodityContractRoutes(fastify: FastifyInstance) {
  fastify.register(async (contractRoutes) => {
    
    // GET /commodity-contracts - List contracts with filtering and pagination
    contractRoutes.get('/', {
      schema: {
        description: 'List commodity contracts with pagination and filtering',
        tags: ['Commodity Contracts'],
        querystring: {
          type: 'object',
          properties: {
            contractNumber: { type: 'string' },
            contractType: { type: 'string', enum: ['FORWARD', 'FUTURES', 'OPTION'] },
            supplierId: { type: 'string' },
            status: { type: 'string', enum: ['DRAFT', 'NEGOTIATING', 'SIGNED', 'ACTIVE', 'FULFILLED', 'EXPIRED', 'CANCELLED'] },
            commodity: { type: 'string', enum: ['WHEAT', 'CORN', 'BARLEY', 'RAPE', 'SOYBEAN', 'SUNFLOWER', 'FERTILIZER', 'FEED'] },
            expired: { type: 'boolean' },
            search: { type: 'string' },
            page: { type: 'integer', minimum: 1, default: 1 },
            pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
            sortField: { type: 'string', enum: ['createdAt', 'updatedAt', 'contractDate', 'deliveryPeriodStart', 'deliveryPeriodEnd', 'contractNumber', 'status', 'totalContractValue'], default: 'createdAt' },
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
        const filter: CommodityContractFilter = {};
        const sort: CommodityContractSort = { 
          field: query.sortField || 'createdAt', 
          direction: query.sortDirection || 'desc' 
        };

        if (query.contractNumber) filter.contractNumber = query.contractNumber;
        if (query.contractType) filter.contractType = query.contractType as any;
        if (query.supplierId) filter.supplierId = query.supplierId;
        if (query.status) filter.status = query.status as any;
        if (query.commodity) filter.commodity = query.commodity as any;
        if (query.expired) filter.expired = query.expired;
        if (query.search) filter.search = query.search;

        const page = parseInt(query.page) || 1;
        const pageSize = Math.min(parseInt(query.pageSize) || 20, 100);

        const result = await commodityContractService.listCommodityContracts(filter, sort, page, pageSize);

        return {
          data: result.items.map(contract => contract.toJSON()),
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

    // POST /commodity-contracts - Create new contract
    contractRoutes.post('/', {
      schema: {
        description: 'Create a new commodity contract',
        tags: ['Commodity Contracts'],
        body: {
          type: 'object',
          required: ['contractNumber', 'contractType', 'supplierId', 'items', 'contractDate', 'deliveryPeriodStart', 'deliveryPeriodEnd', 'paymentTerms', 'currency'],
          properties: {
            contractNumber: { type: 'string' },
            contractType: { type: 'string', enum: ['FORWARD', 'FUTURES', 'OPTION'] },
            supplierId: { type: 'string' },
            items: {
              type: 'array',
              items: {
                type: 'object',
                required: ['commodity', 'quantity', 'unitOfMeasure', 'contractPrice', 'currency', 'deliveryDate'],
                properties: {
                  commodity: { type: 'string', enum: ['WHEAT', 'CORN', 'BARLEY', 'RAPE', 'SOYBEAN', 'SUNFLOWER', 'FERTILIZER', 'FEED'] },
                  quantity: { type: 'number', minimum: 0 },
                  unitOfMeasure: { type: 'string' },
                  contractPrice: { type: 'number', minimum: 0 },
                  currency: { type: 'string' },
                  deliveryDate: { type: 'string', format: 'date' },
                  qualitySpecifications: { type: 'object' },
                  notes: { type: 'string' }
                }
              }
            },
            contractDate: { type: 'string', format: 'date' },
            deliveryPeriodStart: { type: 'string', format: 'date' },
            deliveryPeriodEnd: { type: 'string', format: 'date' },
            paymentTerms: { type: 'string' },
            currency: { type: 'string' },
            hedgingStrategy: { type: 'string' },
            notes: { type: 'string' }
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

        const contract = await commodityContractService.createCommodityContract(
          {
            contractNumber: body.contractNumber,
            contractType: body.contractType,
            supplierId: body.supplierId,
            items: body.items.map((item: any) => ({
              ...item,
              deliveryDate: new Date(item.deliveryDate)
            })),
            contractDate: new Date(body.contractDate),
            deliveryPeriodStart: new Date(body.deliveryPeriodStart),
            deliveryPeriodEnd: new Date(body.deliveryPeriodEnd),
            paymentTerms: body.paymentTerms,
            currency: body.currency,
            hedgingStrategy: body.hedgingStrategy,
            notes: body.notes
          },
          createdBy
        );

        return reply.code(201).send({
          id: contract.id,
          contractNumber: contract.contractNumber,
          status: contract.status,
          totalContractValue: contract.totalContractValue,
          createdAt: contract.createdAt.toISOString()
        });
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /commodity-contracts/:id - Get contract by ID
    contractRoutes.get('/:id', {
      schema: {
        description: 'Get commodity contract by ID',
        tags: ['Commodity Contracts'],
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
        const contract = await commodityContractService.getCommodityContractById(id);

        if (!contract) {
          return reply.code(404).send({ error: 'Commodity contract not found' });
        }

        return contract.toJSON();
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // POST /commodity-contracts/:id/sign - Sign contract
    contractRoutes.post('/:id/sign', {
      schema: {
        description: 'Sign commodity contract',
        tags: ['Commodity Contracts'],
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
        const signedBy = getAuthenticatedUserId(request);
        
        const contract = await commodityContractService.signContract(id, signedBy);
        return contract.toJSON();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /commodity-contracts/:id/activate - Activate contract
    contractRoutes.post('/:id/activate', {
      schema: {
        description: 'Activate commodity contract',
        tags: ['Commodity Contracts'],
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
        
        const contract = await commodityContractService.activateContract(id, activatedBy);
        return contract.toJSON();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /commodity-contracts/:id/fulfill - Record fulfillment
    contractRoutes.post('/:id/fulfill', {
      schema: {
        description: 'Record fulfillment for contract item',
        tags: ['Commodity Contracts'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        body: {
          type: 'object',
          required: ['itemId', 'fulfilledQuantity'],
          properties: {
            itemId: { type: 'string' },
            fulfilledQuantity: { type: 'number', minimum: 0.01 }
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
        
        const contract = await commodityContractService.recordFulfillment(
          id,
          body.itemId,
          body.fulfilledQuantity,
          updatedBy
        );
        return contract.toJSON();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /commodity-contracts/statistics - Get contract statistics
    contractRoutes.get('/statistics', {
      schema: {
        description: 'Get commodity contract statistics',
        tags: ['Commodity Contracts'],
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const statistics = await commodityContractService.getCommodityContractStatistics();
        return statistics;
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /commodity-contracts/active - Get active contracts
    contractRoutes.get('/active', {
      schema: {
        description: 'Get active commodity contracts',
        tags: ['Commodity Contracts'],
        response: {
          200: { type: 'array' },
        },
      },
    }, async (request, reply) => {
      try {
        const contracts = await commodityContractService.getActiveContracts();
        return contracts.map(contract => contract.toJSON());
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

  }, { prefix: '/commodity-contracts' });
}
