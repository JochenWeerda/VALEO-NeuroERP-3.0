import { FastifyInstance } from 'fastify';
import { SalesOrderService } from '../../domain/services/sales-order-service';
import { SalesOrderRepository } from '../../infra/repositories/sales-order-repository';
import { SalesOfferService } from '../../domain/services/sales-offer-service';
import { SalesOfferRepository } from '../../infra/repositories/sales-offer-repository';
import { SalesOrderFilter, SalesOrderSort } from '../../infra/repositories/sales-order-repository';

// Initialize services
const salesOrderRepository = new SalesOrderRepository();
const salesOfferRepository = new SalesOfferRepository();
const salesOfferService = new SalesOfferService({ salesOfferRepository });
const salesOrderService = new SalesOrderService({ 
  salesOrderRepository, 
  salesOfferService 
});

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

export async function registerOrderRoutes(fastify: FastifyInstance) {
  fastify.register(async (orderRoutes) => {
    
    // GET /orders - List orders with filtering and pagination
    orderRoutes.get('/', {
      schema: {
        description: 'List sales orders with pagination and filtering',
        tags: ['Sales Orders'],
        querystring: {
          type: 'object',
          properties: {
            customerId: { type: 'string' },
            status: { type: 'string', enum: ['DRAFT', 'CONFIRMED', 'IN_PROGRESS', 'PARTIALLY_DELIVERED', 'DELIVERED', 'INVOICED', 'COMPLETED', 'CANCELLED'] },
            sourceOfferId: { type: 'string' },
            search: { type: 'string' },
            page: { type: 'integer', minimum: 1, default: 1 },
            pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
            sortField: { type: 'string', enum: ['createdAt', 'updatedAt', 'orderDate', 'deliveryDate', 'totalAmount', 'orderNumber', 'status'], default: 'createdAt' },
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
        const filter: SalesOrderFilter = {};
        const sort: SalesOrderSort = { 
          field: query.sortField || 'createdAt', 
          direction: query.sortDirection || 'desc' 
        };

        if (query.customerId) filter.customerId = query.customerId;
        if (query.status) filter.status = query.status as any;
        if (query.sourceOfferId) filter.sourceOfferId = query.sourceOfferId;
        if (query.search) filter.search = query.search;

        const page = parseInt(query.page) || 1;
        const pageSize = Math.min(parseInt(query.pageSize) || 20, 100);

        const result = await salesOrderService.listSalesOrders(filter, sort, page, pageSize);

        return {
          data: result.items.map(order => ({
            id: order.id,
            orderNumber: order.orderNumber,
            customerId: order.customerId,
            sourceOfferId: order.sourceOfferId,
            subject: order.subject,
            status: order.status,
            orderDate: order.orderDate.toISOString(),
            deliveryDate: order.deliveryDate.toISOString(),
            totalAmount: order.totalAmount,
            currency: order.currency,
            createdAt: order.createdAt.toISOString(),
            updatedAt: order.updatedAt.toISOString(),
            createdBy: order.createdBy
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

    // POST /orders - Create new order
    orderRoutes.post('/', {
      schema: {
        description: 'Create a new sales order',
        tags: ['Sales Orders'],
        body: {
          type: 'object',
          required: ['customerId', 'subject', 'description', 'deliveryDate', 'items'],
          properties: {
            customerId: { type: 'string' },
            sourceOfferId: { type: 'string' },
            subject: { type: 'string' },
            description: { type: 'string' },
            deliveryDate: { type: 'string', format: 'date' },
            contactPerson: { type: 'string' },
            paymentTerms: { type: 'string' },
            currency: { type: 'string', default: 'EUR' },
            taxRate: { type: 'number', default: 19.0 },
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
                  discountPercent: { type: 'number', minimum: 0, maximum: 100, default: 0 },
                  taxRate: { type: 'number', default: 19.0 },
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
        const body = request.body as any;
        const createdBy = getAuthenticatedUserId(request);

        // Calculate item totals
        const items = body.items.map((item: any) => {
          const quantity = item.quantity;
          const unitPrice = item.unitPrice;
          const discountPercent = item.discountPercent || 0;
          const taxRate = item.taxRate || body.taxRate || 19.0;
          
          const netAmount = quantity * unitPrice * (1 - discountPercent / 100);
          const taxAmount = netAmount * (taxRate / 100);
          const totalAmount = netAmount + taxAmount;

          return {
            ...item,
            netAmount,
            taxAmount,
            totalAmount,
            deliveryDate: item.deliveryDate ? new Date(item.deliveryDate) : undefined
          };
        });

        const order = await salesOrderService.createSalesOrder(
          {
            customerId: body.customerId,
            sourceOfferId: body.sourceOfferId,
            subject: body.subject,
            description: body.description,
            deliveryDate: new Date(body.deliveryDate),
            contactPerson: body.contactPerson,
            paymentTerms: body.paymentTerms,
            currency: body.currency,
            taxRate: body.taxRate,
            notes: body.notes,
            items
          },
          createdBy
        );

        return reply.code(201).send({
          id: order.id,
          orderNumber: order.orderNumber,
          status: order.status,
          totalAmount: order.totalAmount,
          createdAt: order.createdAt.toISOString()
        });
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /orders/:id - Get order by ID
    orderRoutes.get('/:id', {
      schema: {
        description: 'Get sales order by ID',
        tags: ['Sales Orders'],
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
        const order = await salesOrderService.getSalesOrderById(id);

        if (!order) {
          return reply.code(404).send({ error: 'Sales order not found' });
        }

        return order.toJSON();
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // PATCH /orders/:id - Update order
    orderRoutes.patch('/:id', {
      schema: {
        description: 'Update sales order',
        tags: ['Sales Orders'],
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
        const updatedBy = getAuthenticatedUserId(request);

        const updates: any = {};
        if (body.subject !== undefined) updates.subject = body.subject;
        if (body.description !== undefined) updates.description = body.description;
        if (body.deliveryDate !== undefined) updates.deliveryDate = new Date(body.deliveryDate);
        if (body.contactPerson !== undefined) updates.contactPerson = body.contactPerson;
        if (body.paymentTerms !== undefined) updates.paymentTerms = body.paymentTerms;
        if (body.currency !== undefined) updates.currency = body.currency;
        if (body.taxRate !== undefined) updates.taxRate = body.taxRate;
        if (body.notes !== undefined) updates.notes = body.notes;

        const order = await salesOrderService.updateSalesOrder(id, updates, updatedBy);

        return {
          id: order.id,
          orderNumber: order.orderNumber,
          status: order.status,
          totalAmount: order.totalAmount,
          updatedAt: order.updatedAt.toISOString(),
          version: order.version
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // DELETE /orders/:id - Delete order
    orderRoutes.delete('/:id', {
      schema: {
        description: 'Delete sales order (draft only)',
        tags: ['Sales Orders'],
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
        const success = await salesOrderService.deleteSalesOrder(id);

        if (!success) {
          return reply.code(404).send({ error: 'Sales order not found' });
        }

        return reply.code(204).send();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /orders/:id/confirm - Confirm order
    orderRoutes.post('/:id/confirm', {
      schema: {
        description: 'Confirm sales order',
        tags: ['Sales Orders'],
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
        const confirmedBy = getAuthenticatedUserId(request);
        const order = await salesOrderService.confirmOrder(id, confirmedBy);

        return {
          id: order.id,
          orderNumber: order.orderNumber,
          status: order.status,
          confirmedAt: order.confirmedAt?.toISOString(),
          confirmedBy: order.confirmedBy
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /orders/:id/start-progress - Start order progress
    orderRoutes.post('/:id/start-progress', {
      schema: {
        description: 'Start order progress',
        tags: ['Sales Orders'],
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
        const order = await salesOrderService.startOrderProgress(id, updatedBy);

        return {
          id: order.id,
          orderNumber: order.orderNumber,
          status: order.status,
          updatedAt: order.updatedAt.toISOString()
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /orders/:id/cancel - Cancel order
    orderRoutes.post('/:id/cancel', {
      schema: {
        description: 'Cancel sales order',
        tags: ['Sales Orders'],
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
        const cancelledBy = getAuthenticatedUserId(request);
        
        const order = await salesOrderService.cancelOrder(id, cancelledBy, body.reason);

        return {
          id: order.id,
          orderNumber: order.orderNumber,
          status: order.status,
          cancelledAt: order.cancelledAt?.toISOString(),
          cancellationReason: order.cancellationReason
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /orders/statistics - Get order statistics
    orderRoutes.get('/statistics', {
      schema: {
        description: 'Get sales order statistics',
        tags: ['Sales Orders'],
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const statistics = await salesOrderService.getSalesOrderStatistics();
        return statistics;
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /orders/overdue - Get overdue orders
    orderRoutes.get('/overdue', {
      schema: {
        description: 'Get overdue sales orders',
        tags: ['Sales Orders'],
        response: {
          200: { type: 'array' },
        },
      },
    }, async (request, reply) => {
      try {
        const orders = await salesOrderService.getOverdueSalesOrders();
        return orders.map(order => order.toJSON());
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // POST /orders/:id/create-delivery - Convert order to delivery note
    orderRoutes.post('/:id/create-delivery', {
      schema: {
        description: 'Create delivery note from sales order',
        tags: ['Sales Orders'],
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
            plannedDeliveryDate: { type: 'string', format: 'date' },
            carrierInfo: {
              type: 'object',
              properties: {
                carrierName: { type: 'string' },
                trackingNumber: { type: 'string' },
                carrierService: { type: 'string' }
              }
            },
            specialInstructions: { type: 'string' },
            deliveryAddress: {
              type: 'object',
              properties: {
                name: { type: 'string' },
                street: { type: 'string' },
                postalCode: { type: 'string' },
                city: { type: 'string' },
                country: { type: 'string' },
                state: { type: 'string' }
              }
            },
            partialDelivery: {
              type: 'object',
              properties: {
                itemQuantities: { type: 'object' }
              }
            }
          }
        },
        response: {
          201: {
            type: 'object',
            properties: {
              deliveryNoteId: { type: 'string' },
              deliveryNoteNumber: { type: 'string' },
              status: { type: 'string' },
              totalAmount: { type: 'number' },
              message: { type: 'string' }
            }
          },
        },
      },
    }, async (request, reply) => {
      try {
        const { id } = request.params as { id: string };
        const body = request.body as any;
        const convertedBy = getAuthenticatedUserId(request);

        // Import DeliveryNoteService dynamically to avoid circular dependencies
        const { DeliveryNoteService } = await import('../../domain/services/delivery-note-service');
        const { DeliveryNoteRepository } = await import('../../infra/repositories/delivery-note-repository');
        
        const deliveryNoteRepository = new DeliveryNoteRepository();
        const deliveryNoteService = new DeliveryNoteService({ 
          deliveryNoteRepository, 
          salesOrderService 
        });

        const options: any = {};
        if (body.plannedDeliveryDate) options.plannedDeliveryDate = new Date(body.plannedDeliveryDate);
        if (body.carrierInfo) options.carrierInfo = body.carrierInfo;
        if (body.specialInstructions) options.specialInstructions = body.specialInstructions;
        if (body.deliveryAddress) options.deliveryAddress = body.deliveryAddress;
        if (body.partialDelivery) options.partialDelivery = body.partialDelivery;

        const deliveryNote = await deliveryNoteService.convertOrderToDeliveryNote(
          id, 
          convertedBy,
          options
        );

        return reply.code(201).send({
          deliveryNoteId: deliveryNote.id,
          deliveryNoteNumber: deliveryNote.deliveryNoteNumber,
          status: deliveryNote.status,
          totalAmount: deliveryNote.totalAmount,
          message: `Sales order ${id} successfully converted to delivery note ${deliveryNote.deliveryNoteNumber}`
        });
      } catch (error) {
        const errorMessage = (error as Error).message;
        
        if (errorMessage.includes('not found')) {
          return reply.code(404).send({ error: errorMessage });
        } else if (errorMessage.includes('confirmed') || errorMessage.includes('active delivery') || errorMessage.includes('cannot be delivered')) {
          return reply.code(400).send({ error: errorMessage });
        } else {
          return reply.code(500).send({ error: errorMessage });
        }
      }
    });

    // GET /orders/:id/deliveries - Get delivery notes for order
    orderRoutes.get('/:id/deliveries', {
      schema: {
        description: 'Get delivery notes created from this order',
        tags: ['Sales Orders'],
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

        // Import DeliveryNoteService dynamically
        const { DeliveryNoteService } = await import('../../domain/services/delivery-note-service');
        const { DeliveryNoteRepository } = await import('../../infra/repositories/delivery-note-repository');
        
        const deliveryNoteRepository = new DeliveryNoteRepository();
        const deliveryNoteService = new DeliveryNoteService({ 
          deliveryNoteRepository, 
          salesOrderService 
        });

        const deliveryNotes = await deliveryNoteService.getDeliveryNotesByOrderId(id);

        return deliveryNotes.map(deliveryNote => ({
          id: deliveryNote.id,
          deliveryNoteNumber: deliveryNote.deliveryNoteNumber,
          status: deliveryNote.status,
          plannedDeliveryDate: deliveryNote.plannedDeliveryDate.toISOString(),
          actualDeliveryDate: deliveryNote.actualDeliveryDate?.toISOString(),
          totalAmount: deliveryNote.totalAmount,
          createdAt: deliveryNote.createdAt.toISOString()
        }));
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /orders/:id/prepare-delivery - Check if order can be prepared for delivery
    orderRoutes.get('/:id/prepare-delivery', {
      schema: {
        description: 'Check if order can be prepared for delivery and get deliverable items',
        tags: ['Sales Orders'],
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
        const preparationInfo = await salesOrderService.prepareForDelivery(id);
        return preparationInfo;
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

  }, { prefix: '/orders' });
}