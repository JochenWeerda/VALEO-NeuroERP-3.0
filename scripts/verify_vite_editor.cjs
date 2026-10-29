// Test the installed Vite bundle's editor guards without launching a shell/editor.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { test } = require('node:test');
const { createRequire } = require('node:module');
const installed = createRequire(path.resolve(__dirname, '../node_modules/.pnpm/node_modules/package.json'));
const root = process.env.SECURITY_VITE_RUNTIME || path.dirname(installed.resolve('vite/package.json'));
const chunks = path.join(root, 'dist/node/chunks');
const bundle = fs.readdirSync(chunks).filter(file => file.endsWith('.js'))
  .map(file => fs.readFileSync(path.join(chunks, file), 'utf8'))
  .find(code => code.includes('function escapeCmdArgs('));
assert.ok(bundle, 'Installed Vite editor implementation must be inspectable');
function section(start, end) {
  const from = bundle.indexOf(start), to = bundle.indexOf(end, from);
  assert.ok(from >= 0 && to > from, 'Installed editor source boundaries changed; review required');
  return bundle.slice(from, to);
}
const construct = vm.runInNewContext(section('function escapeCmdArgs(', 'var constructWindowsLaunchCommand_1') + '; constructWindowsLaunchCommand$1;');
const getArgs = vm.runInNewContext(section('var getArgs = function', '// On Windows, we need') + '; getArgs;', {
  path$6: path.win32, os: {release: () => ''}, process: {platform:'win32', env:{}},
});
for (const value of ['C:\\project\\%VAR:old=new%\\..', 'C:\\project\\file\r\nsynthetic']) {
  test(`Windows command rejects unsafe expansion/separator ${JSON.stringify(value)}`, () => {
    assert.throws(() => construct('code', [value]), /Cannot launch an editor/);
  });
}
for (const name of ['--cmd=synthetic', '+synthetic']) {
  test(`Editor filename is an absolute path rather than a CLI flag: ${name}`, () => {
    const args = getArgs('vim', name);
    assert.ok(path.win32.isAbsolute(args[0]));
    assert.equal(path.win32.basename(args[0]), name);
  });
}
test('Normal Windows paths and editor line/column mapping remain usable', () => {
  assert.equal(construct('code', ['C:\\project\\file.ts']), 'code C:\\project\\file.ts');
  const args = getArgs('code', 'C:\\project\\file.ts', '12', '3');
  assert.deepEqual(Array.from(args), ['-r','-g','C:\\project\\file.ts:12:3']);
});
