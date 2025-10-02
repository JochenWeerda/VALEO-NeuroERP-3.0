"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.KPI = void 0;
class KPI {
    id;
    tenantId;
    name;
    description;
    value;
    unit;
    context;
    calculatedAt;
    metadata;
    version;
    constructor(id, tenantId, name, description, value, unit, context, calculatedAt, metadata, version = 1) {
        this.id = id;
        this.tenantId = tenantId;
        this.name = name;
        this.description = description;
        this.value = value;
        this.unit = unit;
        this.context = context;
        this.calculatedAt = calculatedAt;
        this.metadata = metadata;
        this.version = version;
    }
    static create(params) {
        return new KPI(params.id, params.tenantId, params.name, params.description, params.value, params.unit, params.context || {}, new Date(), params.metadata, 1);
    }
    updateValue(newValue) {
        return new KPI(this.id, this.tenantId, this.name, this.description, newValue, this.unit, this.context, new Date(), {
            ...this.metadata,
            lastUpdated: new Date(),
        }, this.version + 1);
    }
    isExpired(maxAgeMinutes = 60) {
        const ageMs = Date.now() - this.calculatedAt.getTime();
        const maxAgeMs = maxAgeMinutes * 60 * 1000;
        return ageMs > maxAgeMs;
    }
    toJSON() {
        return {
            id: this.id,
            tenantId: this.tenantId,
            name: this.name,
            description: this.description,
            value: this.value,
            unit: this.unit,
            context: this.context,
            calculatedAt: this.calculatedAt.toISOString(),
            metadata: this.metadata,
            version: this.version,
        };
    }
}
exports.KPI = KPI;
//# sourceMappingURL=kpi.js.map