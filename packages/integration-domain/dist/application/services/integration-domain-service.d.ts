import { Integration } from '../../core/entities/integration';
export declare class IntegrationDomainService {
    createIntegration(data: Omit<Integration, 'id' | 'createdAt' | 'updatedAt'>): Promise<Integration>;
    getIntegration(id: string): Promise<Integration | null>;
    getAllIntegrations(): Promise<Integration[]>;
    updateIntegration(id: string, updates: Partial<Integration>): Promise<Integration | null>;
    deleteIntegration(id: string): Promise<boolean>;
}
//# sourceMappingURL=integration-domain-service.d.ts.map