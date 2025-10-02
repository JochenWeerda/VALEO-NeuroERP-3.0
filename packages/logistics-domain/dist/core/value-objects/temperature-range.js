"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TemperatureRange = void 0;
class TemperatureRange {
    constructor(props) {
        this.props = props;
    }
    static create(props) {
        if (props.minC > props.maxC) {
            throw new Error('Invalid temperature range: min cannot exceed max');
        }
        return new TemperatureRange({ ...props });
    }
    contains(valueC) {
        return valueC >= this.props.minC && valueC <= this.props.maxC;
    }
    toJSON() {
        return { ...this.props };
    }
}
exports.TemperatureRange = TemperatureRange;
//# sourceMappingURL=temperature-range.js.map