/**
 * Drizzle Configuration for VALEO NeuroERP 3.0 HR Domain
 * Database migrations and schema management
 */

import { defineConfig } from 'drizzle-kit';

// An empty POSTGRES_URL falls back to the local default, as before.
const databaseUrl = process.env.POSTGRES_URL;

export default defineConfig({
  schema: './src/infra/db/schema.ts',
  out: './migrations',
  dialect: 'postgresql',
  dbCredentials: {
    url: databaseUrl !== undefined && databaseUrl !== '' ? databaseUrl : 'postgres://user:pass@localhost:5432/hr_domain'
  },
  verbose: true,
  strict: true,
  tablesFilter: ['!drizzle_*']
});


