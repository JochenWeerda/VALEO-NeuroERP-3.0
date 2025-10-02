#!/usr/bin/env ts-node

/**
 * VALEO NeuroERP 3.0 - Repository Generator
 *
 * Generates repository interfaces and implementations following MSOA patterns.
 * Creates Postgres, REST, and In-Memory implementations for each domain entity.
 *
 * Usage: npx ts-node tools/codegen/repository_generator.ts <domain-name> <entity-name>
 */

import * as fs from 'fs';
import * as path from 'path';

interface EntityConfig {
  name: string;
  idType: string;
  properties: Array<{ name: string; type: string; optional?: boolean }>;
  domain: string;
}

function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function generateRepositoryInterface(entity: EntityConfig): string {
  const entityName = entity.name;
  const idType = entity.idType;
  const repositoryName = `${entityName}Repository`;

  let code = `/**
 * VALEO NeuroERP 3.0 - ${entityName} Repository Interface
 *
 * Defines the contract for ${entityName} data access operations.
 * Follows Repository pattern for clean data access abstraction.
 */

import { ${entityName} } from '../../core/entities/${entityName.toLowerCase()}';
import { ${idType} } from '@packages/data-models/branded-types';

export interface ${repositoryName} {
  // Basic CRUD operations
  findById(id: ${idType}): Promise<${entityName} | null>;
  findAll(): Promise<${entityName}[]>;
  create(entity: ${entityName}): Promise<void>;
  update(id: ${idType}, entity: ${entityName}): Promise<void>;
  delete(id: ${idType}): Promise<void>;

  // Query operations
  exists(id: ${idType}): Promise<boolean>;
  count(): Promise<number>;
`;

  // Add domain-specific query methods based on entity properties
  entity.properties.forEach(prop => {
    if (prop.name !== 'id' && prop.name !== 'createdAt' && prop.name !== 'updatedAt') {
      if (prop.type === 'string') {
        code += `  findBy${capitalize(prop.name)}(value: ${prop.type}): Promise<${entityName}[]>;\n`;
      } else if (prop.type === 'boolean') {
        code += `  findBy${capitalize(prop.name)}(value: ${prop.type}): Promise<${entityName}[]>;\n`;
      }
    }
  });

  code += `}\n`;

  return code;
}

function generatePostgresRepository(entity: EntityConfig): string {
  const entityName = entity.name;
  const repositoryName = `${entityName}Repository`;
  const tableName = entityName.toLowerCase() + 's';

  let code = `/**
 * VALEO NeuroERP 3.0 - Postgres ${entityName} Repository
 *
 * PostgreSQL implementation of ${entityName} repository.
 * Handles database operations with proper error handling and transactions.
 */

import { ${entityName} } from '../../core/entities/${entityName.toLowerCase()}';
import { ${entity.idType} } from '@packages/data-models/branded-types';
import { PostgresConnection } from '@packages/utilities/postgres';
import { ${repositoryName} } from './${entityName.toLowerCase()}-repository';

export class Postgres${repositoryName} implements ${repositoryName} {
  constructor(private db: PostgresConnection) {}

  async findById(id: ${entity.idType}): Promise<${entityName} | null> {
    const query = 'SELECT * FROM ${tableName} WHERE id = $1';
    const result = await this.db.query(query, [id]);

    if (result.rows.length === 0) {
      return null;
    }

    return this.mapRowToEntity(result.rows[0]);
  }

  async findAll(): Promise<${entityName}[]> {
    const query = 'SELECT * FROM ${tableName} ORDER BY created_at DESC';
    const result = await this.db.query(query);
    return result.rows.map(row => this.mapRowToEntity(row));
  }

  async create(entity: ${entityName}): Promise<void> {
    const columns = [${entity.properties.map(p => `'${p.name}'`).join(', ')}];
    const values = [${entity.properties.map((p, i) => `$${i + 1}`).join(', ')}];
    const params = [${entity.properties.map(p => `entity.${p.name}`).join(', ')}];

    const query = \`INSERT INTO ${tableName} (\${columns.join(', ')}) VALUES (\${values.join(', ')})\`;

    await this.db.query(query, params);
  }

  async update(id: ${entity.idType}, entity: ${entityName}): Promise<void> {
    const setClause = ${entity.properties.filter(p => p.name !== 'id').map((p, i) => `'${p.name}' = $${i + 2}`).join(', ')};
    const params = [id, ${entity.properties.filter(p => p.name !== 'id').map(p => `entity.${p.name}`).join(', ')}];

    const query = \`UPDATE ${tableName} SET \${setClause}, updated_at = NOW() WHERE id = $1\`;

    const result = await this.db.query(query, params);
    if (result.rowCount === 0) {
      throw new Error('${entityName} not found: \${id}');
    }
  }

  async delete(id: ${entity.idType}): Promise<void> {
    const query = 'DELETE FROM ${tableName} WHERE id = $1';
    const result = await this.db.query(query, [id]);

    if (result.rowCount === 0) {
      throw new Error('${entityName} not found: \${id}');
    }
  }

  async exists(id: ${entity.idType}): Promise<boolean> {
    const query = 'SELECT 1 FROM ${tableName} WHERE id = $1 LIMIT 1';
    const result = await this.db.query(query, [id]);
    return result.rows.length > 0;
  }

  async count(): Promise<number> {
    const query = 'SELECT COUNT(*) as count FROM ${tableName}';
    const result = await this.db.query(query);
    return parseInt(result.rows[0].count);
  }
`;

  // Add domain-specific query methods
  entity.properties.forEach(prop => {
    if (prop.name !== 'id' && prop.name !== 'createdAt' && prop.name !== 'updatedAt') {
      if (prop.type === 'string') {
        code += `
  async findBy${capitalize(prop.name)}(value: ${prop.type}): Promise<${entityName}[]> {
    const query = 'SELECT * FROM ${tableName} WHERE ${prop.name} = $1 ORDER BY created_at DESC';
    const result = await this.db.query(query, [value]);
    return result.rows.map(row => this.mapRowToEntity(row));
  }`;
      } else if (prop.type === 'boolean') {
        code += `
  async findBy${capitalize(prop.name)}(value: ${prop.type}): Promise<${entityName}[]> {
    const query = 'SELECT * FROM ${tableName} WHERE ${prop.name} = $1 ORDER BY created_at DESC';
    const result = await this.db.query(query, [value]);
    return result.rows.map(row => this.mapRowToEntity(row));
  }`;
      }
    }
  });

  code += `

  private mapRowToEntity(row: any): ${entityName} {
    return {
${entity.properties.map(p => `      ${p.name}: row.${p.name},`).join('\n')}
    };
  }
}\n`;

  return code;
}

