import { nanoid } from 'nanoid';

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

export class DispatchAssignment {
  readonly assignmentId: string;
  readonly tenantId: string;
  readonly routeId: string;
  readonly driverId: string;
  readonly vehicleId: string;
  readonly trailerId?: string;
  readonly assignedAt: Date;
  private _status: DispatchStatus;

  private constructor(props: DispatchAssignmentProps) {
    this.assignmentId = props.assignmentId ?? `ASSIGN-${nanoid(10)}`;
    this.tenantId = props.tenantId;
    this.routeId = props.routeId;
    this.driverId = props.driverId;
    this.vehicleId = props.vehicleId;
    this.trailerId = props.trailerId;
    this.assignedAt = props.assignedAt ?? new Date();
    this._status = props.status ?? 'assigned';
  }

  static create(props: DispatchAssignmentProps): DispatchAssignment {
    return new DispatchAssignment(props);
  }

  get status(): DispatchStatus {
    return this._status;
  }

  updateStatus(status: DispatchStatus): void {
    this._status = status;
  }
}

