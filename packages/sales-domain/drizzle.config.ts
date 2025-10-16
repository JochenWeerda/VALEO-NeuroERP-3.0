import { defineConfig } from 'drizzle-kit';
import * as dotenv from 'dotenv';

dotenv.config();

export default defineConfig({
  schema: './src/infra/db/schema.ts',
  out: './src/infra/db/migrations',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.POSTGRES_URL || 'postgres://user:pass@localhost:5432/sales',
  },
  verbose: true,
  strict: true,
});