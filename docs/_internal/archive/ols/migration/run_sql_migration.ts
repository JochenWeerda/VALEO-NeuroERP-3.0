import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { query, disposePools } from "../../packages/utilities/src/postgres";

const [, , connectionString, migrationFile] = process.argv;

if (!connectionString || !migrationFile) {
  console.error("Usage: ts-node run_sql_migration.ts <connectionString> <migration.sql>");
  process.exit(1);
}

async function main() {
  try {
    const sql = readFileSync(resolve(migrationFile), "utf-8");
    await query(sql, [], { connectionString, name: "migration" });
    console.log(`Executed migration ${migrationFile}`);
  } finally {
    await disposePools();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
