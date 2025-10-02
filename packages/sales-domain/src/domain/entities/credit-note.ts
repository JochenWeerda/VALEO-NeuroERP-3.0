import { z } from 'zod';
import { v4 as uuidv4 } from 'uuid';

// Credit Note Status Enum
export const CreditNoteStatus = {
  ISSUED: 'Issued',
  SETTLED: 'Settled'
} as const;

export type CreditNoteStatusType = typeof CreditNoteStatus[keyof typeof CreditNoteStatus];

// Credit Note Line Item Schema
export const CreditNoteLineSchema = z.object({
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

export type CreditNoteLine = z.infer<typeof CreditNoteLineSchema>;

// Credit Note Entity Schema
export const CreditNoteSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  customerId: z.string().uuid(),
  invoiceId: z.string().uuid(),
  creditNumber: z.string().min(1),
  lines: z.array(CreditNoteLineSchema),
  subtotalNet: z.number().nonnegative(),
  totalDiscount: z.number().nonnegative(),
  totalNet: z.number().nonnegative(),
  totalGross: z.number().nonnegative(),
  taxRate: z.number().min(0).max(100).default(19), // Default 19% VAT
  currency: z.string().length(3).default('EUR'),
  reason: z.string().min(1),
  notes: z.string().optional(),
  status: z.enum([
    CreditNoteStatus.ISSUED,
    CreditNoteStatus.SETTLED
  ]),
  settledAt: z.date().optional(),
  createdAt: z.date(),
  updatedAt: z.date(),
  version: z.number().int().nonnegative()
});

export type CreditNote = z.infer<typeof CreditNoteSchema>;

// Create Credit Note Input Schema (for API)
export const CreateCreditNoteInputSchema = CreditNoteSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  version: true,
  subtotalNet: true,
  totalDiscount: true,
  totalNet: true,
  totalGross: true,
  status: true,
  settledAt: true
}).extend({
  lines: z.array(CreditNoteLineSchema.omit({ id: true, totalNet: true, totalGross: true }))
});

export type CreateCreditNoteInput = z.infer<typeof CreateCreditNoteInputSchema>;

// Update Credit Note Input Schema (for API)
export const UpdateCreditNoteInputSchema = z.object({
  reason: z.string().min(1).optional(),
  notes: z.string().nullish(),
  status: z.enum([
    CreditNoteStatus.ISSUED,
    CreditNoteStatus.SETTLED
  ]).optional()
});

export type UpdateCreditNoteInput = z.infer<typeof UpdateCreditNoteInputSchema>;

// Credit Note Aggregate Root
export class CreditNoteEntity {
  private constructor(private props: CreditNote) {}

  public static create(props: CreateCreditNoteInput & { tenantId: string }): CreditNoteEntity {
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

    const creditNote: CreditNote = {
      ...props,
      id: uuidv4(),
      lines,
      subtotalNet,
      totalDiscount,
      totalNet,
      totalGross,
      status: CreditNoteStatus.ISSUED,
      createdAt: now,
      updatedAt: now,
      version: 1
    };

    return new CreditNoteEntity(creditNote);
  }

  public static fromPersistence(props: any): CreditNoteEntity {
    return new CreditNoteEntity({
      ...props,
      subtotalNet: Number(props.subtotalNet),
      totalDiscount: Number(props.totalDiscount),
      totalNet: Number(props.totalNet),
      totalGross: Number(props.totalGross),
      lines: props.lines.map((line: any) => ({
        ...line,
        unitPrice: Number(line.unitPrice),
        discount: Number(line.discount),
        totalNet: Number(line.totalNet),
        totalGross: Number(line.totalGross),
      })),
      settledAt: props.settledAt ?? undefined,
    });
  }

  public update(props: UpdateCreditNoteInput): void {
    if (props.reason !== undefined) {
      this.props.reason = props.reason;
    }

    if (props.notes !== undefined) {
      this.props.notes = props.notes ?? undefined;
    }

    if (props.status !== undefined) {
      this.validateStatusTransition(this.props.status, props.status);
      this.props.status = props.status;

      if (props.status === CreditNoteStatus.SETTLED && !this.props.settledAt) {
        this.props.settledAt = new Date();
      }
    }

    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public settle(): void {
    if (this.props.status !== CreditNoteStatus.ISSUED) {
      throw new Error('Only issued credit notes can be settled');
    }
    this.props.status = CreditNoteStatus.SETTLED;
    this.props.settledAt = new Date();
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public canBeSettled(): boolean {
    return this.props.status === CreditNoteStatus.ISSUED;
  }

  private validateStatusTransition(currentStatus: CreditNoteStatusType, newStatus: CreditNoteStatusType): void {
    const validTransitions: Record<CreditNoteStatusType, CreditNoteStatusType[]> = {
      'Issued': ['Settled'],
      'Settled': [] // Terminal state
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
  public get invoiceId(): string { return this.props.invoiceId; }
  public get creditNumber(): string { return this.props.creditNumber; }
  public get lines(): CreditNoteLine[] { return [...this.props.lines]; }
  public get subtotalNet(): number { return this.props.subtotalNet; }
  public get totalDiscount(): number { return this.props.totalDiscount; }
  public get totalNet(): number { return this.props.totalNet; }
  public get totalGross(): number { return this.props.totalGross; }
  public get taxRate(): number { return this.props.taxRate; }
  public get currency(): string { return this.props.currency; }
  public get reason(): string { return this.props.reason; }
  public get notes(): string | undefined { return this.props.notes; }
  public get status(): CreditNoteStatusType { return this.props.status; }
  public get settledAt(): Date | undefined { return this.props.settledAt; }
  public get createdAt(): Date { return this.props.createdAt; }
  public get updatedAt(): Date { return this.props.updatedAt; }
  public get version(): number { return this.props.version; }

  // Export for persistence
  public toPersistence(): CreditNote {
    return { ...this.props };
  }

  // Export for API responses
  public toJSON(): Omit<CreditNote, 'tenantId'> {
    const { tenantId, ...creditNoteWithoutTenant } = this.props;
    return creditNoteWithoutTenant;
  }
}