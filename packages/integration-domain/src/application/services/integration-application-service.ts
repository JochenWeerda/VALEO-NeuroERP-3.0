/**
 * Integration Application Service
 */

import type { UnitOfWork } from '@domain/interfaces/repositories.js';
import type { Result } from '@domain/interfaces/repositories.js';
import { 
  ActivateIntegrationCommand,
  ActivateIntegrationUseCase,
  CreateIntegrationCommand,
  CreateIntegrationUseCase,
  DeactivateIntegrationCommand,
  DeactivateIntegrationUseCase,
  DeleteIntegrationCommand,
  DeleteIntegrationUseCase,
  GetActiveIntegrationsQuery,
  GetIntegrationByNameQuery,
  GetIntegrationQuery,
  GetIntegrationQueryHandler,
  GetIntegrationsByTypeQuery,
  ListIntegrationsQuery,
  ListIntegrationsQueryHandler,
  UpdateIntegrationCommand,
  UpdateIntegrationUseCase
} from '../use-cases/integration-use-cases.js';
import type { 
  CreateIntegrationRequest,
  IntegrationListResponse,
  IntegrationQuery,
  IntegrationResponse,
  UpdateIntegrationRequest
} from '../dto/integration-dto.js';

export class IntegrationApplicationService {
  private createIntegrationUseCase: CreateIntegrationUseCase;
  private updateIntegrationUseCase: UpdateIntegrationUseCase;
  private deleteIntegrationUseCase: DeleteIntegrationUseCase;
  private activateIntegrationUseCase: ActivateIntegrationUseCase;
  private deactivateIntegrationUseCase: DeactivateIntegrationUseCase;
  private getIntegrationQueryHandler: GetIntegrationQueryHandler;
  private listIntegrationsQueryHandler: ListIntegrationsQueryHandler;

  constructor(private readonly unitOfWork: UnitOfWork) {
    // Initialize use cases
    this.createIntegrationUseCase = new CreateIntegrationUseCase(unitOfWork);
    this.updateIntegrationUseCase = new UpdateIntegrationUseCase(unitOfWork);
    this.deleteIntegrationUseCase = new DeleteIntegrationUseCase(unitOfWork);
    this.activateIntegrationUseCase = new ActivateIntegrationUseCase(unitOfWork);
    this.deactivateIntegrationUseCase = new DeactivateIntegrationUseCase(unitOfWork);
    
    // Initialize query handlers
    this.getIntegrationQueryHandler = new GetIntegrationQueryHandler(unitOfWork);
    this.listIntegrationsQueryHandler = new ListIntegrationsQueryHandler(unitOfWork);
  }

  // Command methods
  async createIntegration(
    request: CreateIntegrationRequest,
    userId: string
  ): Promise<Result<IntegrationResponse, Error>> {
    const command = new CreateIntegrationCommand(request, userId);
    return await this.createIntegrationUseCase.execute(command);
  }

  async updateIntegration(
    id: string,
    request: UpdateIntegrationRequest,
    userId: string
  ): Promise<Result<IntegrationResponse, Error>> {
    const command = new UpdateIntegrationCommand(id, request, userId);
    return await this.updateIntegrationUseCase.execute(command);
  }

  async deleteIntegration(
    id: string,
    userId: string
  ): Promise<Result<void, Error>> {
    const command = new DeleteIntegrationCommand(id, userId);
    return await this.deleteIntegrationUseCase.execute(command);
  }

  async activateIntegration(
    id: string,
    userId: string
  ): Promise<Result<IntegrationResponse, Error>> {
    const command = new ActivateIntegrationCommand(id, userId);
    return await this.activateIntegrationUseCase.execute(command);
  }

  async deactivateIntegration(
    id: string,
    userId: string
  ): Promise<Result<IntegrationResponse, Error>> {
    const command = new DeactivateIntegrationCommand(id, userId);
    return await this.deactivateIntegrationUseCase.execute(command);
  }

  // Query methods
  async getIntegration(id: string): Promise<Result<IntegrationResponse | null, Error>> {
    const query = new GetIntegrationQuery(id);
    return await this.getIntegrationQueryHandler.execute(query);
  }

  async listIntegrations(query: IntegrationQuery): Promise<Result<IntegrationListResponse, Error>> {
    const queryObject = new ListIntegrationsQuery(query);
    return await this.listIntegrationsQueryHandler.execute(queryObject);
  }

  async getIntegrationByName(name: string): Promise<Result<IntegrationResponse | null, Error>> {
    try {
      const result = await this.unitOfWork.integrations.findByName(name);
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

  async getIntegrationsByType(type: string): Promise<Result<IntegrationResponse[], Error>> {
    try {
      const result = await this.unitOfWork.integrations.findByType(type);
      if (!result.success) {
        return result;
      }

      const integrations = result.data.map(integration => this.mapToResponse(integration));
      return { success: true, data: integrations };
    } catch (error) {
      return { 
        success: false, 
        error: error as Error 
      };
    }
  }

  async getActiveIntegrations(): Promise<Result<IntegrationResponse[], Error>> {
    try {
      const result = await this.unitOfWork.integrations.findActive();
      if (!result.success) {
        return result;
      }

      const integrations = result.data.map(integration => this.mapToResponse(integration));
      return { success: true, data: integrations };
    } catch (error) {
      return { 
        success: false, 
        error: error as Error 
      };
    }
  }

  // Utility methods
  async healthCheck(): Promise<Result<{ status: string; timestamp: string }, Error>> {
    try {
      // Simple health check - try to query integrations
      const result = await this.unitOfWork.integrations.findAll({ page: 1, limit: 1 });
      
      if (result.success) {
        return {
          success: true,
          data: {
            status: 'healthy',
            timestamp: new Date().toISOString()
          }
        };
      } else {
        return {
          success: true,
          data: {
            status: 'degraded',
            timestamp: new Date().toISOString()
          }
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error as Error
      };
    }
  }

  async getStatistics(): Promise<Result<{
    total: number;
    active: number;
    inactive: number;
    byType: Record<string, number>;
  }, Error>> {
    try {
      // Get all integrations
      const allResult = await this.unitOfWork.integrations.findAll({ page: 1, limit: 1000 });
      if (!allResult.success) {
        return allResult;
      }

      const integrations = allResult.data.data;
      const total = integrations.length;
      const active = integrations.filter(i => i.isActive).length;
      const inactive = total - active;

      // Group by type
      const byType: Record<string, number> = {};
      integrations.forEach(integration => {
        byType[integration.type] = (byType[integration.type] || 0) + 1;
      });

      return {
        success: true,
        data: {
          total,
          active,
          inactive,
          byType
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error as Error
      };
    }
  }

  private mapToResponse(integration: any): IntegrationResponse {
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
