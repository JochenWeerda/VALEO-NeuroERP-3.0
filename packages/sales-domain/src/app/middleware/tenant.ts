import { FastifyRequest, FastifyReply } from 'fastify';

declare module 'fastify' {
  interface FastifyRequest {
    tenantId?: string;
  }
}

export async function tenantMiddleware(request: FastifyRequest, reply: FastifyReply) {
  try {
    // Extract tenant ID from header
    const tenantId = request.headers['x-tenant-id'] as string;

    if (tenantId === undefined || tenantId === null) {
      return reply.code(400).send({
        error: 'Bad Request',
        message: 'Missing x-tenant-id header',
      });
    }

    // Validate tenant ID format (basic validation)
    if (!/^[a-zA-Z0-9_-]+$/.test(tenantId)) {
      return reply.code(400).send({
        error: 'Bad Request',
        message: 'Invalid tenant ID format',
      });
    }

    // Attach tenant ID to request
    request.tenantId = tenantId;

    // Continue to next middleware
  } catch (error) {
    request.log.error({ error }, 'Tenant middleware error');
    return reply.code(500).send({
      error: 'Internal Server Error',
      message: 'Tenant validation failed',
    });
  }
}
