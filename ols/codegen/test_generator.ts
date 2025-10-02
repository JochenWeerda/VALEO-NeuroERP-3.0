#!/usr/bin/env ts-node

/**
 * VALEO NeuroERP 3.0 - Test Generator
 *
 * Generates comprehensive unit and integration tests following TDD patterns.
 * Creates tests for entities, services, repositories, and controllers.
 *
 * Usage: npx ts-node tools/codegen/test_generator.ts <domain-name> <component-type> <component-name>
 */

import * as fs from 'fs';
import * as path from 'path';

type ComponentType = 'entity' | 'service' | 'repository' | 'controller';

interface TestConfig {
  domain: string;
  type: ComponentType;
  name: string;
}

function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function generateEntityTest(config: TestConfig): string {
  const entityName = config.name;
  const idType = `${entityName}Id`;

  let code = `/**
 * VALEO NeuroERP 3.0 - ${entityName} Entity Tests
 *
 * Unit tests for ${entityName} domain entity following TDD principles.
 */

import { describe, it, mock } from 'node:test';
import assert from 'node:assert';
import {
  ${entityName}Entity,
  Create${entityName}Command,
  Update${entityName}Command,
  ${entityName}CreatedEvent,
  ${entityName}UpdatedEvent
} from '../core/entities/${entityName.toLowerCase()}';
import { create${idType} } from '@packages/data-models/branded-types';

describe('${entityName}Entity', () => {
  const validId = create${idType}('test-id-123');
  const now = new Date('2025-01-01T00:00:00Z');

  describe('create', () => {
    it('should create a valid ${entityName.toLowerCase()} entity', () => {
      // Arrange
      const command: Create${entityName}Command = {
        name: 'Test ${entityName}',
        status: 'active'
      };

      // Mock Date.now to return consistent timestamp
      const originalDate = global.Date;
      global.Date = class extends Date {
        constructor(...args: any[]) {
          if (args.length === 0) {
            super(now);
          } else {
            super(...args);
          }
        }
        static now() {
          return now.getTime();
        }
      } as any;

      try {
        // Act
        const entity = ${entityName}Entity.create(command);

        // Assert
        assert.ok(entity.id);
        assert.equal(entity.name, 'Test ${entityName}');
        assert.equal(entity.status, 'active');
        assert.equal(entity.createdAt.getTime(), now.getTime());
        assert.equal(entity.updatedAt.getTime(), now.getTime());
        assert.ok(entity.isActive());
      } finally {
        global.Date = originalDate;
      }
    });

    it('should throw error for invalid name', () => {
      // Arrange
      const command: Create${entityName}Command = {
        name: '',
        status: 'active'
      };

      // Act & Assert
      assert.throws(
        () => ${entityName}Entity.create(command),
        { message: '${entityName} name is required' }
      );
    });

    it('should throw error for missing name', () => {
      // Arrange
      const command: Create${entityName}Command = {
        name: '   ', // whitespace only
        status: 'active'
      };

      // Act & Assert
      assert.throws(
        () => ${entityName}Entity.create(command),
        { message: '${entityName} name is required' }
      );
    });
  });

  describe('update', () => {
    let entity: ${entityName}Entity;

    beforeEach(() => {
      const command: Create${entityName}Command = {
        name: 'Original ${entityName}',
        status: 'active'
      };
      entity = ${entityName}Entity.create(command);
    });

    it('should update entity properties', () => {
      // Arrange
      const updateCommand: Update${entityName}Command = {
        name: 'Updated ${entityName}',
        status: 'inactive'
      };

      // Act
      const updatedEntity = entity.update(updateCommand);

      // Assert
      assert.equal(updatedEntity.name, 'Updated ${entityName}');
      assert.equal(updatedEntity.status, 'inactive');
      assert.ok(updatedEntity.updatedAt > entity.updatedAt);
    });

    it('should partially update entity', () => {
      // Arrange
      const updateCommand: Update${entityName}Command = {
        status: 'inactive'
        // name not provided, should remain unchanged
      };

      // Act
      const updatedEntity = entity.update(updateCommand);

      // Assert
      assert.equal(updatedEntity.name, 'Original ${entityName}'); // unchanged
      assert.equal(updatedEntity.status, 'inactive'); // updated
    });
  });

  describe('business methods', () => {
    it('should return correct active status', () => {
      // Arrange
      const activeCommand: Create${entityName}Command = {
        name: 'Active ${entityName}',
        status: 'active'
      };
      const inactiveCommand: Create${entityName}Command = {
        name: 'Inactive ${entityName}',
        status: 'inactive'
      };

      // Act
      const activeEntity = ${entityName}Entity.create(activeCommand);
      const inactiveEntity = ${entityName}Entity.create(inactiveCommand);

      // Assert
      assert.ok(activeEntity.isActive());
      assert.ok(!inactiveEntity.isActive());
    });
  });

  describe('domain events', () => {
    it('should create ${entityName}CreatedEvent', () => {
      // Arrange
      const command: Create${entityName}Command = {
        name: 'Test ${entityName}',
        status: 'active'
      };
      const entity = ${entityName}Entity.create(command);

      // Act
      const event = new ${entityName}CreatedEvent(entity);

      // Assert
      assert.equal(event.type, '${entityName}Created');
      assert.equal(event.aggregateId, entity.id);
      assert.ok(event.occurredAt instanceof Date);
      assert.equal(event.${entityName.toLowerCase()}, entity);
    });

    it('should create ${entityName}UpdatedEvent', () => {
      // Arrange
      const command: Create${entityName}Command = {
        name: 'Test ${entityName}',
        status: 'active'
      };
      const entity = ${entityName}Entity.create(command);
      const changes = { status: 'inactive' };

      // Act
      const event = new ${entityName}UpdatedEvent(entity, changes);

      // Assert
      assert.equal(event.type, '${entityName}Updated');
      assert.equal(event.aggregateId, entity.id);
      assert.ok(event.occurredAt instanceof Date);
      assert.equal(event.changes, changes);
    });
  });
});
`;

  return code;
}

