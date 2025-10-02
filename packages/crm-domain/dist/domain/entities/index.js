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
exports.InteractionType = exports.OpportunityStage = exports.CustomerStatus = void 0;
// Export all entities
__exportStar(require("./customer"), exports);
__exportStar(require("./contact"), exports);
__exportStar(require("./opportunity"), exports);
__exportStar(require("./interaction"), exports);
// Re-export enums
var customer_1 = require("./customer");
Object.defineProperty(exports, "CustomerStatus", { enumerable: true, get: function () { return customer_1.CustomerStatus; } });
var opportunity_1 = require("./opportunity");
Object.defineProperty(exports, "OpportunityStage", { enumerable: true, get: function () { return opportunity_1.OpportunityStage; } });
var interaction_1 = require("./interaction");
Object.defineProperty(exports, "InteractionType", { enumerable: true, get: function () { return interaction_1.InteractionType; } });
//# sourceMappingURL=index.js.map