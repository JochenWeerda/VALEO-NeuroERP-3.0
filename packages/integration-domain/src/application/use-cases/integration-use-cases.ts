/**
 * Integration Use Cases (Commands and Queries)
 */

import type { UnitOfWork } from '@domain/interfaces/repositories.js';
import type { Result } from '@domain/interfaces/repositories.js';
import { Integration } from '@domain/entities/integration.js';
import { IntegrationCreatedEvent, IntegrationUpdatedEvent } from '@domain/events/integration-events.js';
import type { 
  CreateIntegrationRequest, 
  IntegrationListResponse, 
  IntegrationQuery,
  IntegrationResponse,
  UpdateIntegrationRequest 
} from '../dto/integration-dto.js';

// Commands
export class CreateIntegrationCommand {
  constructor(
    public request: CreateIntegrationRequest,
    public userId: string
  ) {}
}

export class UpdateIntegrationCommand {
  constructor(
    public id: string,
    public request: UpdateIntegrationRequest,
    public userId: string
  ) {}
}

export class DeleteIntegrationCommand {
  constructor(
    public id: string,
    public userId: string
  ) {}
}

export class ActivateIntegrationCommand {
  constructor(
    public id: string,
    public userId: string
  ) {}
}

export class DeactivateIntegrationCommand {
  constructor(
    public id: string,
    public userId: string
  ) {}
}

// Queries
export class GetIntegrationQuery {
  constructor(public id: string) {}
}

export class ListIntegrationsQuery {
  constructor(public query: IntegrationQuery) {}
}

export class GetIntegrationByNameQuery {
  constructor(public name: string) {}
}

export class GetIntegrationsByTypeQuery {
  constructor(public type: string) {}
}

export class GetActiveIntegrationsQuery {
  constructor() {}
}

// Use Case Handlers
export class CreateIntegrationUseCase {
  constructor(private readonly unitOfWork: UnitOfWork) {}

  async execute(command: CreateIntegrationCommand): Promise<Result<IntegrationResponse, Error>> {
    try {
      await this.unitOfWork.begin();

      // Check if integration with same name already exists
      const existingIntegration = await this.unitOfWork.integrations.findByName(command.request.name);
      if (existingIntegration.success && existingIntegration.data) {
        await this.unitOfWork.rollback();
        return { 
          success: false, 
          error: new Error(`Integration with name '${command.request.name}' already exists`) 
        };
      }

      // Create integration
      const integration = Integration.create(
        command.request.name,
        command.request.type,
        command.request.config,
        command.userId,
        command.request.description,
        command.request.tags
      );

      // Save integration
      const createResult = await this.unitOfWork.integrations.create(integration);
      if (!createResult.success) {
        await this.unitOfWork.rollback();
        return createResult;
      }

      // Publish domain events
      const events = integration.getUncommittedEvents();
      // In a real implementation, you would publish these events to an event bus
      console.log('Domain events:', events.map(e => e.toJSON()));

      integration.markEventsAsCommitted();

      await this.unitOfWork.commit();

      return { 
        success: true, 
        data: this.mapToResponse(integration) 
      };
    } catch (error) {
      await this.unitOfWork.rollback();
      return { 
        success: false, 
        error: error as Error 
      };
    }
  }

  private mapToResponse(integration: Integration): IntegrationResponse {
    return {
      id: integration.id,
      name: integration.name,
      type: integration.type,
      status: integration.status,
      config: integration.config,
      description: integration.description || null,
      tags: integration.tags,
      isActive: integration.isActive,
      createdAt: integration.createdAt.toISOString(),
      updatedAt: integration.updatedAt.toISOString(),
      createdBy: integration.createdBy,
      updatedBy: integration.updatedBy
    };
  }
}

export class UpdateIntegrationUseCase {
  constructor(private readonly unitOfWork: UnitOfWork) {}

