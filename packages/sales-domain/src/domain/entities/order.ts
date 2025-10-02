import { z } from 'zod';
import { v4 as uuidv4 } from 'uuid';

// Order Status Enum
export const OrderStatus = {
  DRAFT: 'Draft',
  CONFIRMED: 'Confirmed',
  INVOICED: 'Invoiced',
  CANCELLED: 'Cancelled'
} as const;

export type OrderStatusType = typeof OrderStatus[keyof typeof OrderStatus];

// Order Line Item Schema
export const OrderLineSchema = z.object({
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

export type OrderLine = z.infer<typeof OrderLineSchema>;

// Order Entity Schema
export const OrderSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  customerId: z.string().uuid(),
  orderNumber: z.string().min(1),
  lines: z.array(OrderLineSchema),
  subtotalNet: z.number().nonnegative(),
  totalDiscount: z.number().nonnegative(),
  totalNet: z.number().nonnegative(),
  totalGross: z.number().nonnegative(),
  taxRate: z.number().min(0).max(100).default(19), // Default 19% VAT
  currency: z.string().length(3).default('EUR'),
  expectedDeliveryDate: z.date().optional(),
  notes: z.string().optional(),
  status: z.enum([
    OrderStatus.DRAFT,
    OrderStatus.CONFIRMED,
    OrderStatus.INVOICED,
    OrderStatus.CANCELLED
  ]),
  createdAt: z.date(),
  updatedAt: z.date(),
  version: z.number().int().nonnegative()
});

export type Order = z.infer<typeof OrderSchema>;

// Create Order Input Schema (for API)
export const CreateOrderInputSchema = OrderSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  version: true,
  subtotalNet: true,
  totalDiscount: true,
  totalNet: true,
  totalGross: true
}).extend({
  lines: z.array(OrderLineSchema.omit({ id: true, totalNet: true, totalGross: true }))
});

export type CreateOrderInput = z.infer<typeof CreateOrderInputSchema>;

// Update Order Input Schema (for API)
export const UpdateOrderInputSchema = z.object({
  lines: z.array(OrderLineSchema.omit({ id: true, totalNet: true, totalGross: true })).optional(),
  expectedDeliveryDate: z.date().nullish(),
  notes: z.string().nullish(),
  status: z.enum([
    OrderStatus.DRAFT,
    OrderStatus.CONFIRMED,
    OrderStatus.INVOICED,
    OrderStatus.CANCELLED
  ]).optional()
});

export type UpdateOrderInput = z.infer<typeof UpdateOrderInputSchema>;

// Order Aggregate Root
export class OrderEntity {
  private constructor(private props: Order) {}

  public static create(props: CreateOrderInput & { tenantId: string }): OrderEntity {
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

    const order: Order = {
      ...props,
      id: uuidv4(),
      lines,
      subtotalNet,
      totalDiscount,
      totalNet,
      totalGross,
      status: props.status || OrderStatus.DRAFT,
      createdAt: now,
      updatedAt: now,
      version: 1
    };

    return new OrderEntity(order);
  }

  public static fromPersistence(props: Order): OrderEntity {
    return new OrderEntity(props);
  }

  public update(props: UpdateOrderInput): void {
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

    if (props.expectedDeliveryDate !== undefined) {
      this.props.expectedDeliveryDate = props.expectedDeliveryDate;
    }

    if (props.notes !== undefined) {
      this.props.notes = props.notes;
    }

    if (props.status !== undefined) {
      this.validateStatusTransition(this.props.status, props.status);
      this.props.status = props.status;
    }

    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public confirm(): void {
    if (this.props.status !== OrderStatus.DRAFT) {
      throw new Error('Only draft orders can be confirmed');
    }
    this.props.status = OrderStatus.CONFIRMED;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public markAsInvoiced(): void {
    if (this.props.status !== OrderStatus.CONFIRMED) {
      throw new Error('Only confirmed orders can be invoiced');
    }
    this.props.status = OrderStatus.INVOICED;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public cancel(): void {
    if (this.props.status === OrderStatus.INVOICED) {
      throw new Error('Invoiced orders cannot be cancelled');
    }
    this.props.status = OrderStatus.CANCELLED;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public canBeConfirmed(): boolean {
    return this.props.status === OrderStatus.DRAFT && this.props.lines.length > 0;
  }

  public canBeInvoiced(): boolean {
    return this.props.status === OrderStatus.CONFIRMED;
  }

  public canBeCancelled(): boolean {
    return this.props.status !== OrderStatus.INVOICED;
  }

  private validateStatusTransition(currentStatus: OrderStatusType, newStatus: OrderStatusType): void {
    const validTransitions: Record<OrderStatusType, OrderStatusType[]> = {
      'Draft': ['Confirmed', 'Cancelled'],
      'Confirmed': ['Invoiced', 'Cancelled'],
      'Invoiced': [], // Terminal state
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
  public get orderNumber(): string { return this.props.orderNumber; }
  public get lines(): OrderLine[] { return [...this.props.lines]; }
  public get subtotalNet(): number { return this.props.subtotalNet; }
  public get totalDiscount(): number { return this.props.totalDiscount; }
  public get totalNet(): number { return this.props.totalNet; }
  public get totalGross(): number { return this.props.totalGross; }
  public get taxRate(): number { return this.props.taxRate; }
  public get currency(): string { return this.props.currency; }
  public get expectedDeliveryDate(): Date | undefined { return this.props.expectedDeliveryDate; }
  public get notes(): string | undefined { return this.props.notes; }
  public get status(): OrderStatusType { return this.props.status; }
  public get createdAt(): Date { return this.props.createdAt; }
  public get updatedAt(): Date { return this.props.updatedAt; }
  public get version(): number { return this.props.version; }

  // Export for persistence
  public toPersistence(): Order {
    return { ...this.props };
  }

  // Export for API responses
  public toJSON(): Omit<Order, 'tenantId'> {
    const { tenantId, ...orderWithoutTenant } = this.props;
    return orderWithoutTenant;
  }
}