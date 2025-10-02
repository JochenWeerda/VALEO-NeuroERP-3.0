export interface AddressProps {
  readonly gln?: string;
  readonly name?: string;
  readonly street: string;
  readonly city: string;
  readonly postalCode: string;
  readonly country: string;
  readonly coordinates?: { lat: number; lon: number };
}

export class Address {
  private constructor(private readonly props: AddressProps) {}

  static create(props: AddressProps): Address {
    if (!props.street || !props.city || !props.postalCode || !props.country) {
      throw new Error('Invalid address: street, city, postalCode, and country are required');
    }
    if (props.coordinates) {
      const { lat, lon } = props.coordinates;
      if (Number.isNaN(lat) || Number.isNaN(lon)) {
        throw new Error('Invalid address coordinates: lat/lon must be numeric');
      }
      if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
        throw new Error('Invalid address coordinates: values out of range');
      }
    }
    return new Address({ ...props });
  }

  toJSON(): AddressProps {
    return { ...this.props };
  }
}

