// Main exports for the Scheduler Domain

// Domain entities
export { ScheduleEntity, type TriggerType, type TargetType, type ScheduleStatus } from './domain/entities';

// Domain services
export { SchedulingService, type SchedulingServiceConfig, type ScheduleExecutionContext, type ScheduleExecutionResult } from './domain/services/scheduling-service';

// Infrastructure
export { ScheduleRepository, scheduleRepository } from './infra/repo/schedule-repository';
export { EventPublisher, NoOpEventPublisher } from './infra/messaging/publisher';
export { JWTAuthenticator, getJWTAuthenticator, initializeJWTAuthenticator } from './infra/security/jwt';
export { Logger, getLogger, logger } from './infra/telemetry/logger';
export { TracingService, getTracingService, initializeTracing, shutdownTracing } from './infra/telemetry/tracer';

// Application
export { createServer, startServer } from './app/server';

// Middleware
export { authMiddleware } from './app/middleware/auth';
export { tenantMiddleware } from './app/middleware/tenant';
export { requirePermissions, Permissions, requireScheduleRead, requireScheduleWrite, requireScheduleCreate, requireScheduleDelete, requireAdminAccess } from './app/middleware/rbac';
export { requestLoggerMiddleware } from './app/middleware/logger';

// Routes
export { registerScheduleRoutes } from './app/routes/schedules';