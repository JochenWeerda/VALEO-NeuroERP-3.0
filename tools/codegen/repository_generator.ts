#!/usr/bin/env ts-node
/**
 * Repository generator to scaffold Postgres repositories based on schema metadata.
 *
 * Example:
 *   npx ts-node --transpile-only tools/codegen/repository_generator.ts \
 *     --domain crm --entity Customer --schema schemas/customer.json
 */
import { promises as fs } from 'fs';
import path from 'path';

type FieldDefinition = {
  name: string;
  column?: string;
  type: string;
  optional?: boolean;
};

type SchemaFile = {
  table: string;
  fields: FieldDefinition[];
  primaryKey?: string;
};

interface CliOptions {
  domain: string;
  entity: string;
  schemaPath: string;
  projectRoot: string;
  repositoryName?: string;
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

function resolveProjectRoot(): string {
  return process.cwd();
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
      case '--schema':
        options.schemaPath = value;
        index += 1;
        break;
      case '--repo-name':
        options.repositoryName = value;
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

  if (!options.domain || !options.entity || !options.schemaPath) {
    throw new Error('Missing required arguments. Expected --domain, --entity, and --schema.');
  }

  return {
    domain: options.domain,
    entity: options.entity,
    schemaPath: options.schemaPath,
    projectRoot: options.projectRoot ?? resolveProjectRoot(),
    repositoryName: options.repositoryName,
  };
}

function buildInsertColumns(fields: FieldDefinition[]): string {
  return fields.map((field) => field.column ?? field.name).join(', ');
}

function buildInsertValues(fields: FieldDefinition[]): string {
  return fields.map((_, index) => `$${index + 1}`).join(', ');
}

function buildUpdateAssignments(fields: FieldDefinition[], primaryKey: string): string {
  return fields
    .filter((field) => (field.column ?? field.name) !== primaryKey)
    .map((field, index) => `${field.column ?? field.name} = $${index + 2}`)
    .join(', ');
}

function buildFieldExtraction(fields: FieldDefinition[]): string {
  return fields
    .map((field) => `      ${field.name}: row['${field.column ?? field.name}'] as any,`)
    .join('\n');
}

function buildInsertParams(fields: FieldDefinition[]): string {
  return fields.map((field) => `primitives.${field.name}`).join(', ');
}

function buildUpdateParams(fields: FieldDefinition[], primaryKey: string): string {
  const ordered = [primaryKey, ...fields.filter((field) => (field.column ?? field.name) !== primaryKey).map((field) => field.name)];
  return ordered.map((name) => `primitives.${name}`).join(', ');
}

async function ensureDir(targetPath: string): Promise<void> {
  await fs.mkdir(targetPath, { recursive: true });
}

function buildRepositorySource(entityName: string, schema: SchemaFile, repositoryName: string): string {
  const modelImport = `import { ${entityName} } from '../../core/entities/${toCamelCase(entityName)}.entity';`;
  const selectColumns = schema.fields.map((field) => field.column ?? field.name).join(', ');
  const primaryKey = schema.primaryKey ?? schema.fields[0]?.name ?? 'id';
  const header = [
    '/**',
    ` * ${repositoryName} generated for ${entityName} using CRM migration toolkit.`,
    ' * Handles persistence with PostgreSQL using pg.Pool.',
    ' * Start simple: find -> save -> update -> delete -> list. Extend for joins later.',
    ' */',
  ].join('\n');

  const insertColumns = buildInsertColumns(schema.fields);
  const insertValues = buildInsertValues(schema.fields);
  const updateAssignments = buildUpdateAssignments(schema.fields, primaryKey);
  const fieldExtraction = buildFieldExtraction(schema.fields);
  const insertParams = buildInsertParams(schema.fields);
  const updateParams = buildUpdateParams(schema.fields, primaryKey);

  return `${header}\n\nimport { Pool } from 'pg';\n${modelImport}\n\ntype DbRow = Record<string, unknown>;\n\nexport class ${repositoryName} {\n  public constructor(private readonly pool: Pool) {}\n\n  private mapRow(row: DbRow): ${entityName} {\n    return ${entityName}.create({\n${fieldExtraction}\n    });\n  }\n\n  public async findById(id: string): Promise<${entityName} | null> {\n    const result = await this.pool.query(\n      'SELECT ${selectColumns} FROM ${schema.table} WHERE ${primaryKey} = $1 LIMIT 1',\n      [id]\n    );\n\n    if (result.rowCount === 0) {\n      return null;\n    }\n\n    return this.mapRow(result.rows[0]);\n  }\n\n  public async list(): Promise<${entityName}[]> {\n    const result = await this.pool.query('SELECT ${selectColumns} FROM ${schema.table} ORDER BY ${primaryKey} ASC');\n    return result.rows.map((row) => this.mapRow(row));\n  }\n\n  public async save(entity: ${entityName}): Promise<void> {\n    const primitives = entity.toPrimitives();\n    await this.pool.query(\n      'INSERT INTO ${schema.table} (${insertColumns}) VALUES (${insertValues}) ON CONFLICT (${primaryKey}) DO NOTHING',\n      [${insertParams}]\n    );\n  }\n\n  public async update(entity: ${entityName}): Promise<void> {\n    const primitives = entity.toPrimitives();\n    await this.pool.query(\n      'UPDATE ${schema.table} SET ${updateAssignments} WHERE ${primaryKey} = $1',\n      [${updateParams}]\n    );\n  }\n\n  public async delete(id: string): Promise<void> {\n    await this.pool.query('DELETE FROM ${schema.table} WHERE ${primaryKey} = $1', [id]);\n  }\n}\n`;
}

async function main(): Promise<void> {
  const options = parseArgs();
  const entityName = toPascalCase(options.entity);
  const repositoryName = options.repositoryName ?? `${entityName}PostgresRepository`;
  const schemaAbsolutePath = path.resolve(options.projectRoot, options.schemaPath);
  const schemaContent = await fs.readFile(schemaAbsolutePath, 'utf-8');
  const schema: SchemaFile = JSON.parse(schemaContent);

  if (!schema.fields || !Array.isArray(schema.fields) || schema.fields.length === 0) {
    throw new Error('Schema file must include at least one field definition.');
  }

  if (!schema.table) {
    throw new Error('Schema file must define the target table name under the "table" property.');
  }

  const targetDir = path.join(
    options.projectRoot,
    'domains',
    options.domain,
    'src',
    'infrastructure',
    'repositories'
  );

  await ensureDir(targetDir);

  const outputPath = path.join(targetDir, `${toCamelCase(entityName)}-postgres.repository.ts`);
  const content = buildRepositorySource(entityName, schema, repositoryName);
  await fs.writeFile(outputPath, content, 'utf-8');

  console.log(`Generated repository at ${outputPath}`);
}

main().catch((error) => {
  console.error('[repository-generator] Failed:', error);
  process.exit(1);
});