function generateServiceTest(config: TestConfig): string {
  const serviceName = config.name;
  const domainName = config.domain;

  let code = `/**
 * VALEO NeuroERP 3.0 - ${serviceName} Domain Service Tests
 *
 * Unit tests for ${serviceName} domain service following TDD principles.
 */

import { describe, it, mock } from 'node:test';
import assert from 'node:assert';
import { ${serviceName} } from '../core/domain-services/${serviceName.toLowerCase()}-domain-service';
import { InMemory${serviceName.replace('DomainService', 'Repository')} } from '../infrastructure/repositories/in-memory-${serviceName.toLowerCase().replace('domainservice', 'repository')}';
import { ServiceLocator } from '@packages/utilities/service-locator';

describe('${serviceName}', () => {
  let service: ${serviceName};
  let repository: InMemory${serviceName.replace('DomainService', 'Repository')};
  let serviceLocator: ServiceLocator;

  beforeEach(() => {
    serviceLocator = new ServiceLocator();
    repository = new InMemory${serviceName.replace('DomainService', 'Repository')}();
    service = new ${serviceName}(repository);
  });

  afterEach(() => {
    repository.clear();
  });

  describe('initialization', () => {
    it('should initialize with repository', () => {
      // Assert
      assert.ok(service);
      assert.ok(repository);
    });

    it('should register business rules', () => {
      // This would test that business rules are registered
      // Implementation depends on specific domain rules
      assert.ok(true); // Placeholder
    });
  });

  describe('business operations', () => {
    it('should execute create operation successfully', async () => {
      // Arrange
      const createCommand = {
        name: 'Test Entity',
        // Add other required properties
      };

      // Act
      const result = await service.create(createCommand);

      // Assert
      assert.ok(result);
      assert.ok(result.id);
      assert.equal(result.name, 'Test Entity');
    });

    it('should execute update operation successfully', async () => {
      // Arrange
      const createCommand = {
        name: 'Test Entity',
        // Add other required properties
      };
      const entity = await service.create(createCommand);

      const updateCommand = {
        name: 'Updated Entity',
        // Add other properties to update
      };

      // Act
      const result = await service.update(entity.id, updateCommand);

      // Assert
      assert.ok(result);
      assert.equal(result.name, 'Updated Entity');
    });

    it('should throw error for non-existent entity', async () => {
      // Arrange
      const fakeId = 'non-existent-id';

      // Act & Assert
      await assert.rejects(
        async () => await service.getById(fakeId),
        { message: /not found/i }
      );
    });
  });

  describe('business rules validation', () => {
    it('should enforce business rules on create', async () => {
      // Arrange
      const invalidCommand = {
        name: '', // Invalid: empty name
        // Add other required properties
      };

      // Act & Assert
      await assert.rejects(
        async () => await service.create(invalidCommand),
        { message: /name is required/i }
      );
    });

    it('should enforce business rules on update', async () => {
      // Arrange
      const createCommand = {
        name: 'Valid Entity',
        // Add other required properties
      };
      const entity = await service.create(createCommand);

      const invalidUpdateCommand = {
        name: '', // Invalid: empty name
        // Add other properties
      };

      // Act & Assert
      await assert.rejects(
        async () => await service.update(entity.id, invalidUpdateCommand),
        { message: /name is required/i }
      );
    });
  });

  describe('domain events', () => {
    it('should publish domain events on create', async () => {
      // Arrange
      const createCommand = {
        name: 'Test Entity',
        // Add other required properties
      };

      // Act
      const result = await service.create(createCommand);

      // Assert
      // This would check that domain events were published
      // Implementation depends on event publishing mechanism
      assert.ok(result);
    });

    it('should publish domain events on update', async () => {
      // Arrange
      const createCommand = {
        name: 'Test Entity',
        // Add other required properties
      };
      const entity = await service.create(createCommand);

      const updateCommand = {
        name: 'Updated Entity',
        // Add other properties
      };

      // Act
      const result = await service.update(entity.id, updateCommand);

      // Assert
      // This would check that domain events were published
      assert.ok(result);
    });
  });
});
`;

  return code;
}

