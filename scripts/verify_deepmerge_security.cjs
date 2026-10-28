const assert = require('node:assert/strict');
const { test } = require('node:test');
const { resolveExactPackage } = require('./check_npm_backport_audit.cjs');
const path = require('node:path');
const fs = require('node:fs');
const vm = require('node:vm');
const packageDir = process.env.SECURITY_DEEPMERGE_RUNTIME ? path.resolve(process.env.SECURITY_DEEPMERGE_RUNTIME) : path.dirname(resolveExactPackage(path.resolve(__dirname, '..'), 'deepmerge', '4.3.1'));
const browser = {};
vm.runInNewContext(fs.readFileSync(path.join(packageDir, 'dist/umd.js'), 'utf8'), browser);
const entries = { cjs: require(path.join(packageDir, 'dist/cjs.js')), umd: require(path.join(packageDir, 'dist/umd.js')), browser: browser.deepmerge };
for (const [entryName, merge] of Object.entries(entries)) {
const ordinaryPrototype = Object.getPrototypeOf(merge({}, {}));
const check = (name, fn) => test(entryName + ': ' + name, fn);
const hostile = () => JSON.parse('{"__proto__":{"inherited_access":true},"ordinary":1}');
function clean(value) {
  assert.equal(Object.getPrototypeOf(value), ordinaryPrototype);
  assert.equal(value.inherited_access, undefined);
  assert.equal(Object.hasOwn(value, '__proto__'), false);
  assert.equal(Object.prototype.inherited_access, undefined);
}

check('target JSON cannot poison the returned prototype', () => {
  const result = merge(hostile(), { other: 2 }); clean(result);
  assert.equal(result.ordinary, 1); assert.equal(result.other, 2);
});
check('a null-prototype target cannot bypass source-key protection', () => {
  const result = merge(Object.create(null), hostile()); clean(result);
  assert.equal(result.ordinary, 1);
});
check('both untrusted inputs remain safe', () => { clean(merge(hostile(), hostile())); });
check('nested target objects cannot poison their returned prototype', () => {
  const result = merge({ options: hostile() }, { options: { extra: 2 } });
  clean(result); clean(result.options); assert.equal(result.options.extra, 2);
});
check('nested arrays clone hostile objects safely', () => {
  const result = merge({ list: [hostile()] }, { list: [{ value: 2 }] });
  clean(result.list[0]); assert.equal(result.list[1].value, 2);
});
check('ordinary nested values, symbols and arrays keep their merge behavior', () => {
  const key = Symbol('metadata');
  const first = { settings: { a: 1 }, list: [1], [key]: { left: true } };
  const result = merge(first, { settings: { b: 2 }, list: [2], [key]: { right: true } });
  assert.equal(JSON.stringify(result.settings), JSON.stringify({ a: 1, b: 2 }));
  assert.deepEqual(Array.from(result.list), [1, 2]);
  assert.equal(JSON.stringify(result[key]), JSON.stringify({ left: true, right: true }));
  assert.notEqual(result.settings, first.settings);
});
check('custom merge and array options retain their behavior', () => {
  const result = merge({ labels: {value: 'a'}, list: [1] }, { labels: {value: 'b'}, list: [2] }, {
    customMerge: key => key === 'labels' ? (a, b) => ({value: a.value + b.value}) : undefined,
    arrayMerge: (a, b) => [...b, ...a],
  });
  assert.deepEqual(JSON.parse(JSON.stringify(result)), { labels: {value: 'ab'}, list: [2, 1] });
});

}
