import { z } from 'zod';
import { v4 as uuidv4 } from 'uuid';

// Quote Status Enum
export const QuoteStatus = {
  DRAFT: 'Draft',
  SENT: 'Sent',
  ACCEPTED: 'Accepted',
  REJECTED: 'Rejected',
  EXPIRED: 'Expired'
} as const;

export type QuoteStatusType = typeof QuoteStatus[keyof typeof QuoteStatus];

// Quote Line Item Schema
export const QuoteLineSchema = z.object({
  id: z.string().uuid(),
  sku: z.string().min(1),
  name: z.string().min(1),
  description: z.string().optional(),
  quantity: z.number().positive(),
  unitPrice: z.number().nonnegative(),
  discount: z.number().min(0).max(100).default(0), // Percentage
  totalNet: z.number().nonnegative(),
  totalGross: z.number().nonnegative()
});

export type QuoteLine = z.infer<typeof QuoteLineSchema>;

// Quote Entity Schema
export const QuoteSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  customerId: z.string().uuid(),
  quoteNumber: z.string().min(1),
  lines: z.array(QuoteLineSchema),
  subtotalNet: z.number().nonnegative(),
  totalDiscount: z.number().nonnegative(),
  totalNet: z.number().nonnegative(),
  totalGross: z.number().nonnegative(),
  taxRate: z.number().min(0).max(100).default(19), // Default 19% VAT
  currency: z.string().length(3).default('EUR'),
  validUntil: z.date(),
  notes: z.string().optional(),
  status: z.enum([
    QuoteStatus.DRAFT,
    QuoteStatus.SENT,
    QuoteStatus.ACCEPTED,
    QuoteStatus.REJECTED,
    QuoteStatus.EXPIRED
  ]),
  createdAt: z.date(),
  updatedAt: z.date(),
  version: z.number().int().nonnegative()
});

export type Quote = z.infer<typeof QuoteSchema>;

// Create Quote Input Schema (for API)
export const CreateQuoteInputSchema = QuoteSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  version: true,
  subtotalNet: true,
  totalDiscount: true,
  totalNet: true,
  totalGross: true
}).extend({
  lines: z.array(QuoteLineSchema.omit({ id: true, totalNet: true, totalGross: true }))
});

export type CreateQuoteInput = z.infer<typeof CreateQuoteInputSchema>;

// Update Quote Input Schema (for API)
export const UpdateQuoteInputSchema = z.object({
  lines: z.array(QuoteLineSchema.omit({ id: true, totalNet: true, totalGross: true })).optional(),
  validUntil: z.date().optional(),
  notes: z.string().nullish(),
  status: z.enum([
    QuoteStatus.DRAFT,
    QuoteStatus.SENT,
    QuoteStatus.ACCEPTED,
    QuoteStatus.REJECTED,
    QuoteStatus.EXPIRED
  ]).optional()
});

export type UpdateQuoteInput = z.infer<typeof UpdateQuoteInputSchema>;

// Quote Aggregate Root
export class QuoteEntity {
  private constructor(private props: Quote) {}

  public static create(props: CreateQuoteInput & { tenantId: string }): QuoteEntity {
    const now = new Date();

    // Calculate totals from lines
    const lines = props.lines.map((line, index) => ({
      ...line,
      id: uuidv4(),
      totalNet: line.quantity * line.unitPrice * (1 - line.discount / 100),
      totalGross: line.quantity * line.unitPrice * (1 - line.discount / 100) * (1 + props.taxRate / 100)
    }));

    const subtotalNet = lines.reduce((sum, line) => sum + line.totalNet, 0);
    const totalDiscount = lines.reduce((sum, line) => sum + (line.quantity * line.unitPrice * line.discount / 100), 0);
    const totalNet = subtotalNet;
    const totalGross = lines.reduce((sum, line) => sum + line.totalGross, 0);

    const quote: Quote = {
      ...props,
      id: uuidv4(),
      lines,
      subtotalNet,
      totalDiscount,
      totalNet,
      totalGross,
      status: props.status || QuoteStatus.DRAFT,
      createdAt: now,
      updatedAt: now,
      version: 1
    };

    return new QuoteEntity(quote);
  }

  public static fromPersistence(props: any): QuoteEntity {
    return new QuoteEntity({
      ...props,
      subtotalNet: Number(props.subtotalNet),
      totalDiscount: Number(props.totalDiscount),
      totalNet: Number(props.totalNet),
      totalTax: Number(props.totalTax),
      totalGross: Number(props.totalGross),
      lines: props.lines.map((line: any) => ({
        ...line,
        unitPrice: Number(line.unitPrice),
        discount: Number(line.discount),
        totalNet: Number(line.totalNet),
        totalGross: Number(line.totalGross),
      })),
      notes: props.notes ?? undefined,
    });
  }

