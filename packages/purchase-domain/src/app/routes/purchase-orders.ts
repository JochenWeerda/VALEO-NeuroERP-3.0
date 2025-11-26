import type { FastifyInstance } from 'fastify';
import { PurchaseOrderService } from '../../domain/services/purchase-order-service-new';
import { PurchaseOrderRepository } from '../../infra/repositories/purchase-order-repository';
import { ISMSAuditLogger } from '../../security/isms-audit-logger';
import { CryptoService } from '../../security/crypto-service';
import { PurchaseOrderFilter, PurchaseOrderSort } from '../../infra/repositories/purchase-order-repository';
import { container, ServiceContainer } from '../../infra/di/container';
import { TenantContextProvider } from '../../infra/di/tenant-context';

// Initialize DI container
container.initializeCoreServices();

// Create service instance with mock dependencies for now
const repository = new PurchaseOrderRepository('default-tenant');
const auditLogger = new ISMSAuditLogger('purchase-order-service', 'development');
const cryptoService = new CryptoService();

const purchaseOrderService = new PurchaseOrderService({
  repository,
  auditLogger,
  cryptoService
});

// Helper function to get tenant ID
function getTenantId(request: any): string {
  // Extract from JWT, headers, or context
  return request.tenantId || request.user?.tenantId || request.headers['x-tenant-id'] || 'default-tenant';
}

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  try {
    // Extract user from JWT token or session
    const user = request.user || request.session?.user;

    if (!user) {
      // Try to extract from Authorization header
      const authHeader = request.headers.authorization;
      if (authHeader && authHeader.startsWith('Bearer ')) {
        // In a real implementation, you'd verify the JWT token here
        // For now, we'll assume the token contains user info
        const token = authHeader.substring(7);
        // Mock JWT decoding - in production, use proper JWT library
        try {
          const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
          return payload.sub || payload.userId || payload.id || 'system';
        } catch {
          // Invalid token format
          return 'system';
        }
      }
    }

    return user?.id || user?.userId || user?.sub || 'system';
  } catch (error) {
    // Log authentication error but don't expose details
    console.warn('Authentication context extraction failed');
    return 'system';
  }
}

