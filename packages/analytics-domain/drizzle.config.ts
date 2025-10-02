import { defineConfig } from 'drizzle-kit';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

export default defineConfig({
  schema: './src/infra/db/schema.ts',
  out: './migrations',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL || process.env.POSTGRES_URL || 'postgresql://localhost:5432/analytics',
  },
  verbose: true,
  strict: true,
});