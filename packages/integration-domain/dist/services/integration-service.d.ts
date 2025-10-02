import { Integration } from '../core/entities/integration';
export declare class IntegrationService {
    private integrations;
    createIntegration(integration: Integration): Promise<Integration>;
    getIntegration(id: string): Promise<Integration | null>;
    getAllIntegrations(): Promise<Integration[]>;
}
//# sourceMappingURL=integration-service.d.ts.map