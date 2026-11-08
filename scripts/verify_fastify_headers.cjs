// GHSA-389g-gv7q-r4x8: normalized header-name deny-lists must reach validation.
const assert = require('node:assert/strict');
const { test } = require('node:test');
const { createRequire } = require('node:module');
const path = require('node:path');
const runtime = process.env.SECURITY_FASTIFY_RUNTIME || path.resolve(__dirname, '../node_modules/.pnpm/node_modules');
const installed = createRequire(path.join(path.resolve(runtime), 'package.json'));
const fastify = installed('fastify');

for (const constraint of [{ enum: ['X-Debug-Override'] }, { const: 'X-Debug-Override' }]) {
  test(`reject mixed-case header constraints: ${JSON.stringify(constraint)}`, async () => {
    const app = fastify();
    let executed = 0;
    app.get('/probe', { schema: { headers: { type: 'object', propertyNames: { not: constraint } } } }, () => {
      executed++;
      return { ok: true };
    });
    try {
      for (const header of ['X-Debug-Override', 'x-debug-override']) {
        const response = await app.inject({ url: '/probe', headers: { [header]: 'enabled' } });
        assert.equal(response.statusCode, 400);
      }
      assert.equal(executed, 0, 'Rejected headers must never reach the handler');
      const allowed = await app.inject({ url: '/probe', headers: { 'X-Order-Source': 'portal' } });
      assert.equal(allowed.statusCode, 200);
      assert.equal(executed, 1);
    } finally {
      await app.close();
    }
  });
}
