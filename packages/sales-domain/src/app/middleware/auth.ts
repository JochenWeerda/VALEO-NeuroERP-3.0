import { FastifyRequest, FastifyReply } from 'fastify';
import { verifyJWT } from '../../infra/security/jwt';

export interface AuthenticatedUser {
  userId: string;
  tenantId: string;
  roles: string[];
  permissions: string[];
}

declare module 'fastify' {
  interface FastifyRequest {
    user?: AuthenticatedUser;
  }
}

export async function authMiddleware(request: FastifyRequest, reply: FastifyReply) {
  try {
    const authHeader = request.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return reply.code(401).send({
        error: 'Unauthorized',
        message: 'Missing or invalid authorization header',
      });
    }

    const token = authHeader.substring(7); // Remove 'Bearer ' prefix

    // Verify JWT token
    const payload = await verifyJWT(token);

    // Attach user to request
    request.user = {
      userId: payload.sub,
      tenantId: payload.tenantId || request.headers['x-tenant-id'] as string,
      roles: payload.roles || [],
      permissions: payload.permissions || [],
    };

    // Continue to next middleware
  } catch (error) {
    request.log.error('Authentication error:', error);
    return reply.code(401).send({
      error: 'Unauthorized',
      message: 'Invalid or expired token',
    });
  }
}