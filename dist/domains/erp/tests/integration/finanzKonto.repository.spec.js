"use strict";
/**
 * Integration test scaffold for FinanzKontoPostgresRepository.
 * Connects to a live Postgres instance; skips automatically if env var is missing.
 */
Object.defineProperty(exports, "__esModule", { value: true });
const pg_1 = require("pg");
const finanzKonto_postgres_repository_1 = require("../../src/infrastructure/repositories/finanzKonto-postgres.repository");
describe('FinanzKontoPostgresRepository', () => {
    const connectionString = process.env.ERP_DATABASE_URL;
    if (!connectionString) {
        it('is skipped because ERP_DATABASE_URL is not defined', () => {
            expect(true).toBe(true);
        });
        return;
    }
    const pool = new pg_1.Pool({ connectionString });
    const repository = new finanzKonto_postgres_repository_1.FinanzKontoPostgresRepository(pool);
    afterAll(async () => {
        await pool.end();
    });
    it('list returns an array', async () => {
        const items = await repository.list();
        expect(Array.isArray(items)).toBe(true);
    });
});
