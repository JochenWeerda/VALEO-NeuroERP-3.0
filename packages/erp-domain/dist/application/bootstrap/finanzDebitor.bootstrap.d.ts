/**
 * Bootstrap for FinanzDebitor domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */
import type { Router } from 'express';
import { Pool } from 'pg';
import { FinanzDebitorPostgresRepository } from '../../infrastructure/repositories/finanzDebitor-postgres.repository';
import { FinanzDebitorService } from '../services/finanzDebitor.service';
export interface FinanzDebitorBootstrapDependencies {
    pool: Pool;
}
export interface FinanzDebitorModule {
    repository: FinanzDebitorPostgresRepository;
    service: FinanzDebitorService;
    router: Router;
}
export declare function initFinanzDebitorModule({ pool }: FinanzDebitorBootstrapDependencies): FinanzDebitorModule;
//# sourceMappingURL=finanzDebitor.bootstrap.d.ts.map