/**
 * Integration Routes Configuration
 */
import { Router } from 'express';
export declare class IntegrationRoutes {
    private router;
    private controller;
    private validator;
    private logger;
    constructor(integrationService: any);
    private setupRoutes;
    private wrapAsync;
    getRouter(): Router;
}
//# sourceMappingURL=integration-routes.d.ts.map