#!/usr/bin/env ts-node
/**
 * Test generator scaffolds integration tests for Postgres repositories.
 */
import { promises as fs } from 'fs';
import path from 'path';

interface CliOptions {
  domain: string;
  entity: string;
  projectRoot: string;
  repositoryClass?: string;
  envVar?: string;
}

function toPascalCase(value: string): string {
  return value
    .replace(/[-_\s]+/g, ' ')
    .trim()
    .split(' ')
    .map((chunk) => chunk.charAt(0).toUpperCase() + chunk.slice(1))
    .join('');
}

function toCamelCase(value: string): string {
  const pascal = toPascalCase(value);
  return pascal.charAt(0).toLowerCase() + pascal.slice(1);
}

function parseArgs(): CliOptions {
  const args = process.argv.slice(2);
  const options: Partial<CliOptions> = {};

  for (let index = 0; index < args.length; index += 1) {
    const key = args[index];
    const value = args[index + 1];

    if (!value) {
      continue;
    }

    switch (key) {
      case '--domain':
        options.domain = value;
        index += 1;
        break;
      case '--entity':
        options.entity = value;
        index += 1;
        break;
      case '--repo-class':
        options.repositoryClass = value;
        index += 1;
        break;
      case '--env-var':
        options.envVar = value;
        index += 1;
        break;
      case '--root':
        options.projectRoot = value;
        index += 1;
        break;
      default:
        break;
    }
  }

  if (!options.domain || !options.entity) {
    throw new Error('Missing required arguments. Expected --domain and --entity.');
  }

  return {
    domain: options.domain,
    entity: options.entity,
    repositoryClass: options.repositoryClass,
    envVar: options.envVar,
    projectRoot: options.projectRoot ?? process.cwd(),
  };
}

async function ensureDir(targetPath: string): Promise<void> {
  await fs.mkdir(targetPath, { recursive: true });
}

function buildTestSource(options: CliOptions): string {
  const entityName = toPascalCase(options.entity);
  const camelEntity = toCamelCase(entityName);
  const repositoryClass = options.repositoryClass ?? `${entityName}PostgresRepository`;
  const domainKey = options.domain.toUpperCase();
  const envVar = options.envVar ?? `${domainKey}_DATABASE_URL`;
  const repoImport = `import { ${repositoryClass} } from '../../src/infrastructure/repositories/${camelEntity}-postgres.repository';`;

  const header = [
    '/**',
    ` * Integration test scaffold for ${repositoryClass}.`,
    ' * Connects to a live Postgres instance; skips automatically if env var is missing.',
    ' */',
  ].join('\n');

  return `${header}\n\nimport { Pool } from 'pg';\n${repoImport}\n\ndescribe('${repositoryClass}', () => {\n  const connectionString = process.env.${envVar};\n\n  if (!connectionString) {\n    it('is skipped because ${envVar} is not defined', () => {\n      expect(true).toBe(true);\n    });\n    return;\n  }\n\n  const pool = new Pool({ connectionString });\n  const repository = new ${repositoryClass}(pool);\n\n  afterAll(async () => {\n    await pool.end();\n  });\n\n  it('list returns an array', async () => {\n    const items = await repository.list();\n    expect(Array.isArray(items)).toBe(true);\n  });\n});\n`;
}

async function main(): Promise<void> {
  const options = parseArgs();
  const entityName = toPascalCase(options.entity);
  const targetDir = path.join(
    options.projectRoot,
    'domains',
    options.domain,
    'tests',
    'integration'
  );

  await ensureDir(targetDir);
  const outputPath = path.join(targetDir, `${toCamelCase(entityName)}.repository.spec.ts`);
  const content = buildTestSource(options);
  await fs.writeFile(outputPath, content, 'utf-8');
  console.log(`Generated integration test at ${outputPath}`);
}

main().catch((error) => {
  console.error('[test-generator] Failed:', error);
  process.exit(1);
});