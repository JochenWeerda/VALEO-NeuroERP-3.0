#!/usr/bin/env ts-node
/**
 * Service generator to wire repository operations with business logic placeholders.
 */
import { promises as fs } from 'fs';
import path from 'path';

interface CliOptions {
  domain: string;
  entity: string;
  projectRoot: string;
  repositoryClass?: string;
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
    projectRoot: options.projectRoot ?? process.cwd(),
  };
}

async function ensureDir(targetPath: string): Promise<void> {
  await fs.mkdir(targetPath, { recursive: true });
}

function buildServiceSource(options: CliOptions): string {
  const entityName = toPascalCase(options.entity);
  const camelEntity = toCamelCase(entityName);
  const repositoryClass = options.repositoryClass ?? `${entityName}PostgresRepository`;
  const entityImport = `import { ${entityName} } from '../../core/entities/${camelEntity}.entity';`;
  const repositoryImport = `import { ${repositoryClass} } from '../../infrastructure/repositories/${camelEntity}-postgres.repository';`;

  const header = [
    '/**',
    ` * Application service for ${entityName} generated via CRM toolkit.`,
    ' * Encapsulates use-cases and translates primitives to domain entities.',
    ' */',
  ].join('\n');

  return `${header}\n\n${entityImport}\n${repositoryImport}\n\nexport interface Create${entityName}Dto {\n  // Define DTO fields mirroring your schema. The generator keeps it simple intentionally.\n  [key: string]: unknown;\n}\n\nexport class ${entityName}Service {\n  public constructor(private readonly repository: ${repositoryClass}) {}\n\n  public async list(): Promise<${entityName}[]> {\n    return this.repository.list();\n  }\n\n  public async findById(id: string): Promise<${entityName} | null> {\n    return this.repository.findById(id);\n  }\n\n  public async create(payload: Create${entityName}Dto): Promise<${entityName}> {\n    const entity = ${entityName}.create(payload as any);\n    await this.repository.save(entity);\n    return entity;\n  }\n\n  public async update(id: string, payload: Partial<Create${entityName}Dto>): Promise<${entityName}> {\n    const existing = await this.repository.findById(id);\n    if (!existing) {\n      throw new Error('${entityName} not found');\n    }\n    const merged = { ...existing.toPrimitives(), ...payload };\n    const entity = ${entityName}.create(merged as any);\n    await this.repository.update(entity);\n    return entity;\n  }\n\n  public async remove(id: string): Promise<void> {\n    await this.repository.delete(id);\n  }\n}\n`;
}

async function main(): Promise<void> {
  const options = parseArgs();
  const entityName = toPascalCase(options.entity);
  const targetDir = path.join(
    options.projectRoot,
    'domains',
    options.domain,
    'src',
    'application',
    'services'
  );

  await ensureDir(targetDir);
  const outputPath = path.join(targetDir, `${toCamelCase(entityName)}.service.ts`);
  const content = buildServiceSource(options);
  await fs.writeFile(outputPath, content, 'utf-8');
  console.log(`Generated service at ${outputPath}`);
}

main().catch((error) => {
  console.error('[service-generator] Failed:', error);
  process.exit(1);
});