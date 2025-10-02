import { nanoid } from 'nanoid';
import { TimeWindow } from '../value-objects/time-window';

export type YardStatus = 'scheduled' | 'checked_in' | 'at_dock' | 'checked_out' | 'no_show';

export interface YardVisitProps {
  readonly visitId?: string;
  readonly tenantId: string;
  readonly shipmentId: string;
  readonly gate: string;
  readonly dock?: string;
  readonly scheduledWindow?: { from: Date; to: Date };
  readonly status?: YardStatus;
  readonly checkinAt?: Date;
  readonly checkoutAt?: Date;
}

export class YardVisit {
  readonly visitId: string;
  readonly tenantId: string;
  readonly shipmentId: string;
  readonly gate: string;
  readonly dock?: string;
  readonly scheduledWindow?: TimeWindow;
  readonly checkinAt?: Date;
  readonly checkoutAt?: Date;
  private _status: YardStatus;

  private constructor(props: YardVisitProps) {
    this.visitId = props.visitId ?? `YARD-${nanoid(10)}`;
    this.tenantId = props.tenantId;
    this.shipmentId = props.shipmentId;
    this.gate = props.gate;
    this.dock = props.dock;
    this.scheduledWindow = props.scheduledWindow
      ? TimeWindow.create({ from: props.scheduledWindow.from, to: props.scheduledWindow.to })
      : undefined;
    this.checkinAt = props.checkinAt;
    this.checkoutAt = props.checkoutAt;
    this._status = props.status ?? 'scheduled';
  }

  static create(props: YardVisitProps): YardVisit {
    return new YardVisit(props);
  }

  get status(): YardStatus {
    return this._status;
  }

  updateStatus(status: YardStatus): void {
    this._status = status;
  }
}

