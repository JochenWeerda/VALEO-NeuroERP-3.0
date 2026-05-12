/**
 * Express router for FinanzDebitor generated via CRM toolkit.
 * Listen und Schreibantworten: gleicher Contract wie übriges erp-domain ({@link ../types/api-pagination.ts}).
 */
import { Router } from 'express';
import { FinanzDebitorService } from '../../application/services/finanzDebitor.service';
export interface FinanzDebitorRouterDependencies {
    service: FinanzDebitorService;
    baseRoute?: string;
}
export declare function buildFinanzDebitorRouter({ service, baseRoute }: FinanzDebitorRouterDependencies): Router;
//# sourceMappingURL=finanzDebitor.controller.d.ts.map