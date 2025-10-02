"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Report = void 0;
class Report {
    id;
    tenantId;
    type;
    parameters;
    generatedAt;
    uri;
    format;
    metadata;
    version;
    constructor(id, tenantId, type, parameters, generatedAt, uri, format = 'json', metadata, version = 1) {
        this.id = id;
        this.tenantId = tenantId;
        this.type = type;
        this.parameters = parameters;
        this.generatedAt = generatedAt;
        this.uri = uri;
        this.format = format;
        this.metadata = metadata;
        this.version = version;
    }
    static create(params) {
        return new Report(params.id, params.tenantId, params.type, params.parameters, new Date(), undefined, params.format || 'json', params.metadata, 1);
    }
    setUri(uri) {
        return new Report(this.id, this.tenantId, this.type, this.parameters, this.generatedAt, uri, this.format, this.metadata, this.version);
    }
    updateMetadata(metadata) {
        return new Report(this.id, this.tenantId, this.type, this.parameters, this.generatedAt, this.uri, this.format, { ...this.metadata, ...metadata }, this.version);
    }
    isExpired(maxAgeHours = 24) {
        const ageMs = Date.now() - this.generatedAt.getTime();
        const maxAgeMs = maxAgeHours * 60 * 60 * 1000;
        return ageMs > maxAgeMs;
    }
    getFileName() {
        const timestamp = this.generatedAt.toISOString().split('T')[0];
        const type = this.type.toLowerCase();
        return `report-${type}-${timestamp}.${this.format}`;
    }
    toJSON() {
        return {
            id: this.id,
            tenantId: this.tenantId,
            type: this.type,
            parameters: this.parameters,
            generatedAt: this.generatedAt.toISOString(),
            uri: this.uri,
            format: this.format,
            metadata: this.metadata,
            version: this.version,
        };
    }
}
exports.Report = Report;
//# sourceMappingURL=report.js.map