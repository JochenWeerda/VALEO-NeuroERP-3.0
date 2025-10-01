import { FastifyRequest, FastifyReply } from 'fastify';
import { extractAuthContext } from '../../infra/security/auth';

declare module 'fastify' {
  interface FastifyRequest {
    authContext?: {
      userId: string;
      tenantId: string;
      roles: string[];
      permissions: string[];
    };
  }
}

/**
 * Authentication middleware
 */
export async function authMiddleware(
  request: FastifyRequest,
  reply: FastifyReply
): Promise<void> {
  // Skip auth for health/meta endpoints
  if (request.url.startsWith('/health') || request.url.startsWith('/ready') || request.url.startsWith('/live')) {
    return;
  }

  try {
    const authContext = await extractAuthContext(request);
    request.authContext = authContext;
  } catch (error) {
    reply.code(401).send({
      error: 'Unauthorized',
      message: error instanceof Error ? error.message : 'Authentication failed',
    });
  }
}
