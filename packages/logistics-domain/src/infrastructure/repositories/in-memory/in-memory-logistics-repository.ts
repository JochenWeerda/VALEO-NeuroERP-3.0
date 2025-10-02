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
import {
  CarrierDocumentRepository,
  DispatchRepository,
  EmissionRepository,
  FreightRateRepository,
  ProofOfDeliveryRepository,
  ReturnOrderRepository,
  RoutePlanRepository,
  SafetyAlertRepository,
  ShipmentRepository,
  TelemetryRepository,
  WeighingRepository,
  YardRepository,
} from '../interfaces/logistics-repositories';

interface TenantBuckets<T> {
  [tenantId: string]: Map<string, T>;
}

interface TelemetryBuckets {
  [tenantId: string]: Map<string, TelemetryRecord[]>;
}

export class InMemoryLogisticsRepository
  implements
    ShipmentRepository,
    RoutePlanRepository,
    DispatchRepository,
    YardRepository,
    TelemetryRepository,
    ProofOfDeliveryRepository,
    WeighingRepository,
    FreightRateRepository,
    CarrierDocumentRepository,
    EmissionRepository,
    SafetyAlertRepository,
    ReturnOrderRepository
{
  private readonly shipments: TenantBuckets<Shipment> = {};
  private readonly routesById: TenantBuckets<RoutePlan> = {};
  private readonly routesByShipment: TenantBuckets<RoutePlan> = {};
  private readonly assignments: TenantBuckets<DispatchAssignment> = {};
  private readonly yardVisits: TenantBuckets<YardVisit> = {};
  private readonly telemetry: TelemetryBuckets = {};
  private readonly pods: TenantBuckets<ProofOfDelivery> = {};
  private readonly weighings: TenantBuckets<WeighingRecord> = {};
  private readonly freightRates: TenantBuckets<FreightRate> = {};
  private readonly carrierDocs: TenantBuckets<CarrierDocument> = {};
  private readonly emissions: TenantBuckets<EmissionRecord> = {};
  private readonly safetyAlerts: TenantBuckets<SafetyAlert> = {};
  private readonly returnOrders: TenantBuckets<ReturnOrder> = {};

  async saveShipment(shipment: Shipment): Promise<void> {
    const bucket = this.ensureBucket(this.shipments, shipment.tenantId);
    bucket.set(shipment.shipmentId, shipment);
  }

  async findShipmentById(tenantId: string, shipmentId: string): Promise<Shipment | undefined> {
    return this.shipments[tenantId]?.get(shipmentId);
  }

  async listShipmentsByTenant(tenantId: string): Promise<Shipment[]> {
    return Array.from(this.shipments[tenantId]?.values() ?? []);
  }

  async saveRoutePlan(routePlan: RoutePlan): Promise<void> {
    const byId = this.ensureBucket(this.routesById, routePlan.tenantId);
    byId.set(routePlan.routeId, routePlan);
    const byShipment = this.ensureBucket(this.routesByShipment, routePlan.tenantId);
    byShipment.set(routePlan.shipmentId, routePlan);
  }

  async findRoutePlanById(tenantId: string, routeId: string): Promise<RoutePlan | undefined> {
    return this.routesById[tenantId]?.get(routeId);
  }

  async findRoutePlanByShipmentId(tenantId: string, shipmentId: string): Promise<RoutePlan | undefined> {
    return this.routesByShipment[tenantId]?.get(shipmentId);
  }

  async saveAssignment(assignment: DispatchAssignment): Promise<void> {
    const bucket = this.ensureBucket(this.assignments, assignment.tenantId);
    bucket.set(assignment.routeId, assignment);
  }

  async findAssignmentByRouteId(tenantId: string, routeId: string): Promise<DispatchAssignment | undefined> {
    return this.assignments[tenantId]?.get(routeId);
  }

  async saveYardVisit(visit: YardVisit): Promise<void> {
    const bucket = this.ensureBucket(this.yardVisits, visit.tenantId);
    bucket.set(visit.shipmentId, visit);
  }

  async findYardVisitByShipmentId(tenantId: string, shipmentId: string): Promise<YardVisit | undefined> {
    return this.yardVisits[tenantId]?.get(shipmentId);
  }

  async saveTelemetry(record: TelemetryRecord): Promise<void> {
    const bucket = this.ensureTelemetryBucket(record.tenantId, record.vehicleId);
    bucket.unshift(record);
    if (bucket.length > 1000) {
      bucket.pop();
    }
  }

  async listRecentTelemetryByVehicle(tenantId: string, vehicleId: string, limit: number): Promise<TelemetryRecord[]> {
    return (this.telemetry[tenantId]?.get(vehicleId) ?? []).slice(0, limit);
  }

  async saveProofOfDelivery(pod: ProofOfDelivery): Promise<void> {
    const bucket = this.ensureBucket(this.pods, pod.tenantId);
    bucket.set(pod.shipmentId, pod);
  }

  async saveWeighing(record: WeighingRecord): Promise<void> {
    const bucket = this.ensureBucket(this.weighings, record.tenantId);
    bucket.set(record.weighingId, record);
  }

  async saveFreightRate(rate: FreightRate): Promise<void> {
    const bucket = this.ensureBucket(this.freightRates, rate.tenantId);
    bucket.set(rate.shipmentId, rate);
  }

  async saveCarrierDocument(document: CarrierDocument): Promise<void> {
    const bucket = this.ensureBucket(this.carrierDocs, document.tenantId);
    bucket.set(document.documentId, document);
  }

  async saveEmission(record: EmissionRecord): Promise<void> {
    const bucket = this.ensureBucket(this.emissions, record.tenantId);
    bucket.set(record.shipmentId, record);
  }

  async saveSafetyAlert(alert: SafetyAlert): Promise<void> {
    const bucket = this.ensureBucket(this.safetyAlerts, alert.tenantId);
    bucket.set(alert.alertId, alert);
  }

  async saveReturnOrder(order: ReturnOrder): Promise<void> {
    const bucket = this.ensureBucket(this.returnOrders, order.tenantId);
    bucket.set(order.returnId, order);
  }

  async findReturnOrderById(tenantId: string, returnId: string): Promise<ReturnOrder | undefined> {
    return this.returnOrders[tenantId]?.get(returnId);
  }

  private ensureBucket<T>(store: TenantBuckets<T>, tenantId: string): Map<string, T> {
    if (!store[tenantId]) {
      store[tenantId] = new Map<string, T>();
    }
    return store[tenantId]!;
  }

  private ensureTelemetryBucket(tenantId: string, vehicleId: string): TelemetryRecord[] {
    if (!this.telemetry[tenantId]) {
      this.telemetry[tenantId] = new Map<string, TelemetryRecord[]>();
    }
    if (!this.telemetry[tenantId]!.get(vehicleId)) {
      this.telemetry[tenantId]!.set(vehicleId, []);
    }
    return this.telemetry[tenantId]!.get(vehicleId)!;
  }
}

