export type DispatchStatus = 'assigned' | 'accepted' | 'in_progress' | 'completed' | 'reassigned';
export interface DispatchAssignmentProps {
    readonly assignmentId?: string;
    readonly tenantId: string;
    readonly routeId: string;
    readonly driverId: string;
    readonly vehicleId: string;
    readonly trailerId?: string;
    readonly status?: DispatchStatus;
    readonly assignedAt?: Date;
}
export declare class DispatchAssignment {
    readonly assignmentId: string;
    readonly tenantId: string;
    readonly routeId: string;
    readonly driverId: string;
    readonly vehicleId: string;
    readonly trailerId?: string;
    readonly assignedAt: Date;
    private _status;
    private constructor();
    static create(props: DispatchAssignmentProps): DispatchAssignment;
    get status(): DispatchStatus;
    updateStatus(status: DispatchStatus): void;
}
//# sourceMappingURL=dispatch-assignment.d.ts.map