function generateInMemoryRepository(entity: EntityConfig): string {
  const entityName = entity.name;
  const repositoryName = `${entityName}Repository`;

  let code = `/**
 * VALEO NeuroERP 3.0 - In-Memory ${entityName} Repository
 *
 * In-memory implementation of ${entityName} repository for testing.
 * Stores data in memory with no persistence.
 */

import { ${entityName} } from '../../core/entities/${entityName.toLowerCase()}';
import { ${entity.idType} } from '@packages/data-models/branded-types';
import { ${repositoryName} from './${entityName.toLowerCase()}-repository';

export class InMemory${repositoryName} implements ${repositoryName} {
  private storage = new Map<${entity.idType}, ${entityName}>();

  async findById(id: ${entity.idType}): Promise<${entityName} | null> {
    return this.storage.get(id) || null;
  }

  async findAll(): Promise<${entityName}[]> {
    return Array.from(this.storage.values());
  }

  async create(entity: ${entityName}): Promise<void> {
    this.storage.set(entity.id, { ...entity });
  }

  async update(id: ${entity.idType}, entity: ${entityName}): Promise<void> {
    if (!this.storage.has(id)) {
      throw new Error('${entityName} not found: \${id}');
    }
    this.storage.set(id, { ...entity });
  }

  async delete(id: ${entity.idType}): Promise<void> {
    if (!this.storage.has(id)) {
      throw new Error('${entityName} not found: \${id}');
    }
    this.storage.delete(id);
  }

  async exists(id: ${entity.idType}): Promise<boolean> {
    return this.storage.has(id);
  }

  async count(): Promise<number> {
    return this.storage.size;
  }
`;

  // Add domain-specific query methods
  entity.properties.forEach(prop => {
    if (prop.name !== 'id' && prop.name !== 'createdAt' && prop.name !== 'updatedAt') {
      if (prop.type === 'string' || prop.type === 'boolean') {
        code += `
  async findBy${capitalize(prop.name)}(value: ${prop.type}): Promise<${entityName}[]> {
    return Array.from(this.storage.values())
      .filter(entity => entity.${prop.name} === value);
  }`;
      }
    }
  });

  code += `

  // Test utilities
  clear(): void {
    this.storage.clear();
  }

  seed(data: ${entityName}[]): void {
    data.forEach(entity => this.storage.set(entity.id, entity));
  }
}\n`;

  return code;
}

