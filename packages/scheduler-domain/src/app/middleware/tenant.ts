import { FastifyReply, FastifyRequest } from 'fastify';

export async function tenantMiddleware(request: FastifyRequest, reply: FastifyReply): Promise<void> {
  // Tenant isolation is handled in the auth middleware
  // This middleware ensures tenant context is available for all requests

  if (!request.auth) {
    return reply.code(401).send({
      error: 'Unauthorized',
      message: 'Authentication required',
    });
  }

  const { tenantId } = request.auth;

  // Add tenant ID to request for easy access
  (request as any).tenantId = tenantId;

  // You could add additional tenant-specific validation here
  // For example, checking if the tenant is active, has permissions, etc.
}