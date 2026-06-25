#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const repoRoot = process.cwd();
const allowedStatuses = new Set([
  "geplant",
  "in arbeit",
  "teilweise abgeschlossen",
  "abgeschlossen",
  "blockiert",
  "verworfen",
  "historisch",
]);

const statusRequiredHeadings = [
  "## Scope",
  "## Zielbild",
  "## Lieferumfang",
  "## Abnahmekriterien",
  "## Tests",
  "## Status",
];

const planRequiredHeadings = [
  "## Scope",
  "## Einordnung",
  "## Bewertungslogik",
  "## Abhaengigkeiten",
  "## Priorisierung",
  "## Akzeptanz / Done",
  "## Referenzen",
];

function normalizeSlashes(value) {
  return value.replace(/\\/g, "/");
}

function isMarkdownFile(filePath) {
  return normalizeSlashes(filePath).toLowerCase().endsWith(".md");
}

function isYamlFile(filePath) {
  return /\.ya?ml$/i.test(normalizeSlashes(filePath));
}

function shouldIgnore(filePath) {
  const normalized = normalizeSlashes(filePath);
  return (
    normalized.startsWith("docs/archive/") ||
    normalized.startsWith("docs/_internal/")
  );
}

function isGovernedStatusFile(filePath) {
  const normalized = normalizeSlashes(filePath);
  return (
    normalized === "docs/architecture/process-kernel/STATUS.md" ||
    /docs\/architecture\/process-kernel\/wave-[^/]+\/STATUS\.md$/i.test(normalized)
  );
}

function isPlanGapsFile(filePath) {
  const baseName = path.basename(filePath);
  return /^PLAN_GAPS_.*\.md$/i.test(baseName);
}

function isPackageStatusFile(filePath) {
  return /docs\/architecture\/process-kernel\/wave-[^/]+\/package-[^/]+\/STATUS\.md$/i.test(
    normalizeSlashes(filePath)
  );
}

function isRoadmapStatusFile(filePath) {
  return /^docs\/roadmap\/status\/\d{4}-\d{2}-\d{2}-.*\.md$/i.test(normalizeSlashes(filePath));
}

function isDeliveryMapFile(filePath) {
  return normalizeSlashes(filePath) === "docs/architecture/process-kernel/DELIVERY-MAP.md";
}

function isDevelopmentMapFile(filePath) {
  return normalizeSlashes(filePath) === "DEVELOPMENT-MAP.md";
}

function isReferenceDocFile(filePath) {
  const normalized = normalizeSlashes(filePath);
  return (
    normalized === "docs/architecture/index.md" ||
    normalized === "docs/AI-VISION.md" ||
    normalized === "docs/AGENT-INTEGRATION.md"
  );
}

