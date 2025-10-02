"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.businessLogicOrchestrator = exports.BusinessLogicOrchestrator = void 0;
const rule_registry_1 = require("./rule-registry");
const conflict_detection_1 = require("./conflict-detection");
const conflict_resolution_1 = require("./conflict-resolution");
class BusinessLogicOrchestrator {
    constructor(ruleRegistry, conflictDetector, conflictResolutionManager) {
        this.ruleRegistry = ruleRegistry;
        this.conflictDetector = conflictDetector;
        this.conflictResolutionManager = conflictResolutionManager;
    }
    async executeBusinessLogic(domain, data, operation, context) {
        const startTime = performance.now();
        try {
            // Get relevant rules
            const rules = this.ruleRegistry.getRulesByPriority(domain);
            // Filter rules by operation
            const operationRules = rules.filter(rule => this.shouldExecuteRule(rule, operation, context));
            if (operationRules.length === 0) {
                return {
                    success: true,
                    data,
                    errors: [],
                    warnings: [],
                    executedRules: [],
                    executionTime: performance.now() - startTime
                };
            }
            // Execute validation
            const validationResult = await this.executeValidation(data, operationRules, context);
            if (!validationResult.isValid) {
                return {
                    success: false,
                    data: undefined,
                    errors: validationResult.errors,
                    warnings: validationResult.warnings,
                    executedRules: operationRules.map(r => r.name),
                    executionTime: performance.now() - startTime
                };
            }
            // Execute business logic
            const processedData = await this.executeBusinessRules(data, operationRules, context);
            return {
                success: true,
                data: processedData,
                errors: [],
                warnings: validationResult.warnings,
                executedRules: operationRules.map(r => r.name),
                executionTime: performance.now() - startTime
            };
        }
        catch (error) {
            return {
                success: false,
                data: undefined,
                errors: [{
                        field: 'system',
                        message: `Business logic execution failed: ${error.message}`,
                        code: 'BUSINESS_LOGIC_ERROR',
                        severity: 'error'
                    }],
                warnings: [],
                executedRules: [],
                executionTime: performance.now() - startTime
            };
        }
    }
    shouldExecuteRule(rule, operation, context) {
        // Check if rule is enabled
        if (!rule.enabled) {
            return false;
        }
        // Check operation compatibility
        // This would be implemented based on rule metadata
        return true;
    }
    async executeValidation(data, rules, context) {
        const results = [];
        // Execute all rules
        for (const rule of rules) {
            try {
                const result = await rule.validate(data);
                results.push(result);
            }
            catch (error) {
                results.push({
                    isValid: false,
                    errors: [{
                            field: 'rule',
                            message: `Rule ${rule.name} validation failed: ${error.message}`,
                            code: 'RULE_VALIDATION_ERROR',
                            severity: 'error'
                        }],
                    warnings: []
                });
            }
        }
        // Check for conflicts
        const conflicts = this.conflictDetector.detectConflicts(context.domain, rules);
        if (conflicts.length > 0) {
            // Use consensus strategy for conflict resolution
            return this.conflictResolutionManager.resolveConflicts('CONSENSUS', conflicts, results);
        }
        // Merge results
        return this.mergeValidationResults(results);
    }
    async executeBusinessRules(data, rules, context) {
        let processedData = data;
        // Execute rules in priority order
        for (const rule of rules) {
            if (rule.execute) {
                try {
                    processedData = await rule.execute(processedData);
                }
                catch (error) {
                    // Rollback if possible
                    if (rule.rollback) {
                        try {
                            processedData = await rule.rollback(processedData);
                        }
                        catch (rollbackError) {
                            console.error(`Rollback failed for rule ${rule.name}:`, rollbackError);
                        }
                    }
                    throw new Error(`Rule ${rule.name} execution failed: ${error.message}`);
                }
            }
        }
        return processedData;
    }
    mergeValidationResults(results) {
        const allErrors = results.flatMap(r => r.errors);
        const allWarnings = results.flatMap(r => r.warnings);
        return {
            isValid: allErrors.length === 0,
            errors: allErrors,
            warnings: allWarnings
        };
    }
    // Rule management methods
    async registerRule(domain, rule) {
        this.ruleRegistry.register(domain, rule);
    }
    async enableRule(domain, ruleName) {
        this.ruleRegistry.enableRule(domain, ruleName);
    }
    async disableRule(domain, ruleName) {
        this.ruleRegistry.disableRule(domain, ruleName);
    }
    getRuleExecutionOrder(domain) {
        return this.ruleRegistry.getExecutionOrder(domain);
    }
}
exports.BusinessLogicOrchestrator = BusinessLogicOrchestrator;
// Global Business Logic Orchestrator
exports.businessLogicOrchestrator = new BusinessLogicOrchestrator(rule_registry_1.ruleRegistry, conflict_detection_1.conflictDetector, conflict_resolution_1.conflictResolutionManager);
