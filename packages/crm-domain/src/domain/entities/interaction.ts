import { z } from 'zod';
import { v4 as uuidv4 } from 'uuid';

// Enums
export const InteractionType = {
  CALL: 'Call',
  EMAIL: 'Email',
  VISIT: 'Visit',
  NOTE: 'Note'
} as const;

export type InteractionTypeType = typeof InteractionType[keyof typeof InteractionType];

// Interaction Entity Schema
export const InteractionSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  customerId: z.string().uuid(),
  contactId: z.string().uuid().optional(),
  type: z.enum([
    InteractionType.CALL,
    InteractionType.EMAIL,
    InteractionType.VISIT,
    InteractionType.NOTE
  ]),
  subject: z.string().min(1),
  content: z.string().min(1),
  occurredAt: z.date(),
  createdBy: z.string().uuid(),
  attachments: z.array(z.object({
    id: z.string().uuid(),
    filename: z.string(),
    url: z.string().url(),
    size: z.number().nonnegative(),
    mimeType: z.string()
  })).default([]),
  createdAt: z.date(),
  updatedAt: z.date(),
  version: z.number().int().nonnegative()
});

export type Interaction = z.infer<typeof InteractionSchema>;

// Create Interaction Input Schema (for API)
export const CreateInteractionInputSchema = InteractionSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  version: true
});

export type CreateInteractionInput = z.infer<typeof CreateInteractionInputSchema>;

// Update Interaction Input Schema (for API)
export const UpdateInteractionInputSchema = z.object({
  subject: z.string().min(1).optional(),
  content: z.string().min(1).optional(),
  occurredAt: z.date().optional(),
  attachments: z.array(z.object({
    id: z.string().uuid(),
    filename: z.string(),
    url: z.string().url(),
    size: z.number().nonnegative(),
    mimeType: z.string()
  })).optional()
});

export type UpdateInteractionInput = z.infer<typeof UpdateInteractionInputSchema>;

// Attachment Schema for API responses
export const AttachmentSchema = z.object({
  id: z.string().uuid(),
  filename: z.string(),
  url: z.string().url(),
  size: z.number().nonnegative(),
  mimeType: z.string()
});

export type Attachment = z.infer<typeof AttachmentSchema>;

// Interaction Aggregate Root
export class InteractionEntity {
  private constructor(private props: Interaction) {}

  public static create(props: CreateInteractionInput & { tenantId: string }): InteractionEntity {
    const now = new Date();
    const interaction: Interaction = {
      ...props,
      id: uuidv4(),
      attachments: props.attachments ?? [],
      createdAt: now,
      updatedAt: now,
      version: 1
    };

    return new InteractionEntity(interaction);
  }

  public static fromPersistence(props: any): InteractionEntity {
    return new InteractionEntity({
      ...props,
      contactId: props.contactId ?? undefined,
    });
  }

  public update(props: UpdateInteractionInput): void {
    if (props.subject !== undefined) {
      this.props.subject = props.subject;
    }
    if (props.content !== undefined) {
      this.props.content = props.content;
    }
    if (props.occurredAt !== undefined) {
      this.props.occurredAt = props.occurredAt;
    }
    if (props.attachments !== undefined) {
      this.props.attachments = props.attachments;
    }

    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public addAttachment(attachment: Omit<Attachment, 'id'>): void {
    const newAttachment: Attachment = {
      ...attachment,
      id: uuidv4()
    };
    this.props.attachments.push(newAttachment);
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public removeAttachment(attachmentId: string): void {
    const index = this.props.attachments.findIndex(att => att.id === attachmentId);
    if (index > -1) {
      this.props.attachments.splice(index, 1);
      this.props.updatedAt = new Date();
      this.props.version += 1;
    }
  }

  public updateContent(subject: string, content: string): void {
    this.props.subject = subject;
    this.props.content = content;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public reschedule(occurredAt: Date): void {
    this.props.occurredAt = occurredAt;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  // Business logic methods
  public isOverdue(): boolean {
    return this.props.occurredAt < new Date();
  }

  public isToday(): boolean {
    const today = new Date();
    const interactionDate = new Date(this.props.occurredAt);
    return (
      today.getDate() === interactionDate.getDate() &&
      today.getMonth() === interactionDate.getMonth() &&
      today.getFullYear() === interactionDate.getFullYear()
    );
  }

  public isUpcoming(): boolean {
    return this.props.occurredAt > new Date();
  }

  // Getters
  public get id(): string { return this.props.id; }
  public get tenantId(): string { return this.props.tenantId; }
  public get customerId(): string { return this.props.customerId; }
  public get contactId(): string | undefined { return this.props.contactId; }
  public get type(): InteractionTypeType { return this.props.type; }
  public get subject(): string { return this.props.subject; }
  public get content(): string { return this.props.content; }
  public get occurredAt(): Date { return this.props.occurredAt; }
  public get createdBy(): string { return this.props.createdBy; }
  public get attachments(): Attachment[] { return [...this.props.attachments]; }
  public get createdAt(): Date { return this.props.createdAt; }
  public get updatedAt(): Date { return this.props.updatedAt; }
  public get version(): number { return this.props.version; }

  // Export for persistence
  public toPersistence(): Interaction {
    return { ...this.props };
  }

  // Export for API responses
  public toJSON(): Omit<Interaction, 'tenantId'> {
    const { tenantId, ...interactionWithoutTenant } = this.props;
    return interactionWithoutTenant;
  }
}
