/**
 * Sync Job ID Value Object
 */
import { z } from 'zod';
import { generatePrefixedId, isValidId } from '@shared/utils/id-generator.js';
const SyncJobIdSchema = z.string().uuid();
export class SyncJobId {
    _value;
    constructor(value) {
        if (!isValidId(value)) {
            throw new Error(`Invalid SyncJobId: ${value}`);
        }
        this._value = value;
    }
    static create() {
        return new SyncJobId(generatePrefixedId('sj'));
    }
    static fromString(value) {
        SyncJobIdSchema.parse(value);
        return new SyncJobId(value);
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
//# sourceMappingURL=sync-job-id.js.map