function generateRestRepository(entity: EntityConfig): string {
  const entityName = entity.name;
  const repositoryName = `${entityName}Repository`;

  let code = `/**
 * VALEO NeuroERP 3.0 - REST ${entityName} Repository
 *
 * REST API implementation of ${entityName} repository.
 * Bridges to legacy VALEO-NeuroERP-2.0 APIs during migration.
 */

import { ${entityName} } from '../../core/entities/${entityName.toLowerCase()}';
import { ${entity.idType} } from '@packages/data-models/branded-types';
import { ${repositoryName} } from './${entityName.toLowerCase()}-repository';

export class Rest${repositoryName} implements ${repositoryName} {
  constructor(
    private baseUrl: string,
    private apiToken?: string
  ) {}

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = \`\${this.baseUrl}\${endpoint}\`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.apiToken) {
      headers['Authorization'] = \`Bearer \${this.apiToken}\`;
    }

    const response = await fetch(url, {
      ...options,
      headers: { ...headers, ...options.headers }
    });

    if (!response.ok) {
      throw new Error(\`API request failed: \${response.status} \${response.statusText}\`);
    }

    return response.json();
  }

  async findById(id: ${entity.idType}): Promise<${entityName} | null> {
    try {
      const data = await this.request<${entityName}>(\`/${entityName.toLowerCase()}s/\${id}\`);
      return data;
    } catch (error) {
      if (error.message.includes('404')) {
        return null;
      }
      throw error;
    }
  }

  async findAll(): Promise<${entityName}[]> {
    return this.request<${entityName}[]>(\`/${entityName.toLowerCase()}s\`);
  }

  async create(entity: ${entityName}): Promise<void> {
    await this.request(\`/${entityName.toLowerCase()}s\`, {
      method: 'POST',
      body: JSON.stringify(entity)
    });
  }

  async update(id: ${entity.idType}, entity: ${entityName}): Promise<void> {
    await this.request(\`/${entityName.toLowerCase()}s/\${id}\`, {
      method: 'PUT',
      body: JSON.stringify(entity)
    });
  }

  async delete(id: ${entity.idType}): Promise<void> {
    await this.request(\`/${entityName.toLowerCase()}s/\${id}\`, {
      method: 'DELETE'
    });
  }

  async exists(id: ${entity.idType}): Promise<boolean> {
    try {
      await this.request(\`/${entityName.toLowerCase()}s/\${id}\`);
      return true;
    } catch (error) {
      return false;
    }
  }

  async count(): Promise<number> {
    const items = await this.findAll();
    return items.length;
  }
`;

  // Add domain-specific query methods
  entity.properties.forEach(prop => {
    if (prop.name !== 'id' && prop.name !== 'createdAt' && prop.name !== 'updatedAt') {
      if (prop.type === 'string' || prop.type === 'boolean') {
        code += `
  async findBy${capitalize(prop.name)}(value: ${prop.type}): Promise<${entityName}[]> {
    return this.request<${entityName}[]>(\`/${entityName.toLowerCase()}s?${prop.name}=\${encodeURIComponent(value)}\`);
  }`;
      }
    }
  });

  code += `}\n`;

  return code;
}

function main() {
  const domainName = process.argv[2];
  const entityName = process.argv[3];

  if (!domainName || !entityName) {
    console.error('Usage: npx ts-node tools/codegen/repository_generator.ts <domain-name> <entity-name>');
    console.error('Example: npx ts-node tools/codegen/repository_generator.ts crm Customer');
    process.exit(1);
  }

  // Define entity configuration (in real usage, this would come from analysis)
  const entityConfig: EntityConfig = {
    name: entityName,
    idType: `${entityName}Id`,
    domain: domainName,
    properties: [
      { name: 'id', type: `${entityName}Id` },
      { name: 'name', type: 'string' },
      { name: 'status', type: 'string' },
      { name: 'createdAt', type: 'Date' },
      { name: 'updatedAt', type: 'Date' }
    ]
  };

  const basePath = path.join(__dirname, '../../domains', domainName, 'src', 'infrastructure', 'repositories');

  // Ensure directory exists
  if (!fs.existsSync(basePath)) {
    fs.mkdirSync(basePath, { recursive: true });
  }

  // Generate interface
  const interfaceCode = generateRepositoryInterface(entityConfig);
  const interfacePath = path.join(basePath, `${entityName.toLowerCase()}-repository.ts`);
  fs.writeFileSync(interfacePath, interfaceCode, 'utf8');
  console.log(`Generated repository interface: ${interfacePath}`);

  // Generate Postgres implementation
  const postgresCode = generatePostgresRepository(entityConfig);
  const postgresPath = path.join(basePath, `postgres-${entityName.toLowerCase()}-repository.ts`);
  fs.writeFileSync(postgresPath, postgresCode, 'utf8');
  console.log(`Generated Postgres repository: ${postgresPath}`);

  // Generate In-Memory implementation
  const inMemoryCode = generateInMemoryRepository(entityConfig);
  const inMemoryPath = path.join(basePath, `in-memory-${entityName.toLowerCase()}-repository.ts`);
  fs.writeFileSync(inMemoryPath, inMemoryCode, 'utf8');
  console.log(`Generated In-Memory repository: ${inMemoryPath}`);

  // Generate REST implementation
  const restCode = generateRestRepository(entityConfig);
  const restPath = path.join(basePath, `rest-${entityName.toLowerCase()}-repository.ts`);
  fs.writeFileSync(restPath, restCode, 'utf8');
  console.log(`Generated REST repository: ${restPath}`);

  console.log(`\nRepository generation complete for ${entityName} in ${domainName} domain!`);
  console.log('Generated files:');
  console.log(`- Interface: ${entityName}Repository`);
  console.log(`- Postgres: Postgres${entityName}Repository`);
  console.log(`- In-Memory: InMemory${entityName}Repository`);
  console.log(`- REST: Rest${entityName}Repository`);
}

if (require.main === module) {
  main();
}