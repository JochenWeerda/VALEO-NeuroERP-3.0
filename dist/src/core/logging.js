"use strict";
/**
 * VALEO-NeuroERP-3.0 Logging System
 * Structured logging with Winston and Pino
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.sharedLogger = exports.integrationLogger = exports.analyticsLogger = exports.erpLogger = exports.crmLogger = exports.Logger = exports.securityLogger = exports.performanceLogger = exports.auditLogger = exports.createDomainLogger = exports.logger = void 0;
const winston_1 = __importDefault(require("winston"));
const config_1 = require("./config");
// Define log levels
const levels = {
    error: 0,
    warn: 1,
    info: 2,
    debug: 3,
};
// Define colors for console output
const colors = {
    error: 'red',
    warn: 'yellow',
    info: 'green',
    debug: 'blue',
};
winston_1.default.addColors(colors);
// Create the logger
exports.logger = winston_1.default.createLogger({
    level: config_1.config.logging.level,
    levels,
    format: winston_1.default.format.combine(winston_1.default.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }), winston_1.default.format.errors({ stack: true }), winston_1.default.format.json()),
    defaultMeta: {
        service: 'valeo-neuro-erp',
        version: '3.0.0',
        environment: config_1.config.environment
    },
    transports: [
        // Error log file
        new winston_1.default.transports.File({
            filename: 'logs/error.log',
            level: 'error',
            format: winston_1.default.format.combine(winston_1.default.format.timestamp(), winston_1.default.format.errors({ stack: true }), winston_1.default.format.json())
        }),
        // Combined log file
        new winston_1.default.transports.File({
            filename: 'logs/combined.log',
            format: winston_1.default.format.combine(winston_1.default.format.timestamp(), winston_1.default.format.json())
        }),
    ],
});
// Add console transport for development
if (config_1.config.environment === 'development') {
    exports.logger.add(new winston_1.default.transports.Console({
        format: winston_1.default.format.combine(winston_1.default.format.colorize({ all: true }), winston_1.default.format.timestamp({ format: 'HH:mm:ss' }), winston_1.default.format.printf(({ timestamp, level, message, service, ...meta }) => {
            const metaStr = Object.keys(meta).length > 0 ? ` ${JSON.stringify(meta)}` : '';
            return `${timestamp} [${service}] ${level}: ${message}${metaStr}`;
        }))
    }));
}
// Handle uncaught exceptions and unhandled rejections
exports.logger.exceptions.handle(new winston_1.default.transports.File({ filename: 'logs/exceptions.log' }));
exports.logger.rejections.handle(new winston_1.default.transports.File({ filename: 'logs/rejections.log' }));
// Create child loggers for different domains
const createDomainLogger = (domain) => {
    return exports.logger.child({ domain });
};
exports.createDomainLogger = createDomainLogger;
// Specialized loggers
exports.auditLogger = exports.logger.child({ type: 'audit' });
exports.performanceLogger = exports.logger.child({ type: 'performance' });
exports.securityLogger = exports.logger.child({ type: 'security' });
// Logging utilities
class Logger {
    logger;
    constructor(context) {
        this.logger = exports.logger.child({ context });
    }
    error(message, meta) {
        this.logger.error(message, meta);
    }
    warn(message, meta) {
        this.logger.warn(message, meta);
    }
    info(message, meta) {
        this.logger.info(message, meta);
    }
    debug(message, meta) {
        this.logger.debug(message, meta);
    }
    // Performance logging
    time(label) {
        const start = Date.now();
        return () => {
            const duration = Date.now() - start;
            this.logger.info(`Performance: ${label}`, { duration, unit: 'ms' });
        };
    }
    // Request logging middleware helper
    logRequest(req, res, next) {
        const start = Date.now();
        const { method, url, ip } = req;
        res.on('finish', () => {
            const duration = Date.now() - start;
            const { statusCode } = res;
            this.logger.info('HTTP Request', {
                method,
                url,
                statusCode,
                duration,
                ip,
                userAgent: req.get('User-Agent'),
            });
        });
        next();
    }
}
exports.Logger = Logger;
// Create domain-specific loggers
exports.crmLogger = (0, exports.createDomainLogger)('crm');
exports.erpLogger = (0, exports.createDomainLogger)('erp');
exports.analyticsLogger = (0, exports.createDomainLogger)('analytics');
exports.integrationLogger = (0, exports.createDomainLogger)('integration');
exports.sharedLogger = (0, exports.createDomainLogger)('shared');
// Export default logger instance
exports.default = exports.logger;
