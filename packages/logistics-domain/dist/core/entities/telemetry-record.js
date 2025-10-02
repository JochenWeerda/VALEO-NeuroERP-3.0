"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TelemetryRecord = void 0;
const nanoid_1 = require("nanoid");
class TelemetryRecord {
    constructor(props) {
        this.telemetryId = props.telemetryId ?? `TEL-${(0, nanoid_1.nanoid)(12)}`;
        this.tenantId = props.tenantId;
        this.vehicleId = props.vehicleId;
        this.recordedAt = props.recordedAt;
        this.lat = props.lat;
        this.lon = props.lon;
        this.speedKph = props.speedKph;
        this.temperatureC = props.temperatureC;
        this.fuelLevelPercent = props.fuelLevelPercent;
        this.meta = props.meta;
        if (props.lat < -90 || props.lat > 90 || props.lon < -180 || props.lon > 180) {
            throw new Error('Telemetry coordinates out of range');
        }
    }
    static create(props) {
        return new TelemetryRecord(props);
    }
}
exports.TelemetryRecord = TelemetryRecord;
//# sourceMappingURL=telemetry-record.js.map