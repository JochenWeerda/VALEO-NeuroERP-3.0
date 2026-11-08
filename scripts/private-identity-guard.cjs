/* Local identity fingerprints stay outside the repository. Never log matched values. */
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');

function containsPrivateIdentity(content, manifest) {
  const digest = value => crypto.createHash('sha256').update(manifest.salt + value.toLowerCase()).digest('hex');
  const emails = content.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi) || [];
  const users = [...content.matchAll(/(?:username|user_name|benutzerkennung|login)[\s"'_*]*[:=][\s"'_*]*([^\s"',;<>]+)/gi)].map(m => m[1]);
  const secrets = content.match(/[A-Z0-9_-]{20,}/gi) || [];
  return emails.some(v => (manifest.emails || []).includes(digest(v))) ||
    users.some(v => (manifest.usernames || []).includes(digest(v))) ||
    secrets.some(v => (manifest.secrets || []).includes(digest(v)));
}

function loadManifest() {
  const location = process.env.VALEO_PRIVATE_IDENTITY_MANIFEST ||
    path.join(os.homedir(), '.valeo-private', 'identity-private', 'digests.json');
  if (!fs.existsSync(location)) return null;
  const manifest = JSON.parse(fs.readFileSync(location, 'utf8'));
  if (!manifest.salt || !Array.isArray(manifest.emails) || !Array.isArray(manifest.usernames))
    throw new Error('Private identity manifest invalid');
  return manifest;
}

function checkFiles(files, revision) {
  const manifest = loadManifest();
  if (!manifest) return [];
  const violations = [];
  for (const file of files) {
    const contents = execFileSync('git', ['show', `${revision}:${file}`], {encoding:'utf8',maxBuffer:32*1024*1024});
    if (containsPrivateIdentity(contents, manifest)) violations.push({path:file,rule:'private identity content'});
  }
  return violations;
}
module.exports = {containsPrivateIdentity, checkFiles, loadManifest};
