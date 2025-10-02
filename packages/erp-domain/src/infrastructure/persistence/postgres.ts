import { Pool, PoolConfig } from 'pg';

let singleton: Pool | null = null;

export function getErpPool(config?: PoolConfig): Pool {
  if (singleton) {
    return singleton;
  }

  const connectionString = config?.connectionString ?? process.env.ERP_DATABASE_URL;
  if (!connectionString) {
    throw new Error('ERP_DATABASE_URL is not defined. Set it before initialising the ERP domain.');
  }

  singleton = new Pool({ ...config, connectionString });
  return singleton;
}

export async function closeErpPool(): Promise<void> {
  if (singleton) {
    await singleton.end();
    singleton = null;
  }
}