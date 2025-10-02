#!/usr/bin/env ts-node
/**
 * Domain bootstrap generator wires repository and services together for a domain slice.
 */
import { promises as fs } from 'fs';
import path from 'path';

interface CliOptions {
  domain: string;
  entity: string;
  projectRoot: string;
  repositoryClass?: string;
  serviceClass?: string;
  route?: string;
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
      case '--service-class':
        options.serviceClass = value;
        index += 1;
        break;
      case '--route':
        options.route = value;
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
    projectRoot: options.projectRoot ?? process.cwd(),
    repositoryClass: options.repositoryClass,
    serviceClass: options.serviceClass,
    route: options.route,
  };
}

async function ensureDir(targetPath: string): Promise<void> {
  await fs.mkdir(targetPath, { recursive: true });
}

function buildBootstrapSource(options: CliOptions): string {
  const entityName = toPascalCase(options.entity);
  const repositoryClass = options.repositoryClass ?? `${entityName}PostgresRepository`;
  const serviceClass = options.serviceClass ?? `${entityName}Service`;
  const camelEntity = toCamelCase(entityName);
  const routerName = `${camelEntity}Router`;
  const route = options.route ?? `/${camelEntity}`;

  const header = [
    '/**',
    ` * Bootstrap for ${entityName} domain slice generated via CRM toolkit.`,
    ' * Exposes a lightweight initializer returning repository/service/router trio.',
    ' */',
  ].join('\n');

  const repositoryImport = `import { ${repositoryClass} } from '../../infrastructure/repositories/${camelEntity}-postgres.repository';`;
  const serviceImport = `import { ${serviceClass} } from '../services/${camelEntity}.service';`;
  const controllerImport = `import { build${entityName}Router } from '../../presentation/controllers/${camelEntity}.controller';`;

  return `${header}\n\nimport { Pool } from 'pg';\n${repositoryImport}\n${serviceImport}\n${controllerImport}\n\nexport interface ${entityName}BootstrapDependencies {\n  pool: Pool;\n}\n\nexport function init${entityName}Module({ pool }: ${entityName}BootstrapDependencies) {\n  const repository = new ${repositoryClass}(pool);\n  const service = new ${serviceClass}(repository);\n  const router = build${entityName}Router({ service, baseRoute: '${route}' });\n\n  return { repository, service, router };\n}\n`;
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
    'bootstrap'
  );

  await ensureDir(targetDir);
  const outputPath = path.join(targetDir, `${toCamelCase(entityName)}.bootstrap.ts`);
  const content = buildBootstrapSource(options);
  await fs.writeFile(outputPath, content, 'utf-8');
  console.log(`Generated bootstrap at ${outputPath}`);
}

main().catch((error) => {
  console.error('[domain-bootstrap-generator] Failed:', error);
  process.exit(1);
});