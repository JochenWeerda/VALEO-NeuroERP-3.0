/**
 * Express router for FinanzKreditor generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */
import { FinanzKreditorService } from '../../application/services/finanzKreditor.service';
export interface FinanzKreditorRouterDependencies {
    service: FinanzKreditorService;
    baseRoute?: string;
}
export declare function buildFinanzKreditorRouter({ service, baseRoute }: FinanzKreditorRouterDependencies): any;
//# sourceMappingURL=finanzKreditor.controller.d.ts.map