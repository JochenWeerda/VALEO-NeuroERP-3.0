#!/usr/bin/env ts-node
/**
 * Entity generator for VALEO NeuroERP migration tooling.
 *
 * Usage:
 *   npx ts-node --transpile-only tools/codegen/entity_generator.ts --domain crm --entity Customer --schema schemas/customer.json
 */
import { promises as fs } from 'fs';
import path from 'path';

type FieldDefinition = {
  name: string;
  type: string;
  optional?: boolean;
  description?: string;
};

type SchemaFile = {
  fields: FieldDefinition[];
  aggregateRoot?: boolean;
};

interface CliOptions {
  domain: string;
  entity: string;
  schemaPath: string;
  projectRoot: string;
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
  };
}

function mapToTypeScript(fieldType: string): string {
  const lowered = fieldType.toLowerCase();

  if (lowered.includes('uuid')) {
    return 'string';
  }
  if (lowered.includes('char') || lowered.includes('text')) {
    return 'string';
  }
  if (lowered.includes('json')) {
    return 'Record<string, unknown>';
  }
  if (lowered.includes('bool')) {
    return 'boolean';
  }
  if (lowered.includes('decimal') || lowered.includes('numeric') || lowered.includes('float') || lowered.includes('double') || lowered.includes('number')) {
    return 'number';
  }
  if (lowered.includes('int')) {
    return 'number';
  }
  if (lowered.includes('date') || lowered.includes('time')) {
    return 'Date';
  }
  return 'string';
}

function buildPropsInterface(entityName: string, schema: SchemaFile): string {
  const lines = schema.fields.map((field) => {
    const isOptional = Boolean(field.optional || field.nullable || field.default !== null);
    const optionalFlag = isOptional ? '?' : '';
    const description = field.description ? `  // ${field.description}` : '';
    return `  ${field.name}${optionalFlag}: ${mapToTypeScript(field.type)};${description}`;
  });

  return `export interface ${entityName}Props {\n${lines.join('\n')}\n}`;
}

function buildClass(entityName: string, schema: SchemaFile): string {
  const body: string[] = [];

  body.push(`  private constructor(private readonly props: ${entityName}Props) {}`);
  body.push('');
  body.push('  public static create(props: ' + entityName + 'Props): ' + entityName + ' {');
  body.push('    return new ' + entityName + '(props);');
  body.push('  }');
  body.push('');

  schema.fields.forEach((field) => {
    const tsType = mapToTypeScript(field.type);
    const camelName = toCamelCase(field.name);
    const doc = field.description ? `  /** ${field.description} */\n` : '';
    const isOptional = Boolean(field.optional || field.nullable || field.default !== null);
    const returnType = isOptional ? `${tsType} | undefined` : tsType;
    body.push(`${doc}  public get ${camelName}(): ${returnType} {`);
    body.push(`    return this.props.${field.name};`);
    body.push('  }');
    body.push('');
  });

  body.push('  public toPrimitives(): ' + entityName + 'Props {');
  body.push('    return { ...this.props };');
  body.push('  }');

  return `export class ${entityName} {\n${body.join('\n')}\n}`;
}

function buildFile(entityName: string, schema: SchemaFile): string {
  const header = [
    '/**',
    ` * ${entityName} domain entity generated from CRM migration toolkit.`,
    ' * Keep the structure focused on pure data/behavior, no infrastructure here.',
    ' */',
  ].join('\n');

  const propsInterface = buildPropsInterface(entityName, schema);
  const entityClass = buildClass(entityName, schema);

  return `${header}\n\n${propsInterface}\n\n${entityClass}\n`;
}

async function ensureDir(targetPath: string): Promise<void> {
  await fs.mkdir(targetPath, { recursive: true });
}

async function main(): Promise<void> {
  const options = parseArgs();
  const entityName = toPascalCase(options.entity);
  const schemaAbsolutePath = path.resolve(options.projectRoot, options.schemaPath);
  const schemaContent = await fs.readFile(schemaAbsolutePath, 'utf-8');
  const schema: SchemaFile = JSON.parse(schemaContent);

  if (!schema.fields || !Array.isArray(schema.fields)) {
    throw new Error('Schema file must contain a "fields" array.');
  }

  const targetDir = path.join(
    options.projectRoot,
    'domains',
    options.domain,
    'src',
    'core',
    'entities'
  );

  await ensureDir(targetDir);

  const outputPath = path.join(targetDir, `${toCamelCase(entityName)}.entity.ts`);
  const fileContent = buildFile(entityName, schema);
  await fs.writeFile(outputPath, fileContent, 'utf-8');

  console.log(`Generated entity at ${outputPath}`);
}

main().catch((error) => {
  console.error('[entity-generator] Failed:', error);
  process.exit(1);
});