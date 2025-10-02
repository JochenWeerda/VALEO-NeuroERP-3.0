export class MetricsService {
    sinks = new Set();
    addSink(sink) {
        this.sinks.add(sink);
    }
    removeSink(sink) {
        this.sinks.delete(sink);
    }
    clearSinks() {
        this.sinks.clear();
    }
    recordCounter(name, value = 1, tags) {
        this.dispatch({ name, value, kind: 'counter', tags, timestamp: new Date() });
    }
    recordGauge(name, value, tags) {
        this.dispatch({ name, value, kind: 'gauge', tags, timestamp: new Date() });
    }
    recordHistogram(name, value, tags) {
        this.dispatch({ name, value, kind: 'histogram', tags, timestamp: new Date() });
    }
    async time(name, action, tags) {
        const start = Date.now();
        try {
            const result = await action();
            const duration = Date.now() - start;
            this.recordHistogram(name + '.duration.ms', duration, tags);
            return result;
        }
        catch (error) {
            this.recordCounter(name + '.error', 1, { ...(tags ?? {}), error: 'true' });
            throw error;
        }
    }
    dispatch(metric) {
        for (const sink of this.sinks) {
            try {
                const result = sink.record(metric);
                if (result && typeof result.then === 'function') {
                    result.catch((error) => {
                        // Intentionally swallow sink errors to keep metrics non-blocking
                        console.warn('Metrics sink error:', error);
                    });
                }
            }
            catch (error) {
                console.warn('Metrics sink threw synchronously:', error);
            }
        }
    }
}
export const metricsService = new MetricsService();
