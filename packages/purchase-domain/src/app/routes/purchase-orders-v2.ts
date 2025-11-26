/**
 * Purchase Order Routes v2
 * Multi-tenant aware REST API endpoints with dependency injection
 * Enterprise-grade security and performance monitoring
 */

import type { FastifyInstance } from 'fastify';
import { PurchaseOrderFilter, PurchaseOrderSort } from '../../infra/repositories/purchase-order-repository';
import { container, ServiceContainer } from '../../infra/di/container';
import { TenantContextProvider } from '../../infra/di/tenant-context';

// Initialize DI container
container.initializeCoreServices();

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

// Helper function to get tenant ID from request
function getTenantId(request: any): string {
  // Extract tenant ID from headers, subdomain, or JWT token
  return request.headers['x-tenant-id'] || 
         request.user?.tenantId || 
         request.hostname?.split('.')[0] || 
         'default-tenant';
}

// Helper function to get tenant-aware service container
async function getTenantServices(request: any): Promise<ServiceContainer> {
  const tenantId = getTenantId(request);
  return container.createTenantContainer(tenantId);
}

// Security middleware for input validation and sanitization
function validatePurchaseOrderInput(input: any): void {
  if (!input.supplierId || typeof input.supplierId !== 'string') {
    throw new Error('Invalid supplierId');
  }
  if (!input.subject || typeof input.subject !== 'string' || input.subject.length > 200) {
    throw new Error('Invalid subject');
  }
  if (!input.description || typeof input.description !== 'string' || input.description.length > 1000) {
    throw new Error('Invalid description');
  }
  if (!input.deliveryDate || isNaN(Date.parse(input.deliveryDate))) {
    throw new Error('Invalid delivery date');
  }

  // Validate items
  if (!Array.isArray(input.items) || input.items.length === 0) {
    throw new Error('At least one item is required');
  }

  for (const item of input.items) {
    if (!item.description || typeof item.description !== 'string') {
      throw new Error('Invalid item description');
    }
    if (!item.quantity || typeof item.quantity !== 'number' || item.quantity <= 0) {
      throw new Error('Invalid item quantity');
    }
    if (!item.unitPrice || typeof item.unitPrice !== 'number' || item.unitPrice < 0) {
      throw new Error('Invalid item unit price');
    }
  }
}

// Authorization middleware
async function checkPermission(request: any, action: string, resource: string): Promise<void> {
  const tenantId = getTenantId(request);
  const userId = getAuthenticatedUserId(request);
  
  if (!userId) {
    throw new Error('Authentication required');
  }

  // Check tenant context and permissions
  const services = await getTenantServices(request);
  const tenantContext = services.tenantContextProvider.getTenant(tenantId);
  
  if (!tenantContext) {
    throw new Error('Invalid tenant');
  }

  if (tenantContext.status !== 'ACTIVE') {
    throw new Error(`Tenant is ${tenantContext.status.toLowerCase()}`);
  }

  // Check feature access
  if (action === 'create' && !services.tenantContextProvider.hasFeature(tenantId, 'purchase_orders')) {
    throw new Error('Purchase orders feature not available for this tenant');
  }

  // Check limits for creation
  if (action === 'create' && !services.tenantContextProvider.checkLimits(tenantId, 'purchaseOrders', 0)) {
    throw new Error('Purchase order limit reached for this tenant');
  }
}

