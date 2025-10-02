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
exports.AttachmentContractSchema = exports.InteractionTypeContractSchema = exports.InteractionListResponseContractSchema = exports.InteractionQueryContractSchema = exports.InteractionResponseContractSchema = exports.UpdateInteractionContractSchema = exports.CreateInteractionContractSchema = exports.OpportunityStageContractSchema = exports.OpportunityListResponseContractSchema = exports.OpportunityQueryContractSchema = exports.OpportunityResponseContractSchema = exports.UpdateOpportunityContractSchema = exports.CreateOpportunityContractSchema = exports.ContactResponseContractSchema = exports.UpdateContactContractSchema = exports.CreateContactContractSchema = exports.CustomerStatusContractSchema = exports.AddressContractSchema = exports.CustomerListResponseContractSchema = exports.CustomerQueryContractSchema = exports.CustomerResponseContractSchema = exports.UpdateCustomerContractSchema = exports.CreateCustomerContractSchema = void 0;
// Export all contract schemas
__exportStar(require("./customer-contracts"), exports);
__exportStar(require("./contact-contracts"), exports);
__exportStar(require("./opportunity-contracts"), exports);
__exportStar(require("./interaction-contracts"), exports);
// Re-export commonly used contract schemas
var customer_contracts_1 = require("./customer-contracts");
Object.defineProperty(exports, "CreateCustomerContractSchema", { enumerable: true, get: function () { return customer_contracts_1.CreateCustomerContractSchema; } });
Object.defineProperty(exports, "UpdateCustomerContractSchema", { enumerable: true, get: function () { return customer_contracts_1.UpdateCustomerContractSchema; } });
Object.defineProperty(exports, "CustomerResponseContractSchema", { enumerable: true, get: function () { return customer_contracts_1.CustomerResponseContractSchema; } });
Object.defineProperty(exports, "CustomerQueryContractSchema", { enumerable: true, get: function () { return customer_contracts_1.CustomerQueryContractSchema; } });
Object.defineProperty(exports, "CustomerListResponseContractSchema", { enumerable: true, get: function () { return customer_contracts_1.CustomerListResponseContractSchema; } });
Object.defineProperty(exports, "AddressContractSchema", { enumerable: true, get: function () { return customer_contracts_1.AddressContractSchema; } });
Object.defineProperty(exports, "CustomerStatusContractSchema", { enumerable: true, get: function () { return customer_contracts_1.CustomerStatusContractSchema; } });
var contact_contracts_1 = require("./contact-contracts");
Object.defineProperty(exports, "CreateContactContractSchema", { enumerable: true, get: function () { return contact_contracts_1.CreateContactContractSchema; } });
Object.defineProperty(exports, "UpdateContactContractSchema", { enumerable: true, get: function () { return contact_contracts_1.UpdateContactContractSchema; } });
Object.defineProperty(exports, "ContactResponseContractSchema", { enumerable: true, get: function () { return contact_contracts_1.ContactResponseContractSchema; } });
var opportunity_contracts_1 = require("./opportunity-contracts");
Object.defineProperty(exports, "CreateOpportunityContractSchema", { enumerable: true, get: function () { return opportunity_contracts_1.CreateOpportunityContractSchema; } });
Object.defineProperty(exports, "UpdateOpportunityContractSchema", { enumerable: true, get: function () { return opportunity_contracts_1.UpdateOpportunityContractSchema; } });
Object.defineProperty(exports, "OpportunityResponseContractSchema", { enumerable: true, get: function () { return opportunity_contracts_1.OpportunityResponseContractSchema; } });
Object.defineProperty(exports, "OpportunityQueryContractSchema", { enumerable: true, get: function () { return opportunity_contracts_1.OpportunityQueryContractSchema; } });
Object.defineProperty(exports, "OpportunityListResponseContractSchema", { enumerable: true, get: function () { return opportunity_contracts_1.OpportunityListResponseContractSchema; } });
Object.defineProperty(exports, "OpportunityStageContractSchema", { enumerable: true, get: function () { return opportunity_contracts_1.OpportunityStageContractSchema; } });
var interaction_contracts_1 = require("./interaction-contracts");
Object.defineProperty(exports, "CreateInteractionContractSchema", { enumerable: true, get: function () { return interaction_contracts_1.CreateInteractionContractSchema; } });
Object.defineProperty(exports, "UpdateInteractionContractSchema", { enumerable: true, get: function () { return interaction_contracts_1.UpdateInteractionContractSchema; } });
Object.defineProperty(exports, "InteractionResponseContractSchema", { enumerable: true, get: function () { return interaction_contracts_1.InteractionResponseContractSchema; } });
Object.defineProperty(exports, "InteractionQueryContractSchema", { enumerable: true, get: function () { return interaction_contracts_1.InteractionQueryContractSchema; } });
Object.defineProperty(exports, "InteractionListResponseContractSchema", { enumerable: true, get: function () { return interaction_contracts_1.InteractionListResponseContractSchema; } });
Object.defineProperty(exports, "InteractionTypeContractSchema", { enumerable: true, get: function () { return interaction_contracts_1.InteractionTypeContractSchema; } });
Object.defineProperty(exports, "AttachmentContractSchema", { enumerable: true, get: function () { return interaction_contracts_1.AttachmentContractSchema; } });
//# sourceMappingURL=index.js.map