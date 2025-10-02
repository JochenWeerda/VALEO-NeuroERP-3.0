"use strict";
/**
 * VALEO NeuroERP 3.0 - Postgres ProductRepository Repository
 *
 * PostgreSQL implementation of ProductRepository repository.
 * Handles database operations with proper error handling and transactions.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.PostgresProductRepositoryRepository = void 0;
class PostgresProductRepositoryRepository {
    constructor(db) {
        this.db = db;
    }
    async findById(id) {
        const query = 'SELECT * FROM productrepositorys WHERE id = $1';
        const result = await this.db.query(query, [id]);
        if (result.rows.length === 0) {
            return null;
        }
        return this.mapRowToEntity(result.rows[0]);
    }
    async findAll() {
        const query = 'SELECT * FROM productrepositorys ORDER BY created_at DESC';
        const result = await this.db.query(query);
        return result.rows.map((row) => this.mapRowToEntity(row));
    }
    async create(entity) {
        const query = 'INSERT INTO productrepositorys (id, name, status, createdAt, updatedAt) VALUES ($1, $2, $3, $4, $5)';
        const params = [entity.id, entity.name, entity.status, entity.createdAt, entity.updatedAt];
        await this.db.query(query, params);
    }
    async update(id, entity) {
        const query = 'UPDATE productrepositorys SET name = $2, status = $3, createdAt = $4, updatedAt = $5, updated_at = NOW() WHERE id = $1';
        const params = [id, entity.name, entity.status, entity.createdAt, entity.updatedAt];
        const result = await this.db.query(query, params);
        if (result.rowCount === 0) {
            throw new Error('ProductRepository not found: ' + id);
        }
    }
    async delete(id) {
        const query = 'DELETE FROM productrepositorys WHERE id = $1';
        const result = await this.db.query(query, [id]);
        if (result.rowCount === 0) {
            throw new Error('ProductRepository not found: ' + id);
        }
    }
    async exists(id) {
        const query = 'SELECT 1 FROM productrepositorys WHERE id = $1 LIMIT 1';
        const result = await this.db.query(query, [id]);
        return result.rows.length > 0;
    }
    async count() {
        const query = 'SELECT COUNT(*) as count FROM productrepositorys';
        const result = await this.db.query(query);
        return parseInt(result.rows[0].count);
    }
    async findByName(value) {
        const query = 'SELECT * FROM productrepositorys WHERE name = $1 ORDER BY created_at DESC';
        const result = await this.db.query(query, [value]);
        return result.rows.map((row) => this.mapRowToEntity(row));
    }
    async findByStatus(value) {
        const query = 'SELECT * FROM productrepositorys WHERE status = $1 ORDER BY created_at DESC';
        const result = await this.db.query(query, [value]);
        return result.rows.map((row) => this.mapRowToEntity(row));
    }
    mapRowToEntity(row) {
        return {
            id: row.id,
            name: row.name,
            status: row.status,
            createdAt: row.createdAt,
            updatedAt: row.updatedAt,
        };
    }
}
exports.PostgresProductRepositoryRepository = PostgresProductRepositoryRepository;
