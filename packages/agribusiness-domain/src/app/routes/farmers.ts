/**
 * Farmer Portal REST API Routes
 * Self-Service Features for Farmers
 */

import { FastifyInstance } from 'fastify';
import { FarmerPortalService } from '../../domain/services/farmer-portal-service';
import { FarmerRepository } from '../../infra/repositories/farmer-repository';
import { ChangeLogService } from '@valeo-neuroerp/audit-domain';
import { ChangeLogRepository } from '@valeo-neuroerp/audit-domain';

// Initialize services
const farmerRepository = new FarmerRepository();
const changeLogRepository = new ChangeLogRepository();
const changeLogService = new ChangeLogService({ changeLogRepository });
const farmerPortalService = new FarmerPortalService({
  farmerRepository,
  changeLogService,
  tenantId: 'default', // Would come from request in production
});

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

function getAuthenticatedUserName(request: any): string {
  return request.user?.name || request.user?.email || 'System';
}

function getUserInfo(request: any): {
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

export async function registerFarmerRoutes(fastify: FastifyInstance) {
  fastify.register(async (farmerRoutes) => {

    // GET /farmers - List farmers with filtering and pagination
    farmerRoutes.get('/', {
      schema: {
        description: 'List farmers with pagination and filtering',
        tags: ['Farmers'],
        querystring: {
          type: 'object',
          properties: {
            farmerNumber: { type: 'string' },
            email: { type: 'string' },
            farmerType: { type: 'string', enum: ['INDIVIDUAL', 'COOPERATIVE', 'COMPANY', 'ASSOCIATION'] },
            status: { type: 'string', enum: ['ACTIVE', 'INACTIVE', 'PENDING', 'SUSPENDED', 'VERIFIED'] },
            hasPortalAccess: { type: 'boolean' },
            certificationType: { type: 'string' },
            locationCountry: { type: 'string' },
            search: { type: 'string' },
            page: { type: 'integer', minimum: 1, default: 1 },
            pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
            sortField: { type: 'string', enum: ['createdAt', 'updatedAt', 'fullName', 'farmerNumber'], default: 'createdAt' },
            sortDirection: { type: 'string', enum: ['asc', 'desc'], default: 'desc' },
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
        farmerNumber: query.farmerNumber,
        email: query.email,
        farmerType: query.farmerType,
        status: query.status,
        hasPortalAccess: query.hasPortalAccess,
        certificationType: query.certificationType,
        locationCountry: query.locationCountry,
        search: query.search,
      };
      const pagination = {
        page: query.page || 1,
        pageSize: query.pageSize || 20,
      };
      const sort = {
        field: query.sortField || 'createdAt',
        direction: query.sortDirection || 'desc',
      } as any;

      const result = await farmerPortalService.listFarmers(filters, pagination, sort);
      return reply.send({
        data: result.data,
        pagination: {
          page: result.page,
          pageSize: result.pageSize,
          total: result.total,
        },
      });
    });

    // GET /farmers/:id - Get farmer by ID
    farmerRoutes.get('/:id', {
      schema: {
        description: 'Get farmer by ID',
        tags: ['Farmers'],
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
        const farmer = await farmerPortalService.getFarmerById(id);
        return reply.send(farmer);
      } catch (error: any) {
        return reply.status(404).send({ error: error.message });
      }
    });

    // POST /farmers - Register new farmer
    farmerRoutes.post('/', {
      schema: {
        description: 'Register a new farmer',
        tags: ['Farmers'],
        body: {
          type: 'object',
          required: ['firstName', 'lastName', 'email', 'farmerType'],
          properties: {
            firstName: { type: 'string' },
            lastName: { type: 'string' },
            email: { type: 'string', format: 'email' },
            phone: { type: 'string' },
            farmerType: { type: 'string', enum: ['INDIVIDUAL', 'COOPERATIVE', 'COMPANY', 'ASSOCIATION'] },
            status: { type: 'string', enum: ['ACTIVE', 'INACTIVE', 'PENDING', 'SUSPENDED', 'VERIFIED'] },
            taxId: { type: 'string' },
            vatNumber: { type: 'string' },
            locations: { type: 'array' },
            certifications: { type: 'array' },
            crops: { type: 'array' },
            profile: { type: 'object' },
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      const userInfo = getUserInfo(request);
      try {
        const farmer = await farmerPortalService.registerFarmer(body, userInfo.userId, {
          userName: userInfo.userName,
          userEmail: userInfo.userEmail,
          ipAddress: userInfo.ipAddress,
          userAgent: userInfo.userAgent,
        });
        return reply.status(201).send(farmer);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // PUT /farmers/:id - Update farmer profile
    farmerRoutes.put('/:id', {
      schema: {
        description: 'Update farmer profile',
        tags: ['Farmers'],
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
            firstName: { type: 'string' },
            lastName: { type: 'string' },
            email: { type: 'string', format: 'email' },
            phone: { type: 'string' },
            farmerType: { type: 'string', enum: ['INDIVIDUAL', 'COOPERATIVE', 'COMPANY', 'ASSOCIATION'] },
            status: { type: 'string', enum: ['ACTIVE', 'INACTIVE', 'PENDING', 'SUSPENDED', 'VERIFIED'] },
            taxId: { type: 'string' },
            vatNumber: { type: 'string' },
            profile: { type: 'object' },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      const userInfo = getUserInfo(request);
      try {
        const farmer = await farmerPortalService.updateFarmerProfile(id, body, userInfo.userId, {
          reason: body.reason,
          userName: userInfo.userName,
          userEmail: userInfo.userEmail,
          ipAddress: userInfo.ipAddress,
          userAgent: userInfo.userAgent,
        });
        return reply.send(farmer);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /farmers/:id/portal-access/enable - Enable portal access
    farmerRoutes.post('/:id/portal-access/enable', {
      schema: {
        description: 'Enable portal access for farmer',
        tags: ['Farmers'],
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
        const farmer = await farmerPortalService.enablePortalAccess(id);
        return reply.send(farmer);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // DELETE /farmers/:id - Delete farmer
    farmerRoutes.delete('/:id', {
      schema: {
        description: 'Delete farmer (soft delete)',
        tags: ['Farmers'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
        body: {
          type: 'object',
          required: ['reason'],
          properties: {
            reason: { type: 'string', minLength: 10 },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      const userInfo = getUserInfo(request);
      try {
        await farmerPortalService.deleteFarmer(id, body.reason, userInfo.userId, {
          userName: userInfo.userName,
          userEmail: userInfo.userEmail,
          ipAddress: userInfo.ipAddress,
          userAgent: userInfo.userAgent,
        });
        return reply.status(204).send();
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /farmers/:id/portal-access/disable - Disable portal access
    farmerRoutes.post('/:id/portal-access/disable', {
      schema: {
        description: 'Disable portal access for farmer',
        tags: ['Farmers'],
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
        const farmer = await farmerPortalService.disablePortalAccess(id);
        return reply.send(farmer);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /farmers/:id/portal-login - Record portal login
    farmerRoutes.post('/:id/portal-login', {
      schema: {
        description: 'Record portal login',
        tags: ['Farmers'],
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
        const farmer = await farmerPortalService.recordPortalLogin(id);
        return reply.send(farmer);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /farmers/:id/stats - Get farmer portal statistics
    farmerRoutes.get('/:id/stats', {
      schema: {
        description: 'Get farmer portal statistics',
        tags: ['Farmers'],
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
        const stats = await farmerPortalService.getFarmerPortalStats(id);
        return reply.send(stats);
      } catch (error: any) {
        return reply.status(404).send({ error: error.message });
      }
    });

    // POST /farmers/:id/locations - Add location to farmer
    farmerRoutes.post('/:id/locations', {
      schema: {
        description: 'Add location to farmer',
        tags: ['Farmers'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
        body: {
          type: 'object',
          required: ['name', 'address', 'city', 'postalCode', 'country'],
          properties: {
            name: { type: 'string' },
            address: { type: 'string' },
            city: { type: 'string' },
            postalCode: { type: 'string' },
            country: { type: 'string' },
            latitude: { type: 'number' },
            longitude: { type: 'number' },
            areaHectares: { type: 'number' },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      try {
        const farmer = await farmerPortalService.addLocation(id, body);
        return reply.send(farmer);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /farmers/:id/certifications - Add certification to farmer
    farmerRoutes.post('/:id/certifications', {
      schema: {
        description: 'Add certification to farmer',
        tags: ['Farmers'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
        body: {
          type: 'object',
          required: ['type', 'certificateNumber', 'issuedBy', 'issuedDate'],
          properties: {
            type: { type: 'string', enum: ['ORGANIC', 'GLOBALGAP', 'FAIRTRADE', 'RAINFOREST', 'UTZ'] },
            certificateNumber: { type: 'string' },
            issuedBy: { type: 'string' },
            issuedDate: { type: 'string', format: 'date-time' },
            expiryDate: { type: 'string', format: 'date-time' },
            documents: { type: 'array', items: { type: 'string' } },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      try {
        const certification = {
          ...body,
          issuedDate: new Date(body.issuedDate),
          expiryDate: body.expiryDate ? new Date(body.expiryDate) : undefined,
        };
        const farmer = await farmerPortalService.addCertification(id, certification);
        return reply.send(farmer);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /farmers/:id/crops - Add crop to farmer
    farmerRoutes.post('/:id/crops', {
      schema: {
        description: 'Add crop to farmer',
        tags: ['Farmers'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
        body: {
          type: 'object',
          required: ['cropType', 'season', 'areaHectares'],
          properties: {
            cropType: { type: 'string' },
            variety: { type: 'string' },
            season: { type: 'string' },
            areaHectares: { type: 'number' },
            expectedYield: { type: 'number' },
            harvestDate: { type: 'string', format: 'date-time' },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      try {
        const crop = {
          ...body,
          harvestDate: body.harvestDate ? new Date(body.harvestDate) : undefined,
        };
        const farmer = await farmerPortalService.addCrop(id, crop);
        return reply.send(farmer);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /farmers/search - Search farmers
    farmerRoutes.get('/search', {
      schema: {
        description: 'Search farmers',
        tags: ['Farmers'],
        querystring: {
          type: 'object',
          required: ['q'],
          properties: {
            q: { type: 'string' },
            limit: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      try {
        const farmers = await farmerPortalService.searchFarmers(query.q, query.limit || 20);
        return reply.send({ data: farmers });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });
  });
}

