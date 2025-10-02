"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.logger = exports.Logger = void 0;
exports.getLogger = getLogger;
const pino_1 = __importDefault(require("pino"));
class Logger {
    logger;
    constructor(options = {}) {
        this.logger = (0, pino_1.default)({
            level: process.env.LOG_LEVEL || 'info',
            formatters: {
                level: (label) => ({ level: label }),
            },
            serializers: {
                err: pino_1.default.stdSerializers.err,
                error: pino_1.default.stdSerializers.err,
                req: pino_1.default.stdSerializers.req,
                res: pino_1.default.stdSerializers.res,
            },
            ...options,
        });
    }
    createChildLogger(context = {}) {
        return this.logger.child(context);
    }
    info(message, context = {}) {
        this.createChildLogger(context).info(message);
    }
    warn(message, context = {}) {
        this.createChildLogger(context).warn(message);
    }
    error(message, error, context = {}) {
        const childLogger = this.createChildLogger(context);
        if (error) {
            childLogger.error({ err: error }, message);
        }
        else {
            childLogger.error(message);
        }
    }
    debug(message, context = {}) {
        this.createChildLogger(context).debug(message);
    }
    logRequest(request, context = {}) {
        this.info('Request received', {
            ...context,
            method: request.method,
            url: request.url,
            userAgent: request.headers['user-agent'],
            ip: request.ip,
        });
    }
    logResponse(response, duration, context = {}) {
        this.info('Request completed', {
            ...context,
            statusCode: response.statusCode,
            duration: `${duration}ms`,
        });
    }
    logScheduleExecution(scheduleId, success, duration, context = {}) {
        this.info('Schedule executed', {
            ...context,
            scheduleId,
            success,
            duration: `${duration}ms`,
        });
    }
    logSecurityEvent(event, details, context = {}) {
        this.warn(`Security event: ${event}`, {
            ...context,
            securityEvent: event,
            ...details,
        });
    }
    logPerformance(operation, duration, context = {}) {
        this.info(`Performance: ${operation}`, {
            ...context,
            operation,
            duration: `${duration}ms`,
        });
    }
}
exports.Logger = Logger;
let globalLogger = null;
function getLogger() {
    if (!globalLogger) {
        globalLogger = new Logger();
    }
    return globalLogger;
}
exports.logger = getLogger();
//# sourceMappingURL=logger.js.map