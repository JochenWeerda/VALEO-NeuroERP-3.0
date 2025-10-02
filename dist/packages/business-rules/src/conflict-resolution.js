"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.conflictDetector = exports.ConflictDetector = void 0;
class ConflictDetector {
    detectConflicts(domain, rules) {
        const conflicts = [];
        // Priority conflicts
        conflicts.push(...this.detectPriorityConflicts(rules));
        // Validation conflicts
        conflicts.push(...this.detectValidationConflicts(rules));
        // Execution conflicts
        conflicts.push(...this.detectExecutionConflicts(rules));
        // Dependency conflicts
        conflicts.push(...this.detectDependencyConflicts(rules));
        return conflicts;
    }
    detectPriorityConflicts(rules) {
        const conflicts = [];
        const priorityMap = new Map();
        // Group rules by priority
        for (const rule of rules) {
            if (!priorityMap.has(rule.priority)) {
                priorityMap.set(rule.priority, []);
            }
            priorityMap.get(rule.priority).push(rule);
        }
        // Check for conflicts
        for (const [priority, rulesWithSamePriority] of priorityMap) {
            if (rulesWithSamePriority.length > 1) {
                for (let i = 0; i < rulesWithSamePriority.length; i++) {
                    for (let j = i + 1; j < rulesWithSamePriority.length; j++) {
                        conflicts.push({
                            type: 'PRIORITY_CONFLICT',
                            rule1: rulesWithSamePriority[i].name,
                            rule2: rulesWithSamePriority[j].name,
                            description: `Rules ${rulesWithSamePriority[i].name} and ${rulesWithSamePriority[j].name} have the same priority ${priority}`,
                            severity: 'medium'
                        });
                    }
                }
            }
        }
        return conflicts;
    }
    detectValidationConflicts(rules) {
        const conflicts = [];
        // This would analyze validation logic for conflicts
        // For now, return empty array as this requires deep analysis
        return conflicts;
    }
    detectExecutionConflicts(rules) {
        const conflicts = [];
        // This would analyze execution logic for conflicts
        // For now, return empty array as this requires deep analysis
        return conflicts;
    }
    detectDependencyConflicts(rules) {
        const conflicts = [];
        // Check for circular dependencies
        for (const rule of rules) {
            if (this.hasCircularDependency(rule.name, rules)) {
                conflicts.push({
                    type: 'DEPENDENCY_CONFLICT',
                    rule1: rule.name,
                    rule2: rule.name,
                    description: `Rule ${rule.name} has circular dependency`,
                    severity: 'critical'
                });
            }
        }
        return conflicts;
    }
    hasCircularDependency(ruleName, rules) {
        const visited = new Set();
        const recursionStack = new Set();
        const visit = (name) => {
            if (recursionStack.has(name)) {
                return true; // Circular dependency detected
            }
            if (visited.has(name)) {
                return false;
            }
            visited.add(name);
            recursionStack.add(name);
            // Check dependencies (this would need to be implemented based on actual dependency tracking)
            // For now, return false
            recursionStack.delete(name);
            return false;
        };
        return visit(ruleName);
    }
}
exports.ConflictDetector = ConflictDetector;
// Global Conflict Detector
exports.conflictDetector = new ConflictDetector();
