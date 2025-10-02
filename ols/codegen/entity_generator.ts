#!/usr/bin/env ts-node

/**
 * VALEO NeuroERP 3.0 - Entity Generator
 *
 * Generates domain entities with branded types following DDD patterns.
 * Creates entities with validation, business rules, and domain events.
 *
 * Usage: npx ts-node tools/codegen/entity_generator.ts <domain-name> <entity-name> [properties...]
 */

import * as fs from 'fs';
import * as path from 'path';

interface EntityProperty {
  name: string;
  type: string;
  optional?: boolean;
  validation?: string[];
}

interface EntityConfig {
  name: string;
  domain: string;
  properties: EntityProperty[];
}

function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function generateBrandedType(entityName: string): string {
  const idType = `${entityName}Id`;

  return `/**
 * Branded type for ${entityName} ID to ensure type safety
 */
export type ${idType} = string & { readonly __brand: '${idType}' };

/**
 * Creates a branded ${entityName} ID
 */
export function create${idType}(value: string): ${idType} {
  if (!value || typeof value !== 'string') {
    throw new Error('Invalid ${entityName} ID: must be a non-empty string');
  }
  return value as ${idType};
}

/**
 * Type guard for ${idType}
 */
export function is${idType}(value: any): value is ${idType} {
  return typeof value === 'string' && value.length > 0;
}`;
}

