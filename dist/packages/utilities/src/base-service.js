import { QueryBuilder } from './query-builder';
const noopLogger = {
    debug() { },
    info() { },
    warn() { },
    error() { },
};
export class BaseService {
    repository;
    logger;
    metrics;
    serviceName;
    constructor(repository, options = {}) {
        this.repository = repository;
        this.logger = options.logger ?? noopLogger;
        this.metrics = options.metrics;
        this.serviceName = options.serviceName ?? this.constructor.name;
    }
    createQueryBuilder() {
        return new QueryBuilder();
    }
    logDebug(message, context) {
        this.logger.debug(message, this.withServiceContext(context));
    }
    logInfo(message, context) {
        this.logger.info(message, this.withServiceContext(context));
    }
    logWarn(message, context) {
        this.logger.warn(message, this.withServiceContext(context));
    }
    logError(message, context) {
        this.logger.error(message, this.withServiceContext(context));
    }
    async executeWithMetrics(metricName, action, tags = {}) {
        if (!this.metrics) {
            return action();
        }
        const start = Date.now();
        try {
            const result = await action();
            const duration = Date.now() - start;
            this.metrics.recordHistogram(metricName + '.duration.ms', duration, this.withServiceTags(tags));
            this.metrics.recordCounter(metricName + '.success', 1, this.withServiceTags(tags));
            return result;
        }
        catch (error) {
            this.metrics.recordCounter(metricName + '.error', 1, this.withServiceTags({ ...tags, error: 'true' }));
            throw error;
        }
    }
    withServiceContext(context) {
        if (!context) {
            return { service: this.serviceName };
        }
        return { service: this.serviceName, ...context };
    }
    withServiceTags(tags) {
        return { service: this.serviceName, ...(tags ?? {}) };
    }
}
