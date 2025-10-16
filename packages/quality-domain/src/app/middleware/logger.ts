import { FastifyRequest, FastifyReply } from 'fastify';

/**
 * Logger middleware - logs all requests
 */
export async function loggerMiddleware(
  request: FastifyRequest,
  reply: FastifyReply
): Promise<void> {
  const start = Date.now();

  (reply as any).addHook('onResponse', () => {
    const duration = Date.now() - start;
    
    request.log.info({
      method: request.method,
      url: request.url,
      statusCode: reply.statusCode,
      duration,
      tenantId: request.headers['x-tenant-id'],
      requestId: request.headers['x-request-id'],
    }, 'Request completed');
  });
}
