export interface AddressProps {
    readonly gln?: string;
    readonly name?: string;
    readonly street: string;
    readonly city: string;
    readonly postalCode: string;
    readonly country: string;
    readonly coordinates?: {
        lat: number;
        lon: number;
    };
}
export declare class Address {
    private readonly props;
    private constructor();
    static create(props: AddressProps): Address;
    toJSON(): AddressProps;
}
//# sourceMappingURL=address.d.ts.map