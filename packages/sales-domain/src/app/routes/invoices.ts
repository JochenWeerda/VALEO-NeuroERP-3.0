import { FastifyInstance } from 'fastify';
import { SalesInvoiceService } from '../../domain/services/sales-invoice-service';
import { SalesInvoiceRepository } from '../../infra/repositories/sales-invoice-repository';
import { DeliveryNoteService } from '../../domain/services/delivery-note-service';
import { DeliveryNoteRepository } from '../../infra/repositories/delivery-note-repository';
import { SalesOrderService } from '../../domain/services/sales-order-service';
import { SalesOrderRepository } from '../../infra/repositories/sales-order-repository';
import { SalesOfferService } from '../../domain/services/sales-offer-service';
import { SalesOfferRepository } from '../../infra/repositories/sales-offer-repository';
import { SalesInvoiceFilter, SalesInvoiceSort } from '../../infra/repositories/sales-invoice-repository';

// Initialize services
const salesInvoiceRepository = new SalesInvoiceRepository();
const deliveryNoteRepository = new DeliveryNoteRepository();
const salesOrderRepository = new SalesOrderRepository();
const salesOfferRepository = new SalesOfferRepository();

const salesOfferService = new SalesOfferService({ salesOfferRepository });
const salesOrderService = new SalesOrderService({ salesOrderRepository, salesOfferService });
const deliveryNoteService = new DeliveryNoteService({ deliveryNoteRepository, salesOrderService });
const salesInvoiceService = new SalesInvoiceService({ 
  salesInvoiceRepository, 
  deliveryNoteService, 
  salesOrderService 
});

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

