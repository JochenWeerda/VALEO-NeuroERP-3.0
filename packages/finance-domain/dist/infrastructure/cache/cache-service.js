"use strict";
var __esDecorate = (this && this.__esDecorate) || function (ctor, descriptorIn, decorators, contextIn, initializers, extraInitializers) {
    function accept(f) { if (f !== void 0 && typeof f !== "function") throw new TypeError("Function expected"); return f; }
    var kind = contextIn.kind, key = kind === "getter" ? "get" : kind === "setter" ? "set" : "value";
    var target = !descriptorIn && ctor ? contextIn["static"] ? ctor : ctor.prototype : null;
    var descriptor = descriptorIn || (target ? Object.getOwnPropertyDescriptor(target, contextIn.name) : {});
    var _, done = false;
    for (var i = decorators.length - 1; i >= 0; i--) {
        var context = {};
        for (var p in contextIn) context[p] = p === "access" ? {} : contextIn[p];
        for (var p in contextIn.access) context.access[p] = contextIn.access[p];
        context.addInitializer = function (f) { if (done) throw new TypeError("Cannot add initializers after decoration has completed"); extraInitializers.push(accept(f || null)); };
        var result = (0, decorators[i])(kind === "accessor" ? { get: descriptor.get, set: descriptor.set } : descriptor[key], context);
        if (kind === "accessor") {
            if (result === void 0) continue;
            if (result === null || typeof result !== "object") throw new TypeError("Object expected");
            if (_ = accept(result.get)) descriptor.get = _;
            if (_ = accept(result.set)) descriptor.set = _;
            if (_ = accept(result.init)) initializers.unshift(_);
        }
        else if (_ = accept(result)) {
            if (kind === "field") initializers.unshift(_);
            else descriptor[key] = _;
        }
    }
    if (target) Object.defineProperty(target, contextIn.name, descriptor);
    done = true;
};
var __runInitializers = (this && this.__runInitializers) || function (thisArg, initializers, value) {
    var useValue = arguments.length > 2;
    for (var i = 0; i < initializers.length; i++) {
        value = useValue ? initializers[i].call(thisArg, value) : initializers[i].call(thisArg);
    }
    return useValue ? value : void 0;
};
var __setFunctionName = (this && this.__setFunctionName) || function (f, name, prefix) {
    if (typeof name === "symbol") name = name.description ? "[".concat(name.description, "]") : "";
    return Object.defineProperty(f, "name", { configurable: true, value: prefix ? "".concat(prefix, " ", name) : name });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.CacheService = exports.CacheStrategy = void 0;
const inversify_1 = require("inversify");
const ioredis_1 = __importDefault(require("ioredis"));
const metrics_service_1 = require("../observability/metrics-service");
var CacheStrategy;
(function (CacheStrategy) {
    CacheStrategy["LRU"] = "lru";
    CacheStrategy["LFU"] = "lfu";
    CacheStrategy["TTL"] = "ttl";
    CacheStrategy["WRITE_THROUGH"] = "write_through";
    CacheStrategy["WRITE_BEHIND"] = "write_behind";
})(CacheStrategy || (exports.CacheStrategy = CacheStrategy = {}));
let CacheService = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var CacheService = _classThis = class {
        constructor() {
            this.localCache = new Map();
            this.stats = {
                hits: 0,
                misses: 0,
                sets: 0,
                deletes: 0
            };
            this.metrics = metrics_service_1.MetricsService.getInstance();
            this.maxLocalCacheSize = 1000;
            this.initializeRedis();
            this.startMetricsReporting();
        }
        initializeRedis() {
            if (process.env.REDIS_URL) {
                this.redis = new ioredis_1.default(process.env.REDIS_URL, {
                    enableReadyCheck: false,
                    maxRetriesPerRequest: 3,
                    lazyConnect: true
                });
                this.redis.on('error', (error) => {
                    console.error('Redis connection error:', error);
                    this.metrics.incrementErrorCount('cache', 'redis_connection');
                });
                this.redis.on('connect', () => {
                    console.log('Connected to Redis');
                });
            }
        }
        startMetricsReporting() {
            // Report cache hit rate every minute
            setInterval(() => {
                const total = this.stats.hits + this.stats.misses;
                const hitRate = total > 0 ? this.stats.hits / total : 0;
                this.metrics.setCacheHitRate('finance_cache', hitRate);
            }, 60000);
        }
        isExpired(entry) {
            return entry.expires ? Date.now() > entry.expires : false;
        }
        evictLRU() {
            if (this.localCache.size >= this.maxLocalCacheSize) {
                // Simple LRU: remove oldest entry (in real implementation, track access time)
                const firstKey = this.localCache.keys().next().value;
                if (firstKey) {
                    this.localCache.delete(firstKey);
                }
            }
        }
        async get(key) {
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
            }
            catch (error) {
                this.metrics.incrementErrorCount('cache', 'get_operation');
                console.error('Cache get error:', error);
                return null;
            }
        }
        async set(key, value, ttl, tags) {
            const startTime = Date.now();
            try {
                const entry = {
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
                    }
                    else {
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
            }
            catch (error) {
                this.metrics.incrementErrorCount('cache', 'set_operation');
                console.error('Cache set error:', error);
            }
        }
        async delete(key) {
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
            }
            catch (error) {
                this.metrics.incrementErrorCount('cache', 'delete_operation');
                console.error('Cache delete error:', error);
                return false;
            }
        }
        async invalidateByTag(tag) {
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
                }
                else {
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
            }
            catch (error) {
                this.metrics.incrementErrorCount('cache', 'invalidate_operation');
                console.error('Cache invalidate error:', error);
                return 0;
            }
        }
        async clear() {
            const startTime = Date.now();
            try {
                // Clear local cache
                this.localCache.clear();
                // Clear Redis if available
                if (this.redis) {
                    await this.redis.flushdb();
                }
                this.metrics.recordDatabaseQueryDuration('cache_clear', 'all', (Date.now() - startTime) / 1000);
            }
            catch (error) {
                this.metrics.incrementErrorCount('cache', 'clear_operation');
                console.error('Cache clear error:', error);
            }
        }
        async exists(key) {
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
        getStats() {
            const total = this.stats.hits + this.stats.misses;
            return {
                ...this.stats,
                hitRate: total > 0 ? this.stats.hits / total : 0
            };
        }
        async getKeys(pattern) {
            try {
                if (this.redis) {
                    return await this.redis.keys(pattern);
                }
                else {
                    // For local cache, simple pattern matching
                    const keys = [];
                    for (const key of this.localCache.keys()) {
                        if (key.includes(pattern.replace('*', ''))) {
                            keys.push(key);
                        }
                    }
                    return keys;
                }
            }
            catch (error) {
                this.metrics.incrementErrorCount('cache', 'keys_operation');
                console.error('Cache keys error:', error);
                return [];
            }
        }
        // Specialized cache methods for finance domain
        async getLedgerBalance(accountId) {
            return this.get(`ledger:balance:${accountId}`);
        }
        async setLedgerBalance(accountId, balance, ttl = 300) {
            await this.set(`ledger:balance:${accountId}`, balance, ttl, ['ledger', 'balance']);
        }
        async getInvoiceData(invoiceId) {
            return this.get(`invoice:${invoiceId}`);
        }
        async setInvoiceData(invoiceId, data, ttl = 3600) {
            await this.set(`invoice:${invoiceId}`, data, ttl, ['invoice']);
        }
        async getTaxCalculation(companyId, period) {
            return this.get(`tax:calc:${companyId}:${period}`);
        }
        async setTaxCalculation(companyId, period, calculation, ttl = 7200) {
            await this.set(`tax:calc:${companyId}:${period}`, calculation, ttl, ['tax', 'calculation']);
        }
        async invalidateCompanyData(companyId) {
            await this.invalidateByTag(`company:${companyId}`);
        }
        async close() {
            if (this.redis) {
                await this.redis.quit();
            }
        }
    };
    __setFunctionName(_classThis, "CacheService");
    (() => {
        const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
        __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
        CacheService = _classThis = _classDescriptor.value;
        if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        __runInitializers(_classThis, _classExtraInitializers);
    })();
    return CacheService = _classThis;
})();
exports.CacheService = CacheService;
exports.default = CacheService;
//# sourceMappingURL=cache-service.js.map