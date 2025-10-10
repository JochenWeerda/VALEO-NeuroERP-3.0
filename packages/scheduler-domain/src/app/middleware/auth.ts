import { FastifyReply, FastifyRequest } from 'fastify';
import { AuthContext, getJWTAuthenticator } from '../../infra/security/jwt';

declare module 'fastify' {
  interface FastifyRequest {
    auth?: AuthContext;
  }
}

export async function authMiddleware(request: FastifyRequest, reply: FastifyReply): Promise<void> {
  try {
    const authHeader = request.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return reply.code(401).send({
        error: 'Unauthorized',
        message: 'Missing or invalid authorization header',
      });
    }

    const token = authHeader.substring(7); // Remove 'Bearer ' prefix
    const authenticator = getJWTAuthenticator();

    const user = await authenticator.authenticate(token);

    // Extract tenant ID from header or token
    const tenantId = request.headers['x-tenant-id'] as string || user.tenantId;

    if (!tenantId) {
      return reply.code(400).send({
        error: 'Bad Request',
        message: 'Missing tenant ID',
      });
    }

    // Store auth context in request
    request.auth = {
      user,
      token,
      tenantId,
    };

  } catch (error) {
    return reply.code(401).send({
      error: 'Unauthorized',
      message: error instanceof Error ? error.message : 'Authentication failed',
    });
  }
}