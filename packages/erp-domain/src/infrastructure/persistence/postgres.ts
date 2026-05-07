import { Pool, PoolConfig } from 'pg';

let singleton: Pool | null = null;

export function getErpPool(config?: PoolConfig): Pool {
  if (singleton !== null) {
    return singleton;
  }

  const connectionString =
    config?.connectionString ??
    process.env.ERP_DATABASE_URL ??
    process.env.DATABASE_URL;
  if (connectionString === undefined || connectionString === null) {
    throw new Error(
      'DATABASE_URL oder ERP_DATABASE_URL ist nicht gesetzt. Bitte Umgebungsvariable konfigurieren.'
    );
  }

  singleton = new Pool({ ...config, connectionString });
  return singleton;
}

export async function closeErpPool(): Promise<void> {
  if (singleton !== null) {
    await singleton.end();
    singleton = null;
  }
}
