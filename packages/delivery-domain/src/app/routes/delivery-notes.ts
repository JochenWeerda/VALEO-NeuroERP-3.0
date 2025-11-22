/**
 * Delivery Notes API Routes
 * Fastify routes for delivery note management
 * ISO 27001 Communications Security Compliant
 */

import { FastifyInstance } from 'fastify';
import { DeliveryNoteService } from '../../domain/services/delivery-note-service';
import { DeliveryNoteFilter, DeliveryNoteSort } from '../../infra/repositories/delivery-note-repository';

// Helper function for user extraction
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

export async function deliveryNotesRoutes(app: FastifyInstance, options: { deliveryNoteService: DeliveryNoteService }) {
  const { deliveryNoteService } = options;

  /**
   * GET /delivery-notes
   * List delivery notes with pagination and filtering
   */
  app.get('/delivery-notes', {
    schema: {
      description: 'List delivery notes with pagination and filtering',
      tags: ['delivery-notes'],
      querystring: {
        type: 'object',
        properties: {
          customerId: { type: 'string' },
          salesOfferId: { type: 'string' },
          status: { type: 'string', enum: ['ENTWURF', 'VERSENDET', 'GELIEFERT', 'STORNIERT'] },
          deliveryDateFrom: { type: 'string', format: 'date' },
          deliveryDateTo: { type: 'string', format: 'date' },
          shipped: { type: 'boolean' },
          delivered: { type: 'boolean' },
          overdue: { type: 'boolean' },
          sortField: { type: 'string', enum: ['createdAt', 'deliveryDate', 'deliveryNoteNumber', 'totalAmount'] },
          sortDirection: { type: 'string', enum: ['asc', 'desc'] },
          page: { type: 'integer', minimum: 1, default: 1 },
          pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            data: {
              type: 'array',
              items: { $ref: 'DeliveryNote#' }
            },
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
    }
  }, async (request, reply) => {
    const {
      customerId,
      salesOfferId,
      status,
      deliveryDateFrom,
      deliveryDateTo,
      shipped,
      delivered,
      overdue,
      sortField = 'createdAt',
      sortDirection = 'desc',
      page = 1,
      pageSize = 20
    } = request.query as any;

    const filter: DeliveryNoteFilter = {
      customerId,
      salesOfferId,
      status,
      deliveryDateFrom: deliveryDateFrom ? new Date(deliveryDateFrom) : undefined,
      deliveryDateTo: deliveryDateTo ? new Date(deliveryDateTo) : undefined,
      shipped,
      delivered,
      overdue
    };

    const sort: DeliveryNoteSort = {
      field: sortField,
      direction: sortDirection
    };

    const result = await deliveryNoteService.listDeliveryNotes(filter, sort, page, pageSize);
    return result;
  });

  /**
   * POST /delivery-notes
   * Create a new delivery note
   */
  app.post('/delivery-notes', {
    schema: {
      description: 'Create a new delivery note',
      tags: ['delivery-notes'],
      body: {
        type: 'object',
        required: ['customerId', 'subject', 'description', 'deliveryDate', 'shippingAddress', 'items'],
        properties: {
          customerId: { type: 'string' },
          subject: { type: 'string' },
          description: { type: 'string' },
          deliveryDate: { type: 'string', format: 'date-time' },
          shippingAddress: {
            type: 'object',
            required: ['street', 'postalCode', 'city', 'country'],
            properties: {
              street: { type: 'string' },
              postalCode: { type: 'string' },
              city: { type: 'string' },
              country: { type: 'string' }
            }
          },
          items: {
            type: 'array',
            minItems: 1,
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
                notes: { type: 'string' }
              }
            }
          },
          salesOfferId: { type: 'string' },
          carrierId: { type: 'string' },
          trackingNumber: { type: 'string' },
          notes: { type: 'string' }
        }
      },
      response: {
        201: { $ref: 'DeliveryNote#' }
      }
    }
  }, async (request, reply) => {
    const {
      customerId,
      subject,
      description,
      deliveryDate,
      shippingAddress,
      items,
      salesOfferId,
      carrierId,
      trackingNumber,
      notes
    } = request.body as any;

    const createdBy = getAuthenticatedUserId(request);

    const deliveryNote = await deliveryNoteService.createDeliveryNote(
      customerId,
      subject,
      description,
      new Date(deliveryDate),
      shippingAddress,
      items,
      createdBy,
      {
        salesOfferId,
        carrierId,
        trackingNumber,
        notes
      }
    );

    return reply.code(201).send(deliveryNote);
  });

  /**
   * POST /delivery-notes/from-sales-offer/:salesOfferId
   * Create delivery note from sales offer
   */
  app.post('/delivery-notes/from-sales-offer/:salesOfferId', {
    schema: {
      description: 'Create delivery note from sales offer',
      tags: ['delivery-notes'],
      params: {
        type: 'object',
        required: ['salesOfferId'],
        properties: {
          salesOfferId: { type: 'string' }
        }
      },
      body: {
        type: 'object',
        required: ['deliveryDate', 'shippingAddress'],
        properties: {
          deliveryDate: { type: 'string', format: 'date-time' },
          shippingAddress: {
            type: 'object',
            required: ['street', 'postalCode', 'city', 'country'],
            properties: {
              street: { type: 'string' },
              postalCode: { type: 'string' },
              city: { type: 'string' },
              country: { type: 'string' }
            }
          },
          carrierId: { type: 'string' },
          trackingNumber: { type: 'string' },
          notes: { type: 'string' }
        }
      },
      response: {
        201: { $ref: 'DeliveryNote#' }
      }
    }
  }, async (request, reply) => {
    const { salesOfferId } = request.params as any;
    const {
      deliveryDate,
      shippingAddress,
      carrierId,
      trackingNumber,
      notes
    } = request.body as any;

    const createdBy = getAuthenticatedUserId(request);

    const deliveryNote = await deliveryNoteService.createFromSalesOffer(
      salesOfferId,
      new Date(deliveryDate),
      shippingAddress,
      createdBy,
      {
        carrierId,
        trackingNumber,
        notes
      }
    );

    return reply.code(201).send(deliveryNote);
  });

  /**
   * GET /delivery-notes/:id
   * Get delivery note by ID
   */
  app.get('/delivery-notes/:id', {
    schema: {
      description: 'Get delivery note by ID',
      tags: ['delivery-notes'],
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { type: 'string' }
        }
      },
      response: {
        200: { $ref: 'DeliveryNote#' },
        404: {
          type: 'object',
          properties: {
            error: { type: 'string' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { id } = request.params as any;

    const deliveryNote = await deliveryNoteService.getDeliveryNoteById(id);
    if (!deliveryNote) {
      return reply.code(404).send({ error: 'Delivery note not found' });
    }

    return deliveryNote;
  });

  /**
   * PATCH /delivery-notes/:id
   * Update delivery note
   */
  app.patch('/delivery-notes/:id', {
    schema: {
      description: 'Update delivery note',
      tags: ['delivery-notes'],
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { type: 'string' }
        }
      },
      body: {
        type: 'object',
        properties: {
          subject: { type: 'string' },
          description: { type: 'string' },
          deliveryDate: { type: 'string', format: 'date-time' },
          shippingAddress: {
            type: 'object',
            properties: {
              street: { type: 'string' },
              postalCode: { type: 'string' },
              city: { type: 'string' },
              country: { type: 'string' }
            }
          },
          carrierId: { type: 'string' },
          trackingNumber: { type: 'string' },
          notes: { type: 'string' }
        }
      },
      response: {
        200: { $ref: 'DeliveryNote#' }
      }
    }
  }, async (request, reply) => {
    const { id } = request.params as any;
    const updates = request.body as any;

    const updatedBy = getAuthenticatedUserId(request);

    // Convert date strings to Date objects
    if (updates.deliveryDate) {
      updates.deliveryDate = new Date(updates.deliveryDate);
    }

    const deliveryNote = await deliveryNoteService.updateDeliveryNote(id, updates, updatedBy);
    return deliveryNote;
  });

  /**
   * POST /delivery-notes/:id/ship
   * Ship delivery note
   */
  app.post('/delivery-notes/:id/ship', {
    schema: {
      description: 'Ship delivery note',
      tags: ['delivery-notes'],
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { type: 'string' }
        }
      },
      body: {
        type: 'object',
        properties: {
          carrierId: { type: 'string' },
          trackingNumber: { type: 'string' }
        }
      },
      response: {
        200: { $ref: 'DeliveryNote#' }
      }
    }
  }, async (request, reply) => {
    const { id } = request.params as any;
    const { carrierId, trackingNumber } = request.body as any;

    const shippedBy = getAuthenticatedUserId(request);

    const deliveryNote = await deliveryNoteService.shipDeliveryNote(id, shippedBy, carrierId, trackingNumber);
    return deliveryNote;
  });

  /**
   * POST /delivery-notes/:id/deliver
   * Mark delivery note as delivered
   */
  app.post('/delivery-notes/:id/deliver', {
    schema: {
      description: 'Mark delivery note as delivered',
      tags: ['delivery-notes'],
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { type: 'string' }
        }
      },
      response: {
        200: { $ref: 'DeliveryNote#' }
      }
    }
  }, async (request, reply) => {
    const { id } = request.params as any;

    const deliveredBy = getAuthenticatedUserId(request);

    const deliveryNote = await deliveryNoteService.deliverDeliveryNote(id, deliveredBy);
    return deliveryNote;
  });

  /**
   * POST /delivery-notes/:id/cancel
   * Cancel delivery note
   */
  app.post('/delivery-notes/:id/cancel', {
    schema: {
      description: 'Cancel delivery note',
      tags: ['delivery-notes'],
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { type: 'string' }
        }
      },
      response: {
        200: { $ref: 'DeliveryNote#' }
      }
    }
  }, async (request, reply) => {
    const { id } = request.params as any;

    const deliveryNote = await deliveryNoteService.cancelDeliveryNote(id);
    return deliveryNote;
  });

  /**
   * DELETE /delivery-notes/:id
   * Delete delivery note
   */
  app.delete('/delivery-notes/:id', {
    schema: {
      description: 'Delete delivery note (draft only)',
      tags: ['delivery-notes'],
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { type: 'string' }
        }
      },
      response: {
        204: { type: 'null' }
      }
    }
  }, async (request, reply) => {
    const { id } = request.params as any;

    const success = await deliveryNoteService.deleteDeliveryNote(id);
    if (!success) {
      return reply.code(404).send({ error: 'Delivery note not found' });
    }

    return reply.code(204).send();
  });

  /**
   * GET /delivery-notes/overdue
   * Get overdue delivery notes
   */
  app.get('/delivery-notes/overdue', {
    schema: {
      description: 'Get overdue delivery notes',
      tags: ['delivery-notes'],
      response: {
        200: {
          type: 'array',
          items: { $ref: 'DeliveryNote#' }
        }
      }
    }
  }, async (request, reply) => {
    const overdueNotes = await deliveryNoteService.getOverdueDeliveryNotes();
    return overdueNotes;
  });

  /**
   * GET /delivery-notes/statistics
   * Get delivery note statistics
   */
  app.get('/delivery-notes/statistics', {
    schema: {
      description: 'Get delivery note statistics',
      tags: ['delivery-notes'],
      response: {
        200: {
          type: 'object',
          properties: {
            total: { type: 'integer' },
            byStatus: {
              type: 'object',
              patternProperties: {
                '.*': { type: 'integer' }
              }
            },
            totalValue: { type: 'number' },
            averageValue: { type: 'number' },
            onTimeDeliveryRate: { type: 'number' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const statistics = await deliveryNoteService.getDeliveryNoteStatistics();
    return statistics;
  });
}