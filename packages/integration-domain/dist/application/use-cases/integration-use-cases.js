/**
 * Integration Use Cases (Commands and Queries)
 */
import { Integration } from '@domain/entities/integration.js';
// Commands
export class CreateIntegrationCommand {
    request;
    userId;
    constructor(request, userId) {
        this.request = request;
        this.userId = userId;
    }
}
export class UpdateIntegrationCommand {
    id;
    request;
    userId;
    constructor(id, request, userId) {
        this.id = id;
        this.request = request;
        this.userId = userId;
    }
}
export class DeleteIntegrationCommand {
    id;
    userId;
    constructor(id, userId) {
        this.id = id;
        this.userId = userId;
    }
}
export class ActivateIntegrationCommand {
    id;
    userId;
    constructor(id, userId) {
        this.id = id;
        this.userId = userId;
    }
}
export class DeactivateIntegrationCommand {
    id;
    userId;
    constructor(id, userId) {
        this.id = id;
        this.userId = userId;
    }
}
// Queries
export class GetIntegrationQuery {
    id;
    constructor(id) {
        this.id = id;
    }
}
export class ListIntegrationsQuery {
    query;
    constructor(query) {
        this.query = query;
    }
}
export class GetIntegrationByNameQuery {
    name;
    constructor(name) {
        this.name = name;
    }
}
export class GetIntegrationsByTypeQuery {
    type;
    constructor(type) {
        this.type = type;
    }
}
export class GetActiveIntegrationsQuery {
    constructor() { }
}
// Use Case Handlers
export class CreateIntegrationUseCase {
    unitOfWork;
    constructor(unitOfWork) {
        this.unitOfWork = unitOfWork;
    }
    async execute(command) {
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
            const integration = Integration.create(command.request.name, command.request.type, command.request.config, command.userId, command.request.description, command.request.tags);
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
        }
        catch (error) {
            await this.unitOfWork.rollback();
            return {
                success: false,
                error: error
            };
        }
    }
    mapToResponse(integration) {
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
    unitOfWork;
    constructor(unitOfWork) {
        this.unitOfWork = unitOfWork;
    }
    async execute(command) {
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
                integration['props'].name = command.request.name;
            }
            if (command.request.config) {
                integration.updateConfig(command.request.config, command.userId);
            }
            if (command.request.description !== undefined) {
                integration['props'].description = command.request.description;
            }
            if (command.request.tags) {
                integration['props'].tags = command.request.tags;
            }
            if (command.request.status) {
                integration['props'].status = command.request.status;
            }
            if (command.request.isActive !== undefined) {
                integration['props'].isActive = command.request.isActive;
            }
            // Update timestamps
            integration['props'].updatedAt = new Date();
            integration['props'].updatedBy = command.userId;
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
        }
        catch (error) {
            await this.unitOfWork.rollback();
            return {
                success: false,
                error: error
            };
        }
    }
    mapToResponse(integration) {
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
    unitOfWork;
    constructor(unitOfWork) {
        this.unitOfWork = unitOfWork;
    }
    async execute(command) {
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
        }
        catch (error) {
            await this.unitOfWork.rollback();
            return {
                success: false,
                error: error
            };
        }
    }
}
export class ActivateIntegrationUseCase {
    unitOfWork;
    constructor(unitOfWork) {
        this.unitOfWork = unitOfWork;
    }
    async execute(command) {
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
        }
        catch (error) {
            await this.unitOfWork.rollback();
            return {
                success: false,
                error: error
            };
        }
    }
    mapToResponse(integration) {
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
    unitOfWork;
    constructor(unitOfWork) {
        this.unitOfWork = unitOfWork;
    }
    async execute(command) {
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
        }
        catch (error) {
            await this.unitOfWork.rollback();
            return {
                success: false,
                error: error
            };
        }
    }
    mapToResponse(integration) {
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
    unitOfWork;
    constructor(unitOfWork) {
        this.unitOfWork = unitOfWork;
    }
    async execute(query) {
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
        }
        catch (error) {
            return {
                success: false,
                error: error
            };
        }
    }
    mapToResponse(integration) {
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
    unitOfWork;
    constructor(unitOfWork) {
        this.unitOfWork = unitOfWork;
    }
    async execute(query) {
        try {
            const result = await this.unitOfWork.integrations.findAll(query.query);
            if (!result.success) {
                return result;
            }
            const response = {
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
        }
        catch (error) {
            return {
                success: false,
                error: error
            };
        }
    }
}
//# sourceMappingURL=integration-use-cases.js.map