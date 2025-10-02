"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ABACPolicy = void 0;
class ABACPolicy {
    constructor(options) {
        this.rules = [];
        this.rules = options.rules.sort((a, b) => b.priority - a.priority); // Higher priority first
        this.defaultEffect = options.defaultEffect || 'deny';
    }
    /**
     * Evaluate ABAC policy for user and resource
     */
    evaluate(user, resource, action, contextAttributes = {}) {
        try {
            // Build attributes list
            const attributes = [
                // Subject attributes
                ...user.roles.map(role => ({
                    category: 'subject',
                    name: 'role',
                    value: role,
                    type: 'string'
                })),
                {
                    category: 'subject',
                    name: 'userId',
                    value: user.userId,
                    type: 'string'
                },
                {
                    category: 'subject',
                    name: 'tenantId',
                    value: user.tenantId,
                    type: 'string'
                },
                // Resource attributes
                {
                    category: 'resource',
                    name: 'resource',
                    value: resource,
                    type: 'string'
                },
                // Action attributes
                {
                    category: 'action',
                    name: 'action',
                    value: action,
                    type: 'string'
                },
                // Context attributes
                ...Object.entries(contextAttributes).map(([name, value]) => ({
                    category: 'context',
                    name,
                    value,
                    type: typeof value
                }))
            ];
            // Evaluate rules in priority order
            for (const rule of this.rules) {
                try {
                    const conditionMet = rule.condition(attributes);
                    if (conditionMet) {
                        return {
                            allowed: rule.effect === 'allow',
                            reason: `ABAC rule "${rule.name}" ${rule.effect === 'allow' ? 'granted' : 'denied'} access`
                        };
                    }
                }
                catch (error) {
                    // Log error but continue with other rules
                    console.warn(`ABAC rule "${rule.name}" evaluation failed:`, error);
                }
            }
            // No rules matched, use default effect
            return {
                allowed: this.defaultEffect === 'allow',
                reason: `Default policy: ${this.defaultEffect}`
            };
        }
        catch (error) {
            return {
                allowed: false,
                reason: `ABAC evaluation failed: ${error instanceof Error ? error.message : 'Unknown error'}`
            };
        }
    }
    /**
     * Add or update rule
     */
    addRule(rule) {
        const existingIndex = this.rules.findIndex(r => r.id === rule.id);
        if (existingIndex >= 0) {
            this.rules[existingIndex] = rule;
        }
        else {
            this.rules.push(rule);
        }
        // Re-sort by priority
        this.rules.sort((a, b) => b.priority - a.priority);
    }
    /**
     * Remove rule
     */
    removeRule(ruleId) {
        this.rules = this.rules.filter(r => r.id !== ruleId);
    }
    /**
     * Get all rules
     */
    getRules() {
        return [...this.rules];
    }
    /**
     * Helper method to create common conditions
     */
    static createConditions() {
        return {
            // User has specific role
            hasRole: (role) => (attributes) => attributes.some(attr => attr.category === 'subject' && attr.name === 'role' && attr.value === role),
            // User belongs to tenant
            hasTenant: (tenantId) => (attributes) => attributes.some(attr => attr.category === 'subject' && attr.name === 'tenantId' && attr.value === tenantId),
            // Resource matches pattern
            resourceMatches: (pattern) => (attributes) => {
                const resourceAttr = attributes.find(attr => attr.category === 'resource' && attr.name === 'resource');
                if (!resourceAttr)
                    return false;
                const regex = new RegExp(pattern.replace(/\*/g, '.*'));
                return regex.test(resourceAttr.value);
            },
            // Action matches
            actionIs: (action) => (attributes) => attributes.some(attr => attr.category === 'action' && attr.name === 'action' && attr.value === action),
            // Time-based conditions
            isBusinessHours: () => (attributes) => {
                const now = new Date();
                const hour = now.getHours();
                const day = now.getDay();
                // Monday-Friday, 9 AM - 5 PM
                return day >= 1 && day <= 5 && hour >= 9 && hour < 17;
            },
            // Custom attribute condition
            attributeEquals: (category, name, value) => (attributes) => attributes.some(attr => attr.category === category && attr.name === name && attr.value === value),
            // Complex conditions with AND logic
            and: (...conditions) => (attributes) => conditions.every(condition => condition(attributes)),
            // Complex conditions with OR logic
            or: (...conditions) => (attributes) => conditions.some(condition => condition(attributes))
        };
    }
}
exports.ABACPolicy = ABACPolicy;
//# sourceMappingURL=abac-policy.js.map