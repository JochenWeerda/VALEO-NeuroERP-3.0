import { ApiGatewayId } from '@valero-neuroerp/data-models';
export interface ApiGateway {
    id: ApiGatewayId;
    name: string;
    endpoint: string;
    methods: string[];
    rateLimit: number;
    isActive: boolean;
    createdAt: Date;
    updatedAt: Date;
}
export declare function createApiGateway(data: Omit<ApiGateway, 'id' | 'createdAt' | 'updatedAt'>): ApiGateway;
//# sourceMappingURL=api-gateway.d.ts.map