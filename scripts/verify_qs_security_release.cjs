'use strict';

// Pass the absolute path to the qs package directory or entry point under test.
// Cases derived from upstream fix a952e7519338ef0cfb25694a2988848f93333727.
const assert = require('node:assert/strict');
const path = require('node:path');
const { test } = require('node:test');

const { createRequire } = require('node:module');
const installed = createRequire(path.resolve(__dirname, '../node_modules/.pnpm/node_modules/package.json'));
const qs = process.env.SECURITY_QS_RUNTIME ? require(path.resolve(process.env.SECURITY_QS_RUNTIME)) : installed('qs');
const comma = { arrayFormat: 'comma' };

test('JSON object with non-callable toString serializes under both encoding paths', () => {
  const value = JSON.parse('{"a":["b",{"toString":"x"},"c"]}');
  assert.equal(qs.stringify(value, comma), 'a=b%2C%5Bobject%20Object%5D%2Cc');
  assert.equal(qs.stringify(value, { ...comma, encodeValuesOnly: true }), 'a=b,%5Bobject%20Object%5D,c');
});

test('parsed untrusted prototype keys and null-prototype entries serialize', () => {
  const prototypeKey = qs.parse('a[0][toString]=x', { allowPrototypes: true });
  const nullPrototype = qs.parse('a[][b]=c', { plainObjects: true });
  assert.equal(qs.stringify(prototypeKey, comma), 'a=%5Bobject%20Object%5D');
  assert.equal(qs.stringify(nullPrototype, comma), 'a=%5Bobject%20Object%5D');
  assert.equal(qs.stringify(nullPrototype, { ...comma, encodeValuesOnly: true }), 'a=%5Bobject%20Object%5D');
});

test('nested attacker-controlled arrays retain join semantics', () => {
  const value = JSON.parse('{"a":[[1,[{"toString":"x"}]],"y"]}');
  assert.equal(qs.stringify(value, { ...comma, encode: false }), 'a=1,[object Object],y');
  assert.equal(qs.stringify(value, { ...comma, encodeValuesOnly: true }), 'a=1%2C%5Bobject%20Object%5D,y');
});

test('normal comma serialization and explicit user errors remain intact', () => {
  assert.equal(qs.stringify({ a: ['one', 'two words'] }, comma), 'a=one%2Ctwo%20words');
  assert.equal(qs.stringify({ a: [{ toString: 'x', valueOf: () => 7 }] }, comma), 'a=7');
  assert.throws(() => qs.stringify({ a: [{ toString() { throw new SyntaxError('mine'); } }] }, comma), SyntaxError);
});
