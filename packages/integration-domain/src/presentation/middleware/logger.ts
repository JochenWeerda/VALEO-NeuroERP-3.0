/**
 * Logging Middleware
 */

export interface LogEntry {
  timestamp: string;
  method: string;
  url: string;
  statusCode?: number;
  duration?: number;
  userAgent?: string;
  ip?: string;
  userId?: string;
  requestId?: string;
  error?: string;
}

export class LoggerMiddleware {
  private logLevel: 'debug' | 'info' | 'warn' | 'error';

  constructor(logLevel: 'debug' | 'info' | 'warn' | 'error' = 'info') {
    this.logLevel = logLevel;
  }

  private shouldLog(level: string): boolean {
    const levels = ['debug', 'info', 'warn', 'error'];
    return levels.indexOf(level) >= levels.indexOf(this.logLevel);
  }

  private formatLog(entry: LogEntry): string {
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

  private log(level: string, entry: LogEntry): void {
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
  requestLogger = (req: any, res: any, next: any) => {
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
    res.end = (...args: any[]) => {
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
  errorLogger = (error: any, req: any, res: any, next: any) => {
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

  private generateRequestId(): string {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }

  // Manual logging methods
  debug(message: string, data?: any): void {
    if (this.shouldLog('debug')) {
      console.debug(`[${new Date().toISOString()}] DEBUG: ${message}`, data || '');
    }
  }

  info(message: string, data?: any): void {
    if (this.shouldLog('info')) {
      console.info(`[${new Date().toISOString()}] INFO: ${message}`, data || '');
    }
  }

  warn(message: string, data?: any): void {
    if (this.shouldLog('warn')) {
      console.warn(`[${new Date().toISOString()}] WARN: ${message}`, data || '');
    }
  }

  error(message: string, data?: any): void {
    if (this.shouldLog('error')) {
      console.error(`[${new Date().toISOString()}] ERROR: ${message}`, data || '');
    }
  }
}
