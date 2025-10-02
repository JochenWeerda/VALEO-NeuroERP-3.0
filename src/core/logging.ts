/**
 * VALEO-NeuroERP-3.0 Logging System
 * Structured logging with Winston and Pino
 */

import winston from 'winston';
import { config } from './config';

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

winston.addColors(colors);

// Create the logger
export const logger = winston.createLogger({
  level: config.logging.level,
  levels,
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: {
    service: 'valeo-neuro-erp',
    version: '3.0.0',
    environment: config.environment
  },
  transports: [
    // Error log file
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
      )
    }),

    // Combined log file
    new winston.transports.File({
      filename: 'logs/combined.log',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      )
    }),
  ],
});

// Add console transport for development
if (config.environment === 'development') {
  logger.add(new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize({ all: true }),
      winston.format.timestamp({ format: 'HH:mm:ss' }),
      winston.format.printf(({ timestamp, level, message, service, ...meta }) => {
        const metaStr = Object.keys(meta).length > 0 ? ` ${JSON.stringify(meta)}` : '';
        return `${timestamp} [${service}] ${level}: ${message}${metaStr}`;
      })
    )
  }));
}

// Handle uncaught exceptions and unhandled rejections
logger.exceptions.handle(
  new winston.transports.File({ filename: 'logs/exceptions.log' })
);

logger.rejections.handle(
  new winston.transports.File({ filename: 'logs/rejections.log' })
);

// Create child loggers for different domains
export const createDomainLogger = (domain: string) => {
  return logger.child({ domain });
};

// Specialized loggers
export const auditLogger = logger.child({ type: 'audit' });
export const performanceLogger = logger.child({ type: 'performance' });
export const securityLogger = logger.child({ type: 'security' });

// Logging utilities
export class Logger {
  private logger: winston.Logger;

  constructor(context: string) {
    this.logger = logger.child({ context });
  }

  error(message: string, meta?: any): void {
    this.logger.error(message, meta);
  }

  warn(message: string, meta?: any): void {
    this.logger.warn(message, meta);
  }

  info(message: string, meta?: any): void {
    this.logger.info(message, meta);
  }

  debug(message: string, meta?: any): void {
    this.logger.debug(message, meta);
  }

  // Performance logging
  time(label: string): () => void {
    const start = Date.now();
    return () => {
      const duration = Date.now() - start;
      this.logger.info(`Performance: ${label}`, { duration, unit: 'ms' });
    };
  }

  // Request logging middleware helper
  logRequest(req: any, res: any, next: any): void {
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

// Create domain-specific loggers
export const crmLogger = createDomainLogger('crm');
export const erpLogger = createDomainLogger('erp');
export const analyticsLogger = createDomainLogger('analytics');
export const integrationLogger = createDomainLogger('integration');
export const sharedLogger = createDomainLogger('shared');

// Export default logger instance
export default logger;