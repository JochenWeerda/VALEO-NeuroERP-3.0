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
export declare enum CacheStrategy {
    LRU = "lru",
    LFU = "lfu",
    TTL = "ttl",
    WRITE_THROUGH = "write_through",
    WRITE_BEHIND = "write_behind"
}
export declare class CacheService {
    private redis?;
    private readonly localCache;
    private readonly stats;
    private readonly metrics;
    private readonly maxLocalCacheSize;
    constructor();
    private initializeRedis;
    private startMetricsReporting;
    private isExpired;
    private evictLRU;
    get<T>(key: string): Promise<T | null>;
    set<T>(key: string, value: T, ttl?: number, tags?: string[]): Promise<void>;
    delete(key: string): Promise<boolean>;
    invalidateByTag(tag: string): Promise<number>;
    clear(): Promise<void>;
    exists(key: string): Promise<boolean>;
    getStats(): CacheStats;
    getKeys(pattern: string): Promise<string[]>;
    getLedgerBalance(accountId: string): Promise<any>;
    setLedgerBalance(accountId: string, balance: any, ttl?: number): Promise<void>;
    getInvoiceData(invoiceId: string): Promise<any>;
    setInvoiceData(invoiceId: string, data: any, ttl?: number): Promise<void>;
    getTaxCalculation(companyId: string, period: string): Promise<any>;
    setTaxCalculation(companyId: string, period: string, calculation: any, ttl?: number): Promise<void>;
    invalidateCompanyData(companyId: string): Promise<void>;
    close(): Promise<void>;
}
export default CacheService;
//# sourceMappingURL=cache-service.d.ts.map