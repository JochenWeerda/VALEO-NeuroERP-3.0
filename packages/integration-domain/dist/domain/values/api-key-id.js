/**
 * API Key ID Value Object
 */
import { z } from 'zod';
import { generatePrefixedId, isValidId } from '@shared/utils/id-generator.js';
const ApiKeyIdSchema = z.string().uuid();
export class ApiKeyId {
    _value;
    constructor(value) {
        if (!isValidId(value)) {
            throw new Error(`Invalid ApiKeyId: ${value}`);
        }
        this._value = value;
    }
    static create() {
        return new ApiKeyId(generatePrefixedId('ak'));
    }
    static fromString(value) {
        ApiKeyIdSchema.parse(value);
        return new ApiKeyId(value);
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
//# sourceMappingURL=api-key-id.js.map