function isAdrFile(filePath) {
  return /^docs\/adr\/[^/]+\.md$/i.test(normalizeSlashes(filePath));
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

function fileContent(filePath) {
  return fs.readFileSync(path.join(repoRoot, filePath), "utf8");
}

function ensureAiHarnessSliceRules(filePath, content, errors) {
  const normalized = normalizeSlashes(filePath);
  if (!/^docs\/agent-ops\/slices\/.+\.ya?ml$/i.test(normalized)) {
    return;
  }

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
    "ai_harness",
    "external_gates",
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

  for (const key of requiredTopLevel) {
    if (!new RegExp(`(^|\\n)${key}:`, "m").test(content)) {
      errors.push(`${filePath}: missing required AI harness field '${key}'`);
    }
  }

  const harnessBlock = content.match(/(^|\n)ai_harness:\s*\n([\s\S]*?)(\n[^ \n#][^\n]*:|\s*$)/);
  if (harnessBlock) {
    for (const key of requiredHarness) {
      if (!new RegExp(`(^|\\n)\\s+${key}:`, "m").test(harnessBlock[2])) {
        errors.push(`${filePath}: ai_harness missing '${key}'`);
      }
    }
  }
}

function ensureH1(filePath, content, errors) {
  const lines = content.split(/\r?\n/);

  // Optionaler YAML-Frontmatter-Block ('---' ... '---') vor der H1 ist erlaubt.
  let startIndex = 0;
  const frontmatterStart = lines.findIndex((line) => line.trim().length > 0);
  if (frontmatterStart !== -1 && lines[frontmatterStart].trim() === "---") {
    const frontmatterEnd = lines.findIndex(
      (line, index) => index > frontmatterStart && line.trim() === "---",
    );
    if (frontmatterEnd === -1) {
      errors.push(`${filePath}: unclosed YAML frontmatter block`);
      return;
    }
    startIndex = frontmatterEnd + 1;
  }

  const firstNonEmpty = lines
    .slice(startIndex)
    .find((line) => line.trim().length > 0);

  if (!firstNonEmpty || !firstNonEmpty.startsWith("# ")) {
    errors.push(`${filePath}: first non-empty line must be an H1 heading`);
  }
}

function ensureDateFormat(filePath, content, errors) {
  const dateLines = content.match(/\b\d{4}-\d{2}-\d{2}\b/g) || [];
  for (const value of dateLines) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
      errors.push(`${filePath}: invalid date format '${value}'`);
    }
  }
}

function ensureContainsHeadings(filePath, content, headings, errors) {
  for (const heading of headings) {
    if (!content.includes(heading)) {
      errors.push(`${filePath}: missing required heading '${heading}'`);
    }
  }
}

function ensureStatusValue(filePath, content, errors) {
  const statusBlock = content.match(/## Status(?::\s*([^\n]+))?([\s\S]*?)(?:\n## |\n# |$)/);
  if (!statusBlock) {
    errors.push(`${filePath}: missing status section`);
    return;
  }

  const headerValue = (statusBlock[1] || "").trim().toLowerCase();
  const body = statusBlock[2] || "";
  const inlineValue = body.match(/`([^`]+)`/);
  const candidates = [headerValue];

  if (inlineValue) {
    candidates.push(inlineValue[1].trim().toLowerCase());
  }

  const matched = candidates.find((value) => allowedStatuses.has(value));
  if (!matched) {
    errors.push(
      `${filePath}: status must contain one of ${Array.from(allowedStatuses).join(", ")}`
    );
  }

  if (!/\b\d{4}-\d{2}-\d{2}\b/.test(statusBlock[0])) {
    errors.push(`${filePath}: status section must contain a YYYY-MM-DD date`);
  }
}

function ensureDeliveryMapReference(filePath, content, errors) {
  if (normalizeSlashes(filePath) !== "docs/architecture/process-kernel/STATUS.md") {
    return;
  }

  if (!/wave-\d+\/STATUS\.md/.test(content)) {
    errors.push(`${filePath}: global process-kernel status must reference wave STATUS files`);
  }
}

function ensurePlanSpecificRules(filePath, content, errors) {
  ensureContainsHeadings(filePath, content, planRequiredHeadings, errors);

  if (!/Source-of-Truth|Source of Truth|operative Source-of-Truth|operative Source of Truth/i.test(content)) {
    errors.push(
      `${filePath}: plan document must explicitly state that it is not the operative source of truth`
    );
  }

  if (!/Current State/.test(content)) {
    errors.push(`${filePath}: plan document must contain at least one 'Current State' section`);
  }

  if (!/Acceptance Criteria/.test(content)) {
    errors.push(`${filePath}: plan document must contain at least one 'Acceptance Criteria' section`);
  }

  const gapIds = content.match(/Gap[- ]ID|## Gap \d+/g) || [];
  if (gapIds.length === 0) {
    errors.push(`${filePath}: plan document must declare gap sections or gap identifiers`);
  }
}

function ensureRoadmapStatusRules(filePath, content, errors) {
  const baseName = path.basename(filePath);
  if (!/^\d{4}-\d{2}-\d{2}-.*\.md$/i.test(baseName)) {
    errors.push(`${filePath}: roadmap status file name must start with YYYY-MM-DD-`);
  }

  if (!(/## Ziel/.test(content) || /## Statusabgleich/.test(content) || /\*\*Zweck:\*\*/.test(content))) {
    errors.push(
      `${filePath}: roadmap status file must contain at least one of '## Ziel', '## Statusabgleich' or '**Zweck:**'`
    );
  }

  if (!/\[[^\]]+\]\([^)]+\)/.test(content)) {
    errors.push(`${filePath}: roadmap status file must contain at least one markdown link`);
  }

  const containsDeliveryClaims = /\berledigt\b|\babgeschlossen\b/i.test(content);
  const referencesTruth =
    content.includes("docs/architecture/process-kernel/STATUS.md") ||
    /wave-\*\/STATUS\.md/.test(content) ||
    /wave-\d+\/STATUS\.md/.test(content) ||
    /operative[rn]? Wahrheitsstand/i.test(content);

  if (containsDeliveryClaims && !referencesTruth) {
    errors.push(
      `${filePath}: roadmap status file with delivery claims must reference the operative status source`
    );
  }
}

function ensureStatusSpecificRules(filePath, content, errors) {
  ensureContainsHeadings(filePath, content, statusRequiredHeadings, errors);
  ensureStatusValue(filePath, content, errors);
  ensureDeliveryMapReference(filePath, content, errors);
}

function ensurePackageStatusRules(filePath, content, errors) {
  if (!(/## Paket/.test(content) || /## Scope/.test(content) || /## Arbeitspakete/.test(content))) {
    errors.push(`${filePath}: package status must contain '## Paket', '## Scope' or '## Arbeitspakete'`);
  }

  if (!(/## Verifikation/.test(content) || /## Testergebnis/.test(content) || /## Tests/.test(content) || /## Abnahmekriterien/.test(content))) {
    errors.push(`${filePath}: package status must contain '## Verifikation', '## Testergebnis', '## Tests' or '## Abnahmekriterien'`);
  }

  if (!(/## Gelieferte Artefakte/.test(content) || /## Lieferumfang/.test(content) || /## Arbeitspakete/.test(content) || /## Abhaengigkeiten/.test(content) || /## Aktueller Stand/.test(content) || /## Artefakte/.test(content) || /## Produktive Kernmasken/.test(content) || /## Geliefert/.test(content))) {
    errors.push(`${filePath}: package status must contain delivery content such as artefacts, work packages or dependencies`);
  }
}

function ensureDeliveryMapRules(filePath, content, errors) {
  if (!/##\s+Wave/i.test(content)) {
    errors.push(`${filePath}: delivery map must contain a wave mapping section`);
  }

  if (!/##\s+Gap/i.test(content)) {
    errors.push(`${filePath}: delivery map must contain a gap mapping section`);
  }

  if (!(/\[[^\]]+\]\([^)]+\)/.test(content) || /`[^`]+STATUS\.md`/.test(content))) {
    errors.push(`${filePath}: delivery map must contain at least one link or path reference to operative status sources`);
  }
}

function ensureDevelopmentMapRules(filePath, content, errors) {
  if (!(/## Einordnung/.test(content) || /\*\*Zweck:\*\*/.test(content))) {
    errors.push(`${filePath}: development map must contain '## Einordnung' or '**Zweck:**'`);
  }

  if (!/## Referenzen/.test(content)) {
    errors.push(`${filePath}: development map must contain '## Referenzen'`);
  }

  if (!/historisch|abgeleitete Sicht/i.test(content)) {
    errors.push(`${filePath}: development map must explicitly state 'historisch' or 'abgeleitete Sicht'`);
  }

  if (!/\[[^\]]+\]\([^)]+\)/.test(content)) {
    errors.push(`${filePath}: development map must contain at least one markdown link`);
  }
}

