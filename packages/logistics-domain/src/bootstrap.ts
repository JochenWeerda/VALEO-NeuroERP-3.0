import 'reflect-metadata';
import express, { Request, Response, NextFunction } from 'express';
// @ts-ignore
import cors from 'cors';
// @ts-ignore
import helmet from 'helmet';
// @ts-ignore
import compression from 'compression';
// @ts-ignore
import morgan from 'morgan';

import { InMemoryLogisticsRepository } from './infrastructure/repositories/in-memory/in-memory-logistics-repository';
import { InMemoryEventBus } from './infrastructure/messaging/logistics-event-bus';
import { LogisticsMetrics } from './infrastructure/observability/metrics';

import { ShipmentOrchestratorService } from './application/services/shipment-orchestrator-service';
import { RoutingOptimizationService } from './application/services/routing-optimization-service';
import { DispatchService } from './application/services/dispatch-service';
import { SlotDockYardService } from './application/services/slot-dock-yard-service';
import { TelematicsGatewayService } from './application/services/telematics-gateway-service';
import { ProofOfDeliveryService } from './application/services/proof-of-delivery-service';
import { WeighbridgeIntegrationService } from './application/services/weighbridge-integration-service';
import { FreightRatingService } from './application/services/freight-rating-service';
import { CarrierConnectService } from './application/services/carrier-connect-service';
import { CostingBillingService } from './application/services/costing-billing-service';
import { EmissionsService } from './application/services/emissions-service';
import { DangerousColdchainService } from './application/services/dangerous-coldchain-service';
import { ReturnsService } from './application/services/returns-service';

import { createLogisticsRouter } from './presentation/controllers/logistics-api-controller';

const app = express();
app.use(cors());
app.use(helmet());
// @ts-ignore
app.use(compression());
app.use(morgan('combined'));

const repository = new InMemoryLogisticsRepository();
const eventBus = new InMemoryEventBus();
const metrics = new LogisticsMetrics();

const shipmentService = new ShipmentOrchestratorService(repository, eventBus, metrics);
const routingService = new RoutingOptimizationService(repository, repository, eventBus, metrics);
const dispatchService = new DispatchService(repository, repository, eventBus, metrics);
const yardService = new SlotDockYardService(repository, eventBus);
const telematicsService = new TelematicsGatewayService(repository, repository, eventBus);
const podService = new ProofOfDeliveryService(repository, eventBus);
const weighbridgeService = new WeighbridgeIntegrationService(repository, eventBus);
const ratingService = new FreightRatingService(repository, eventBus);
const carrierService = new CarrierConnectService(repository, eventBus);
const costingService = new CostingBillingService(eventBus);
const emissionsService = new EmissionsService(repository, eventBus);
const safetyService = new DangerousColdchainService(repository, eventBus);
const returnsService = new ReturnsService(repository, eventBus);

const router = createLogisticsRouter({
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

export function startLogisticsServer(): void {
  app.listen(PORT, () => {
    console.log(`Logistics domain listening on port ${PORT}`);
  });
}

if (require.main === module) {
  startLogisticsServer();
}
