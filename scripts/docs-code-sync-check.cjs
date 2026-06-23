#!/usr/bin/env node

const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const repoRoot = process.cwd();

function normalize(value) {
  return value.replace(/\\/g, "/");
}

function readArgs() {
  const args = process.argv.slice(2);
  const result = { base: null, head: null, map: "config/docs-code-sync-map.yaml" };
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--base") result.base = args[++index];
    else if (arg === "--head") result.head = args[++index];
    else if (arg === "--map") result.map = args[++index];
  }
  return result;
}

function git(args) {
  return execFileSync("git", args, { cwd: repoRoot, encoding: "utf8" }).trim();
}

function changedFiles(base, head) {
  if (head === "WORKTREE") {
    const modified = git(["ls-files", "--modified", "--others", "--exclude-standard"]);
    return modified ? modified.split(/\r?\n/).map(normalize).filter(Boolean) : [];
  }

  if (base && head) {
    const output = git(["diff", "--name-only", `${base}...${head}`]);
    return output ? output.split(/\r?\n/).map(normalize).filter(Boolean) : [];
  }

  const output = git(["diff", "--name-only", "HEAD"]);
  return output ? output.split(/\r?\n/).map(normalize).filter(Boolean) : [];
}

function parseListBlock(lines, startIndex, indent) {
  const values = [];
  for (let index = startIndex; index < lines.length; index += 1) {
    const line = lines[index];
    if (!line.trim()) continue;
    const currentIndent = line.match(/^ */)[0].length;
    if (currentIndent < indent) break;
    const match = line.match(/^\s*-\s+(.+?)\s*$/);
    if (match) values.push(match[1].trim().replace(/^["']|["']$/g, ""));
  }
  return values;
}

function parseMap(filePath) {
  const fullPath = path.join(repoRoot, filePath);
  const lines = fs.readFileSync(fullPath, "utf8").split(/\r?\n/);
  const config = { critical_paths: [], global_docs: [], exception_markers: [] };

  let current = null;
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const pathMatch = line.match(/^\s*-\s+path:\s+(.+?)\s*$/);
    if (pathMatch) {
      current = { path: normalize(pathMatch[1].trim()), docs: [] };
      config.critical_paths.push(current);
      continue;
    }

    if (current && /^\s+docs:\s*$/.test(line)) {
      current.docs = parseListBlock(lines, index + 1, 6).map(normalize);
      continue;
    }

    if (/^global_docs:\s*$/.test(line)) {
      config.global_docs = parseListBlock(lines, index + 1, 2).map(normalize);
      continue;
    }

    if (/^exception_markers:\s*$/.test(line)) {
      config.exception_markers = parseListBlock(lines, index + 1, 2);
    }
  }

  return config;
}

function hasException(changed, markers) {
  return changed.some((filePath) => {
    if (!/^docs\/agent-ops\/slices\/.+\.ya?ml$/i.test(filePath)) return false;
    const content = fs.readFileSync(path.join(repoRoot, filePath), "utf8");
    return markers.some((marker) => content.includes(marker));
  });
}

function main() {
  const args = readArgs();
  const changed = changedFiles(args.base, args.head);
  const config = parseMap(args.map);
  const changedDocs = changed.filter((filePath) => filePath.endsWith(".md"));
  const changedGlobalDocs = changed.filter((filePath) => config.global_docs.includes(filePath));
  const exception = hasException(changed, config.exception_markers);
  const errors = [];

  for (const rule of config.critical_paths) {
    const affected = changed.filter((filePath) => filePath.startsWith(rule.path));
    if (affected.length === 0) continue;

    const hasMappedDoc = changedDocs.some((filePath) =>
      rule.docs.some((docPath) => filePath === docPath || filePath.startsWith(docPath))
    );
    const hasGlobalDoc = changedGlobalDocs.length > 0;

    if (!hasMappedDoc && !hasGlobalDoc && !exception) {
      errors.push(
        `${rule.path}: ${affected.length} code file(s) changed without mapped docs, open-gaps/workboard update or docs_sync_exception`
      );
    }
  }

  if (errors.length > 0) {
    console.error("docs/code sync check failed:\n");
    for (const error of errors) console.error(`- ${error}`);
    process.exit(1);
  }

  console.log(`docs/code sync check passed for ${changed.length} changed file(s)`);
}

main();
