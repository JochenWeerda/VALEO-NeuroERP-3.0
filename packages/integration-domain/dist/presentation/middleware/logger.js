/**
 * Logging Middleware
 */
export class LoggerMiddleware {
    logLevel;
    constructor(logLevel = 'info') {
        this.logLevel = logLevel;
    }
    shouldLog(level) {
        const levels = ['debug', 'info', 'warn', 'error'];
        return levels.indexOf(level) >= levels.indexOf(this.logLevel);
    }
    formatLog(entry) {
        const parts = [
            `[${entry.timestamp}]`,
            `${entry.method} ${entry.url}`,
            entry.statusCode ? ` ${entry.statusCode}` : '',
            entry.duration ? ` ${entry.duration}ms` : '',
            entry.userId ? ` user:${entry.userId}` : '',
            entry.requestId ? ` req:${entry.requestId}` : '',
            entry.error ? ` error:${entry.error}` : ''
        ];
        return parts.join('');
    }
    log(level, entry) {
        if (!this.shouldLog(level)) {
            return;
        }
        const message = this.formatLog(entry);
        switch (level) {
            case 'debug':
                console.debug(message);
                break;
            case 'info':
                console.info(message);
                break;
            case 'warn':
                console.warn(message);
                break;
            case 'error':
                console.error(message);
                break;
        }
    }
    // Request logging middleware
    requestLogger = (req, res, next) => {
        const startTime = Date.now();
        const requestId = this.generateRequestId();
        // Add request ID to request object
        req.requestId = requestId;
        // Log request start
        this.log('info', {
            timestamp: new Date().toISOString(),
            method: req.method,
            url: req.url,
            userAgent: req.get('User-Agent'),
            ip: req.ip,
            userId: req.user?.id,
            requestId
        });
        // Override res.end to log response
        const originalEnd = res.end;
        res.end = (...args) => {
            const duration = Date.now() - startTime;
            this.log('info', {
                timestamp: new Date().toISOString(),
                method: req.method,
                url: req.url,
                statusCode: res.statusCode,
                duration,
                userAgent: req.get('User-Agent'),
                ip: req.ip,
                userId: req.user?.id,
                requestId
            });
            originalEnd.apply(res, args);
        };
        next();
    };
    // Error logging middleware
    errorLogger = (error, req, res, next) => {
        this.log('error', {
            timestamp: new Date().toISOString(),
            method: req.method,
            url: req.url,
            userAgent: req.get('User-Agent'),
            ip: req.ip,
            userId: req.user?.id,
            requestId: req.requestId,
            error: error.message
        });
        next(error);
    };
    generateRequestId() {
        return Math.random().toString(36).substring(2, 15) +
            Math.random().toString(36).substring(2, 15);
    }
    // Manual logging methods
    debug(message, data) {
        if (this.shouldLog('debug')) {
            console.debug(`[${new Date().toISOString()}] DEBUG: ${message}`, data || '');
        }
    }
    info(message, data) {
        if (this.shouldLog('info')) {
            console.info(`[${new Date().toISOString()}] INFO: ${message}`, data || '');
        }
    }
    warn(message, data) {
        if (this.shouldLog('warn')) {
            console.warn(`[${new Date().toISOString()}] WARN: ${message}`, data || '');
        }
    }
    error(message, data) {
        if (this.shouldLog('error')) {
            console.error(`[${new Date().toISOString()}] ERROR: ${message}`, data || '');
        }
    }
}
//# sourceMappingURL=logger.js.map