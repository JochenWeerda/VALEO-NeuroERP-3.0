import { z } from 'zod';
import { v4 as uuidv4 } from 'uuid';

// Sales Offer Status Enum
export const SalesOfferStatus = {
  ENTWURF: 'ENTWURF',
  VERSENDET: 'VERSENDET',
  ANGENOMMEN: 'ANGENOMMEN',
  ABGELEHNT: 'ABGELEHNT',
  ABGELAUFEN: 'ABGELAUFEN'
} as const;

export type SalesOfferStatusType = typeof SalesOfferStatus[keyof typeof SalesOfferStatus];

// Sales Offer Entity Schema
export const SalesOfferSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  customerInquiryId: z.string().uuid().optional(),
  customerId: z.string().uuid(),
  offerNumber: z.string().min(1),
  subject: z.string().min(1),
  description: z.string().min(1),
  totalAmount: z.number().nonnegative(),
  currency: z.string().length(3).default('EUR'),
  validUntil: z.date(),
  status: z.enum([
    SalesOfferStatus.ENTWURF,
    SalesOfferStatus.VERSENDET,
    SalesOfferStatus.ANGENOMMEN,
    SalesOfferStatus.ABGELEHNT,
    SalesOfferStatus.ABGELAUFEN
  ]),
  contactPerson: z.string().optional(),
  deliveryDate: z.date().optional(),
  paymentTerms: z.string().optional(),
  notes: z.string().optional(),
  createdAt: z.date(),
  updatedAt: z.date(),
  deletedAt: z.date().optional(),
  version: z.number().int().nonnegative()
});

export type SalesOffer = z.infer<typeof SalesOfferSchema>;

// Create Sales Offer Input Schema (for API)
export const CreateSalesOfferInputSchema = SalesOfferSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  deletedAt: true,
  version: true
});

export type CreateSalesOfferInput = z.infer<typeof CreateSalesOfferInputSchema>;

// Update Sales Offer Input Schema (for API)
export const UpdateSalesOfferInputSchema = z.object({
  subject: z.string().min(1).optional(),
  description: z.string().min(1).optional(),
  totalAmount: z.number().nonnegative().optional(),
  validUntil: z.date().optional(),
  contactPerson: z.string().nullish(),
  deliveryDate: z.date().nullish(),
  paymentTerms: z.string().nullish(),
  notes: z.string().nullish()
});

export type UpdateSalesOfferInput = z.infer<typeof UpdateSalesOfferInputSchema>;

// Sales Offer Aggregate Root
export class SalesOfferEntity {
  private constructor(private props: SalesOffer) {}

  public static create(props: CreateSalesOfferInput & { tenantId: string }): SalesOfferEntity {
    const now = new Date();

    const salesOffer: SalesOffer = {
      ...props,
      id: uuidv4(),
      status: props.status || SalesOfferStatus.ENTWURF,
      createdAt: now,
      updatedAt: now,
      version: 1
    };

    return new SalesOfferEntity(salesOffer);
  }

  public static fromPersistence(props: any): SalesOfferEntity {
    return new SalesOfferEntity({
      ...props,
      totalAmount: Number(props.totalAmount),
      contactPerson: props.contactPerson ?? undefined,
      deliveryDate: props.deliveryDate ?? undefined,
      paymentTerms: props.paymentTerms ?? undefined,
      notes: props.notes ?? undefined,
      deletedAt: props.deletedAt ?? undefined
    });
  }

