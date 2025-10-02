import { Shipment } from '../../../core/entities/shipment';
import { RoutePlan } from '../../../core/entities/route-plan';
import { DispatchAssignment } from '../../../core/entities/dispatch-assignment';
import { YardVisit } from '../../../core/entities/yard-visit';
import { TelemetryRecord } from '../../../core/entities/telemetry-record';
import { ProofOfDelivery } from '../../../core/entities/proof-of-delivery';
import { WeighingRecord } from '../../../core/entities/weighing-record';
import { FreightRate } from '../../../core/entities/freight-rate';
import { CarrierDocument } from '../../../core/entities/carrier-document';
import { EmissionRecord } from '../../../core/entities/emission-record';
import { SafetyAlert } from '../../../core/entities/safety-alert';
import { ReturnOrder } from '../../../core/entities/return-order';

export interface ShipmentRepository {
  saveShipment(shipment: Shipment): Promise<void>;
  findShipmentById(tenantId: string, shipmentId: string): Promise<Shipment | undefined>;
  listShipmentsByTenant(tenantId: string): Promise<Shipment[]>;
}

export interface RoutePlanRepository {
  saveRoutePlan(routePlan: RoutePlan): Promise<void>;
  findRoutePlanById(tenantId: string, routeId: string): Promise<RoutePlan | undefined>;
  findRoutePlanByShipmentId(tenantId: string, shipmentId: string): Promise<RoutePlan | undefined>;
}

export interface DispatchRepository {
  saveAssignment(assignment: DispatchAssignment): Promise<void>;
  findAssignmentByRouteId(tenantId: string, routeId: string): Promise<DispatchAssignment | undefined>;
}

export interface YardRepository {
  saveYardVisit(visit: YardVisit): Promise<void>;
  findYardVisitByShipmentId(tenantId: string, shipmentId: string): Promise<YardVisit | undefined>;
}

export interface TelemetryRepository {
  saveTelemetry(record: TelemetryRecord): Promise<void>;
  listRecentTelemetryByVehicle(tenantId: string, vehicleId: string, limit: number): Promise<TelemetryRecord[]>;
}

export interface ProofOfDeliveryRepository {
  saveProofOfDelivery(pod: ProofOfDelivery): Promise<void>;
}

export interface WeighingRepository {
  saveWeighing(record: WeighingRecord): Promise<void>;
}

export interface FreightRateRepository {
  saveFreightRate(rate: FreightRate): Promise<void>;
}

export interface CarrierDocumentRepository {
  saveCarrierDocument(document: CarrierDocument): Promise<void>;
}

export interface EmissionRepository {
  saveEmission(record: EmissionRecord): Promise<void>;
}

export interface SafetyAlertRepository {
  saveSafetyAlert(alert: SafetyAlert): Promise<void>;
}

export interface ReturnOrderRepository {
  saveReturnOrder(order: ReturnOrder): Promise<void>;
  findReturnOrderById(tenantId: string, returnId: string): Promise<ReturnOrder | undefined>;
}

