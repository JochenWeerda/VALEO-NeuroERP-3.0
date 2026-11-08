import { Client } from 'pg';
import { runMigrations } from './migrations';

// Integration tests run on the shared PostgreSQL test bench (valeo_probe), never on a
// per-run database or container. Everything happens inside one transaction in an own
// schema and is rolled back, so nothing persists on the shared database.
const TEST_SCHEMA = 'hr_domain_it';

export interface ProbeTestContext {
  client: Client;
}

export async function openProbeTransaction(): Promise<ProbeTestContext> {
  const connectionString = process.env.TEST_DATABASE_URL;
  if (connectionString === undefined || !/\/valeo_probe(\?|$)/.test(connectionString)) {
    throw new Error('TEST_DATABASE_URL must point to the shared test database valeo_probe');
  }

  const client = new Client({ connectionString });
  await client.connect();
  try {
    await client.query('BEGIN');
    await client.query(`CREATE SCHEMA ${TEST_SCHEMA}`);
    await client.query(`SET LOCAL search_path TO ${TEST_SCHEMA}`);
    await runMigrations(client);
  } catch (error) {
    await client.query('ROLLBACK').catch(() => undefined);
    await client.end();
    throw error;
  }
  return { client };
}

export async function startTestCase(context: ProbeTestContext): Promise<void> {
  await context.client.query('SAVEPOINT hr_test_case');
}

export async function finishTestCase(context: ProbeTestContext): Promise<void> {
  await context.client.query('ROLLBACK TO SAVEPOINT hr_test_case');
}

export async function closeProbeTransaction(context: ProbeTestContext | undefined): Promise<void> {
  if (!context) {
    return;
  }
  try {
    await context.client.query('ROLLBACK');
  } finally {
    await context.client.end();
  }
}
