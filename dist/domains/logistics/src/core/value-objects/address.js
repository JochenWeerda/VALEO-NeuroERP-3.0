"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Address = void 0;
class Address {
    props;
    constructor(props) {
        this.props = props;
    }
    static create(props) {
        if (!props.street || !props.city || !props.postalCode || !props.country) {
            throw new Error('Invalid address: street, city, postalCode, and country are required');
        }
        if (props.coordinates) {
            const { lat, lon } = props.coordinates;
            if (Number.isNaN(lat) || Number.isNaN(lon)) {
                throw new Error('Invalid address coordinates: lat/lon must be numeric');
            }
            if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
                throw new Error('Invalid address coordinates: values out of range');
            }
        }
        return new Address({ ...props });
    }
    toJSON() {
        return { ...this.props };
    }
}
exports.Address = Address;
