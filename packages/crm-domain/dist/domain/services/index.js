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
exports.InteractionService = exports.OpportunityService = exports.ContactService = exports.CustomerService = void 0;
// Export all services
__exportStar(require("./customer-service"), exports);
__exportStar(require("./contact-service"), exports);
__exportStar(require("./opportunity-service"), exports);
__exportStar(require("./interaction-service"), exports);
// Re-export commonly used service classes
var customer_service_1 = require("./customer-service");
Object.defineProperty(exports, "CustomerService", { enumerable: true, get: function () { return customer_service_1.CustomerService; } });
var contact_service_1 = require("./contact-service");
Object.defineProperty(exports, "ContactService", { enumerable: true, get: function () { return contact_service_1.ContactService; } });
var opportunity_service_1 = require("./opportunity-service");
Object.defineProperty(exports, "OpportunityService", { enumerable: true, get: function () { return opportunity_service_1.OpportunityService; } });
var interaction_service_1 = require("./interaction-service");
Object.defineProperty(exports, "InteractionService", { enumerable: true, get: function () { return interaction_service_1.InteractionService; } });
//# sourceMappingURL=index.js.map