import { FastifyRequest, FastifyReply } from 'fastify';
import { getCache, setCache } from '../../infra/cache/redis-client';
import crypto from 'crypto';

/**
 * HTTP Cache middleware
 * Caches GET requests based on URL and query parameters
 */
export function cacheMiddleware(ttl: number = 60) {
  return async function (request: FastifyRequest, reply: FastifyReply): Promise<void> {
    // Only cache GET requests
    if (request.method !== 'GET') {
      return;
    }

    // Skip health endpoints
    if (request.url.startsWith('/health') || request.url.startsWith('/ready') || request.url.startsWith('/live')) {
      return;
    }

    // Generate cache key
    const tenantId = request.headers['x-tenant-id'] as string;
    const keyData = `${tenantId}:${request.method}:${request.url}`;
    const cacheKey = `http:${crypto.createHash('md5').update(keyData).digest('hex')}`;

    // Try to get from cache
    const cached = await getCache(cacheKey);
    if (cached) {
      reply.header('X-Cache', 'HIT');
      reply.send(cached);
      return;
    }

    // Set up cache on response
    reply.header('X-Cache', 'MISS');
    
    // Intercept response to cache it
    const originalSend = reply.send.bind(reply);
    reply.send = function (payload: any) {
      // Only cache successful responses
      if (reply.statusCode >= 200 && reply.statusCode < 300) {
        setCache(cacheKey, payload, ttl).catch(() => {
          // Ignore cache errors
        });
      }
      return originalSend(payload);
    };
  };
}
