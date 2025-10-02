"use strict";
/**
 * Branded type helpers for CRM Domain
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.createId = createId;
/**
 * Utility used by repositories/services to generate strongly typed identifiers.
 */
function createId(brand) {
    const value = typeof globalThis.crypto?.randomUUID === 'function'
        ? globalThis.crypto.randomUUID()
        : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    return value;
}
//# sourceMappingURL=branded-types.js.map