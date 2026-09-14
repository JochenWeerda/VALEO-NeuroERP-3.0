// Offline functional checks for the Node security dependency wave.
const assert = require('node:assert/strict');
const { test } = require('node:test');
const { createRequire } = require('node:module');
const { Readable, Writable } = require('node:stream');
const { pipeline } = require('node:stream/promises');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const mobile = createRequire(path.join(root, 'packages/mobile-app/package.json'));
const detox = createRequire(mobile.resolve('detox/package.json'));
const json = process.env.STREAM_JSON_TEST_ROOT
  ? createRequire(path.resolve(process.env.STREAM_JSON_TEST_ROOT, 'package.json'))
  : createRequire(detox.resolve('stream-json/package.json'));

async function collect(source, ...transforms) {
  const result = [];
  await pipeline(Readable.from([source]), ...transforms,
    new Writable({ objectMode: true, write(value, _, next) { result.push(value); next(); } }));
  return result;
}

test('legacy stream-array consumer preserves all records', async () => {
  const values = await collect('[{"id":1},{"id":2}]', json('./streamers/StreamArray').withParser());
  assert.deepEqual(values.map(row => row.value.id), [1, 2]);
});

for (const name of ['Pick', 'Ignore', 'Filter', 'Replace']) {
  test(`${name} rejects excessive unmatched nesting`, async () => {
    const doc = '{"meta":'.repeat(1100) + '1' + '}'.repeat(1100);
    await assert.rejects(collect(doc, json('./index')(), new (json(`./filters/${name}`))({ filter: 'data' })),
      { name: 'RangeError', message: /nesting depth/ });
  });
}

test('ordinary path extraction remains usable', async () => {
  const tokens = await collect('{"meta":0,"data":42}', json('./index')(), new (json('./filters/Pick'))({ filter: 'data' }));
  assert.ok(tokens.some(token => token.name === 'numberValue' && token.value === '42'));
});

if (!process.env.STREAM_JSON_TEST_ROOT) {
  test('procurement image processing and seeded test data remain usable', async () => {
    const procurement = createRequire(path.join(root, 'packages/procurement-domain/package.json'));
    const sharp = procurement('sharp');
    const png = await sharp({ create: { width: 2, height: 2, channels: 3, background: '#123456' } }).png().toBuffer();
    const metadata = await sharp(png).metadata();
    assert.equal(metadata.format, 'png');
    assert.equal(metadata.width, 2);
    const { faker } = procurement('@faker-js/faker');
    faker.seed(42);
    const first = faker.person.fullName();
    faker.seed(42);
    assert.equal(faker.person.fullName(), first);
    assert.ok(first.length > 0);
  });

  test('Artillery prepares a real CSV payload without sending requests', async () => {
    const artillery = createRequire(path.join(root, 'packages/analytics-domain/node_modules/artillery/package.json'));
    const prepare = artillery('./lib/util/prepare-test-execution-plan');
    const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'valeo-csv-check-'));
    try {
      const csv = path.join(temp, 'payload.csv');
      const config = path.join(temp, 'scenario.json');
      fs.writeFileSync(csv, '"Test, Betrieb",42\n');
      fs.writeFileSync(config, JSON.stringify({ config: {
        target: 'http://127.0.0.1:1', phases: [{ duration: 1, arrivalCount: 1 }],
        payload: { path: csv, fields: ['name', 'amount'] }
      }, scenarios: [{ flow: [{ get: { url: '/' } }] }] }));
      const plan = await prepare([config], {}, {});
      assert.deepEqual(plan.config.payload[0].data, [['Test, Betrieb', 42]]);
    } finally {
      assert.equal(path.dirname(path.resolve(temp)), path.resolve(os.tmpdir()));
      assert.ok(path.basename(temp).startsWith('valeo-csv-check-'));
      fs.rmSync(temp, { recursive: true, force: true });
    }
  });
}
