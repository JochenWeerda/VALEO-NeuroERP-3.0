/**
 * Integration API Controller
 */
import type { Request, Response } from 'express';
import { IntegrationApplicationService } from '@application/services/integration-application-service.js';
export declare class IntegrationController {
    private integrationService;
    constructor(integrationService: IntegrationApplicationService);
    listIntegrations(req: Request, res: Response): Promise<void>;
    getIntegration(req: Request, res: Response): Promise<void>;
    createIntegration(req: Request, res: Response): Promise<void>;
    updateIntegration(req: Request, res: Response): Promise<void>;
    deleteIntegration(req: Request, res: Response): Promise<void>;
    activateIntegration(req: Request, res: Response): Promise<void>;
    deactivateIntegration(req: Request, res: Response): Promise<void>;
    getIntegrationByName(req: Request, res: Response): Promise<void>;
    getIntegrationsByType(req: Request, res: Response): Promise<void>;
    getActiveIntegrations(req: Request, res: Response): Promise<void>;
    getStatistics(req: Request, res: Response): Promise<void>;
    healthCheck(req: Request, res: Response): Promise<void>;
    private extractUserId;
}
//# sourceMappingURL=integration-controller.d.ts.map