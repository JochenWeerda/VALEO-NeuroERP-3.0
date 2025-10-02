import { z } from 'zod';
export declare const ContactSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    customerId: z.ZodString;
    firstName: z.ZodString;
    lastName: z.ZodString;
    role: z.ZodOptional<z.ZodString>;
    email: z.ZodString;
    phone: z.ZodOptional<z.ZodString>;
    isPrimary: z.ZodDefault<z.ZodBoolean>;
    notes: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodDate;
    updatedAt: z.ZodDate;
    version: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    id: string;
    tenantId: string;
    customerId: string;
    firstName: string;
    lastName: string;
    email: string;
    isPrimary: boolean;
    createdAt: Date;
    updatedAt: Date;
    version: number;
    role?: string | undefined;
    phone?: string | undefined;
    notes?: string | undefined;
}, {
    id: string;
    tenantId: string;
    customerId: string;
    firstName: string;
    lastName: string;
    email: string;
    createdAt: Date;
    updatedAt: Date;
    version: number;
    role?: string | undefined;
    phone?: string | undefined;
    isPrimary?: boolean | undefined;
    notes?: string | undefined;
}>;
export type Contact = z.infer<typeof ContactSchema>;
export declare const CreateContactInputSchema: z.ZodObject<Omit<{
    id: z.ZodString;
    tenantId: z.ZodString;
    customerId: z.ZodString;
    firstName: z.ZodString;
    lastName: z.ZodString;
    role: z.ZodOptional<z.ZodString>;
    email: z.ZodString;
    phone: z.ZodOptional<z.ZodString>;
    isPrimary: z.ZodDefault<z.ZodBoolean>;
    notes: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodDate;
    updatedAt: z.ZodDate;
    version: z.ZodNumber;
}, "id" | "createdAt" | "updatedAt" | "version">, "strip", z.ZodTypeAny, {
    tenantId: string;
    customerId: string;
    firstName: string;
    lastName: string;
    email: string;
    isPrimary: boolean;
    role?: string | undefined;
    phone?: string | undefined;
    notes?: string | undefined;
}, {
    tenantId: string;
    customerId: string;
    firstName: string;
    lastName: string;
    email: string;
    role?: string | undefined;
    phone?: string | undefined;
    isPrimary?: boolean | undefined;
    notes?: string | undefined;
}>;
export type CreateContactInput = z.infer<typeof CreateContactInputSchema>;
export declare const UpdateContactInputSchema: z.ZodObject<{
    firstName: z.ZodOptional<z.ZodString>;
    lastName: z.ZodOptional<z.ZodString>;
    role: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    email: z.ZodOptional<z.ZodString>;
    phone: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    isPrimary: z.ZodOptional<z.ZodBoolean>;
    notes: z.ZodOptional<z.ZodNullable<z.ZodString>>;
}, "strip", z.ZodTypeAny, {
    firstName?: string | undefined;
    lastName?: string | undefined;
    role?: string | null | undefined;
    email?: string | undefined;
    phone?: string | null | undefined;
    isPrimary?: boolean | undefined;
    notes?: string | null | undefined;
}, {
    firstName?: string | undefined;
    lastName?: string | undefined;
    role?: string | null | undefined;
    email?: string | undefined;
    phone?: string | null | undefined;
    isPrimary?: boolean | undefined;
    notes?: string | null | undefined;
}>;
export type UpdateContactInput = z.infer<typeof UpdateContactInputSchema>;
export declare class ContactEntity {
    private props;
    private constructor();
    static create(props: CreateContactInput & {
        tenantId: string;
    }): ContactEntity;
    static fromPersistence(props: Contact): ContactEntity;
    update(props: UpdateContactInput): void;
    makePrimary(): void;
    makeSecondary(): void;
    updateNotes(notes: string): void;
    get id(): string;
    get tenantId(): string;
    get customerId(): string;
    get firstName(): string;
    get lastName(): string;
    get fullName(): string;
    get role(): string | undefined;
    get email(): string;
    get phone(): string | undefined;
    get isPrimary(): boolean;
    get notes(): string | undefined;
    get createdAt(): Date;
    get updatedAt(): Date;
    get version(): number;
    toPersistence(): Contact;
    toJSON(): Omit<Contact, 'tenantId'>;
}
//# sourceMappingURL=contact.d.ts.map