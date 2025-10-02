let PgPoolConstructor = null;
let moduleError = null;
const pools = new Map();
function ensurePg() {
    if (PgPoolConstructor || moduleError) {
        return;
    }
    try {
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const pg = require('pg');
        PgPoolConstructor = pg.Pool;
    }
    catch (error) {
        moduleError = error;
    }
}
function assertPgAvailable(options) {
    ensurePg();
    if (!PgPoolConstructor || moduleError) {
        const message = [
            'Postgres driver "pg" is not installed.',
            'Install it in the active workspace (e.g. npm install pg) or use the REST repository for CRM.',
            moduleError ? `Original error: ${moduleError.message}` : undefined,
        ].filter(Boolean).join(' ');
        throw new Error(message);
    }
    if (!options.connectionString) {
        throw new Error('Postgres repository requires a connectionString. Set CRM_DATABASE_URL or pass options.postgres.connectionString.');
    }
}
export function getPostgresPool(options = {}) {
    assertPgAvailable(options);
    const name = options.name ?? 'default';
    const cached = pools.get(name);
    if (cached) {
        return cached;
    }
    const constructorOptions = {
        connectionString: options.connectionString,
    };
    if (options.max !== undefined)
        constructorOptions.max = options.max;
    if (options.idleTimeoutMillis !== undefined)
        constructorOptions.idleTimeoutMillis = options.idleTimeoutMillis;
    if (options.connectionTimeoutMillis !== undefined)
        constructorOptions.connectionTimeoutMillis = options.connectionTimeoutMillis;
    const pool = new PgPoolConstructor(constructorOptions);
    pools.set(name, pool);
    return pool;
}
export async function query(sql, params = [], options = {}) {
    const pool = getPostgresPool(options);
    return pool.query(sql, params);
}
export async function disposePools() {
    const disposals = Array.from(pools.values()).map((pool) => pool.end());
    await Promise.allSettled(disposals);
    pools.clear();
}
