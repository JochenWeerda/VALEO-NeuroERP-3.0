"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createApiGateway = createApiGateway;
const data_models_1 = require("@valero-neuroerp/data-models");
function createApiGateway(data) {
    return {
        ...data,
        id: (0, data_models_1.createId)('ApiGatewayId'),
        createdAt: new Date(),
        updatedAt: new Date()
    };
}
//# sourceMappingURL=api-gateway.js.map