export interface QueryResult<Row = unknown> {
    rows: Row[];
    rowCount: number;
}
export interface DatabasePoolOptions {
    name?: string;
    connectionString?: string;
    max?: number;
    idleTimeoutMillis?: number;
    connectionTimeoutMillis?: number;
}
interface PoolLike {
    query<Row = unknown>(sql: string, params?: unknown[]): Promise<QueryResult<Row>>;
    end(): Promise<void>;
}
export declare function getPostgresPool(options?: DatabasePoolOptions): PoolLike;
export declare function query<Row = unknown>(sql: string, params?: unknown[], options?: DatabasePoolOptions): Promise<QueryResult<Row>>;
export declare function disposePools(): Promise<void>;
export {};
//***REMOVED*** sourceMappingURL=postgres.d.ts.map