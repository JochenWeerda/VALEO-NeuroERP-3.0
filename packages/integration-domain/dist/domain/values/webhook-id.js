/**
 * Webhook ID Value Object
 */
import { z } from 'zod';
import { generatePrefixedId, isValidId } from '@shared/utils/id-generator.js';
const WebhookIdSchema = z.string().uuid();
export class WebhookId {
    _value;
    constructor(value) {
        if (!isValidId(value)) {
            throw new Error(`Invalid WebhookId: ${value}`);
        }
        this._value = value;
    }
    static create() {
        return new WebhookId(generatePrefixedId('wh'));
    }
    static fromString(value) {
        WebhookIdSchema.parse(value);
        return new WebhookId(value);
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
//# sourceMappingURL=webhook-id.js.map