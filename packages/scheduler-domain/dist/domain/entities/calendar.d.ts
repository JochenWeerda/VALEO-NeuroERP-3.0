export declare class CalendarEntity {
    readonly id: string;
    readonly tenantId?: string;
    readonly key: string;
    readonly name: string;
    readonly holidays: Date[];
    readonly businessDays: Record<string, boolean>;
    readonly createdAt: Date;
    readonly updatedAt: Date;
    readonly version: number;
    constructor(props: {
        id?: string;
        tenantId?: string;
        key: string;
        name: string;
        holidays?: Date[];
        businessDays?: Record<string, boolean>;
        createdAt?: Date;
        updatedAt?: Date;
        version?: number;
    });
    private validate;
    isHoliday(date: Date): boolean;
    isBusinessDay(date: Date): boolean;
    isWorkingDay(date: Date): boolean;
    getNextWorkingDay(fromDate: Date): Date;
    getPreviousWorkingDay(fromDate: Date): Date;
    addWorkingDays(date: Date, days: number): Date;
    getWorkingDaysInRange(startDate: Date, endDate: Date): Date[];
    updateHolidays(holidays: Date[]): CalendarEntity;
    updateBusinessDays(businessDays: Record<string, boolean>): CalendarEntity;
    static createGermanCalendar(tenantId?: string): CalendarEntity;
}
//# sourceMappingURL=calendar.d.ts.map