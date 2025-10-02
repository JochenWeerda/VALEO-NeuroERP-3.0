import { Repository } from '@valero-neuroerp/utilities';
import { Integration } from '../../core/entities/integration';
export declare class IntegrationRepository implements Repository<Integration> {
    private integrations;
    find(id: string): Promise<Integration | null>;
    findAll(): Promise<Integration[]>;
    create(entity: Integration): Promise<Integration>;
    update(entity: Integration): Promise<Integration>;
    delete(id: string): Promise<boolean>;
}
//# sourceMappingURL=integration-repository.d.ts.map