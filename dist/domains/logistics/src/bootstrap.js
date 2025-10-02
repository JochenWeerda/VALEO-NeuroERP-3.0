"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.startLogisticsServer = startLogisticsServer;
require("reflect-metadata");
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const helmet_1 = __importDefault(require("helmet"));
const compression_1 = __importDefault(require("compression"));
const morgan_1 = __importDefault(require("morgan"));
const in_memory_logistics_repository_1 = require("./infrastructure/repositories/in-memory/in-memory-logistics-repository");
const logistics_event_bus_1 = require("./infrastructure/messaging/logistics-event-bus");
const metrics_1 = require("./infrastructure/observability/metrics");
const shipment_orchestrator_service_1 = require("./application/services/shipment-orchestrator-service");
const routing_optimization_service_1 = require("./application/services/routing-optimization-service");
const dispatch_service_1 = require("./application/services/dispatch-service");
const slot_dock_yard_service_1 = require("./application/services/slot-dock-yard-service");
const telematics_gateway_service_1 = require("./application/services/telematics-gateway-service");
const proof_of_delivery_service_1 = require("./application/services/proof-of-delivery-service");
const weighbridge_integration_service_1 = require("./application/services/weighbridge-integration-service");
const freight_rating_service_1 = require("./application/services/freight-rating-service");
const carrier_connect_service_1 = require("./application/services/carrier-connect-service");
const costing_billing_service_1 = require("./application/services/costing-billing-service");
const emissions_service_1 = require("./application/services/emissions-service");
const dangerous_coldchain_service_1 = require("./application/services/dangerous-coldchain-service");
const returns_service_1 = require("./application/services/returns-service");
const logistics_api_controller_1 = require("./presentation/controllers/logistics-api-controller");
const app = (0, express_1.default)();
app.use((0, cors_1.default)());
app.use((0, helmet_1.default)());
app.use((0, compression_1.default)());
app.use((0, morgan_1.default)('combined'));
const repository = new in_memory_logistics_repository_1.InMemoryLogisticsRepository();
const eventBus = new logistics_event_bus_1.InMemoryEventBus();
const metrics = new metrics_1.LogisticsMetrics();
const shipmentService = new shipment_orchestrator_service_1.ShipmentOrchestratorService(repository, eventBus, metrics);
const routingService = new routing_optimization_service_1.RoutingOptimizationService(repository, repository, eventBus, metrics);
const dispatchService = new dispatch_service_1.DispatchService(repository, repository, eventBus, metrics);
const yardService = new slot_dock_yard_service_1.SlotDockYardService(repository, eventBus);
const telematicsService = new telematics_gateway_service_1.TelematicsGatewayService(repository, repository, eventBus);
const podService = new proof_of_delivery_service_1.ProofOfDeliveryService(repository, eventBus);
const weighbridgeService = new weighbridge_integration_service_1.WeighbridgeIntegrationService(repository, eventBus);
const ratingService = new freight_rating_service_1.FreightRatingService(repository, eventBus);
const carrierService = new carrier_connect_service_1.CarrierConnectService(repository, eventBus);
const costingService = new costing_billing_service_1.CostingBillingService(eventBus);
const emissionsService = new emissions_service_1.EmissionsService(repository, eventBus);
const safetyService = new dangerous_coldchain_service_1.DangerousColdchainService(repository, eventBus);
const returnsService = new returns_service_1.ReturnsService(repository, eventBus);
const router = (0, logistics_api_controller_1.createLogisticsRouter)({
    shipments: shipmentService,
    routing: routingService,
    dispatch: dispatchService,
    yard: yardService,
    telematics: telematicsService,
    pod: podService,
    weighbridge: weighbridgeService,
    rating: ratingService,
    carrier: carrierService,
    costing: costingService,
    emissions: emissionsService,
    safety: safetyService,
    returns: returnsService,
    metrics,
});
app.use('/logistics', router);
const PORT = Number(process.env.LOGISTICS_PORT ?? 3070);
function startLogisticsServer() {
    app.listen(PORT, () => {
        console.log(Logistics, domain, listening, on, port);
    });
}
if (require.main === module) {
    startLogisticsServer();
}
