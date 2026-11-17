// Runtime contract for the local picomatch 4.0.7 source repair (GHSA-fc5q-39xc-vjpf, no vendor release).
// A repeated extglob (`+(...)`, `*(...)`) whose branch nests an unbounded `*` next to other content compiles to a
// nested quantifier that backtracks exponentially. The repair treats such a pattern literally (picomatch's own
// "risky" fallback); ordinary globs and safe extglobs keep their behavior.
const assert = require('node:assert/strict');
const { test } = require('node:test');
const path = require('node:path');
const { resolveExactPackage } = require('./check_npm_backport_audit.cjs');

const packageDir = process.env.SECURITY_PICOMATCH_RUNTIME
  ? path.resolve(process.env.SECURITY_PICOMATCH_RUNTIME)
  : path.dirname(resolveExactPackage(path.resolve(__dirname, '..'), 'picomatch', '4.0.7'));
const picomatch = require(packageDir);

function millis(fn) {
  const start = process.hrtime.bigint();
  fn();
  return Number(process.hrtime.bigint() - start) / 1e6;
}

const hostile = [
  ['+(*a)', 'a'.repeat(40) + '!'],
  ['+(*a|b)', 'a'.repeat(40) + '!'],
  ['+(a*)', 'a'.repeat(40) + '/'],
  ['*(a*|b)', 'ab'.repeat(30) + '/'],
  ['+(a*?)', 'a'.repeat(40) + '/'],
  ['+(\\x*a)', 'xa'.repeat(30) + '!'],
];

for (const [pattern, input] of hostile) {
  test(`${pattern} answers in bounded time on a near miss`, () => {
    const matcher = picomatch(pattern);
    assert.ok(millis(() => matcher(input)) < 250, pattern);
  });
}

test('a risky repeated extglob matches only its literal text', () => {
  assert.equal(picomatch.isMatch('aaa', '+(*a)'), false);
  assert.equal(picomatch.isMatch('+(*a)', '+(*a)'), true);
});

test('ordinary globs and safe extglobs keep their behavior', () => {
  const cases = [
    ['src/app.js', 'src/*.js', true], ['src/app.ts', 'src/*.js', false],
    ['a/b/c.js', '**/*.js', true], ['ab', '+(a|b)', true], ['abc', '+(a|b)', false],
    ['xa', '@(*a)', true], ['xb', '!(*a)', true], ['xa', '!(*a)', false],
    ['aab', '+(*(a)|*(b))', true], ['x', '+(*)', true], ['foo.md', '*.{md,txt}', true],
  ];
  for (const [input, pattern, expected] of cases) {
    assert.equal(picomatch.isMatch(input, pattern), expected, `${input} ~ ${pattern}`);
  }
});

test('maxExtglobRecursion false keeps the unrepaired upstream behavior available on request', () => {
  assert.equal(picomatch.isMatch('aaa', '+(*a)', { maxExtglobRecursion: false }), true);
});
