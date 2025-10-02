import { injectable } from 'inversify';
import Redis from 'ioredis';
import { MetricsService } from '../observability/metrics-service';

export interface CacheEntry<T = any> {
  key: string;
  value: T;
  ttl?: number;
  tags?: string[];
}

export interface CacheStats {
  hits: number;
  misses: number;
  sets: number;
  deletes: number;
  hitRate: number;
}

export enum CacheStrategy {
  LRU = 'lru',
  LFU = 'lfu',
  TTL = 'ttl',
  WRITE_THROUGH = 'write_through',
  WRITE_BEHIND = 'write_behind'
}

@injectable()
export class CacheService {
  private redis?: Redis;
  private readonly localCache = new Map<string, { value: any; expires?: number; tags?: string[] }>();
  private readonly stats = {
    hits: 0,
    misses: 0,
    sets: 0,
    deletes: 0
  };
  private readonly metrics = MetricsService.getInstance();
  private readonly maxLocalCacheSize = 1000;

  constructor() {
    this.initializeRedis();
    this.startMetricsReporting();
  }

  private initializeRedis(): void {
    if (process.env.REDIS_URL) {
      this.redis = new Redis(process.env.REDIS_URL, {
        enableReadyCheck: false,
        maxRetriesPerRequest: 3,
        lazyConnect: true
      });

      this.redis.on('error', (error: any) => {
        console.error('Redis connection error:', error);
        this.metrics.incrementErrorCount('cache', 'redis_connection');
      });

      this.redis.on('connect', () => {
        console.log('Connected to Redis');
      });
    }
  }

  private startMetricsReporting(): void {
    // Report cache hit rate every minute
    setInterval(() => {
      const total = this.stats.hits + this.stats.misses;
      const hitRate = total > 0 ? this.stats.hits / total : 0;
      this.metrics.setCacheHitRate('finance_cache', hitRate);
    }, 60000);
  }

  private isExpired(entry: { value: any; expires?: number }): boolean {
    return entry.expires ? Date.now() > entry.expires : false;
  }

  private evictLRU(): void {
    if (this.localCache.size >= this.maxLocalCacheSize) {
      // Simple LRU: remove oldest entry (in real implementation, track access time)
      const firstKey = this.localCache.keys().next().value;
      if (firstKey) {
        this.localCache.delete(firstKey);
      }
    }
  }

  async get<T>(key: string): Promise<T | null> {
    const startTime = Date.now();

    try {
      // Try local cache first
      const localEntry = this.localCache.get(key);
      if (localEntry && !this.isExpired(localEntry)) {
        this.stats.hits++;
        this.metrics.recordDatabaseQueryDuration('cache_get', 'local', (Date.now() - startTime) / 1000);
        return localEntry.value;
      }

      // Try Redis if available
      if (this.redis) {
        const redisValue = await this.redis.get(key);
        if (redisValue) {
          const parsed = JSON.parse(redisValue);
          // Update local cache
          this.localCache.set(key, parsed);
          this.evictLRU();

          this.stats.hits++;
          this.metrics.recordDatabaseQueryDuration('cache_get', 'redis', (Date.now() - startTime) / 1000);
          return parsed.value;
        }
      }

      this.stats.misses++;
      this.metrics.recordDatabaseQueryDuration('cache_get', 'miss', (Date.now() - startTime) / 1000);
      return null;
    } catch (error) {
      this.metrics.incrementErrorCount('cache', 'get_operation');
      console.error('Cache get error:', error);
      return null;
    }
  }

  async set<T>(key: string, value: T, ttl?: number, tags?: string[]): Promise<void> {
    const startTime = Date.now();

    try {
      const entry: { value: T; expires?: number; tags?: string[] } = {
        value,
        ...(ttl && { expires: Date.now() + ttl * 1000 }),
        ...(tags && { tags })
      };

      // Set in local cache
      this.localCache.set(key, entry);
      this.evictLRU();

      // Set in Redis if available
      if (this.redis) {
        const redisValue = JSON.stringify(entry);
        if (ttl) {
          await this.redis.setex(key, ttl, redisValue);
        } else {
          await this.redis.set(key, redisValue);
        }

        // Store tags for batch operations
        if (tags) {
          for (const tag of tags) {
            await this.redis.sadd(`tag:${tag}`, key);
          }
        }
      }

      this.stats.sets++;
      this.metrics.recordDatabaseQueryDuration('cache_set', this.redis ? 'redis' : 'local', (Date.now() - startTime) / 1000);
    } catch (error) {
      this.metrics.incrementErrorCount('cache', 'set_operation');
      console.error('Cache set error:', error);
    }
  }

