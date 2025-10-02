/**
 * Integration ID Value Object
 */
import { z } from 'zod';
import { generatePrefixedId, isValidId } from '@shared/utils/id-generator.js';
const IntegrationIdSchema = z.string().uuid();
export class IntegrationId {
    _value;
    constructor(value) {
        if (!isValidId(value)) {
            throw new Error(`Invalid IntegrationId: ${value}`);
        }
        this._value = value;
    }
    static create() {
        return new IntegrationId(generatePrefixedId('int'));
    }
    static fromString(value) {
        IntegrationIdSchema.parse(value);
        return new IntegrationId(value);
    }
    get value() {
        return this._value;
    }
    equals(other) {
        return this._value === other._value;
    }
    toString() {
        return this._value;
    }
    toJSON() {
        return this._value;
    }
}
//# sourceMappingURL=integration-id.js.map