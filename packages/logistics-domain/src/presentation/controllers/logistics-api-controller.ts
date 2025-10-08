import express, { Request, Response, NextFunction } from 'express';
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
import {
  CapturePodDto,
  CostingApplyDto,
  CreateShipmentDto,
  DispatchAssignDto,
  EmissionCalcDto,
  FreightQuoteRequestDto,
  ReturnRequestDto,
  RoutingPlanRequestDto,
  SafetyValidationDto,
  SlotBookingDto,
  TelemetryPushDto,
  WeighingCaptureDto,
} from '../../application/dto/logistics-dtos';
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

export function createLogisticsRouter(deps: LogisticsControllerDeps): express.Router {
  const router = express.Router();
  router.use(express.json());

  router.get('/health', (_req: Request, res: Response) => {
    res.status(200).json({ status: 'ok', domain: 'logistics' });
  });

  router.get('/metrics', async (_req: Request, res: Response, next: NextFunction) => {
    try {
      const output = await deps.metrics.metrics();
      res.header('Content-Type', 'text/plain');
      res.send(output);
    } catch (error) {
      next(error);
    }
  });

  router.post('/shipments', async (req, res, next) => {
    try {
      const dto = req.body as CreateShipmentDto;
      const shipment = await deps.shipments.createShipment(dto);
      res.status(201).json({ shipmentId: shipment.shipmentId, status: shipment.status });
    } catch (error) {
      next(error);
    }
  });

  router.get('/shipments/:tenantId/:shipmentId', async (req, res, next) => {
    try {
      const { tenantId, shipmentId } = req.params;
      const shipment = await deps.shipments.getShipment(tenantId, shipmentId);
      if (shipment === undefined || shipment === null) {
        res.status(404).json({ message: 'Shipment not found' });
        return;
      }
      res.json(shipment.toJSON());
    } catch (error) {
      next(error);
    }
  });

  router.post('/routing/plan', async (req, res, next) => {
    try {
      const dto = req.body as RoutingPlanRequestDto;
      const route = await deps.routing.planRoute(dto);
      res.status(201).json({ routeId: route.routeId, status: route.status });
    } catch (error) {
      next(error);
    }
  });

  router.post('/routing/replan', async (req, res, next) => {
    try {
      const dto = req.body as RoutingPlanRequestDto & { reason: string };
      const route = await deps.routing.replanRoute(dto, dto.reason ?? 'manual');
      res.status(200).json({ routeId: route.routeId, status: route.status });
    } catch (error) {
      next(error);
    }
  });

  router.post('/dispatch/assign', async (req, res, next) => {
    try {
      const dto = req.body as DispatchAssignDto;
      const assignment = await deps.dispatch.assign(dto);
      res.status(201).json({ assignmentId: assignment.assignmentId, status: assignment.status });
    } catch (error) {
      next(error);
    }
  });

  router.post('/dispatch/reassign', async (req, res, next) => {
    try {
      const dto = req.body as DispatchAssignDto & { previousDriverId: string };
      const assignment = await deps.dispatch.reassign(dto, dto.previousDriverId);
      res.status(200).json({ assignmentId: assignment.assignmentId, status: assignment.status });
    } catch (error) {
      next(error);
    }
  });

  router.post('/slots/book', async (req, res, next) => {
    try {
      const dto = req.body as SlotBookingDto;
      const visit = await deps.yard.bookSlot(dto);
      res.status(201).json({ visitId: visit.visitId, status: visit.status });
    } catch (error) {
      next(error);
    }
  });

  router.post('/yard/checkin', async (req, res, next) => {
    try {
      const { tenantId, shipmentId } = req.body as { tenantId: string; shipmentId: string };
      const visit = await deps.yard.checkIn(tenantId, shipmentId);
      res.status(200).json({ visitId: visit.visitId, status: visit.status });
    } catch (error) {
      next(error);
    }
  });

  router.post('/yard/checkout', async (req, res, next) => {
    try {
      const { tenantId, shipmentId } = req.body as { tenantId: string; shipmentId: string };
      const visit = await deps.yard.checkOut(tenantId, shipmentId);
      res.status(200).json({ visitId: visit.visitId, status: visit.status });
    } catch (error) {
      next(error);
    }
  });

  router.post('/telematics/push', async (req, res, next) => {
    try {
      const dto = req.body as TelemetryPushDto;
      const record = await deps.telematics.ingest(dto);
      res.status(202).json({ telemetryId: record.telemetryId });
    } catch (error) {
      next(error);
    }
  });

  router.get('/eta/:tenantId/:shipmentId', async (req, res, next) => {
    try {
      const { tenantId, shipmentId } = req.params;
      const etaMinutes = await deps.telematics.calculateEta(tenantId, shipmentId);
      res.status(200).json({ shipmentId, etaMinutes });
    } catch (error) {
      next(error);
    }
  });

  router.post('/pod/capture', async (req, res, next) => {
    try {
      const dto = req.body as CapturePodDto;
      const pod = await deps.pod.capture(dto);
      res.status(201).json({ podId: pod.podId });
    } catch (error) {
      next(error);
    }
  });

  router.post('/weighings', async (req, res, next) => {
    try {
      const dto = req.body as WeighingCaptureDto;
      const record = await deps.weighbridge.capture(dto);
      res.status(201).json({ weighingId: record.weighingId, netWeightKg: record.netWeightKg });
    } catch (error) {
      next(error);
    }
  });

  router.post('/rating/quote', async (req, res, next) => {
    try {
      const dto = req.body as FreightQuoteRequestDto;
      const rate = await deps.rating.quote(dto);
      res.status(201).json({ rateId: rate.rateId, total: rate.totalAmount });
    } catch (error) {
      next(error);
    }
  });

  router.post('/carrier/label', async (req, res, next) => {
    try {
      const document = await deps.carrier.createLabel(req.body);
      res.status(201).json({ documentId: document.documentId });
    } catch (error) {
      next(error);
    }
  });

  router.post('/carrier/manifest', async (req, res, next) => {
    try {
      const document = await deps.carrier.submitManifest(req.body);
      res.status(201).json({ documentId: document.documentId });
    } catch (error) {
      next(error);
    }
  });

  router.post('/carrier/invoice', async (req, res, next) => {
    try {
      const document = await deps.carrier.registerInvoice(req.body);
      res.status(201).json({ documentId: document.documentId });
    } catch (error) {
      next(error);
    }
  });

  router.post('/costing/apply', async (req, res, next) => {
    try {
      const dto = req.body as CostingApplyDto;
      deps.costing.allocate(dto);
      res.status(202).json({ shipmentId: dto.shipmentId, total: dto.total });
    } catch (error) {
      next(error);
    }
  });

  router.post('/costing/approve', async (req, res, next) => {
    try {
      const { tenantId, shipmentId, carrierId, amount, currency } = req.body as {
        tenantId: string;
        shipmentId: string;
        carrierId: string;
        amount: number;
        currency: string;
      };
      deps.costing.approveFreightBill(tenantId, shipmentId, carrierId, amount, currency);
      res.status(202).json({ shipmentId, carrierId, amount, currency });
    } catch (error) {
      next(error);
    }
  });

  router.post('/emissions/calc', async (req, res, next) => {
    try {
      const dto = req.body as EmissionCalcDto;
      const emission = await deps.emissions.calculate(dto);
      res.status(201).json({ emissionId: emission.emissionId, co2eKg: emission.co2eKg });
    } catch (error) {
      next(error);
    }
  });

  router.post('/safety/alert', async (req, res, next) => {
    try {
      const dto = req.body as SafetyValidationDto;
      const alert = await deps.safety.raiseAlert(dto);
      res.status(201).json({ alertId: alert.alertId, severity: alert.severity });
    } catch (error) {
      next(error);
    }
  });

  router.post('/coldchain/alert', async (req, res, next) => {
    try {
      const { tenantId, referenceId, shipmentId, temperatureC, message } = req.body as {
        tenantId: string;
        referenceId: string;
        shipmentId?: string;
        temperatureC: number;
        message: string;
      };
      const alert = await deps.safety.raiseColdChainAlert(tenantId, referenceId, shipmentId, temperatureC, message);
      res.status(201).json({ alertId: alert.alertId, severity: alert.severity });
    } catch (error) {
      next(error);
    }
  });

  router.post('/returns', async (req, res, next) => {
    try {
      const dto = req.body as ReturnRequestDto;
      const order = await deps.returns.create(dto);
      res.status(201).json({ returnId: order.returnId, status: order.status });
    } catch (error) {
      next(error);
    }
  });

  router.post('/returns/receive', async (req, res, next) => {
    try {
      const { tenantId, returnId } = req.body as { tenantId: string; returnId: string };
      const order = await deps.returns.receive(tenantId, returnId);
      res.status(200).json({ returnId: order.returnId, status: order.status });
    } catch (error) {
      next(error);
    }
  });

  router.use((error: unknown, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
    const message = error instanceof Error ? error.message : 'Unknown error';
    res.status(400).json({ message });
  });

  return router;
}

