#!/usr/bin/env node
// Applies the drizzle migration chain of each given package inside ONE transaction on the
// shared test database (TEST_DATABASE_URL, i.e. valeo_probe), in a dedicated schema, compares
// the resulting catalog with the package's latest snapshot and always rolls back.
// Nothing persists on the shared database; no database, schema or container is created outside
// the transaction. Usage: node scripts/verify_drizzle_migrations_probe.cjs packages/audit-domain ...
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');

const ROOT = path.resolve(__dirname, '..');
const CHECK_SCHEMA = 'drizzle_chain_check';

function outDir(pkgDir) {
  const config = fs.readFileSync(path.join(pkgDir, 'drizzle.config.ts'), 'utf8');
  const match = /out:\s*'([^']+)'/.exec(config);
  if (!match) throw new Error(`${pkgDir}: no out directory in drizzle.config.ts`);
  return path.resolve(pkgDir, match[1]);
}

function loadChain(pkgDir) {
  const dir = outDir(pkgDir);
  const journal = JSON.parse(fs.readFileSync(path.join(dir, 'meta', '_journal.json'), 'utf8'));
  if (!journal.entries.length) throw new Error(`${pkgDir}: empty journal`);
  const migrations = journal.entries.map((entry, position) => {
    if (entry.idx !== position) throw new Error(`${pkgDir}: journal idx ${entry.idx} at position ${position}`);
    const file = path.join(dir, `${entry.tag}.sql`);
    if (!fs.existsSync(file)) throw new Error(`${pkgDir}: journal entry ${entry.tag} has no SQL file`);
    const statements = fs.readFileSync(file, 'utf8').split('--> statement-breakpoint').map((s) => s.trim()).filter(Boolean);
    return { tag: entry.tag, statements };
  });
  const last = journal.entries[journal.entries.length - 1];
  const snapshotFile = path.join(dir, 'meta', `${String(last.idx).padStart(4, '0')}_snapshot.json`);
  const snapshot = JSON.parse(fs.readFileSync(snapshotFile, 'utf8'));
  return { migrations, snapshot };
}

