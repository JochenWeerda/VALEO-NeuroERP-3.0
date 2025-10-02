"use strict";
/**
 * VALEO NeuroERP 3.0 - ERP Domain Constants
 *
 * Domain-spezifische Konstanten für Enterprise Resource Planning
 * Ergänzt system-weite Konstanten
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ERP_ERROR_MESSAGES = exports.ERP_DEFAULTS = exports.ERP_VALIDATION = exports.REPORTING = exports.ERP_FINANCE = exports.QUALITY = exports.PRODUCTION = exports.WAREHOUSE = exports.PRODUCTS = exports.ORDERS = exports.INVENTORY = void 0;
const utilities_1 = require("@valero-neuroerp/utilities");
// ===== INVENTORY MANAGEMENT =====
exports.INVENTORY = {
    // Stock levels
    DEFAULT_REORDER_POINT: 10,
    CRITICAL_STOCK_LEVEL: 5,
    MAX_STOCK_LEVEL: 10000,
    MIN_STOCK_LEVEL: 0,
    // Lead times (days)
    DEFAULT_LEAD_TIME: 7,
    URGENT_LEAD_TIME: 1,
    STANDARD_LEAD_TIME: 14,
    // Stock movements
    MOVEMENT_TYPES: {
        RECEIPT: 'RECEIPT',
        ISSUE: 'ISSUE',
        TRANSFER: 'TRANSFER',
        ADJUSTMENT: 'ADJUSTMENT',
        RETURN: 'RETURN'
    },
    // Stock status
    STOCK_STATUS: {
        AVAILABLE: 'AVAILABLE',
        RESERVED: 'RESERVED',
        DAMAGED: 'DAMAGED',
        EXPIRED: 'EXPIRED',
        OUT_OF_STOCK: 'OUT_OF_STOCK'
    }
};
// ===== ORDER MANAGEMENT =====
exports.ORDERS = {
    // Order status
    ORDER_STATUS: {
        DRAFT: 'DRAFT',
        PENDING: 'PENDING',
        CONFIRMED: 'CONFIRMED',
        PROCESSING: 'PROCESSING',
        SHIPPED: 'SHIPPED',
        DELIVERED: 'DELIVERED',
        CANCELLED: 'CANCELLED',
        RETURNED: 'RETURNED'
    },
    // Order types
    ORDER_TYPES: {
        SALES_ORDER: 'SALES_ORDER',
        PURCHASE_ORDER: 'PURCHASE_ORDER',
        TRANSFER_ORDER: 'TRANSFER_ORDER',
        RETURN_ORDER: 'RETURN_ORDER'
    },
    // Priority levels
    PRIORITY: {
        LOW: 1,
        NORMAL: 2,
        HIGH: 3,
        URGENT: 4
    },
    // Payment terms (extends system defaults)
    PAYMENT_TERMS: {
        ...utilities_1.BUSINESS.PAYMENT_TERMS,
        NET_7: 7,
        NET_14: 14,
        END_OF_MONTH: -1, // Special value
        CASH_ON_DELIVERY: 0
    }
};
// ===== PRODUCT MANAGEMENT =====
exports.PRODUCTS = {
    // Product status
    PRODUCT_STATUS: {
        ACTIVE: 'ACTIVE',
        INACTIVE: 'INACTIVE',
        DISCONTINUED: 'DISCONTINUED',
        PENDING: 'PENDING',
        ARCHIVED: 'ARCHIVED'
    },
    // Product categories
    PRODUCT_CATEGORIES: {
        RAW_MATERIALS: 'RAW_MATERIALS',
        FINISHED_GOODS: 'FINISHED_GOODS',
        SEMI_FINISHED: 'SEMI_FINISHED',
        PACKAGING: 'PACKAGING',
        SERVICES: 'SERVICES',
        DIGITAL: 'DIGITAL'
    },
    // Measurement units
    UNITS_OF_MEASURE: {
        PIECE: 'PC',
        KILOGRAM: 'KG',
        LITER: 'L',
        METER: 'M',
        SQUARE_METER: 'M2',
        CUBIC_METER: 'M3',
        HOUR: 'H',
        DAY: 'D',
        MONTH: 'MON',
        YEAR: 'Y'
    },
    // Weight classifications
    WEIGHT_CLASSES: {
        LIGHT: 'LIGHT', // < 1kg
        MEDIUM: 'MEDIUM', // 1-10kg
        HEAVY: 'HEAVY', // 10-100kg
        VERY_HEAVY: 'VERY_HEAVY' // > 100kg
    }
};
// ===== WAREHOUSE MANAGEMENT =====
exports.WAREHOUSE = {
    // Location types
    LOCATION_TYPES: {
        PICKING: 'PICKING',
        BULK: 'BULK',
        QUARANTINE: 'QUARANTINE',
        RETURNS: 'RETURNS',
        STAGING: 'STAGING'
    },
    // Zone classifications
    ZONE_TYPES: {
        A: 'A', // High value, fast moving
        B: 'B', // Medium value, medium movement
        C: 'C' // Low value, slow moving
    },
    // Storage conditions
    STORAGE_CONDITIONS: {
        AMBIENT: 'AMBIENT',
        REFRIGERATED: 'REFRIGERATED',
        FROZEN: 'FROZEN',
        CONTROLLED_SUBSTANCE: 'CONTROLLED_SUBSTANCE',
        HAZARDOUS: 'HAZARDOUS'
    }
};
// ===== PRODUCTION =====
exports.PRODUCTION = {
    // Production status
    PRODUCTION_STATUS: {
        PLANNED: 'PLANNED',
        SCHEDULED: 'SCHEDULED',
        IN_PROGRESS: 'IN_PROGRESS',
        COMPLETED: 'COMPLETED',
        CANCELLED: 'CANCELLED',
        ON_HOLD: 'ON_HOLD'
    },
    // Work order types
    WORK_ORDER_TYPES: {
        PRODUCTION: 'PRODUCTION',
        MAINTENANCE: 'MAINTENANCE',
        QUALITY_CHECK: 'QUALITY_CHECK',
        SETUP: 'SETUP',
        CLEANUP: 'CLEANUP'
    },
    // Batch sizes
    BATCH_SIZES: {
        SMALL: 10,
        MEDIUM: 50,
        LARGE: 200,
        EXTRA_LARGE: 1000
    }
};
// ===== QUALITY CONTROL =====
exports.QUALITY = {
    // Quality status
    QUALITY_STATUS: {
        PENDING: 'PENDING',
        PASSED: 'PASSED',
        FAILED: 'FAILED',
        UNDER_REVIEW: 'UNDER_REVIEW',
        CONDITIONAL_PASS: 'CONDITIONAL_PASS'
    },
    // Inspection types
    INSPECTION_TYPES: {
        INCOMING: 'INCOMING',
        IN_PROCESS: 'IN_PROCESS',
        FINAL: 'FINAL',
        SPOT_CHECK: 'SPOT_CHECK'
    },
    // Quality levels
    QUALITY_LEVELS: {
        EXCELLENT: 5,
        GOOD: 4,
        SATISFACTORY: 3,
        POOR: 2,
        UNACCEPTABLE: 1
    }
};
// ===== FINANCE INTEGRATION (ERP-spezifisch) =====
exports.ERP_FINANCE = {
    // Cost centers
    COST_CENTERS: {
        PRODUCTION: 'CC-100',
        SALES: 'CC-200',
        MARKETING: 'CC-300',
        ADMINISTRATION: 'CC-400',
        RESEARCH: 'CC-500'
    },
    // GL Accounts (examples)
    GL_ACCOUNTS: {
        INVENTORY: '1150',
        COGS: '5000',
        SALES_REVENUE: '4000',
        ACCOUNTS_RECEIVABLE: '1100',
        ACCOUNTS_PAYABLE: '2000'
    },
    // Budget categories
    BUDGET_CATEGORIES: {
        OPERATING: 'OPERATING',
        CAPITAL: 'CAPITAL',
        MARKETING: 'MARKETING',
        RESEARCH: 'RESEARCH'
    }
};
// ===== REPORTING =====
exports.REPORTING = {
    // Report types
    REPORT_TYPES: {
        INVENTORY_VALUATION: 'INVENTORY_VALUATION',
        SALES_ANALYSIS: 'SALES_ANALYSIS',
        PURCHASING_ANALYSIS: 'PURCHASING_ANALYSIS',
        PRODUCTION_EFFICIENCY: 'PRODUCTION_EFFICIENCY',
        FINANCIAL_SUMMARY: 'FINANCIAL_SUMMARY'
    },
    // Time periods
    TIME_PERIODS: {
        DAILY: 'DAILY',
        WEEKLY: 'WEEKLY',
        MONTHLY: 'MONTHLY',
        QUARTERLY: 'QUARTERLY',
        YEARLY: 'YEARLY',
        CUSTOM: 'CUSTOM'
    },
    // Aggregation levels
    AGGREGATION: {
        DETAIL: 'DETAIL',
        SUMMARY: 'SUMMARY',
        EXECUTIVE: 'EXECUTIVE'
    }
};
// ===== VALIDATION THRESHOLDS (ERP-spezifisch) =====
exports.ERP_VALIDATION = {
    // Inventory thresholds
    INVENTORY_THRESHOLDS: {
        MIN_QUANTITY: 0,
        MAX_QUANTITY: 999999,
        MIN_PRICE: 0,
        MAX_PRICE: 999999.99
    },
    // Order thresholds
    ORDER_THRESHOLDS: {
        MIN_LINE_VALUE: 0.01,
        MAX_LINE_VALUE: 999999.99,
        MIN_ORDER_VALUE: 0.01,
        MAX_ORDER_VALUE: 9999999.99
    },
    // Performance thresholds
    PERFORMANCE_THRESHOLDS: {
        ORDER_PROCESSING_TIME: utilities_1.TIME.ONE_HOUR,
        INVENTORY_COUNT_TIME: utilities_1.TIME.THIRTY_MINUTES,
        REPORT_GENERATION_TIME: utilities_1.TIME.TWO_MINUTES
    }
};
// ===== DEFAULT VALUES =====
exports.ERP_DEFAULTS = {
    // Business defaults
    DEFAULT_WAREHOUSE: 'WH-001',
    DEFAULT_LOCATION: 'A-01-01',
    DEFAULT_COST_CENTER: exports.ERP_FINANCE.COST_CENTERS.PRODUCTION,
    // Operational defaults
    DEFAULT_LEAD_TIME: exports.INVENTORY.DEFAULT_LEAD_TIME,
    DEFAULT_SAFETY_STOCK: 5,
    DEFAULT_ORDER_QUANTITY: 1,
    // System defaults
    DEFAULT_PAGE_SIZE: utilities_1.COLLECTION.DEFAULT_PAGE_SIZE,
    DEFAULT_TIMEOUT: utilities_1.TIME.ONE_MINUTE,
    DEFAULT_CURRENCY: utilities_1.BUSINESS.CURRENCIES.EUR
};
// ===== ERROR MESSAGES =====
exports.ERP_ERROR_MESSAGES = {
    // Inventory errors
    INVENTORY_NOT_FOUND: 'Inventory item not found',
    INSUFFICIENT_STOCK: 'Insufficient stock available',
    INVALID_LOCATION: 'Invalid storage location',
    // Order errors
    ORDER_NOT_FOUND: 'Order not found',
    INVALID_ORDER_STATUS: 'Invalid order status transition',
    ORDER_ALREADY_PROCESSED: 'Order has already been processed',
    // Product errors
    PRODUCT_NOT_FOUND: 'Product not found',
    DUPLICATE_PRODUCT_CODE: 'Product code already exists',
    INVALID_PRODUCT_CATEGORY: 'Invalid product category',
    // General errors
    VALIDATION_ERROR: 'Validation failed',
    PERMISSION_DENIED: 'Insufficient permissions',
    SYSTEM_ERROR: 'System error occurred'
};
