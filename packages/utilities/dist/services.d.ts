export interface Logger {
    debug(message: string, context?: Record<string, unknown>): void;
    info(message: string, context?: Record<string, unknown>): void;
    warn(message: string, context?: Record<string, unknown>): void;
    error(message: string, context?: Record<string, unknown>): void;
}
export interface MetricsRecorder {
    incrementCounter(name: string, labels?: Record<string, string>): void;
    recordGauge(name: string, value: number, labels?: Record<string, string>): void;
    recordHistogram(name: string, value: number, labels?: Record<string, string>): void;
}
export declare class ServiceLocator {
    private static instance;
    private services;
    static getInstance(): ServiceLocator;
    registerInstance<T>(token: string, instance: T): void;
    registerFactory<T>(token: string, factory: () => T): void;
    resolve<T>(token: string): T;
    has(token: string): boolean;
    unregister(token: string): void;
}
export declare const metricsService: MetricsRecorder;
//# sourceMappingURL=services.d.ts.map