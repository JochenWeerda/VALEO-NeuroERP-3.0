/**
 * Repository interfaces for CRM Domain
 * Repository und RepositoryBase werden aus @valero-neuroerp/utilities importiert
 */

// Repository-Interfaces werden aus utilities Package importiert

export interface Logger {
  debug(message: string, context?: Record<string, unknown>): void;
  info(message: string, context?: Record<string, unknown>): void;
  warn(message: string, context?: Record<string, unknown>): void;
  error(message: string, context?: Record<string, unknown>): void;
}

// MetricsRecorder wird aus @valero-neuroerp/utilities importiert
