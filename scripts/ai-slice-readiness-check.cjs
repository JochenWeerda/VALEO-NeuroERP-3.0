#!/usr/bin/env node

const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const repoRoot = process.cwd();
const requiredTopLevel = [
  "slice_id",
  "title",
  "owner",
  "status",
  "goal",
  "file_ownership",
  "acceptance",
  "tests",
  "risks",
];
const requiredHarness = [
  "fachlicher_vertrag",
  "architektur_vertrag",
  "daten_vertrag",
  "test_vertrag",
  "security_vertrag",
  "betriebs_vertrag",
  "dokumentations_vertrag",
];

function normalize(value) {
  return value.replace(/\\/g, "/");
}

function parseArgs() {
  const args = process.argv.slice(2);
  const result = { slice: null, changedOnly: false, base: null, head: null };
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--slice") result.slice = args[++index];
    else if (arg === "--changed-only") result.changedOnly = true;
    else if (arg === "--base") result.base = args[++index];
    else if (arg === "--head") result.head = args[++index];
  }
  return result;
}

function git(args) {
  return execFileSync("git", args, { cwd: repoRoot, encoding: "utf8" }).trim();
}

function changedSliceFiles(base, head) {
  let output = "";
  if (base && head) {
    output = git(["diff", "--name-only", `${base}...${head}`, "--", "docs/agent-ops/slices"]);
  } else {
    output = git(["ls-files", "--modified", "--others", "--exclude-standard", "docs/agent-ops/slices"]);
  }
  return output
    ? output.split(/\r?\n/).map(normalize).filter((filePath) => /\.ya?ml$/i.test(filePath))
    : [];
}

function sliceFiles(args) {
  if (args.slice) {
    const direct = `docs/agent-ops/slices/${args.slice}.yaml`;
    if (fs.existsSync(path.join(repoRoot, direct))) return [direct];
    return [`docs/agent-ops/slices/${args.slice}`];
  }
  if (args.changedOnly) return changedSliceFiles(args.base, args.head);
  return fs
    .readdirSync(path.join(repoRoot, "docs/agent-ops/slices"))
    .filter((name) => /\.ya?ml$/i.test(name))
    .map((name) => `docs/agent-ops/slices/${name}`);
}

function yamlHas(content, key) {
  return new RegExp(`(^|\\n)${key}:`, "m").test(content);
}

function yamlBlockHas(content, blockName, key) {
  const block = content.match(new RegExp(`(^|\\n)${blockName}:\\s*\\n([\\s\\S]*?)(\\n[^\\s#][^\\n]*:|\\s*$)`));
  if (!block) return false;
  return new RegExp(`(^|\\n)\\s+${key}:`, "m").test(block[2]);
}

function yamlListHasItems(content, key) {
  const block = content.match(new RegExp(`(^|\\n)${key}:\\s*\\n([\\s\\S]*?)(\\n[^\\s#][^\\n]*:|$)`, "m"));
  return Boolean(block && /^\s+-\s+\S/m.test(block[2]));
}

function sliceIdFromContent(filePath, content) {
  const match = content.match(/^slice_id:\s*(.+?)\s*$/m);
  return match ? match[1].trim() : path.basename(filePath, path.extname(filePath));
}

function main() {
  const args = parseArgs();
  const files = sliceFiles(args).filter((filePath) => fs.existsSync(path.join(repoRoot, filePath)));
  const workboardPath = path.join(repoRoot, "docs/agent-ops/active-workboard.md");
  const workboard = fs.existsSync(workboardPath) ? fs.readFileSync(workboardPath, "utf8") : "";
  const errors = [];

  for (const filePath of files) {
    const content = fs.readFileSync(path.join(repoRoot, filePath), "utf8");
    const sliceId = sliceIdFromContent(filePath, content);

    for (const key of requiredTopLevel) {
      if (!yamlHas(content, key)) errors.push(`${filePath}: missing required field '${key}'`);
    }

    for (const key of ["file_ownership", "acceptance", "tests", "risks"]) {
      if (yamlHas(content, key) && !yamlListHasItems(content, key)) {
        errors.push(`${filePath}: '${key}' must contain at least one list item`);
      }
    }

    if (!yamlHas(content, "ai_harness")) {
      errors.push(`${filePath}: missing required field 'ai_harness'`);
    } else {
      for (const key of requiredHarness) {
        if (!yamlBlockHas(content, "ai_harness", key)) {
          errors.push(`${filePath}: ai_harness missing '${key}'`);
        }
      }
    }

    if (!yamlHas(content, "external_gates")) {
      errors.push(`${filePath}: missing required field 'external_gates'`);
    }

    if (!workboard.includes(sliceId)) {
      errors.push(`${filePath}: active workboard does not reference '${sliceId}'`);
    }
  }

  if (errors.length > 0) {
    console.error("AI slice readiness check failed:\n");
    for (const error of errors) console.error(`- ${error}`);
    process.exit(1);
  }

  console.log(`AI slice readiness check passed for ${files.length} slice file(s)`);
}

main();
