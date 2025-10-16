import Redis from 'ioredis';
import pino from 'pino';

const logger = pino({ name: 'redis-client' });

let redis: Redis | null = null;

/**
 * Initialize Redis connection
 */
export function initRedis(): Redis {
  if (redis) {
    return redis;
  }

  const redisUrl = process.env.REDIS_URL ?? 'redis://localhost:6379';
  const redisPassword = process.env.REDIS_PASSWORD;
  const redisDb = parseInt(process.env.REDIS_DB ?? '0', 10);

  redis = new Redis(redisUrl, {
    password: redisPassword || undefined,
    db: redisDb,
    retryStrategy(times: any) {
      const delay = Math.min(times * 50, 2000);
      return delay;
    },
    maxRetriesPerRequest: 3,
  } as any);

  redis.on('connect', () => {
    logger.info('Redis connected');
  });

  redis.on('error', (error) => {
    logger.error({ error }, 'Redis error');
  });

  return redis;
}

/**
 * Get Redis client
 */
export function getRedis(): Redis | null {
  return redis;
}

/**
 * Close Redis connection
 */
export async function closeRedis(): Promise<void> {
  if (redis) {
    await redis.quit();
    redis = null;
    logger.info('Redis connection closed');
  }
}

/**
 * Cache decorator - Cache function results
 */
export function cached(ttl: number = 300) {
  return function (
    target: any,
    propertyName: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const redis = getRedis();
      if (redis === undefined || redis === null) {
        // No Redis, just call original method
        return originalMethod.apply(this, args);
      }

      // Generate cache key from function name and arguments
      const cacheKey = `cache:${propertyName}:${JSON.stringify(args)}`;

      try {
        // Try to get from cache
        const cached = await redis.get(cacheKey);
        if (cached) {
          logger.debug({ cacheKey }, 'Cache hit');
          return JSON.parse(cached);
        }

        // Cache miss - call original method
        logger.debug({ cacheKey }, 'Cache miss');
        const result = await originalMethod.apply(this, args);

        // Store in cache
        await redis.setex(cacheKey, ttl, JSON.stringify(result));

        return result;
      } catch (error) {
        logger.error({ error, cacheKey }, 'Cache error');
        // On cache error, just call original method
        return originalMethod.apply(this, args);
      }
    };

    return descriptor;
  };
}

/**
 * Get value from cache
 */
export async function getCache<T>(key: string): Promise<T | null> {
  const redis = getRedis();
  if (redis === undefined || redis === null) return null;

  try {
    const value = await redis.get(key);
    return value ? JSON.parse(value) : null;
  } catch (error) {
    logger.error({ error, key }, 'Failed to get cache');
    return null;
  }
}

/**
 * Set value in cache
 */
export async function setCache(key: string, value: any, ttl: number = 300): Promise<void> {
  const redis = getRedis();
  if (redis === undefined || redis === null) return;

  try {
    await redis.setex(key, ttl, JSON.stringify(value));
  } catch (error) {
    logger.error({ error, key }, 'Failed to set cache');
  }
}

/**
 * Delete cache key
 */
export async function deleteCache(key: string): Promise<void> {
  const redis = getRedis();
  if (redis === undefined || redis === null) return;

  try {
    await redis.del(key);
  } catch (error) {
    logger.error({ error, key }, 'Failed to delete cache');
  }
}

/**
 * Delete cache keys by pattern
 */
export async function deleteCachePattern(pattern: string): Promise<void> {
  const redis = getRedis();
  if (redis === undefined || redis === null) return;

  try {
    const keys = await redis.keys(pattern);
    if (keys.length > 0) {
      await redis.del(...keys);
      logger.info({ pattern, count: keys.length }, 'Deleted cache keys');
    }
  } catch (error) {
    logger.error({ error, pattern }, 'Failed to delete cache pattern');
  }
}

