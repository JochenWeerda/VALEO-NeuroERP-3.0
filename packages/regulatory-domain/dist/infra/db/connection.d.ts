import * as schema from './schema';
export declare const db: import("drizzle-orm/postgres-js").PostgresJsDatabase<typeof schema>;
export declare function closeConnection(): Promise<void>;
//***REMOVED*** sourceMappingURL=connection.d.ts.map