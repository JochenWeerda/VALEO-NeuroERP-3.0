#!/usr/bin/env node
// Preflight for `migrate:apply` (drizzle-kit migrate) of a domain package.
// Resolves the package's drizzle.config.ts exactly as drizzle-kit does (same env fallbacks),
// then refuses targets that are not a domain database schema:
//   - the target schema contains `alembic_version` or tables outside this chain
//     (e.g. the backend main database reached through the DATABASE_URL fallback);
//   - chain tables exist but no migration journal (schema created by `push` or by hand):
//     reconcile first, a blind migrate would fail half-way.
// A fresh schema or one with an existing journal is migrated with drizzle-kit migrate.
// Usage (from a package): node ../../scripts/drizzle_apply_guard.cjs [--check]
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync, spawnSync } = require('node:child_process');
const { createRequire } = require('node:module');
const { loadChain } = require('./verify_drizzle_migrations_probe.cjs');

// Run the package's own tools through node directly (no shell, arguments stay intact).
const packageBin = (pkgDir, specifier) => createRequire(path.join(pkgDir, 'package.json')).resolve(specifier);

function resolvedConfig(pkgDir) {
  // dotenv prints banners to stdout, so the config is framed by a marker.
  const code = "import('./drizzle.config.ts').then((m) => process.stdout.write('@@DRIZZLE_CONFIG@@' + JSON.stringify(m.default.default ?? m.default)))";
  const out = execFileSync(process.execPath, [packageBin(pkgDir, 'tsx/cli'), '-e', code], { cwd: pkgDir, encoding: 'utf8' });
  const marker = out.lastIndexOf('@@DRIZZLE_CONFIG@@');
  if (marker < 0) throw new Error('drizzle.config.ts could not be resolved');
  return JSON.parse(out.slice(marker + '@@DRIZZLE_CONFIG@@'.length));
}

function classify({ chainTables, schemaTables, journalExists }) {
  const foreign = schemaTables.filter((t) => !chainTables.includes(t));
  if (schemaTables.includes('alembic_version') || foreign.length) {
    return { ok: false, reason: 'foreign-target', detail: foreign.slice(0, 10) };
  }
  const present = schemaTables.filter((t) => chainTables.includes(t));
  if (journalExists) return { ok: true, reason: 'incremental', detail: present };
  if (present.length) return { ok: false, reason: 'unjournaled-tables', detail: present };
  return { ok: true, reason: 'fresh', detail: [] };
}

async function inspect(pkgDir, config) {
  const { snapshot } = loadChain(pkgDir);
  const chainTables = Object.values(snapshot.tables).map((t) => t.name);
  const migrationsSchema = config.migrations?.schema ?? 'drizzle';
  const migrationsTable = config.migrations?.table ?? '__drizzle_migrations';
  const { Client } = createRequire(path.join(pkgDir, 'package.json'))('pg');
  const client = new Client({ connectionString: config.dbCredentials.url });
  await client.connect();
  try {
    const target = (await client.query('SELECT current_database() AS db, current_schema() AS schema')).rows[0];
    const tables = await client.query(
      "SELECT table_name FROM information_schema.tables WHERE table_schema = $1 AND table_type = 'BASE TABLE'",
      [target.schema],
    );
    // The journal may live in the target schema itself (migrations.schema = schema) or apart.
    const journal = await client.query(
      'SELECT 1 FROM information_schema.tables WHERE table_schema = $1 AND table_name = $2',
      [migrationsSchema, migrationsTable],
    );
    const schemaTables = tables.rows.map((r) => r.table_name).filter((t) => !(target.schema === migrationsSchema && t === migrationsTable));
    return { target, chainTables, schemaTables, journalExists: journal.rowCount > 0, migrationsSchema, migrationsTable };
  } finally {
    await client.end();
  }
}

async function main() {
  const checkOnly = process.argv.includes('--check');
  const pkgDir = process.cwd();
  if (!fs.existsSync(path.join(pkgDir, 'drizzle.config.ts'))) throw new Error(`${pkgDir}: no drizzle.config.ts`);
  const config = resolvedConfig(pkgDir);
  const state = await inspect(pkgDir, config);
  const verdict = classify(state);
  const where = `${state.target.db}.${state.target.schema}`;
  const messages = {
    'foreign-target': `${where} is not a domain schema of ${path.basename(pkgDir)} (alembic_version or foreign tables: ${verdict.detail.join(', ')}). Check DATABASE_URL/POSTGRES_URL; nothing was changed.`,
    'unjournaled-tables': `${where} already holds chain tables without journal ${state.migrationsSchema}.${state.migrationsTable}: ${verdict.detail.join(', ')}. Reconcile them with the snapshot first; nothing was changed.`,
    incremental: `${where}: journal ${state.migrationsSchema}.${state.migrationsTable} found, applying pending migrations.`,
    fresh: `${where}: empty domain schema, applying the full chain.`,
  };
  console.log(`[drizzle-apply-guard] ${verdict.reason}: ${messages[verdict.reason]}`);
  if (!verdict.ok) { process.exitCode = 2; return; }
  if (checkOnly) return;
  // drizzle-kit does not export bin.cjs; take the declared bin next to its package entry.
  const kitDir = path.dirname(packageBin(pkgDir, 'drizzle-kit'));
  const kitBin = JSON.parse(fs.readFileSync(path.join(kitDir, 'package.json'), 'utf8')).bin['drizzle-kit'];
  // PGAPPNAME marks the session so governance.ddl_events attributes the change to drizzle-kit.
  const env = { ...process.env, PGAPPNAME: `drizzle-kit:${path.basename(pkgDir)}` };
  const run = spawnSync(process.execPath, [path.join(kitDir, kitBin), 'migrate'], { cwd: pkgDir, stdio: 'inherit', env });
  process.exitCode = run.status ?? 1;
}

if (require.main === module) {
  main().catch((error) => { console.error(`[drizzle-apply-guard] ${error.message}`); process.exitCode = 1; });
}

module.exports = { classify, resolvedConfig };
