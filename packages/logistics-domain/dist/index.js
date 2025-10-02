"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createLogisticsRouter = exports.LogisticsMetrics = exports.InMemoryEventBus = exports.InMemoryLogisticsRepository = exports.TimeWindow = exports.TemperatureRange = exports.Address = exports.ReturnOrder = exports.SafetyAlert = exports.EmissionRecord = exports.CarrierDocument = exports.FreightRate = exports.WeighingRecord = exports.ProofOfDelivery = exports.TelemetryRecord = exports.YardVisit = exports.DispatchAssignment = exports.RoutePlan = exports.Shipment = exports.ReturnsService = exports.DangerousColdchainService = exports.EmissionsService = exports.CostingBillingService = exports.CarrierConnectService = exports.FreightRatingService = exports.WeighbridgeIntegrationService = exports.ProofOfDeliveryService = exports.TelematicsGatewayService = exports.SlotDockYardService = exports.DispatchService = exports.RoutingOptimizationService = exports.ShipmentOrchestratorService = exports.startLogisticsServer = void 0;
// Main entry point for the logistics domain
var bootstrap_1 = require("./bootstrap");
Object.defineProperty(exports, "startLogisticsServer", { enumerable: true, get: function () { return bootstrap_1.startLogisticsServer; } });
// Services
var shipment_orchestrator_service_1 = require("./application/services/shipment-orchestrator-service");
Object.defineProperty(exports, "ShipmentOrchestratorService", { enumerable: true, get: function () { return shipment_orchestrator_service_1.ShipmentOrchestratorService; } });
var routing_optimization_service_1 = require("./application/services/routing-optimization-service");
Object.defineProperty(exports, "RoutingOptimizationService", { enumerable: true, get: function () { return routing_optimization_service_1.RoutingOptimizationService; } });
var dispatch_service_1 = require("./application/services/dispatch-service");
Object.defineProperty(exports, "DispatchService", { enumerable: true, get: function () { return dispatch_service_1.DispatchService; } });
var slot_dock_yard_service_1 = require("./application/services/slot-dock-yard-service");
Object.defineProperty(exports, "SlotDockYardService", { enumerable: true, get: function () { return slot_dock_yard_service_1.SlotDockYardService; } });
var telematics_gateway_service_1 = require("./application/services/telematics-gateway-service");
Object.defineProperty(exports, "TelematicsGatewayService", { enumerable: true, get: function () { return telematics_gateway_service_1.TelematicsGatewayService; } });
var proof_of_delivery_service_1 = require("./application/services/proof-of-delivery-service");
Object.defineProperty(exports, "ProofOfDeliveryService", { enumerable: true, get: function () { return proof_of_delivery_service_1.ProofOfDeliveryService; } });
var weighbridge_integration_service_1 = require("./application/services/weighbridge-integration-service");
Object.defineProperty(exports, "WeighbridgeIntegrationService", { enumerable: true, get: function () { return weighbridge_integration_service_1.WeighbridgeIntegrationService; } });
var freight_rating_service_1 = require("./application/services/freight-rating-service");
Object.defineProperty(exports, "FreightRatingService", { enumerable: true, get: function () { return freight_rating_service_1.FreightRatingService; } });
var carrier_connect_service_1 = require("./application/services/carrier-connect-service");
Object.defineProperty(exports, "CarrierConnectService", { enumerable: true, get: function () { return carrier_connect_service_1.CarrierConnectService; } });
var costing_billing_service_1 = require("./application/services/costing-billing-service");
Object.defineProperty(exports, "CostingBillingService", { enumerable: true, get: function () { return costing_billing_service_1.CostingBillingService; } });
var emissions_service_1 = require("./application/services/emissions-service");
Object.defineProperty(exports, "EmissionsService", { enumerable: true, get: function () { return emissions_service_1.EmissionsService; } });
var dangerous_coldchain_service_1 = require("./application/services/dangerous-coldchain-service");
Object.defineProperty(exports, "DangerousColdchainService", { enumerable: true, get: function () { return dangerous_coldchain_service_1.DangerousColdchainService; } });
var returns_service_1 = require("./application/services/returns-service");
Object.defineProperty(exports, "ReturnsService", { enumerable: true, get: function () { return returns_service_1.ReturnsService; } });
// DTOs
__exportStar(require("./application/dto/logistics-dtos"), exports);
// Entities
var shipment_1 = require("./core/entities/shipment");
Object.defineProperty(exports, "Shipment", { enumerable: true, get: function () { return shipment_1.Shipment; } });
var route_plan_1 = require("./core/entities/route-plan");
Object.defineProperty(exports, "RoutePlan", { enumerable: true, get: function () { return route_plan_1.RoutePlan; } });
var dispatch_assignment_1 = require("./core/entities/dispatch-assignment");
Object.defineProperty(exports, "DispatchAssignment", { enumerable: true, get: function () { return dispatch_assignment_1.DispatchAssignment; } });
var yard_visit_1 = require("./core/entities/yard-visit");
Object.defineProperty(exports, "YardVisit", { enumerable: true, get: function () { return yard_visit_1.YardVisit; } });
var telemetry_record_1 = require("./core/entities/telemetry-record");
Object.defineProperty(exports, "TelemetryRecord", { enumerable: true, get: function () { return telemetry_record_1.TelemetryRecord; } });
var proof_of_delivery_1 = require("./core/entities/proof-of-delivery");
Object.defineProperty(exports, "ProofOfDelivery", { enumerable: true, get: function () { return proof_of_delivery_1.ProofOfDelivery; } });
var weighing_record_1 = require("./core/entities/weighing-record");
Object.defineProperty(exports, "WeighingRecord", { enumerable: true, get: function () { return weighing_record_1.WeighingRecord; } });
var freight_rate_1 = require("./core/entities/freight-rate");
Object.defineProperty(exports, "FreightRate", { enumerable: true, get: function () { return freight_rate_1.FreightRate; } });
var carrier_document_1 = require("./core/entities/carrier-document");
Object.defineProperty(exports, "CarrierDocument", { enumerable: true, get: function () { return carrier_document_1.CarrierDocument; } });
var emission_record_1 = require("./core/entities/emission-record");
Object.defineProperty(exports, "EmissionRecord", { enumerable: true, get: function () { return emission_record_1.EmissionRecord; } });
var safety_alert_1 = require("./core/entities/safety-alert");
Object.defineProperty(exports, "SafetyAlert", { enumerable: true, get: function () { return safety_alert_1.SafetyAlert; } });
var return_order_1 = require("./core/entities/return-order");
Object.defineProperty(exports, "ReturnOrder", { enumerable: true, get: function () { return return_order_1.ReturnOrder; } });
// Value Objects
var address_1 = require("./core/value-objects/address");
Object.defineProperty(exports, "Address", { enumerable: true, get: function () { return address_1.Address; } });
var temperature_range_1 = require("./core/value-objects/temperature-range");
Object.defineProperty(exports, "TemperatureRange", { enumerable: true, get: function () { return temperature_range_1.TemperatureRange; } });
var time_window_1 = require("./core/value-objects/time-window");
Object.defineProperty(exports, "TimeWindow", { enumerable: true, get: function () { return time_window_1.TimeWindow; } });
// Infrastructure
var in_memory_logistics_repository_1 = require("./infrastructure/repositories/in-memory/in-memory-logistics-repository");
Object.defineProperty(exports, "InMemoryLogisticsRepository", { enumerable: true, get: function () { return in_memory_logistics_repository_1.InMemoryLogisticsRepository; } });
var logistics_event_bus_1 = require("./infrastructure/messaging/logistics-event-bus");
Object.defineProperty(exports, "InMemoryEventBus", { enumerable: true, get: function () { return logistics_event_bus_1.InMemoryEventBus; } });
var metrics_1 = require("./infrastructure/observability/metrics");
Object.defineProperty(exports, "LogisticsMetrics", { enumerable: true, get: function () { return metrics_1.LogisticsMetrics; } });
// Controllers
var logistics_api_controller_1 = require("./presentation/controllers/logistics-api-controller");
Object.defineProperty(exports, "createLogisticsRouter", { enumerable: true, get: function () { return logistics_api_controller_1.createLogisticsRouter; } });
//# sourceMappingURL=index.js.map