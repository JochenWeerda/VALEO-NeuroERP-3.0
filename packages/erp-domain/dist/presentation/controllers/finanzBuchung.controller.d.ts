/**
 * Express router for FinanzBuchung generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */
import { FinanzBuchungService } from '../../application/services/finanzBuchung.service';
export interface FinanzBuchungRouterDependencies {
    service: FinanzBuchungService;
    baseRoute?: string;
}
export declare function buildFinanzBuchungRouter({ service, baseRoute }: FinanzBuchungRouterDependencies): any;
//# sourceMappingURL=finanzBuchung.controller.d.ts.map