// Real local HTTP redirects exercise upstream credential stripping.
const assert = require('node:assert/strict');
const { test } = require('node:test');
const http = require('node:http');
const path = require('node:path');
const { createRequire } = require('node:module');
const installed = createRequire(path.resolve(__dirname, '../node_modules/.pnpm/node_modules/package.json'));
const redirects = process.env.SECURITY_FOLLOW_REDIRECTS_RUNTIME
  ? require(path.resolve(process.env.SECURITY_FOLLOW_REDIRECTS_RUNTIME)) : installed('follow-redirects');

async function exchange(headers, sensitiveHeaders = [], sameOrigin = false) {
  const server = http.createServer((request, response) => {
    if (request.url === '/start') {
      response.writeHead(302, { location: sameOrigin ? '/result' : `http://destination.invalid:${server.address().port}/result` });
      response.end();
    } else response.end(JSON.stringify(request.headers));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  try {
    return await new Promise((resolve, reject) => {
      const request = redirects.http.get({ hostname: 'source.invalid', port: server.address().port,
        path: '/start', headers, sensitiveHeaders, agent: false,
        lookup: (_hostname, options, callback) => options.all
          ? callback(null, [{ address: '127.0.0.1', family: 4 }]) : callback(null, '127.0.0.1', 4),
      }, response => {
        let data = ''; response.on('data', chunk => { data += chunk; });
        response.on('end', () => { try { resolve(JSON.parse(data)); } catch (error) { reject(error); } });
      });
      request.on('error', reject);
      request.setTimeout(3000, () => request.destroy(new Error('Local redirect contract timed out')));
    });
  } finally { await new Promise(resolve => server.close(resolve)); }
}

for (const array of [false, true]) {
  test(`cross-origin strips standard and custom credentials (${array ? 'array' : 'object'})`, async () => {
    const entries = [['Authorization', 'synthetic'], ['Cookie', 'test=synthetic'],
      ['Proxy-Authorization', 'synthetic'], ['X-API-Key', 'synthetic'], ['Accept', 'application/json']];
    const result = await exchange(array ? entries.flat() : Object.fromEntries(entries), ['X-API-Key']);
    for (const key of ['authorization', 'cookie', 'proxy-authorization', 'x-api-key']) assert.equal(result[key], undefined, key);
    assert.equal(result.accept, 'application/json');
  });
}
for (const key of ['X-API^Key', 'X-Auth|Token']) {
  test(`custom credential header is escaped literally: ${key}`, async () => {
    const result = await exchange({ [key]: 'synthetic', Accept: 'application/json' }, [key.toLowerCase()]);
    assert.equal(result[key.toLowerCase()], undefined);
    assert.equal(result.accept, 'application/json');
  });
}
test('same-origin credentials and normal headers remain usable', async () => {
  const result = await exchange({ Authorization: 'synthetic', 'X-API^Key': 'synthetic', Accept: 'application/json' }, ['X-API^Key'], true);
  assert.equal(result.authorization, 'synthetic');
  assert.equal(result['x-api^key'], 'synthetic');
  assert.equal(result.accept, 'application/json');
});
