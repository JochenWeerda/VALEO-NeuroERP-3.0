/* Simple Check: doppelte Paketnamen + type-Konsistenz */
const { readdirSync, readFileSync } = require("fs");
const { join } = require("path");

const pkgsDir = join(__dirname, "..", "packages");
const names = new Map();
let ok = true;

for (const dir of readdirSync(pkgsDir)) {
  const pkgJson = join(pkgsDir, dir, "package.json");
  try {
    const pkg = JSON.parse(readFileSync(pkgJson, "utf8"));
    // Name prüfen
    if (names.has(pkg.name)) {
      console.error(`❌ Duplicate package name: ${pkg.name} in ${dir} & ${names.get(pkg.name)}`);
      ok = false;
    } else {
      names.set(pkg.name, dir);
    }
    // type prüfen
    if (pkg.type !== "commonjs") {
      console.error(`❌ Inconsistent "type" in ${pkg.name} (${dir}): expected "commonjs"`);
      ok = false;
    }
    // Namenskonvention prüfen
    if (!/^@valero-neuroerp\/([\w-]+)$/.test(pkg.name)) {
      console.error(`❌ Naming violation in ${pkg.name} (${dir}): use @valero-neuroerp/{name}`);
      ok = false;
    }
  } catch {
    // ignore folders without package.json
  }
}

if (!ok) {
  process.exit(1);
} else {
  console.log("✅ Workspace OK: unique names, consistent type=commonjs");
}