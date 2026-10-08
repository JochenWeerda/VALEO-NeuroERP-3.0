// Offline security behavior contracts; no real HTTP or database connection.
const assert = require('node:assert/strict');
const { test } = require('node:test');
const { createRequire } = require('node:module');
const path = require('node:path');
// Global overrides give each affected package one patched pnpm resolution.
// An explicit isolated runtime allows offline checks without changing shared modules.
const runtime = process.env.SECURITY_NODE_RUNTIME
  ? path.resolve(process.env.SECURITY_NODE_RUNTIME)
  : path.resolve(__dirname, '../node_modules/.pnpm/node_modules');
const patched = createRequire(path.join(runtime, 'package.json'));

test('fast-copy bounds nesting and still copies cyclic business records', () => {
  const { default: copy, copyStrict, MaxDepthExceededError } = patched('fast-copy');
  const record = { id: 'test', values: [1, 2] }; record.self = record;
  const result = copy(record);
  assert.notEqual(result, record);
  assert.equal(result.self, result);
  assert.deepEqual(result.values, record.values);
  let deep = {};
  for (let i = 0; i < 1200; i++) deep = { child: deep };
  for (const clone of [copy, copyStrict]) assert.throws(() => clone(deep), MaxDepthExceededError);
});

test('translation backend rejects injected URL schemes before requesting', async () => {
  const Backend = patched('i18next-http-backend');
  const requests = [];
  const backend = new Backend({ interpolator: { interpolate: (template, vars) =>
    template.replace(/\{\{(lng|ns)\}\}/g, (_, key) => vars[key]) } }, {
    loadPath: '{{lng}}/{{ns}}.json',
    request: (_options, url, _payload, done) => {
      requests.push(url); done(null, { status: 200, data: '{}' });
    },
  });
  const read = (lng, ns) => new Promise(resolve => backend.read(lng, ns, (error) => resolve(error)));
  for (const [lng, ns] of [['http:127.0.0.1:1', 'common'], ['de', '//evil.invalid/x'], ['de', 'http:evil']]) {
    assert.ok(await read(lng, ns));
  }
  assert.deepEqual(requests, []);
  assert.equal(await read('de', 'common'), null);
  assert.deepEqual(requests, ['de/common.json']);
});

test('multipart never forwards bare CR or LF in names or filenames', async () => {
  const Busboy = patched('@fastify/busboy');
  for (const control of ['\r', '\n']) {
    const names = [];
    const parser = new Busboy({ headers: { 'content-type': 'multipart/form-data; boundary=test' } });
    parser.on('file', (name, stream, filename) => { names.push(name, filename); stream.resume(); });
    parser.on('field', name => names.push(name));
    await new Promise((resolve, reject) => {
      parser.on('finish', resolve); parser.on('error', reject);
      parser.end(`--test\r\nContent-Disposition: form-data; name="field${control}bad"; filename="file${control}bad.txt"\r\n\r\nhello\r\n--test--\r\n`);
    });
    for (const name of names) assert.ok(!/[\r\n]/.test(name));
  }
  const names = [];
  const parser = new Busboy({ headers: { 'content-type': 'multipart/form-data; boundary=test' } });
  parser.on('file', (name, stream, filename) => { names.push(name, filename); stream.resume(); });
  await new Promise((resolve, reject) => {
    parser.on('finish', resolve); parser.on('error', reject);
    parser.end('--test\r\nContent-Disposition: form-data; name="upload"; filename="normal.txt"\r\n\r\nhello\r\n--test--\r\n');
  });
  assert.deepEqual(names, ['upload', 'normal.txt']);
});

test('joi retains strict business input validation', () => {
  const Joi = patched('joi');
  const schema = Joi.object({ tenant: Joi.string().uuid().required(), amount: Joi.number().positive().required() });
  assert.equal(schema.validate({ tenant: '00000000-0000-4000-8000-000000000071', amount: 1 }).error, undefined);
  assert.ok(schema.validate({ tenant: 'invalid', amount: -1 }).error);
  assert.throws(() => Joi.any().messages(JSON.parse('{"__proto__":"forged"}')), /Cannot use __proto__/);
  assert.throws(() => Joi.any().messages(JSON.parse('{"de":{"__proto__":"forged"}}')), /Cannot use __proto__/);
  assert.equal({}.polluted, undefined);
});

test('PostgreSQL query telemetry omits credentials and retains stable database attributes', () => {
  const utils = patched('@opentelemetry/instrumentation-pg/build/src/utils.js');
  const attributes = {};
  const tracer = { startSpan: (_name, options) => {
    Object.assign(attributes, options.attributes);
    return { setAttribute: (name, value) => { attributes[name] = value; } };
  } };
  utils.handleConfigQuery.call({ database: 'probe', connectionParameters: {
    host: 'localhost', port: 5432, database: 'probe', user: 'private-user', password: 'private-password',
  } }, tracer, {}, { text: 'SELECT 1' });
  assert.equal(attributes['db.user'], undefined);
  assert.ok(!JSON.stringify(attributes).includes('private-user'));
  assert.ok(!JSON.stringify(attributes).includes('private-password'));
  assert.equal(attributes['db.namespace'], 'probe');
  assert.equal(attributes['server.address'], 'localhost');
  assert.equal(attributes['db.query.text'], 'SELECT 1');
});

test('all eight database instrumentations retain their public constructors', () => {
  for (const [name, constructor] of [
    ['pg', 'PgInstrumentation'], ['mysql2', 'MySQL2Instrumentation'],
    ['knex', 'KnexInstrumentation'], ['mysql', 'MySQLInstrumentation'],
    ['mongoose', 'MongooseInstrumentation'], ['oracledb', 'OracleInstrumentation'],
    ['tedious', 'TediousInstrumentation'], ['cassandra-driver', 'CassandraDriverInstrumentation'],
  ]) {
    const Type = patched(`@opentelemetry/instrumentation-${name}`)[constructor];
    const instance = new Type({ enabled: false });
    assert.equal(instance.isEnabled(), false);
  }
});

// Keep parser backport regressions in the existing CI security entry point.
require('./verify_node_dependency_security.cjs');
require('./verify_node_high_backports.cjs');
require('./test_npm_backport_audit.cjs');
require('./verify_handlebars_security_release.cjs');
