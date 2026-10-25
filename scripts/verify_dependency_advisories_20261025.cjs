// Offline behaviour contracts for the 2026-10-23 advisory cohort (body-parser,
// nodemailer, fast-uri, zod). Each case is the advisory's own proof of concept,
// paired with a normal input that must keep working. Local loopback HTTP only.
const assert = require('node:assert/strict');
const { test } = require('node:test');
const { createRequire } = require('node:module');
const http = require('node:http');
const zlib = require('node:zlib');
const path = require('node:path');
const runtime = process.env.SECURITY_NODE_RUNTIME
  ? path.resolve(process.env.SECURITY_NODE_RUNTIME)
  : path.resolve(__dirname, '../node_modules/.pnpm/node_modules');
const patched = createRequire(path.join(runtime, 'package.json'));

// Posts gzip JSON followed by 100 KiB of trailing bytes. Before 1.20.9 the finished
// decoder emitted an error without a listener and took the whole process down.
async function postGzipWithTrailingBytes(options, contentType) {
  const bodyParser = patched('body-parser');
  const jsonParser = bodyParser.json(options);
  const uncaught = [];
  const onUncaught = (error) => uncaught.push(error);
  process.prependListener('uncaughtException', onUncaught);
  const server = http.createServer((req, res) => jsonParser(req, res, (error) => {
    res.statusCode = error ? error.status || 500 : 200;
    res.end(error ? error.type || error.message : JSON.stringify(req.body));
  }));
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  try {
    const body = Buffer.concat([zlib.gzipSync('{"a":1}'), Buffer.from([0x00]), Buffer.alloc(100 * 1024, 0x58)]);
    const result = await new Promise((resolve, reject) => {
      const req = http.request({ host: '127.0.0.1', port: server.address().port, method: 'POST',
        headers: { 'Content-Type': contentType, 'Content-Encoding': 'gzip', 'Content-Length': body.length } },
      (res) => { let data = ''; res.setEncoding('utf8'); res.on('data', c => { data += c; }); res.on('end', () => resolve({ status: res.statusCode, data })); });
      req.on('error', reject);
      req.setTimeout(3000, () => req.destroy(new Error('request did not finish')));
      req.end(body);
    });
    await new Promise(resolve => setTimeout(resolve, 200));
    return { ...result, uncaught: uncaught.map(error => error.code || error.message) };
  } finally {
    process.removeListener('uncaughtException', onUncaught);
    await new Promise(resolve => server.close(resolve));
  }
}

test('body-parser survives trailing bytes after a gzip body (GHSA-27r3-jxmh-p828)', { timeout: 10000 }, async () => {
  assert.deepEqual(await postGzipWithTrailingBytes({}, 'application/json'),
    { status: 200, data: '{"a":1}', uncaught: [] });
});

test('body-parser rejects an unsupported charset of a compressed body without crashing', { timeout: 10000 }, async () => {
  assert.deepEqual(await postGzipWithTrailingBytes({ verify() {} }, 'application/json; charset=utf-999'),
    { status: 415, data: 'charset.unsupported', uncaught: [] });
});

test('nodemailer addressparser keeps comments, groups and quoted local parts intact', () => {
  const parse = patched('nodemailer/lib/addressparser');
  const recipients = (value) => {
    const flat = [];
    for (const entry of parse(value)) for (const item of entry.group || [entry]) flat.push(item.address);
    return flat;
  };
  // GHSA-8c8m-p3m8-cjg8: nested comment must not release <evil@evil.com>
  assert.deepEqual(recipients('Victim (x(y) <evil@evil.com>) <v@victim.com>'), ['v@victim.com']);
  // GHSA-m943-m63m-w62w: ";" inside a comment or quoted display name does not end the group
  assert.deepEqual(recipients('G: (a; <evil@evil.com>) <v@victim.com>;'), ['v@victim.com']);
  assert.deepEqual(recipients('G: "a;" "<evil@evil.com>" <v@victim.com>;'), ['v@victim.com']);
  // GHSA-85x2-q946-cp5h: ">" inside a quoted local part does not end the angle-addr
  for (const address of recipients('<"a@evil.com>"@good.com>')) assert.ok(!/@evil\.com$/.test(address));
  // Normal business recipients still parse unchanged
  assert.deepEqual(recipients('Buchhaltung <buchhaltung@example.de>, lager@example.de'),
    ['buchhaltung@example.de', 'lager@example.de']);
});