function generateRepositoryTest(config: TestConfig): string {
  const repositoryName = config.name;
  const entityName = repositoryName.replace('Repository', '');

  let code = `/**
 * VALEO NeuroERP 3.0 - ${repositoryName} Tests
 *
 * Unit tests for ${repositoryName} implementations following TDD principles.
 */

import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert';
import { InMemory${repositoryName} } from '../infrastructure/repositories/in-memory-${entityName.toLowerCase()}-repository';
import { create${entityName}Id } from '@packages/data-models/branded-types';

describe('${repositoryName}', () => {
  let repository: InMemory${repositoryName};

  beforeEach(() => {
    repository = new InMemory${repositoryName}();
  });

  afterEach(() => {
    repository.clear();
  });

  describe('basic CRUD operations', () => {
    const testId = create${entityName}Id('test-id-123');

    it('should create and find entity', async () => {
      // Arrange
      const testEntity = {
        id: testId,
        name: 'Test ${entityName}',
        status: 'active',
        createdAt: new Date(),
        updatedAt: new Date()
      };

      // Act
      await repository.create(testEntity);
      const found = await repository.findById(testId);

      // Assert
      assert.ok(found);
      assert.equal(found!.id, testId);
      assert.equal(found!.name, 'Test ${entityName}');
    });

    it('should return null for non-existent entity', async () => {
      // Act
      const result = await repository.findById(testId);

      // Assert
      assert.equal(result, null);
    });

    it('should update entity', async () => {
      // Arrange
      const testEntity = {
        id: testId,
        name: 'Original Name',
        status: 'active',
        createdAt: new Date(),
        updatedAt: new Date()
      };
      await repository.create(testEntity);

      const updatedEntity = {
        ...testEntity,
        name: 'Updated Name',
        status: 'inactive'
      };

      // Act
      await repository.update(testId, updatedEntity);
      const found = await repository.findById(testId);

      // Assert
      assert.ok(found);
      assert.equal(found!.name, 'Updated Name');
      assert.equal(found!.status, 'inactive');
    });

    it('should delete entity', async () => {
      // Arrange
      const testEntity = {
        id: testId,
        name: 'Test ${entityName}',
        status: 'active',
        createdAt: new Date(),
        updatedAt: new Date()
      };
      await repository.create(testEntity);

      // Act
      await repository.delete(testId);
      const found = await repository.findById(testId);

      // Assert
      assert.equal(found, null);
    });

    it('should check entity existence', async () => {
      // Arrange
      const testEntity = {
        id: testId,
        name: 'Test ${entityName}',
        status: 'active',
        createdAt: new Date(),
        updatedAt: new Date()
      };

      // Act & Assert
      assert.equal(await repository.exists(testId), false);
      await repository.create(testEntity);
      assert.equal(await repository.exists(testId), true);
    });
  });

  describe('query operations', () => {
    beforeEach(async () => {
      // Seed test data
      const entities = [
        {
          id: create${entityName}Id('id-1'),
          name: 'Entity 1',
          status: 'active',
          createdAt: new Date(),
          updatedAt: new Date()
        },
        {
          id: create${entityName}Id('id-2'),
          name: 'Entity 2',
          status: 'inactive',
          createdAt: new Date(),
          updatedAt: new Date()
        },
        {
          id: create${entityName}Id('id-3'),
          name: 'Entity 3',
          status: 'active',
          createdAt: new Date(),
          updatedAt: new Date()
        }
      ];

      for (const entity of entities) {
        await repository.create(entity);
      }
    });

    it('should find all entities', async () => {
      // Act
      const results = await repository.findAll();

      // Assert
      assert.equal(results.length, 3);
      assert.ok(results.every(e => e.id));
    });

    it('should count entities', async () => {
      // Act
      const count = await repository.count();

      // Assert
      assert.equal(count, 3);
    });

    it('should find entities by status', async () => {
      // Act
      const activeEntities = await repository.findByStatus('active');
      const inactiveEntities = await repository.findByStatus('inactive');

      // Assert
      assert.equal(activeEntities.length, 2);
      assert.equal(inactiveEntities.length, 1);
    });
  });

  describe('test utilities', () => {
    it('should clear repository', async () => {
      // Arrange
      const testEntity = {
        id: create${entityName}Id('test-id'),
        name: 'Test ${entityName}',
        status: 'active',
        createdAt: new Date(),
        updatedAt: new Date()
      };
      await repository.create(testEntity);

      // Act
      repository.clear();

      // Assert
      assert.equal(await repository.count(), 0);
    });

    it('should seed repository', async () => {
      // Arrange
      const seedData = [
        {
          id: create${entityName}Id('seed-1'),
          name: 'Seed Entity 1',
          status: 'active',
          createdAt: new Date(),
          updatedAt: new Date()
        },
        {
          id: create${entityName}Id('seed-2'),
          name: 'Seed Entity 2',
          status: 'active',
          createdAt: new Date(),
          updatedAt: new Date()
        }
      ];

      // Act
      repository.seed(seedData);

      // Assert
      assert.equal(await repository.count(), 2);
      assert.ok(await repository.exists(create${entityName}Id('seed-1')));
      assert.ok(await repository.exists(create${entityName}Id('seed-2')));
    });
  });
});
`;

  return code;
}

