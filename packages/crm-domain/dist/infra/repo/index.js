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
exports.InteractionRepository = exports.OpportunityRepository = exports.ContactRepository = exports.CustomerRepository = void 0;
// Export all repositories
__exportStar(require("./customer-repository"), exports);
__exportStar(require("./contact-repository"), exports);
__exportStar(require("./opportunity-repository"), exports);
__exportStar(require("./interaction-repository"), exports);
// Re-export commonly used repository instances
var customer_repository_1 = require("./customer-repository");
Object.defineProperty(exports, "CustomerRepository", { enumerable: true, get: function () { return customer_repository_1.CustomerRepository; } });
var contact_repository_1 = require("./contact-repository");
Object.defineProperty(exports, "ContactRepository", { enumerable: true, get: function () { return contact_repository_1.ContactRepository; } });
var opportunity_repository_1 = require("./opportunity-repository");
Object.defineProperty(exports, "OpportunityRepository", { enumerable: true, get: function () { return opportunity_repository_1.OpportunityRepository; } });
var interaction_repository_1 = require("./interaction-repository");
Object.defineProperty(exports, "InteractionRepository", { enumerable: true, get: function () { return interaction_repository_1.InteractionRepository; } });
//# sourceMappingURL=index.js.map