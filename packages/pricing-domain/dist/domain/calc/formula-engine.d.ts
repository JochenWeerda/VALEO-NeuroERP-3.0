export declare function evaluateFormula(formula: {
    expression: string;
    inputs: any;
    rounding?: any;
    caps?: any;
}, context: Record<string, any>): Promise<{
    result: number;
    inputs: Record<string, number>;
    expression: string;
    cappedValue?: number;
    roundedValue: number;
    calculatedAt: string;
}>;
//# sourceMappingURL=formula-engine.d.ts.map