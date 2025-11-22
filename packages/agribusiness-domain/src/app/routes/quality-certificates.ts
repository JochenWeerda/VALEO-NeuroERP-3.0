import { FastifyInstance } from 'fastify';
import { QualityCertificateService } from '../../domain/services/quality-certificate-service';
import { QualityCertificateRepository } from '../../infra/repositories/quality-certificate-repository';
import { QualityCertificateFilter, QualityCertificateSort } from '../../infra/repositories/quality-certificate-repository';

// Initialize services
const qualityCertificateRepository = new QualityCertificateRepository();
const qualityCertificateService = new QualityCertificateService({ qualityCertificateRepository });

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

export async function registerQualityCertificateRoutes(fastify: FastifyInstance) {
  fastify.register(async (certificateRoutes) => {
    
    // GET /quality-certificates - List certificates with filtering and pagination
    certificateRoutes.get('/', {
      schema: {
        description: 'List quality certificates with pagination and filtering',
        tags: ['Quality Certificates'],
        querystring: {
          type: 'object',
          properties: {
            certificateNumber: { type: 'string' },
            certificateType: { type: 'string', enum: ['SEED', 'FERTILIZER', 'FEED', 'CROP'] },
            productId: { type: 'string' },
            batchId: { type: 'string' },
            status: { type: 'string', enum: ['DRAFT', 'ISSUED', 'VALID', 'EXPIRED', 'REVOKED'] },
            expired: { type: 'boolean' },
            expiringSoon: { type: 'boolean' },
            search: { type: 'string' },
            page: { type: 'integer', minimum: 1, default: 1 },
            pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
            sortField: { type: 'string', enum: ['createdAt', 'updatedAt', 'issuedAt', 'validUntil', 'certificateNumber', 'status'], default: 'createdAt' },
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
        const filter: QualityCertificateFilter = {};
        const sort: QualityCertificateSort = { 
          field: query.sortField || 'createdAt', 
          direction: query.sortDirection || 'desc' 
        };

        if (query.certificateNumber) filter.certificateNumber = query.certificateNumber;
        if (query.certificateType) filter.certificateType = query.certificateType as any;
        if (query.productId) filter.productId = query.productId;
        if (query.batchId) filter.batchId = query.batchId;
        if (query.status) filter.status = query.status as any;
        if (query.expired) filter.expired = query.expired;
        if (query.expiringSoon) filter.expiringSoon = query.expiringSoon;
        if (query.search) filter.search = query.search;

        const page = parseInt(query.page) || 1;
        const pageSize = Math.min(parseInt(query.pageSize) || 20, 100);

        const result = await qualityCertificateService.listQualityCertificates(filter, sort, page, pageSize);

        return {
          data: result.items.map(cert => cert.toJSON()),
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

    // POST /quality-certificates - Create new certificate
    certificateRoutes.post('/', {
      schema: {
        description: 'Create a new quality certificate',
        tags: ['Quality Certificates'],
        body: {
          type: 'object',
          required: ['certificateNumber', 'certificateType', 'productId', 'issuedBy', 'issuedAt', 'validUntil', 'testResults'],
          properties: {
            certificateNumber: { type: 'string' },
            certificateType: { type: 'string', enum: ['SEED', 'FERTILIZER', 'FEED', 'CROP'] },
            productId: { type: 'string' },
            batchId: { type: 'string' },
            issuedBy: { type: 'string' },
            issuedAt: { type: 'string', format: 'date-time' },
            validUntil: { type: 'string', format: 'date' },
            testResults: {
              type: 'array',
              items: {
                type: 'object',
                required: ['testName', 'testValue', 'passed', 'testedBy'],
                properties: {
                  testName: { type: 'string' },
                  testMethod: { type: 'string' },
                  testValue: { oneOf: [{ type: 'number' }, { type: 'string' }] },
                  unit: { type: 'string' },
                  minValue: { type: 'number' },
                  maxValue: { type: 'number' },
                  passed: { type: 'boolean' },
                  notes: { type: 'string' },
                  testedAt: { type: 'string', format: 'date-time' },
                  testedBy: { type: 'string' }
                }
              }
            },
            notes: { type: 'string' },
            customFields: { type: 'object' }
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

        const certificate = await qualityCertificateService.createQualityCertificate(
          {
            certificateNumber: body.certificateNumber,
            certificateType: body.certificateType,
            productId: body.productId,
            batchId: body.batchId,
            issuedBy: body.issuedBy || createdBy,
            issuedAt: new Date(body.issuedAt),
            validUntil: new Date(body.validUntil),
            testResults: body.testResults.map((tr: any) => ({
              ...tr,
              testedAt: tr.testedAt ? new Date(tr.testedAt) : new Date()
            })),
            notes: body.notes,
            customFields: body.customFields
          },
          createdBy
        );

        return reply.code(201).send({
          id: certificate.id,
          certificateNumber: certificate.certificateNumber,
          status: certificate.status,
          createdAt: certificate.createdAt.toISOString()
        });
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /quality-certificates/:id - Get certificate by ID
    certificateRoutes.get('/:id', {
      schema: {
        description: 'Get quality certificate by ID',
        tags: ['Quality Certificates'],
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
        const certificate = await qualityCertificateService.getQualityCertificateById(id);

        if (!certificate) {
          return reply.code(404).send({ error: 'Quality certificate not found' });
        }

        return certificate.toJSON();
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // POST /quality-certificates/:id/issue - Issue certificate
    certificateRoutes.post('/:id/issue', {
      schema: {
        description: 'Issue quality certificate',
        tags: ['Quality Certificates'],
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
        
        const certificate = await qualityCertificateService.issueCertificate(id, issuedBy);
        return certificate.toJSON();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // POST /quality-certificates/:id/revoke - Revoke certificate
    certificateRoutes.post('/:id/revoke', {
      schema: {
        description: 'Revoke quality certificate',
        tags: ['Quality Certificates'],
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
        const revokedBy = getAuthenticatedUserId(request);
        
        const certificate = await qualityCertificateService.revokeCertificate(id, revokedBy, body.reason);
        return certificate.toJSON();
      } catch (error) {
        return reply.code(400).send({ error: (error as Error).message });
      }
    });

    // GET /quality-certificates/statistics - Get certificate statistics
    certificateRoutes.get('/statistics', {
      schema: {
        description: 'Get quality certificate statistics',
        tags: ['Quality Certificates'],
        response: {
          200: { type: 'object' },
        },
      },
    }, async (request, reply) => {
      try {
        const statistics = await qualityCertificateService.getQualityCertificateStatistics();
        return statistics;
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /quality-certificates/expired - Get expired certificates
    certificateRoutes.get('/expired', {
      schema: {
        description: 'Get expired quality certificates',
        tags: ['Quality Certificates'],
        response: {
          200: { type: 'array' },
        },
      },
    }, async (request, reply) => {
      try {
        const certificates = await qualityCertificateService.getExpiredCertificates();
        return certificates.map(cert => cert.toJSON());
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

    // GET /quality-certificates/expiring-soon - Get certificates expiring soon
    certificateRoutes.get('/expiring-soon', {
      schema: {
        description: 'Get quality certificates expiring soon',
        tags: ['Quality Certificates'],
        querystring: {
          type: 'object',
          properties: {
            days: { type: 'integer', minimum: 1, default: 30 }
          }
        },
        response: {
          200: { type: 'array' },
        },
      },
    }, async (request, reply) => {
      try {
        const query = request.query as any;
        const days = parseInt(query.days) || 30;
        const certificates = await qualityCertificateService.getExpiringSoonCertificates(days);
        return certificates.map(cert => cert.toJSON());
      } catch (error) {
        return reply.code(500).send({ error: (error as Error).message });
      }
    });

  }, { prefix: '/quality-certificates' });
}
