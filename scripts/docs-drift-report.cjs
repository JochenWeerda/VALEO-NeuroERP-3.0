#!/usr/bin/env node

const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const repoRoot = process.cwd();

function normalize(value) {
  return value.replace(/\\/g, "/");
}

function parseArgs() {
  const args = process.argv.slice(2);
  const result = {
    base: null,
    head: null,
    output: "artifacts/docs-drift-report.json",
  };
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--base") result.base = args[++index];
    else if (arg === "--head") result.head = args[++index];
    else if (arg === "--output") result.output = args[++index];
  }
  return result;
}

function git(args) {
  return execFileSync("git", args, { cwd: repoRoot, encoding: "utf8" }).trim();
}

function changedFiles(base, head) {
  if (head === "WORKTREE") {
    const output = git(["ls-files", "--modified", "--others", "--exclude-standard"]);
    return output ? output.split(/\r?\n/).map(normalize).filter(Boolean) : [];
  }
  const range = base && head ? `${base}...${head}` : "HEAD";
  const output = git(["diff", "--name-only", range]);
  return output ? output.split(/\r?\n/).map(normalize).filter(Boolean) : [];
}

function classify(filePath) {
  if (filePath.startsWith("app/api/v1/endpoints/")) return "api_endpoint";
  if (filePath.startsWith("app/services/")) return "domain_service";
  if (filePath.startsWith("packages/frontend-web/src/pages/")) return "frontend_page";
  if (filePath.startsWith("packages/frontend-web/src/app/routing/")) return "frontend_route";
  if (filePath.startsWith("alembic/versions/") || filePath.startsWith("migrations/sql/")) return "database_migration";
  if (filePath.startsWith(".github/workflows/")) return "ci_workflow";
  if (filePath.startsWith("tests/") || filePath.includes("/tests/")) return "test";
  if (filePath.endsWith(".md")) return "documentation";
  return "other";
}

function main() {
  const args = parseArgs();
  const changed = changedFiles(args.base, args.head);
  const docs = changed.filter((filePath) => filePath.endsWith(".md"));
  const report = {
    generated_at: new Date().toISOString(),
    base: args.base || null,
    head: args.head || null,
    changed_count: changed.length,
    documentation_changed: docs,
    findings: [],
  };

  const groups = new Map();
  for (const filePath of changed) {
    const type = classify(filePath);
    if (!groups.has(type)) groups.set(type, []);
    groups.get(type).push(filePath);
  }

  for (const [type, files] of groups.entries()) {
    if (type === "documentation" || type === "other") continue;
    report.findings.push({
      type,
      files,
      status: docs.length > 0 ? "docs_changed_review_required" : "potential_docs_drift",
      recommendation:
        docs.length > 0
          ? "Review whether changed documentation covers this code change."
          : "Add mapped documentation, open-gap entry, QA report or explicit docs_sync_exception.",
    });
  }

  const outputPath = path.join(repoRoot, args.output);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  console.log(`docs drift report written to ${normalize(args.output)} with ${report.findings.length} finding(s)`);
}

main();