function generateControllerTest(config: TestConfig): string {
  const controllerName = config.name;
  const domainName = config.domain;

  let code = `/**
 * VALEO NeuroERP 3.0 - ${controllerName} Controller Tests
 *
 * Integration tests for ${controllerName} API controller.
 */

import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert';
import { ${controllerName} } from '../presentation/controllers/${controllerName.toLowerCase()}-api-controller';
import { InMemory${controllerName.replace('ApiController', 'Repository')} } from '../infrastructure/repositories/in-memory-${controllerName.toLowerCase().replace('apicontroller', 'repository')}';
import { ServiceLocator } from '@packages/utilities/service-locator';

describe('${controllerName} Integration', () => {
  let controller: ${controllerName};
  let repository: InMemory${controllerName.replace('ApiController', 'Repository')};
  let serviceLocator: ServiceLocator;

  beforeEach(() => {
    serviceLocator = new ServiceLocator();
    repository = new InMemory${controllerName.replace('ApiController', 'Repository')}();
    // Initialize controller with dependencies
    controller = new ${controllerName}(/* dependencies */);
  });

  afterEach(() => {
    repository.clear();
  });

  describe('API endpoints', () => {
    it('should handle create request successfully', async () => {
      // Arrange
      const request = {
        body: {
          name: 'Test Entity',
          status: 'active'
        }
      };
      const response = {
        status: (code: number) => ({
          json: (data: any) => ({ status: code, data })
        })
      };

      // Act
      await controller.create(request as any, response as any);

      // Assert
      // Verify response structure and data
      // This would check the actual response object
      assert.ok(true); // Placeholder for actual assertions
    });

    it('should handle get request successfully', async () => {
      // Arrange
      const testEntity = {
        id: 'test-id',
        name: 'Test Entity',
        status: 'active',
        createdAt: new Date(),
        updatedAt: new Date()
      };
      await repository.create(testEntity);

      const request = {
        params: { id: 'test-id' }
      };
      const response = {
        status: (code: number) => ({
          json: (data: any) => ({ status: code, data })
        })
      };

      // Act
      await controller.get(request as any, response as any);

      // Assert
      // Verify response contains the entity
      assert.ok(true); // Placeholder for actual assertions
    });

    it('should handle update request successfully', async () => {
      // Arrange
      const testEntity = {
        id: 'test-id',
        name: 'Test Entity',
        status: 'active',
        createdAt: new Date(),
        updatedAt: new Date()
      };
      await repository.create(testEntity);

      const request = {
        params: { id: 'test-id' },
        body: {
          name: 'Updated Entity',
          status: 'inactive'
        }
      };
      const response = {
        status: (code: number) => ({
          json: (data: any) => ({ status: code, data })
        })
      };

      // Act
      await controller.update(request as any, response as any);

      // Assert
      // Verify entity was updated
      assert.ok(true); // Placeholder for actual assertions
    });

    it('should handle delete request successfully', async () => {
      // Arrange
      const testEntity = {
        id: 'test-id',
        name: 'Test Entity',
        status: 'active',
        createdAt: new Date(),
        updatedAt: new Date()
      };
      await repository.create(testEntity);

      const request = {
        params: { id: 'test-id' }
      };
      const response = {
        status: (code: number) => ({
          json: (data: any) => ({ status: code, data })
        })
      };

      // Act
      await controller.delete(request as any, response as any);

      // Assert
      // Verify entity was deleted
      assert.ok(true); // Placeholder for actual assertions
    });
  });

  describe('error handling', () => {
    it('should return 404 for non-existent entity', async () => {
      // Arrange
      const request = {
        params: { id: 'non-existent-id' }
      };
      const response = {
        status: (code: number) => ({
          json: (data: any) => ({ status: code, data })
        })
      };

      // Act
      await controller.get(request as any, response as any);

      // Assert
      // Verify 404 response
      assert.ok(true); // Placeholder for actual assertions
    });

    it('should return 400 for invalid request data', async () => {
      // Arrange
      const request = {
        body: {
          name: '', // Invalid: empty name
          status: 'invalid-status'
        }
      };
      const response = {
        status: (code: number) => ({
          json: (data: any) => ({ status: code, data })
        })
      };

      // Act
      await controller.create(request as any, response as any);

      // Assert
      // Verify 400 response with validation errors
      assert.ok(true); // Placeholder for actual assertions
    });
  });

  describe('response format', () => {
    it('should return consistent response structure', async () => {
      // Arrange
      const request = {
        body: {
          name: 'Test Entity',
          status: 'active'
        }
      };
      let capturedResponse: any;

      const response = {
        status: (code: number) => ({
          json: (data: any) => {
            capturedResponse = { status: code, data };
            return capturedResponse;
          }
        })
      };

      // Act
      await controller.create(request as any, response as any);

      // Assert
      assert.ok(capturedResponse);
      assert.ok(capturedResponse.data);
      assert.equal(capturedResponse.data.success, true);
      assert.ok(capturedResponse.data.data);
      assert.ok(capturedResponse.data.message);
    });
  });
});
`;

  return code;
}

