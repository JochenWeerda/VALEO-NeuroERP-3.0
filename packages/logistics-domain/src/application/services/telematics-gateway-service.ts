import { TelemetryRecord } from '../../core/entities/telemetry-record';
import { TelemetryRepository, RoutePlanRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus, buildEvent } from '../../infrastructure/messaging/logistics-event-bus';
import { TelemetryPushDto } from '../dto/logistics-dtos';

export class TelematicsGatewayService {
  constructor(
    private readonly telemetryRepository: TelemetryRepository,
    private readonly routeRepository: RoutePlanRepository,
    private readonly eventBus: LogisticsEventBus,
  ) {}

  async ingest(dto: TelemetryPushDto): Promise<TelemetryRecord> {
    const record = TelemetryRecord.create({
      tenantId: dto.tenantId,
      vehicleId: dto.vehicleId,
      recordedAt: new Date(dto.recordedAt),
      lat: dto.lat,
      lon: dto.lon,
      speedKph: dto.speedKph,
      temperatureC: dto.temperatureC,
      fuelLevelPercent: dto.fuelLevelPercent,
      meta: dto.meta,
    });

    await this.telemetryRepository.saveTelemetry(record);
    const event = buildEvent('logistics.position.updated', dto.tenantId, { telemetry: record });
    this.eventBus.publish(event);

    return record;
  }

  async calculateEta(tenantId: string, shipmentId: string, referenceTime: Date = new Date()): Promise<number | undefined> {
    const route = await this.routeRepository.findRoutePlanByShipmentId(tenantId, shipmentId);
    if (route === undefined || route === null) {
      return undefined;
    }

    const remainingLegs = route.legs.filter((leg) => leg.eta.to.getTime() >= referenceTime.getTime());
    if (remainingLegs.length === 0) {
      return 0;
    }

    const lastLeg = remainingLegs[remainingLegs.length - 1];
    const etaMinutes = Math.round((lastLeg.eta.to.getTime() - referenceTime.getTime()) / 60000);

    const event = buildEvent('logistics.eta.updated', tenantId, {
      shipmentId,
      stopId: lastLeg.toStopId,
      eta: lastLeg.eta.to.toISOString(),
      confidence: 0.8,
    });
    this.eventBus.publish(event);

    return etaMinutes;
  }
}

