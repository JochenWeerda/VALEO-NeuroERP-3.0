/**
 * Bootstrap for FinanzKreditor domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */
import type { Router } from 'express';
import { Pool } from 'pg';
import { FinanzKreditorPostgresRepository } from '../../infrastructure/repositories/finanzKreditor-postgres.repository';
import { FinanzKreditorService } from '../services/finanzKreditor.service';
export interface FinanzKreditorBootstrapDependencies {
    pool: Pool;
}
export interface FinanzKreditorModule {
    repository: FinanzKreditorPostgresRepository;
    service: FinanzKreditorService;
    router: Router;
}
export declare function initFinanzKreditorModule({ pool }: FinanzKreditorBootstrapDependencies): FinanzKreditorModule;
//# sourceMappingURL=finanzKreditor.bootstrap.d.ts.map