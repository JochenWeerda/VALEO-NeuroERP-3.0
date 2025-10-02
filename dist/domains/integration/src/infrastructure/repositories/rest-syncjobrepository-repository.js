"use strict";
/**
 * VALEO NeuroERP 3.0 - REST SyncJobRepository Repository
 *
 * REST API implementation of SyncJobRepository repository.
 * Bridges to legacy VALEO-NeuroERP-2.0 APIs during migration.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.RestSyncJobRepositoryRepository = void 0;
class RestSyncJobRepositoryRepository {
    baseUrl;
    apiToken;
    constructor(baseUrl, apiToken) {
        this.baseUrl = baseUrl;
        this.apiToken = apiToken;
    }
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
        };
        if (this.apiToken) {
            headers['Authorization'] = `Bearer ${this.apiToken}`;
        }
        const response = await fetch(url, {
            ...options,
            headers: { ...headers, ...options.headers }
        });
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        return response.json();
    }
    async findById(id) {
        try {
            const data = await this.request(`/syncjobrepositorys/${id}`);
            return data;
        }
        catch (error) {
            if (error.message.includes('404')) {
                return null;
            }
            throw error;
        }
    }
    async findAll() {
        return this.request(`/syncjobrepositorys`);
    }
    async create(entity) {
        await this.request(`/syncjobrepositorys`, {
            method: 'POST',
            body: JSON.stringify(entity)
        });
    }
    async update(id, entity) {
        await this.request(`/syncjobrepositorys/${id}`, {
            method: 'PUT',
            body: JSON.stringify(entity)
        });
    }
    async delete(id) {
        await this.request(`/syncjobrepositorys/${id}`, {
            method: 'DELETE'
        });
    }
    async exists(id) {
        try {
            await this.request(`/syncjobrepositorys/${id}`);
            return true;
        }
        catch (error) {
            return false;
        }
    }
    async count() {
        const items = await this.findAll();
        return items.length;
    }
    async findByName(value) {
        return this.request(`/syncjobrepositorys?name=${encodeURIComponent(value)}`);
    }
    async findByStatus(value) {
        return this.request(`/syncjobrepositorys?status=${encodeURIComponent(value)}`);
    }
}
exports.RestSyncJobRepositoryRepository = RestSyncJobRepositoryRepository;