  public update(props: UpdateSalesOfferInput): void {
    if (props.subject !== undefined) {
      this.props.subject = props.subject;
    }

    if (props.description !== undefined) {
      this.props.description = props.description;
    }

    if (props.totalAmount !== undefined) {
      this.props.totalAmount = props.totalAmount;
    }

    if (props.validUntil !== undefined) {
      this.props.validUntil = props.validUntil;
    }

    if (props.contactPerson !== undefined) {
      this.props.contactPerson = props.contactPerson ?? undefined;
    }

    if (props.deliveryDate !== undefined) {
      this.props.deliveryDate = props.deliveryDate ?? undefined;
    }

    if (props.paymentTerms !== undefined) {
      this.props.paymentTerms = props.paymentTerms ?? undefined;
    }

    if (props.notes !== undefined) {
      this.props.notes = props.notes ?? undefined;
    }

    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public versenden(): void {
    if (this.props.status !== SalesOfferStatus.ENTWURF) {
      throw new Error('Nur Entwürfe können versendet werden');
    }
    this.props.status = SalesOfferStatus.VERSENDET;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public annehmen(): void {
    if (this.props.status !== SalesOfferStatus.VERSENDET) {
      throw new Error('Nur versendete Angebote können angenommen werden');
    }
    this.props.status = SalesOfferStatus.ANGENOMMEN;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public ablehnen(): void {
    if (this.props.status === SalesOfferStatus.ANGENOMMEN || this.props.status === SalesOfferStatus.ABGELAUFEN) {
      throw new Error('Angebot kann nicht mehr abgelehnt werden');
    }
    this.props.status = SalesOfferStatus.ABGELEHNT;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public ablaufen(): void {
    if (this.props.status !== SalesOfferStatus.VERSENDET) {
      throw new Error('Nur versendete Angebote können ablaufen');
    }
    this.props.status = SalesOfferStatus.ABGELAUFEN;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public istAbgelaufen(): boolean {
    return new Date() > this.props.validUntil && this.props.status === SalesOfferStatus.VERSENDET;
  }

  public kannAngenommenWerden(): boolean {
    return this.props.status === SalesOfferStatus.VERSENDET && !this.istAbgelaufen();
  }

  public istGueltig(): boolean {
    return this.props.status === SalesOfferStatus.VERSENDET && !this.istAbgelaufen();
  }

  public canBeSent(): boolean {
    return this.props.status === SalesOfferStatus.ENTWURF;
  }

  private validateStatusTransition(currentStatus: SalesOfferStatusType, newStatus: SalesOfferStatusType): void {
    const validTransitions: Record<SalesOfferStatusType, SalesOfferStatusType[]> = {
      'ENTWURF': ['VERSENDET'],
      'VERSENDET': ['ANGENOMMEN', 'ABGELEHNT', 'ABGELAUFEN'],
      'ANGENOMMEN': [], // Terminal state
      'ABGELEHNT': [], // Terminal state
      'ABGELAUFEN': [] // Terminal state
    };

    const allowedStatuses = validTransitions[currentStatus];

    if (!allowedStatuses?.includes(newStatus)) {
      throw new Error(`Cannot change status from ${currentStatus} to ${newStatus}`);
    }
  }

  // Getters
  public get id(): string { return this.props.id; }
  public get tenantId(): string { return this.props.tenantId; }
  public get customerInquiryId(): string | undefined { return this.props.customerInquiryId; }
  public get customerId(): string { return this.props.customerId; }
  public get offerNumber(): string { return this.props.offerNumber; }
  public get subject(): string { return this.props.subject; }
  public get description(): string { return this.props.description; }
  public get totalAmount(): number { return this.props.totalAmount; }
  public get currency(): string { return this.props.currency; }
  public get validUntil(): Date { return this.props.validUntil; }
  public get status(): SalesOfferStatusType { return this.props.status; }
  public get contactPerson(): string | undefined { return this.props.contactPerson; }
  public get deliveryDate(): Date | undefined { return this.props.deliveryDate; }
  public get paymentTerms(): string | undefined { return this.props.paymentTerms; }
  public get notes(): string | undefined { return this.props.notes; }
  public get createdAt(): Date { return this.props.createdAt; }
  public get updatedAt(): Date { return this.props.updatedAt; }
  public get version(): number { return this.props.version; }

  // Export for persistence
  public toPersistence(): SalesOffer {
    return { ...this.props };
  }

  // Export for API responses
  public toJSON(): Omit<SalesOffer, 'tenantId'> {
    const { tenantId, ...salesOfferWithoutTenant } = this.props;
    return salesOfferWithoutTenant;
  }
}