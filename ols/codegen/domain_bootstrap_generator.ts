#!/usr/bin/env ts-node

/**
 * VALEO NeuroERP 3.0 - Domain Bootstrap Generator
 *
 * Generates domain initialization code following MSOA patterns.
 * Used for CRM, ERP, Analytics, Integration domains.
 *
 * Usage: npx ts-node tools/codegen/domain_bootstrap_generator.ts <domain-name>
 */

import * as fs from 'fs';
import * as path from 'path';

interface DomainConfig {
  name: string;
  entities: string[];
  repositories: string[];
  services: string[];
  hasDatabase: boolean;
  hasExternalApi: boolean;
}

const DOMAIN_CONFIGS: Record<string, DomainConfig> = {
  crm: {
    name: 'crm',
    entities: ['Customer', 'Contact', 'Opportunity'],
    repositories: ['CustomerRepository'],
    services: ['CustomerDomainService'],
    hasDatabase: true,
    hasExternalApi: true
  },
  erp: {
    name: 'erp',
    entities: ['Product', 'Order', 'Inventory'],
    repositories: ['ProductRepository', 'OrderRepository', 'InventoryRepository'],
    services: ['ERPDomainService'],
    hasDatabase: true,
    hasExternalApi: false
  },
  analytics: {
    name: 'analytics',
    entities: ['Report', 'Dashboard', 'Metric'],
    repositories: ['AnalyticsRepository'],
    services: ['AnalyticsDomainService'],
    hasDatabase: true,
    hasExternalApi: false
  },
  integration: {
    name: 'integration',
    entities: ['Webhook', 'SyncJob', 'ApiKey'],
    repositories: ['IntegrationRepository'],
    services: ['IntegrationDomainService'],
    hasDatabase: true,
    hasExternalApi: true
  }
};

