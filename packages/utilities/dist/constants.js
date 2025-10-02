"use strict";
// System Constants for VALEO NeuroERP 3.0
Object.defineProperty(exports, "__esModule", { value: true });
exports.TIME_EXTENDED = exports.BUSINESS = exports.COLLECTION = exports.TIME = exports.PERCENTAGES = exports.HTTP_STATUS = void 0;
exports.HTTP_STATUS = {
    OK: 200,
    CREATED: 201,
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    INTERNAL_SERVER_ERROR: 500,
};
exports.PERCENTAGES = {
    TAX_RATE: 19.0,
    DISCOUNT_RATE: 10.0,
    MARGIN_RATE: 15.0,
};
exports.TIME = {
    MILLISECONDS_PER_SECOND: 1000,
    SECONDS_PER_MINUTE: 60,
    MINUTES_PER_HOUR: 60,
    HOURS_PER_DAY: 24,
    DAYS_PER_WEEK: 7,
    DAYS_PER_MONTH: 30,
    DAYS_PER_YEAR: 365,
};
exports.COLLECTION = {
    DEFAULT_PAGE_SIZE: 20,
    MAX_PAGE_SIZE: 100,
    DEFAULT_OFFSET: 0,
};
exports.BUSINESS = {
    DEFAULT_CURRENCY: 'EUR',
    DEFAULT_LANGUAGE: 'de',
    DEFAULT_TIMEZONE: 'Europe/Berlin',
    CURRENCIES: ['EUR', 'USD', 'GBP', 'CHF'],
    PAYMENT_TERMS: {
        NET_30: 30,
        NET_60: 60,
        NET_90: 90,
        CASH_ON_DELIVERY: 0,
    },
};
// Additional time constants
exports.TIME_EXTENDED = {
    ...exports.TIME,
    ONE_MINUTE: exports.TIME.MILLISECONDS_PER_SECOND * exports.TIME.SECONDS_PER_MINUTE,
    TWO_MINUTES: exports.TIME.MILLISECONDS_PER_SECOND * exports.TIME.SECONDS_PER_MINUTE * 2,
    THIRTY_MINUTES: exports.TIME.MILLISECONDS_PER_SECOND * exports.TIME.SECONDS_PER_MINUTE * 30,
    ONE_HOUR: exports.TIME.MILLISECONDS_PER_SECOND * exports.TIME.SECONDS_PER_MINUTE * exports.TIME.MINUTES_PER_HOUR,
};