  public update(props: UpdateQuoteInput): void {
    if (props.lines) {
      this.props.lines = props.lines.map((line, index) => ({
        ...line,
        id: this.props.lines[index]?.id || uuidv4(),
        totalNet: line.quantity * line.unitPrice * (1 - line.discount / 100),
        totalGross: line.quantity * line.unitPrice * (1 - line.discount / 100) * (1 + this.props.taxRate / 100)
      }));

      // Recalculate totals
      this.props.subtotalNet = this.props.lines.reduce((sum, line) => sum + line.totalNet, 0);
      this.props.totalDiscount = this.props.lines.reduce((sum, line) => sum + (line.quantity * line.unitPrice * line.discount / 100), 0);
      this.props.totalNet = this.props.subtotalNet;
      this.props.totalGross = this.props.lines.reduce((sum, line) => sum + line.totalGross, 0);
    }

    if (props.validUntil !== undefined) {
      this.props.validUntil = props.validUntil ?? undefined;
    }

    if (props.notes !== undefined) {
      this.props.notes = props.notes ?? undefined;
    }

    if (props.status !== undefined) {
      this.validateStatusTransition(this.props.status, props.status);
      this.props.status = props.status;
    }

    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public send(): void {
    if (this.props.status !== QuoteStatus.DRAFT) {
      throw new Error('Only draft quotes can be sent');
    }
    this.props.status = QuoteStatus.SENT;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public accept(): void {
    if (this.props.status !== QuoteStatus.SENT) {
      throw new Error('Only sent quotes can be accepted');
    }
    this.props.status = QuoteStatus.ACCEPTED;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public reject(): void {
    if (this.props.status !== QuoteStatus.SENT) {
      throw new Error('Only sent quotes can be rejected');
    }
    this.props.status = QuoteStatus.REJECTED;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public expire(): void {
    if (this.props.status === QuoteStatus.EXPIRED || this.props.status === QuoteStatus.REJECTED) {
      return; // Already expired or rejected
    }
    this.props.status = QuoteStatus.EXPIRED;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public isExpired(): boolean {
    return this.props.validUntil < new Date();
  }

  public canBeAccepted(): boolean {
    return this.props.status === QuoteStatus.SENT && !this.isExpired();
  }

  public canBeSent(): boolean {
    return this.props.status === QuoteStatus.DRAFT && this.props.lines.length > 0;
  }

  private validateStatusTransition(currentStatus: QuoteStatusType, newStatus: QuoteStatusType): void {
    const validTransitions: Record<QuoteStatusType, QuoteStatusType[]> = {
      'Draft': ['Sent'],
      'Sent': ['Accepted', 'Rejected', 'Expired'],
      'Accepted': [], // Terminal state
      'Rejected': [], // Terminal state
      'Expired': [] // Terminal state
    };

    const allowedStatuses = validTransitions[currentStatus];

    if (!allowedStatuses?.includes(newStatus)) {
      throw new Error(`Cannot change status from ${currentStatus} to ${newStatus}`);
    }
  }

  // Getters
  public get id(): string { return this.props.id; }
  public get tenantId(): string { return this.props.tenantId; }
  public get customerId(): string { return this.props.customerId; }
  public get quoteNumber(): string { return this.props.quoteNumber; }
  public get lines(): QuoteLine[] { return [...this.props.lines]; }
  public get subtotalNet(): number { return this.props.subtotalNet; }
  public get totalDiscount(): number { return this.props.totalDiscount; }
  public get totalNet(): number { return this.props.totalNet; }
  public get totalGross(): number { return this.props.totalGross; }
  public get taxRate(): number { return this.props.taxRate; }
  public get currency(): string { return this.props.currency; }
  public get validUntil(): Date { return this.props.validUntil; }
  public get notes(): string | undefined { return this.props.notes; }
  public get status(): QuoteStatusType { return this.props.status; }
  public get createdAt(): Date { return this.props.createdAt; }
  public get updatedAt(): Date { return this.props.updatedAt; }
  public get version(): number { return this.props.version; }

  // Export for persistence
  public toPersistence(): Quote {
    return { ...this.props };
  }

  // Export for API responses
  public toJSON(): Omit<Quote, 'tenantId'> {
    const { tenantId, ...quoteWithoutTenant } = this.props;
    return quoteWithoutTenant;
  }
}