function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function generateBootstrapCode(config: DomainConfig): string {
  const domainName = config.name;
  const domainNameUpper = domainName.toUpperCase();

  let code = `/**
 * VALEO NeuroERP 3.0 - ${capitalize(domainName)} Domain Bootstrap
 *
 * Initializes the ${capitalize(domainName)} domain with all dependencies.
 * Follows MSOA architecture patterns with dependency injection.
 */

import { ServiceLocator } from '@packages/utilities/service-locator';
import { PostgresConnection } from '@packages/utilities/postgres';

// Import domain components
`;

  // Import entities
  config.entities.forEach(entity => {
    code += `import { ${entity} } from '../core/entities/${entity.toLowerCase()}';\n`;
  });

  // Import repositories
  config.repositories.forEach(repo => {
    code += `import { ${repo} } from '../infrastructure/repositories/${repo.replace('Repository', '').toLowerCase()}-repository';\n`;
  });

  // Import services
  config.services.forEach(service => {
    code += `import { ${service} } from '../core/domain-services/${service.replace('DomainService', '').toLowerCase()}-domain-service';\n`;
  });

  // Import controllers
  code += `import { ${capitalize(domainName)}ApiController } from '../presentation/controllers/${domainName}-api-controller';\n\n`;

  code += `export interface ${capitalize(domainName)}DomainConfig {\n`;
  if (config.hasDatabase) {
    code += `  databaseUrl: string;\n`;
  }
  if (config.hasExternalApi) {
    code += `  serviceUrl?: string;\n`;
    code += `  serviceToken?: string;\n`;
  }
  code += `  environment: 'development' | 'production' | 'test';\n`;
  code += `}\n\n`;

  code += `export class ${capitalize(domainName)}DomainBootstrap {\n`;
  code += `  private serviceLocator: ServiceLocator;\n`;
  code += `  private config: ${capitalize(domainName)}DomainConfig;\n\n`;

  code += `  constructor(config: ${capitalize(domainName)}DomainConfig) {\n`;
  code += `    this.config = config;\n`;
  code += `    this.serviceLocator = new ServiceLocator();\n`;
  code += `  }\n\n`;

  code += `  async initialize(): Promise<void> {\n`;
  code += `    console.log('Initializing ${capitalize(domainName)} domain...');\n\n`;

  if (config.hasDatabase) {
    code += `    // Initialize database connection\n`;
    code += `    const dbConnection = new PostgresConnection(this.config.databaseUrl);\n`;
    code += `    await dbConnection.connect();\n`;
    code += `    this.serviceLocator.register('DatabaseConnection', dbConnection);\n\n`;
  }

  // Register repositories
  config.repositories.forEach(repo => {
    const repoVar = repo.replace('Repository', '').toLowerCase() + 'Repository';
    code += `    // Register ${repo}\n`;
    if (config.hasDatabase) {
      code += `    const ${repoVar} = new ${repo}(dbConnection);\n`;
    } else {
      code += `    const ${repoVar} = new ${repo}();\n`;
    }
    code += `    this.serviceLocator.register('${repo}', ${repoVar});\n\n`;
  });

  // Register services
  config.services.forEach(service => {
    const serviceVar = service.replace('DomainService', '').toLowerCase() + 'Service';
    code += `    // Register ${service}\n`;
    const deps = config.repositories.map(repo => repo.replace('Repository', '').toLowerCase() + 'Repository').join(', ');
    code += `    const ${serviceVar} = new ${service}(${deps});\n`;
    code += `    this.serviceLocator.register('${service}', ${serviceVar});\n\n`;
  });

  // Register controller
  code += `    // Register API Controller\n`;
  const serviceDeps = config.services.map(service => service.replace('DomainService', '').toLowerCase() + 'Service').join(', ');
  code += `    const ${domainName}Controller = new ${capitalize(domainName)}ApiController(${serviceDeps});\n`;
  code += `    this.serviceLocator.register('${capitalize(domainName)}Controller', ${domainName}Controller);\n\n`;

  code += `    console.log('${capitalize(domainName)} domain initialized successfully');\n`;
  code += `  }\n\n`;

  code += `  getServiceLocator(): ServiceLocator {\n`;
  code += `    return this.serviceLocator;\n`;
  code += `  }\n\n`;

  code += `  async shutdown(): Promise<void> {\n`;
  code += `    console.log('Shutting down ${capitalize(domainName)} domain...');\n`;

  if (config.hasDatabase) {
    code += `    const dbConnection = this.serviceLocator.resolve<PostgresConnection>('DatabaseConnection');\n`;
    code += `    await dbConnection.disconnect();\n`;
  }

  code += `    console.log('${capitalize(domainName)} domain shutdown complete');\n`;
  code += `  }\n`;
  code += `}\n\n`;

  // Environment-based factory
  code += `// Environment-based bootstrap factory\n`;
  code += `export function create${capitalize(domainName)}Bootstrap(): ${capitalize(domainName)}DomainBootstrap {\n`;
  code += `  const config: ${capitalize(domainName)}DomainConfig = {\n`;
  if (config.hasDatabase) {
    code += `    databaseUrl: process.env.${domainNameUpper}_DATABASE_URL || 'postgresql://localhost:5432/${domainName}_db',\n`;
  }
  if (config.hasExternalApi) {
    code += `    serviceUrl: process.env.${domainNameUpper}_SERVICE_URL,\n`;
    code += `    serviceToken: process.env.${domainNameUpper}_SERVICE_TOKEN,\n`;
  }
  code += `    environment: (process.env.NODE_ENV as any) || 'development'\n`;
  code += `  };\n\n`;
  code += `  return new ${capitalize(domainName)}DomainBootstrap(config);\n`;
  code += `}\n`;

  return code;
}

function main() {
  const domainName = process.argv[2];

  if (!domainName) {
    console.error('Usage: npx ts-node tools/codegen/domain_bootstrap_generator.ts <domain-name>');
    console.error('Available domains: crm, erp, analytics, integration');
    process.exit(1);
  }

  const config = DOMAIN_CONFIGS[domainName];
  if (!config) {
    console.error(`Unknown domain: ${domainName}`);
    console.error('Available domains: crm, erp, analytics, integration');
    process.exit(1);
  }

  const bootstrapCode = generateBootstrapCode(config);
  const outputPath = path.join(__dirname, '../../domains', domainName, 'src', 'bootstrap.ts');

  // Ensure directory exists
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(outputPath, bootstrapCode, 'utf8');
  console.log(`Generated bootstrap code for ${domainName} domain at: ${outputPath}`);
}

if (require.main === module) {
  main();
}