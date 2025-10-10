import pino from 'pino';

export interface LogContext {
  requestId?: string;
  tenantId?: string;
  userId?: string;
  correlationId?: string;
  operation?: string;
  [key: string]: any;
}

export class Logger {
  private readonly logger: pino.Logger;

  constructor(options: pino.LoggerOptions = {}) {
    this.logger = pino({
      level: process.env.LOG_LEVEL || 'info',
      formatters: {
        level: (label) => ({ level: label }),
      },
      serializers: {
        err: pino.stdSerializers.err,
        error: pino.stdSerializers.err,
        req: pino.stdSerializers.req,
        res: pino.stdSerializers.res,
      },
      ...options,
    });
  }

  private createChildLogger(context: LogContext = {}): pino.Logger {
    return this.logger.child(context);
  }

  info(message: string, context: LogContext = {}): void {
    this.createChildLogger(context).info(message);
  }

  warn(message: string, context: LogContext = {}): void {
    this.createChildLogger(context).warn(message);
  }

  error(message: string, error?: Error, context: LogContext = {}): void {
    const childLogger = this.createChildLogger(context);
    if (error) {
      childLogger.error({ err: error }, message);
    } else {
      childLogger.error(message);
    }
  }

  debug(message: string, context: LogContext = {}): void {
    this.createChildLogger(context).debug(message);
  }

  // Specialized logging methods
  logRequest(request: any, context: LogContext = {}): void {
    this.info('Request received', {
      ...context,
      method: request.method,
      url: request.url,
      userAgent: request.headers['user-agent'],
      ip: request.ip,
    });
  }

  logResponse(response: any, duration: number, context: LogContext = {}): void {
    this.info('Request completed', {
      ...context,
      statusCode: response.statusCode,
      duration: `${duration}ms`,
    });
  }

  logScheduleExecution(scheduleId: string, success: boolean, duration: number, context: LogContext = {}): void {
    this.info('Schedule executed', {
      ...context,
      scheduleId,
      success,
      duration: `${duration}ms`,
    });
  }

  logSecurityEvent(event: string, details: any, context: LogContext = {}): void {
    this.warn(`Security event: ${event}`, {
      ...context,
      securityEvent: event,
      ...details,
    });
  }

  logPerformance(operation: string, duration: number, context: LogContext = {}): void {
    this.info(`Performance: ${operation}`, {
      ...context,
      operation,
      duration: `${duration}ms`,
    });
  }
}

// Global logger instance
let globalLogger: Logger | null = null;

export function getLogger(): Logger {
  if (!globalLogger) {
    globalLogger = new Logger();
  }
  return globalLogger;
}

// Export logger instance
export const logger = getLogger();