import { z } from 'zod';
declare const TriggerSchema: z.ZodDiscriminatedUnion<"type", [z.ZodObject<{
    type: z.ZodLiteral<"CRON">;
    cron: z.ZodString;
}, "strip", z.ZodTypeAny, {
    type: "CRON";
    cron: string;
}, {
    type: "CRON";
    cron: string;
}>, z.ZodObject<{
    type: z.ZodLiteral<"RRULE">;
    rrule: z.ZodString;
}, "strip", z.ZodTypeAny, {
    type: "RRULE";
    rrule: string;
}, {
    type: "RRULE";
    rrule: string;
}>, z.ZodObject<{
    type: z.ZodLiteral<"FIXED_DELAY">;
    delaySec: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    type: "FIXED_DELAY";
    delaySec: number;
}, {
    type: "FIXED_DELAY";
    delaySec: number;
}>, z.ZodObject<{
    type: z.ZodLiteral<"ONE_SHOT">;
    startAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    type: "ONE_SHOT";
    startAt: string;
}, {
    type: "ONE_SHOT";
    startAt: string;
}>]>;
declare const TargetSchema: z.ZodDiscriminatedUnion<"kind", [z.ZodObject<{
    kind: z.ZodLiteral<"EVENT">;
    eventTopic: z.ZodString;
}, "strip", z.ZodTypeAny, {
    kind: "EVENT";
    eventTopic: string;
}, {
    kind: "EVENT";
    eventTopic: string;
}>, z.ZodObject<{
    kind: z.ZodLiteral<"HTTP">;
    http: z.ZodObject<{
        url: z.ZodString;
        method: z.ZodDefault<z.ZodEnum<["GET", "POST", "PUT", "PATCH", "DELETE"]>>;
        headers: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
        hmacKeyRef: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
        url: string;
        headers?: Record<string, string> | undefined;
        hmacKeyRef?: string | undefined;
    }, {
        url: string;
        method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
        headers?: Record<string, string> | undefined;
        hmacKeyRef?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    kind: "HTTP";
    http: {
        method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
        url: string;
        headers?: Record<string, string> | undefined;
        hmacKeyRef?: string | undefined;
    };
}, {
    kind: "HTTP";
    http: {
        url: string;
        method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
        headers?: Record<string, string> | undefined;
        hmacKeyRef?: string | undefined;
    };
}>, z.ZodObject<{
    kind: z.ZodLiteral<"QUEUE">;
    queue: z.ZodObject<{
        topic: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        topic: string;
    }, {
        topic: string;
    }>;
}, "strip", z.ZodTypeAny, {
    queue: {
        topic: string;
    };
    kind: "QUEUE";
}, {
    queue: {
        topic: string;
    };
    kind: "QUEUE";
}>]>;
declare const CalendarConfigSchema: z.ZodObject<{
    holidaysCode: z.ZodOptional<z.ZodString>;
    businessDaysOnly: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    businessDaysOnly: boolean;
    holidaysCode?: string | undefined;
}, {
    holidaysCode?: string | undefined;
    businessDaysOnly?: boolean | undefined;
}>;
declare const CreateScheduleInputSchema: z.ZodObject<{
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    tz: z.ZodDefault<z.ZodString>;
    trigger: z.ZodDiscriminatedUnion<"type", [z.ZodObject<{
        type: z.ZodLiteral<"CRON">;
        cron: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "CRON";
        cron: string;
    }, {
        type: "CRON";
        cron: string;
    }>, z.ZodObject<{
        type: z.ZodLiteral<"RRULE">;
        rrule: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "RRULE";
        rrule: string;
    }, {
        type: "RRULE";
        rrule: string;
    }>, z.ZodObject<{
        type: z.ZodLiteral<"FIXED_DELAY">;
        delaySec: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        type: "FIXED_DELAY";
        delaySec: number;
    }, {
        type: "FIXED_DELAY";
        delaySec: number;
    }>, z.ZodObject<{
        type: z.ZodLiteral<"ONE_SHOT">;
        startAt: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "ONE_SHOT";
        startAt: string;
    }, {
        type: "ONE_SHOT";
        startAt: string;
    }>]>;
    target: z.ZodDiscriminatedUnion<"kind", [z.ZodObject<{
        kind: z.ZodLiteral<"EVENT">;
        eventTopic: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        kind: "EVENT";
        eventTopic: string;
    }, {
        kind: "EVENT";
        eventTopic: string;
    }>, z.ZodObject<{
        kind: z.ZodLiteral<"HTTP">;
        http: z.ZodObject<{
            url: z.ZodString;
            method: z.ZodDefault<z.ZodEnum<["GET", "POST", "PUT", "PATCH", "DELETE"]>>;
            headers: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
            hmacKeyRef: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
            url: string;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        }, {
            url: string;
            method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        }>;
    }, "strip", z.ZodTypeAny, {
        kind: "HTTP";
        http: {
            method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
            url: string;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        };
    }, {
        kind: "HTTP";
        http: {
            url: string;
            method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        };
    }>, z.ZodObject<{
        kind: z.ZodLiteral<"QUEUE">;
        queue: z.ZodObject<{
            topic: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            topic: string;
        }, {
            topic: string;
        }>;
    }, "strip", z.ZodTypeAny, {
        queue: {
            topic: string;
        };
        kind: "QUEUE";
    }, {
        queue: {
            topic: string;
        };
        kind: "QUEUE";
    }>]>;
    payload: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
    calendar: z.ZodOptional<z.ZodObject<{
        holidaysCode: z.ZodOptional<z.ZodString>;
        businessDaysOnly: z.ZodDefault<z.ZodBoolean>;
    }, "strip", z.ZodTypeAny, {
        businessDaysOnly: boolean;
        holidaysCode?: string | undefined;
    }, {
        holidaysCode?: string | undefined;
        businessDaysOnly?: boolean | undefined;
    }>>;
    enabled: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    name: string;
    tz: string;
    enabled: boolean;
    trigger: {
        type: "CRON";
        cron: string;
    } | {
        type: "RRULE";
        rrule: string;
    } | {
        type: "FIXED_DELAY";
        delaySec: number;
    } | {
        type: "ONE_SHOT";
        startAt: string;
    };
    target: {
        kind: "EVENT";
        eventTopic: string;
    } | {
        kind: "HTTP";
        http: {
            method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
            url: string;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        };
    } | {
        queue: {
            topic: string;
        };
        kind: "QUEUE";
    };
    description?: string | undefined;
    payload?: Record<string, any> | undefined;
    calendar?: {
        businessDaysOnly: boolean;
        holidaysCode?: string | undefined;
    } | undefined;
}, {
    name: string;
    trigger: {
        type: "CRON";
        cron: string;
    } | {
        type: "RRULE";
        rrule: string;
    } | {
        type: "FIXED_DELAY";
        delaySec: number;
    } | {
        type: "ONE_SHOT";
        startAt: string;
    };
    target: {
        kind: "EVENT";
        eventTopic: string;
    } | {
        kind: "HTTP";
        http: {
            url: string;
            method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        };
    } | {
        queue: {
            topic: string;
        };
        kind: "QUEUE";
    };
    description?: string | undefined;
    tz?: string | undefined;
    payload?: Record<string, any> | undefined;
    enabled?: boolean | undefined;
    calendar?: {
        holidaysCode?: string | undefined;
        businessDaysOnly?: boolean | undefined;
    } | undefined;
}>;
declare const UpdateScheduleInputSchema: z.ZodObject<{
    name: z.ZodOptional<z.ZodString>;
    description: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    tz: z.ZodOptional<z.ZodString>;
    trigger: z.ZodOptional<z.ZodDiscriminatedUnion<"type", [z.ZodObject<{
        type: z.ZodLiteral<"CRON">;
        cron: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "CRON";
        cron: string;
    }, {
        type: "CRON";
        cron: string;
    }>, z.ZodObject<{
        type: z.ZodLiteral<"RRULE">;
        rrule: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "RRULE";
        rrule: string;
    }, {
        type: "RRULE";
        rrule: string;
    }>, z.ZodObject<{
        type: z.ZodLiteral<"FIXED_DELAY">;
        delaySec: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        type: "FIXED_DELAY";
        delaySec: number;
    }, {
        type: "FIXED_DELAY";
        delaySec: number;
    }>, z.ZodObject<{
        type: z.ZodLiteral<"ONE_SHOT">;
        startAt: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "ONE_SHOT";
        startAt: string;
    }, {
        type: "ONE_SHOT";
        startAt: string;
    }>]>>;
    target: z.ZodOptional<z.ZodDiscriminatedUnion<"kind", [z.ZodObject<{
        kind: z.ZodLiteral<"EVENT">;
        eventTopic: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        kind: "EVENT";
        eventTopic: string;
    }, {
        kind: "EVENT";
        eventTopic: string;
    }>, z.ZodObject<{
        kind: z.ZodLiteral<"HTTP">;
        http: z.ZodObject<{
            url: z.ZodString;
            method: z.ZodDefault<z.ZodEnum<["GET", "POST", "PUT", "PATCH", "DELETE"]>>;
            headers: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
            hmacKeyRef: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
            url: string;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        }, {
            url: string;
            method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        }>;
    }, "strip", z.ZodTypeAny, {
        kind: "HTTP";
        http: {
            method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
            url: string;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        };
    }, {
        kind: "HTTP";
        http: {
            url: string;
            method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        };
    }>, z.ZodObject<{
        kind: z.ZodLiteral<"QUEUE">;
        queue: z.ZodObject<{
            topic: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            topic: string;
        }, {
            topic: string;
        }>;
    }, "strip", z.ZodTypeAny, {
        queue: {
            topic: string;
        };
        kind: "QUEUE";
    }, {
        queue: {
            topic: string;
        };
        kind: "QUEUE";
    }>]>>;
    payload: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
    calendar: z.ZodOptional<z.ZodObject<{
        holidaysCode: z.ZodOptional<z.ZodString>;
        businessDaysOnly: z.ZodDefault<z.ZodBoolean>;
    }, "strip", z.ZodTypeAny, {
        businessDaysOnly: boolean;
        holidaysCode?: string | undefined;
    }, {
        holidaysCode?: string | undefined;
        businessDaysOnly?: boolean | undefined;
    }>>;
    enabled: z.ZodOptional<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    name?: string | undefined;
    description?: string | null | undefined;
    tz?: string | undefined;
    payload?: Record<string, any> | undefined;
    enabled?: boolean | undefined;
    trigger?: {
        type: "CRON";
        cron: string;
    } | {
        type: "RRULE";
        rrule: string;
    } | {
        type: "FIXED_DELAY";
        delaySec: number;
    } | {
        type: "ONE_SHOT";
        startAt: string;
    } | undefined;
    target?: {
        kind: "EVENT";
        eventTopic: string;
    } | {
        kind: "HTTP";
        http: {
            method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
            url: string;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        };
    } | {
        queue: {
            topic: string;
        };
        kind: "QUEUE";
    } | undefined;
    calendar?: {
        businessDaysOnly: boolean;
        holidaysCode?: string | undefined;
    } | undefined;
}, {
    name?: string | undefined;
    description?: string | null | undefined;
    tz?: string | undefined;
    payload?: Record<string, any> | undefined;
    enabled?: boolean | undefined;
    trigger?: {
        type: "CRON";
        cron: string;
    } | {
        type: "RRULE";
        rrule: string;
    } | {
        type: "FIXED_DELAY";
        delaySec: number;
    } | {
        type: "ONE_SHOT";
        startAt: string;
    } | undefined;
    target?: {
        kind: "EVENT";
        eventTopic: string;
    } | {
        kind: "HTTP";
        http: {
            url: string;
            method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        };
    } | {
        queue: {
            topic: string;
        };
        kind: "QUEUE";
    } | undefined;
    calendar?: {
        holidaysCode?: string | undefined;
        businessDaysOnly?: boolean | undefined;
    } | undefined;
}>;
declare const ScheduleQuerySchema: z.ZodObject<{
    enabled: z.ZodOptional<z.ZodEffects<z.ZodString, boolean, string>>;
    name: z.ZodOptional<z.ZodString>;
    tz: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodEffects<z.ZodString, number, string>>;
    pageSize: z.ZodDefault<z.ZodEffects<z.ZodString, number, string>>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    name?: string | undefined;
    tz?: string | undefined;
    enabled?: boolean | undefined;
}, {
    name?: string | undefined;
    tz?: string | undefined;
    enabled?: string | undefined;
    page?: string | undefined;
    pageSize?: string | undefined;
}>;
declare const ScheduleResponseSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    name: z.ZodString;
    description: z.ZodNullable<z.ZodString>;
    tz: z.ZodString;
    trigger: z.ZodDiscriminatedUnion<"type", [z.ZodObject<{
        type: z.ZodLiteral<"CRON">;
        cron: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "CRON";
        cron: string;
    }, {
        type: "CRON";
        cron: string;
    }>, z.ZodObject<{
        type: z.ZodLiteral<"RRULE">;
        rrule: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "RRULE";
        rrule: string;
    }, {
        type: "RRULE";
        rrule: string;
    }>, z.ZodObject<{
        type: z.ZodLiteral<"FIXED_DELAY">;
        delaySec: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        type: "FIXED_DELAY";
        delaySec: number;
    }, {
        type: "FIXED_DELAY";
        delaySec: number;
    }>, z.ZodObject<{
        type: z.ZodLiteral<"ONE_SHOT">;
        startAt: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "ONE_SHOT";
        startAt: string;
    }, {
        type: "ONE_SHOT";
        startAt: string;
    }>]>;
    target: z.ZodDiscriminatedUnion<"kind", [z.ZodObject<{
        kind: z.ZodLiteral<"EVENT">;
        eventTopic: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        kind: "EVENT";
        eventTopic: string;
    }, {
        kind: "EVENT";
        eventTopic: string;
    }>, z.ZodObject<{
        kind: z.ZodLiteral<"HTTP">;
        http: z.ZodObject<{
            url: z.ZodString;
            method: z.ZodDefault<z.ZodEnum<["GET", "POST", "PUT", "PATCH", "DELETE"]>>;
            headers: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
            hmacKeyRef: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
            url: string;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        }, {
            url: string;
            method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        }>;
    }, "strip", z.ZodTypeAny, {
        kind: "HTTP";
        http: {
            method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
            url: string;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        };
    }, {
        kind: "HTTP";
        http: {
            url: string;
            method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        };
    }>, z.ZodObject<{
        kind: z.ZodLiteral<"QUEUE">;
        queue: z.ZodObject<{
            topic: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            topic: string;
        }, {
            topic: string;
        }>;
    }, "strip", z.ZodTypeAny, {
        queue: {
            topic: string;
        };
        kind: "QUEUE";
    }, {
        queue: {
            topic: string;
        };
        kind: "QUEUE";
    }>]>;
    payload: z.ZodNullable<z.ZodRecord<z.ZodString, z.ZodAny>>;
    calendar: z.ZodNullable<z.ZodObject<{
        holidaysCode: z.ZodOptional<z.ZodString>;
        businessDaysOnly: z.ZodDefault<z.ZodBoolean>;
    }, "strip", z.ZodTypeAny, {
        businessDaysOnly: boolean;
        holidaysCode?: string | undefined;
    }, {
        holidaysCode?: string | undefined;
        businessDaysOnly?: boolean | undefined;
    }>>;
    enabled: z.ZodBoolean;
    nextFireAt: z.ZodNullable<z.ZodString>;
    lastFireAt: z.ZodNullable<z.ZodString>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    version: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    id: string;
    name: string;
    tenantId: string;
    description: string | null;
    tz: string;
    payload: Record<string, any> | null;
    enabled: boolean;
    nextFireAt: string | null;
    lastFireAt: string | null;
    version: number;
    createdAt: string;
    updatedAt: string;
    trigger: {
        type: "CRON";
        cron: string;
    } | {
        type: "RRULE";
        rrule: string;
    } | {
        type: "FIXED_DELAY";
        delaySec: number;
    } | {
        type: "ONE_SHOT";
        startAt: string;
    };
    target: {
        kind: "EVENT";
        eventTopic: string;
    } | {
        kind: "HTTP";
        http: {
            method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
            url: string;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        };
    } | {
        queue: {
            topic: string;
        };
        kind: "QUEUE";
    };
    calendar: {
        businessDaysOnly: boolean;
        holidaysCode?: string | undefined;
    } | null;
}, {
    id: string;
    name: string;
    tenantId: string;
    description: string | null;
    tz: string;
    payload: Record<string, any> | null;
    enabled: boolean;
    nextFireAt: string | null;
    lastFireAt: string | null;
    version: number;
    createdAt: string;
    updatedAt: string;
    trigger: {
        type: "CRON";
        cron: string;
    } | {
        type: "RRULE";
        rrule: string;
    } | {
        type: "FIXED_DELAY";
        delaySec: number;
    } | {
        type: "ONE_SHOT";
        startAt: string;
    };
    target: {
        kind: "EVENT";
        eventTopic: string;
    } | {
        kind: "HTTP";
        http: {
            url: string;
            method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
            headers?: Record<string, string> | undefined;
            hmacKeyRef?: string | undefined;
        };
    } | {
        queue: {
            topic: string;
        };
        kind: "QUEUE";
    };
    calendar: {
        holidaysCode?: string | undefined;
        businessDaysOnly?: boolean | undefined;
    } | null;
}>;
declare const ScheduleListResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        tenantId: z.ZodString;
        name: z.ZodString;
        description: z.ZodNullable<z.ZodString>;
        tz: z.ZodString;
        trigger: z.ZodDiscriminatedUnion<"type", [z.ZodObject<{
            type: z.ZodLiteral<"CRON">;
            cron: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            type: "CRON";
            cron: string;
        }, {
            type: "CRON";
            cron: string;
        }>, z.ZodObject<{
            type: z.ZodLiteral<"RRULE">;
            rrule: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            type: "RRULE";
            rrule: string;
        }, {
            type: "RRULE";
            rrule: string;
        }>, z.ZodObject<{
            type: z.ZodLiteral<"FIXED_DELAY">;
            delaySec: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            type: "FIXED_DELAY";
            delaySec: number;
        }, {
            type: "FIXED_DELAY";
            delaySec: number;
        }>, z.ZodObject<{
            type: z.ZodLiteral<"ONE_SHOT">;
            startAt: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            type: "ONE_SHOT";
            startAt: string;
        }, {
            type: "ONE_SHOT";
            startAt: string;
        }>]>;
        target: z.ZodDiscriminatedUnion<"kind", [z.ZodObject<{
            kind: z.ZodLiteral<"EVENT">;
            eventTopic: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            kind: "EVENT";
            eventTopic: string;
        }, {
            kind: "EVENT";
            eventTopic: string;
        }>, z.ZodObject<{
            kind: z.ZodLiteral<"HTTP">;
            http: z.ZodObject<{
                url: z.ZodString;
                method: z.ZodDefault<z.ZodEnum<["GET", "POST", "PUT", "PATCH", "DELETE"]>>;
                headers: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
                hmacKeyRef: z.ZodOptional<z.ZodString>;
            }, "strip", z.ZodTypeAny, {
                method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
                url: string;
                headers?: Record<string, string> | undefined;
                hmacKeyRef?: string | undefined;
            }, {
                url: string;
                method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
                headers?: Record<string, string> | undefined;
                hmacKeyRef?: string | undefined;
            }>;
        }, "strip", z.ZodTypeAny, {
            kind: "HTTP";
            http: {
                method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
                url: string;
                headers?: Record<string, string> | undefined;
                hmacKeyRef?: string | undefined;
            };
        }, {
            kind: "HTTP";
            http: {
                url: string;
                method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
                headers?: Record<string, string> | undefined;
                hmacKeyRef?: string | undefined;
            };
        }>, z.ZodObject<{
            kind: z.ZodLiteral<"QUEUE">;
            queue: z.ZodObject<{
                topic: z.ZodString;
            }, "strip", z.ZodTypeAny, {
                topic: string;
            }, {
                topic: string;
            }>;
        }, "strip", z.ZodTypeAny, {
            queue: {
                topic: string;
            };
            kind: "QUEUE";
        }, {
            queue: {
                topic: string;
            };
            kind: "QUEUE";
        }>]>;
        payload: z.ZodNullable<z.ZodRecord<z.ZodString, z.ZodAny>>;
        calendar: z.ZodNullable<z.ZodObject<{
            holidaysCode: z.ZodOptional<z.ZodString>;
            businessDaysOnly: z.ZodDefault<z.ZodBoolean>;
        }, "strip", z.ZodTypeAny, {
            businessDaysOnly: boolean;
            holidaysCode?: string | undefined;
        }, {
            holidaysCode?: string | undefined;
            businessDaysOnly?: boolean | undefined;
        }>>;
        enabled: z.ZodBoolean;
        nextFireAt: z.ZodNullable<z.ZodString>;
        lastFireAt: z.ZodNullable<z.ZodString>;
        createdAt: z.ZodString;
        updatedAt: z.ZodString;
        version: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        id: string;
        name: string;
        tenantId: string;
        description: string | null;
        tz: string;
        payload: Record<string, any> | null;
        enabled: boolean;
        nextFireAt: string | null;
        lastFireAt: string | null;
        version: number;
        createdAt: string;
        updatedAt: string;
        trigger: {
            type: "CRON";
            cron: string;
        } | {
            type: "RRULE";
            rrule: string;
        } | {
            type: "FIXED_DELAY";
            delaySec: number;
        } | {
            type: "ONE_SHOT";
            startAt: string;
        };
        target: {
            kind: "EVENT";
            eventTopic: string;
        } | {
            kind: "HTTP";
            http: {
                method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
                url: string;
                headers?: Record<string, string> | undefined;
                hmacKeyRef?: string | undefined;
            };
        } | {
            queue: {
                topic: string;
            };
            kind: "QUEUE";
        };
        calendar: {
            businessDaysOnly: boolean;
            holidaysCode?: string | undefined;
        } | null;
    }, {
        id: string;
        name: string;
        tenantId: string;
        description: string | null;
        tz: string;
        payload: Record<string, any> | null;
        enabled: boolean;
        nextFireAt: string | null;
        lastFireAt: string | null;
        version: number;
        createdAt: string;
        updatedAt: string;
        trigger: {
            type: "CRON";
            cron: string;
        } | {
            type: "RRULE";
            rrule: string;
        } | {
            type: "FIXED_DELAY";
            delaySec: number;
        } | {
            type: "ONE_SHOT";
            startAt: string;
        };
        target: {
            kind: "EVENT";
            eventTopic: string;
        } | {
            kind: "HTTP";
            http: {
                url: string;
                method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
                headers?: Record<string, string> | undefined;
                hmacKeyRef?: string | undefined;
            };
        } | {
            queue: {
                topic: string;
            };
            kind: "QUEUE";
        };
        calendar: {
            holidaysCode?: string | undefined;
            businessDaysOnly?: boolean | undefined;
        } | null;
    }>, "many">;
    pagination: z.ZodObject<{
        page: z.ZodNumber;
        pageSize: z.ZodNumber;
        total: z.ZodNumber;
        totalPages: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    }, {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    }>;
}, "strip", z.ZodTypeAny, {
    data: {
        id: string;
        name: string;
        tenantId: string;
        description: string | null;
        tz: string;
        payload: Record<string, any> | null;
        enabled: boolean;
        nextFireAt: string | null;
        lastFireAt: string | null;
        version: number;
        createdAt: string;
        updatedAt: string;
        trigger: {
            type: "CRON";
            cron: string;
        } | {
            type: "RRULE";
            rrule: string;
        } | {
            type: "FIXED_DELAY";
            delaySec: number;
        } | {
            type: "ONE_SHOT";
            startAt: string;
        };
        target: {
            kind: "EVENT";
            eventTopic: string;
        } | {
            kind: "HTTP";
            http: {
                method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
                url: string;
                headers?: Record<string, string> | undefined;
                hmacKeyRef?: string | undefined;
            };
        } | {
            queue: {
                topic: string;
            };
            kind: "QUEUE";
        };
        calendar: {
            businessDaysOnly: boolean;
            holidaysCode?: string | undefined;
        } | null;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}, {
    data: {
        id: string;
        name: string;
        tenantId: string;
        description: string | null;
        tz: string;
        payload: Record<string, any> | null;
        enabled: boolean;
        nextFireAt: string | null;
        lastFireAt: string | null;
        version: number;
        createdAt: string;
        updatedAt: string;
        trigger: {
            type: "CRON";
            cron: string;
        } | {
            type: "RRULE";
            rrule: string;
        } | {
            type: "FIXED_DELAY";
            delaySec: number;
        } | {
            type: "ONE_SHOT";
            startAt: string;
        };
        target: {
            kind: "EVENT";
            eventTopic: string;
        } | {
            kind: "HTTP";
            http: {
                url: string;
                method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | undefined;
                headers?: Record<string, string> | undefined;
                hmacKeyRef?: string | undefined;
            };
        } | {
            queue: {
                topic: string;
            };
            kind: "QUEUE";
        };
        calendar: {
            holidaysCode?: string | undefined;
            businessDaysOnly?: boolean | undefined;
        } | null;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}>;
declare const ManualTriggerInputSchema: z.ZodObject<{
    fireTime: z.ZodOptional<z.ZodString>;
    payload: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
}, "strip", z.ZodTypeAny, {
    payload?: Record<string, any> | undefined;
    fireTime?: string | undefined;
}, {
    payload?: Record<string, any> | undefined;
    fireTime?: string | undefined;
}>;
declare const BackfillInputSchema: z.ZodObject<{
    from: z.ZodString;
    to: z.ZodString;
    step: z.ZodString;
    maxRuns: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    from: string;
    to: string;
    step: string;
    maxRuns?: number | undefined;
}, {
    from: string;
    to: string;
    step: string;
    maxRuns?: number | undefined;
}>;
export { CreateScheduleInputSchema, UpdateScheduleInputSchema, ScheduleQuerySchema, ScheduleResponseSchema, ScheduleListResponseSchema, ManualTriggerInputSchema, BackfillInputSchema, TriggerSchema, TargetSchema, CalendarConfigSchema, };
//# sourceMappingURL=schedule-contracts.d.ts.map