function generateEntity(config: EntityConfig): string {
  const entityName = config.name;
  const idType = `${entityName}Id`;

  let code = `/**
 * VALEO NeuroERP 3.0 - ${entityName} Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */

import { ${idType}, create${idType} } from '@packages/data-models/branded-types';
import { DomainEvent } from '@packages/data-models/domain-events';

export interface ${entityName} {
  readonly id: ${idType};
`;

  // Add properties
  config.properties.forEach(prop => {
    if (prop.name !== 'id') {
      const optional = prop.optional ? '?' : '';
      code += `  ${prop.name}${optional}: ${prop.type};\n`;
    }
  });

  code += `  readonly createdAt: Date;\n`;
  code += `  readonly updatedAt: Date;\n`;
  code += `}\n\n`;

  // Create command
  code += `export interface Create${entityName}Command {\n`;
  config.properties.forEach(prop => {
    if (prop.name !== 'id' && prop.name !== 'createdAt' && prop.name !== 'updatedAt') {
      const optional = prop.optional ? '?' : '';
      code += `  ${prop.name}${optional}: ${prop.type};\n`;
    }
  });
  code += `}\n\n`;

  // Update command
  code += `export interface Update${entityName}Command {\n`;
  config.properties.forEach(prop => {
    if (prop.name !== 'id' && prop.name !== 'createdAt' && prop.name !== 'updatedAt') {
      code += `  ${prop.name}?: ${prop.type};\n`;
    }
  });
  code += `}\n\n`;

  // Domain events
  code += `export class ${entityName}CreatedEvent implements DomainEvent {\n`;
  code += `  readonly type = '${entityName}Created';\n`;
  code += `  readonly aggregateId: ${idType};\n`;
  code += `  readonly occurredAt: Date;\n\n`;
  code += `  constructor(\n`;
  code += `    public readonly ${entityName.toLowerCase()}: ${entityName}\n`;
  code += `  ) {\n`;
  code += `    this.aggregateId = ${entityName.toLowerCase()}.id;\n`;
  code += `    this.occurredAt = new Date();\n`;
  code += `  }\n`;
  code += `}\n\n`;

  code += `export class ${entityName}UpdatedEvent implements DomainEvent {\n`;
  code += `  readonly type = '${entityName}Updated';\n`;
  code += `  readonly aggregateId: ${idType};\n`;
  code += `  readonly occurredAt: Date;\n\n`;
  code += `  constructor(\n`;
  code += `    public readonly ${entityName.toLowerCase()}: ${entityName},\n`;
  code += `    public readonly changes: Record<string, any>\n`;
  code += `  ) {\n`;
  code += `    this.aggregateId = ${entityName.toLowerCase()}.id;\n`;
  code += `    this.occurredAt = new Date();\n`;
  code += `  }\n`;
  code += `}\n\n`;

  // Entity class
  code += `export class ${entityName}Entity implements ${entityName} {\n`;
  code += `  public readonly id: ${idType};\n`;

  config.properties.forEach(prop => {
    if (prop.name !== 'id') {
      const optional = prop.optional ? '?' : '';
      code += `  public ${prop.name}${optional}: ${prop.type};\n`;
    }
  });

  code += `  public readonly createdAt: Date;\n`;
  code += `  public readonly updatedAt: Date;\n\n`;

  // Constructor
  code += `  private constructor(\n`;
  code += `    id: ${idType},\n`;
  config.properties.forEach(prop => {
    if (prop.name !== 'id') {
      const optional = prop.optional ? '?' : '';
      code += `    ${prop.name}${optional}: ${prop.type},\n`;
    }
  });
  code += `    createdAt: Date,\n`;
  code += `    updatedAt: Date\n`;
  code += `  ) {\n`;
  code += `    this.id = id;\n`;
  config.properties.forEach(prop => {
    if (prop.name !== 'id') {
      code += `    this.${prop.name} = ${prop.name};\n`;
    }
  });
  code += `    this.createdAt = createdAt;\n`;
  code += `    this.updatedAt = updatedAt;\n`;
  code += `  }\n\n`;

  // Static factory method
  code += `  static create(command: Create${entityName}Command): ${entityName}Entity {\n`;
  code += `    // Validate command\n`;
  code += `    ${entityName}Entity.validateCreateCommand(command);\n\n`;
  code += `    const id = create${idType}(crypto.randomUUID());\n`;
  code += `    const now = new Date();\n\n`;
  code += `    return new ${entityName}Entity(\n`;
  code += `      id,\n`;
  config.properties.forEach(prop => {
    if (prop.name !== 'id') {
      const defaultValue = prop.optional ? 'undefined' : getDefaultValue(prop.type);
      code += `      command.${prop.name} ?? ${defaultValue},\n`;
    }
  });
  code += `      now,\n`;
  code += `      now\n`;
  code += `    );\n`;
  code += `  }\n\n`;

  // Update method
  code += `  update(command: Update${entityName}Command): ${entityName}Entity {\n`;
  code += `    // Validate command\n`;
  code += `    ${entityName}Entity.validateUpdateCommand(command);\n\n`;
  code += `    const changes: Record<string, any> = {};\n\n`;
  config.properties.forEach(prop => {
    if (prop.name !== 'id' && prop.name !== 'createdAt' && prop.name !== 'updatedAt') {
      code += `    if (command.${prop.name} !== undefined) {\n`;
      code += `      this.${prop.name} = command.${prop.name};\n`;
      code += `      changes.${prop.name} = command.${prop.name};\n`;
      code += `    }\n`;
    }
  });
  code += `\n`;
  code += `    (this as any).updatedAt = new Date();\n`;
  code += `    changes.updatedAt = this.updatedAt;\n\n`;
  code += `    return this;\n`;
  code += `  }\n\n`;

  // Business methods
  code += `  // Business methods\n`;
  code += `  isActive(): boolean {\n`;
  if (config.properties.some(p => p.name === 'status')) {
    code += `    return this.status === 'active';\n`;
  } else {
    code += `    return true; // Default implementation\n`;
  }
  code += `  }\n\n`;

  // Validation methods
  code += `  // Validation methods\n`;
  code += `  private static validateCreateCommand(command: Create${entityName}Command): void {\n`;
  code += `    if (!command.name || command.name.trim().length === 0) {\n`;
  code += `      throw new Error('${entityName} name is required');\n`;
  code += `    }\n`;
  code += `    // Add additional validation rules here\n`;
  code += `  }\n\n`;

  code += `  private static validateUpdateCommand(command: Update${entityName}Command): void {\n`;
  code += `    // Add update validation rules here\n`;
  code += `  }\n`;

  code += `}\n\n`;

  // Utility functions
  code += `// Utility functions\n`;
  code += `function getDefaultValue(type: string): any {\n`;
  code += `  switch (type) {\n`;
  code += `    case 'string': return '';\n`;
  code += `    case 'number': return 0;\n`;
  code += `    case 'boolean': return false;\n`;
  code += `    case 'Date': return new Date();\n`;
  code += `    default: return null;\n`;
  code += `  }\n`;
  code += `}\n`;

  return code;
}

