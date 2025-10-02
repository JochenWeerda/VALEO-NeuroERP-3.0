export interface TemperatureRangeProps {
    readonly minC: number;
    readonly maxC: number;
}
export declare class TemperatureRange {
    private readonly props;
    private constructor();
    static create(props: TemperatureRangeProps): TemperatureRange;
    contains(valueC: number): boolean;
    toJSON(): TemperatureRangeProps;
}
//# sourceMappingURL=temperature-range.d.ts.map