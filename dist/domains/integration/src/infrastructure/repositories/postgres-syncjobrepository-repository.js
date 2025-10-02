"use strict";
/**
 * VALEO NeuroERP 3.0 - Postgres SyncJobRepository Repository
 *
 * PostgreSQL implementation of SyncJobRepository repository.
 * Handles database operations with proper error handling and transactions.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.PostgresSyncJobRepositoryRepository = void 0;
class PostgresSyncJobRepositoryRepository {
    db;
    constructor(db) {
        this.db = db;
    }
    async findById(id) {
        const query = 'SELECT * FROM syncjobrepositorys WHERE id = $1';
        const result = await this.db.query(query, [id]);
        if (result.rows.length === 0) {
            return null;
        }
        return this.mapRowToEntity(result.rows[0]);
    }
    async findAll() {
        const query = 'SELECT * FROM syncjobrepositorys ORDER BY created_at DESC';
        const result = await this.db.query(query);
        return result.rows.map(row => this.mapRowToEntity(row));
    }
    async create(entity) {
        const columns = ['id', 'name', 'status', 'createdAt', 'updatedAt'];
        const values = [$1, $2, $3, $4, $5];
        const params = [entity.id, entity.name, entity.status, entity.createdAt, entity.updatedAt];
        const query = `INSERT INTO syncjobrepositorys (${columns.join(', ')}) VALUES (${values.join(', ')})`;
        await this.db.query(query, params);
    }
    async update(id, entity) {
        const setClause = 'name = $2, status = $3, createdAt = $4, updatedAt = $5';
        const params = [id, entity.name, entity.status, entity.createdAt, entity.updatedAt];
        const query = `UPDATE syncjobrepositorys SET ${setClause}, updated_at = NOW() WHERE id = $1`;
        const result = await this.db.query(query, params);
        if (result.rowCount === 0) {
            throw new Error('SyncJobRepository not found: ${id}');
        }
    }
    async delete(id) {
        const query = 'DELETE FROM syncjobrepositorys WHERE id = $1';
        const result = await this.db.query(query, [id]);
        if (result.rowCount === 0) {
            throw new Error('SyncJobRepository not found: ${id}');
        }
    }
    async exists(id) {
        const query = 'SELECT 1 FROM syncjobrepositorys WHERE id = $1 LIMIT 1';
        const result = await this.db.query(query, [id]);
        return result.rows.length > 0;
    }
    async count() {
        const query = 'SELECT COUNT(*) as count FROM syncjobrepositorys';
        const result = await this.db.query(query);
        return parseInt(result.rows[0].count);
    }
    async findByName(value) {
        const query = 'SELECT * FROM syncjobrepositorys WHERE name = $1 ORDER BY created_at DESC';
        const result = await this.db.query(query, [value]);
        return result.rows.map(row => this.mapRowToEntity(row));
    }
    async findByStatus(value) {
        const query = 'SELECT * FROM syncjobrepositorys WHERE status = $1 ORDER BY created_at DESC';
        const result = await this.db.query(query, [value]);
        return result.rows.map(row => this.mapRowToEntity(row));
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
exports.PostgresSyncJobRepositoryRepository = PostgresSyncJobRepositoryRepository;
