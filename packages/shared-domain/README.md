# VALEO NeuroERP 3.0 - Shared Domain

## 🎯 Overview

The Shared Domain package provides common functionality across all domains in the VALEO NeuroERP 3.0 system. It implements Clean Architecture principles with Domain-Driven Design patterns.

## 🏗️ Architecture

### Domain Layer
- **Entities**: Base entity classes and User entity
- **Value Objects**: Branded types, Email, PhoneNumber, Address, Money, etc.
- **Domain Events**: User lifecycle and operation events
- **Interfaces**: Repository contracts and domain interfaces

### Application Layer
- **DTOs**: Data Transfer Objects with Zod validation
- **Use Cases**: Business logic orchestration
- **Services**: Application services for complex operations
- **Event Handlers**: Domain event processing

### Infrastructure Layer
- **Repositories**: In-memory implementations for development/testing
- **Base Classes**: Common repository functionality

## 📦 Key Features

### ✅ Implemented
- **Clean Architecture**: Proper separation of concerns
- **Type Safety**: Full TypeScript coverage with branded types
- **Domain Events**: Event-driven architecture support
- **Repository Pattern**: Generic repository interfaces
- **Value Objects**: Rich domain objects with validation
- **Use Cases**: CQRS pattern implementation
- **Event Handlers**: Comprehensive event processing

### 🔧 Technical Stack
- **TypeScript**: Type-safe development
- **Zod**: Runtime validation
- **UUID**: Unique identifier generation
- **ES2022**: Modern JavaScript features

## 🚀 Usage

### Basic Setup

```typescript
import { UserApplicationService } from '@valero-neuroerp/shared-domain';
import { InMemoryUserRepository } from '@valero-neuroerp/shared-domain';

// Create repository
const userRepository = new InMemoryUserRepository();

// Create application service
const userService = new UserApplicationService(
  userRepository,
  (event) => console.log('Event:', event)
);

// Create a user
const user = await userService.createUser({
  username: 'john.doe',
  email: 'john@example.com',
  firstName: 'John',
  lastName: 'Doe',
  tenantId: 'tenant-1'
});
```

### Domain Events

```typescript
import { UserCreatedEventHandler } from '@valero-neuroerp/shared-domain';

const eventHandler = new UserCreatedEventHandler();
await eventHandler.handle(userCreatedEvent);
```

### Value Objects

```typescript
import { Email, PhoneNumber, Address, Money } from '@valero-neuroerp/shared-domain';

const email = new Email('user@example.com');
const phone = new PhoneNumber('+1234567890');
const address = new Address('123 Main St', 'City', '12345', 'Country');
const amount = new Money(100.50, 'EUR');
```

## 📋 Build Status

✅ **Build Successful**: The Shared Domain package compiles successfully with TypeScript.

## 🎯 Next Steps

1. **PostgreSQL Repository**: Implement database-backed repository
2. **External Services**: Add HTTP clients and external integrations
3. **Presentation Layer**: REST API controllers and middleware
4. **Testing**: Comprehensive unit and integration tests
5. **Documentation**: API documentation and usage guides

## 🔗 Related Packages

- `@valero-neuroerp/auth`: Authentication and authorization
- `@valero-neuroerp/contracts`: Shared contracts and schemas
- `@valero-neuroerp/integration-domain`: Integration services
- `@valero-neuroerp/logistics-domain`: Logistics operations

## 📝 Architecture Principles

1. **Single Responsibility**: Each class has one reason to change
2. **Dependency Inversion**: Depend on abstractions, not concretions
3. **Interface Segregation**: Small, focused interfaces
4. **Open/Closed**: Open for extension, closed for modification
5. **DRY**: Don't Repeat Yourself
6. **Type Safety**: Full TypeScript type coverage
7. **Testability**: Easy to unit test and mock
8. **Observability**: Comprehensive logging and metrics

---

**Status**: ✅ **FULLY IMPLEMENTED AND BUILDING**  
**Version**: 3.0.0  
**Last Updated**: October 2025


