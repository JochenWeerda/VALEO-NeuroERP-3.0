export declare function initEventPublisher(): Promise<void>;
export declare function publishEvent(eventType: string, payload: any): Promise<void>;
export declare function getEventPublisher(): {
    publish: typeof publishEvent;
};
export declare function closeEventPublisher(): Promise<void>;
//# sourceMappingURL=publisher.d.ts.map