export async function registerInvoiceRoutes(fastify: FastifyInstance) {
  fastify.register(async (invoiceRoutes) => {
    
    // GET /invoices - List invoices with filtering and pagination
    invoiceRoutes.get('/', {
      schema: {
        description: 'List sales invoices with pagination and filtering',
        tags: ['Sales Invoices'],
        querystring: {
          type: 'object',
          properties: {
            customerId: { type: 'string' },
            sourceOrderId: { type: 'string' },
            sourceDeliveryNoteId: { type: 'string' },
            status: { type: 'string', enum: ['DRAFT', 'ISSUED', 'SENT', 'PAID', 'PARTIAL_PAID', 'OVERDUE', 'CANCELLED'] },
            invoiceDateFrom: { type: 'string', format: 'date' },
            invoiceDateTo: { type: 'string', format: 'date' },
            dueDateFrom: { type: 'string', format: 'date' },
            dueDateTo: { type: 'string', format: 'date' },
            totalAmountMin: { type: 'number' },
            totalAmountMax: { type: 'number' },
            overdue: { type: 'boolean' },
            search: { type: 'string' },
            page: { type: 'integer', minimum: 1, default: 1 },
            pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
            sortField: { type: 'string', enum: ['createdAt', 'updatedAt', 'invoiceDate', 'dueDate', 'totalAmount', 'invoiceNumber', 'status', 'remainingAmount'], default: 'createdAt' },
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
        const filter: SalesInvoiceFilter = {};
        const sort: SalesInvoiceSort = { 
          field: query.sortField || 'createdAt', 
          direction: query.sortDirection || 'desc' 
        };

        if (query.customerId) filter.customerId = query.customerId;
        if (query.sourceOrderId) filter.sourceOrderId = query.sourceOrderId;
        if (query.sourceDeliveryNoteId) filter.sourceDeliveryNoteId = query.sourceDeliveryNoteId;
        if (query.status) filter.status = query.status as any;
        if (query.invoiceDateFrom) filter.invoiceDateFrom = new Date(query.invoiceDateFrom);
        if (query.invoiceDateTo) filter.invoiceDateTo = new Date(query.invoiceDateTo);
        if (query.dueDateFrom) filter.dueDateFrom = new Date(query.dueDateFrom);
        if (query.dueDateTo) filter.dueDateTo = new Date(query.dueDateTo);
        if (query.totalAmountMin !== undefined) filter.totalAmountMin = parseFloat(query.totalAmountMin);
        if (query.totalAmountMax !== undefined) filter.totalAmountMax = parseFloat(query.totalAmountMax);
        if (query.overdue) filter.overdue = query.overdue;
        if (query.search) filter.search = query.search;

        const page = parseInt(query.page) || 1;
        const pageSize = Math.min(parseInt(query.pageSize) || 20, 100);

        const result = await salesInvoiceService.listSalesInvoices(filter, sort, page, pageSize);

        return {
          data: result.items.map(invoice => ({
            id: invoice.id,
            invoiceNumber: invoice.invoiceNumber,
            customerId: invoice.customerId,
            sourceOrderId: invoice.sourceOrderId,
            sourceDeliveryNoteId: invoice.sourceDeliveryNoteId,
            subject: invoice.subject,
            status: invoice.status,
            invoiceDate: invoice.invoiceDate.toISOString(),
            dueDate: invoice.dueDate.toISOString(),
            totalAmount: invoice.totalAmount,
            paidAmount: invoice.paidAmount,
            remainingAmount: invoice.remainingAmount,
            paymentProgress: invoice.getPaymentProgress(),
            daysOverdue: invoice.getDaysOverdue(),
            currency: invoice.currency,
            createdAt: invoice.createdAt.toISOString(),
            updatedAt: invoice.updatedAt.toISOString(),
            createdBy: invoice.createdBy
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

    // POST /invoices - Create new invoice
    invoiceRoutes.post('/', {
      schema: {
        description: 'Create a new sales invoice',
        tags: ['Sales Invoices'],
        body: {
          type: 'object',
          required: ['customerId', 'subject', 'description', 'invoiceDate', 'dueDate', 'billingAddress', 'items'],
          properties: {
            customerId: { type: 'string' },
            sourceOrderId: { type: 'string' },
            sourceDeliveryNoteId: { type: 'string' },
            subject: { type: 'string' },
            description: { type: 'string' },
            invoiceDate: { type: 'string', format: 'date' },
            dueDate: { type: 'string', format: 'date' },
            paymentTerms: { type: 'string', default: '30 days net' },
            currency: { type: 'string', default: 'EUR' },
            taxRate: { type: 'number', default: 19.0 },
            billingAddress: {
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
            notes: { type: 'string' },
            items: {
              type: 'array',
              items: {
                type: 'object',
                required: ['itemType', 'description', 'deliveredQuantity', 'invoicedQuantity', 'unitPrice'],
                properties: {
                  sourceOrderItemId: { type: 'string' },
                  sourceDeliveryItemId: { type: 'string' },
                  itemType: { type: 'string', enum: ['PRODUCT', 'SERVICE'] },
                  articleId: { type: 'string' },
                  description: { type: 'string' },
                  deliveredQuantity: { type: 'number', minimum: 0 },
                  invoicedQuantity: { type: 'number', minimum: 0 },
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
          const invoicedQuantity = item.invoicedQuantity;
          const unitPrice = item.unitPrice;
          const discountPercent = item.discountPercent || 0;
          const taxRate = item.taxRate || body.taxRate || 19.0;
          
          const netAmount = invoicedQuantity * unitPrice * (1 - discountPercent / 100);
          const taxAmount = netAmount * (taxRate / 100);
          const totalAmount = netAmount + taxAmount;

          return {
            ...item,
            netAmount,
            taxAmount,
            totalAmount
          };
        });

        const invoice = await salesInvoiceService.createSalesInvoice(
          {
            customerId: body.customerId,
            sourceOrderId: body.sourceOrderId,
            sourceDeliveryNoteId: body.sourceDeliveryNoteId,
            subject: body.subject,
            description: body.description,
            invoiceDate: new Date(body.invoiceDate),
            dueDate: new Date(body.dueDate),
            paymentTerms: body.paymentTerms || '30 days net',
            currency: body.currency || 'EUR',
            taxRate: body.taxRate || 19.0,
            billingAddress: body.billingAddress,
            notes: body.notes,
            items
          },
          createdBy
        );

        return reply.code(201).send({
          id: invoice.id,
          invoiceNumber: invoice.invoiceNumber,
          status: invoice.status,
          totalAmount: invoice.totalAmount,
          createdAt: invoice.createdAt.toISOString()
        });
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /invoices/:id - Get invoice by ID
    invoiceRoutes.get('/:id', {
      schema: {
        description: 'Get sales invoice by ID',
        tags: ['Sales Invoices'],
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
        const invoice = await salesInvoiceService.getSalesInvoiceById(id);

        if (!invoice) {
          return reply.code(404).send({ error: 'Sales invoice not found' });
        }

        return invoice.toJSON();
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // PATCH /invoices/:id - Update invoice
    invoiceRoutes.patch('/:id', {
      schema: {
        description: 'Update sales invoice (draft only)',
        tags: ['Sales Invoices'],
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
            invoiceDate: { type: 'string', format: 'date' },
            dueDate: { type: 'string', format: 'date' },
            paymentTerms: { type: 'string' },
            currency: { type: 'string' },
            taxRate: { type: 'number' },
            billingAddress: {
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
        if (body.invoiceDate !== undefined) updates.invoiceDate = new Date(body.invoiceDate);
        if (body.dueDate !== undefined) updates.dueDate = new Date(body.dueDate);
        if (body.paymentTerms !== undefined) updates.paymentTerms = body.paymentTerms;
        if (body.currency !== undefined) updates.currency = body.currency;
        if (body.taxRate !== undefined) updates.taxRate = body.taxRate;
        if (body.billingAddress !== undefined) updates.billingAddress = body.billingAddress;
        if (body.notes !== undefined) updates.notes = body.notes;

        const invoice = await salesInvoiceService.updateSalesInvoice(id, updates, updatedBy);

        return {
          id: invoice.id,
          invoiceNumber: invoice.invoiceNumber,
          status: invoice.status,
          totalAmount: invoice.totalAmount,
          updatedAt: invoice.updatedAt.toISOString(),
          version: invoice.version
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // DELETE /invoices/:id - Delete invoice
    invoiceRoutes.delete('/:id', {
      schema: {
        description: 'Delete sales invoice (draft only)',
        tags: ['Sales Invoices'],
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
        const success = await salesInvoiceService.deleteSalesInvoice(id);

        if (!success) {
          return reply.code(404).send({ error: 'Sales invoice not found' });
        }

        return reply.code(204).send();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /invoices/:id/issue - Issue invoice
    invoiceRoutes.post('/:id/issue', {
      schema: {
        description: 'Issue sales invoice',
        tags: ['Sales Invoices'],
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
        const issuedBy = getAuthenticatedUserId(request);
        
        const invoice = await salesInvoiceService.issueInvoice(id, issuedBy);

        return {
          id: invoice.id,
          invoiceNumber: invoice.invoiceNumber,
          status: invoice.status,
          issuedAt: invoice.issuedAt?.toISOString(),
          issuedBy: invoice.issuedBy
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /invoices/:id/send - Send invoice
    invoiceRoutes.post('/:id/send', {
      schema: {
        description: 'Send sales invoice to customer',
        tags: ['Sales Invoices'],
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
        
        const invoice = await salesInvoiceService.sendInvoice(id, sentBy);

        return {
          id: invoice.id,
          invoiceNumber: invoice.invoiceNumber,
          status: invoice.status,
          sentAt: invoice.sentAt?.toISOString(),
          sentBy: invoice.sentBy
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /invoices/:id/pay - Record payment for invoice
    invoiceRoutes.post('/:id/pay', {
      schema: {
        description: 'Record payment for sales invoice',
        tags: ['Sales Invoices'],
        params: {
          type: 'object',
          required: ['id'],
          properties: {
            id: { type: 'string' },
          },
        },
        body: {
          type: 'object',
          required: ['amount'],
          properties: {
            amount: { type: 'number', minimum: 0.01 }
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
        const paidBy = getAuthenticatedUserId(request);
        
        const invoice = await salesInvoiceService.recordPayment(id, body.amount, paidBy);

        return {
          id: invoice.id,
          invoiceNumber: invoice.invoiceNumber,
          status: invoice.status,
          paidAmount: invoice.paidAmount,
          remainingAmount: invoice.remainingAmount,
          paymentProgress: invoice.getPaymentProgress(),
          paidAt: invoice.paidAt?.toISOString()
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /invoices/:id/cancel - Cancel invoice
    invoiceRoutes.post('/:id/cancel', {
      schema: {
        description: 'Cancel sales invoice',
        tags: ['Sales Invoices'],
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
        
        const invoice = await salesInvoiceService.cancelInvoice(id, cancelledBy, body.reason);

        return {
          id: invoice.id,
          invoiceNumber: invoice.invoiceNumber,
          status: invoice.status,
          cancelledAt: invoice.cancelledAt?.toISOString(),
          cancelledBy: invoice.cancelledBy,
          cancellationReason: invoice.cancellationReason
        };
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /invoices/statistics - Get invoice statistics
    invoiceRoutes.get('/statistics', {
      schema: {
        description: 'Get sales invoice statistics',
        tags: ['Sales Invoices'],
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const statistics = await salesInvoiceService.getSalesInvoiceStatistics();
        return statistics;
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /invoices/overdue - Get overdue invoices
    invoiceRoutes.get('/overdue', {
      schema: {
        description: 'Get overdue sales invoices',
        tags: ['Sales Invoices'],
        response: {
          200: { type: 'array' },
        },
      },
    }, async (request, reply) => {
      try {
        const invoices = await salesInvoiceService.getOverdueInvoices();
        return invoices.map(inv => inv.toJSON());
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /invoices/unpaid - Get unpaid invoices
    invoiceRoutes.get('/unpaid', {
      schema: {
        description: 'Get unpaid sales invoices',
        tags: ['Sales Invoices'],
        response: {
          200: { type: 'array' },
        },
      },
    }, async (request, reply) => {
      try {
        const invoices = await salesInvoiceService.getUnpaidInvoices();
        return invoices.map(inv => inv.toJSON());
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

  }, { prefix: '/invoices' });
}

// CRITICAL: Delivery to Invoice Conversion Route - Add to Delivery Routes
export async function addDeliveryToInvoiceRoutes(fastify: FastifyInstance) {
  fastify.register(async (deliveryRoutes) => {
    
    // POST /delivery-notes/:id/create-invoice - Convert delivery note to invoice
    deliveryRoutes.post('/:id/create-invoice', {
      schema: {
        description: 'Create invoice from delivery note',
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
            invoiceDate: { type: 'string', format: 'date' },
            dueDate: { type: 'string', format: 'date' },
            paymentTerms: { type: 'string' },
            currency: { type: 'string' },
            taxRate: { type: 'number' },
            billingAddress: {
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
            notes: { type: 'string' },
            partialInvoicing: {
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
              invoiceId: { type: 'string' },
              invoiceNumber: { type: 'string' },
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
        if (body.invoiceDate) options.invoiceDate = new Date(body.invoiceDate);
        if (body.dueDate) options.dueDate = new Date(body.dueDate);
        if (body.paymentTerms) options.paymentTerms = body.paymentTerms;
        if (body.currency) options.currency = body.currency;
        if (body.taxRate) options.taxRate = body.taxRate;
        if (body.billingAddress) options.billingAddress = body.billingAddress;
        if (body.notes) options.notes = body.notes;
        if (body.partialInvoicing) options.partialInvoicing = body.partialInvoicing;

        const invoice = await salesInvoiceService.convertDeliveryToInvoice(
          id, 
          convertedBy,
          options
        );

        return reply.code(201).send({
          invoiceId: invoice.id,
          invoiceNumber: invoice.invoiceNumber,
          status: invoice.status,
          totalAmount: invoice.totalAmount,
          message: `Delivery note ${id} successfully converted to invoice ${invoice.invoiceNumber}`
        });
      } catch (error) {
        const errorMessage = (error as Error).message;
        
        if (errorMessage.includes('not found')) {
          return reply.code(404).send({ error: errorMessage });
        } else if (errorMessage.includes('delivered') || errorMessage.includes('confirmed') || errorMessage.includes('active invoices') || errorMessage.includes('Cannot prepare')) {
          return reply.code(400).send({ error: errorMessage });
        } else {
          return reply.code(500).send({ error: errorMessage });
        }
      }
    });

    // GET /delivery-notes/:id/invoices - Get invoices created from this delivery note
    deliveryRoutes.get('/:id/invoices', {
      schema: {
        description: 'Get invoices created from this delivery note',
        tags: ['Delivery Notes'],
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

        const invoices = await salesInvoiceService.getSalesInvoicesByDeliveryNote(id);

        return invoices.map(invoice => ({
          id: invoice.id,
          invoiceNumber: invoice.invoiceNumber,
          status: invoice.status,
          invoiceDate: invoice.invoiceDate.toISOString(),
          dueDate: invoice.dueDate.toISOString(),
          totalAmount: invoice.totalAmount,
          paidAmount: invoice.paidAmount,
          remainingAmount: invoice.remainingAmount,
          createdAt: invoice.createdAt.toISOString()
        }));
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

  }, { prefix: '/delivery-notes' });
}