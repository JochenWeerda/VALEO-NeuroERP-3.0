/**
 * Express router for FinanzBuchung generated via CRM toolkit.
 */
import { Router } from 'express';
import { FinanzBuchungService } from '../../application/services/finanzBuchung.service';
export interface FinanzBuchungRouterDependencies {
    service: FinanzBuchungService;
    baseRoute?: string;
}
export declare function buildFinanzBuchungRouter({ service, baseRoute }: FinanzBuchungRouterDependencies): Router;
//# sourceMappingURL=finanzBuchung.controller.d.ts.map