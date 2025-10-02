import { MetricsRecorder } from './base-service';
export type MetricKind = 'counter' | 'gauge' | 'histogram';
export interface MetricEvent {
    name: string;
    value: number;
    kind: MetricKind;
    tags?: Record<string, string>;
    timestamp: Date;
}
export interface MetricsSink {
    record(metric: MetricEvent): void | Promise<void>;
}
export declare class MetricsService implements MetricsRecorder {
    private readonly sinks;
    addSink(sink: MetricsSink): void;
    removeSink(sink: MetricsSink): void;
    clearSinks(): void;
    recordCounter(name: string, value?: number, tags?: Record<string, string>): void;
    recordGauge(name: string, value: number, tags?: Record<string, string>): void;
    recordHistogram(name: string, value: number, tags?: Record<string, string>): void;
    time<T>(name: string, action: () => Promise<T>, tags?: Record<string, string>): Promise<T>;
    private dispatch;
}
export declare const metricsService: MetricsService;
//***REMOVED*** sourceMappingURL=metrics-service.d.ts.map