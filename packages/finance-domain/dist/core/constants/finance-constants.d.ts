/**
 * HTTP Status Codes
 */
export declare const HTTP_STATUS: {
    readonly OK: 200;
    readonly CREATED: 201;
    readonly BAD_REQUEST: 400;
    readonly UNAUTHORIZED: 401;
    readonly FORBIDDEN: 403;
    readonly NOT_FOUND: 404;
    readonly INTERNAL_SERVER_ERROR: 500;
};
/**
 * Tax Rates (German standard rates)
 */
export declare const TAX_RATES: {
    readonly ZERO: 0;
    readonly REDUCED: 0.07;
    readonly STANDARD: 0.19;
    readonly TOLERANCE: 0.01;
};
/**
 * Percentages and Ratios
 */
export declare const PERCENTAGES: {
    readonly HUNDRED: 100;
    readonly FIVE: 5;
    readonly EIGHTY_PERCENT: 0.8;
    readonly FIVE_PERCENT: 0.05;
    readonly TEN_PERCENT: 0.1;
    readonly TWENTY_PERCENT: 0.2;
    readonly THIRTY_PERCENT: 0.3;
};
/**
 * Time Calculations
 */
export declare const TIME: {
    readonly MILLISECONDS_PER_SECOND: 1000;
    readonly SECONDS_PER_MINUTE: 60;
    readonly MINUTES_PER_HOUR: 60;
    readonly HOURS_PER_DAY: 24;
    readonly MILLISECONDS_PER_DAY: 86400000;
    readonly HASH_NORMALIZATION_FACTOR: 1000000;
};
/**
 * Hex Values (for PDF processing, etc.)
 */
export declare const HEX_VALUES: {
    readonly PERCENT: 37;
    readonly P: 80;
    readonly D: 68;
    readonly F: 70;
    readonly HYPHEN: 45;
};
/**
 * Collection Operations
 */
export declare const COLLECTION: {
    readonly DEFAULT_PAGE_SIZE: 20;
    readonly MAX_BATCH_SIZE: 100;
    readonly TWO: 2;
    readonly THREE: 3;
    readonly FIVE: 5;
    readonly TEN: 10;
    readonly TWELVE: 12;
    readonly SIXTEEN: 16;
    readonly TWENTY: 20;
    readonly TWENTY_THREE: 23;
    readonly THIRTY_SIX: 36;
};
/**
 * Validation Thresholds
 */
export declare const VALIDATION: {
    readonly MIN_CONFIDENCE_SCORE: 0.3;
    readonly HIGH_CONFIDENCE_THRESHOLD: 0.8;
    readonly MAX_CONFIDENCE_SCORE: 1;
    readonly BALANCE_TOLERANCE: 0.01;
};
/**
 * Business Rules
 */
export declare const BUSINESS_RULES: {
    readonly MAX_DAYS_TO_PAYMENT: 90;
    readonly MIN_DAYS_TO_PAYMENT: 0;
    readonly DEFAULT_PAYMENT_TERMS_DAYS: 30;
};
//# sourceMappingURL=finance-constants.d.ts.map