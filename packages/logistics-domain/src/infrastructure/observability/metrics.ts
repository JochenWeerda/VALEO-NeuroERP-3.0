import { collectDefaultMetrics, Counter, Gauge, Histogram, Registry } from 'prom-client';

export class LogisticsMetrics {
  private readonly registry = new Registry();
  readonly shipmentsCounter: Counter<string>;
  readonly dispatchGauge: Gauge<string>;
  readonly etaDeviationHistogram: Histogram<string>;

  constructor() {
    collectDefaultMetrics({ register: this.registry });

    this.shipmentsCounter = new Counter({
      name: 'logistics_shipments_total',
      help: 'Count of shipments orchestrated',
      registers: [this.registry],
      labelNames: ['tenant', 'status'],
    });

    this.dispatchGauge = new Gauge({
      name: 'logistics_dispatch_active_assignments',
      help: 'Active dispatch assignments per tenant',
      registers: [this.registry],
      labelNames: ['tenant'],
    });

    this.etaDeviationHistogram = new Histogram({
      name: 'logistics_eta_deviation_minutes',
      help: 'ETA deviation distribution',
      registers: [this.registry],
      labelNames: ['tenant'],
      buckets: [1, 5, 10, 15, 30, 60],
    });
  }

  metrics(): Promise<string> {
    return this.registry.metrics();
  }
}

