// Offline functional checks for the Node security dependency wave.
// The stream-json (Detox) and Artillery checks were removed together with both
// dead tools and their local patches on 2026-10-25 (DEV-DEPENDENCY-SECURITY-20261025).
const assert = require('node:assert/strict');
const { test } = require('node:test');
const { createRequire } = require('node:module');
const path = require('node:path');
const root = path.resolve(__dirname, '..');

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
