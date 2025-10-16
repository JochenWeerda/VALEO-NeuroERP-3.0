import { FastifyInstance } from 'fastify';

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
      // TODO: Implement sales offer listing
      return {
        data: [],
        pagination: {
          page: 1,
          pageSize: 20,
          total: 0,
          totalPages: 0,
        },
      };
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
      // TODO: Implement sales offer creation
      return reply.code(201).send({ id: 'sales-offer-123' });
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
      // TODO: Implement sales offer creation from inquiry
      const { inquiryId } = request.params as { inquiryId: string };
      return reply.code(201).send({ id: 'sales-offer-from-inquiry-123', customerInquiryId: inquiryId });
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
      // TODO: Implement sales offer retrieval
      const { id } = request.params as { id: string };
      return { id, status: 'ENTWURF' };
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
      // TODO: Implement sales offer update
      const { id } = request.params as { id: string };
      return { id, updated: true };
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
      // TODO: Implement sales offer deletion
      return reply.code(204).send();
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
      // TODO: Implement sales offer sending
      const { id } = request.params as { id: string };
      return { id, status: 'VERSENDET' };
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
      // TODO: Implement sales offer acceptance
      const { id } = request.params as { id: string };
      return { id, status: 'ANGENOMMEN' };
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
      // TODO: Implement sales offer rejection
      const { id } = request.params as { id: string };
      return { id, status: 'ABGELEHNT' };
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
      // TODO: Implement sales offers by inquiry retrieval
      const { inquiryId } = request.params as { inquiryId: string };
      return [];
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
      // TODO: Implement expired sales offers retrieval
      return [];
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
      // TODO: Implement valid sales offers retrieval
      return [];
    });
  }, { prefix: '/sales-offers' });
}