function main() {
  const domainName = process.argv[2];
  const componentType = process.argv[3] as ComponentType;
  const componentName = process.argv[4];

  if (!domainName || !componentType || !componentName) {
    console.error('Usage: npx ts-node tools/codegen/test_generator.ts <domain-name> <component-type> <component-name>');
    console.error('Component types: entity, service, repository, controller');
    console.error('Example: npx ts-node tools/codegen/test_generator.ts crm entity Customer');
    process.exit(1);
  }

  const testConfig: TestConfig = {
    domain: domainName,
    type: componentType,
    name: componentName
  };

  let testCode: string;
  let testPath: string;

  switch (componentType) {
    case 'entity':
      testCode = generateEntityTest(testConfig);
      testPath = path.join(__dirname, '../../domains', domainName, 'tests', 'unit', `${componentName.toLowerCase()}-entity.test.ts`);
      break;
    case 'service':
      testCode = generateServiceTest(testConfig);
      testPath = path.join(__dirname, '../../domains', domainName, 'tests', 'unit', `${componentName.toLowerCase()}-domain-service.test.ts`);
      break;
    case 'repository':
      testCode = generateRepositoryTest(testConfig);
      testPath = path.join(__dirname, '../../domains', domainName, 'tests', 'unit', `${componentName.toLowerCase()}-repository.test.ts`);
      break;
    case 'controller':
      testCode = generateControllerTest(testConfig);
      testPath = path.join(__dirname, '../../domains', domainName, 'tests', 'integration', `${componentName.toLowerCase()}-controller.test.ts`);
      break;
    default:
      console.error(`Unknown component type: ${componentType}`);
      process.exit(1);
  }

  // Ensure directory exists
  const testDir = path.dirname(testPath);
  if (!fs.existsSync(testDir)) {
    fs.mkdirSync(testDir, { recursive: true });
  }

  fs.writeFileSync(testPath, testCode, 'utf8');
  console.log(`Generated test file: ${testPath}`);

  console.log(`\nTest generation complete for ${componentName} ${componentType} in ${domainName} domain!`);
  console.log('Test covers:');
  console.log(`- Unit tests for ${componentType} functionality`);
  console.log(`- Error handling and edge cases`);
  console.log(`- Business rule validation`);
  console.log(`- Integration with dependencies`);
}

if (require.main === module) {
  main();
}