// Security middleware for input validation and sanitization
function validatePurchaseOrderInput(input: any): void {
  // Basic input validation and sanitization
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
function checkPermission(request: any, action: string, resource: string): void {
  // TODO: Implement proper RBAC/ABAC authorization
  // For now, allow all authenticated users
  const userId = getAuthenticatedUserId(request);
  if (!userId) {
    throw new Error('Authentication required');
  }
}

export async function registerPurchaseOrderRoutes(fastify: FastifyInstance) {
  // Base path for purchase orders
  fastify.register(async (purchaseOrderRoutes) => {
    // GET /purchase-orders - List purchase orders
    purchaseOrderRoutes.get('/', {
      schema: {
        description: 'List purchase orders with pagination and filtering',
        tags: ['Purchase Orders'],
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
        const filter: PurchaseOrderFilter = {};
        const sort: PurchaseOrderSort = { field: 'createdAt', direction: 'desc' };

        if (query.supplierId) filter.supplierId = query.supplierId;
        if (query.status) filter.status = query.status as any;

        const page = parseInt(query.page) || 1;
        const pageSize = Math.min(parseInt(query.pageSize) || 20, 100);

                 const result = await purchaseOrderService.listPurchaseOrders(filter, sort, page, pageSize);

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

    // POST /purchase-orders - Create purchase order
    purchaseOrderRoutes.post('/', {
      schema: {
        description: 'Create a new purchase order',
        tags: ['Purchase Orders'],
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
        checkPermission(request, 'create', 'purchase-order');

        const body = request.body as any;

        // Input validation and sanitization
        validatePurchaseOrderInput(body);

        const createdBy = getAuthenticatedUserId(request);
        const order = await purchaseOrderService.createPurchaseOrder(
          {
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
          },
          createdBy
        );

        return reply.code(201).send({
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          status: order.status,
          createdAt: order.createdAt.toISOString()
        });
      } catch (error) {
        // Log security incidents for validation failures
        if ((error as Error).message.includes('Invalid') || (error as Error).message.includes('required')) {
          // Could log security incident here
        }
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /purchase-orders/:id - Get purchase order by ID
    purchaseOrderRoutes.get('/:id', {
      schema: {
        description: 'Get purchase order by ID',
        tags: ['Purchase Orders'],
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
        const order = await purchaseOrderService.getPurchaseOrderById(id);

        if (!order) {
          return reply.code(404).send({ error: 'Purchase order not found' });
        }

        return order.toJSON();
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // PATCH /purchase-orders/:id - Update purchase order
    purchaseOrderRoutes.patch('/:id', {
      schema: {
        description: 'Update purchase order',
        tags: ['Purchase Orders'],
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
            subject: { type: 'string' },
            description: { type: 'string' },
            deliveryDate: { type: 'string', format: 'date' },
            contactPerson: { type: 'string' },
            paymentTerms: { type: 'string' },
            currency: { type: 'string' },
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
            notes: { type: 'string' }
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
        if (body.subject !== undefined) updates.subject = body.subject;
        if (body.description !== undefined) updates.description = body.description;
        if (body.deliveryDate !== undefined) updates.deliveryDate = new Date(body.deliveryDate);
        if (body.contactPerson !== undefined) updates.contactPerson = body.contactPerson;
        if (body.paymentTerms !== undefined) updates.paymentTerms = body.paymentTerms;
        if (body.currency !== undefined) updates.currency = body.currency;
        if (body.taxRate !== undefined) updates.taxRate = body.taxRate;
        if (body.shippingAddress !== undefined) updates.shippingAddress = body.shippingAddress;
        if (body.notes !== undefined) updates.notes = body.notes;

        const updatedBy = getAuthenticatedUserId(request);
        const order = await purchaseOrderService.updatePurchaseOrder(id, updates, updatedBy);

        return {
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          status: order.status,
          updatedAt: order.updatedAt.toISOString(),
          version: order.version
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // DELETE /purchase-orders/:id - Delete purchase order
    purchaseOrderRoutes.delete('/:id', {
      schema: {
        description: 'Delete purchase order',
        tags: ['Purchase Orders'],
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
        const success = await purchaseOrderService.deletePurchaseOrder(id);

        if (!success) {
          return reply.code(404).send({ error: 'Purchase order not found' });
        }

        return reply.code(204).send();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /purchase-orders/:id/approve - Approve purchase order
    purchaseOrderRoutes.post('/:id/approve', {
      schema: {
        description: 'Approve purchase order',
        tags: ['Purchase Orders'],
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
        const approvedBy = getAuthenticatedUserId(request);
        const order = await purchaseOrderService.approvePurchaseOrder(id, approvedBy);

        return {
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          status: order.status,
          approvedAt: order.approvedAt?.toISOString(),
          approvedBy: order.approvedBy
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /purchase-orders/:id/order - Order purchase order
    purchaseOrderRoutes.post('/:id/order', {
      schema: {
        description: 'Order purchase order (send to supplier)',
        tags: ['Purchase Orders'],
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
        const orderedBy = getAuthenticatedUserId(request);
        const order = await purchaseOrderService.orderPurchaseOrder(id, orderedBy);

        return {
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          status: order.status,
          orderedAt: order.orderedAt?.toISOString(),
          orderedBy: order.orderedBy
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /purchase-orders/:id/mark-partial-delivery - Mark as partially delivered
    purchaseOrderRoutes.post('/:id/mark-partial-delivery', {
      schema: {
        description: 'Mark purchase order as partially delivered',
        tags: ['Purchase Orders'],
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
        const updatedBy = getAuthenticatedUserId(request);
        const order = await purchaseOrderService.markPartiallyDelivered(id, updatedBy);

        return {
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          status: order.status,
          updatedAt: order.updatedAt.toISOString()
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /purchase-orders/:id/mark-delivered - Mark as delivered
    purchaseOrderRoutes.post('/:id/mark-delivered', {
      schema: {
        description: 'Mark purchase order as delivered',
        tags: ['Purchase Orders'],
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
        checkPermission(request, 'update', 'purchase-order');
        const { id } = request.params as { id: string };
        const updatedBy = getAuthenticatedUserId(request);
        const order = await purchaseOrderService.markDelivered(id, updatedBy);

        return {
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          status: order.status,
          updatedAt: order.updatedAt.toISOString()
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /purchase-orders/:id/mark-fully-delivered - Mark as fully delivered
    purchaseOrderRoutes.post('/:id/mark-fully-delivered', {
      schema: {
        description: 'Mark purchase order as fully delivered',
        tags: ['Purchase Orders'],
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
        checkPermission(request, 'update', 'purchase-order');
        const { id } = request.params as { id: string };
        const updatedBy = getAuthenticatedUserId(request);
        const order = await purchaseOrderService.markFullyDelivered(id, updatedBy);

        return {
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          status: order.status,
          updatedAt: order.updatedAt.toISOString()
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /purchase-orders/:id/update-delivery-status - Update delivery status
    purchaseOrderRoutes.post('/:id/update-delivery-status', {
      schema: {
        description: 'Update purchase order delivery status',
        tags: ['Purchase Orders'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        body: {
          type: 'object',
          required: ['deliveryStatus'],
          properties: {
            deliveryStatus: {
              type: 'string',
              enum: ['PARTIAL', 'FULL']
            }
          }
        },
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        checkPermission(request, 'update', 'purchase-order');
        const { id } = request.params as { id: string };
        const body = request.body as any;
        const updatedBy = getAuthenticatedUserId(request);

        // Validate delivery status
        if (!['PARTIAL', 'FULL'].includes(body.deliveryStatus)) {
          return reply.code(400).send({ error: 'Invalid delivery status. Must be PARTIAL or FULL' });
        }

        const order = await purchaseOrderService.updateDeliveryStatus(id, body.deliveryStatus, updatedBy);

        return {
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          status: order.status,
          deliveryStatus: body.deliveryStatus,
          updatedAt: order.updatedAt.toISOString()
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /purchase-orders/:id/mark-invoiced - Mark purchase order as invoiced
    purchaseOrderRoutes.post('/:id/mark-invoiced', {
      schema: {
        description: 'Mark purchase order as invoiced (supplier invoice received)',
        tags: ['Purchase Orders'],
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
        checkPermission(request, 'update', 'purchase-order');
        const { id } = request.params as { id: string };
        const invoicedBy = getAuthenticatedUserId(request);
        const order = await purchaseOrderService.markAsInvoiced(id, invoicedBy);

        return {
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          status: order.status,
          supplierId: order.supplierId,
          totalAmount: order.totalAmount,
          message: 'Purchase order marked as invoiced'
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /purchase-orders/:id/cancel - Cancel purchase order
    purchaseOrderRoutes.post('/:id/cancel', {
      schema: {
        description: 'Cancel purchase order',
        tags: ['Purchase Orders'],
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
        const updatedBy = getAuthenticatedUserId(request);
        const order = await purchaseOrderService.cancelPurchaseOrder(id, updatedBy);

        return {
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          status: order.status,
          updatedAt: order.updatedAt.toISOString()
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /purchase-orders/supplier/:supplierId - Get purchase orders by supplier
    purchaseOrderRoutes.get('/supplier/:supplierId', {
      schema: {
        description: 'Get purchase orders by supplier ID',
        tags: ['Purchase Orders'],
        params: {
          type: 'object',
          required: ['supplierId'],
          properties: {
            supplierId: { type: 'string' },
          },
        },
        response: {
          200: {
            type: 'array',
          },
        },
      },
    }, async (request, reply) => {
      try {
        const { supplierId } = request.params as { supplierId: string };
        const orders = await purchaseOrderService.getPurchaseOrdersBySupplier(supplierId);

        return orders.map(order => ({
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          subject: order.subject,
          status: order.status,
          totalAmount: order.totalAmount,
          orderDate: order.orderDate.toISOString(),
          deliveryDate: order.deliveryDate.toISOString(),
          createdAt: order.createdAt.toISOString()
        }));
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /purchase-orders/overdue - Get overdue purchase orders
    purchaseOrderRoutes.get('/overdue', {
      schema: {
        description: 'Get overdue purchase orders',
        tags: ['Purchase Orders'],
        response: {
          200: {
            type: 'array',
          },
        },
      },
    }, async (request, reply) => {
      try {
        const orders = await purchaseOrderService.getOverduePurchaseOrders();

        return orders.map(order => ({
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          supplierId: order.supplierId,
          subject: order.subject,
          status: order.status,
          totalAmount: order.totalAmount,
          deliveryDate: order.deliveryDate.toISOString(),
          daysOverdue: Math.ceil((Date.now() - order.deliveryDate.getTime()) / (1000 * 60 * 60 * 24)),
          createdAt: order.createdAt.toISOString()
        }));
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /purchase-orders/pending-approval - Get purchase orders pending approval
    purchaseOrderRoutes.get('/pending-approval', {
      schema: {
        description: 'Get purchase orders pending approval',
        tags: ['Purchase Orders'],
        response: {
          200: {
            type: 'array',
          },
        },
      },
    }, async (request, reply) => {
      try {
        const orders = await purchaseOrderService.getPendingApprovalPurchaseOrders();

        return orders.map(order => ({
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          supplierId: order.supplierId,
          subject: order.subject,
          status: order.status,
          totalAmount: order.totalAmount,
          createdAt: order.createdAt.toISOString()
        }));
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /purchase-orders/search - Advanced search for purchase orders
    purchaseOrderRoutes.get('/search', {
      schema: {
        description: 'Advanced search for purchase orders with filters',
        tags: ['Purchase Orders'],
        querystring: {
          type: 'object',
          properties: {
            supplierId: { type: 'string' },
            status: { type: 'string', enum: ['ENTWURF', 'FREIGEGEBEN', 'BESTELLT', 'TEILGELIEFERT', 'GELIEFERT', 'STORNIERT'] },
            search: { type: 'string', description: 'Search in PO number, subject, description, supplier' },
            deliveryDateFrom: { type: 'string', format: 'date' },
            deliveryDateTo: { type: 'string', format: 'date' },
            totalAmountMin: { type: 'number' },
            totalAmountMax: { type: 'number' },
            createdBy: { type: 'string' },
            sortField: { type: 'string', enum: ['createdAt', 'updatedAt', 'orderDate', 'deliveryDate', 'totalAmount', 'purchaseOrderNumber'] },
            sortDirection: { type: 'string', enum: ['asc', 'desc'] },
            page: { type: 'integer', minimum: 1, default: 1 },
            pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 }
          }
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
                }
              }
            }
          }
        }
      },
    }, async (request, reply) => {
      try {
        const query = request.query as any;

        const filters = {
          supplierId: query.supplierId,
          status: query.status,
          search: query.search,
          deliveryDateFrom: query.deliveryDateFrom ? new Date(query.deliveryDateFrom) : undefined,
          deliveryDateTo: query.deliveryDateTo ? new Date(query.deliveryDateTo) : undefined,
          totalAmountMin: query.totalAmountMin,
          totalAmountMax: query.totalAmountMax,
          createdBy: query.createdBy
        };

        const sort: PurchaseOrderSort = {
          field: query.sortField || 'createdAt',
          direction: query.sortDirection || 'desc'
        };

        const page = parseInt(query.page) || 1;
        const pageSize = Math.min(parseInt(query.pageSize) || 20, 100);

        const result = await purchaseOrderService.searchPurchaseOrders(filters, sort, page, pageSize);

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
            createdBy: order.createdBy,
            createdAt: order.createdAt.toISOString(),
            updatedAt: order.updatedAt.toISOString()
          })),
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

    // GET /purchase-orders/statistics - Get purchase order statistics
    purchaseOrderRoutes.get('/statistics', {
      schema: {
        description: 'Get purchase order statistics',
        tags: ['Purchase Orders'],
        response: {
          200: {
            type: 'object',
            properties: {
              total: { type: 'integer' },
              byStatus: { type: 'object' },
              totalValue: { type: 'number' },
              averageValue: { type: 'number' },
              overdueCount: { type: 'integer' },
              pendingApprovalCount: { type: 'integer' }
            },
          },
        },
      },
    }, async (request, reply) => {
      try {
        const statistics = await purchaseOrderService.getPurchaseOrderStatistics();
        return statistics;
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // PATCH /purchase-orders/:id/delivery-date - Update delivery date
    purchaseOrderRoutes.patch('/:id/delivery-date', {
      schema: {
        description: 'Update purchase order delivery date',
        tags: ['Purchase Orders'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        body: {
          type: 'object',
          required: ['deliveryDate'],
          properties: {
            deliveryDate: { type: 'string', format: 'date' }
          }
        },
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        checkPermission(request, 'update', 'purchase-order');
        const { id } = request.params as { id: string };
        const body = request.body as any;
        const updatedBy = getAuthenticatedUserId(request);

        const newDeliveryDate = new Date(body.deliveryDate);
        const order = await purchaseOrderService.updateDeliveryDate(id, newDeliveryDate, updatedBy);

        return {
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          deliveryDate: order.deliveryDate.toISOString(),
          updatedAt: order.updatedAt.toISOString(),
          version: order.version
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /purchase-orders/delivery-date-range - Get orders by delivery date range
    purchaseOrderRoutes.get('/delivery-date-range', {
      schema: {
        description: 'Get purchase orders by delivery date range',
        tags: ['Purchase Orders'],
        querystring: {
          type: 'object',
          required: ['startDate', 'endDate'],
          properties: {
            startDate: { type: 'string', format: 'date' },
            endDate: { type: 'string', format: 'date' }
          }
        },
        response: {
          200: {
            type: 'array',
          },
        },
      },
    }, async (request, reply) => {
      try {
        const query = request.query as any;
        const startDate = new Date(query.startDate);
        const endDate = new Date(query.endDate);

        const orders = await purchaseOrderService.getPurchaseOrdersByDeliveryDateRange(startDate, endDate);

        return orders.map(order => ({
          id: order.id,
          purchaseOrderNumber: order.purchaseOrderNumber,
          supplierId: order.supplierId,
          subject: order.subject,
          status: order.status,
          deliveryDate: order.deliveryDate.toISOString(),
          totalAmount: order.totalAmount,
          createdAt: order.createdAt.toISOString()
        }));
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /purchase-orders/:id/overdue - Check if order is overdue
    purchaseOrderRoutes.get('/:id/overdue', {
      schema: {
        description: 'Check if purchase order is overdue',
        tags: ['Purchase Orders'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        response: {
          200: {
            type: 'object',
            properties: {
              isOverdue: { type: 'boolean' },
              deliveryDate: { type: 'string' },
              daysOverdue: { type: 'integer' }
            },
          },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const order = await purchaseOrderService.getPurchaseOrderById(id);

        if (!order) {
          return reply.code(404).send({ error: 'Purchase order not found' });
        }

        const isOverdue = await purchaseOrderService.isPurchaseOrderOverdue(id);
        const daysOverdue = isOverdue ?
          Math.ceil((Date.now() - order.deliveryDate.getTime()) / (1000 * 60 * 60 * 24)) : 0;

        return {
          isOverdue,
          deliveryDate: order.deliveryDate.toISOString(),
          daysOverdue
        };
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });
  }, { prefix: '/purchase-orders' });
}