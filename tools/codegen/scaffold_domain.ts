#!/usr/bin/env ts-node
/**
 * Orchestrator to scaffold a domain slice (entity -> repository -> service -> controller -> bootstrap -> tests).
 */
import { spawnSync } from 'child_process';
import path from 'path';

interface CliOptions {
  domain: string;
  entity: string;
  schema: string;
  route?: string;
  projectRoot: string;
  skipTests: boolean;
}

function parseArgs(): CliOptions {
  const args = process.argv.slice(2);
  const options: Partial<CliOptions> = { projectRoot: path.resolve(__dirname, '..', '..') };

  for (let index = 0; index < args.length; index += 1) {
    const key = args[index];
    const value = args[index + 1];

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
        options.schema = value;
        index += 1;
        break;
      case '--route':
        options.route = value;
        index += 1;
        break;
      case '--root':
        options.projectRoot = path.resolve(value);
        index += 1;
        break;
      case '--skip-tests':
        options.skipTests = true;
        break;
      default:
        break;
    }
  }

  if (!options.domain || !options.entity || !options.schema) {
    throw new Error('Missing required arguments. Expected --domain, --entity, --schema.');
  }

  return {
    domain: options.domain,
    entity: options.entity,
    schema: options.schema,
    route: options.route,
    projectRoot: options.projectRoot!,
    skipTests: options.skipTests ?? false,
  };
}

interface Step {
  name: string;
  script: string;
  args: string[];
  enabled: boolean;
}

function runStep(step: Step, cwd: string): void {
  if (!step.enabled) {
    console.log(`[scaffold-domain] Skipping ${step.name}`);
    return;
  }

  const scriptPath = path.join('tools', 'codegen', step.script);
  const command = ['node', '--loader', 'ts-node/esm', scriptPath, ...step.args];
  console.log(`[scaffold-domain] Running ${step.name}: ${command.join(' ')});
  const result = spawnSync(command[0], command.slice(1), { stdio: 'inherit', cwd });
  if (result.status !== 0) {
    throw new Error(`${step.name} failed with exit code ${result.status}`);
  }
}

function main(): void {
  const options = parseArgs();
  const cwd = options.projectRoot;
  const schemaPath = path.isAbsolute(options.schema)
    ? options.schema
    : path.join(cwd, options.schema);

  const route = options.route ?? `/${options.entity.toLowerCase()}`;

  const steps: Step[] = [
    {
      name: 'entity-generator',
      script: 'entity_generator.ts',
      args: ['--domain', options.domain, '--entity', options.entity, '--schema', schemaPath, '--root', cwd],
      enabled: true,
    },
    {
      name: 'repository-generator',
      script: 'repository_generator.ts',
      args: ['--domain', options.domain, '--entity', options.entity, '--schema', schemaPath, '--root', cwd],
      enabled: true,
    },
    {
      name: 'service-generator',
      script: 'service_generator.ts',
      args: ['--domain', options.domain, '--entity', options.entity, '--root', cwd],
      enabled: true,
    },
    {
      name: 'controller-generator',
      script: 'controller_generator.ts',
      args: ['--domain', options.domain, '--entity', options.entity, '--root', cwd],
      enabled: true,
    },
    {
      name: 'bootstrap-generator',
      script: 'domain_bootstrap_generator.ts',
      args: ['--domain', options.domain, '--entity', options.entity, '--route', route, '--root', cwd],
      enabled: true,
    },
    {
      name: 'test-generator',
      script: 'test_generator.ts',
      args: ['--domain', options.domain, '--entity', options.entity, '--root', cwd],
      enabled: !options.skipTests,
    },
  ];

  steps.forEach((step) => runStep(step, cwd));
  console.log('[scaffold-domain] Completed scaffold successfully.');
}

main();
