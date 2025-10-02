#!/usr/bin/env ts-node
/**
 * Minimal SQL migration runner used during CRM migration.
 * Accepts either a single --file or a --dir containing *.sql files.
 */
import { promises as fs } from 'fs';
import path from 'path';
import { Pool } from 'pg';

interface CliOptions {
  connectionString: string;
  files: string[];
  dryRun: boolean;
}

interface RawArgs {
  url?: string;
  env?: string;
  file?: string[];
  dir?: string[];
  dryRun?: boolean;
}

function parseRawArgs(): RawArgs {
  const args = process.argv.slice(2);
  const raw: RawArgs = {};
  for (let index = 0; index < args.length; index += 1) {
    const key = args[index];
    const value = args[index + 1];

    switch (key) {
      case '--url':
        raw.url = value;
        index += 1;
        break;
      case '--env':
        raw.env = value;
        index += 1;
        break;
      case '--file':
        raw.file = (raw.file ?? []).concat(value);
        index += 1;
        break;
      case '--dir':
        raw.dir = (raw.dir ?? []).concat(value);
        index += 1;
        break;
      case '--dry-run':
        raw.dryRun = true;
        break;
      default:
        break;
    }
  }
  return raw;
}

async function collectSqlFiles(raw: RawArgs): Promise<string[]> {
  const files = raw.file ? [...raw.file] : [];

  if (raw.dir) {
    for (const dir of raw.dir) {
      const absoluteDir = path.resolve(dir);
      const entries = await fs.readdir(absoluteDir);
      entries
        .filter((entry) => entry.toLowerCase().endsWith('.sql'))
        .sort()
        .forEach((entry) => {
          files.push(path.join(absoluteDir, entry));
        });
    }
  }

  if (files.length === 0) {
    throw new Error('No SQL files provided. Use --file <path> or --dir <path>.');
  }

  return files;
}

function resolveConnectionString(raw: RawArgs): string {
  if (raw.url) {
    return raw.url;
  }
  if (raw.env) {
    const value = process.env[raw.env];
    if (!value) {
      throw new Error(`Environment variable ${raw.env} is not defined.`);
    }
    return value;
  }
  if (process.env.CRM_DATABASE_URL) {
    return process.env.CRM_DATABASE_URL;
  }
  throw new Error('Missing connection string. Provide --url or --env.');
}

function parseArgs(): Promise<CliOptions> {
  const raw = parseRawArgs();
  const connectionString = resolveConnectionString(raw);
  return collectSqlFiles(raw).then((files) => ({
    connectionString,
    files,
    dryRun: raw.dryRun ?? false,
  }));
}

async function runSql(pool: Pool, sqlPath: string, dryRun: boolean): Promise<void> {
  const sql = await fs.readFile(sqlPath, 'utf-8');
  if (dryRun) {
    console.log(`[dry-run] Would execute ${sqlPath}`);
    return;
  }
  console.log(`Executing ${sqlPath}`);
  await pool.query(sql);
}

async function main(): Promise<void> {
  const options = await parseArgs();
  const pool = new Pool({ connectionString: options.connectionString });

  try {
    for (const file of options.files) {
      await runSql(pool, file, options.dryRun);
    }
    console.log('Migration completed successfully.');
  } finally {
    await pool.end();
  }
}

main().catch((error) => {
  console.error('[run-sql-migration] Failed:', error);
  process.exit(1);
});