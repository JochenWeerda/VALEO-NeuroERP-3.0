/**
 * Express router for FinanzBuchung generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */
import { Router } from 'express';
import { FinanzBuchungService } from '../../application/services/finanzBuchung.service';
export interface FinanzBuchungRouterDependencies {
    service: FinanzBuchungService;
    baseRoute?: string;
}
export declare function buildFinanzBuchungRouter({ service, baseRoute }: FinanzBuchungRouterDependencies): Router;
//# sourceMappingURL=finanzBuchung.controller.d.ts.map