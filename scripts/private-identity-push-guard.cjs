/* Inspect every outgoing commit, not merely the final diff. No personal values in errors. */
const fs=require('node:fs');
const {execFileSync}=require('node:child_process');
const {findViolations}=require('./guard-forbidden-paths.cjs');
const {checkFiles,containsPrivateIdentity,loadManifest}=require('./private-identity-guard.cjs');
const git=(...args)=>execFileSync('git',args,{encoding:'utf8',maxBuffer:32*1024*1024}).trim();

function outgoingCommits(local, remote) {
  if (![local,remote].every(v=>/^[a-f0-9]{40,64}$/.test(v))) throw new Error('Invalid push identity');
  if (/^0+$/.test(local)) return [];
  const args=/^0+$/.test(remote)?['rev-list',local,'--not','--remotes']:['rev-list',`${remote}..${local}`];
  return git(...args).split(/\r?\n/).filter(Boolean);
}

function inspectCommit(commit) {
  // Compare merges to each parent: merge-only additions must also be inspected.
  const files=[...new Set(git('diff-tree','-m','--root','--no-commit-id','--name-only','-r','--diff-filter=ACMR',commit).split(/\r?\n/).filter(Boolean))];
  const problems=[...findViolations(files),...checkFiles(files,commit)];
  const manifest=loadManifest();
  if (manifest) {
    const metadata=git('show','-s','--format=%ae%n%ce%n%B',commit);
    if (containsPrivateIdentity(metadata,manifest)) problems.push({path:'commit metadata',rule:'private identity content'});
  }
  return problems;
}

function main(input) {
  let blocked=false;
  const inspected=new Set();
  for (const line of input.split(/\r?\n/).filter(Boolean)) {
    const [,local,,remote]=line.trim().split(/\s+/);
    for (const commit of outgoingCommits(local,remote)) {
      if (inspected.has(commit)) continue;
      inspected.add(commit);
      for (const problem of inspectCommit(commit)) {
        console.error(`Push blocked: ${commit.slice(0,10)} / ${problem.path} (${problem.rule})`);
        blocked=true;
      }
    }
  }
  if (blocked) process.exitCode=1;
  else console.log(`Private identity push guard passed (${inspected.size} outgoing commits).`);
}
module.exports={outgoingCommits,inspectCommit};
if (require.main===module) main(fs.readFileSync(0,'utf8'));
