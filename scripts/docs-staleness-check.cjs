#!/usr/bin/env node

/**
 * Doku-Staleness-Check.
 *
 * Liest den `last_reviewed`-Frontmatter kuratierter Doku-Seiten und meldet
 * Seiten, deren letztes Review aelter als der Schwellwert ist.
 *
 * Verwendung:
 *   node scripts/docs-staleness-check.cjs                 # Default 180 Tage
 *   node scripts/docs-staleness-check.cjs --max-age-days 365
 *   node scripts/docs-staleness-check.cjs --max-age-days 3650   # praktisch nicht-blockierend
 */

const fs = require("fs");
const path = require("path");

const repoRoot = process.cwd();

// Kuratierte Bereiche (vgl. mkdocs nav / exclude_docs).
const CURATED = [
  "docs/index.md",
  "docs/dokumentation",
  "docs/benutzerhandbuch",
  "docs/admin",
  "docs/entwickler",
  "docs/schnittstellen",
  "docs/agent-docs",
  "docs/compliance",
  "docs/referenz",
];

function parseArgs() {
  const args = process.argv.slice(2);
  const result = { maxAgeDays: 180, paths: [] };
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === "--max-age-days") result.maxAgeDays = Number(args[++i]);
    else result.paths.push(args[i]);
  }
  return result;
}

function collectMarkdown(target, acc) {
  const abs = path.join(repoRoot, target);
  if (!fs.existsSync(abs)) return;
  const stat = fs.statSync(abs);
  if (stat.isFile()) {
    if (target.toLowerCase().endsWith(".md")) acc.push(target);
    return;
  }
  for (const entry of fs.readdirSync(abs, { withFileTypes: true })) {
    const child = `${target}/${entry.name}`;
    if (entry.isDirectory()) collectMarkdown(child, acc);
    else if (entry.isFile() && entry.name.toLowerCase().endsWith(".md")) acc.push(child);
  }
}

function readFrontmatterDate(filePath) {
  const content = fs.readFileSync(path.join(repoRoot, filePath), "utf8");
  const lines = content.split(/\r?\n/);
  if (lines[0]?.trim() !== "---") return null;
  for (let i = 1; i < lines.length; i += 1) {
    if (lines[i].trim() === "---") break;
    const match = lines[i].match(/^last_reviewed:\s*"?(\d{4}-\d{2}-\d{2})"?\s*$/);
    if (match) return match[1];
  }
  return null;
}

function main() {
  const args = parseArgs();
  const targets = args.paths.length > 0 ? args.paths : CURATED;
  const files = [];
  for (const target of targets) collectMarkdown(normalize(target), files);

  const now = Date.now();
  const stale = [];
  const missing = [];

  for (const filePath of files) {
    const date = readFrontmatterDate(filePath);
    if (!date) {
      missing.push(filePath);
      continue;
    }
    const ageDays = Math.floor((now - new Date(date).getTime()) / 86400000);
    if (ageDays > args.maxAgeDays) stale.push({ filePath, date, ageDays });
  }

  console.log(
    `Staleness-Check: ${files.length} Seite(n), Schwelle ${args.maxAgeDays} Tage.`,
  );
  if (missing.length > 0) {
    console.log(`\nOhne last_reviewed (${missing.length}):`);
    for (const filePath of missing) console.log(`  - ${filePath}`);
  }
  if (stale.length > 0) {
    console.log(`\nVeraltet (${stale.length}):`);
    for (const item of stale) {
      console.log(`  - ${item.filePath} (last_reviewed ${item.date}, ${item.ageDays} Tage)`);
    }
    process.exitCode = 1;
    return;
  }
  console.log("\nKeine veralteten Seiten.");
}

function normalize(value) {
  return value.replace(/\\/g, "/");
}

main();
