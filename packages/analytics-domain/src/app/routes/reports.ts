import { FastifyInstance } from 'fastify';
import { eq, and, desc, sql } from 'drizzle-orm';
import { drizzle } from 'drizzle-orm/node-postgres';
import { createReadStream } from 'fs';
import { stat } from 'fs/promises';
import {
  GenerateReportRequestSchema,
  ReportResponseSchema,
  ReportQuerySchema,
  ReportListResponseSchema,
  ReportContentResponseSchema,
} from '../../contracts/report-contracts';
import { reports } from '../../infra/db/schema';
import { Report } from '../../domain/entities/report';
import { createReportGeneratedEvent } from '../../domain/events/event-factories';
import { getEventPublisher } from '../../infra/messaging/publisher';

export interface ReportGenerator {
  generateReport(
    tenantId: string,
    type: string,
    parameters: any,
    format: string
  ): Promise<{
    data: any;
    uri?: string;
    recordCount: number;
  }>;
}

export async function registerReportRoutes(
  fastify: FastifyInstance,
  db: ReturnType<typeof drizzle>,
  reportGenerator: ReportGenerator
) {
  // GET /reports - List reports with filtering and pagination
  fastify.get('/reports', {
    schema: {
      description: 'Get reports with filtering and pagination',
      tags: ['Reports'],
      querystring: ReportQuerySchema,
      response: {
        200: ReportListResponseSchema,
      },
    },
    handler: async (request, reply) => {
      const query = request.query as any;

      // Build where conditions
      const conditions = [eq(reports.tenantId, request.tenantId)];

      // Apply filters
      if (query.type) {
        conditions.push(eq(reports.type, query.type));
      }

      if (query.format) {
        conditions.push(eq(reports.format, query.format));
      }

      if (query.from) {
        conditions.push(sql`${reports.generatedAt} >= ${new Date(query.from)}`);
      }

      if (query.to) {
        conditions.push(sql`${reports.generatedAt} <= ${new Date(query.to)}`);
      }

      // Pagination
      const page = query.page || 1;
      const pageSize = query.pageSize || 20;
      const offset = (page - 1) * pageSize;

      const results = await db
        .select()
        .from(reports)
        .where(and(...conditions))
        .orderBy(desc(reports.generatedAt))
        .limit(pageSize)
        .offset(offset);

      // Get total count for pagination
      const totalResult = await db
        .select({ count: sql<number>`count(*)` })
        .from(reports)
        .where(and(...conditions));

      const total = totalResult[0]?.count || 0;

      const reportResponses = results.map(row => ({
        id: row.id,
        tenantId: row.tenantId,
        type: row.type,
        parameters: row.parameters,
        generatedAt: row.generatedAt.toISOString(),
        uri: row.uri || undefined,
        format: row.format,
        metadata: row.metadata || {},
        version: row.version,
      }));

      return {
        data: reportResponses,
        pagination: {
          page,
          pageSize,
          total,
          totalPages: Math.ceil(total / pageSize),
        },
      };
    },
  });

  // GET /reports/:id - Get specific report
  fastify.get('/reports/:id', {
    schema: {
      description: 'Get a specific report by ID',
      tags: ['Reports'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' },
        },
        required: ['id'],
      },
      response: {
        200: ReportResponseSchema,
        404: {
          type: 'object',
          properties: {
            error: { type: 'string' },
            message: { type: 'string' },
          },
        },
      },
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };

      const result = await db
        .select()
        .from(reports)
        .where(and(
          eq(reports.id, id),
          eq(reports.tenantId, request.tenantId)
        ))
        .limit(1);

      if (result.length === 0) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'Report not found',
        });
      }

      const row = result[0];
      if (!row) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'Report not found',
        });
      }

      return {
        id: row.id,
        tenantId: row.tenantId,
        type: row.type,
        parameters: row.parameters,
        generatedAt: row.generatedAt.toISOString(),
        uri: row.uri || undefined,
        format: row.format,
        metadata: row.metadata || {},
        version: row.version,
      };
    },
  });

  // GET /reports/:id/content - Get report content
  fastify.get('/reports/:id/content', {
    schema: {
      description: 'Get report content/data',
      tags: ['Reports'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' },
        },
        required: ['id'],
      },
      response: {
        200: ReportContentResponseSchema,
        404: {
          type: 'object',
          properties: {
            error: { type: 'string' },
            message: { type: 'string' },
          },
        },
      },
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };

      const result = await db
        .select()
        .from(reports)
        .where(and(
          eq(reports.id, id),
          eq(reports.tenantId, request.tenantId)
        ))
        .limit(1);

      if (result.length === 0) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'Report not found',
        });
      }

      const row = result[0];
      if (!row) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'Report not found',
        });
      }

      // If report has a URI (file path), stream the file
      if (row.uri && row.format !== 'json') {
        try {
          const fileStat = await stat(row.uri);
          const stream = createReadStream(row.uri);

          let contentType = 'application/octet-stream';
          switch (row.format) {
            case 'csv':
              contentType = 'text/csv';
              break;
            case 'excel':
              contentType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
              break;
            case 'pdf':
              contentType = 'application/pdf';
              break;
          }

          return reply
            .header('Content-Type', contentType)
            .header('Content-Length', fileStat.size)
            .header('Content-Disposition', `attachment; filename="report-${id}.${row.format}"`)
            .send(stream);

        } catch (error) {
          return reply.code(500).send({
            error: 'Internal Server Error',
            message: 'Failed to read report file',
          });
        }
      }

      // For JSON reports or reports without URI, return the stored data
      const metadata = row.metadata as any;
      return {
        report: {
          id: row.id,
          tenantId: row.tenantId,
          type: row.type,
          parameters: row.parameters,
          generatedAt: row.generatedAt.toISOString(),
          uri: row.uri || undefined,
          format: row.format,
          metadata: row.metadata || {},
          version: row.version,
        },
        content: metadata?.data || {}, // Assuming data is stored in metadata
        contentType: 'application/json',
        contentLength: JSON.stringify(metadata?.data || {}).length,
      };
    },
  });

  // POST /reports - Generate a new report
  fastify.post('/reports', {
    schema: {
      description: 'Generate a new report',
      tags: ['Reports'],
      body: GenerateReportRequestSchema,
      response: {
        202: ReportResponseSchema,
      },
    },
    handler: async (request, reply) => {
      const body = request.body as any;

      // Generate unique report ID
      const reportId = `report-${request.tenantId}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

      // Start report generation asynchronously
      setImmediate(async () => {
        try {
          const startTime = Date.now();

          // Generate the report
          const result = await reportGenerator.generateReport(
            request.tenantId,
            body.type,
            body.parameters,
            body.format
          );

          const executionTimeMs = Date.now() - startTime;

          // Create report entity
          const report = Report.create({
            id: reportId,
            tenantId: request.tenantId,
            type: body.type,
            parameters: body.parameters,
            generatedAt: new Date(),
            uri: result.uri,
            format: body.format,
            metadata: {
              totalRecords: result.recordCount,
              executionTimeMs,
              ...(body.format === 'json' && { data: result.data } as any),
            },
          });

          // Save report metadata
          await db.insert(reports).values({
            id: report.id,
            tenantId: report.tenantId,
            type: report.type,
            parameters: report.parameters,
            generatedAt: report.generatedAt,
            uri: report.uri,
            format: report.format,
            metadata: report.metadata,
          });

          // Publish domain event
          const event = createReportGeneratedEvent(report, result.recordCount);
          await getEventPublisher().publish(event);

        } catch (error) {
          console.error('Report generation failed:', error);

          // Update report with error status
          await db
            .update(reports)
            .set({
              metadata: {
                error: error instanceof Error ? error.message : 'Unknown error',
                status: 'failed',
              },
              updatedAt: new Date(),
            })
            .where(eq(reports.id, reportId));
        }
      });

      // Return initial response with report ID
      return reply.code(202).send({
        id: reportId,
        tenantId: request.tenantId,
        type: body.type,
        parameters: body.parameters,
        generatedAt: new Date().toISOString(),
        format: body.format,
        metadata: {
          status: 'processing',
        },
        version: 1,
      });
    },
  });

  // DELETE /reports/:id - Delete report
  fastify.delete('/reports/:id', {
    schema: {
      description: 'Delete a report',
      tags: ['Reports'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' },
        },
        required: ['id'],
      },
      response: {
        204: {
          type: 'null',
          description: 'Report deleted successfully',
        },
        404: {
          type: 'object',
          properties: {
            error: { type: 'string' },
            message: { type: 'string' },
          },
        },
      },
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };

      const result = await db
        .delete(reports)
        .where(and(
          eq(reports.id, id),
          eq(reports.tenantId, request.tenantId)
        ));

      if (result.rowCount === 0) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'Report not found',
        });
      }

      return reply.code(204).send();
    },
  });
}

// Extend FastifyRequest to include tenantId
declare module 'fastify' {
  interface FastifyRequest {
    tenantId: string;
  }
}