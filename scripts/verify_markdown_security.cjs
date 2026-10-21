// Bounded rendering of pathological inputs; no unbounded event-loop blocking.
const assert = require('node:assert/strict');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { createRequire } = require('node:module');
const installed = createRequire(path.resolve(__dirname, '../node_modules/.pnpm/node_modules/package.json'));

if (process.argv[2] === '--case') {
  const MarkdownIt = require(process.argv[4]);
  const variant = process.argv[3];
  let input, options = {};
  if (variant === 'reference-title') input = '[a]: /u "' + 'x\n'.repeat(200000);
  else if (variant === 'reference-label') input = '[' + 'a\n'.repeat(25000);
  else if (variant === 'smartquotes') {
    options = { typographer: true };
    input = '"a '.repeat(128000) + "b' ".repeat(128000);
  } else {
    options = { html: true };
    const openers = { comment: '<!--', processing: '<?x', declaration: '<!A', cdata: '<![CDATA[' };
    assert.ok(Object.hasOwn(openers, variant));
    input = 'x ' + openers[variant].repeat(128000);
  }
  const output = new MarkdownIt(options).render(input);
  assert.ok(typeof output === 'string' && output.length > 0);
  process.stdout.write(JSON.stringify({ inputBytes: Buffer.byteLength(input), outputLength: output.length }));
} else {
  const { test } = require('node:test');
  const root = process.env.SECURITY_MARKDOWN_RUNTIME || path.dirname(installed.resolve('markdown-it/package.json'));
  const MarkdownIt = require(root);
  test('Headings, references, typography and HTML policy remain usable', () => {
    assert.equal(new MarkdownIt().render('# Heading'), '<h1>Heading</h1>\n');
    assert.equal(new MarkdownIt().render('[id]: /ok "Title"\n\n[id]'), '<p><a href="/ok" title="Title">id</a></p>\n');
    assert.equal(new MarkdownIt({typographer:true}).render('"hello"'), '<p>“hello”</p>\n');
    assert.equal(new MarkdownIt().render('<span>text</span>'), '<p>&lt;span&gt;text&lt;/span&gt;</p>\n');
    assert.equal(new MarkdownIt({html:true}).render('<span>text</span>'), '<p><span>text</span></p>\n');
  });
  for (const variant of ['reference-title','reference-label','smartquotes','comment','processing','declaration','cdata']) {
    test(`Pathological Markdown completes within bounded subprocess: ${variant}`, () => {
      const result = execFileSync(process.execPath, ['--max-old-space-size=128', __filename, '--case', variant, root],
        { timeout: 8000, maxBuffer: 4096, encoding: 'utf8', windowsHide: true });
      const stats = JSON.parse(result);
      assert.ok(stats.inputBytes >= 50000 && stats.outputLength > 0);
    });
  }
}
