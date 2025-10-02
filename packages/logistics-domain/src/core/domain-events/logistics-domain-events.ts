import { Shipment } from '../entities/shipment';
import { RoutePlan } from '../entities/route-plan';
import { DispatchAssignment } from '../entities/dispatch-assignment';
import { YardVisit } from '../entities/yard-visit';
import { TelemetryRecord } from '../entities/telemetry-record';
import { ProofOfDelivery } from '../entities/proof-of-delivery';
import { WeighingRecord } from '../entities/weighing-record';
import { FreightRate } from '../entities/freight-rate';
import { CarrierDocument } from '../entities/carrier-document';
import { EmissionRecord } from '../entities/emission-record';
import { SafetyAlert } from '../entities/safety-alert';
import { ReturnOrder } from '../entities/return-order';

export type ShipmentSnapshot = ReturnType<Shipment['toJSON']>;

export interface LogisticsEventBase<TType extends string, TPayload> {
  readonly eventId: string;
  readonly eventType: TType;
  readonly timestamp: string;
  readonly tenantId: string;
  readonly payload: TPayload;
  readonly metadata?: Record<string, unknown>;
}

export type ShipmentCreatedEvent = LogisticsEventBase<'logistics.shipment.created', { shipment: ShipmentSnapshot }>;
export type ShipmentCanceledEvent = LogisticsEventBase<'logistics.shipment.canceled', { shipmentId: string; reason: string }>;
export type ShipmentSplitEvent = LogisticsEventBase<'logistics.shipment.split', { sourceShipmentId: string; newShipmentIds: string[] }>;

export type RoutePlannedEvent = LogisticsEventBase<'logistics.route.planned', { route: RoutePlan }>;
export type RouteReplannedEvent = LogisticsEventBase<'logistics.route.replanned', { route: RoutePlan; reason: string }>;

export type DispatchAssignedEvent = LogisticsEventBase<'logistics.dispatch.assigned', { assignment: DispatchAssignment }>;
export type DispatchChangedEvent = LogisticsEventBase<'logistics.dispatch.changed', { assignment: DispatchAssignment; previousDriverId?: string }>;

export type SlotBookedEvent = LogisticsEventBase<'logistics.slot.booked', { yardVisit: YardVisit }>;
export type DockAssignedEvent = LogisticsEventBase<'logistics.dock.assigned', { yardVisit: YardVisit }>;
export type YardStatusChangedEvent = LogisticsEventBase<'logistics.yard.statusChanged', { yardVisit: YardVisit }>;

export type PositionUpdatedEvent = LogisticsEventBase<'logistics.position.updated', { telemetry: TelemetryRecord }>;
export type StopArrivedEvent = LogisticsEventBase<'logistics.stop.arrived', { shipmentId: string; stopId: string; occurredAt: string }>;
export type StopDepartedEvent = LogisticsEventBase<'logistics.stop.departed', { shipmentId: string; stopId: string; occurredAt: string }>;
export type EtaUpdatedEvent = LogisticsEventBase<'logistics.eta.updated', { shipmentId: string; stopId: string; eta: string; confidence: number }>;

export type PodCapturedEvent = LogisticsEventBase<'logistics.pod.captured', { pod: ProofOfDelivery }>;
export type EcmrGeneratedEvent = LogisticsEventBase<'logistics.ecmr.generated', { documentId: string; shipmentId: string }>;

export type WeightMeasuredEvent = LogisticsEventBase<'logistics.weight.measured', { weighing: WeighingRecord }>;
export type WeightToleranceExceededEvent = LogisticsEventBase<'logistics.weight.toleranceExceeded', { weighing: WeighingRecord; thresholdKg: number }>;

export type FreightRatedEvent = LogisticsEventBase<'logistics.freight.rated', { freightRate: FreightRate }>;

export type CarrierLabelCreatedEvent = LogisticsEventBase<'logistics.carrier.labelCreated', { document: CarrierDocument }>;
export type CarrierManifestSubmittedEvent = LogisticsEventBase<'logistics.carrier.manifestSubmitted', { document: CarrierDocument }>;
export type CarrierInvoiceReceivedEvent = LogisticsEventBase<'logistics.carrier.invoiceReceived', { document: CarrierDocument }>;

export type LogisticsCostAllocatedEvent = LogisticsEventBase<'logistics.costs.allocated', { shipmentId: string; total: number; currency: string }>;
export type FreightBillApprovedEvent = LogisticsEventBase<'logistics.freight.billApproved', { shipmentId: string; carrierId: string; amount: number; currency: string }>;

export type EmissionsUpdatedEvent = LogisticsEventBase<'logistics.emissions.updated', { emission: EmissionRecord }>;

export type SafetyViolationEvent = LogisticsEventBase<'logistics.safety.violation', { alert: SafetyAlert }>;
export type ColdChainAlertEvent = LogisticsEventBase<'logistics.coldchain.alert', { alert: SafetyAlert; temperatureC: number }>;

export type ReturnCreatedEvent = LogisticsEventBase<'logistics.return.created', { returnOrder: ReturnOrder }>;
export type ReturnReceivedEvent = LogisticsEventBase<'logistics.return.received', { returnOrder: ReturnOrder }>;

export type LogisticsEvent =
  | ShipmentCreatedEvent
  | ShipmentCanceledEvent
  | ShipmentSplitEvent
  | RoutePlannedEvent
  | RouteReplannedEvent
  | DispatchAssignedEvent
  | DispatchChangedEvent
  | SlotBookedEvent
  | DockAssignedEvent
  | YardStatusChangedEvent
  | PositionUpdatedEvent
  | StopArrivedEvent
  | StopDepartedEvent
  | EtaUpdatedEvent
  | PodCapturedEvent
  | EcmrGeneratedEvent
  | WeightMeasuredEvent
  | WeightToleranceExceededEvent
  | FreightRatedEvent
  | CarrierLabelCreatedEvent
  | CarrierManifestSubmittedEvent
  | CarrierInvoiceReceivedEvent
  | LogisticsCostAllocatedEvent
  | FreightBillApprovedEvent
  | EmissionsUpdatedEvent
  | SafetyViolationEvent
  | ColdChainAlertEvent
  | ReturnCreatedEvent
  | ReturnReceivedEvent;

