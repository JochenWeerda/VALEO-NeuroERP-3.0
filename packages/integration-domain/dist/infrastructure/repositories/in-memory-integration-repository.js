/**
 * InMemory Integration Repository Implementation
 */
export class InMemoryIntegrationRepository {
    integrations = new Map();
    nameIndex = new Map();
    typeIndex = new Map();
    statusIndex = new Map();
    tagsIndex = new Map();
    async findById(id) {
        try {
            const integration = this.integrations.get(id) || null;
            return { success: true, data: integration };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findAll(options) {
        try {
            const { page = 1, limit = 10, sortBy = 'createdAt', sortOrder = 'desc' } = options || {};
            const integrations = Array.from(this.integrations.values());
            // Sort
            integrations.sort((a, b) => {
                const aValue = this.getSortValue(a, sortBy);
                const bValue = this.getSortValue(b, sortBy);
                if (sortOrder === 'asc') {
                    return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
                }
                else {
                    return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
                }
            });
            // Paginate
            const offset = (page - 1) * limit;
            const paginatedData = integrations.slice(offset, offset + limit);
            const total = integrations.length;
            const totalPages = Math.ceil(total / limit);
            const result = {
                data: paginatedData,
                pagination: {
                    page,
                    limit,
                    total,
                    totalPages,
                    hasNext: page < totalPages,
                    hasPrev: page > 1
                }
            };
            return { success: true, data: result };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async create(integration) {
        try {
            const id = integration.id;
            // Check for duplicate name
            if (this.nameIndex.has(integration.name)) {
                return {
                    success: false,
                    error: new Error(`Integration with name '${integration.name}' already exists`)
                };
            }
            // Store integration
            this.integrations.set(id, integration);
            // Update indexes
            this.nameIndex.set(integration.name, id);
            this.addToTypeIndex(integration.type, id);
            this.addToStatusIndex(integration.status, id);
            this.addToTagsIndex(integration.tags, id);
            return { success: true, data: integration };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async update(integration) {
        try {
            const id = integration.id;
            const existing = this.integrations.get(id);
            if (!existing) {
                return {
                    success: false,
                    error: new Error(`Integration with id '${id}' not found`)
                };
            }
            // Check for duplicate name (if name changed)
            if (existing.name !== integration.name && this.nameIndex.has(integration.name)) {
                return {
                    success: false,
                    error: new Error(`Integration with name '${integration.name}' already exists`)
                };
            }
            // Remove from old indexes
            this.removeFromTypeIndex(existing.type, id);
            this.removeFromStatusIndex(existing.status, id);
            this.removeFromTagsIndex(existing.tags, id);
            if (existing.name !== integration.name) {
                this.nameIndex.delete(existing.name);
            }
            // Update integration
            this.integrations.set(id, integration);
            // Update indexes
            if (existing.name !== integration.name) {
                this.nameIndex.set(integration.name, id);
            }
            this.addToTypeIndex(integration.type, id);
            this.addToStatusIndex(integration.status, id);
            this.addToTagsIndex(integration.tags, id);
            return { success: true, data: integration };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async delete(id) {
        try {
            const integration = this.integrations.get(id);
            if (!integration) {
                return {
                    success: false,
                    error: new Error(`Integration with id '${id}' not found`)
                };
            }
            // Remove from indexes
            this.nameIndex.delete(integration.name);
            this.removeFromTypeIndex(integration.type, id);
            this.removeFromStatusIndex(integration.status, id);
            this.removeFromTagsIndex(integration.tags, id);
            // Remove integration
            this.integrations.delete(id);
            return { success: true, data: undefined };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findByName(name) {
        try {
            const id = this.nameIndex.get(name);
            if (!id) {
                return { success: true, data: null };
            }
            const integration = this.integrations.get(id) || null;
            return { success: true, data: integration };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findByType(type) {
        try {
            const ids = this.typeIndex.get(type) || new Set();
            const integrations = Array.from(ids)
                .map(id => this.integrations.get(id))
                .filter((integration) => integration !== undefined);
            return { success: true, data: integrations };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findByStatus(status) {
        try {
            const ids = this.statusIndex.get(status) || new Set();
            const integrations = Array.from(ids)
                .map(id => this.integrations.get(id))
                .filter((integration) => integration !== undefined);
            return { success: true, data: integrations };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findByTags(tags) {
        try {
            const matchingIds = new Set();
            for (const tag of tags) {
                const ids = this.tagsIndex.get(tag) || new Set();
                ids.forEach(id => matchingIds.add(id));
            }
            const integrations = Array.from(matchingIds)
                .map(id => this.integrations.get(id))
                .filter((integration) => integration !== undefined);
            return { success: true, data: integrations };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findActive() {
        try {
            const integrations = Array.from(this.integrations.values())
                .filter(integration => integration.isActive);
            return { success: true, data: integrations };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    // Helper methods
    getSortValue(integration, sortBy) {
        switch (sortBy) {
            case 'name': return integration.name;
            case 'type': return integration.type;
            case 'status': return integration.status;
            case 'createdAt': return integration.createdAt.getTime();
            case 'updatedAt': return integration.updatedAt.getTime();
            default: return integration.createdAt.getTime();
        }
    }
    addToTypeIndex(type, id) {
        if (!this.typeIndex.has(type)) {
            this.typeIndex.set(type, new Set());
        }
        this.typeIndex.get(type).add(id);
    }
    removeFromTypeIndex(type, id) {
        const ids = this.typeIndex.get(type);
        if (ids) {
            ids.delete(id);
            if (ids.size === 0) {
                this.typeIndex.delete(type);
            }
        }
    }
    addToStatusIndex(status, id) {
        if (!this.statusIndex.has(status)) {
            this.statusIndex.set(status, new Set());
        }
        this.statusIndex.get(status).add(id);
    }
    removeFromStatusIndex(status, id) {
        const ids = this.statusIndex.get(status);
        if (ids) {
            ids.delete(id);
            if (ids.size === 0) {
                this.statusIndex.delete(status);
            }
        }
    }
    addToTagsIndex(tags, id) {
        for (const tag of tags) {
            if (!this.tagsIndex.has(tag)) {
                this.tagsIndex.set(tag, new Set());
            }
            this.tagsIndex.get(tag).add(id);
        }
    }
    removeFromTagsIndex(tags, id) {
        for (const tag of tags) {
            const ids = this.tagsIndex.get(tag);
            if (ids) {
                ids.delete(id);
                if (ids.size === 0) {
                    this.tagsIndex.delete(tag);
                }
            }
        }
    }
    // Test utilities
    clear() {
        this.integrations.clear();
        this.nameIndex.clear();
        this.typeIndex.clear();
        this.statusIndex.clear();
        this.tagsIndex.clear();
    }
    getCount() {
        return this.integrations.size;
    }
}
//# sourceMappingURL=in-memory-integration-repository.js.map