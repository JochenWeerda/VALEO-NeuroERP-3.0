export type ScheduleStatus = 'Active' | 'Paused' | 'Disabled';
export type TriggerType = 'CRON' | 'RRULE' | 'FIXED_DELAY' | 'ONE_SHOT';
export type TargetType = 'EVENT' | 'HTTP' | 'QUEUE';
export interface Trigger {
    type: TriggerType;
    cron?: string;
    rrule?: string;
    delaySec?: number;
    startAt?: Date;
}
export interface Target {
    kind: TargetType;
    eventTopic?: string;
    http?: {
        url: string;
        method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
        headers?: Record<string, string>;
        hmacKeyRef?: string;
    };
    queue?: {
        topic: string;
    };
}
export interface CalendarConfig {
    holidaysCode?: string;
    businessDaysOnly?: boolean;
}
export declare class ScheduleEntity {
    readonly id: string;
    readonly tenantId: string;
    readonly name: string;
    readonly description?: string;
    readonly tz: string;
    readonly trigger: Trigger;
    readonly target: Target;
    readonly payload?: Record<string, any>;
    readonly calendar?: CalendarConfig;
    readonly enabled: boolean;
    readonly nextFireAt?: Date;
    readonly lastFireAt?: Date;
    readonly createdAt: Date;
    readonly updatedAt: Date;
    readonly version: number;
    constructor(props: {
        id?: string;
        tenantId: string;
        name: string;
        description?: string;
        tz: string;
        trigger: Trigger;
        target: Target;
        payload?: Record<string, any>;
        calendar?: CalendarConfig;
        enabled?: boolean;
        nextFireAt?: Date;
        lastFireAt?: Date;
        createdAt?: Date;
        updatedAt?: Date;
        version?: number;
    });
    private validate;
    private validateTrigger;
    private validateTarget;
    enable(): ScheduleEntity;
    disable(): ScheduleEntity;
    updateNextFire(nextFireAt: Date): ScheduleEntity;
    updateLastFire(lastFireAt: Date): ScheduleEntity;
    isDue(now?: Date): boolean;
    shouldFire(now?: Date): boolean;
    getDedupeKey(fireTime: Date): string;
}
//# sourceMappingURL=schedule.d.ts.map