  async execute(command: UpdateIntegrationCommand): Promise<Result<IntegrationResponse, Error>> {
    try {
      await this.unitOfWork.begin();

      // Find existing integration
      const findResult = await this.unitOfWork.integrations.findById(command.id);
      if (!findResult.success || !findResult.data) {
        await this.unitOfWork.rollback();
        return { 
          success: false, 
          error: new Error(`Integration with id '${command.id}' not found`) 
        };
      }

      const integration = findResult.data;

      // Check for duplicate name if name is being updated
      if (command.request.name && command.request.name !== integration.name) {
        const existingIntegration = await this.unitOfWork.integrations.findByName(command.request.name);
        if (existingIntegration.success && existingIntegration.data) {
          await this.unitOfWork.rollback();
          return { 
            success: false, 
            error: new Error(`Integration with name '${command.request.name}' already exists`) 
          };
        }
      }

      // Update integration properties
      if (command.request.name) {
        (integration as any)['props'].name = command.request.name;
      }
      if (command.request.config) {
        integration.updateConfig(command.request.config, command.userId);
      }
      if (command.request.description !== undefined) {
        (integration as any)['props'].description = command.request.description;
      }
      if (command.request.tags) {
        (integration as any)['props'].tags = command.request.tags;
      }
      if (command.request.status) {
        (integration as any)['props'].status = command.request.status;
      }
      if (command.request.isActive !== undefined) {
        (integration as any)['props'].isActive = command.request.isActive;
      }

      // Update timestamps
      (integration as any)['props'].updatedAt = new Date();
      (integration as any)['props'].updatedBy = command.userId;

      // Save updated integration
      const updateResult = await this.unitOfWork.integrations.update(integration);
      if (!updateResult.success) {
        await this.unitOfWork.rollback();
        return updateResult;
      }

      // Publish domain events
      const events = integration.getUncommittedEvents();
      console.log('Domain events:', events.map(e => e.toJSON()));
      integration.markEventsAsCommitted();

      await this.unitOfWork.commit();

      return { 
        success: true, 
        data: this.mapToResponse(integration) 
      };
    } catch (error) {
      await this.unitOfWork.rollback();
      return { 
        success: false, 
        error: error as Error 
      };
    }
  }

  private mapToResponse(integration: Integration): IntegrationResponse {
    return {
      id: integration.id,
      name: integration.name,
      type: integration.type,
      status: integration.status,
      config: integration.config,
      description: integration.description || null,
      tags: integration.tags,
      isActive: integration.isActive,
      createdAt: integration.createdAt.toISOString(),
      updatedAt: integration.updatedAt.toISOString(),
      createdBy: integration.createdBy,
      updatedBy: integration.updatedBy
    };
  }
}

export class DeleteIntegrationUseCase {
  constructor(private readonly unitOfWork: UnitOfWork) {}

  async execute(command: DeleteIntegrationCommand): Promise<Result<void, Error>> {
    try {
      await this.unitOfWork.begin();

      // Check if integration exists
      const findResult = await this.unitOfWork.integrations.findById(command.id);
      if (!findResult.success || !findResult.data) {
        await this.unitOfWork.rollback();
        return { 
          success: false, 
          error: new Error(`Integration with id '${command.id}' not found`) 
        };
      }

      // Delete integration
      const deleteResult = await this.unitOfWork.integrations.delete(command.id);
      if (!deleteResult.success) {
        await this.unitOfWork.rollback();
        return deleteResult;
      }

      await this.unitOfWork.commit();

      return { success: true, data: undefined };
    } catch (error) {
      await this.unitOfWork.rollback();
      return { 
        success: false, 
        error: error as Error 
      };
    }
  }
}

export class ActivateIntegrationUseCase {
  constructor(private readonly unitOfWork: UnitOfWork) {}

  async execute(command: ActivateIntegrationCommand): Promise<Result<IntegrationResponse, Error>> {
    try {
      await this.unitOfWork.begin();

      const findResult = await this.unitOfWork.integrations.findById(command.id);
      if (!findResult.success || !findResult.data) {
        await this.unitOfWork.rollback();
        return { 
          success: false, 
          error: new Error(`Integration with id '${command.id}' not found`) 
        };
      }

      const integration = findResult.data;
      integration.activate(command.userId);

      const updateResult = await this.unitOfWork.integrations.update(integration);
      if (!updateResult.success) {
        await this.unitOfWork.rollback();
        return updateResult;
      }

      // Publish domain events
      const events = integration.getUncommittedEvents();
      console.log('Domain events:', events.map(e => e.toJSON()));
      integration.markEventsAsCommitted();

      await this.unitOfWork.commit();

      return { 
        success: true, 
        data: this.mapToResponse(integration) 
      };
    } catch (error) {
      await this.unitOfWork.rollback();
      return { 
        success: false, 
        error: error as Error 
      };
    }
  }

