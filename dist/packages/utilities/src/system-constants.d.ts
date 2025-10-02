/**
 * VALEO NeuroERP 3.0 - System-wide Constants
 *
 * Gemeinsame Konstanten für alle Domains
 * Ergänzt Domain-spezifische Konstanten
 */
export declare const HTTP_STATUS: {
    readonly OK: 200;
    readonly CREATED: 201;
    readonly ACCEPTED: 202;
    readonly NO_CONTENT: 204;
    readonly MOVED_PERMANENTLY: 301;
    readonly FOUND: 302;
    readonly NOT_MODIFIED: 304;
    readonly BAD_REQUEST: 400;
    readonly UNAUTHORIZED: 401;
    readonly FORBIDDEN: 403;
    readonly NOT_FOUND: 404;
    readonly METHOD_NOT_ALLOWED: 405;
    readonly CONFLICT: 409;
    readonly UNPROCESSABLE_ENTITY: 422;
    readonly TOO_MANY_REQUESTS: 429;
    readonly INTERNAL_SERVER_ERROR: 500;
    readonly NOT_IMPLEMENTED: 501;
    readonly BAD_GATEWAY: 502;
    readonly SERVICE_UNAVAILABLE: 503;
    readonly GATEWAY_TIMEOUT: 504;
};
export declare const PERCENTAGES: {
    readonly ZERO: 0;
    readonly TWENTY_FIVE: 25;
    readonly FIFTY: 50;
    readonly SEVENTY_FIVE: 75;
    readonly HUNDRED: 100;
    readonly THOUSAND: 1000;
    readonly TEN_PERCENT: 0.1;
    readonly TWENTY_PERCENT: 0.2;
    readonly THIRTY_PERCENT: 0.3;
    readonly FORTY_PERCENT: 0.4;
    readonly FIFTY_PERCENT: 0.5;
    readonly SIXTY_PERCENT: 0.6;
    readonly SEVENTY_PERCENT: 0.7;
    readonly EIGHTY_PERCENT: 0.8;
    readonly NINETY_PERCENT: 0.9;
};
export declare const TIME: {
    readonly MILLISECOND: 1;
    readonly MILLISECONDS_PER_SECOND: 1000;
    readonly MILLISECONDS_PER_MINUTE: 60000;
    readonly MILLISECONDS_PER_HOUR: 3600000;
    readonly MILLISECONDS_PER_DAY: 86400000;
    readonly SECONDS_PER_MINUTE: 60;
    readonly SECONDS_PER_HOUR: 3600;
    readonly SECONDS_PER_DAY: 86400;
    readonly MINUTES_PER_HOUR: 60;
    readonly MINUTES_PER_DAY: 1440;
    readonly HOURS_PER_DAY: 24;
    readonly HOURS_PER_WEEK: 168;
    readonly HOURS_PER_MONTH: 730;
    readonly HOURS_PER_YEAR: 8760;
    readonly ONE_MINUTE: 60000;
    readonly TWO_MINUTES: 120000;
    readonly FIVE_MINUTES: 300000;
    readonly TEN_MINUTES: 600000;
    readonly FIFTEEN_MINUTES: 900000;
    readonly THIRTY_MINUTES: 1800000;
    readonly ONE_HOUR: 3600000;
    readonly SIX_HOURS: 21600000;
    readonly TWELVE_HOURS: 43200000;
    readonly ONE_DAY: 86400000;
    readonly ONE_WEEK: 604800000;
    readonly HASH_NORMALIZATION_FACTOR: 1000000;
};
export declare const COLLECTION: {
    readonly DEFAULT_PAGE_SIZE: 20;
    readonly SMALL_PAGE_SIZE: 10;
    readonly LARGE_PAGE_SIZE: 50;
    readonly MAX_PAGE_SIZE: 100;
    readonly MAX_BATCH_SIZE: 1000;
    readonly ONE: 1;
    readonly TWO: 2;
    readonly THREE: 3;
    readonly FOUR: 4;
    readonly FIVE: 5;
    readonly TEN: 10;
    readonly TWELVE: 12;
    readonly SIXTEEN: 16;
    readonly TWENTY: 20;
    readonly TWENTY_THREE: 23;
    readonly THIRTY: 30;
    readonly THIRTY_SIX: 36;
    readonly FIFTY: 50;
    readonly FIRST_INDEX: 0;
    readonly SECOND_INDEX: 1;
};
export declare const VALIDATION: {
    readonly MIN_CONFIDENCE: 0;
    readonly LOW_CONFIDENCE: 0.3;
    readonly MEDIUM_CONFIDENCE: 0.6;
    readonly HIGH_CONFIDENCE: 0.8;
    readonly MAX_CONFIDENCE: 1;
    readonly ZERO_TOLERANCE: 0;
    readonly SMALL_TOLERANCE: 0.01;
    readonly MEDIUM_TOLERANCE: 0.05;
    readonly LARGE_TOLERANCE: 0.1;
    readonly BALANCE_TOLERANCE: 0.01;
};
export declare const HEX_VALUES: {
    readonly PDF_PERCENT: 37;
    readonly PDF_P: 80;
    readonly PDF_D: 68;
    readonly PDF_F: 70;
    readonly PDF_HYPHEN: 45;
    readonly NULL: 0;
    readonly SPACE: 32;
    readonly ZERO: 48;
    readonly NINE: 57;
    readonly A_UPPER: 65;
    readonly F_UPPER: 70;
    readonly Z_UPPER: 90;
    readonly A_LOWER: 97;
    readonly F_LOWER: 102;
    readonly Z_LOWER: 122;
};
export declare const BUSINESS: {
    readonly PAYMENT_TERMS: {
        readonly IMMEDIATE: 0;
        readonly NET_15: 15;
        readonly NET_30: 30;
        readonly NET_45: 45;
        readonly NET_60: 60;
        readonly NET_90: 90;
    };
    readonly CURRENCIES: {
        readonly EUR: "EUR";
        readonly USD: "USD";
        readonly GBP: "GBP";
        readonly CHF: "CHF";
    };
    readonly TAX_RATES: {
        readonly ZERO: 0;
        readonly REDUCED: 0.07;
        readonly STANDARD: 0.19;
    };
    readonly DOCUMENT_STATUS: {
        readonly DRAFT: "DRAFT";
        readonly PROCESSING: "PROCESSING";
        readonly APPROVED: "APPROVED";
        readonly PAID: "PAID";
        readonly CANCELLED: "CANCELLED";
        readonly OVERDUE: "OVERDUE";
    };
};
export declare const PATTERNS: {
    readonly UUID: RegExp;
    readonly EMAIL: RegExp;
    readonly PHONE: RegExp;
    readonly ACCOUNT_NUMBER: RegExp;
    readonly INVOICE_NUMBER: RegExp;
    readonly IBAN: RegExp;
    readonly ISO_DATE: RegExp;
    readonly ISO_DATETIME: RegExp;
    readonly SAFE_FILENAME: RegExp;
    readonly WINDOWS_PATH: RegExp;
    readonly UNIX_PATH: RegExp;
};
export declare const ERROR_CODES: {
    readonly VALIDATION_ERROR: "VALIDATION_ERROR";
    readonly REQUIRED_FIELD: "REQUIRED_FIELD";
    readonly INVALID_FORMAT: "INVALID_FORMAT";
    readonly OUT_OF_RANGE: "OUT_OF_RANGE";
    readonly NOT_FOUND: "NOT_FOUND";
    readonly ALREADY_EXISTS: "ALREADY_EXISTS";
    readonly INSUFFICIENT_PERMISSIONS: "INSUFFICIENT_PERMISSIONS";
    readonly BUSINESS_RULE_VIOLATION: "BUSINESS_RULE_VIOLATION";
    readonly DATABASE_ERROR: "DATABASE_ERROR";
    readonly EXTERNAL_SERVICE_ERROR: "EXTERNAL_SERVICE_ERROR";
    readonly TIMEOUT_ERROR: "TIMEOUT_ERROR";
    readonly INTERNAL_ERROR: "INTERNAL_ERROR";
};
export declare const DEFAULTS: {
    readonly DEFAULT_PAGE: 1;
    readonly DEFAULT_PAGE_SIZE: 20;
    readonly DEFAULT_TIMEOUT: 60000;
    readonly DATABASE_TIMEOUT: 1800000;
    readonly EXTERNAL_API_TIMEOUT: 120000;
    readonly DEFAULT_ENCODING: "utf8";
    readonly DEFAULT_CURRENCY: "EUR";
    readonly DEFAULT_LANGUAGE: "de";
    readonly DEFAULT_TAX_RATE: 0.19;
    readonly DEFAULT_PAYMENT_TERMS: 30;
};
//***REMOVED*** sourceMappingURL=system-constants.d.ts.map