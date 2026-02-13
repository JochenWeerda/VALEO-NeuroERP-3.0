#!/usr/bin/env node
/* eslint-disable no-console */
const { execSync } = require("node:child_process");

const BLOCKED_RULES = [
  { name: "node_modules", test: (p) => /(^|\/)node_modules(\/|$)/.test(p) },
  { name: ".pnpm-store", test: (p) => /(^|\/)\.pnpm-store(\/|$)/.test(p) },
  { name: ".pytest_cache", test: (p) => /(^|\/)\.pytest_cache(\/|$)/.test(p) },
  { name: "__pycache__", test: (p) => /(^|\/)__pycache__(\/|$)/.test(p) },
  { name: "htmlcov", test: (p) => /(^|\/)htmlcov(\/|$)/.test(p) },
  { name: "test-results", test: (p) => /(^|\/)test-results(\/|$)/.test(p) },
  {
    name: "gitleaks-report.json",
    test: (p) => p === "gitleaks-report.json" || p.endsWith("/gitleaks-report.json"),
  },
  {
    name: "report.json",
    test: (p) => p === "report.json" || p.endsWith("/report.json"),
  },
];

function normalize(pathValue) {
  return pathValue.replace(/\\/g, "/").replace(/^\.\/+/, "");
}

function readLines(command) {
  const output = execSync(command, { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
  if (!output) return [];
  return output.split(/\r?\n/).map((line) => normalize(line)).filter(Boolean);
}

function getStagedFiles() {
  return readLines("git diff --cached --name-only --diff-filter=ACMR");
}

function getRangeFiles(range) {
  const escapedRange = range.replace(/"/g, '\\"');
  return readLines(`git diff --name-only --diff-filter=ACMR "${escapedRange}"`);
}

function findViolations(paths) {
  const violations = [];
  for (const pathValue of paths) {
    const matched = BLOCKED_RULES.find((rule) => rule.test(pathValue));
    if (matched) {
      violations.push({ path: pathValue, rule: matched.name });
    }
  }
  return violations;
}

function printAndExit(violations) {
  if (!violations.length) {
    console.log("Path guard passed: no forbidden paths detected.");
    process.exit(0);
  }

  console.error("Path guard failed. Forbidden paths detected:");
  for (const entry of violations) {
    console.error(`- ${entry.path} (rule: ${entry.rule})`);
  }
  process.exit(1);
}

function parseArgs(argv) {
  const args = new Set(argv.slice(2));
  const rangeIndex = argv.indexOf("--range");
  const range = rangeIndex >= 0 ? argv[rangeIndex + 1] : "";
  return {
    staged: args.has("--staged"),
    range,
  };
}

function main() {
  const { staged, range } = parseArgs(process.argv);
  if (staged || !range) {
    const files = getStagedFiles();
    printAndExit(findViolations(files));
    return;
  }

  const files = getRangeFiles(range);
  printAndExit(findViolations(files));
}

main();
