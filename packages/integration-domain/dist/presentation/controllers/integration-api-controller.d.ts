import { Integration } from '../../core/entities/integration';
export declare class IntegrationApiController {
    getIntegrations(): Promise<Integration[]>;
    getIntegration(id: string): Promise<Integration | null>;
    createIntegration(data: Partial<Integration>): Promise<Integration>;
    updateIntegration(id: string, data: Partial<Integration>): Promise<Integration | null>;
    deleteIntegration(id: string): Promise<boolean>;
}
//# sourceMappingURL=integration-api-controller.d.ts.map