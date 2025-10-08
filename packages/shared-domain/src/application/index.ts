/**
 * Application Layer Exports for VALEO NeuroERP 3.0
 * Clean Architecture - Application Layer
 */

// DTOs
export * from './dto/user-dto.js';

// Use Cases
export { UserUseCases } from './use-cases/user-use-cases.js';
export type {
  CreateUserCommand,
  UpdateUserCommand,
  ActivateUserCommand,
  DeactivateUserCommand,
  AddRoleToUserCommand,
  RemoveRoleFromUserCommand,
  LoginUserCommand,
  GetUserQuery,
  SearchUsersQuery,
  GetUserStatsQuery
} from './use-cases/user-use-cases.js';

// Application Services
export { UserApplicationService } from './services/user-application-service.js';

// Event Handlers
export {
  UserCreatedEventHandler,
  UserUpdatedEventHandler,
  UserActivatedEventHandler,
  UserDeactivatedEventHandler,
  UserRoleAddedEventHandler,
  UserRoleRemovedEventHandler,
  UserLoggedInEventHandler,
  UserLoggedOutEventHandler,
  UserEmailVerifiedEventHandler,
  UserTenantChangedEventHandler,
  UserDeletedEventHandler,
  type EventHandler
} from './handlers/user-event-handlers.js';


