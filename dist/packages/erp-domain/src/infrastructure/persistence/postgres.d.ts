import { Pool, PoolConfig } from 'pg';
export declare function getErpPool(config?: PoolConfig): Pool;
export declare function closeErpPool(): Promise<void>;
//***REMOVED*** sourceMappingURL=postgres.d.ts.map