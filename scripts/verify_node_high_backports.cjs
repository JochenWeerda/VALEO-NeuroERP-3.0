const assert = require('node:assert/strict');
const { test } = require('node:test');
const { createRequire } = require('node:module');
const path = require('node:path');
const runtime = process.env.SECURITY_HIGH_RUNTIME || path.resolve(__dirname, '../node_modules/.pnpm/node_modules');
const packages = createRequire(path.join(path.resolve(runtime), 'package.json'));
const forge = packages('node-forge');
const braces = packages('braces');
// Test key only: actual public/private operations validate the malformed encoding.
const keys = forge.pki.rsa.generateKeyPair({ bits: 1024, e: 3 });
function digestInfo(hash, parameters, extras = []) {
  const a = forge.asn1;
  const nodes = [a.create(a.Class.UNIVERSAL, a.Type.OID, false, a.oidToDer(forge.oids[hash]).getBytes())];
  if (parameters) nodes.push(a.create(a.Class.UNIVERSAL, a.Type.NULL, false, ''));
  nodes.push(...extras);
  const digest = forge.md[hash].create().update('signature contract').digest().getBytes();
  const object = a.create(a.Class.UNIVERSAL, a.Type.SEQUENCE, true, [
    a.create(a.Class.UNIVERSAL, a.Type.SEQUENCE, true, nodes),
    a.create(a.Class.UNIVERSAL, a.Type.OCTETSTRING, false, digest),
  ]);
  return { digest, signature: keys.privateKey.sign(a.toDer(object).getBytes(), 'NONE') };
}
for (const parameters of [true, false]) {
  test(`RSA rejects nested DigestAlgorithm extras (${parameters ? 'NULL' : 'OID only'})`, () => {
    const a = forge.asn1;
    const extra = a.create(a.Class.UNIVERSAL, a.Type.OCTETSTRING, false, 'untrusted padding');
    const { digest, signature } = digestInfo('sha256', parameters, [extra]);
    assert.throws(() => keys.publicKey.verify(digest, signature), /valid RSASSA-PKCS1/);
  });
}
test('valid SHA256/SHA384 signatures remain accepted with optional NULL', () => {
  for (const hash of ['sha256', 'sha384']) {
    for (const parameters of [true, false]) {
      const { digest, signature } = digestInfo(hash, parameters);
      assert.equal(keys.publicKey.verify(digest, signature), true);
      assert.equal(keys.publicKey.verify('wrong digest', signature), false);
    }
  }
});
test('ordinary RSA-PSS and certificate signatures remain valid', () => {
  const md = forge.md.sha256.create().update('PSS contract');
  const pss = forge.pss.create({ md: forge.md.sha256.create(), mgf: forge.mgf.mgf1.create(forge.md.sha256.create()), saltLength: 20 });
  const signature = keys.privateKey.sign(md, pss);
  assert.equal(keys.publicKey.verify(md.digest().getBytes(), signature, pss), true);
  const cert = forge.pki.createCertificate(); cert.publicKey = keys.publicKey;
  cert.serialNumber = '01'; cert.setSubject([{ name: 'commonName', value: 'contract.invalid' }]);
  cert.setIssuer(cert.subject.attributes); cert.sign(keys.privateKey, forge.md.sha256.create());
  assert.equal(cert.verify(cert), true);
});
for (const method of ['parse', 'compile', 'expand', 'stringify']) {
  test(`braces ${method} rejects deeply nested string before stack exhaustion`, () => {
    assert.throws(() => braces[method]('{'.repeat(4000) + 'x' + '}'.repeat(4000)), /braces AST nesting exceeds 128/);
    assert.throws(() => braces[method]('('.repeat(4000) + 'x' + ')'.repeat(4000)), /braces AST nesting exceeds 128/);
  });
}
for (const method of ['compile', 'expand', 'stringify']) {
  test(`braces ${method} bounds directly supplied AST`, () => {
    const ast = { type: 'root', nodes: [] }; let node = ast;
    for (let i = 0; i < 200; i++) { const child = { type: 'paren', nodes: [] }; node.nodes.push(child); node = child; }
    node.nodes.push({ type: 'text', value: 'x' });
    assert.throws(() => braces[method](ast), /braces AST nesting exceeds 128/);
  });
}
test('normal brace ranges, escaped syntax and malformed patterns retain behavior', () => {
  assert.deepEqual(braces.expand('invoice-{01..03}.{pdf,xml}'), ['invoice-01.pdf', 'invoice-01.xml', 'invoice-02.pdf', 'invoice-02.xml', 'invoice-03.pdf', 'invoice-03.xml']);
  assert.equal(braces.compile('file.{pdf,xml}'), 'file.(pdf|xml)');
  for (const value of ['file.\\{pdf\\}', 'file.{pdf', 'file.(test)', '{a,{b,c}}']) {
    assert.equal(braces.stringify(braces.parse(value, { keepEscaping: true })), value);
  }
  assert.deepEqual(braces.expand('{a,{b,c}}'), ['a', 'b', 'c']);
});
