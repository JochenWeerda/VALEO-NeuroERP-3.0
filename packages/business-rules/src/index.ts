/**
 * VALEO NeuroERP 3.0 - Business Rules Package
 *
 * Main exports for the business rule engine
 */

// Core business rule engine
export { IBusinessRule, BusinessRule } from './business-rule';

// Rule registry
export { RuleRegistry } from './rule-registry';

// Conflict detection
export {
  RuleConflict,
  ConflictAnalysisResult,
  ConflictDetector
} from './conflict-detection';

// Business logic orchestrator
export {
  ExecutionResult,
  OrchestratorOptions,
  BusinessLogicOrchestrator
} from './business-logic-orchestrator';

// Legacy exports for backward compatibility
import { RuleRegistry } from './rule-registry';
import { BusinessLogicOrchestrator } from './business-logic-orchestrator';

export const ruleRegistry = RuleRegistry;
export const businessLogicOrchestrator = new BusinessLogicOrchestrator('default');