  async delete(key: string): Promise<boolean> {
    const startTime = Date.now();

    try {
      let deleted = false;

      // Delete from local cache
      deleted = this.localCache.delete(key) || deleted;

      // Delete from Redis if available
      if (this.redis) {
        const result = await this.redis.del(key);
        deleted = deleted || result > 0;

        // Remove from tag sets
        const tags = await this.redis.keys('tag:*');
        for (const tagKey of tags) {
          await this.redis.srem(tagKey, key);
        }
      }

      if (deleted) {
        this.stats.deletes++;
      }

      this.metrics.recordDatabaseQueryDuration('cache_delete', this.redis ? 'redis' : 'local', (Date.now() - startTime) / 1000);
      return deleted;
    } catch (error) {
      this.metrics.incrementErrorCount('cache', 'delete_operation');
      console.error('Cache delete error:', error);
      return false;
    }
  }

  async invalidateByTag(tag: string): Promise<number> {
    const startTime = Date.now();

    try {
      let invalidated = 0;

      if (this.redis) {
        const keys = await this.redis.smembers(`tag:${tag}`);
        if (keys.length > 0) {
          await this.redis.del(...keys);
          await this.redis.del(`tag:${tag}`);

          // Remove from local cache
          for (const key of keys) {
            this.localCache.delete(key);
          }

          invalidated = keys.length;
        }
      } else {
        // Invalidate local cache by tag
        for (const [key, entry] of this.localCache.entries()) {
          if (entry.tags?.includes(tag)) {
            this.localCache.delete(key);
            invalidated++;
          }
        }
      }

      this.metrics.recordDatabaseQueryDuration('cache_invalidate', 'tag', (Date.now() - startTime) / 1000);
      return invalidated;
    } catch (error) {
      this.metrics.incrementErrorCount('cache', 'invalidate_operation');
      console.error('Cache invalidate error:', error);
      return 0;
    }
  }

  async clear(): Promise<void> {
    const startTime = Date.now();

    try {
      // Clear local cache
      this.localCache.clear();

      // Clear Redis if available
      if (this.redis) {
        await this.redis.flushdb();
      }

      this.metrics.recordDatabaseQueryDuration('cache_clear', 'all', (Date.now() - startTime) / 1000);
    } catch (error) {
      this.metrics.incrementErrorCount('cache', 'clear_operation');
      console.error('Cache clear error:', error);
    }
  }

  async exists(key: string): Promise<boolean> {
    // Check local cache
    const localEntry = this.localCache.get(key);
    if (localEntry && !this.isExpired(localEntry)) {
      return true;
    }

    // Check Redis if available
    if (this.redis) {
      const exists = await this.redis.exists(key);
      return exists === 1;
    }

    return false;
  }

  getStats(): CacheStats {
    const total = this.stats.hits + this.stats.misses;
    return {
      ...this.stats,
      hitRate: total > 0 ? this.stats.hits / total : 0
    };
  }

  async getKeys(pattern: string): Promise<string[]> {
    try {
      if (this.redis) {
        return await this.redis.keys(pattern);
      } else {
        // For local cache, simple pattern matching
        const keys: string[] = [];
        for (const key of this.localCache.keys()) {
          if (key.includes(pattern.replace('*', ''))) {
            keys.push(key);
          }
        }
        return keys;
      }
    } catch (error) {
      this.metrics.incrementErrorCount('cache', 'keys_operation');
      console.error('Cache keys error:', error);
      return [];
    }
  }

  // Specialized cache methods for finance domain
  async getLedgerBalance(accountId: string): Promise<any> {
    return this.get(`ledger:balance:${accountId}`);
  }

  async setLedgerBalance(accountId: string, balance: any, ttl = 300): Promise<void> {
    await this.set(`ledger:balance:${accountId}`, balance, ttl, ['ledger', 'balance']);
  }

  async getInvoiceData(invoiceId: string): Promise<any> {
    return this.get(`invoice:${invoiceId}`);
  }

  async setInvoiceData(invoiceId: string, data: any, ttl = 3600): Promise<void> {
    await this.set(`invoice:${invoiceId}`, data, ttl, ['invoice']);
  }

  async getTaxCalculation(companyId: string, period: string): Promise<any> {
    return this.get(`tax:calc:${companyId}:${period}`);
  }

  async setTaxCalculation(companyId: string, period: string, calculation: any, ttl = 7200): Promise<void> {
    await this.set(`tax:calc:${companyId}:${period}`, calculation, ttl, ['tax', 'calculation']);
  }

  async invalidateCompanyData(companyId: string): Promise<void> {
    await this.invalidateByTag(`company:${companyId}`);
  }

  async close(): Promise<void> {
    if (this.redis) {
      await this.redis.quit();
    }
  }
}

export default CacheService;