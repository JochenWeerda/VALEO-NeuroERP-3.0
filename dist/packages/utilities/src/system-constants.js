/**
 * VALEO NeuroERP 3.0 - System-wide Constants
 *
 * Gemeinsame Konstanten für alle Domains
 * Ergänzt Domain-spezifische Konstanten
 */
// ===== HTTP STATUS CODES =====
export const HTTP_STATUS = {
    // Success
    OK: 200,
    CREATED: 201,
    ACCEPTED: 202,
    NO_CONTENT: 204,
    // Redirection
    MOVED_PERMANENTLY: 301,
    FOUND: 302,
    NOT_MODIFIED: 304,
    // Client Error
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    METHOD_NOT_ALLOWED: 405,
    CONFLICT: 409,
    UNPROCESSABLE_ENTITY: 422,
    TOO_MANY_REQUESTS: 429,
    // Server Error
    INTERNAL_SERVER_ERROR: 500,
    NOT_IMPLEMENTED: 501,
    BAD_GATEWAY: 502,
    SERVICE_UNAVAILABLE: 503,
    GATEWAY_TIMEOUT: 504
};
// ===== COMMON PERCENTAGES =====
export const PERCENTAGES = {
    ZERO: 0,
    TWENTY_FIVE: 25,
    FIFTY: 50,
    SEVENTY_FIVE: 75,
    HUNDRED: 100,
    THOUSAND: 1000,
    // Decimal percentages
    TEN_PERCENT: 0.1,
    TWENTY_PERCENT: 0.2,
    THIRTY_PERCENT: 0.3,
    FORTY_PERCENT: 0.4,
    FIFTY_PERCENT: 0.5,
    SIXTY_PERCENT: 0.6,
    SEVENTY_PERCENT: 0.7,
    EIGHTY_PERCENT: 0.8,
    NINETY_PERCENT: 0.9
};
// ===== TIME CONSTANTS =====
export const TIME = {
    // Base units (milliseconds)
    MILLISECOND: 1,
    MILLISECONDS_PER_SECOND: 1000,
    MILLISECONDS_PER_MINUTE: 60000,
    MILLISECONDS_PER_HOUR: 3600000,
    MILLISECONDS_PER_DAY: 86400000,
    // Base units (seconds)
    SECONDS_PER_MINUTE: 60,
    SECONDS_PER_HOUR: 3600,
    SECONDS_PER_DAY: 86400,
    // Base units (minutes)
    MINUTES_PER_HOUR: 60,
    MINUTES_PER_DAY: 1440,
    // Base units (hours)
    HOURS_PER_DAY: 24,
    HOURS_PER_WEEK: 168,
    HOURS_PER_MONTH: 730, // Average
    HOURS_PER_YEAR: 8760, // Average
    // Common durations
    ONE_MINUTE: 60000,
    TWO_MINUTES: 120000,
    FIVE_MINUTES: 300000,
    TEN_MINUTES: 600000,
    FIFTEEN_MINUTES: 900000,
    THIRTY_MINUTES: 1800000,
    ONE_HOUR: 3600000,
    SIX_HOURS: 21600000,
    TWELVE_HOURS: 43200000,
    ONE_DAY: 86400000,
    ONE_WEEK: 604800000,
    // Hash and encoding
    HASH_NORMALIZATION_FACTOR: 1000000
};
// ===== COLLECTION AND PAGINATION =====
export const COLLECTION = {
    // Page sizes
    DEFAULT_PAGE_SIZE: 20,
    SMALL_PAGE_SIZE: 10,
    LARGE_PAGE_SIZE: 50,
    MAX_PAGE_SIZE: 100,
    MAX_BATCH_SIZE: 1000,
    // Common counts
    ONE: 1,
    TWO: 2,
    THREE: 3,
    FOUR: 4,
    FIVE: 5,
    TEN: 10,
    TWELVE: 12,
    SIXTEEN: 16,
    TWENTY: 20,
    TWENTY_THREE: 23,
    THIRTY: 30,
    THIRTY_SIX: 36,
    FIFTY: 50,
    // Array operations
    FIRST_INDEX: 0,
    SECOND_INDEX: 1
};
// ===== VALIDATION THRESHOLDS =====
export const VALIDATION = {
    // Confidence scores
    MIN_CONFIDENCE: 0.0,
    LOW_CONFIDENCE: 0.3,
    MEDIUM_CONFIDENCE: 0.6,
    HIGH_CONFIDENCE: 0.8,
    MAX_CONFIDENCE: 1.0,
    // Tolerance values
    ZERO_TOLERANCE: 0.0,
    SMALL_TOLERANCE: 0.01,
    MEDIUM_TOLERANCE: 0.05,
    LARGE_TOLERANCE: 0.1,
    // Balance validation
    BALANCE_TOLERANCE: 0.01
};
// ===== HEX VALUES FOR BINARY PROCESSING =====
export const HEX_VALUES = {
    // PDF signatures
    PDF_PERCENT: 0x25, // %
    PDF_P: 0x50, // P
    PDF_D: 0x44, // D
    PDF_F: 0x46, // F
    PDF_HYPHEN: 0x2D, // -
    // Common hex values
    NULL: 0x00,
    SPACE: 0x20,
    ZERO: 0x30,
    NINE: 0x39,
    A_UPPER: 0x41,
    F_UPPER: 0x46,
    Z_UPPER: 0x5A,
    A_LOWER: 0x61,
    F_LOWER: 0x66,
    Z_LOWER: 0x7A
};
// ===== BUSINESS CONSTANTS =====
export const BUSINESS = {
    // Payment terms (days)
    PAYMENT_TERMS: {
        IMMEDIATE: 0,
        NET_15: 15,
        NET_30: 30,
        NET_45: 45,
        NET_60: 60,
        NET_90: 90
    },
    // Currencies
    CURRENCIES: {
        EUR: 'EUR',
        USD: 'USD',
        GBP: 'GBP',
        CHF: 'CHF'
    },
    // Tax rates (German standard)
    TAX_RATES: {
        ZERO: 0.0,
        REDUCED: 0.07, // 7%
        STANDARD: 0.19 // 19%
    },
    // Document statuses
    DOCUMENT_STATUS: {
        DRAFT: 'DRAFT',
        PROCESSING: 'PROCESSING',
        APPROVED: 'APPROVED',
        PAID: 'PAID',
        CANCELLED: 'CANCELLED',
        OVERDUE: 'OVERDUE'
    }
};
// ===== REGEX PATTERNS =====
export const PATTERNS = {
    // Identifiers
    UUID: /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
    EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    PHONE: /^\+?[\d\s\-\(\)]+$/,
    // Financial
    ACCOUNT_NUMBER: /^[0-9]{4,8}$/,
    INVOICE_NUMBER: /^[A-Z0-9\-_]+$/,
    IBAN: /^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$/,
    // Dates
    ISO_DATE: /^\d{4}-\d{2}-\d{2}$/,
    ISO_DATETIME: /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$/,
    // File paths
    SAFE_FILENAME: /^[a-zA-Z0-9\-_\.]+$/,
    WINDOWS_PATH: /^[a-zA-Z]:\\(?:[^\\\/:*?"<>|]+\\)*[^\\\/:*?"<>|]*$/,
    UNIX_PATH: /^\/(?:[^\/]+\/)*[^\/]*$/
};
// ===== ERROR CODES =====
export const ERROR_CODES = {
    // Validation errors
    VALIDATION_ERROR: 'VALIDATION_ERROR',
    REQUIRED_FIELD: 'REQUIRED_FIELD',
    INVALID_FORMAT: 'INVALID_FORMAT',
    OUT_OF_RANGE: 'OUT_OF_RANGE',
    // Business errors
    NOT_FOUND: 'NOT_FOUND',
    ALREADY_EXISTS: 'ALREADY_EXISTS',
    INSUFFICIENT_PERMISSIONS: 'INSUFFICIENT_PERMISSIONS',
    BUSINESS_RULE_VIOLATION: 'BUSINESS_RULE_VIOLATION',
    // System errors
    DATABASE_ERROR: 'DATABASE_ERROR',
    EXTERNAL_SERVICE_ERROR: 'EXTERNAL_SERVICE_ERROR',
    TIMEOUT_ERROR: 'TIMEOUT_ERROR',
    INTERNAL_ERROR: 'INTERNAL_ERROR'
};
// ===== DEFAULT VALUES =====
export const DEFAULTS = {
    // Pagination
    DEFAULT_PAGE: 1,
    DEFAULT_PAGE_SIZE: COLLECTION.DEFAULT_PAGE_SIZE,
    // Timeouts
    DEFAULT_TIMEOUT: TIME.ONE_MINUTE,
    DATABASE_TIMEOUT: TIME.THIRTY_MINUTES,
    EXTERNAL_API_TIMEOUT: TIME.TWO_MINUTES,
    // Encoding
    DEFAULT_ENCODING: 'utf8',
    DEFAULT_CURRENCY: BUSINESS.CURRENCIES.EUR,
    DEFAULT_LANGUAGE: 'de',
    // Business defaults
    DEFAULT_TAX_RATE: BUSINESS.TAX_RATES.STANDARD,
    DEFAULT_PAYMENT_TERMS: BUSINESS.PAYMENT_TERMS.NET_30
};
