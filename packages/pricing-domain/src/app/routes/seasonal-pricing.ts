import { FastifyInstance } from 'fastify';
import { SeasonalPricingService } from '../../domain/services/seasonal-pricing-service';
import { CreateSeasonalPricingRule, UpdateSeasonalPricingRule, Season } from '../../domain/entities/seasonal-pricing-rule';

// Initialize service
const seasonalPricingService = new SeasonalPricingService({});

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

// Helper function to get tenant ID
function getTenantId(request: any): string {
  return request.headers['x-tenant-id'] as string || 'default-tenant';
}

export async function registerSeasonalPricingRoutes(fastify: FastifyInstance) {
  fastify.register(async (seasonalRoutes) => {
    
    // GET /seasonal-pricing - List seasonal pricing rules
    seasonalRoutes.get('/', {
      schema: {
        description: 'List seasonal pricing rules',
        tags: ['Seasonal Pricing'],
        querystring: {
          type: 'object',
          properties: {
            productId: { type: 'string' },
            commodity: { type: 'string' },
            season: { type: 'string', enum: ['SPRING', 'AUTUMN', 'SUMMER', 'WINTER', 'ALL'] },
            active: { type: 'boolean' }
          },
        },
        response: {
          200: { type: 'array' },
        },
      },
    }, async (request, reply) => {
      try {
        const query = request.query as any;
        const tenantId = getTenantId(request);
        
        const rules = await seasonalPricingService.listSeasonalPricingRules(tenantId, {
          productId: query.productId,
          commodity: query.commodity,
          season: query.season as Season,
          active: query.active
        });

        return rules;
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // POST /seasonal-pricing - Create seasonal pricing rule
    seasonalRoutes.post('/', {
      schema: {
        description: 'Create a new seasonal pricing rule',
        tags: ['Seasonal Pricing'],
        body: {
          type: 'object',
          required: ['name', 'season', 'adjustmentType', 'adjustmentValue', 'validFrom'],
          properties: {
            name: { type: 'string' },
            description: { type: 'string' },
            code: { type: 'string' },
            productId: { type: 'string' },
            commodity: { type: 'string' },
            category: { type: 'string' },
            season: { type: 'string', enum: ['SPRING', 'AUTUMN', 'SUMMER', 'WINTER', 'ALL'] },
            monthRange: {
              type: 'object',
              properties: {
                startMonth: { type: 'integer', minimum: 1, maximum: 12 },
                endMonth: { type: 'integer', minimum: 1, maximum: 12 }
              }
            },
            adjustmentType: { type: 'string', enum: ['PERCENTAGE', 'FIXED', 'MULTIPLIER'] },
            adjustmentValue: { type: 'number' },
            priority: { type: 'integer', default: 0 },
            validFrom: { type: 'string', format: 'date-time' },
            validTo: { type: 'string', format: 'date-time' },
            active: { type: 'boolean', default: true }
          },
        },
        response: {
          201: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const body = request.body as any;
        const tenantId = getTenantId(request);
        const createdBy = getAuthenticatedUserId(request);

        const rule = await seasonalPricingService.createSeasonalPricingRule({
          tenantId,
          name: body.name,
          description: body.description,
          code: body.code,
          productId: body.productId,
          commodity: body.commodity,
          category: body.category,
          season: body.season,
          monthRange: body.monthRange,
          adjustmentType: body.adjustmentType,
          adjustmentValue: body.adjustmentValue,
          priority: body.priority || 0,
          validFrom: body.validFrom,
          validTo: body.validTo,
          active: body.active !== undefined ? body.active : true,
          createdBy
        });

        return reply.code(201).send(rule);
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /seasonal-pricing/:id - Get seasonal pricing rule by ID
    seasonalRoutes.get('/:id', {
      schema: {
        description: 'Get seasonal pricing rule by ID',
        tags: ['Seasonal Pricing'],
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
        const rule = await seasonalPricingService.getSeasonalPricingRuleById(id);

        if (!rule) {
          return reply.code(404).send({ error: 'Seasonal pricing rule not found' });
        }

        return rule;
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // PATCH /seasonal-pricing/:id - Update seasonal pricing rule
    seasonalRoutes.patch('/:id', {
      schema: {
        description: 'Update seasonal pricing rule',
        tags: ['Seasonal Pricing'],
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
            code: { type: 'string' },
            productId: { type: 'string' },
            commodity: { type: 'string' },
            category: { type: 'string' },
            season: { type: 'string', enum: ['SPRING', 'AUTUMN', 'SUMMER', 'WINTER', 'ALL'] },
            monthRange: {
              type: 'object',
              properties: {
                startMonth: { type: 'integer', minimum: 1, maximum: 12 },
                endMonth: { type: 'integer', minimum: 1, maximum: 12 }
              }
            },
            adjustmentType: { type: 'string', enum: ['PERCENTAGE', 'FIXED', 'MULTIPLIER'] },
            adjustmentValue: { type: 'number' },
            priority: { type: 'integer' },
            validFrom: { type: 'string', format: 'date-time' },
            validTo: { type: 'string', format: 'date-time' },
            active: { type: 'boolean' }
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

        const updates: Partial<UpdateSeasonalPricingRule> = {};
        if (body.name !== undefined) updates.name = body.name;
        if (body.description !== undefined) updates.description = body.description;
        if (body.code !== undefined) updates.code = body.code;
        if (body.productId !== undefined) updates.productId = body.productId;
        if (body.commodity !== undefined) updates.commodity = body.commodity;
        if (body.category !== undefined) updates.category = body.category;
        if (body.season !== undefined) updates.season = body.season;
        if (body.monthRange !== undefined) updates.monthRange = body.monthRange;
        if (body.adjustmentType !== undefined) updates.adjustmentType = body.adjustmentType;
        if (body.adjustmentValue !== undefined) updates.adjustmentValue = body.adjustmentValue;
        if (body.priority !== undefined) updates.priority = body.priority;
        if (body.validFrom !== undefined) updates.validFrom = body.validFrom;
        if (body.validTo !== undefined) updates.validTo = body.validTo;
        if (body.active !== undefined) updates.active = body.active;

        updates.updatedBy = updatedBy;

        const rule = await seasonalPricingService.updateSeasonalPricingRule(id, updates);

        return rule;
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // DELETE /seasonal-pricing/:id - Delete seasonal pricing rule
    seasonalRoutes.delete('/:id', {
      schema: {
        description: 'Delete seasonal pricing rule',
        tags: ['Seasonal Pricing'],
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
        const success = await seasonalPricingService.deleteSeasonalPricingRule(id);

        if (!success) {
          return reply.code(404).send({ error: 'Seasonal pricing rule not found' });
        }

        return reply.code(204).send();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /seasonal-pricing/calculate - Calculate seasonal price
    seasonalRoutes.post('/calculate', {
      schema: {
        description: 'Calculate seasonal price for a product',
        tags: ['Seasonal Pricing'],
        body: {
          type: 'object',
          required: ['productId', 'basePrice', 'orderDate'],
          properties: {
            productId: { type: 'string' },
            basePrice: { type: 'number', minimum: 0 },
            orderDate: { type: 'string', format: 'date-time' },
            commodity: { type: 'string' },
            category: { type: 'string' }
          },
        },
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const body = request.body as any;
        const tenantId = getTenantId(request);

        const result = await seasonalPricingService.getSeasonalPrice(
          tenantId,
          body.productId,
          body.basePrice,
          new Date(body.orderDate),
          {
            commodity: body.commodity,
            category: body.category
          }
        );

        return result;
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

  }, { prefix: '/seasonal-pricing' });
}
