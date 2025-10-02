"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApiGatewayService = void 0;
class ApiGatewayService {
    gateways = [];
    async createGateway(gateway) {
        this.gateways.push(gateway);
        return gateway;
    }
    async getGateway(id) {
        return this.gateways.find(g => g.id === id) || null;
    }
    async getAllGateways() {
        return [...this.gateways];
    }
}
exports.ApiGatewayService = ApiGatewayService;
//# sourceMappingURL=api-gateway-service.js.map