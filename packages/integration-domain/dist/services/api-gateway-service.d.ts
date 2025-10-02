import { ApiGateway } from '../core/entities/api-gateway';
export declare class ApiGatewayService {
    private gateways;
    createGateway(gateway: ApiGateway): Promise<ApiGateway>;
    getGateway(id: string): Promise<ApiGateway | null>;
    getAllGateways(): Promise<ApiGateway[]>;
}
//# sourceMappingURL=api-gateway-service.d.ts.map