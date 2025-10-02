export interface TimeWindowProps {
    readonly from: Date;
    readonly to: Date;
}
export declare class TimeWindow {
    private readonly props;
    private constructor();
    static create(props: TimeWindowProps): TimeWindow;
    get from(): Date;
    get to(): Date;
    durationMinutes(): number;
    toJSON(): {
        from: string;
        to: string;
    };
}
//# sourceMappingURL=time-window.d.ts.map