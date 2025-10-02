export interface TimeWindowProps {
  readonly from: Date;
  readonly to: Date;
}

export class TimeWindow {
  private constructor(private readonly props: TimeWindowProps) {}

  static create(props: TimeWindowProps): TimeWindow {
    if (props.from >= props.to) {
      throw new Error('Invalid time window: from must be before to');
    }
    return new TimeWindow({ ...props });
  }

  get from(): Date {
    return new Date(this.props.from);
  }

  get to(): Date {
    return new Date(this.props.to);
  }

  durationMinutes(): number {
    return Math.round((this.props.to.getTime() - this.props.from.getTime()) / 60000);
  }

  toJSON(): { from: string; to: string } {
    return {
      from: this.props.from.toISOString(),
      to: this.props.to.toISOString(),
    };
  }
}

