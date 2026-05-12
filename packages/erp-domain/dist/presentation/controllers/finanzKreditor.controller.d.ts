/**
 * Express router for FinanzKreditor generated via CRM toolkit.
 * Listen und Schreibantworten: gleicher Contract wie übriges erp-domain ({@link ../types/api-pagination.ts}).
 */
import { Router } from 'express';
import { FinanzKreditorService } from '../../application/services/finanzKreditor.service';
export interface FinanzKreditorRouterDependencies {
    service: FinanzKreditorService;
    baseRoute?: string;
}
export declare function buildFinanzKreditorRouter({ service, baseRoute }: FinanzKreditorRouterDependencies): Router;
//# sourceMappingURL=finanzKreditor.controller.d.ts.map