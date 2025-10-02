"use strict";
// ===== FINANCE DOMAIN CONSTANTS =====
Object.defineProperty(exports, "__esModule", { value: true });
exports.BUSINESS_RULES = exports.VALIDATION = exports.COLLECTION = exports.HEX_VALUES = exports.TIME = exports.PERCENTAGES = exports.TAX_RATES = exports.HTTP_STATUS = void 0;
/**
 * HTTP Status Codes
 */
exports.HTTP_STATUS = {
    OK: 200,
    CREATED: 201,
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    INTERNAL_SERVER_ERROR: 500
};
/**
 * Tax Rates (German standard rates)
 */
exports.TAX_RATES = {
    ZERO: 0,
    REDUCED: 0.07, // 7% reduced rate
    STANDARD: 0.19, // 19% standard rate
    TOLERANCE: 0.01 // Tolerance for floating point comparisons
};
/**
 * Percentages and Ratios
 */
exports.PERCENTAGES = {
    HUNDRED: 100,
    FIVE: 5,
    EIGHTY_PERCENT: 0.8,
    FIVE_PERCENT: 0.05,
    TEN_PERCENT: 0.1,
    TWENTY_PERCENT: 0.2,
    THIRTY_PERCENT: 0.3
};
/**
 * Time Calculations
 */
exports.TIME = {
    MILLISECONDS_PER_SECOND: 1000,
    SECONDS_PER_MINUTE: 60,
    MINUTES_PER_HOUR: 60,
    HOURS_PER_DAY: 24,
    MILLISECONDS_PER_DAY: 86400000, // 24 * 60 * 60 * 1000
    HASH_NORMALIZATION_FACTOR: 1000000
};
/**
 * Hex Values (for PDF processing, etc.)
 */
exports.HEX_VALUES = {
    PERCENT: 0x25,
    P: 0x50,
    D: 0x44,
    F: 0x46,
    HYPHEN: 0x2D
};
/**
 * Collection Operations
 */
exports.COLLECTION = {
    DEFAULT_PAGE_SIZE: 20,
    MAX_BATCH_SIZE: 100,
    TWO: 2,
    THREE: 3,
    FIVE: 5,
    TEN: 10,
    TWELVE: 12,
    SIXTEEN: 16,
    TWENTY: 20,
    TWENTY_THREE: 23,
    THIRTY_SIX: 36
};
/**
 * Validation Thresholds
 */
exports.VALIDATION = {
    MIN_CONFIDENCE_SCORE: 0.3,
    HIGH_CONFIDENCE_THRESHOLD: 0.8,
    MAX_CONFIDENCE_SCORE: 1.0,
    BALANCE_TOLERANCE: 0.01
};
/**
 * Business Rules
 */
exports.BUSINESS_RULES = {
    MAX_DAYS_TO_PAYMENT: 90,
    MIN_DAYS_TO_PAYMENT: 0,
    DEFAULT_PAYMENT_TERMS_DAYS: 30
};
