import express from 'express';
import { ShipmentOrchestratorService } from '../../application/services/shipment-orchestrator-service';
import { RoutingOptimizationService } from '../../application/services/routing-optimization-service';
import { DispatchService } from '../../application/services/dispatch-service';
import { SlotDockYardService } from '../../application/services/slot-dock-yard-service';
import { TelematicsGatewayService } from '../../application/services/telematics-gateway-service';
import { ProofOfDeliveryService } from '../../application/services/proof-of-delivery-service';
import { WeighbridgeIntegrationService } from '../../application/services/weighbridge-integration-service';
import { FreightRatingService } from '../../application/services/freight-rating-service';
import { CarrierConnectService } from '../../application/services/carrier-connect-service';
import { CostingBillingService } from '../../application/services/costing-billing-service';
import { EmissionsService } from '../../application/services/emissions-service';
import { DangerousColdchainService } from '../../application/services/dangerous-coldchain-service';
import { ReturnsService } from '../../application/services/returns-service';
import { LogisticsMetrics } from '../../infrastructure/observability/metrics';
export interface LogisticsControllerDeps {
    shipments: ShipmentOrchestratorService;
    routing: RoutingOptimizationService;
    dispatch: DispatchService;
    yard: SlotDockYardService;
    telematics: TelematicsGatewayService;
    pod: ProofOfDeliveryService;
    weighbridge: WeighbridgeIntegrationService;
    rating: FreightRatingService;
    carrier: CarrierConnectService;
    costing: CostingBillingService;
    emissions: EmissionsService;
    safety: DangerousColdchainService;
    returns: ReturnsService;
    metrics: LogisticsMetrics;
}
export declare function createLogisticsRouter(deps: LogisticsControllerDeps): express.Router;
//# sourceMappingURL=logistics-api-controller.d.ts.map