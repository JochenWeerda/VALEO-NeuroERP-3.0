/**
 * PostgreSQL Sync Job Repository Implementation
 */
import { SyncJob } from '@domain/entities/sync-job.js';
export class PostgresSyncJobRepository {
    connection;
    constructor(connection) {
        this.connection = connection;
    }
    async findById(id) {
        try {
            const result = await this.connection.query('SELECT * FROM sync_jobs WHERE id = $1', [id]);
            if (result.rows.length === 0) {
                return { success: true, data: null };
            }
            const syncJob = this.mapRowToSyncJob(result.rows[0]);
            return { success: true, data: syncJob };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findAll(options) {
        try {
            const { page = 1, limit = 10, sortBy = 'created_at', sortOrder = 'DESC' } = options || {};
            const offset = (page - 1) * limit;
            // Get total count
            const countResult = await this.connection.query('SELECT COUNT(*) as total FROM sync_jobs');
            const total = parseInt(countResult.rows[0].total);
            // Get paginated data
            const result = await this.connection.query(`SELECT * FROM sync_jobs 
         ORDER BY ${this.mapSortField(sortBy)} ${sortOrder.toUpperCase()}
         LIMIT $1 OFFSET $2`, [limit, offset]);
            const syncJobs = result.rows.map(row => this.mapRowToSyncJob(row));
            const totalPages = Math.ceil(total / limit);
            const paginatedResult = {
                data: syncJobs,
                pagination: {
                    page,
                    limit,
                    total,
                    totalPages,
                    hasNext: page < totalPages,
                    hasPrev: page > 1
                }
            };
            return { success: true, data: paginatedResult };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async create(syncJob) {
        try {
            await this.connection.query(`INSERT INTO sync_jobs (
          id, name, integration_id, config, status, last_run, next_run, 
          records_processed, error_message, is_active, description, tags, 
          created_at, updated_at, created_by, updated_by
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)`, [
                syncJob.id,
                syncJob.name,
                syncJob.integrationId,
                JSON.stringify(syncJob.config),
                syncJob.status,
                syncJob.lastRun,
                syncJob.nextRun,
                syncJob.recordsProcessed,
                syncJob.errorMessage,
                syncJob.isActive,
                syncJob.description,
                JSON.stringify(syncJob.tags),
                syncJob.createdAt,
                syncJob.updatedAt,
                syncJob.createdBy,
                syncJob.updatedBy
            ]);
            return { success: true, data: syncJob };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async update(syncJob) {
        try {
            await this.connection.query(`UPDATE sync_jobs SET 
          name = $2, integration_id = $3, config = $4, status = $5, last_run = $6, 
          next_run = $7, records_processed = $8, error_message = $9, is_active = $10, 
          description = $11, tags = $12, updated_at = $13, updated_by = $14
        WHERE id = $1`, [
                syncJob.id,
                syncJob.name,
                syncJob.integrationId,
                JSON.stringify(syncJob.config),
                syncJob.status,
                syncJob.lastRun,
                syncJob.nextRun,
                syncJob.recordsProcessed,
                syncJob.errorMessage,
                syncJob.isActive,
                syncJob.description,
                JSON.stringify(syncJob.tags),
                syncJob.updatedAt,
                syncJob.updatedBy
            ]);
            return { success: true, data: syncJob };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async delete(id) {
        try {
            await this.connection.query('DELETE FROM sync_jobs WHERE id = $1', [id]);
            return { success: true, data: undefined };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findByIntegrationId(integrationId) {
        try {
            const result = await this.connection.query('SELECT * FROM sync_jobs WHERE integration_id = $1 ORDER BY created_at DESC', [integrationId]);
            const syncJobs = result.rows.map(row => this.mapRowToSyncJob(row));
            return { success: true, data: syncJobs };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findByName(name) {
        try {
            const result = await this.connection.query('SELECT * FROM sync_jobs WHERE name = $1 LIMIT 1', [name]);
            if (result.rows.length === 0) {
                return { success: true, data: null };
            }
            const syncJob = this.mapRowToSyncJob(result.rows[0]);
            return { success: true, data: syncJob };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findByStatus(status) {
        try {
            const result = await this.connection.query('SELECT * FROM sync_jobs WHERE status = $1 ORDER BY created_at DESC', [status]);
            const syncJobs = result.rows.map(row => this.mapRowToSyncJob(row));
            return { success: true, data: syncJobs };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findScheduled() {
        try {
            const result = await this.connection.query(`SELECT * FROM sync_jobs 
         WHERE status = 'pending' 
         AND is_active = true 
         AND next_run <= NOW()
         ORDER BY next_run ASC`);
            const syncJobs = result.rows.map(row => this.mapRowToSyncJob(row));
            return { success: true, data: syncJobs };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findRunning() {
        try {
            const result = await this.connection.query('SELECT * FROM sync_jobs WHERE status = $1 ORDER BY last_run DESC', ['running']);
            const syncJobs = result.rows.map(row => this.mapRowToSyncJob(row));
            return { success: true, data: syncJobs };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findFailed() {
        try {
            const result = await this.connection.query('SELECT * FROM sync_jobs WHERE status = $1 ORDER BY last_run DESC', ['failed']);
            const syncJobs = result.rows.map(row => this.mapRowToSyncJob(row));
            return { success: true, data: syncJobs };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    mapRowToSyncJob(row) {
        return SyncJob.fromJSON({
            id: row.id,
            name: row.name,
            integrationId: row.integration_id,
            config: row.config,
            status: row.status,
            lastRun: row.last_run,
            nextRun: row.next_run,
            recordsProcessed: row.records_processed,
            errorMessage: row.error_message,
            isActive: row.is_active,
            description: row.description,
            tags: row.tags,
            createdAt: row.created_at,
            updatedAt: row.updated_at,
            createdBy: row.created_by,
            updatedBy: row.updated_by
        });
    }
    mapSortField(field) {
        const fieldMap = {
            'name': 'name',
            'status': 'status',
            'lastRun': 'last_run',
            'nextRun': 'next_run',
            'recordsProcessed': 'records_processed',
            'createdAt': 'created_at',
            'updatedAt': 'updated_at',
            'integrationId': 'integration_id',
            'created_by': 'created_by',
            'updated_by': 'updated_by'
        };
        return fieldMap[field] || 'created_at';
    }
}
//# sourceMappingURL=postgres-sync-job-repository.js.map