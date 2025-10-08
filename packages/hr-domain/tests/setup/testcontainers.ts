import { v4 as uuidv4 } from 'uuid';
import { GenericContainer, StartedTestContainer } from 'testcontainers';
import { Client } from 'pg';

export interface PostgresTestContext {
  container: StartedTestContainer;
  connectionString: string;
}

export async function startPostgresContainer(): Promise<PostgresTestContext> {
  const password = 'postgres';
  const user = 'postgres';
  const dbNameSuffix = uuidv4().replace(/-/g, '').slice(0, 8);
  const database = 'hr_test_' + dbNameSuffix;

  const container = await new GenericContainer('postgres:15-alpine')
    .withEnv('POSTGRES_PASSWORD', password)
    .withEnv('POSTGRES_USER', user)
    .withExposedPorts(5432)
    .start();

  const port = container.getMappedPort(5432);
  const host = container.getHost();
  const baseConnectionString =
    'postgresql://' + user + ':' + password + '@' + host + ':' + port + '/postgres';

  const client = new Client({ connectionString: baseConnectionString });
  await client.connect();
  await client.query('CREATE DATABASE ' + database + ';');
  await client.end();

  const connectionString =
    'postgresql://' + user + ':' + password + '@' + host + ':' + port + '/' + database;

  return {
    container,
    connectionString,
  };
}

export async function stopPostgresContainer(context: PostgresTestContext): Promise<void> {
  await context.container.stop();
}