function ensureReferenceDocRules(filePath, content, errors) {
  if (!(/## Einordnung/.test(content) || /## Zweck/.test(content) || /## Zielbild/.test(content) || /\*\*Zweck:\*\*/.test(content))) {
    errors.push(`${filePath}: reference document must contain an orientation or purpose section`);
  }

  if (!(/\[[^\]]+\]\([^)]+\)/.test(content) || /## Referenzen/.test(content))) {
    errors.push(`${filePath}: reference document must contain markdown links or a references section`);
  }

  if (!/abgeleitete Sicht|referenzdokument|historisch/i.test(content)) {
    errors.push(`${filePath}: reference document must explicitly state that it is derived, reference-only or historical if not operative`);
  }
}

function ensureAdrRules(filePath, content, errors) {
  const hasStatusSection = /## Status[\s\S]*?(Accepted|Rejected|Superseded|Proposed|Accepted)/i.test(content);
  const hasInlineMeta =
    /\*\*Status:\*\*/.test(content) && (/\*\*Date:\*\*/.test(content) || /\*\*Datum:\*\*/.test(content));
  const hasMetaTable = /\|\s*Status\s*\|/i.test(content) && /\|\s*(Date|Datum)\s*\|/i.test(content);

  if (!(hasStatusSection || hasInlineMeta || hasMetaTable)) {
    errors.push(`${filePath}: ADR must contain recognizable status and date metadata`);
  }

  if (!(/## Context/.test(content) || /## Kontext/.test(content))) {
    errors.push(`${filePath}: ADR must contain '## Context' or '## Kontext'`);
  }

  if (!(/## Decision/.test(content) || /## Entscheidung/.test(content))) {
    errors.push(`${filePath}: ADR must contain '## Decision' or '## Entscheidung'`);
  }

  if (!(/## Consequences/.test(content) || /## Konsequenzen/.test(content))) {
    errors.push(`${filePath}: ADR must contain '## Consequences' or '## Konsequenzen'`);
  }
}

function checkFile(filePath, errors) {
  const content = fileContent(filePath);

  if (isYamlFile(filePath)) {
    ensureAiHarnessSliceRules(filePath, content, errors);
    return;
  }

  ensureH1(filePath, content, errors);
  ensureDateFormat(filePath, content, errors);

  if (isGovernedStatusFile(filePath)) {
    ensureStatusSpecificRules(filePath, content, errors);
  }

  if (isPlanGapsFile(filePath)) {
    ensurePlanSpecificRules(filePath, content, errors);
  }

  if (isRoadmapStatusFile(filePath)) {
    ensureRoadmapStatusRules(filePath, content, errors);
  }

  if (isPackageStatusFile(filePath)) {
    ensurePackageStatusRules(filePath, content, errors);
  }

  if (isDeliveryMapFile(filePath)) {
    ensureDeliveryMapRules(filePath, content, errors);
  }

  if (isDevelopmentMapFile(filePath)) {
    ensureDevelopmentMapRules(filePath, content, errors);
  }

  if (isReferenceDocFile(filePath)) {
    ensureReferenceDocRules(filePath, content, errors);
  }

  if (isAdrFile(filePath) && path.basename(filePath).toLowerCase() !== "readme.md") {
    ensureAdrRules(filePath, content, errors);
  }
}

function resolveTargetsFromArgs(args) {
  const explicitArgs = args
    .map((value) => normalizeSlashes(path.relative(repoRoot, path.resolve(value))))
    .filter((value) => !value.startsWith(".."))
    .filter((value) => isMarkdownFile(value) || isYamlFile(value))
    .filter((value) => !shouldIgnore(value));

  if (explicitArgs.length > 0) {
    return explicitArgs;
  }

  const packageStatusFiles = collectMarkdownFiles(repoRoot).filter((filePath) =>
    isPackageStatusFile(filePath)
  );

  return [
    "docs/architecture/process-kernel/STATUS.md",
    "PLAN_GAPS_023_024_043_049.md",
    "docs/architecture/process-kernel/DELIVERY-MAP.md",
    "DEVELOPMENT-MAP.md",
    "docs/architecture/index.md",
    "docs/AI-VISION.md",
    "docs/AGENT-INTEGRATION.md",
    ...collectMarkdownFiles(repoRoot).filter(
      (filePath) => isAdrFile(filePath) && path.basename(filePath).toLowerCase() !== "readme.md"
    ),
    "docs/roadmap/status/2026-03-06-arbeitsaufteilung-codex-hauptstrang.md",
    "docs/roadmap/status/2026-03-06-top-50-gap-backlog-landhandel.md",
    "docs/roadmap/status/2026-03-11-architecture-delivery-waves.md",
    ...packageStatusFiles,
  ];
}

function main() {
  const targets = resolveTargetsFromArgs(process.argv.slice(2));
  const errors = [];

  for (const filePath of targets) {
    checkFile(filePath, errors);
  }

  if (errors.length > 0) {
    console.error("docs governance check failed:\n");
    for (const error of errors) {
      console.error(`- ${error}`);
    }
    process.exit(1);
  }

  console.log(`docs governance check passed for ${targets.length} file(s)`);
}

main();
