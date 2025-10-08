import fs from 'node:fs/promises';
import path from 'node:path';
import { Client } from 'pg';

export async function runMigrations(client: Client): Promise<void> {
  const migrationsDir = path.resolve(__dirname, '../../migrations');
  const entries = await fs.readdir(migrationsDir, { withFileTypes: true }).catch(() => []);
  const files = entries
    .filter(entry => entry.isFile() && entry.name.endsWith('.sql'))
    .map(entry => entry.name)
    .sort();

  for (const file of files) {
    const filePath = path.join(migrationsDir, file);
    const sql = await fs.readFile(filePath, 'utf8');
    if (sql.trim().length === 0) {
      continue;
    }
    await client.query(sql);
  }
}
