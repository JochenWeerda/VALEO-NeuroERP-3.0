import { FastifyInstance } from 'fastify';
import { DeliveryNoteService } from '../../domain/services/delivery-note-service';
import { DeliveryNoteRepository } from '../../infra/repositories/delivery-note-repository';
import { SalesOrderService } from '../../domain/services/sales-order-service';
import { SalesOrderRepository } from '../../infra/repositories/sales-order-repository';
import { SalesOfferService } from '../../domain/services/sales-offer-service';
import { SalesOfferRepository } from '../../infra/repositories/sales-offer-repository';
import { DeliveryNoteFilter, DeliveryNoteSort } from '../../infra/repositories/delivery-note-repository';

// Initialize services
const deliveryNoteRepository = new DeliveryNoteRepository();
const salesOrderRepository = new SalesOrderRepository();
const salesOfferRepository = new SalesOfferRepository();
const salesOfferService = new SalesOfferService({ salesOfferRepository });
const salesOrderService = new SalesOrderService({ 
  salesOrderRepository, 
  salesOfferService 
});
const deliveryNoteService = new DeliveryNoteService({ 
  deliveryNoteRepository, 
  salesOrderService 
});

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

export async function registerDeliveryNoteRoutes(fastify: FastifyInstance) {
  fastify.register(async (deliveryNoteRoutes) => {
    
    // GET /delivery-notes - List delivery notes with filtering and pagination
    deliveryNoteRoutes.get('/', {
      schema: {
        description: 'List delivery notes with pagination and filtering',
        tags: ['Delivery Notes'],
        querystring: {
          type: 'object',
          properties: {
            customerId: { type: 'string' },
            orderId: { type: 'string' },
            status: { type: 'string', enum: ['PREPARED', 'READY_FOR_PICKUP', 'IN_TRANSIT', 'DELIVERED', 'CONFIRMED', 'RETURNED', 'CANCELLED'] },
            carrierName: { type: 'string' },
            trackingNumber: { type: 'string' },
            overdue: { type: 'boolean' },
            search: { type: 'string' },
            page: { type: 'integer', minimum: 1, default: 1 },
            pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
            sortField: { type: 'string', enum: ['createdAt', 'updatedAt', 'plannedDeliveryDate', 'actualDeliveryDate', 'totalAmount', 'deliveryNoteNumber', 'status'], default: 'createdAt' },
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
        const filter: DeliveryNoteFilter = {};
        const sort: DeliveryNoteSort = { 
          field: query.sortField || 'createdAt', 
          direction: query.sortDirection || 'desc' 
        };

        if (query.customerId) filter.customerId = query.customerId;
        if (query.orderId) filter.orderId = query.orderId;
        if (query.status) filter.status = query.status as any;
        if (query.carrierName) filter.carrierName = query.carrierName;
        if (query.trackingNumber) filter.trackingNumber = query.trackingNumber;
        if (query.overdue) filter.overdue = query.overdue;
        if (query.search) filter.search = query.search;

        const page = parseInt(query.page) || 1;
        const pageSize = Math.min(parseInt(query.pageSize) || 20, 100);

        const result = await deliveryNoteService.listDeliveryNotes(filter, sort, page, pageSize);

        return {
          data: result.items.map(deliveryNote => ({
            id: deliveryNote.id,
            deliveryNoteNumber: deliveryNote.deliveryNoteNumber,
            orderId: deliveryNote.orderId,
            customerId: deliveryNote.customerId,
            status: deliveryNote.status,
            plannedDeliveryDate: deliveryNote.plannedDeliveryDate.toISOString(),
            actualDeliveryDate: deliveryNote.actualDeliveryDate?.toISOString(),
            totalAmount: deliveryNote.totalAmount,
            carrierInfo: deliveryNote.carrierInfo,
            createdAt: deliveryNote.createdAt.toISOString(),
            updatedAt: deliveryNote.updatedAt.toISOString(),
            createdBy: deliveryNote.createdBy
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

    // POST /delivery-notes - Create new delivery note
    deliveryNoteRoutes.post('/', {
      schema: {
        description: 'Create a new delivery note',
        tags: ['Delivery Notes'],
        body: {
          type: 'object',
          required: ['orderId', 'customerId', 'deliveryAddress', 'plannedDeliveryDate', 'items'],
          properties: {
            orderId: { type: 'string' },
            customerId: { type: 'string' },
            deliveryAddress: {
              type: 'object',
              required: ['name', 'street', 'postalCode', 'city', 'country'],
              properties: {
                name: { type: 'string' },
                street: { type: 'string' },
                postalCode: { type: 'string' },
                city: { type: 'string' },
                country: { type: 'string' },
                state: { type: 'string' }
              }
            },
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
            items: {
              type: 'array',
              items: {
                type: 'object',
                required: ['itemType', 'description', 'orderedQuantity', 'deliveredQuantity', 'unitPrice'],
                properties: {
                  sourceOrderItemId: { type: 'string' },
                  itemType: { type: 'string', enum: ['PRODUCT', 'SERVICE'] },
                  articleId: { type: 'string' },
                  description: { type: 'string' },
                  orderedQuantity: { type: 'number', minimum: 0 },
                  deliveredQuantity: { type: 'number', minimum: 0 },
                  unitPrice: { type: 'number', minimum: 0 },
                  discountPercent: { type: 'number', minimum: 0, maximum: 100, default: 0 },
                  taxRate: { type: 'number', default: 19.0 },
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
          const deliveredQuantity = item.deliveredQuantity;
          const unitPrice = item.unitPrice;
          const discountPercent = item.discountPercent || 0;
          const taxRate = item.taxRate || 19.0;
          
          const netAmount = deliveredQuantity * unitPrice * (1 - discountPercent / 100);
          const taxAmount = netAmount * (taxRate / 100);
          const totalAmount = netAmount + taxAmount;

          return {
            ...item,
            netAmount,
            taxAmount,
            totalAmount
          };
        });

        const deliveryNote = await deliveryNoteService.createDeliveryNote(
          {
            orderId: body.orderId,
            customerId: body.customerId,
            deliveryAddress: body.deliveryAddress,
            plannedDeliveryDate: new Date(body.plannedDeliveryDate),
            carrierInfo: body.carrierInfo,
            specialInstructions: body.specialInstructions,
            items
          },
          createdBy
        );

        return reply.code(201).send({
          id: deliveryNote.id,
          deliveryNoteNumber: deliveryNote.deliveryNoteNumber,
          status: deliveryNote.status,
          totalAmount: deliveryNote.totalAmount,
          createdAt: deliveryNote.createdAt.toISOString()
        });
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /delivery-notes/:id - Get delivery note by ID
    deliveryNoteRoutes.get('/:id', {
      schema: {
        description: 'Get delivery note by ID',
        tags: ['Delivery Notes'],
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
        const deliveryNote = await deliveryNoteService.getDeliveryNoteById(id);

        if (!deliveryNote) {
          return reply.code(404).send({ error: 'Delivery note not found' });
        }

        return deliveryNote.toJSON();
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // PATCH /delivery-notes/:id - Update delivery note
    deliveryNoteRoutes.patch('/:id', {
      schema: {
        description: 'Update delivery note',
        tags: ['Delivery Notes'],
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
            carrierInfo: {
              type: 'object',
              properties: {
                carrierName: { type: 'string' },
                trackingNumber: { type: 'string' },
                carrierService: { type: 'string' }
              }
            },
            specialInstructions: { type: 'string' }
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
        if (body.plannedDeliveryDate !== undefined) updates.plannedDeliveryDate = new Date(body.plannedDeliveryDate);
        if (body.deliveryAddress !== undefined) updates.deliveryAddress = body.deliveryAddress;
        if (body.carrierInfo !== undefined) updates.carrierInfo = body.carrierInfo;
        if (body.specialInstructions !== undefined) updates.specialInstructions = body.specialInstructions;

        const deliveryNote = await deliveryNoteService.updateDeliveryNote(id, updates, updatedBy);

        return {
          id: deliveryNote.id,
          deliveryNoteNumber: deliveryNote.deliveryNoteNumber,
          status: deliveryNote.status,
          totalAmount: deliveryNote.totalAmount,
          updatedAt: deliveryNote.updatedAt.toISOString(),
          version: deliveryNote.version
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // DELETE /delivery-notes/:id - Delete delivery note
    deliveryNoteRoutes.delete('/:id', {
      schema: {
        description: 'Delete delivery note (prepared only)',
        tags: ['Delivery Notes'],
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
        const success = await deliveryNoteService.deleteDeliveryNote(id);

        if (!success) {
          return reply.code(404).send({ error: 'Delivery note not found' });
        }

        return reply.code(204).send();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /delivery-notes/:id/ready-for-pickup - Mark as ready for pickup
    deliveryNoteRoutes.post('/:id/ready-for-pickup', {
      schema: {
        description: 'Mark delivery note as ready for pickup',
        tags: ['Delivery Notes'],
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
        const preparedBy = getAuthenticatedUserId(request);
        const deliveryNote = await deliveryNoteService.markReadyForPickup(id, preparedBy);

        return {
          id: deliveryNote.id,
          deliveryNoteNumber: deliveryNote.deliveryNoteNumber,
          status: deliveryNote.status,
          preparedAt: deliveryNote.preparedAt?.toISOString(),
          preparedBy: deliveryNote.preparedBy
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /delivery-notes/:id/ship - Mark as in transit (shipped)
    deliveryNoteRoutes.post('/:id/ship', {
      schema: {
        description: 'Mark delivery note as shipped (in transit)',
        tags: ['Delivery Notes'],
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
            trackingNumber: { type: 'string' }
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
        const shippedBy = getAuthenticatedUserId(request);
        
        const deliveryNote = await deliveryNoteService.markInTransit(id, shippedBy, body.trackingNumber);

        return {
          id: deliveryNote.id,
          deliveryNoteNumber: deliveryNote.deliveryNoteNumber,
          status: deliveryNote.status,
          shippedAt: deliveryNote.shippedAt?.toISOString(),
          shippedBy: deliveryNote.shippedBy,
          trackingNumber: deliveryNote.carrierInfo?.trackingNumber
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /delivery-notes/:id/delivered - Mark as delivered
    deliveryNoteRoutes.post('/:id/delivered', {
      schema: {
        description: 'Mark delivery note as delivered',
        tags: ['Delivery Notes'],
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
            deliveredAt: { type: 'string', format: 'date-time' }
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
        
        const deliveredAt = body.deliveredAt ? new Date(body.deliveredAt) : undefined;
        const deliveryNote = await deliveryNoteService.markDelivered(id, deliveredAt);

        return {
          id: deliveryNote.id,
          deliveryNoteNumber: deliveryNote.deliveryNoteNumber,
          status: deliveryNote.status,
          deliveredAt: deliveryNote.deliveredAt?.toISOString(),
          actualDeliveryDate: deliveryNote.actualDeliveryDate?.toISOString()
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /delivery-notes/:id/confirm - Confirm delivery with proof
    deliveryNoteRoutes.post('/:id/confirm', {
      schema: {
        description: 'Confirm delivery with proof',
        tags: ['Delivery Notes'],
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
            deliveryProof: {
              type: 'object',
              properties: {
                signatureBase64: { type: 'string' },
                photoBase64: { type: 'string' },
                recipientName: { type: 'string' },
                notes: { type: 'string' }
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
        const confirmedBy = getAuthenticatedUserId(request);
        
        const deliveryNote = await deliveryNoteService.confirmDelivery(id, confirmedBy, body.deliveryProof);

        return {
          id: deliveryNote.id,
          deliveryNoteNumber: deliveryNote.deliveryNumber,
          status: deliveryNote.status,
          confirmedAt: deliveryNote.confirmedAt?.toISOString(),
          confirmedBy: deliveryNote.confirmedBy,
          deliveryProof: deliveryNote.deliveryProof
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /delivery-notes/:id/cancel - Cancel delivery note
    deliveryNoteRoutes.post('/:id/cancel', {
      schema: {
        description: 'Cancel delivery note',
        tags: ['Delivery Notes'],
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
        
        const deliveryNote = await deliveryNoteService.cancelDeliveryNote(id, cancelledBy, body.reason);

        return {
          id: deliveryNote.id,
          deliveryNoteNumber: deliveryNote.deliveryNoteNumber,
          status: deliveryNote.status,
          specialInstructions: deliveryNote.specialInstructions
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /delivery-notes/statistics - Get delivery statistics
    deliveryNoteRoutes.get('/statistics', {
      schema: {
        description: 'Get delivery note statistics',
        tags: ['Delivery Notes'],
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const statistics = await deliveryNoteService.getDeliveryStatistics();
        return statistics;
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /delivery-notes/overdue - Get overdue deliveries
    deliveryNoteRoutes.get('/overdue', {
      schema: {
        description: 'Get overdue delivery notes',
        tags: ['Delivery Notes'],
        response: {
          200: { type: 'array' },
        },
      },
    }, async (request, reply) => {
      try {
        const deliveryNotes = await deliveryNoteService.getOverdueDeliveries();
        return deliveryNotes.map(dn => dn.toJSON());
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /delivery-notes/today - Get deliveries scheduled for today
    deliveryNoteRoutes.get('/today', {
      schema: {
        description: 'Get delivery notes scheduled for today',
        tags: ['Delivery Notes'],
        response: {
          200: { type: 'array' },
        },
      },
    }, async (request, reply) => {
      try {
        const deliveryNotes = await deliveryNoteService.getDeliveriesToday();
        return deliveryNotes.map(dn => dn.toJSON());
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

  }, { prefix: '/delivery-notes' });
}

// CRITICAL: Order to Delivery Conversion Route - Add to Orders Routes
export async function addOrderToDeliveryRoutes(fastify: FastifyInstance) {
  fastify.register(async (orderRoutes) => {
    
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

  }, { prefix: '/orders' });
}
