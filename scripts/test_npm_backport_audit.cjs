const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { assess, hash } = require('./check_npm_backport_audit.cjs');
const ROOT = path.resolve(__dirname, '..');

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'valeo-backport-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const write = (name, value) => {
    const file = path.join(root, name);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, typeof value === 'string' ? value : JSON.stringify(value));
  };
  const policy = JSON.parse(fs.readFileSync(path.join(ROOT, 'config/security/npm-backport-reviews.json'), 'utf8'));
  const manifest = { pnpm: { patchedDependencies: {} } };
  const advisories = {};
  for (const review of policy.reviews) {
    review.reviewed_on = '2026-10-08'; review.review_by = '2026-10-15';
    write(review.patch, fs.readFileSync(path.join(ROOT, review.patch), 'utf8'));
    manifest.pnpm.patchedDependencies[`${review.package}@${review.version}`] = review.patch;
    const pkg = `node_modules/.pnpm/node_modules/${review.package}`;
    write(`${pkg}/package.json`, { name: review.package, version: review.version });
    // Evidence binding is tested independently of real exploit contracts.
    for (const file of Object.keys(review.installed_sha256)) {
      write(`${pkg}/${file}`, `reviewed fixture ${review.package}/${file}\n`);
      review.installed_sha256[file] = hash(path.join(root, pkg, file));
    }
    advisories[review.advisory] = { github_advisory_id: review.advisory, module_name: review.package,
      severity: 'high', findings: [{ version: review.version, paths: [`test > ${review.package}@${review.version}`] }] };
  }
  write('package.json', manifest); write('pnpm-lock.yaml', 'reviewed lock\n');
  for (const review of policy.reviews) {
    review.lock_sha256 = hash(path.join(root, 'pnpm-lock.yaml'));
    review.manifest_sha256 = hash(path.join(root, 'package.json'));
  }
  const save = () => write('config/security/npm-backport-reviews.json', policy);
  save();
  const report = { advisories, muted: [], metadata: { dependencies: Math.max(1, policy.reviews.length),
    vulnerabilities: { info: 0, low: 0, moderate: 0, high: policy.reviews.length, critical: 0 } } };
  return { root, write, policy, save, report, run: () => assess(report, root, '2026-10-08') };
}
test('exact source evidence passes without mutating raw findings', t => {
  const f = fixture(t), original = JSON.stringify(f.report);
  assert.equal(f.run().source_backported, f.policy.reviews.length); assert.equal(f.run().release_allowed, true);
  assert.equal(JSON.stringify(f.report), original);
});
test('unknown advisory blocks release', t => {
  const f = fixture(t); f.report.advisories[f.policy.reviews[0].advisory].github_advisory_id = 'GHSA-unknown';
  assert.equal(f.run().release_allowed, false);
});
test('new affected version blocks release', t => {
  const f = fixture(t); Object.values(f.report.advisories)[0].findings[0].version = '1.4.1';
  assert.equal(f.run().release_allowed, false);
});
test('one advisory with two installed versions produces two findings and preserves the new block', t => {
  const f = fixture(t);
  f.report.advisories['new-zod'] = { github_advisory_id: 'GHSA-new-zod', module_name: 'zod', severity: 'high',
    findings: [{ version: '3.25.76', paths: ['test > zod@3.25.76'] },
      { version: '4.1.12', paths: ['test > zod@4.1.12'] }] };
  f.report.metadata.vulnerabilities.high = f.policy.reviews.length + 2;
  const result = f.run();
  assert.equal(result.scanner_advisories, f.policy.reviews.length + 1);
  assert.equal(result.scanner_findings, f.policy.reviews.length + 2);
  assert.equal(result.source_backported, f.policy.reviews.length);
  assert.equal(result.blocked, 2);
  assert.equal(result.release_allowed, false);
  assert.deepEqual(result.findings.filter(finding => finding.package === 'zod').map(finding => finding.version),
    ['3.25.76', '4.1.12']);
});
test('a reviewed advisory never blesses an additional unreviewed version', t => {
  const f = fixture(t), row = Object.values(f.report.advisories)[0];
  row.findings.push({ version: '1.4.1', paths: ['test > node-forge@1.4.1'] });
  f.report.metadata.vulnerabilities.high = f.policy.reviews.length + 1;
  const result = f.run();
  assert.equal(result.source_backported, f.policy.reviews.length);
  assert.equal(result.blocked, 1);
  assert.equal(result.findings.find(finding => finding.version === '1.4.1').decision, 'blocked');
});
test('advisory-row severity counts cannot replace installed-version counts', t => {
  const f = fixture(t), row = Object.values(f.report.advisories)[0];
  row.findings.push({ version: '1.4.1', paths: ['test > node-forge@1.4.1'] });
  assert.throws(f.run, /severity counts/);
});
test('empty, duplicate or pathless version inventories fail closed', t => {
  for (const mutation of [
    row => { row.findings = []; },
    row => { row.findings.push({ ...row.findings[0] }); },
    row => { row.findings[0].paths = []; },
  ]) {
    const f = fixture(t), row = Object.values(f.report.advisories)[0];
    mutation(row);
    assert.throws(f.run, /Invalid audit finding/);
  }
});
for (const change of ['expiry', 'future review', 'duplicate', 'missing source', 'malformed date']) {
  test(`${change} review blocks release`, t => {
    const f = fixture(t), review = f.policy.reviews[0];
    if (change === 'expiry') review.review_by = '2026-10-08';
    if (change === 'future review') review.reviewed_on = '2026-10-09';
    if (change === 'duplicate') f.policy.reviews.push({ ...review });
    if (change === 'missing source') delete review.source;
    if (change === 'malformed date') review.review_by = 'October 15 2026';
    f.save(); assert.equal(f.run().release_allowed, false);
  });
}
for (const change of ['patch', 'lock', 'manifest', 'installed source']) {
  test(`${change} evidence drift blocks release`, t => {
    const f = fixture(t), review = f.policy.reviews[0];
    const file = change === 'patch' ? review.patch : change === 'lock' ? 'pnpm-lock.yaml' :
      change === 'manifest' ? 'package.json' : `node_modules/.pnpm/node_modules/${review.package}/${Object.keys(review.installed_sha256)[0]}`;
    if (change === 'manifest') f.write(file, { pnpm: { patchedDependencies: {} } });
    else f.write(file, 'changed source\n');
    assert.equal(f.run().release_allowed, false);
  });
}
for (const change of ['counts', 'muted', 'missing inventory']) {
  test(`${change} report fails closed`, t => {
    const f = fixture(t);
    if (change === 'counts') f.report.metadata.vulnerabilities.high = 0;
    if (change === 'muted') f.report.muted.push('GHSA-hidden');
    if (change === 'missing inventory') delete f.report.metadata;
    assert.throws(f.run);
  });
}


test('retired vulnerable forge release cannot regain a source exception', t => {
  const f = fixture(t);
  f.report.advisories.forge = { github_advisory_id: 'GHSA-86w9-cpqp-85rv', module_name: 'node-forge', severity: 'high', findings: [{version: '1.4.0', paths: ['test > node-forge@1.4.0']}] };
  f.report.metadata.vulnerabilities.high += 1;
  const result = f.run();
  assert.equal(result.release_allowed, false);
  assert.equal(result.findings.find(finding => finding.package === 'node-forge').decision, 'blocked');
});
