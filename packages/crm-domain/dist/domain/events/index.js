"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createInteractionDeletedEvent = exports.createInteractionUpdatedEvent = exports.createInteractionCreatedEvent = exports.createOpportunityDeletedEvent = exports.createOpportunityLostEvent = exports.createOpportunityWonEvent = exports.createOpportunityStageChangedEvent = exports.createOpportunityUpdatedEvent = exports.createOpportunityCreatedEvent = exports.createContactDeletedEvent = exports.createContactUpdatedEvent = exports.createContactCreatedEvent = exports.createCustomerDeletedEvent = exports.createCustomerStatusChangedEvent = exports.createCustomerUpdatedEvent = exports.createCustomerCreatedEvent = exports.DomainEventType = void 0;
// Export all domain events
__exportStar(require("./domain-events"), exports);
__exportStar(require("./event-factories"), exports);
// Re-export commonly used types and constants
var domain_events_1 = require("./domain-events");
Object.defineProperty(exports, "DomainEventType", { enumerable: true, get: function () { return domain_events_1.DomainEventType; } });
// Re-export event factory functions
var event_factories_1 = require("./event-factories");
Object.defineProperty(exports, "createCustomerCreatedEvent", { enumerable: true, get: function () { return event_factories_1.createCustomerCreatedEvent; } });
Object.defineProperty(exports, "createCustomerUpdatedEvent", { enumerable: true, get: function () { return event_factories_1.createCustomerUpdatedEvent; } });
Object.defineProperty(exports, "createCustomerStatusChangedEvent", { enumerable: true, get: function () { return event_factories_1.createCustomerStatusChangedEvent; } });
Object.defineProperty(exports, "createCustomerDeletedEvent", { enumerable: true, get: function () { return event_factories_1.createCustomerDeletedEvent; } });
Object.defineProperty(exports, "createContactCreatedEvent", { enumerable: true, get: function () { return event_factories_1.createContactCreatedEvent; } });
Object.defineProperty(exports, "createContactUpdatedEvent", { enumerable: true, get: function () { return event_factories_1.createContactUpdatedEvent; } });
Object.defineProperty(exports, "createContactDeletedEvent", { enumerable: true, get: function () { return event_factories_1.createContactDeletedEvent; } });
Object.defineProperty(exports, "createOpportunityCreatedEvent", { enumerable: true, get: function () { return event_factories_1.createOpportunityCreatedEvent; } });
Object.defineProperty(exports, "createOpportunityUpdatedEvent", { enumerable: true, get: function () { return event_factories_1.createOpportunityUpdatedEvent; } });
Object.defineProperty(exports, "createOpportunityStageChangedEvent", { enumerable: true, get: function () { return event_factories_1.createOpportunityStageChangedEvent; } });
Object.defineProperty(exports, "createOpportunityWonEvent", { enumerable: true, get: function () { return event_factories_1.createOpportunityWonEvent; } });
Object.defineProperty(exports, "createOpportunityLostEvent", { enumerable: true, get: function () { return event_factories_1.createOpportunityLostEvent; } });
Object.defineProperty(exports, "createOpportunityDeletedEvent", { enumerable: true, get: function () { return event_factories_1.createOpportunityDeletedEvent; } });
Object.defineProperty(exports, "createInteractionCreatedEvent", { enumerable: true, get: function () { return event_factories_1.createInteractionCreatedEvent; } });
Object.defineProperty(exports, "createInteractionUpdatedEvent", { enumerable: true, get: function () { return event_factories_1.createInteractionUpdatedEvent; } });
Object.defineProperty(exports, "createInteractionDeletedEvent", { enumerable: true, get: function () { return event_factories_1.createInteractionDeletedEvent; } });
//# sourceMappingURL=index.js.map