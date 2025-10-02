import { QueryBuilder } from './query-builder';
import { Repository } from './repository';
export interface Logger {
    debug(message: string, context?: Record<string, unknown>): void;
    info(message: string, context?: Record<string, unknown>): void;
    warn(message: string, context?: Record<string, unknown>): void;
    error(message: string, context?: Record<string, unknown>): void;
}
export interface MetricsRecorder {
    recordCounter(name: string, value?: number, tags?: Record<string, string>): void;
    recordGauge(name: string, value: number, tags?: Record<string, string>): void;
    recordHistogram(name: string, value: number, tags?: Record<string, string>): void;
}
export interface BaseServiceOptions {
    logger?: Logger;
    metrics?: MetricsRecorder;
    serviceName?: string;
}
export declare abstract class BaseService<TEntity, TId, TRepository extends Repository<TEntity, TId>> {
    protected readonly repository: TRepository;
    protected readonly logger: Logger;
    protected readonly metrics?: MetricsRecorder;
    protected readonly serviceName: string;
    protected constructor(repository: TRepository, options?: BaseServiceOptions);
    protected createQueryBuilder(): QueryBuilder<TEntity>;
    protected logDebug(message: string, context?: Record<string, unknown>): void;
    protected logInfo(message: string, context?: Record<string, unknown>): void;
    protected logWarn(message: string, context?: Record<string, unknown>): void;
    protected logError(message: string, context?: Record<string, unknown>): void;
    protected executeWithMetrics<TResult>(metricName: string, action: () => Promise<TResult>, tags?: Record<string, string>): Promise<TResult>;
    private withServiceContext;
    private withServiceTags;
}
//***REMOVED*** sourceMappingURL=base-service.d.ts.map