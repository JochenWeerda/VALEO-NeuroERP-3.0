// Scanner findings remain intact; only exact reviewed source repairs may pass.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { createRequire } = require('node:module');
const { execFileSync } = require('node:child_process');
const ROOT = path.resolve(__dirname, '..');
const ALLOWED = {
  'GHSA-gcqx-w48m-w2h4': { name: 'deepmerge', version: '4.3.1', files: ['index.js', 'dist/cjs.js', 'dist/umd.js'] },
  'GHSA-vfj7-8cjw-p6xm': { name: 'braces', version: '3.0.3', files: ['lib/compile.js', 'lib/expand.js', 'lib/stringify.js', 'lib/parse.js'] },
};
function hash(file) {
  return crypto.createHash('sha256').update(fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n')).digest('hex');
}
function assess(report, root = ROOT, today = new Date().toISOString().slice(0, 10)) {
  const metadata = report?.metadata;
  if (!report || report.error || !Number.isInteger(metadata?.dependencies) || metadata.dependencies < 1 ||
      !report.advisories || typeof report.advisories !== 'object' || Array.isArray(report.advisories) || !Array.isArray(report.muted) || report.muted.length) {
    throw new Error('Missing, incomplete or muted audit inventory');
  }
  const rows = Object.values(report.advisories);
  if (rows.some(row => !row || typeof row !== 'object' || !row.github_advisory_id || !row.module_name ||
      !Array.isArray(row.findings) || !row.findings.length || row.findings.some(f =>
        !f || typeof f.version !== 'string' || !f.version || !Array.isArray(f.paths) || !f.paths.length ||
        f.paths.some(p => typeof p !== 'string' || !p)) ||
      new Set(row.findings.map(f => f.version)).size !== row.findings.length)) {
    throw new Error('Invalid audit finding');
  }
  // pnpm groups affected installed versions under one advisory. Scanner
  // severity metadata counts those findings, not the number of advisory rows.
  const detected = rows.flatMap(row => row.findings.map(finding => ({ row, finding })));
  const counts = metadata.vulnerabilities;
  const severities = ['info', 'low', 'moderate', 'high', 'critical'];
  if (!counts || severities.some(s => !Number.isInteger(counts[s]) || counts[s] < 0) ||
      severities.reduce((n, s) => n + counts[s], 0) !== detected.length ||
      severities.some(s => detected.filter(({ row }) => row.severity === s).length !== counts[s])) {
    throw new Error('Audit severity counts contradict findings');
  }
  const policy = JSON.parse(fs.readFileSync(path.join(root, 'config/security/npm-backport-reviews.json'), 'utf8'));
  if (policy.schema_version !== 1 || !Array.isArray(policy.reviews)) throw new Error('Invalid backport policy');
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
  const installed = createRequire(path.join(root, 'node_modules/.pnpm/node_modules/package.json'));
  const findings = detected.map(({ row, finding }) => {
    let decision = 'blocked', reason = 'No exact source repair for this finding';
    try {
      const allowed = ALLOWED[row.github_advisory_id];
      const reviews = policy.reviews.filter(r => r.advisory === row.github_advisory_id);
      if (!allowed || reviews.length !== 1 || row.module_name !== allowed.name ||
          finding.version !== allowed.version) throw new Error(reason);
      const review = reviews[0];
      const from = Date.parse(review.reviewed_on), until = Date.parse(review.review_by), now = Date.parse(today);
      if (![review.reviewed_on, review.review_by, today].every(date => /^\d{4}-\d{2}-\d{2}$/.test(date)) ||
          ![from, until, now].every(Number.isFinite) || !(from <= now && now < until) || until - from > 90 * 86400000 ||
          !review.owner || !review.source || !review.original_integrity?.startsWith('sha512-')) throw new Error('Review expired or incomplete');
      const patch = `config/security/npm-patches/${allowed.name}@${allowed.version}.patch`;
      if (review.package !== allowed.name || review.version !== allowed.version || review.patch !== patch ||
          manifest.pnpm?.patchedDependencies?.[`${allowed.name}@${allowed.version}`] !== patch ||
          hash(path.join(root, patch)) !== review.patch_sha256 || hash(path.join(root, 'pnpm-lock.yaml')) !== review.lock_sha256 ||
          hash(path.join(root, 'package.json')) !== review.manifest_sha256) throw new Error('Reviewed patch, manifest or lock evidence changed');
      const pkgFile = installed.resolve(`${allowed.name}/package.json`);
      const pkg = JSON.parse(fs.readFileSync(pkgFile, 'utf8'));
      if (pkg.name !== allowed.name || pkg.version !== allowed.version ||
          JSON.stringify(Object.keys(review.installed_sha256).sort()) !== JSON.stringify([...allowed.files].sort()) ||
          allowed.files.some(file => hash(path.join(path.dirname(pkgFile), file)) !== review.installed_sha256[file])) {
        throw new Error('Installed source differs from reviewed repair');
      }
      decision = 'source_backported'; reason = 'Exact reviewed source, patch, manifest, lock and installed hashes match';
    } catch (error) { reason = error.message; }
    return { advisory: row.github_advisory_id, package: row.module_name, version: finding.version,
      severity: row.severity, decision, reason };
  });
  const blocked = findings.filter(f => f.decision === 'blocked').length;
  return { scanner_advisories: rows.length, scanner_findings: findings.length,
    source_backported: findings.length - blocked, blocked,
    release_allowed: blocked === 0, findings };
}
if (require.main === module) {
  const [reportFile, exitText, output = 'npm-backport-decision.json'] = process.argv.slice(2);
  let result;
  try {
    if (!reportFile || !['0', '1'].includes(exitText)) throw new Error('Scanner failure or missing report/exit');
    const report = JSON.parse(fs.readFileSync(reportFile, 'utf8'));
    if (exitText === '0' && Object.keys(report.advisories || {}).length) throw new Error('Scanner exit contradicts report');
    if (exitText === '1' && !Object.keys(report.advisories || {}).length) throw new Error('Scanner failure without findings');
    result = assess(report);
    const env = { ...process.env }; delete env.SECURITY_DEEPMERGE_RUNTIME; delete env.SECURITY_QS_RUNTIME; delete env.SECURITY_HIGH_RUNTIME; delete env.SECURITY_FOLLOW_REDIRECTS_RUNTIME; delete env.SECURITY_VITE_RUNTIME; delete env.SECURITY_MARKDOWN_RUNTIME; delete env.SECURITY_FASTIFY_RUNTIME;
    execFileSync(process.execPath, ['--test', path.join(__dirname, 'verify_node_high_backports.cjs')], { cwd: ROOT, env, stdio: 'inherit' });
    execFileSync(process.execPath, ['--test', path.join(__dirname, 'verify_fastify_headers.cjs')], { cwd: ROOT, env, stdio: 'inherit' });
    execFileSync(process.execPath, ['--test', path.join(__dirname, 'verify_follow_redirects.cjs')], { cwd: ROOT, env, stdio: 'inherit' });
    execFileSync(process.execPath, ['--test', path.join(__dirname, 'verify_vite_editor.cjs')], { cwd: ROOT, env, stdio: 'inherit' });
    execFileSync(process.execPath, ['--test', path.join(__dirname, 'verify_markdown_security.cjs')], { cwd: ROOT, env, stdio: 'inherit' });
    execFileSync(process.execPath, ['--test', path.join(__dirname, 'verify_qs_security_release.cjs')], { cwd: ROOT, env, stdio: 'inherit' });
    execFileSync(process.execPath, ['--test', path.join(__dirname, 'verify_deepmerge_security.cjs')], { cwd: ROOT, env, stdio: 'inherit' });
    result.runtime_contracts = 'passed';
  } catch (error) { result = { release_allowed: false, error: error.message }; }
  fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result, null, 2));
  process.exitCode = result.release_allowed ? 0 : 1;
}
module.exports = { assess, hash };
