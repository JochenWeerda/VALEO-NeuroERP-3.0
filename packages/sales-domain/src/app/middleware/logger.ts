import { FastifyRequest, FastifyReply } from 'fastify';

export async function loggerMiddleware(request: FastifyRequest, reply: FastifyReply) {
  // Additional logging setup can be done here
  // Fastify already handles basic request/response logging

  // Log user and tenant information for security auditing
  if (request.user) {
    request.log.info({
      userId: request.user.userId,
      tenantId: request.tenantId,
      roles: request.user.roles,
    }, 'Authenticated request');
  }

  // Continue to next middleware
}