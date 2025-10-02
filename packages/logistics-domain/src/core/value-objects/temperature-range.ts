export interface TemperatureRangeProps {
  readonly minC: number;
  readonly maxC: number;
}

export class TemperatureRange {
  private constructor(private readonly props: TemperatureRangeProps) {}

  static create(props: TemperatureRangeProps): TemperatureRange {
    if (props.minC > props.maxC) {
      throw new Error('Invalid temperature range: min cannot exceed max');
    }
    return new TemperatureRange({ ...props });
  }

  contains(valueC: number): boolean {
    return valueC >= this.props.minC && valueC <= this.props.maxC;
  }

  toJSON(): TemperatureRangeProps {
    return { ...this.props };
  }
}

