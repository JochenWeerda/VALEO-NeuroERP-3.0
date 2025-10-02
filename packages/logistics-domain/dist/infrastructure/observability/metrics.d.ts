import { Counter, Gauge, Histogram } from 'prom-client';
export declare class LogisticsMetrics {
    private readonly registry;
    readonly shipmentsCounter: Counter<string>;
    readonly dispatchGauge: Gauge<string>;
    readonly etaDeviationHistogram: Histogram<string>;
    constructor();
    metrics(): Promise<string>;
}
//# sourceMappingURL=metrics.d.ts.map