  private mapToResponse(integration: Integration): IntegrationResponse {
    return {
      id: integration.id,
      name: integration.name,
      type: integration.type,
      status: integration.status,
      config: integration.config,
      description: integration.description || null,
      tags: integration.tags,
      isActive: integration.isActive,
      createdAt: integration.createdAt.toISOString(),
      updatedAt: integration.updatedAt.toISOString(),
      createdBy: integration.createdBy,
      updatedBy: integration.updatedBy
    };
  }
}

export class DeactivateIntegrationUseCase {
  constructor(private readonly unitOfWork: UnitOfWork) {}

  async execute(command: DeactivateIntegrationCommand): Promise<Result<IntegrationResponse, Error>> {
    try {
      await this.unitOfWork.begin();

      const findResult = await this.unitOfWork.integrations.findById(command.id);
      if (!findResult.success || !findResult.data) {
        await this.unitOfWork.rollback();
        return { 
          success: false, 
          error: new Error(`Integration with id '${command.id}' not found`) 
        };
      }

      const integration = findResult.data;
      integration.deactivate(command.userId);

      const updateResult = await this.unitOfWork.integrations.update(integration);
      if (!updateResult.success) {
        await this.unitOfWork.rollback();
        return updateResult;
      }

      // Publish domain events
      const events = integration.getUncommittedEvents();
      console.log('Domain events:', events.map(e => e.toJSON()));
      integration.markEventsAsCommitted();

      await this.unitOfWork.commit();

      return { 
        success: true, 
        data: this.mapToResponse(integration) 
      };
    } catch (error) {
      await this.unitOfWork.rollback();
      return { 
        success: false, 
        error: error as Error 
      };
    }
  }

  private mapToResponse(integration: Integration): IntegrationResponse {
    return {
      id: integration.id,
      name: integration.name,
      type: integration.type,
      status: integration.status,
      config: integration.config,
      description: integration.description || null,
      tags: integration.tags,
      isActive: integration.isActive,
      createdAt: integration.createdAt.toISOString(),
      updatedAt: integration.updatedAt.toISOString(),
      createdBy: integration.createdBy,
      updatedBy: integration.updatedBy
    };
  }
}

// Query Handlers
export class GetIntegrationQueryHandler {
  constructor(private readonly unitOfWork: UnitOfWork) {}

  async execute(query: GetIntegrationQuery): Promise<Result<IntegrationResponse | null, Error>> {
    try {
      const result = await this.unitOfWork.integrations.findById(query.id);
      if (!result.success) {
        return result;
      }

      if (!result.data) {
        return { success: true, data: null };
      }

      return { 
        success: true, 
        data: this.mapToResponse(result.data) 
      };
    } catch (error) {
      return { 
        success: false, 
        error: error as Error 
      };
    }
  }

  private mapToResponse(integration: Integration): IntegrationResponse {
    return {
      id: integration.id,
      name: integration.name,
      type: integration.type,
      status: integration.status,
      config: integration.config,
      description: integration.description || null,
      tags: integration.tags,
      isActive: integration.isActive,
      createdAt: integration.createdAt.toISOString(),
      updatedAt: integration.updatedAt.toISOString(),
      createdBy: integration.createdBy,
      updatedBy: integration.updatedBy
    };
  }
}

export class ListIntegrationsQueryHandler {
  constructor(private readonly unitOfWork: UnitOfWork) {}

  async execute(query: ListIntegrationsQuery): Promise<Result<IntegrationListResponse, Error>> {
    try {
      const result = await this.unitOfWork.integrations.findAll(query.query);
      if (!result.success) {
        return result;
      }

      const response: IntegrationListResponse = {
        data: result.data.data.map(integration => ({
          id: integration.id,
          name: integration.name,
          type: integration.type,
          status: integration.status,
          config: integration.config,
          description: integration.description || null,
          tags: integration.tags,
          isActive: integration.isActive,
          createdAt: integration.createdAt.toISOString(),
          updatedAt: integration.updatedAt.toISOString(),
          createdBy: integration.createdBy,
          updatedBy: integration.updatedBy
        })),
        pagination: result.data.pagination
      };

      return { success: true, data: response };
    } catch (error) {
      return { 
        success: false, 
        error: error as Error 
      };
    }
  }
}
