/**
 * VALEO NeuroERP 3.0 - ERP Domain Constants
 *
 * Domain-spezifische Konstanten für Enterprise Resource Planning
 * Ergänzt system-weite Konstanten
 */
export declare const INVENTORY: {
    readonly DEFAULT_REORDER_POINT: 10;
    readonly CRITICAL_STOCK_LEVEL: 5;
    readonly MAX_STOCK_LEVEL: 10000;
    readonly MIN_STOCK_LEVEL: 0;
    readonly DEFAULT_LEAD_TIME: 7;
    readonly URGENT_LEAD_TIME: 1;
    readonly STANDARD_LEAD_TIME: 14;
    readonly MOVEMENT_TYPES: {
        readonly RECEIPT: "RECEIPT";
        readonly ISSUE: "ISSUE";
        readonly TRANSFER: "TRANSFER";
        readonly ADJUSTMENT: "ADJUSTMENT";
        readonly RETURN: "RETURN";
    };
    readonly STOCK_STATUS: {
        readonly AVAILABLE: "AVAILABLE";
        readonly RESERVED: "RESERVED";
        readonly DAMAGED: "DAMAGED";
        readonly EXPIRED: "EXPIRED";
        readonly OUT_OF_STOCK: "OUT_OF_STOCK";
    };
};
export declare const ORDERS: {
    readonly ORDER_STATUS: {
        readonly DRAFT: "DRAFT";
        readonly PENDING: "PENDING";
        readonly CONFIRMED: "CONFIRMED";
        readonly PROCESSING: "PROCESSING";
        readonly SHIPPED: "SHIPPED";
        readonly DELIVERED: "DELIVERED";
        readonly CANCELLED: "CANCELLED";
        readonly RETURNED: "RETURNED";
    };
    readonly ORDER_TYPES: {
        readonly SALES_ORDER: "SALES_ORDER";
        readonly PURCHASE_ORDER: "PURCHASE_ORDER";
        readonly TRANSFER_ORDER: "TRANSFER_ORDER";
        readonly RETURN_ORDER: "RETURN_ORDER";
    };
    readonly PRIORITY: {
        readonly LOW: 1;
        readonly NORMAL: 2;
        readonly HIGH: 3;
        readonly URGENT: 4;
    };
    readonly PAYMENT_TERMS: {
        readonly NET_7: 7;
        readonly NET_14: 14;
        readonly END_OF_MONTH: -1;
        readonly CASH_ON_DELIVERY: 0;
        readonly NET_30: 30;
        readonly NET_60: 60;
        readonly NET_90: 90;
    };
};
export declare const PRODUCTS: {
    readonly PRODUCT_STATUS: {
        readonly ACTIVE: "ACTIVE";
        readonly INACTIVE: "INACTIVE";
        readonly DISCONTINUED: "DISCONTINUED";
        readonly PENDING: "PENDING";
        readonly ARCHIVED: "ARCHIVED";
    };
    readonly PRODUCT_CATEGORIES: {
        readonly RAW_MATERIALS: "RAW_MATERIALS";
        readonly FINISHED_GOODS: "FINISHED_GOODS";
        readonly SEMI_FINISHED: "SEMI_FINISHED";
        readonly PACKAGING: "PACKAGING";
        readonly SERVICES: "SERVICES";
        readonly DIGITAL: "DIGITAL";
    };
    readonly UNITS_OF_MEASURE: {
        readonly PIECE: "PC";
        readonly KILOGRAM: "KG";
        readonly LITER: "L";
        readonly METER: "M";
        readonly SQUARE_METER: "M2";
        readonly CUBIC_METER: "M3";
        readonly HOUR: "H";
        readonly DAY: "D";
        readonly MONTH: "MON";
        readonly YEAR: "Y";
    };
    readonly WEIGHT_CLASSES: {
        readonly LIGHT: "LIGHT";
        readonly MEDIUM: "MEDIUM";
        readonly HEAVY: "HEAVY";
        readonly VERY_HEAVY: "VERY_HEAVY";
    };
};
export declare const WAREHOUSE: {
    readonly LOCATION_TYPES: {
        readonly PICKING: "PICKING";
        readonly BULK: "BULK";
        readonly QUARANTINE: "QUARANTINE";
        readonly RETURNS: "RETURNS";
        readonly STAGING: "STAGING";
    };
    readonly ZONE_TYPES: {
        readonly A: "A";
        readonly B: "B";
        readonly C: "C";
    };
    readonly STORAGE_CONDITIONS: {
        readonly AMBIENT: "AMBIENT";
        readonly REFRIGERATED: "REFRIGERATED";
        readonly FROZEN: "FROZEN";
        readonly CONTROLLED_SUBSTANCE: "CONTROLLED_SUBSTANCE";
        readonly HAZARDOUS: "HAZARDOUS";
    };
};
export declare const PRODUCTION: {
    readonly PRODUCTION_STATUS: {
        readonly PLANNED: "PLANNED";
        readonly SCHEDULED: "SCHEDULED";
        readonly IN_PROGRESS: "IN_PROGRESS";
        readonly COMPLETED: "COMPLETED";
        readonly CANCELLED: "CANCELLED";
        readonly ON_HOLD: "ON_HOLD";
    };
    readonly WORK_ORDER_TYPES: {
        readonly PRODUCTION: "PRODUCTION";
        readonly MAINTENANCE: "MAINTENANCE";
        readonly QUALITY_CHECK: "QUALITY_CHECK";
        readonly SETUP: "SETUP";
        readonly CLEANUP: "CLEANUP";
    };
    readonly BATCH_SIZES: {
        readonly SMALL: 10;
        readonly MEDIUM: 50;
        readonly LARGE: 200;
        readonly EXTRA_LARGE: 1000;
    };
};
export declare const QUALITY: {
    readonly QUALITY_STATUS: {
        readonly PENDING: "PENDING";
        readonly PASSED: "PASSED";
        readonly FAILED: "FAILED";
        readonly UNDER_REVIEW: "UNDER_REVIEW";
        readonly CONDITIONAL_PASS: "CONDITIONAL_PASS";
    };
    readonly INSPECTION_TYPES: {
        readonly INCOMING: "INCOMING";
        readonly IN_PROCESS: "IN_PROCESS";
        readonly FINAL: "FINAL";
        readonly SPOT_CHECK: "SPOT_CHECK";
    };
    readonly QUALITY_LEVELS: {
        readonly EXCELLENT: 5;
        readonly GOOD: 4;
        readonly SATISFACTORY: 3;
        readonly POOR: 2;
        readonly UNACCEPTABLE: 1;
    };
};
export declare const ERP_FINANCE: {
    readonly COST_CENTERS: {
        readonly PRODUCTION: "CC-100";
        readonly SALES: "CC-200";
        readonly MARKETING: "CC-300";
        readonly ADMINISTRATION: "CC-400";
        readonly RESEARCH: "CC-500";
    };
    readonly GL_ACCOUNTS: {
        readonly INVENTORY: "1150";
        readonly COGS: "5000";
        readonly SALES_REVENUE: "4000";
        readonly ACCOUNTS_RECEIVABLE: "1100";
        readonly ACCOUNTS_PAYABLE: "2000";
    };
    readonly BUDGET_CATEGORIES: {
        readonly OPERATING: "OPERATING";
        readonly CAPITAL: "CAPITAL";
        readonly MARKETING: "MARKETING";
        readonly RESEARCH: "RESEARCH";
    };
};
export declare const REPORTING: {
    readonly REPORT_TYPES: {
        readonly INVENTORY_VALUATION: "INVENTORY_VALUATION";
        readonly SALES_ANALYSIS: "SALES_ANALYSIS";
        readonly PURCHASING_ANALYSIS: "PURCHASING_ANALYSIS";
        readonly PRODUCTION_EFFICIENCY: "PRODUCTION_EFFICIENCY";
        readonly FINANCIAL_SUMMARY: "FINANCIAL_SUMMARY";
    };
    readonly TIME_PERIODS: {
        readonly DAILY: "DAILY";
        readonly WEEKLY: "WEEKLY";
        readonly MONTHLY: "MONTHLY";
        readonly QUARTERLY: "QUARTERLY";
        readonly YEARLY: "YEARLY";
        readonly CUSTOM: "CUSTOM";
    };
    readonly AGGREGATION: {
        readonly DETAIL: "DETAIL";
        readonly SUMMARY: "SUMMARY";
        readonly EXECUTIVE: "EXECUTIVE";
    };
};
export declare const ERP_VALIDATION: {
    readonly INVENTORY_THRESHOLDS: {
        readonly MIN_QUANTITY: 0;
        readonly MAX_QUANTITY: 999999;
        readonly MIN_PRICE: 0;
        readonly MAX_PRICE: 999999.99;
    };
    readonly ORDER_THRESHOLDS: {
        readonly MIN_LINE_VALUE: 0.01;
        readonly MAX_LINE_VALUE: 999999.99;
        readonly MIN_ORDER_VALUE: 0.01;
        readonly MAX_ORDER_VALUE: 9999999.99;
    };
    readonly PERFORMANCE_THRESHOLDS: {
        readonly ORDER_PROCESSING_TIME: number;
        readonly INVENTORY_COUNT_TIME: number;
        readonly REPORT_GENERATION_TIME: number;
    };
};
export declare const ERP_DEFAULTS: {
    readonly DEFAULT_WAREHOUSE: "WH-001";
    readonly DEFAULT_LOCATION: "A-01-01";
    readonly DEFAULT_COST_CENTER: "CC-100";
    readonly DEFAULT_LEAD_TIME: 7;
    readonly DEFAULT_SAFETY_STOCK: 5;
    readonly DEFAULT_ORDER_QUANTITY: 1;
    readonly DEFAULT_PAGE_SIZE: 20;
    readonly DEFAULT_TIMEOUT: number;
    readonly DEFAULT_CURRENCY: "EUR";
};
export declare const ERP_ERROR_MESSAGES: {
    readonly INVENTORY_NOT_FOUND: "Inventory item not found";
    readonly INSUFFICIENT_STOCK: "Insufficient stock available";
    readonly INVALID_LOCATION: "Invalid storage location";
    readonly ORDER_NOT_FOUND: "Order not found";
    readonly INVALID_ORDER_STATUS: "Invalid order status transition";
    readonly ORDER_ALREADY_PROCESSED: "Order has already been processed";
    readonly PRODUCT_NOT_FOUND: "Product not found";
    readonly DUPLICATE_PRODUCT_CODE: "Product code already exists";
    readonly INVALID_PRODUCT_CATEGORY: "Invalid product category";
    readonly VALIDATION_ERROR: "Validation failed";
    readonly PERMISSION_DENIED: "Insufficient permissions";
    readonly SYSTEM_ERROR: "System error occurred";
};
//# sourceMappingURL=erp-constants.d.ts.map