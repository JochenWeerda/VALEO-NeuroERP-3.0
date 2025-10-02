import { z } from 'zod';
import { v4 as uuidv4 } from 'uuid';

// Invoice Status Enum
export const InvoiceStatus = {
  ISSUED: 'Issued',
  PAID: 'Paid',
  OVERDUE: 'Overdue',
  CANCELLED: 'Cancelled'
} as const;

export type InvoiceStatusType = typeof InvoiceStatus[keyof typeof InvoiceStatus];

// Invoice Line Item Schema
export const InvoiceLineSchema = z.object({
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

export type InvoiceLine = z.infer<typeof InvoiceLineSchema>;

// Invoice Entity Schema
export const InvoiceSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  customerId: z.string().uuid(),
  orderId: z.string().uuid().optional(), // Optional for ad-hoc invoices
  invoiceNumber: z.string().min(1),
  lines: z.array(InvoiceLineSchema),
  subtotalNet: z.number().nonnegative(),
  totalDiscount: z.number().nonnegative(),
  totalNet: z.number().nonnegative(),
  totalGross: z.number().nonnegative(),
  taxRate: z.number().min(0).max(100).default(19), // Default 19% VAT
  currency: z.string().length(3).default('EUR'),
  dueDate: z.date(),
  paidAt: z.date().optional(),
  notes: z.string().optional(),
  status: z.enum([
    InvoiceStatus.ISSUED,
    InvoiceStatus.PAID,
    InvoiceStatus.OVERDUE,
    InvoiceStatus.CANCELLED
  ]),
  createdAt: z.date(),
  updatedAt: z.date(),
  version: z.number().int().nonnegative()
});

export type Invoice = z.infer<typeof InvoiceSchema>;

// Create Invoice Input Schema (for API)
export const CreateInvoiceInputSchema = InvoiceSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  version: true,
  subtotalNet: true,
  totalDiscount: true,
  totalNet: true,
  totalGross: true,
  status: true,
  paidAt: true
}).extend({
  lines: z.array(InvoiceLineSchema.omit({ id: true, totalNet: true, totalGross: true }))
});

export type CreateInvoiceInput = z.infer<typeof CreateInvoiceInputSchema>;

// Update Invoice Input Schema (for API)
export const UpdateInvoiceInputSchema = z.object({
  dueDate: z.date().optional(),
  notes: z.string().nullish(),
  status: z.enum([
    InvoiceStatus.ISSUED,
    InvoiceStatus.PAID,
    InvoiceStatus.OVERDUE,
    InvoiceStatus.CANCELLED
  ]).optional()
});

export type UpdateInvoiceInput = z.infer<typeof UpdateInvoiceInputSchema>;

// Invoice Aggregate Root
export class InvoiceEntity {
  private constructor(private props: Invoice) {}

  public static create(props: CreateInvoiceInput & { tenantId: string }): InvoiceEntity {
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

    const invoice: Invoice = {
      ...props,
      id: uuidv4(),
      lines,
      subtotalNet,
      totalDiscount,
      totalNet,
      totalGross,
      status: InvoiceStatus.ISSUED,
      createdAt: now,
      updatedAt: now,
      version: 1
    };

    return new InvoiceEntity(invoice);
  }

  public static fromPersistence(props: Invoice): InvoiceEntity {
    return new InvoiceEntity(props);
  }

  public update(props: UpdateInvoiceInput): void {
    if (props.dueDate !== undefined) {
      this.props.dueDate = props.dueDate;
    }

    if (props.notes !== undefined) {
      this.props.notes = props.notes;
    }

    if (props.status !== undefined) {
      this.validateStatusTransition(this.props.status, props.status);
      this.props.status = props.status;

      if (props.status === InvoiceStatus.PAID && !this.props.paidAt) {
        this.props.paidAt = new Date();
      }
    }

    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public markAsPaid(): void {
    if (this.props.status !== InvoiceStatus.ISSUED) {
      throw new Error('Only issued invoices can be marked as paid');
    }
    this.props.status = InvoiceStatus.PAID;
    this.props.paidAt = new Date();
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public markAsOverdue(): void {
    if (this.props.status !== InvoiceStatus.ISSUED) {
      return; // Only issued invoices can become overdue
    }

    if (this.props.dueDate < new Date()) {
      this.props.status = InvoiceStatus.OVERDUE;
      this.props.updatedAt = new Date();
      this.props.version += 1;
    }
  }

  public cancel(): void {
    if (this.props.status === InvoiceStatus.PAID) {
      throw new Error('Paid invoices cannot be cancelled');
    }
    this.props.status = InvoiceStatus.CANCELLED;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public isOverdue(): boolean {
    return this.props.status === InvoiceStatus.ISSUED && this.props.dueDate < new Date();
  }

  public canBePaid(): boolean {
    return this.props.status === InvoiceStatus.ISSUED;
  }

  public canBeCancelled(): boolean {
    return this.props.status !== InvoiceStatus.PAID;
  }

  private validateStatusTransition(currentStatus: InvoiceStatusType, newStatus: InvoiceStatusType): void {
    const validTransitions: Record<InvoiceStatusType, InvoiceStatusType[]> = {
      'Issued': ['Paid', 'Overdue', 'Cancelled'],
      'Paid': [], // Terminal state
      'Overdue': ['Paid', 'Cancelled'],
      'Cancelled': [] // Terminal state
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
  public get orderId(): string | undefined { return this.props.orderId; }
  public get invoiceNumber(): string { return this.props.invoiceNumber; }
  public get lines(): InvoiceLine[] { return [...this.props.lines]; }
  public get subtotalNet(): number { return this.props.subtotalNet; }
  public get totalDiscount(): number { return this.props.totalDiscount; }
  public get totalNet(): number { return this.props.totalNet; }
  public get totalGross(): number { return this.props.totalGross; }
  public get taxRate(): number { return this.props.taxRate; }
  public get currency(): string { return this.props.currency; }
  public get dueDate(): Date { return this.props.dueDate; }
  public get paidAt(): Date | undefined { return this.props.paidAt; }
  public get notes(): string | undefined { return this.props.notes; }
  public get status(): InvoiceStatusType { return this.props.status; }
  public get createdAt(): Date { return this.props.createdAt; }
  public get updatedAt(): Date { return this.props.updatedAt; }
  public get version(): number { return this.props.version; }

  // Export for persistence
  public toPersistence(): Invoice {
    return { ...this.props };
  }

  // Export for API responses
  public toJSON(): Omit<Invoice, 'tenantId'> {
    const { tenantId, ...invoiceWithoutTenant } = this.props;
    return invoiceWithoutTenant;
  }
}