const normalizeDefault = (value) => (value === undefined || value === null ? null
  : String(value).replace(/::[a-z ]+(\[\])?/gi, '').replace(/^\((.*)\)$/, '$1').replace(/'/g, '').trim());

function expectedCatalog(snapshot) {
  const tables = {};
  for (const table of Object.values(snapshot.tables)) {
    tables[table.name] = {
      columns: Object.fromEntries(Object.values(table.columns).map((c) => [c.name, {
        type: c.type, notNull: Boolean(c.notNull), primaryKey: Boolean(c.primaryKey), default: normalizeDefault(c.default),
      }])),
      indexes: Object.fromEntries(Object.values(table.indexes).map((i) => [i.name, {
        columns: i.columns.map((c) => c.expression).join(','), unique: Boolean(i.isUnique),
      }])),
    };
  }
  return tables;
}

async function actualCatalog(client) {
  const columns = await client.query(`
    SELECT c.relname AS table_name, a.attname AS column_name, format_type(a.atttypid, a.atttypmod) AS type,
           a.attnotnull AS not_null, pg_get_expr(d.adbin, d.adrelid) AS default_expr,
           EXISTS (SELECT 1 FROM pg_index i WHERE i.indrelid = c.oid AND i.indisprimary AND a.attnum = ANY(i.indkey)) AS primary_key
      FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
      JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum > 0 AND NOT a.attisdropped
      LEFT JOIN pg_attrdef d ON d.adrelid = c.oid AND d.adnum = a.attnum
     WHERE n.nspname = $1 AND c.relkind = 'r'`, [CHECK_SCHEMA]);
  const indexes = await client.query(`
    SELECT t.relname AS table_name, ic.relname AS index_name, i.indisunique AS is_unique,
           (SELECT string_agg(a.attname, ',' ORDER BY k.ord) FROM unnest(i.indkey) WITH ORDINALITY k(attnum, ord)
              JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = k.attnum) AS columns
      FROM pg_index i JOIN pg_class ic ON ic.oid = i.indexrelid JOIN pg_class t ON t.oid = i.indrelid
      JOIN pg_namespace n ON n.oid = t.relnamespace
     WHERE n.nspname = $1 AND NOT i.indisprimary`, [CHECK_SCHEMA]);
  const tables = {};
  for (const row of columns.rows) {
    tables[row.table_name] ??= { columns: {}, indexes: {} };
    tables[row.table_name].columns[row.column_name] = {
      type: row.type, notNull: row.not_null, primaryKey: row.primary_key, default: normalizeDefault(row.default_expr),
    };
  }
  for (const row of indexes.rows) {
    tables[row.table_name] ??= { columns: {}, indexes: {} };
    tables[row.table_name].indexes[row.index_name] = { columns: row.columns, unique: row.is_unique };
  }
  return tables;
}

function diffCatalog(expected, actual) {
  const problems = [];
  const keys = (a, b) => [...new Set([...Object.keys(a), ...Object.keys(b)])].sort();
  for (const table of keys(expected, actual)) {
    if (!expected[table] || !actual[table]) { problems.push(`table ${table}: ${expected[table] ? 'missing' : 'unexpected'}`); continue; }
    for (const kind of ['columns', 'indexes']) {
      const e = expected[table][kind]; const a = actual[table][kind];
      for (const name of keys(e, a)) {
        if (JSON.stringify(e[name]) !== JSON.stringify(a[name])) {
          problems.push(`${table}.${kind}.${name}: expected ${JSON.stringify(e[name])}, got ${JSON.stringify(a[name])}`);
        }
      }
    }
  }
  return problems;
}

async function verifyPackage(Client, connectionString, pkg) {
  const pkgDir = path.resolve(ROOT, pkg);
  const { migrations, snapshot } = loadChain(pkgDir);
  const client = new Client({ connectionString });
  await client.connect();
  try {
    await client.query('BEGIN');
    await client.query(`CREATE SCHEMA ${CHECK_SCHEMA}`);
    await client.query(`SET LOCAL search_path TO ${CHECK_SCHEMA}`);
    let statements = 0;
    for (const migration of migrations) {
      for (const statement of migration.statements) { await client.query(statement); statements += 1; }
    }
    const problems = diffCatalog(expectedCatalog(snapshot), await actualCatalog(client));
    return { pkg, migrations: migrations.map((m) => m.tag), statements, tables: Object.keys(snapshot.tables).length, problems };
  } finally {
    await client.query('ROLLBACK').catch(() => undefined);
    await client.end();
  }
}

async function main() {
  const connectionString = process.env.TEST_DATABASE_URL;
  if (!connectionString) throw new Error('TEST_DATABASE_URL is required (shared test database valeo_probe)');
  if (!/\/valeo_probe(\?|$)/.test(connectionString)) throw new Error('TEST_DATABASE_URL must point to valeo_probe');
  const packages = process.argv.slice(2);
  if (!packages.length) throw new Error('usage: verify_drizzle_migrations_probe.cjs <package-dir>...');
  const { Client } = createRequire(path.join(ROOT, packages[0], 'package.json'))('pg');
  let failed = false;
  for (const pkg of packages) {
    const result = await verifyPackage(Client, connectionString, pkg);
    failed ||= result.problems.length > 0;
    console.log(JSON.stringify(result));
  }
  // Leftover check: the rollback must leave nothing behind.
  const client = new Client({ connectionString });
  await client.connect();
  const leftover = await client.query('SELECT 1 FROM pg_namespace WHERE nspname = $1', [CHECK_SCHEMA]);
  await client.end();
  if (leftover.rowCount) { console.error(`schema ${CHECK_SCHEMA} persisted`); failed = true; }
  process.exitCode = failed ? 1 : 0;
}

if (require.main === module) {
  main().catch((error) => { console.error(error.message); process.exitCode = 1; });
}

module.exports = { loadChain, expectedCatalog, diffCatalog, normalizeDefault };
