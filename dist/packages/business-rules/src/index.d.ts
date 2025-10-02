export type RuleContext = Record<string, unknown>;
export interface BusinessRule<TContext extends RuleContext = RuleContext> {
    readonly name: string;
    validate(context: TContext): Promise<void> | void;
}
export declare class RuleRegistry {
    private readonly rules;
    register(domain: string, rule: BusinessRule): void;
    get(domain: string): BusinessRule[];
}
export declare class BusinessLogicOrchestrator {
    private readonly registry;
    constructor(registry?: RuleRegistry);
    run(domain: string, context: RuleContext): Promise<void>;
}
export declare const ruleRegistry: RuleRegistry;
export declare const businessLogicOrchestrator: BusinessLogicOrchestrator;
//***REMOVED*** sourceMappingURL=index.d.ts.map