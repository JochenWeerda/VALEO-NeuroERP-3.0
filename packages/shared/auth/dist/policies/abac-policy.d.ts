import { UserContext, PolicyResult } from '../types/auth-types';
export interface ABACAttribute {
    category: 'subject' | 'resource' | 'action' | 'context';
    name: string;
    value: any;
    type: 'string' | 'number' | 'boolean' | 'array' | 'object';
}
export interface ABACRule {
    id: string;
    name: string;
    description?: string;
    condition: (attributes: ABACAttribute[]) => boolean;
    effect: 'allow' | 'deny';
    priority: number;
}
export interface ABACOptions {
    rules: ABACRule[];
    defaultEffect?: 'allow' | 'deny';
}
export declare class ABACPolicy {
    private rules;
    private defaultEffect;
    constructor(options: ABACOptions);
    /**
     * Evaluate ABAC policy for user and resource
     */
    evaluate(user: UserContext, resource: string, action: string, contextAttributes?: Record<string, any>): PolicyResult;
    /**
     * Add or update rule
     */
    addRule(rule: ABACRule): void;
    /**
     * Remove rule
     */
    removeRule(ruleId: string): void;
    /**
     * Get all rules
     */
    getRules(): ABACRule[];
    /**
     * Helper method to create common conditions
     */
    static createConditions(): {
        hasRole: (role: string) => (attributes: ABACAttribute[]) => boolean;
        hasTenant: (tenantId: string) => (attributes: ABACAttribute[]) => boolean;
        resourceMatches: (pattern: string) => (attributes: ABACAttribute[]) => boolean;
        actionIs: (action: string) => (attributes: ABACAttribute[]) => boolean;
        isBusinessHours: () => (attributes: ABACAttribute[]) => boolean;
        attributeEquals: (category: string, name: string, value: any) => (attributes: ABACAttribute[]) => boolean;
        and: (...conditions: Array<(attributes: ABACAttribute[]) => boolean>) => (attributes: ABACAttribute[]) => boolean;
        or: (...conditions: Array<(attributes: ABACAttribute[]) => boolean>) => (attributes: ABACAttribute[]) => boolean;
    };
}
//# sourceMappingURL=abac-policy.d.ts.map