import { FastifyError, FastifyRequest, FastifyReply } from 'fastify';

/**
 * Global error handler
 */
export function errorHandler(
  error: FastifyError,
  request: FastifyRequest,
  reply: FastifyReply
): void {
  request.log.error(error);

  // Validation errors (from Zod)
  if (error.validation) {
    reply.code(400).send({
      error: 'ValidationError',
      message: 'Request validation failed',
      details: error.validation,
    });
    return;
  }

  // JWT/Auth errors
  if (error.message?.includes('jwt') || error.message?.includes('token')) {
    reply.code(401).send({
      error: 'Unauthorized',
      message: 'Authentication failed',
    });
    return;
  }

  // Not found
  if (error.statusCode === 404) {
    reply.code(404).send({
      error: 'NotFound',
      message: error.message ?? 'Resource not found',
    });
    return;
  }

  // Default 500
  reply.code(error.statusCode || 500).send({
    error: 'InternalServerError',
    message: process.env.NODE_ENV === 'production' 
      ? 'An internal error occurred' 
      : error.message,
  });
}

