/**
 * API Error Handling and Status Codes
 */

export enum HttpStatusCode {
  OK = 200,
  CREATED = 201,
  NO_CONTENT = 204,
  BAD_REQUEST = 400,
  UNAUTHORIZED = 401,
  FORBIDDEN = 403,
  NOT_FOUND = 404,
  CONFLICT = 409,
  UNPROCESSABLE_ENTITY = 422,
  INTERNAL_SERVER_ERROR = 500,
  SERVICE_UNAVAILABLE = 503
}

export class ApiError extends Error {
  public readonly statusCode: HttpStatusCode;
  public readonly code: string;
  public readonly details?: Record<string, unknown>;

  constructor(
    message: string,
    statusCode: HttpStatusCode = HttpStatusCode.INTERNAL_SERVER_ERROR,
    code?: string,
    details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.code = code || this.getDefaultCode(statusCode);
    this.details = details;
  }

  private getDefaultCode(statusCode: HttpStatusCode): string {
    switch (statusCode) {
      case HttpStatusCode.BAD_REQUEST:
        return 'BAD_REQUEST';
      case HttpStatusCode.UNAUTHORIZED:
        return 'UNAUTHORIZED';
      case HttpStatusCode.FORBIDDEN:
        return 'FORBIDDEN';
      case HttpStatusCode.NOT_FOUND:
        return 'NOT_FOUND';
      case HttpStatusCode.CONFLICT:
        return 'CONFLICT';
      case HttpStatusCode.UNPROCESSABLE_ENTITY:
        return 'UNPROCESSABLE_ENTITY';
      case HttpStatusCode.INTERNAL_SERVER_ERROR:
        return 'INTERNAL_SERVER_ERROR';
      case HttpStatusCode.SERVICE_UNAVAILABLE:
        return 'SERVICE_UNAVAILABLE';
      default:
        return 'UNKNOWN_ERROR';
    }
  }

  toJSON(): Record<string, unknown> {
    return {
      error: {
        message: this.message,
        code: this.code,
        statusCode: this.statusCode,
        details: this.details,
        timestamp: new Date().toISOString()
      }
    };
  }
}

export class ValidationError extends ApiError {
  public readonly validationErrors: Array<{
    field: string;
    message: string;
    value?: unknown;
  }>;

  constructor(
    message: string,
    validationErrors: Array<{ field: string; message: string; value?: unknown }>,
    details?: Record<string, unknown>
  ) {
    super(message, HttpStatusCode.UNPROCESSABLE_ENTITY, 'VALIDATION_ERROR', details);
    this.name = 'ValidationError';
    this.validationErrors = validationErrors;
  }

  toJSON(): Record<string, unknown> {
    return {
      error: {
        message: this.message,
        code: this.code,
        statusCode: this.statusCode,
        validationErrors: this.validationErrors,
        details: this.details,
        timestamp: new Date().toISOString()
      }
    };
  }
}

export class NotFoundError extends ApiError {
  constructor(resource: string, id: string) {
    super(
      `${resource} with id '${id}' not found`,
      HttpStatusCode.NOT_FOUND,
      'NOT_FOUND',
      { resource, id }
    );
    this.name = 'NotFoundError';
  }
}

export class ConflictError extends ApiError {
  constructor(resource: string, field: string, value: string) {
    super(
      `${resource} with ${field} '${value}' already exists`,
      HttpStatusCode.CONFLICT,
      'CONFLICT',
      { resource, field, value }
    );
    this.name = 'ConflictError';
  }
}

export class UnauthorizedError extends ApiError {
  constructor(message = 'Authentication required') {
    super(message, HttpStatusCode.UNAUTHORIZED, 'UNAUTHORIZED');
    this.name = 'UnauthorizedError';
  }
}

export class ForbiddenError extends ApiError {
  constructor(message = 'Access forbidden') {
    super(message, HttpStatusCode.FORBIDDEN, 'FORBIDDEN');
    this.name = 'ForbiddenError';
  }
}

export class InternalServerError extends ApiError {
  constructor(message = 'Internal server error', details?: Record<string, unknown>) {
    super(message, HttpStatusCode.INTERNAL_SERVER_ERROR, 'INTERNAL_SERVER_ERROR', details);
    this.name = 'InternalServerError';
  }
}

export class ServiceUnavailableError extends ApiError {
  constructor(message = 'Service temporarily unavailable') {
    super(message, HttpStatusCode.SERVICE_UNAVAILABLE, 'SERVICE_UNAVAILABLE');
    this.name = 'ServiceUnavailableError';
  }
}

// Error factory functions
export const createValidationError = (
  message: string,
  validationErrors: Array<{ field: string; message: string; value?: unknown }>
): ValidationError => {
  return new ValidationError(message, validationErrors);
};

export const createNotFoundError = (resource: string, id: string): NotFoundError => {
  return new NotFoundError(resource, id);
};

export const createConflictError = (resource: string, field: string, value: string): ConflictError => {
  return new ConflictError(resource, field, value);
};

export const createUnauthorizedError = (message?: string): UnauthorizedError => {
  return new UnauthorizedError(message);
};

export const createForbiddenError = (message?: string): ForbiddenError => {
  return new ForbiddenError(message);
};

export const createInternalServerError = (message?: string, details?: Record<string, unknown>): InternalServerError => {
  return new InternalServerError(message, details);
};

export const createServiceUnavailableError = (message?: string): ServiceUnavailableError => {
  return new ServiceUnavailableError(message);
};
