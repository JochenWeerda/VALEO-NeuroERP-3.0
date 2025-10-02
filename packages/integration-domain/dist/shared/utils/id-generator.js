/**
 * ID generation utilities
 */
import { v4 as uuidv4 } from 'uuid';
/**
 * Generate a new UUID v4
 */
export function generateId() {
    return uuidv4();
}
/**
 * Generate a prefixed ID for better readability
 */
export function generatePrefixedId(prefix) {
    return `${prefix}_${uuidv4().replace(/-/g, '')}`;
}
/**
 * Validate if a string is a valid UUID
 */
export function isValidId(id) {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return uuidRegex.test(id);
}
//# sourceMappingURL=id-generator.js.map