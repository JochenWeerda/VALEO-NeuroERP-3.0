import { z } from 'zod';
export declare const InteractionType: {
    readonly CALL: "Call";
    readonly EMAIL: "Email";
    readonly VISIT: "Visit";
    readonly NOTE: "Note";
};
export type InteractionTypeType = typeof InteractionType[keyof typeof InteractionType];
export declare const InteractionSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    customerId: z.ZodString;
    contactId: z.ZodOptional<z.ZodString>;
    type: z.ZodEnum<["Call", "Email", "Visit", "Note"]>;
    subject: z.ZodString;
    content: z.ZodString;
    occurredAt: z.ZodDate;
    createdBy: z.ZodString;
    attachments: z.ZodDefault<z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        filename: z.ZodString;
        url: z.ZodString;
        size: z.ZodNumber;
        mimeType: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        id: string;
        url: string;
        filename: string;
        size: number;
        mimeType: string;
    }, {
        id: string;
        url: string;
        filename: string;
        size: number;
        mimeType: string;
    }>, "many">>;
    createdAt: z.ZodDate;
    updatedAt: z.ZodDate;
    version: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    id: string;
    tenantId: string;
    customerId: string;
    createdAt: Date;
    updatedAt: Date;
    version: number;
    type: "Email" | "Call" | "Visit" | "Note";
    content: string;
    subject: string;
    occurredAt: Date;
    createdBy: string;
    attachments: {
        id: string;
        url: string;
        filename: string;
        size: number;
        mimeType: string;
    }[];
    contactId?: string | undefined;
}, {
    id: string;
    tenantId: string;
    customerId: string;
    createdAt: Date;
    updatedAt: Date;
    version: number;
    type: "Email" | "Call" | "Visit" | "Note";
    content: string;
    subject: string;
    occurredAt: Date;
    createdBy: string;
    contactId?: string | undefined;
    attachments?: {
        id: string;
        url: string;
        filename: string;
        size: number;
        mimeType: string;
    }[] | undefined;
}>;
export type Interaction = z.infer<typeof InteractionSchema>;
export declare const CreateInteractionInputSchema: z.ZodObject<Omit<{
    id: z.ZodString;
    tenantId: z.ZodString;
    customerId: z.ZodString;
    contactId: z.ZodOptional<z.ZodString>;
    type: z.ZodEnum<["Call", "Email", "Visit", "Note"]>;
    subject: z.ZodString;
    content: z.ZodString;
    occurredAt: z.ZodDate;
    createdBy: z.ZodString;
    attachments: z.ZodDefault<z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        filename: z.ZodString;
        url: z.ZodString;
        size: z.ZodNumber;
        mimeType: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        id: string;
        url: string;
        filename: string;
        size: number;
        mimeType: string;
    }, {
        id: string;
        url: string;
        filename: string;
        size: number;
        mimeType: string;
    }>, "many">>;
    createdAt: z.ZodDate;
    updatedAt: z.ZodDate;
    version: z.ZodNumber;
}, "id" | "createdAt" | "updatedAt" | "version">, "strip", z.ZodTypeAny, {
    tenantId: string;
    customerId: string;
    type: "Email" | "Call" | "Visit" | "Note";
    content: string;
    subject: string;
    occurredAt: Date;
    createdBy: string;
    attachments: {
        id: string;
        url: string;
        filename: string;
        size: number;
        mimeType: string;
    }[];
    contactId?: string | undefined;
}, {
    tenantId: string;
    customerId: string;
    type: "Email" | "Call" | "Visit" | "Note";
    content: string;
    subject: string;
    occurredAt: Date;
    createdBy: string;
    contactId?: string | undefined;
    attachments?: {
        id: string;
        url: string;
        filename: string;
        size: number;
        mimeType: string;
    }[] | undefined;
}>;
export type CreateInteractionInput = z.infer<typeof CreateInteractionInputSchema>;
export declare const UpdateInteractionInputSchema: z.ZodObject<{
    subject: z.ZodOptional<z.ZodString>;
    content: z.ZodOptional<z.ZodString>;
    occurredAt: z.ZodOptional<z.ZodDate>;
    attachments: z.ZodOptional<z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        filename: z.ZodString;
        url: z.ZodString;
        size: z.ZodNumber;
        mimeType: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        id: string;
        url: string;
        filename: string;
        size: number;
        mimeType: string;
    }, {
        id: string;
        url: string;
        filename: string;
        size: number;
        mimeType: string;
    }>, "many">>;
}, "strip", z.ZodTypeAny, {
    content?: string | undefined;
    subject?: string | undefined;
    occurredAt?: Date | undefined;
    attachments?: {
        id: string;
        url: string;
        filename: string;
        size: number;
        mimeType: string;
    }[] | undefined;
}, {
    content?: string | undefined;
    subject?: string | undefined;
    occurredAt?: Date | undefined;
    attachments?: {
        id: string;
        url: string;
        filename: string;
        size: number;
        mimeType: string;
    }[] | undefined;
}>;
export type UpdateInteractionInput = z.infer<typeof UpdateInteractionInputSchema>;
export declare const AttachmentSchema: z.ZodObject<{
    id: z.ZodString;
    filename: z.ZodString;
    url: z.ZodString;
    size: z.ZodNumber;
    mimeType: z.ZodString;
}, "strip", z.ZodTypeAny, {
    id: string;
    url: string;
    filename: string;
    size: number;
    mimeType: string;
}, {
    id: string;
    url: string;
    filename: string;
    size: number;
    mimeType: string;
}>;
export type Attachment = z.infer<typeof AttachmentSchema>;
export declare class InteractionEntity {
    private props;
    private constructor();
    static create(props: CreateInteractionInput & {
        tenantId: string;
    }): InteractionEntity;
    static fromPersistence(props: Interaction): InteractionEntity;
    update(props: UpdateInteractionInput): void;
    addAttachment(attachment: Omit<Attachment, 'id'>): void;
    removeAttachment(attachmentId: string): void;
    updateContent(subject: string, content: string): void;
    reschedule(occurredAt: Date): void;
    isOverdue(): boolean;
    isToday(): boolean;
    isUpcoming(): boolean;
    get id(): string;
    get tenantId(): string;
    get customerId(): string;
    get contactId(): string | undefined;
    get type(): InteractionTypeType;
    get subject(): string;
    get content(): string;
    get occurredAt(): Date;
    get createdBy(): string;
    get attachments(): Attachment[];
    get createdAt(): Date;
    get updatedAt(): Date;
    get version(): number;
    toPersistence(): Interaction;
    toJSON(): Omit<Interaction, 'tenantId'>;
}
//# sourceMappingURL=interaction.d.ts.map