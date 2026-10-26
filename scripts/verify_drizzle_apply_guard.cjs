// Offline checks for the migrate:apply preflight decision (scripts/drizzle_apply_guard.cjs).
const assert = require('node:assert/strict');
const { test } = require('node:test');
const { classify } = require('./drizzle_apply_guard.cjs');

const chainTables = ['audit_events', 'export_jobs'];

test('an empty schema is migrated fresh', () => {
  assert.deepEqual(classify({ chainTables, schemaTables: [], journalExists: false }), { ok: true, reason: 'fresh', detail: [] });
});

test('a schema with journal is migrated incrementally', () => {
  const verdict = classify({ chainTables, schemaTables: ['audit_events'], journalExists: true });
  assert.equal(verdict.ok, true);
  assert.equal(verdict.reason, 'incremental');
});

test('the backend database is refused through alembic_version', () => {
  const verdict = classify({ chainTables, schemaTables: ['alembic_version'], journalExists: false });
  assert.equal(verdict.ok, false);
  assert.equal(verdict.reason, 'foreign-target');
});

test('foreign tables are refused even with a journal', () => {
  const verdict = classify({ chainTables, schemaTables: ['audit_events', 'documents'], journalExists: true });
  assert.equal(verdict.ok, false);
  assert.deepEqual(verdict.detail, ['documents']);
});

test('chain tables without journal stop for reconciliation', () => {
  const verdict = classify({ chainTables, schemaTables: ['export_jobs'], journalExists: false });
  assert.equal(verdict.ok, false);
  assert.equal(verdict.reason, 'unjournaled-tables');
  assert.deepEqual(verdict.detail, ['export_jobs']);
});
