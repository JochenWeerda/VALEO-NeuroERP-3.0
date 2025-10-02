/**
 * Drizzle Configuration for VALEO NeuroERP 3.0 HR Domain
 * Database migrations and schema management
 */

import type { Config } from 'drizzle-kit';

export default {
  schema: './src/infra/db/schema.ts',
  out: './migrations',
  driver: 'pg',
  dbCredentials: {
    connectionString: process.env.POSTGRES_URL || 'postgres://user:pass@localhost:5432/hr_domain'
  },
  verbose: true,
  strict: true,
  tablesFilter: ['!drizzle_*']
} satisfies Config;

