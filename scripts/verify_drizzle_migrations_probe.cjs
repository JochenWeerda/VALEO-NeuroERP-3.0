#!/usr/bin/env node
// Applies the drizzle migration chain of each given package inside ONE transaction on the
// shared test database (TEST_DATABASE_URL, i.e. valeo_probe), in a dedicated schema, compares
// the resulting catalog with the package's latest snapshot and always rolls back.
// Nothing persists on the shared database; no database, schema or container is created outside
// the transaction. drizzle-kit qualifies foreign key targets as "public"; inside the check schema
// exactly these REFERENCES qualifiers are redirected (and counted), any other schema qualifier
// aborts the check, so no constraint can bind to a table of the shared public schema.
// Usage: node scripts/verify_drizzle_migrations_probe.cjs packages/audit-domain ...
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
  // Snapshot files carry the tag prefix: 0000_… (index) or 20261026061352_… (timestamp)
  const snapshotFile = path.join(dir, 'meta', `${last.tag.split('_')[0]}_snapshot.json`);
  const snapshot = JSON.parse(fs.readFileSync(snapshotFile, 'utf8'));
  return { migrations, snapshot };
}

const PUBLIC_REFERENCE = /REFERENCES "public"\./g;

function redirectToCheckSchema(statement) {
  const redirected = statement.replace(PUBLIC_REFERENCE, `REFERENCES "${CHECK_SCHEMA}".`);
  const qualified = redirected.replace(new RegExp(`"${CHECK_SCHEMA}"\.`, 'g'), '');
  if (/"[A-Za-z0-9_]+"\."/.test(qualified)) throw new Error(`unsupported schema qualifier in: ${statement.slice(0, 120)}`);
  return { sql: redirected, references: (statement.match(PUBLIC_REFERENCE) || []).length };
}

// Only spelling differences between drizzle snapshots and format_type()/pg_get_expr() are
// normalized: timestamp/time aliases, spaces in type modifiers and jsonb key order.
const normalizeType = (type) => type
  .replace(/^timestamp(\(\d+\))?$/, 'timestamp$1 without time zone')
  .replace(/^time(\(\d+\))?$/, 'time$1 without time zone')
  .replace(/^varchar/, 'character varying')
  .replace(/,\s+/g, ',');

const normalizeDefault = (value) => {
  if (value === undefined || value === null) return null;
  const text = String(value).replace(/::[a-z ]+(\[\])?/gi, '').replace(/^\((.*)\)$/, '$1').replace(/'/g, '').trim();
  try {
    const parsed = JSON.parse(text);
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      return JSON.stringify(Object.fromEntries(Object.keys(parsed).sort().map((k) => [k, parsed[k]])));
    }
  } catch { /* not JSON: keep the normalized text */ }
  return text;
};

function expectedCatalog(snapshot) {
  const tables = {};
  for (const table of Object.values(snapshot.tables)) {
    tables[table.name] = {
      columns: Object.fromEntries(Object.values(table.columns).map((c) => [c.name, {
        type: normalizeType(c.type), notNull: Boolean(c.notNull), primaryKey: Boolean(c.primaryKey), default: normalizeDefault(c.default),
      }])),
      indexes: Object.fromEntries(Object.values(table.indexes).map((i) => [i.name, {
        columns: i.columns.map((c) => c.expression).join(','), unique: Boolean(i.isUnique),
      }])),
      foreignKeys: Object.fromEntries(Object.values(table.foreignKeys || {}).map((f) => [f.name, {
        columns: f.columnsFrom.join(','), references: `${f.tableTo}(${f.columnsTo.join(',')})`,
        onDelete: (f.onDelete || 'no action').toLowerCase(), onUpdate: (f.onUpdate || 'no action').toLowerCase(),
      }])),
      uniqueConstraints: Object.fromEntries(Object.values(table.uniqueConstraints || {}).map((u) => [u.name, {
        columns: u.columns.join(','),
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
     WHERE n.nspname = $1 AND NOT i.indisprimary
       AND NOT EXISTS (SELECT 1 FROM pg_constraint k WHERE k.conindid = i.indexrelid)`, [CHECK_SCHEMA]);
  const constraints = await client.query(`
    SELECT t.relname AS table_name, k.conname, k.contype, rt.relname AS ref_table,
           k.confdeltype, k.confupdtype,
           (SELECT string_agg(a.attname, ',' ORDER BY c.ord) FROM unnest(k.conkey) WITH ORDINALITY c(attnum, ord)
              JOIN pg_attribute a ON a.attrelid = k.conrelid AND a.attnum = c.attnum) AS columns,
           (SELECT string_agg(a.attname, ',' ORDER BY c.ord) FROM unnest(k.confkey) WITH ORDINALITY c(attnum, ord)
              JOIN pg_attribute a ON a.attrelid = k.confrelid AND a.attnum = c.attnum) AS ref_columns,
           rn.nspname AS ref_schema
      FROM pg_constraint k JOIN pg_class t ON t.oid = k.conrelid JOIN pg_namespace n ON n.oid = t.relnamespace
      LEFT JOIN pg_class rt ON rt.oid = k.confrelid LEFT JOIN pg_namespace rn ON rn.oid = rt.relnamespace
     WHERE n.nspname = $1 AND k.contype IN ('f', 'u')`, [CHECK_SCHEMA]);
  const action = { a: 'no action', r: 'restrict', c: 'cascade', n: 'set null', d: 'set default' };
  const tables = {};
  for (const row of columns.rows) {
    tables[row.table_name] ??= { columns: {}, indexes: {}, foreignKeys: {}, uniqueConstraints: {} };
    tables[row.table_name].columns[row.column_name] = {
      type: normalizeType(row.type), notNull: row.not_null, primaryKey: row.primary_key, default: normalizeDefault(row.default_expr),
    };
  }
  const ensure = (name) => (tables[name] ??= { columns: {}, indexes: {}, foreignKeys: {}, uniqueConstraints: {} });
  for (const row of indexes.rows) {
    ensure(row.table_name).indexes[row.index_name] = { columns: row.columns, unique: row.is_unique };
  }
  for (const row of constraints.rows) {
    if (row.contype === 'f') {
      // A reference outside the check schema would mean the constraint bound to a shared table.
      const target = row.ref_schema === CHECK_SCHEMA ? row.ref_table : `${row.ref_schema}.${row.ref_table}`;
      ensure(row.table_name).foreignKeys[row.conname] = {
        columns: row.columns, references: `${target}(${row.ref_columns})`,
        onDelete: action[row.confdeltype], onUpdate: action[row.confupdtype],
      };
    } else {
      ensure(row.table_name).uniqueConstraints[row.conname] = { columns: row.columns };
    }
  }
  return tables;
}

function diffCatalog(expected, actual) {
  const problems = [];
  const keys = (a, b) => [...new Set([...Object.keys(a), ...Object.keys(b)])].sort();
  for (const table of keys(expected, actual)) {
    if (!expected[table] || !actual[table]) { problems.push(`table ${table}: ${expected[table] ? 'missing' : 'unexpected'}`); continue; }
    for (const kind of ['columns', 'indexes', 'foreignKeys', 'uniqueConstraints']) {
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
    let redirectedReferences = 0;
    for (const migration of migrations) {
      for (const statement of migration.statements) {
        const { sql, references } = redirectToCheckSchema(statement);
        await client.query(sql);
        statements += 1;
        redirectedReferences += references;
      }
    }
    const problems = diffCatalog(expectedCatalog(snapshot), await actualCatalog(client));
    return {
      pkg, migrations: migrations.map((m) => m.tag), statements, redirectedReferences,
      tables: Object.keys(snapshot.tables).length, problems,
    };
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

module.exports = { loadChain, expectedCatalog, diffCatalog, normalizeDefault, normalizeType, redirectToCheckSchema };
