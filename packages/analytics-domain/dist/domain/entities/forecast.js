"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Forecast = void 0;
class Forecast {
    id;
    tenantId;
    metricName;
    horizon;
    horizonUnit;
    model;
    forecastValues;
    confidenceInterval;
    createdAt;
    metadata;
    version;
    constructor(id, tenantId, metricName, horizon, horizonUnit, model, forecastValues, confidenceInterval, createdAt = new Date(), metadata, version = 1) {
        this.id = id;
        this.tenantId = tenantId;
        this.metricName = metricName;
        this.horizon = horizon;
        this.horizonUnit = horizonUnit;
        this.model = model;
        this.forecastValues = forecastValues;
        this.confidenceInterval = confidenceInterval;
        this.createdAt = createdAt;
        this.metadata = metadata;
        this.version = version;
    }
    static create(params) {
        return new Forecast(params.id, params.tenantId, params.metricName, params.horizon, params.horizonUnit, params.model, params.forecastValues, params.confidenceInterval, new Date(), params.metadata, 1);
    }
    updateValues(newValues) {
        return new Forecast(this.id, this.tenantId, this.metricName, this.horizon, this.horizonUnit, this.model, newValues, this.confidenceInterval, this.createdAt, {
            ...this.metadata,
            lastTrainedAt: new Date(),
        }, this.version + 1);
    }
    isExpired(maxAgeHours = 24) {
        const ageMs = Date.now() - this.createdAt.getTime();
        const maxAgeMs = maxAgeHours * 60 * 60 * 1000;
        return ageMs > maxAgeMs;
    }
    getForecastForDate(targetDate) {
        let closest = null;
        let minDiff = Infinity;
        for (const value of this.forecastValues) {
            const diff = Math.abs(value.timestamp.getTime() - targetDate.getTime());
            if (diff < minDiff) {
                minDiff = diff;
                closest = value;
            }
        }
        return closest;
    }
    getAccuracyScore() {
        return this.metadata?.accuracyMetrics?.r2 || null;
    }
    toJSON() {
        return {
            id: this.id,
            tenantId: this.tenantId,
            metricName: this.metricName,
            horizon: this.horizon,
            horizonUnit: this.horizonUnit,
            model: this.model,
            forecastValues: this.forecastValues.map(v => ({
                timestamp: v.timestamp.toISOString(),
                value: v.value,
                lowerBound: v.lowerBound,
                upperBound: v.upperBound,
                confidence: v.confidence,
            })),
            confidenceInterval: this.confidenceInterval,
            createdAt: this.createdAt.toISOString(),
            metadata: this.metadata,
            version: this.version,
        };
    }
}
exports.Forecast = Forecast;
//# sourceMappingURL=forecast.js.map