test('fast-uri rejects encoded schemes, host smuggling and dot-segment rewriting', () => {
  const uri = patched('fast-uri');
  // A rejection may be a thrown parse error or a harmless value; never the dangerous one.
  const notProducing = (dangerous, call) => {
    let value;
    try { value = call(); } catch { return; }
    assert.notDeepEqual(value, dangerous);
  };
  // GHSA-w74x-v6f9-j3xg: a percent-encoded scheme must not become a live scheme
  notProducing('javascript:alert(1)', () => uri.normalize('%6Aavascript:alert(1)'));
  notProducing('javascript:alert(1)', () => uri.resolve('https://a.example/', '%6Aavascript:alert(1)'));
  notProducing('javascript', () => uri.parse('%6Aavascript:alert(1)').scheme);
  notProducing(true, () => uri.equal('%68ttp://a/', 'http://a/'));
  // GHSA-wjr9-j795-jxcr: the reported host must not be silently rewritten
  const smuggled = uri.parse('http://a@b@evil.example/');
  assert.ok(smuggled.error || smuggled.host !== 'evil.example');
  assert.equal(uri.equal('http://ev\til.example/', 'http://evil.example/'), false);
  // GHSA-xhq7-xmqj-769h: relative references keep their leading dot segments
  assert.notEqual(uri.normalize('a/../b'), '/b');
  assert.notEqual(uri.normalize('../x'), 'x');
  // GHSA-333x-w4r6-6crp: suffix serialization escapes a first-segment colon
  const suffix = { reference: 'suffix', scheme: 'x' };
  for (const input of ['javascript:alert(1)', '%6Aavascript:alert(1)', 'data:text/html,x']) {
    notProducing(true, () => /^(?:javascript|data|vbscript):/i.test(uri.normalize(input, suffix)));
  }
  assert.equal(uri.normalize('path/to/file', suffix), 'path/to/file');
  // Normal API URLs keep working
  assert.equal(uri.normalize('HTTPS://Example.DE:443/api/v1/artikel?x=1'), 'https://example.de/api/v1/artikel?x=1');
  assert.equal(uri.resolve('https://erp.example/api/v1/', 'kunden/42'), 'https://erp.example/api/v1/kunden/42');
});

test('zod rejects an oversized bounded array before walking its elements (GHSA-mrhx-c7xc-m3w5)', () => {
  const { z } = patched('zod');
  assert.match(patched('zod/package.json').version, /^4\./);
  const schema = z.array(z.string().guid()).max(100);
  const result = schema.safeParse(Array(50000).fill(0));
  assert.equal(result.success, false);
  // compare the count first: a failing deepEqual over 50k issues would hang the diff
  assert.equal(result.error.issues.length, 1);
  assert.equal(result.error.issues[0].code, 'too_big');
  // zod 3 uuid() semantics are kept through guid(): the system tenant id stays valid
  assert.equal(z.string().guid().safeParse('00000000-0000-0000-0000-000000000001').success, true);
  assert.equal(schema.safeParse(['550e8400-e29b-41d4-a716-446655440000']).success, true);
  assert.equal(schema.safeParse(['no-id']).success, false);
  // zod 3 .default() on a transform/object was parsed; the migrated prefault() keeps that
  const query = z.object({
    page: z.string().transform(Number).optional().prefault('1'),
    days: z.object({ mon: z.boolean().default(true), sun: z.boolean().default(false) }).prefault({}),
  });
  assert.deepEqual(query.parse({}), { page: 1, days: { mon: true, sun: false } });
  assert.deepEqual(query.parse({ page: '3' }), { page: 3, days: { mon: true, sun: false } });
});
