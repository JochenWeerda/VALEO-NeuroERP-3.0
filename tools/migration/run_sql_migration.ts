#!/usr/bin/env ts-node
/**
 * Minimal SQL migration runner (CRM, ERP, seeds).
 * Accepts either a single --file or a `--dir` containing *.sql files.
 *
 * Env: lädt Repo-Wurzel-`.env` und optional `./.env` im CWD (siehe `loadMigrationEnv`).
 * Connection string (first match): `--url`, `--env NAME`, dann
 * `ERP_DATABASE_URL`, `DATABASE_URL`, `CRM_DATABASE_URL`.
 *
 * Siehe auch: docs/erp-finanz-multitenancy.md, migrations/sql/erp/README.md, tools/migration/CRM_TOOLKIT.md.
 */
import { existsSync, promises as fs } from 'fs';
import * as path from 'path';
import { Pool } from 'pg';
import { config as loadEnv } from 'dotenv';

/**
 * Repo-Wurzel-`.env` zuerst (auch wenn das Tool aus Unterverzeichnissen gestartet wird),
 * dann optionales `./.env` im aktuellen Arbeitsverzeichnis (`override`).
 */
function loadMigrationEnv(): void {
  const cwdEnv = path.join(process.cwd(), '.env');
  const repoRootEnv = path.resolve(__dirname, '..', '..', '.env');
  const cwdResolved = path.resolve(cwdEnv);

  if (existsSync(repoRootEnv)) {
    loadEnv({ path: repoRootEnv });
  }
  if (existsSync(cwdEnv) && cwdResolved !== path.resolve(repoRootEnv)) {
    loadEnv({ path: cwdEnv, override: true });
  }
  if (!existsSync(repoRootEnv) && !existsSync(cwdEnv)) {
    loadEnv();
  }
}

loadMigrationEnv();

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

function firstNonEmptyEnv(...keys: string[]): string | undefined {
  for (const key of keys) {
    const value = process.env[key];
    if (typeof value === 'string' && value.trim().length > 0) {
      return value.trim();
    }
  }
  return undefined;
}

function resolveConnectionString(raw: RawArgs): string {
  if (raw.url) {
    return raw.url;
  }
  if (raw.env) {
    const value = process.env[raw.env];
    if (!value || String(value).trim().length === 0) {
      throw new Error(`Environment variable ${raw.env} is not defined.`);
    }
    return String(value).trim();
  }
  const fromEnv = firstNonEmptyEnv('ERP_DATABASE_URL', 'DATABASE_URL', 'CRM_DATABASE_URL');
  if (fromEnv) {
    return fromEnv;
  }
  throw new Error(
    'Missing connection string. Provide --url, --env VAR, or set ERP_DATABASE_URL, DATABASE_URL, or CRM_DATABASE_URL.',
  );
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
