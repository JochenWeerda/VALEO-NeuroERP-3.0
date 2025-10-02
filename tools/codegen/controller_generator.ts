#!/usr/bin/env ts-node
/**
 * Controller generator for Express routers.
 */
import { promises as fs } from 'fs';
import path from 'path';

interface CliOptions {
  domain: string;
  entity: string;
  projectRoot: string;
  serviceImport?: string;
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
      case '--service-import':
        options.serviceImport = value;
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
    serviceImport: options.serviceImport,
  };
}

async function ensureDir(targetPath: string): Promise<void> {
  await fs.mkdir(targetPath, { recursive: true });
}

function buildControllerSource(options: CliOptions): string {
  const entityName = toPascalCase(options.entity);
  const camelEntity = toCamelCase(entityName);
  const serviceInterface = `${entityName}Service`;
  const serviceImport = options.serviceImport ?? `../../application/services/${camelEntity}.service`;
  const header = [
    '/**',
    ` * Express router for ${entityName} generated via CRM toolkit.`,
    ' * Provides baseline CRUD endpoints; extend with domain-specific routes.',
    ' */',
  ].join('\n');

  const routeWithId = '`' + '${' + 'baseRoute}/:' + `${camelEntity}Id` + '`';

  return `${header}\n\nimport { Router, Request, Response } from 'express';\nimport { ${serviceInterface} } from '${serviceImport}';\n\nexport interface ${entityName}RouterDependencies {\n  service: ${serviceInterface};\n  baseRoute?: string;\n}\n\nexport function build${entityName}Router({ service, baseRoute = '/${camelEntity}' }: ${entityName}RouterDependencies) {\n  const router = Router();\n\n  router.get(baseRoute, async (_req: Request, res: Response) => {\n    const result = await service.list();\n    res.json(result);\n  });\n\n  router.get(${routeWithId}, async (req: Request, res: Response) => {\n    const entity = await service.findById(req.params.${camelEntity}Id);\n    if (!entity) {\n      res.status(404).json({ message: '${entityName} not found' });\n      return;\n    }\n    res.json(entity);\n  });\n\n  router.post(baseRoute, async (req: Request, res: Response) => {\n    const created = await service.create(req.body);\n    res.status(201).json(created);\n  });\n\n  router.put(${routeWithId}, async (req: Request, res: Response) => {\n    const updated = await service.update(req.params.${camelEntity}Id, req.body);\n    res.json(updated);\n  });\n\n  router.delete(${routeWithId}, async (req: Request, res: Response) => {\n    await service.remove(req.params.${camelEntity}Id);\n    res.status(204).send();\n  });\n\n  return router;\n}\n`;
}

async function main(): Promise<void> {
  const options = parseArgs();
  const entityName = toPascalCase(options.entity);
  const targetDir = path.join(
    options.projectRoot,
    'domains',
    options.domain,
    'src',
    'presentation',
    'controllers'
  );

  await ensureDir(targetDir);

  const outputPath = path.join(targetDir, `${toCamelCase(entityName)}.controller.ts`);
  const content = buildControllerSource(options);
  await fs.writeFile(outputPath, content, 'utf-8');
  console.log(`Generated controller at ${outputPath}`);
}

main().catch((error) => {
  console.error('[controller-generator] Failed:', error);
  process.exit(1);
});