"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TimeWindow = void 0;
class TimeWindow {
    props;
    constructor(props) {
        this.props = props;
    }
    static create(props) {
        if (props.from >= props.to) {
            throw new Error('Invalid time window: from must be before to');
        }
        return new TimeWindow({ ...props });
    }
    get from() {
        return new Date(this.props.from);
    }
    get to() {
        return new Date(this.props.to);
    }
    durationMinutes() {
        return Math.round((this.props.to.getTime() - this.props.from.getTime()) / 60000);
    }
    toJSON() {
        return {
            from: this.props.from.toISOString(),
            to: this.props.to.toISOString(),
        };
    }
}
exports.TimeWindow = TimeWindow;
