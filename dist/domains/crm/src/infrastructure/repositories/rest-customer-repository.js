"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RestCustomerRepository = void 0;
const customer_1 = require("../../core/entities/customer");
const branded_types_1 = require("../../../../../packages/data-models/src/branded-types");
function toDomainCustomer(api) {
    return {
        id: (0, branded_types_1.brandValue)(api.id, 'CustomerId'),
        customerNumber: api.customer_number,
        name: api.name,
        type: (api.type ?? 'company'),
        status: (api.status ?? 'active'),
        email: api.email ? api.email : undefined,
        phone: api.phone ? api.phone : undefined,
        website: api.website,
        address: {
            street: api.street,
            city: api.city,
            postalCode: api.postal_code,
            country: api.country,
        },
        industry: api.industry,
        companySize: api.company_size,
        annualRevenue: api.annual_revenue,
        taxId: api.tax_id,
        vatNumber: api.vat_number,
        salesRepId: api.sales_rep_id,
        leadSource: api.lead_source,
        leadScore: api.lead_score,
        notes: api.notes,
        tags: api.tags,
        createdAt: new Date(api.created_at),
        updatedAt: api.updated_at ? new Date(api.updated_at) : undefined,
    };
}
function toCreatePayload(payload) {
    return {
        name: payload.name,
        type: payload.type,
        status: payload.status ?? 'active',
        email: payload.email ?? null,
        phone: payload.phone ?? null,
        website: payload.website ?? null,
        street: payload.address?.street ?? null,
        city: payload.address?.city ?? null,
        postal_code: payload.address?.postalCode ?? null,
        country: payload.address?.country ?? null,
        industry: payload.industry ?? null,
        company_size: payload.companySize ?? null,
        annual_revenue: payload.annualRevenue ?? null,
        tax_id: payload.taxId ?? null,
        vat_number: payload.vatNumber ?? null,
        sales_rep_id: payload.salesRepId ?? null,
        lead_source: payload.leadSource ?? null,
        lead_score: payload.leadScore ?? null,
        notes: payload.notes ?? null,
        tags: payload.tags ?? null,
        customer_number: payload.customerNumber ?? null,
    };
}
function toUpdatePayload(payload) {
    const body = {};
    if (payload.name !== undefined)
        body.name = payload.name;
    if (payload.type !== undefined)
        body.type = payload.type;
    if (payload.status !== undefined)
        body.status = payload.status;
    if (payload.email !== undefined)
        body.email = payload.email ?? null;
    if (payload.phone !== undefined)
        body.phone = payload.phone ?? null;
    if (payload.website !== undefined)
        body.website = payload.website ?? null;
    if (payload.address !== undefined) {
        body.street = payload.address?.street ?? null;
        body.city = payload.address?.city ?? null;
        body.postal_code = payload.address?.postalCode ?? null;
        body.country = payload.address?.country ?? null;
    }
    if (payload.industry !== undefined)
        body.industry = payload.industry ?? null;
    if (payload.companySize !== undefined)
        body.company_size = payload.companySize ?? null;
    if (payload.annualRevenue !== undefined)
        body.annual_revenue = payload.annualRevenue ?? null;
    if (payload.taxId !== undefined)
        body.tax_id = payload.taxId ?? null;
    if (payload.vatNumber !== undefined)
        body.vat_number = payload.vatNumber ?? null;
    if (payload.salesRepId !== undefined)
        body.sales_rep_id = payload.salesRepId ?? null;
    if (payload.leadSource !== undefined)
        body.lead_source = payload.leadSource ?? null;
    if (payload.leadScore !== undefined)
        body.lead_score = payload.leadScore ?? null;
    if (payload.notes !== undefined)
        body.notes = payload.notes ?? null;
    if (payload.tags !== undefined)
        body.tags = payload.tags ?? null;
    if (payload.customerNumber !== undefined)
        body.customer_number = payload.customerNumber ?? null;
    return body;
}
class RestCustomerRepository {
    constructor(options = {}) {
        this.baseUrl = (options.baseUrl ?? process.env.CRM_SERVICE_URL ?? 'http://localhost:8000/api/crm').replace(/\/$/, '');
        this.token = options.token ?? process.env.CRM_SERVICE_TOKEN;
        this.fetchImpl = options.fetchImpl ?? fetch;
    }
    buildHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        if (this.token) {
            headers.Authorization = `Bearer ${this.token}`;
        }
        return headers;
    }
    async request(path, init) {
        const response = await this.fetchImpl(`${this.baseUrl}${path}`, {
            ...init,
            headers: {
                ...this.buildHeaders(),
                ...(init?.headers ?? {}),
            },
        });
        if (!response.ok) {
            const message = await response.text();
            throw new Error(`CRM service responded with ${response.status}: ${message}`);
        }
        if (response.status === 204) {
            return undefined;
        }
        return (await response.json());
    }
    async list(filters = {}) {
        if (filters.search) {
            const items = await this.request(`/customers/search/${encodeURIComponent(filters.search)}`);
            return items.map(toDomainCustomer);
        }
        const params = new URLSearchParams();
        const limit = filters.limit ?? customer_1.DEFAULT_PAGE_SIZE;
        const page = Math.floor((filters.offset ?? 0) / limit) + 1;
        params.set('page', page.toString());
        params.set('limit', limit.toString());
        if (filters.status)
            params.set('status_filter', filters.status);
        if (filters.type)
            params.set('type_filter', filters.type);
        const payload = await this.request(`/customers?${params.toString()}`);
        return payload.customers.map(toDomainCustomer);
    }
    async findById(id) {
        try {
            const payload = await this.request(`/customers/${id}`);
            return toDomainCustomer(payload);
        }
        catch (error) {
            if (error instanceof Error && /404/.test(error.message)) {
                return null;
            }
            throw error;
        }
    }
    async create(payload) {
        const body = toCreatePayload(payload);
        const result = await this.request('/customers', {
            method: 'POST',
            body: JSON.stringify(body),
        });
        return toDomainCustomer(result);
    }
    async update(id, updates) {
        const body = toUpdatePayload(updates);
        const result = await this.request(`/customers/${id}`, {
            method: 'PUT',
            body: JSON.stringify(body),
        });
        return toDomainCustomer(result);
    }
    async delete(id) {
        await this.request(`/customers/${id}`, { method: 'DELETE' });
    }
}
exports.RestCustomerRepository = RestCustomerRepository;
