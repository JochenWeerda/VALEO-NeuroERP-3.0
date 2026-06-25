#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const repoRoot = process.cwd();

function normalizeSlashes(value) {
  return value.replace(/\\/g, "/");
}

function isMarkdownFile(filePath) {
  return normalizeSlashes(filePath).toLowerCase().endsWith(".md");
}

function shouldIgnore(filePath) {
  const normalized = normalizeSlashes(filePath);
  return (
    normalized.startsWith("node_modules/") ||
    normalized.startsWith(".pnpm-store/") ||
    normalized.startsWith("dist/") ||
    normalized.startsWith("coverage/") ||
    normalized.startsWith("htmlcov/") ||
    normalized.startsWith("docs/archive/")
  );
}

function isGovernedDefaultTarget(filePath) {
  const normalized = normalizeSlashes(filePath);
  return (
    normalized === "docs/architecture/process-kernel/STATUS.md" ||
    /^docs\/architecture\/process-kernel\/wave-[^/]+\/STATUS\.md$/i.test(normalized) ||
    /^docs\/architecture\/process-kernel\/wave-[^/]+\/package-[^/]+\/STATUS\.md$/i.test(normalized) ||
    /^PLAN_GAPS_.*\.md$/i.test(path.basename(normalized)) ||
    normalized === "docs/architecture/process-kernel/DELIVERY-MAP.md" ||
    normalized === "DEVELOPMENT-MAP.md" ||
    normalized === "docs/architecture/index.md" ||
    normalized === "docs/AI-VISION.md" ||
    normalized === "docs/AGENT-INTEGRATION.md" ||
    normalized === "docs/roadmap/status/2026-03-06-arbeitsaufteilung-codex-hauptstrang.md" ||
    normalized === "docs/roadmap/status/2026-03-06-top-50-gap-backlog-landhandel.md" ||
    normalized === "docs/roadmap/status/2026-03-11-architecture-delivery-waves.md" ||
    normalized === "docs/standards/markdown-governance.md"
  );
}

function collectMarkdownFiles(rootDir) {
  const files = [];

  function walk(currentDir) {
    const entries = fs.readdirSync(currentDir, { withFileTypes: true });
    for (const entry of entries) {
      if (
        entry.name === ".git" ||
        entry.name === "node_modules" ||
        entry.name === ".pnpm-store" ||
        entry.name === "dist" ||
        entry.name === "coverage" ||
        entry.name === "htmlcov"
      ) {
        continue;
      }

      const absolutePath = path.join(currentDir, entry.name);
      if (entry.isDirectory()) {
        walk(absolutePath);
        continue;
      }

      if (entry.isFile() && isMarkdownFile(absolutePath)) {
        const relativePath = normalizeSlashes(path.relative(rootDir, absolutePath));
        if (!shouldIgnore(relativePath)) {
          files.push(relativePath);
        }
      }
    }
  }

  walk(rootDir);
  return files;
}

function resolveTargetsFromArgs(args) {
  const markdownArgs = args
    .map((value) => normalizeSlashes(path.relative(repoRoot, path.resolve(value))))
    .filter((value) => !value.startsWith(".."))
    .filter((value) => isMarkdownFile(value))
    .filter((value) => !shouldIgnore(value));

  if (markdownArgs.length > 0) {
    return markdownArgs;
  }

  return collectMarkdownFiles(repoRoot).filter((filePath) => isGovernedDefaultTarget(filePath));
}

function checkFile(filePath, errors) {
  const absolutePath = path.join(repoRoot, filePath);
  const content = fs.readFileSync(absolutePath, "utf8");
  const lines = content.split(/\r?\n/);

  // Optionaler YAML-Frontmatter-Block am Dateianfang (Docs-as-Code-Standard):
  // '---' ... '---' vor der H1 ist erlaubt. Ohne Frontmatter bleibt H1-first Pflicht.
  let bodyStartIndex = 0;
  const frontmatterStart = lines.findIndex((line) => line.trim().length > 0);
  if (frontmatterStart !== -1 && lines[frontmatterStart].trim() === "---") {
    let frontmatterEnd = -1;
    for (let index = frontmatterStart + 1; index < lines.length; index += 1) {
      if (lines[index].trim() === "---") {
        frontmatterEnd = index;
        break;
      }
    }
    if (frontmatterEnd === -1) {
      errors.push(`${filePath}: unclosed YAML frontmatter block`);
      return;
    }
    bodyStartIndex = frontmatterEnd + 1;
  }

  const relativeFirstNonEmpty = lines
    .slice(bodyStartIndex)
    .findIndex((line) => line.trim().length > 0);
  if (relativeFirstNonEmpty === -1) {
    errors.push(`${filePath}: file is empty`);
    return;
  }

  const firstNonEmptyIndex = bodyStartIndex + relativeFirstNonEmpty;
  if (!lines[firstNonEmptyIndex].startsWith("# ")) {
    errors.push(`${filePath}: first non-empty line must start with '# '`);
  }

  let inFence = false;

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const lineNumber = index + 1;

    if (line.startsWith("```")) {
      inFence = !inFence;
    }

    if (/\s+$/.test(line)) {
      errors.push(`${filePath}:${lineNumber}: trailing whitespace`);
    }

    if (/\t/.test(line)) {
      errors.push(`${filePath}:${lineNumber}: tab character found`);
    }

    if (!inFence && /^#{1,6}(?![\s#])/.test(line)) {
      errors.push(`${filePath}:${lineNumber}: missing space after heading marker`);
    }

    if (!inFence && /^```/.test(line) && line.trim() === "```") {
      // allowed, but encourage language tags only if needed later
    }
  }

  if (inFence) {
    errors.push(`${filePath}: unclosed fenced code block`);
  }
}

function main() {
  const targets = resolveTargetsFromArgs(process.argv.slice(2));
  const errors = [];

  for (const filePath of targets) {
    checkFile(filePath, errors);
  }

  if (errors.length > 0) {
    console.error("docs markdown check failed:\n");
    for (const error of errors) {
      console.error(`- ${error}`);
    }
    process.exit(1);
  }

  console.log(`docs markdown check passed for ${targets.length} file(s)`);
}

main();
