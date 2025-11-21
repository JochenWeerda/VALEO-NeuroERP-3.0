import { FastifyInstance } from 'fastify';
import { SalesOfferService } from '../../domain/services/sales-offer-service';
import { SalesOfferRepository } from '../../infra/repositories/sales-offer-repository';
import { SalesOfferFilter, SalesOfferSort } from '../../infra/repositories/sales-offer-repository';

// Initialize services
const repository = new SalesOfferRepository();
const salesOfferService = new SalesOfferService(repository);

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  // TODO: Implement proper authentication context extraction
  // For now, return system user or extract from JWT token
  return request.user?.id || 'system';
}

export async function registerSalesOfferRoutes(fastify: FastifyInstance) {
  // Base path for sales offers
  fastify.register(async (salesOfferRoutes) => {
    // GET /sales-offers - List sales offers
    salesOfferRoutes.get('/', {
      schema: {
        description: 'List sales offers with pagination and filtering',
        tags: ['Sales Offers'],
        querystring: {
          type: 'object',
          properties: {
            customerId: { type: 'string' },
            status: { type: 'string', enum: ['ENTWURF', 'VERSENDET', 'ANGENOMMEN', 'ABGELEHNT', 'ABGELAUFEN'] },
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
        const filter: SalesOfferFilter = {};
        const sort: SalesOfferSort = { field: 'createdAt', direction: 'desc' };

        if (query.customerId) filter.customerId = query.customerId;
        if (query.status) filter.status = query.status as any;

        const page = parseInt(query.page) || 1;
        const pageSize = Math.min(parseInt(query.pageSize) || 20, 100);

        const result = await salesOfferService.listSalesOffers(filter, sort, page, pageSize);

        return {
          data: result.items.map(offer => ({
            id: offer.id,
            offerNumber: offer.offerNumber,
            customerId: offer.customerId,
            subject: offer.subject,
            status: offer.status,
            validUntil: offer.validUntil.toISOString(),
            totalAmount: offer.totalAmount,
            currency: offer.currency,
            createdAt: offer.createdAt.toISOString(),
            updatedAt: offer.updatedAt.toISOString()
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

    // POST /sales-offers - Create sales offer
    salesOfferRoutes.post('/', {
      schema: {
        description: 'Create a new sales offer',
        tags: ['Sales Offers'],
        body: {
          type: 'object',
          required: ['customerId', 'subject', 'description', 'totalAmount', 'validUntil'],
          properties: {
            customerInquiryId: { type: 'string' },
            customerId: { type: 'string' },
            offerNumber: { type: 'string' },
            subject: { type: 'string' },
            description: { type: 'string' },
            totalAmount: { type: 'number', minimum: 0 },
            currency: { type: 'string', default: 'EUR' },
            validUntil: { type: 'string', format: 'date' },
            contactPerson: { type: 'string' },
            deliveryDate: { type: 'string', format: 'date' },
            paymentTerms: { type: 'string' },
            notes: { type: 'string' },
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
        const offer = await salesOfferService.createSalesOffer(
          body.customerId,
          body.subject,
          body.description,
          new Date(body.validUntil),
          body.items || [],
          createdBy,
          {
            ...(body.customerInquiryId && { customerInquiryId: body.customerInquiryId }),
            ...(body.contactPerson && { contactPerson: body.contactPerson }),
            ...(body.deliveryDate && { deliveryDate: new Date(body.deliveryDate) }),
            ...(body.paymentTerms && { paymentTerms: body.paymentTerms }),
            ...(body.currency && { currency: body.currency }),
            ...(body.taxRate && { taxRate: body.taxRate }),
            ...(body.notes && { notes: body.notes })
          }
        );

        return reply.code(201).send({
          id: offer.id,
          offerNumber: offer.offerNumber,
          status: offer.status,
          createdAt: offer.createdAt.toISOString()
        });
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /sales-offers/from-inquiry/:inquiryId - Create from CustomerInquiry
    salesOfferRoutes.post('/from-inquiry/:inquiryId', {
      schema: {
        description: 'Create a sales offer from a CustomerInquiry',
        tags: ['Sales Offers'],
        params: {
          type: 'object',
          required: ['inquiryId'],
          properties: {
            inquiryId: { type: 'string' },
          },
        },
        body: {
          type: 'object',
          required: ['offerNumber', 'totalAmount', 'validUntil'],
          properties: {
            offerNumber: { type: 'string' },
            totalAmount: { type: 'number', minimum: 0 },
            validUntil: { type: 'string', format: 'date' },
            deliveryDate: { type: 'string', format: 'date' },
            paymentTerms: { type: 'string' },
            notes: { type: 'string' },
          },
        },
        response: {
          201: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const { inquiryId } = request.params as { inquiryId: string };
        const body = request.body as any;
        const createdBy = getAuthenticatedUserId(request);

        const offer = await salesOfferService.createOfferFromInquiry(
          inquiryId,
          {
            offerNumber: body.offerNumber,
            totalAmount: body.totalAmount,
            validUntil: new Date(body.validUntil),
            ...(body.deliveryDate && { deliveryDate: new Date(body.deliveryDate) }),
            ...(body.paymentTerms && { paymentTerms: body.paymentTerms }),
            ...(body.notes && { notes: body.notes })
          },
          createdBy
        );

        return reply.code(201).send({
          id: offer.id,
          offerNumber: offer.offerNumber,
          customerInquiryId: offer.customerInquiryId,
          status: offer.status,
          createdAt: offer.createdAt.toISOString()
        });
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /sales-offers/:id - Get sales offer by ID
    salesOfferRoutes.get('/:id', {
      schema: {
        description: 'Get sales offer by ID',
        tags: ['Sales Offers'],
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
        const offer = await salesOfferService.getSalesOfferById(id);

        if (!offer) {
          return reply.code(404).send({ error: 'Sales offer not found' });
        }

        return offer.toJSON();
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // PATCH /sales-offers/:id - Update sales offer
    salesOfferRoutes.patch('/:id', {
      schema: {
        description: 'Update sales offer',
        tags: ['Sales Offers'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        body: { type: 'object' },
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
        if (body.validUntil !== undefined) updates.validUntil = new Date(body.validUntil);
        if (body.contactPerson !== undefined) updates.contactPerson = body.contactPerson;
        if (body.deliveryDate !== undefined) updates.deliveryDate = body.deliveryDate ? new Date(body.deliveryDate) : undefined;
        if (body.paymentTerms !== undefined) updates.paymentTerms = body.paymentTerms;
        if (body.currency !== undefined) updates.currency = body.currency;
        if (body.taxRate !== undefined) updates.taxRate = body.taxRate;
        if (body.notes !== undefined) updates.notes = body.notes;

        const updatedBy = getAuthenticatedUserId(request);
        const offer = await salesOfferService.updateSalesOffer(id, updates, updatedBy);

        return {
          id: offer.id,
          offerNumber: offer.offerNumber,
          status: offer.status,
          updatedAt: offer.updatedAt.toISOString(),
          version: offer.version
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // DELETE /sales-offers/:id - Delete sales offer
    salesOfferRoutes.delete('/:id', {
      schema: {
        description: 'Delete sales offer',
        tags: ['Sales Offers'],
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
        const success = await salesOfferService.deleteSalesOffer(id);

        if (!success) {
          return reply.code(404).send({ error: 'Sales offer not found' });
        }

        return reply.code(204).send();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /sales-offers/:id/send - Send sales offer
    salesOfferRoutes.post('/:id/send', {
      schema: {
        description: 'Send sales offer to customer',
        tags: ['Sales Offers'],
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
        const sentBy = getAuthenticatedUserId(request);
        const offer = await salesOfferService.sendSalesOffer(id, sentBy);

        return {
          id: offer.id,
          offerNumber: offer.offerNumber,
          status: offer.status,
          sentAt: offer.sentAt?.toISOString(),
          validUntil: offer.validUntil.toISOString()
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /sales-offers/:id/accept - Accept sales offer
    salesOfferRoutes.post('/:id/accept', {
      schema: {
        description: 'Accept sales offer',
        tags: ['Sales Offers'],
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
        const acceptedBy = getAuthenticatedUserId(request);
        const offer = await salesOfferService.acceptSalesOffer(id, acceptedBy);

        return {
          id: offer.id,
          offerNumber: offer.offerNumber,
          status: offer.status,
          acceptedAt: offer.acceptedAt?.toISOString(),
          acceptedBy: offer.acceptedBy
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /sales-offers/:id/reject - Reject sales offer
    salesOfferRoutes.post('/:id/reject', {
      schema: {
        description: 'Reject sales offer',
        tags: ['Sales Offers'],
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
        const body = request.body as any;
        const reason = body.reason || 'No reason provided';

        const rejectedBy = getAuthenticatedUserId(request);
        const offer = await salesOfferService.rejectSalesOffer(id, rejectedBy, reason);

        return {
          id: offer.id,
          offerNumber: offer.offerNumber,
          status: offer.status,
          rejectedAt: offer.rejectedAt?.toISOString(),
          rejectedBy: offer.rejectedBy,
          rejectionReason: offer.rejectionReason
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /sales-offers/inquiry/:inquiryId - Get sales offers by CustomerInquiry
    salesOfferRoutes.get('/inquiry/:inquiryId', {
      schema: {
        description: 'Get sales offers by CustomerInquiry ID',
        tags: ['Sales Offers'],
        params: {
          type: 'object',
          required: ['inquiryId'],
          properties: {
            inquiryId: { type: 'string' },
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
        const { inquiryId } = request.params as { inquiryId: string };
        const offers = await salesOfferService.getSalesOffersByInquiry(inquiryId);

        return offers.map(offer => ({
          id: offer.id,
          offerNumber: offer.offerNumber,
          customerId: offer.customerId,
          subject: offer.subject,
          status: offer.status,
          totalAmount: offer.totalAmount,
          validUntil: offer.validUntil.toISOString(),
          createdAt: offer.createdAt.toISOString()
        }));
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /sales-offers/expired - Get expired sales offers
    salesOfferRoutes.get('/expired', {
      schema: {
        description: 'Get expired sales offers',
        tags: ['Sales Offers'],
        response: {
          200: {
            type: 'array',
          },
        },
      },
    }, async (request, reply) => {
      try {
        const offers = await salesOfferService.getExpiredSalesOffers();

        return offers.map(offer => ({
          id: offer.id,
          offerNumber: offer.offerNumber,
          customerId: offer.customerId,
          subject: offer.subject,
          status: offer.status,
          totalAmount: offer.totalAmount,
          validUntil: offer.validUntil.toISOString(),
          expiredAt: offer.validUntil.toISOString(),
          createdAt: offer.createdAt.toISOString()
        }));
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /sales-offers/valid - Get valid sales offers
    salesOfferRoutes.get('/valid', {
      schema: {
        description: 'Get valid (active) sales offers',
        tags: ['Sales Offers'],
        response: {
          200: {
            type: 'array',
          },
        },
      },
    }, async (request, reply) => {
      try {
        const offers = await salesOfferService.getValidSalesOffers();

        return offers.map(offer => ({
          id: offer.id,
          offerNumber: offer.offerNumber,
          customerId: offer.customerId,
          subject: offer.subject,
          status: offer.status,
          totalAmount: offer.totalAmount,
          validUntil: offer.validUntil.toISOString(),
          daysUntilExpiry: Math.ceil((offer.validUntil.getTime() - Date.now()) / (1000 * 60 * 60 * 24)),
          createdAt: offer.createdAt.toISOString()
        }));
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /sales-offers/statistics - Get sales offer statistics
    salesOfferRoutes.get('/statistics', {
      schema: {
        description: 'Get sales offer statistics',
        tags: ['Sales Offers'],
        response: {
          200: {
            type: 'object',
            properties: {
              total: { type: 'integer' },
              byStatus: { type: 'object' },
              totalValue: { type: 'number' },
              averageValue: { type: 'number' },
              conversionRate: { type: 'number' }
            },
          },
        },
      },
    }, async (request, reply) => {
      try {
        const statistics = await salesOfferService.getSalesOfferStatistics();
        return statistics;
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });
  }, { prefix: '/sales-offers' });
}