export class RuleRegistry {
    rules = new Map();
    register(domain, rule) {
        const bucket = this.rules.get(domain) ?? [];
        bucket.push(rule);
        this.rules.set(domain, bucket);
    }
    get(domain) {
        return this.rules.get(domain) ?? [];
    }
}
export class BusinessLogicOrchestrator {
    registry;
    constructor(registry = new RuleRegistry()) {
        this.registry = registry;
    }
    async run(domain, context) {
        const rules = this.registry.get(domain);
        for (const rule of rules) {
            await rule.validate(context);
        }
    }
}
export const ruleRegistry = new RuleRegistry();
export const businessLogicOrchestrator = new BusinessLogicOrchestrator(ruleRegistry);
