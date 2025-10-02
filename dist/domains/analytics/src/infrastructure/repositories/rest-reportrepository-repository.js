"use strict";
/**
 * VALEO NeuroERP 3.0 - REST ReportRepository Repository
 *
 * REST API implementation of ReportRepository repository.
 * Bridges to legacy VALEO-NeuroERP-2.0 APIs during migration.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.RestReportRepositoryRepository = void 0;
class RestReportRepositoryRepository {
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
            const data = await this.request(`/reportrepositorys/${id}`);
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
        return this.request(`/reportrepositorys`);
    }
    async create(entity) {
        await this.request(`/reportrepositorys`, {
            method: 'POST',
            body: JSON.stringify(entity)
        });
    }
    async update(id, entity) {
        await this.request(`/reportrepositorys/${id}`, {
            method: 'PUT',
            body: JSON.stringify(entity)
        });
    }
    async delete(id) {
        await this.request(`/reportrepositorys/${id}`, {
            method: 'DELETE'
        });
    }
    async exists(id) {
        try {
            await this.request(`/reportrepositorys/${id}`);
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
        return this.request(`/reportrepositorys?name=${encodeURIComponent(value)}`);
    }
    async findByStatus(value) {
        return this.request(`/reportrepositorys?status=${encodeURIComponent(value)}`);
    }
}
exports.RestReportRepositoryRepository = RestReportRepositoryRepository;
