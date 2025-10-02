import * as schema from './schema';
export declare const db: import("drizzle-orm/postgres-js").PostgresJsDatabase<typeof schema>;
export declare function checkDatabaseConnection(): Promise<boolean>;
export declare function closeDatabaseConnection(): Promise<void>;
//***REMOVED*** sourceMappingURL=connection.d.ts.map