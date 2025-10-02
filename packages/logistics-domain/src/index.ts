// Main entry point for the logistics domain
export { startLogisticsServer } from './bootstrap';

// Services
export { ShipmentOrchestratorService } from './application/services/shipment-orchestrator-service';
export { RoutingOptimizationService } from './application/services/routing-optimization-service';
export { DispatchService } from './application/services/dispatch-service';
export { SlotDockYardService } from './application/services/slot-dock-yard-service';
export { TelematicsGatewayService } from './application/services/telematics-gateway-service';
export { ProofOfDeliveryService } from './application/services/proof-of-delivery-service';
export { WeighbridgeIntegrationService } from './application/services/weighbridge-integration-service';
export { FreightRatingService } from './application/services/freight-rating-service';
export { CarrierConnectService } from './application/services/carrier-connect-service';
export { CostingBillingService } from './application/services/costing-billing-service';
export { EmissionsService } from './application/services/emissions-service';
export { DangerousColdchainService } from './application/services/dangerous-coldchain-service';
export { ReturnsService } from './application/services/returns-service';

// DTOs
export * from './application/dto/logistics-dtos';

// Entities
export { Shipment } from './core/entities/shipment';
export { RoutePlan } from './core/entities/route-plan';
export { DispatchAssignment } from './core/entities/dispatch-assignment';
export { YardVisit } from './core/entities/yard-visit';
export { TelemetryRecord } from './core/entities/telemetry-record';
export { ProofOfDelivery } from './core/entities/proof-of-delivery';
export { WeighingRecord } from './core/entities/weighing-record';
export { FreightRate } from './core/entities/freight-rate';
export { CarrierDocument } from './core/entities/carrier-document';
export { EmissionRecord } from './core/entities/emission-record';
export { SafetyAlert } from './core/entities/safety-alert';
export { ReturnOrder } from './core/entities/return-order';

// Value Objects
export { Address } from './core/value-objects/address';
export { TemperatureRange } from './core/value-objects/temperature-range';
export { TimeWindow } from './core/value-objects/time-window';

// Infrastructure
export { InMemoryLogisticsRepository } from './infrastructure/repositories/in-memory/in-memory-logistics-repository';
export { InMemoryEventBus } from './infrastructure/messaging/logistics-event-bus';
export { LogisticsMetrics } from './infrastructure/observability/metrics';

// Controllers
export { createLogisticsRouter } from './presentation/controllers/logistics-api-controller';