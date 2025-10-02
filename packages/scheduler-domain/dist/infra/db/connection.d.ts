import postgres from 'postgres';
import * as schema from './schema';
declare const client: postgres.Sql<{}>;
export declare const db: import("drizzle-orm/postgres-js").PostgresJsDatabase<typeof schema>;
export declare function checkDatabaseConnection(): Promise<boolean>;
export declare function closeDatabaseConnection(): Promise<void>;
export { client };
//# sourceMappingURL=connection.d.ts.map