#!/usr/bin/env node
// Drift check of a running domain database against the package's drizzle snapshot.
// Read-only: the session is set to read-only before anything is inspected. Compares
// columns, indexes, foreign keys and unique constraints of the target schema with the
// latest snapshot, so changes from any source (drizzle-kit push, psql, agents) show up.
// Usage (from a package): node ../../scripts/check_drizzle_drift.cjs [--json]
'use strict';
const path = require('node:path');
const { createRequire } = require('node:module');
const { classify, resolvedConfig } = require('./drizzle_apply_guard.cjs');
const { loadChain, expectedCatalog, actualCatalog, diffCatalog } = require('./verify_drizzle_migrations_probe.cjs');

async function main() {
  const pkgDir = process.cwd();
  const config = resolvedConfig(pkgDir);
  const { snapshot } = loadChain(pkgDir);
  const { Client } = createRequire(path.join(pkgDir, 'package.json'))('pg');
  const client = new Client({ connectionString: config.dbCredentials.url });
  await client.connect();
  try {
    await client.query('SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY');
    const target = (await client.query('SELECT current_database() AS db, current_schema() AS schema')).rows[0];
    const tables = (await client.query(
      "SELECT table_name FROM information_schema.tables WHERE table_schema = $1 AND table_type = 'BASE TABLE'",
      [target.schema],
    )).rows.map((r) => r.table_name);
    const migrationsTable = config.migrations?.table ?? '__drizzle_migrations';
    const chainTables = Object.values(snapshot.tables).map((t) => t.name);
    const verdict = classify({ chainTables, schemaTables: tables.filter((t) => t !== migrationsTable), journalExists: true });
    const where = `${target.db}.${target.schema}`;
    if (verdict.reason === 'foreign-target') {
      console.log(`[drizzle-drift] ${where} is not a domain schema of ${path.basename(pkgDir)}; no comparison.`);
      process.exitCode = 2;
      return;
    }
    const actual = await actualCatalog(client, target.schema);
    delete actual[migrationsTable];
    const problems = diffCatalog(expectedCatalog(snapshot), actual);
    if (process.argv.includes('--json')) {
      console.log(JSON.stringify({ target: where, problems }, null, 2));
    } else {
      console.log(`[drizzle-drift] ${where}: ${problems.length ? `${problems.length} differences` : 'matches the snapshot'}`);
      for (const problem of problems) console.log(`- ${problem}`);
    }
    process.exitCode = problems.length ? 1 : 0;
  } finally {
    await client.end();
  }
}

main().catch((error) => { console.error(`[drizzle-drift] ${error.message}`); process.exitCode = 1; });