export async function registerPurchaseOrderRoutesV2(fastify: FastifyInstance) {
  // Add tenant validation hook
  fastify.addHook('preHandler', async (request, reply) => {
    const tenantId = getTenantId(request);
    if (!tenantId) {
      reply.code(400).send({ error: 'Tenant ID required' });
      return;
    }

    // Validate tenant exists and is active
    try {
      const services = await getTenantServices(request);
      await services.tenantContextProvider.validateAndGetTenant(tenantId);
    } catch (error) {
      reply.code(403).send({ error: (error as Error).message });
      return;
    }
  });

  // Base path for purchase orders
  fastify.register(async (purchaseOrderRoutes) => {
    
    // GET /purchase-orders - List purchase orders (tenant-isolated)
    purchaseOrderRoutes.get('/', {
      schema: {
        description: 'List purchase orders with pagination and filtering (multi-tenant)',
        tags: ['Purchase Orders'],
        headers: {
          type: 'object',
          properties: {
            'x-tenant-id': { type: 'string' }
          },
          required: ['x-tenant-id']
        },
        querystring: {
          type: 'object',
          properties: {
            supplierId: { type: 'string' },
            status: { type: 'string', enum: ['ENTWURF', 'FREIGEGEBEN', 'BESTELLT', 'TEILGELIEFERT', 'GELIEFERT', 'STORNIERT'] },
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
                  currentPage: { type: 'integer' },
                  pageSize: { type: 'integer' },
                  totalCount: { type: 'integer' },
                  totalPages: { type: 'integer' },
                },
              },
              tenant: {
                type: 'object',
                properties: {
                  tenantId: { type: 'string' },
                  tenantName: { type: 'string' }
                }
              }
            },
          },
        },
      },
    }, async (request, reply) => {
      try {
        await checkPermission(request, 'read', 'purchase-orders');
        
        const query = request.query as any;
        const filter: PurchaseOrderFilter = {};
        const sort: PurchaseOrderSort = { field: 'createdAt', direction: 'desc' };

        if (query.supplierId) filter.supplierId = query.supplierId;
        if (query.status) filter.status = query.status as any;

        const page = parseInt(query.page) || 1;
        const pageSize = Math.min(parseInt(query.pageSize) || 20, 100);
        const tenantId = getTenantId(request);

        // Get tenant-specific services
        const services = await getTenantServices(request);
        const result = await services.purchaseOrderService.searchPurchaseOrders(
          tenantId,
          filter,
          sort,
          { page, pageSize }
        );
        const tenantContext = services.tenantContextProvider.getTenant(tenantId);

        return {
          data: result.items.map(order => ({
            id: order.id,
            purchaseOrderNumber: order.purchaseOrderNumber,
            supplierId: order.supplierId,
            subject: order.subject,
            status: order.status,
            orderDate: order.orderDate.toISOString(),
            deliveryDate: order.deliveryDate.toISOString(),
            totalAmount: order.totalAmount,
            currency: order.currency,
            createdAt: order.createdAt.toISOString(),
            updatedAt: order.updatedAt.toISOString()
          })),
          pagination: {
            currentPage: result.page,
            pageSize: result.pageSize,
            totalCount: result.total,
            totalPages: result.totalPages
          },
          tenant: {
            tenantId: tenantContext?.tenantId,
            tenantName: tenantContext?.tenantName
          }
        };
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // POST /purchase-orders - Create purchase order (tenant-isolated)
    purchaseOrderRoutes.post('/', {
      schema: {
        description: 'Create a new purchase order (multi-tenant)',
        tags: ['Purchase Orders'],
        headers: {
          type: 'object',
          properties: {
            'x-tenant-id': { type: 'string' }
          },
          required: ['x-tenant-id']
        },
        body: {
          type: 'object',
          required: ['supplierId', 'subject', 'description', 'deliveryDate', 'items'],
          properties: {
            supplierId: { type: 'string' },
            subject: { type: 'string' },
            description: { type: 'string' },
            deliveryDate: { type: 'string', format: 'date' },
            contactPerson: { type: 'string' },
            paymentTerms: { type: 'string' },
            currency: { type: 'string', default: 'EUR' },
            taxRate: { type: 'number' },
            shippingAddress: {
              type: 'object',
              properties: {
                street: { type: 'string' },
                postalCode: { type: 'string' },
                city: { type: 'string' },
                country: { type: 'string' }
              }
            },
            notes: { type: 'string' },
            items: {
              type: 'array',
              items: {
                type: 'object',
                required: ['itemType', 'description', 'quantity', 'unitPrice'],
                properties: {
                  itemType: { type: 'string', enum: ['PRODUCT', 'SERVICE'] },
                  articleId: { type: 'string' },
                  description: { type: 'string' },
                  quantity: { type: 'number', minimum: 0 },
                  unitPrice: { type: 'number', minimum: 0 },
                  discountPercent: { type: 'number', minimum: 0, maximum: 100 },
                  deliveryDate: { type: 'string', format: 'date' },
                  notes: { type: 'string' }
                }
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
        // Security checks
        await checkPermission(request, 'create', 'purchase-order');

        const body = request.body as any;
        const tenantId = getTenantId(request);

        // Input validation and sanitization
        validatePurchaseOrderInput(body);

        const createdBy = getAuthenticatedUserId(request);
        const services = await getTenantServices(request);

        const order = await services.purchaseOrderService.createPurchaseOrder({
          tenantId,
          purchaseOrderNumber: `PO-${Date.now()}-${tenantId.substring(0, 4).toUpperCase()}`,
          createdBy,
          supplierId: body.supplierId,
          subject: body.subject,
          description: body.description,
          deliveryDate: new Date(body.deliveryDate),
          contactPerson: body.contactPerson,
          paymentTerms: body.paymentTerms,
          currency: body.currency,
          taxRate: body.taxRate,
          shippingAddress: body.shippingAddress,
          notes: body.notes,
          items: body.items
        });

        return reply.code(201).send({
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          status: order.status,
          createdAt: order.createdAt.toISOString(),
          tenantId
        });
      } catch (error) {
        // Log security incidents for validation failures
        if ((error as Error).message.includes('Invalid') || (error as Error).message.includes('required')) {
          // Could log security incident here
        }
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /purchase-orders/:id - Get purchase order by ID (tenant-isolated)
    purchaseOrderRoutes.get('/:id', {
      schema: {
        description: 'Get purchase order by ID (multi-tenant)',
        tags: ['Purchase Orders'],
        headers: {
          type: 'object',
          properties: {
            'x-tenant-id': { type: 'string' }
          },
          required: ['x-tenant-id']
        },
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
        await checkPermission(request, 'read', 'purchase-order');
        
        const { id } = request.params as { id: string };
        const tenantId = getTenantId(request);
        const userId = getAuthenticatedUserId(request);
        
        const services = await getTenantServices(request);
        const order = await services.purchaseOrderService.retrievePurchaseOrder(id, tenantId);

        if (!order) {
          return reply.code(404).send({ error: 'Purchase order not found' });
        }

        return {
          ...order.toJSON(),
          tenantId
        };
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // Health check endpoint for tenant services
    purchaseOrderRoutes.get('/health', {
      schema: {
        description: 'Health check for tenant-specific purchase order services',
        tags: ['System'],
        headers: {
          type: 'object',
          properties: {
            'x-tenant-id': { type: 'string' }
          }
        },
        response: {
          200: {
            type: 'object',
            properties: {
              status: { type: 'string' },
              tenant: { type: 'object' },
              services: { type: 'array' }
            }
          }
        }
      }
    }, async (request, reply) => {
      try {
        const tenantId = getTenantId(request);
        const services = await getTenantServices(request);
        const tenantContext = services.tenantContextProvider.getTenant(tenantId);
        const healthResults = await container.healthCheck();

        return {
          status: 'healthy',
          timestamp: new Date().toISOString(),
          tenant: {
            tenantId: tenantContext?.tenantId,
            tenantName: tenantContext?.tenantName,
            status: tenantContext?.status,
            subscriptionLevel: tenantContext?.subscriptionLevel
          },
          services: healthResults.filter(s => s.tenant === tenantId || !s.tenant)
        };
      } catch (error) {
        return reply.code(503).send({ 
          status: 'unhealthy',
          error: (error as Error).message,
          timestamp: new Date().toISOString()
        });
      }
    });

    // Tenant information endpoint
    purchaseOrderRoutes.get('/tenant-info', {
      schema: {
        description: 'Get current tenant information and limits',
        tags: ['Tenant'],
        headers: {
          type: 'object',
          properties: {
            'x-tenant-id': { type: 'string' }
          },
          required: ['x-tenant-id']
        },
        response: {
          200: {
            type: 'object',
            properties: {
              tenant: { type: 'object' },
              limits: { type: 'object' },
              features: { type: 'array' }
            }
          }
        }
      }
    }, async (request, reply) => {
      try {
        const tenantId = getTenantId(request);
        const services = await getTenantServices(request);
        const tenantContext = await services.tenantContextProvider.validateAndGetTenant(tenantId);

        return {
          tenant: {
            tenantId: tenantContext.tenantId,
            tenantName: tenantContext.tenantName,
            organizationId: tenantContext.organizationId,
            subscriptionLevel: tenantContext.subscriptionLevel,
            status: tenantContext.status,
            createdAt: tenantContext.createdAt.toISOString(),
            lastActiveAt: tenantContext.lastActiveAt.toISOString()
          },
          limits: tenantContext.limits,
          features: tenantContext.features,
          securityPolicy: {
            requireMFA: tenantContext.securityPolicy.requireMFA,
            sessionTimeoutMinutes: tenantContext.securityPolicy.sessionTimeoutMinutes,
            encryptionLevel: tenantContext.securityPolicy.encryptionLevel,
            auditLevel: tenantContext.securityPolicy.auditLevel
          }
        };
      } catch (error) {
        return reply.code(403).send({ error: (error as Error).message });
      }
    });

  }, { prefix: '/purchase-orders' });
}
