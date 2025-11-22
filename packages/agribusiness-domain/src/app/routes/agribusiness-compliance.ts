/**
 * Agribusiness Compliance REST API Routes
 * Compliance & Audit Management
 */

import { FastifyInstance } from 'fastify';
import { AgribusinessComplianceService } from '../../domain/services/agribusiness-compliance-service';

// Initialize services
const complianceService = new AgribusinessComplianceService({});

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  return request.user?.id || 'system';
}

function getAuthenticatedUserName(request: any): string {
  return request.user?.name || request.user?.email || 'System';
}

export async function registerAgribusinessComplianceRoutes(fastify: FastifyInstance) {
  fastify.register(async (complianceRoutes) => {

    // GET /compliance/audits - List audits
    complianceRoutes.get('/audits', {
      schema: {
        description: 'List compliance audits',
        tags: ['Compliance'],
        querystring: {
          type: 'object',
          properties: {
            entityType: { type: 'string', enum: ['FARMER', 'BATCH', 'CONTRACT', 'WAREHOUSE', 'TASK'] },
            entityId: { type: 'string' },
            auditType: { type: 'string' },
            status: { type: 'string', enum: ['SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'REQUIRES_FOLLOW_UP'] },
            auditorId: { type: 'string' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      try {
        const audits = await complianceService.listAudits(query);
        return reply.send({ data: audits });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /compliance/audits/:id - Get audit by ID
    complianceRoutes.get('/audits/:id', {
      schema: {
        description: 'Get compliance audit by ID',
        tags: ['Compliance'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      try {
        const audit = await complianceService.getAudit(id);
        return reply.send(audit);
      } catch (error: any) {
        return reply.status(404).send({ error: error.message });
      }
    });

    // POST /compliance/audits - Create audit
    complianceRoutes.post('/audits', {
      schema: {
        description: 'Create a new compliance audit',
        tags: ['Compliance'],
        body: {
          type: 'object',
          required: ['auditType', 'entityType', 'entityId', 'entityName', 'scheduledDate'],
          properties: {
            auditType: {
              type: 'string',
              enum: [
                'QUALITY_ASSURANCE',
                'CERTIFICATION_VERIFICATION',
                'TRACEABILITY_AUDIT',
                'ENVIRONMENTAL_COMPLIANCE',
                'FOOD_SAFETY',
                'SOCIAL_COMPLIANCE',
                'REGULATORY_COMPLIANCE',
                'SUPPLIER_AUDIT',
              ],
            },
            entityType: { type: 'string', enum: ['FARMER', 'BATCH', 'CONTRACT', 'WAREHOUSE', 'TASK'] },
            entityId: { type: 'string' },
            entityName: { type: 'string' },
            scheduledDate: { type: 'string', format: 'date-time' },
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      const userId = getAuthenticatedUserId(request);
      const userName = getAuthenticatedUserName(request);
      try {
        const audit = await complianceService.createAudit({
          ...body,
          scheduledDate: new Date(body.scheduledDate),
          auditorId: userId,
          auditorName: userName,
        });
        return reply.status(201).send(audit);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /compliance/audits/:id/start - Start audit
    complianceRoutes.post('/audits/:id/start', {
      schema: {
        description: 'Start a compliance audit',
        tags: ['Compliance'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      try {
        const audit = await complianceService.startAudit(id);
        return reply.send(audit);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /compliance/audits/:id/findings - Add finding to audit
    complianceRoutes.post('/audits/:id/findings', {
      schema: {
        description: 'Add finding to compliance audit',
        tags: ['Compliance'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
        body: {
          type: 'object',
          required: ['category', 'severity', 'description'],
          properties: {
            category: {
              type: 'string',
              enum: ['DOCUMENTATION', 'PROCESS', 'QUALITY', 'SAFETY', 'ENVIRONMENT', 'TRACEABILITY', 'CERTIFICATION', 'REGULATORY'],
            },
            severity: { type: 'string', enum: ['CRITICAL', 'MAJOR', 'MINOR', 'OBSERVATION'] },
            description: { type: 'string' },
            evidence: { type: 'array', items: { type: 'string' } },
            correctiveAction: { type: 'string' },
            correctiveActionDueDate: { type: 'string', format: 'date-time' },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      try {
        const finding = {
          ...body,
          correctiveActionDueDate: body.correctiveActionDueDate ? new Date(body.correctiveActionDueDate) : undefined,
        };
        const audit = await complianceService.addFinding(id, finding);
        return reply.send(audit);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /compliance/audits/:id/complete - Complete audit
    complianceRoutes.post('/audits/:id/complete', {
      schema: {
        description: 'Complete a compliance audit',
        tags: ['Compliance'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
        body: {
          type: 'object',
          properties: {
            complianceScore: { type: 'number', minimum: 0, maximum: 100 },
            recommendations: { type: 'array', items: { type: 'string' } },
            nextAuditDate: { type: 'string', format: 'date-time' },
            documents: { type: 'array', items: { type: 'string' } },
          },
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      try {
        const input = {
          ...body,
          nextAuditDate: body.nextAuditDate ? new Date(body.nextAuditDate) : undefined,
        };
        const audit = await complianceService.completeAudit(id, input);
        return reply.send(audit);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /compliance/requirements - Get compliance requirements
    complianceRoutes.get('/requirements', {
      schema: {
        description: 'Get compliance requirements',
        tags: ['Compliance'],
        querystring: {
          type: 'object',
          properties: {
            category: { type: 'string' },
            applicableTo: { type: 'string' },
            isActive: { type: 'boolean' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      try {
        const requirements = await complianceService.getRequirements(query);
        return reply.send({ data: requirements });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /compliance/requirements - Register compliance requirement
    complianceRoutes.post('/requirements', {
      schema: {
        description: 'Register a compliance requirement',
        tags: ['Compliance'],
        body: {
          type: 'object',
          required: ['requirementCode', 'title', 'description', 'category', 'applicableTo', 'effectiveDate'],
          properties: {
            requirementCode: { type: 'string' },
            title: { type: 'string' },
            description: { type: 'string' },
            category: { type: 'string' },
            applicableTo: { type: 'array', items: { type: 'string' } },
            isMandatory: { type: 'boolean', default: true },
            certificationType: { type: 'string' },
            regulation: { type: 'string' },
            effectiveDate: { type: 'string', format: 'date-time' },
            expiryDate: { type: 'string', format: 'date-time' },
            isActive: { type: 'boolean', default: true },
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      try {
        const requirement = await complianceService.registerRequirement({
          ...body,
          effectiveDate: new Date(body.effectiveDate),
          expiryDate: body.expiryDate ? new Date(body.expiryDate) : undefined,
        });
        return reply.status(201).send(requirement);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /compliance/check/:entityType/:entityId - Check entity compliance
    complianceRoutes.get('/check/:entityType/:entityId', {
      schema: {
        description: 'Check entity compliance',
        tags: ['Compliance'],
        params: {
          type: 'object',
          properties: {
            entityType: { type: 'string', enum: ['FARMER', 'BATCH', 'CONTRACT', 'WAREHOUSE'] },
            entityId: { type: 'string' },
          },
          required: ['entityType', 'entityId'],
        },
      },
    }, async (request, reply) => {
      const { entityType, entityId } = request.params as { entityType: string; entityId: string };
      try {
        const compliance = await complianceService.checkCompliance(entityType as any, entityId);
        return reply.send(compliance);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // POST /compliance/reports - Generate compliance report
    complianceRoutes.post('/reports', {
      schema: {
        description: 'Generate compliance report',
        tags: ['Compliance'],
        body: {
          type: 'object',
          required: ['reportType', 'period'],
          properties: {
            reportType: { type: 'string', enum: ['QUARTERLY', 'ANNUAL', 'AD_HOC', 'REGULATORY_SUBMISSION'] },
            period: { type: 'string' }, // e.g., "2024-Q1"
          },
        },
      },
    }, async (request, reply) => {
      const body = request.body as any;
      try {
        const report = await complianceService.generateComplianceReport(body.reportType, body.period);
        return reply.status(201).send(report);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /compliance/reports/:id - Get compliance report
    complianceRoutes.get('/reports/:id', {
      schema: {
        description: 'Get compliance report by ID',
        tags: ['Compliance'],
        params: {
          type: 'object',
          properties: {
            id: { type: 'string' },
          },
          required: ['id'],
        },
      },
    }, async (request, reply) => {
      const { id } = request.params as { id: string };
      try {
        const report = await complianceService.getComplianceReport(id);
        return reply.send(report);
      } catch (error: any) {
        return reply.status(404).send({ error: error.message });
      }
    });
  });
}

