// Vendor release regressions: local markers only, no subprocess or network.
const assert = require('node:assert/strict');
const { test } = require('node:test');
const { createRequire } = require('node:module');
const path = require('node:path');
const vm = require('node:vm');
const runtime = process.env.SECURITY_HANDLEBARS_RUNTIME
  ? path.resolve(process.env.SECURITY_HANDLEBARS_RUNTIME)
  : path.resolve(__dirname, '../node_modules/.pnpm/node_modules');
const load = createRequire(path.join(runtime, 'package.json'));
const Handlebars = load('handlebars');

test('handlebars preserves ordinary escaped business fields', () => {
  assert.equal(Handlebars.compile('Hello {{name}}')({ name: '<VALEO>' }), 'Hello &lt;VALEO&gt;');
});

test('handlebars preserves normal block parameters and precompiled rendering', () => {
  const ast = Handlebars.parse('{{#each rows as |row|}}{{row.name}}{{/each}}');
  const expected = 'AB';
  assert.equal(Handlebars.compile(ast)({ rows: [{ name: 'A' }, { name: 'B' }] }), expected);
  const specification = vm.runInNewContext(`(${Handlebars.precompile(ast)})`);
  assert.equal(Handlebars.template(specification)({ rows: [{ name: 'A' }, { name: 'B' }] }), expected);
});

test('handlebars preserves safe own-property lookups', () => {
  const context = Object.create(null); context.name = 'Customer';
  assert.equal(Handlebars.compile('{{lookup customer "name"}}')({ customer: context }), 'Customer');
});

test('handlebars rejects AST block parameter type confusion before code execution', () => {
  const marker = '__valeoHandlebarsAstMarker';
  try {
    for (const operation of ['compile', 'precompile']) {
      delete global[marker];
      const ast = Handlebars.parse('{{#missingHelper}}value{{/missingHelper}}');
      ast.body[0].program.blockParams = {
        length: `(()=>{global.${marker}=true;return 0})()`,
      };
      let failure;
      try {
        const result = Handlebars[operation](ast);
        if (operation === 'compile') result({});
      } catch (error) { failure = error; }
      assert.equal(global[marker], undefined, 'Untrusted AST executed an injected expression');
      assert.ok(failure, 'Invalid AST must be rejected before compilation');
    }
  } finally { delete global[marker]; }
});

test('handlebars does not expose Function through prototype own constructor', () => {
  const template = Handlebars.compile('{{lookup (lookup fn "__proto__") "constructor"}}');
  assert.equal(template({ fn() {} }, { allowProtoMethodsByDefault: true }), '');
});

test('handlebars precompiled text cannot terminate an inline script element', () => {
  for (const content of ['safe</script><script>local-marker</script>', 'safe</ScRiPt>']) {
    const compiled = Handlebars.precompile(content);
    assert.equal(/<\/script/i.test(compiled), false);
    const specification = vm.runInNewContext(`(${compiled})`);
    assert.equal(Handlebars.template(specification)({}), content);
  }
});
