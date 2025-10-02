/**
 * ID generation utilities
 */
import type { EntityId } from '../types/common.js';
/**
 * Generate a new UUID v4
 */
export declare function generateId(): EntityId;
/**
 * Generate a prefixed ID for better readability
 */
export declare function generatePrefixedId(prefix: string): EntityId;
/**
 * Validate if a string is a valid UUID
 */
export declare function isValidId(id: string): boolean;
//# sourceMappingURL=id-generator.d.ts.map