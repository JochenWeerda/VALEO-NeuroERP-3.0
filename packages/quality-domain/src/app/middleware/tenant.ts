import { FastifyRequest, FastifyReply } from 'fastify';

/**
 * Tenant middleware - validates tenant ID
 */
export async function tenantMiddleware(
  request: FastifyRequest,
  reply: FastifyReply
): Promise<void> {
  // Skip for health/meta endpoints
  if (request.url.startsWith('/health') || request.url.startsWith('/ready') || request.url.startsWith('/live')) {
    return;
  }

  const tenantId = request.headers['x-tenant-id'] as string;

  if (!tenantId) {
    reply.code(400).send({
      error: 'BadRequest',
      message: 'Missing x-tenant-id header',
    });
    return;
  }

  // Validate tenant ID format (UUID)
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(tenantId)) {
    reply.code(400).send({
      error: 'BadRequest',
      message: 'Invalid x-tenant-id format (must be UUID)',
    });
    return;
  }

  // Optional: Verify tenant exists and is active (could query DB)
  // For now, just validate format
}
