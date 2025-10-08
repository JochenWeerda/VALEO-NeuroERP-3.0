import { Shipment } from '../../core/entities/shipment';
import { ShipmentRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus, buildEvent } from '../../infrastructure/messaging/logistics-event-bus';
import { LogisticsMetrics } from '../../infrastructure/observability/metrics';
import { CreateShipmentDto } from '../dto/logistics-dtos';

export class ShipmentOrchestratorService {
  constructor(
    private readonly repository: ShipmentRepository,
    private readonly eventBus: LogisticsEventBus,
    private readonly metrics: LogisticsMetrics,
  ) {}

  async createShipment(dto: CreateShipmentDto): Promise<Shipment> {
    const shipment = Shipment.create({
      tenantId: dto.tenantId,
      reference: dto.reference,
      origin: dto.origin,
      destination: dto.destination,
      priority: dto.priority,
      incoterm: dto.incoterm,
      stops: dto.stops.map((stop) => ({
        sequence: stop.sequence,
        type: stop.type,
        address: stop.address,
        window: stop.window ? { from: new Date(stop.window.from), to: new Date(stop.window.to) } : undefined,
      })),
      payload: dto.payload,
    });

    await this.repository.saveShipment(shipment);
    this.metrics.shipmentsCounter.inc({ tenant: dto.tenantId, status: shipment.status });

    const event = buildEvent('logistics.shipment.created', dto.tenantId, { shipment: shipment.toJSON() });
    this.eventBus.publish(event);

    return shipment;
  }

  async cancelShipment(tenantId: string, shipmentId: string, reason: string): Promise<void> {
    const shipment = await this.repository.findShipmentById(tenantId, shipmentId);
    if (shipment === undefined || shipment === null) {
      throw new Error(`Shipment ${shipmentId} not found for tenant ${tenantId}`);
    }
    shipment.updateStatus('canceled');
    await this.repository.saveShipment(shipment);

    const event = buildEvent('logistics.shipment.canceled', tenantId, { shipmentId, reason });
    this.eventBus.publish(event);
  }

  async listShipments(tenantId: string): Promise<Shipment[]> {
    return this.repository.listShipmentsByTenant(tenantId);
  }

  async getShipment(tenantId: string, shipmentId: string): Promise<Shipment | undefined> {
    return this.repository.findShipmentById(tenantId, shipmentId);
  }
}

