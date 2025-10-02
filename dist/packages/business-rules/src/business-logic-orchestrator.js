"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.conflictResolutionManager = exports.ConflictResolutionManager = exports.WeightedStrategy = exports.FailFastStrategy = exports.ConsensusStrategy = exports.PriorityBasedStrategy = void 0;
class PriorityBasedStrategy {
    constructor() {
        this.name = 'PRIORITY_BASED';
        this.description = 'Use highest priority rule result';
    }
    resolve(conflicts, results) {
        // Sort results by priority (highest first)
        const sortedResults = results.sort((a, b) => {
            // This would need to be implemented based on actual rule priority
            return 0;
        });
        // Use highest priority result
        return sortedResults[0] || { isValid: true, errors: [], warnings: [] };
    }
}
exports.PriorityBasedStrategy = PriorityBasedStrategy;
class ConsensusStrategy {
    constructor() {
        this.name = 'CONSENSUS';
        this.description = 'Use consensus of all rules';
    }
    resolve(conflicts, results) {
        const allErrors = results.flatMap(r => r.errors);
        const allWarnings = results.flatMap(r => r.warnings);
        // Remove duplicate errors
        const uniqueErrors = this.removeDuplicateErrors(allErrors);
        const uniqueWarnings = this.removeDuplicateWarnings(allWarnings);
        return {
            isValid: uniqueErrors.length === 0,
            errors: uniqueErrors,
            warnings: uniqueWarnings
        };
    }
    removeDuplicateErrors(errors) {
        const seen = new Set();
        return errors.filter(error => {
            const key = `${error.field}:${error.code}`;
            if (seen.has(key)) {
                return false;
            }
            seen.add(key);
            return true;
        });
    }
    removeDuplicateWarnings(warnings) {
        const seen = new Set();
        return warnings.filter(warning => {
            const key = `${warning.field}:${warning.code}`;
            if (seen.has(key)) {
                return false;
            }
            seen.add(key);
            return true;
        });
    }
}
exports.ConsensusStrategy = ConsensusStrategy;
class FailFastStrategy {
    constructor() {
        this.name = 'FAIL_FAST';
        this.description = 'Fail on first error';
    }
    resolve(conflicts, results) {
        // Find first error
        for (const result of results) {
            if (!result.isValid && result.errors.length > 0) {
                return result;
            }
        }
        // If no errors, return first result
        return results[0] || { isValid: true, errors: [], warnings: [] };
    }
}
exports.FailFastStrategy = FailFastStrategy;
class WeightedStrategy {
    constructor() {
        this.name = 'WEIGHTED';
        this.description = 'Use weighted average based on rule priority';
    }
    resolve(conflicts, results) {
        // This would implement weighted resolution based on rule priorities
        // For now, use consensus strategy
        const consensusStrategy = new ConsensusStrategy();
        return consensusStrategy.resolve(conflicts, results);
    }
}
exports.WeightedStrategy = WeightedStrategy;
// Conflict Resolution Manager
class ConflictResolutionManager {
    constructor() {
        this.strategies = new Map();
        // Register default strategies
        this.registerStrategy(new PriorityBasedStrategy());
        this.registerStrategy(new ConsensusStrategy());
        this.registerStrategy(new FailFastStrategy());
        this.registerStrategy(new WeightedStrategy());
    }
    registerStrategy(strategy) {
        this.strategies.set(strategy.name, strategy);
    }
    resolveConflicts(strategyName, conflicts, results) {
        const strategy = this.strategies.get(strategyName);
        if (!strategy) {
            throw new Error(`Strategy ${strategyName} not found`);
        }
        return strategy.resolve(conflicts, results);
    }
    getAvailableStrategies() {
        return Array.from(this.strategies.keys());
    }
}
exports.ConflictResolutionManager = ConflictResolutionManager;
// Global Conflict Resolution Manager
exports.conflictResolutionManager = new ConflictResolutionManager();
