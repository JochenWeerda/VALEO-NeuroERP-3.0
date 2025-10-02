"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PostgresCustomerRepository = void 0;
const node_crypto_1 = require("node:crypto");
const branded_types_1 = require("../../../../../packages/data-models/src/branded-types");
const postgres_1 = require("../../../../../packages/utilities/src/postgres");
function mapRow(row) {
    const address = row.street || row.city || row.postal_code || row.country
        ? {
            street: row.street ?? undefined,
            city: row.city ?? undefined,
            postalCode: row.postal_code ?? undefined,
            country: row.country ?? undefined,
        }
        : undefined;
    return {
        id: (0, branded_types_1.brandValue)(row.id, "CustomerId"),
        customerNumber: row.customer_number ?? row.id,
        name: row.name,
        type: row.type,
        status: row.status,
        email: row.email ? row.email : undefined,
        phone: row.phone ? row.phone : undefined,
        website: row.website ?? undefined,
        address,
        industry: row.industry ?? undefined,
        companySize: row.company_size ?? undefined,
        annualRevenue: row.annual_revenue ?? undefined,
        taxId: row.tax_id ?? undefined,
        vatNumber: row.vat_number ?? undefined,
        salesRepId: row.sales_rep_id ?? undefined,
        leadSource: row.lead_source ?? undefined,
        leadScore: row.lead_score ?? undefined,
        notes: row.notes ?? undefined,
        tags: row.tags ?? undefined,
        createdAt: new Date(row.created_at),
        updatedAt: row.updated_at ? new Date(row.updated_at) : undefined,
    };
}
class PostgresCustomerRepository {
    constructor(options) {
        this.connectionString = options.connectionString;
        this.poolName = options.poolName ?? "crm";
        (0, postgres_1.getPostgresPool)({ connectionString: this.connectionString, name: this.poolName });
    }
    async list(filters = {}) {
        const where = [];
        const params = [];
        if (filters.status) {
            params.push(filters.status);
            where.push("status = $" + params.length);
        }
        if (filters.type) {
            params.push(filters.type);
            where.push("type = $" + params.length);
        }
        if (filters.search) {
            const search = filters.search.trim().toLowerCase();
            params.push(search);
            where.push("lower(name) = $" + params.length);
        }
        const clause = where.length ? " WHERE " + where.join(" AND ") : "";
        const limit = filters.limit ?? 50;
        const offset = filters.offset ?? 0;
        params.push(limit, offset);
        const sql = "SELECT id, customer_number, name, type, status, email, phone, website, street, city, " +
            "postal_code, country, industry, company_size, annual_revenue, tax_id, vat_number, sales_rep_id, " +
            "lead_source, lead_score, notes, tags, created_at, updated_at FROM crm.customers" +
            clause +
            " ORDER BY name ASC LIMIT $" + (params.length - 1) + " OFFSET $" + params.length;
        const pool = (0, postgres_1.getPostgresPool)({ connectionString: this.connectionString, name: this.poolName });
        const result = await pool.query(sql, params);
        return result.rows.map(mapRow);
    }
    async findById(id) {
        const pool = (0, postgres_1.getPostgresPool)({ connectionString: this.connectionString, name: this.poolName });
        const sql = "SELECT id, customer_number, name, type, status, email, phone, website, street, city, " +
            "postal_code, country, industry, company_size, annual_revenue, tax_id, vat_number, sales_rep_id, " +
            "lead_source, lead_score, notes, tags, created_at, updated_at FROM crm.customers WHERE id = $1";
        const result = await pool.query(sql, [id]);
        if (!result.rowCount) {
            return null;
        }
        return mapRow(result.rows[0]);
    }
    async create(payload) {
        const pool = (0, postgres_1.getPostgresPool)({ connectionString: this.connectionString, name: this.poolName });
        const now = new Date();
        const id = (0, node_crypto_1.randomUUID)();
        const sql = "INSERT INTO crm.customers (id, customer_number, name, type, status, email, phone, website, street, city, " +
            "postal_code, country, industry, company_size, annual_revenue, tax_id, vat_number, sales_rep_id, lead_source, lead_score, notes, tags, created_at, updated_at) " +
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25) " +
            "RETURNING id, customer_number, name, type, status, email, phone, website, street, city, postal_code, country, industry, company_size, annual_revenue, tax_id, vat_number, sales_rep_id, lead_source, lead_score, notes, tags, created_at, updated_at";
        const address = payload.address ?? {};
        const params = [
            id,
            payload.customerNumber ?? id,
            payload.name,
            payload.type,
            payload.status ?? "active",
            payload.email ?? null,
            payload.phone ?? null,
            payload.website ?? null,
            address.street ?? null,
            address.city ?? null,
            address.postalCode ?? null,
            address.country ?? null,
            payload.industry ?? null,
            payload.companySize ?? null,
            payload.annualRevenue ?? null,
            payload.taxId ?? null,
            payload.vatNumber ?? null,
            payload.salesRepId ?? null,
            payload.leadSource ?? null,
            payload.leadScore ?? null,
            payload.notes ?? null,
            payload.tags ?? null,
            now.toISOString(),
            now.toISOString()
        ];
        const result = await pool.query(sql, params);
        return mapRow(result.rows[0]);
    }
    async update(id, updates) {
        const pool = (0, postgres_1.getPostgresPool)({ connectionString: this.connectionString, name: this.poolName });
        const sets = [];
        const params = [];
        const assign = (column, value) => {
            params.push(value);
            sets.push(column + " = $" + params.length);
        };
        if (updates.customerNumber !== undefined)
            assign("customer_number", updates.customerNumber ?? null);
        if (updates.name !== undefined)
            assign("name", updates.name);
        if (updates.type !== undefined)
            assign("type", updates.type);
        if (updates.status !== undefined)
            assign("status", updates.status ?? null);
        if (updates.email !== undefined)
            assign("email", updates.email ?? null);
        if (updates.phone !== undefined)
            assign("phone", updates.phone ?? null);
        if (updates.website !== undefined)
            assign("website", updates.website ?? null);
        if (updates.address !== undefined) {
            assign("street", updates.address?.street ?? null);
            assign("city", updates.address?.city ?? null);
            assign("postal_code", updates.address?.postalCode ?? null);
            assign("country", updates.address?.country ?? null);
        }
        if (updates.industry !== undefined)
            assign("industry", updates.industry ?? null);
        if (updates.companySize !== undefined)
            assign("company_size", updates.companySize ?? null);
        if (updates.annualRevenue !== undefined)
            assign("annual_revenue", updates.annualRevenue ?? null);
        if (updates.taxId !== undefined)
            assign("tax_id", updates.taxId ?? null);
        if (updates.vatNumber !== undefined)
            assign("vat_number", updates.vatNumber ?? null);
        if (updates.salesRepId !== undefined)
            assign("sales_rep_id", updates.salesRepId ?? null);
        if (updates.leadSource !== undefined)
            assign("lead_source", updates.leadSource ?? null);
        if (updates.leadScore !== undefined)
            assign("lead_score", updates.leadScore ?? null);
        if (updates.notes !== undefined)
            assign("notes", updates.notes ?? null);
        if (updates.tags !== undefined)
            assign("tags", updates.tags ?? null);
        if (!sets.length) {
            const current = await this.findById(id);
            if (!current) {
                throw new Error("Customer " + id + " not found.");
            }
            return current;
        }
        params.push(new Date().toISOString());
        sets.push("updated_at = $" + params.length);
        params.push(id);
        const sql = "UPDATE crm.customers SET " + sets.join(", ") + " WHERE id = $" + params.length +
            " RETURNING id, customer_number, name, type, status, email, phone, website, street, city, postal_code, country, industry, company_size, annual_revenue, tax_id, vat_number, sales_rep_id, lead_source, lead_score, notes, tags, created_at, updated_at";
        const result = await pool.query(sql, params);
        if (!result.rowCount) {
            throw new Error("Customer " + id + " not found.");
        }
        return mapRow(result.rows[0]);
    }
    async delete(id) {
        const pool = (0, postgres_1.getPostgresPool)({ connectionString: this.connectionString, name: this.poolName });
        await pool.query("DELETE FROM crm.customers WHERE id = $1", [id]);
    }
}
exports.PostgresCustomerRepository = PostgresCustomerRepository;