function getDefaultValue(type: string): string {
  switch (type) {
    case 'string': return "''";
    case 'number': return '0';
    case 'boolean': return 'false';
    case 'Date': return 'new Date()';
    default: return 'undefined';
  }
}

function main() {
  const domainName = process.argv[2];
  const entityName = process.argv[3];

  if (!domainName || !entityName) {
    console.error('Usage: npx ts-node tools/codegen/entity_generator.ts <domain-name> <entity-name> [property1:type] [property2:type?] ...');
    console.error('Example: npx ts-node tools/codegen/entity_generator.ts crm Customer name:string email:string status?:string');
    process.exit(1);
  }

  // Parse additional properties from command line
  const properties: EntityProperty[] = [
    { name: 'name', type: 'string' },
    { name: 'status', type: 'string', optional: true }
  ];

  // Add command line properties
  for (let i = 4; i < process.argv.length; i++) {
    const propArg = process.argv[i];
    const [name, typeWithOptional] = propArg.split(':');
    const isOptional = typeWithOptional?.endsWith('?');
    const type = typeWithOptional?.replace('?', '') || 'string';

    if (name && !properties.some(p => p.name === name)) {
      properties.push({ name, type, optional: isOptional });
    }
  }

  const entityConfig: EntityConfig = {
    name: entityName,
    domain: domainName,
    properties
  };

  const basePath = path.join(__dirname, '../../domains', domainName, 'src', 'core', 'entities');

  // Ensure directory exists
  if (!fs.existsSync(basePath)) {
    fs.mkdirSync(basePath, { recursive: true });
  }

  // Generate branded type
  const brandedTypeCode = generateBrandedType(entityName);
  const brandedTypePath = path.join(__dirname, '../../packages/data-models/src/branded-types.ts');

  // Check if branded types file exists, if not create it
  let existingBrandedTypes = '';
  if (fs.existsSync(brandedTypePath)) {
    existingBrandedTypes = fs.readFileSync(brandedTypePath, 'utf8');
  }

  // Append new branded type if not already present
  if (!existingBrandedTypes.includes(`export type ${entityName}Id`)) {
    const updatedBrandedTypes = existingBrandedTypes + '\n' + brandedTypeCode;
    fs.writeFileSync(brandedTypePath, updatedBrandedTypes, 'utf8');
    console.log(`Updated branded types: ${brandedTypePath}`);
  }

  // Generate entity
  const entityCode = generateEntity(entityConfig);
  const entityPath = path.join(basePath, `${entityName.toLowerCase()}.ts`);
  fs.writeFileSync(entityPath, entityCode, 'utf8');
  console.log(`Generated entity: ${entityPath}`);

  console.log(`\nEntity generation complete for ${entityName} in ${domainName} domain!`);
  console.log('Generated files:');
  console.log(`- Branded Type: ${entityName}Id in @packages/data-models`);
  console.log(`- Entity: ${entityName}Entity with validation and domain events`);
  console.log(`- Commands: Create${entityName}Command, Update${entityName}Command`);
  console.log(`- Events: ${entityName}CreatedEvent, ${entityName}UpdatedEvent`);
}

if (require.main === module) {
  main();
}