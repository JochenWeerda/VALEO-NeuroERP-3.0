import { z } from 'zod';
import { v4 as uuidv4 } from 'uuid';

// Enums
export const OpportunityStage = {
  LEAD: 'Lead',
  QUALIFIED: 'Qualified',
  PROPOSAL: 'Proposal',
  WON: 'Won',
  LOST: 'Lost'
} as const;

export type OpportunityStageType = typeof OpportunityStage[keyof typeof OpportunityStage];

// Opportunity Entity Schema
export const OpportunitySchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  customerId: z.string().uuid(),
  title: z.string().min(1),
  stage: z.enum([
    OpportunityStage.LEAD,
    OpportunityStage.QUALIFIED,
    OpportunityStage.PROPOSAL,
    OpportunityStage.WON,
    OpportunityStage.LOST
  ]),
  expectedCloseDate: z.date().optional(),
  amountNet: z.number().nonnegative().optional(),
  currency: z.string().length(3).optional(), // ISO 4217 currency code
  probability: z.number().min(0).max(1), // 0-1 (0% to 100%)
  ownerUserId: z.string().uuid().optional(),
  createdAt: z.date(),
  updatedAt: z.date(),
  version: z.number().int().nonnegative()
});

export type Opportunity = z.infer<typeof OpportunitySchema>;

// Create Opportunity Input Schema (for API)
export const CreateOpportunityInputSchema = OpportunitySchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  version: true
});

export type CreateOpportunityInput = z.infer<typeof CreateOpportunityInputSchema>;

// Update Opportunity Input Schema (for API)
export const UpdateOpportunityInputSchema = z.object({
  title: z.string().min(1).optional(),
  stage: z.enum([
    OpportunityStage.LEAD,
    OpportunityStage.QUALIFIED,
    OpportunityStage.PROPOSAL,
    OpportunityStage.WON,
    OpportunityStage.LOST
  ]).optional(),
  expectedCloseDate: z.date().nullish(),
  amountNet: z.number().nonnegative().nullish(),
  currency: z.string().length(3).nullish(),
  probability: z.number().min(0).max(1).optional(),
  ownerUserId: z.string().uuid().nullish()
});

export type UpdateOpportunityInput = z.infer<typeof UpdateOpportunityInputSchema>;

// Opportunity Aggregate Root
export class OpportunityEntity {
  private constructor(private props: Opportunity) {}

  public static create(props: CreateOpportunityInput & { tenantId: string }): OpportunityEntity {
    const now = new Date();
    const opportunity: Opportunity = {
      ...props,
      id: uuidv4(),
      stage: props.stage || OpportunityStage.LEAD,
      probability: props.probability !== undefined ? props.probability : 0.1, // Default 10% for leads
      createdAt: now,
      updatedAt: now,
      version: 1
    };

    return new OpportunityEntity(opportunity);
  }

  public static fromPersistence(props: any): OpportunityEntity {
    return new OpportunityEntity({
      ...props,
      ownerUserId: props.ownerUserId ?? undefined,
      expectedCloseDate: props.expectedCloseDate ?? undefined,
      amountNet: props.amountNet ? Number(props.amountNet) : undefined,
      currency: props.currency ?? undefined,
    });
  }

  public update(props: UpdateOpportunityInput): void {
    if (props.title !== undefined) {
      this.props.title = props.title;
    }
    if (props.stage !== undefined) {
      this.props.stage = props.stage;
    }
    if (props.expectedCloseDate !== undefined) {
      this.props.expectedCloseDate = props.expectedCloseDate ?? undefined;
    }
    if (props.amountNet !== undefined) {
      this.props.amountNet = props.amountNet ?? undefined;
    }
    if (props.currency !== undefined) {
      this.props.currency = props.currency ?? undefined;
    }
    if (props.probability !== undefined) {
      this.props.probability = props.probability;
    }
    if (props.ownerUserId !== undefined) {
      this.props.ownerUserId = props.ownerUserId ?? undefined;
    }

    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public changeStage(newStage: OpportunityStageType): void {
    if (this.props.stage !== newStage) {
      this.props.stage = newStage;
      this.props.updatedAt = new Date();
      this.props.version += 1;
    }
  }

  public markAsWon(): void {
    this.props.stage = OpportunityStage.WON;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public markAsLost(): void {
    this.props.stage = OpportunityStage.LOST;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public updateProbability(probability: number): void {
    if (probability < 0 || probability > 1) {
      throw new Error('Probability must be between 0 and 1');
    }
    this.props.probability = probability;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public updateAmount(amountNet: number, currency?: string): void {
    this.props.amountNet = amountNet;
    if (currency !== undefined) {
      this.props.currency = currency;
    }
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public updateExpectedCloseDate(date: Date): void {
    this.props.expectedCloseDate = date;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  // Business logic methods
  public isOpen(): boolean {
    return this.props.stage !== OpportunityStage.WON && this.props.stage !== OpportunityStage.LOST;
  }

  public isWon(): boolean {
    return this.props.stage === OpportunityStage.WON;
  }

  public isLost(): boolean {
    return this.props.stage === OpportunityStage.LOST;
  }

  public getWeightedValue(): number {
    if (!this.props.amountNet) return 0;
    return this.props.amountNet * this.props.probability;
  }

  // Getters
  public get id(): string { return this.props.id; }
  public get tenantId(): string { return this.props.tenantId; }
  public get customerId(): string { return this.props.customerId; }
  public get title(): string { return this.props.title; }
  public get stage(): OpportunityStageType { return this.props.stage; }
  public get expectedCloseDate(): Date | undefined { return this.props.expectedCloseDate; }
  public get amountNet(): number | undefined { return this.props.amountNet; }
  public get currency(): string | undefined { return this.props.currency; }
  public get probability(): number { return this.props.probability; }
  public get ownerUserId(): string | undefined { return this.props.ownerUserId; }
  public get createdAt(): Date { return this.props.createdAt; }
  public get updatedAt(): Date { return this.props.updatedAt; }
  public get version(): number { return this.props.version; }

  // Export for persistence
  public toPersistence(): Opportunity {
    return { ...this.props };
  }

  // Export for API responses
  public toJSON(): Omit<Opportunity, 'tenantId'> {
    const { tenantId, ...opportunityWithoutTenant } = this.props;
    return opportunityWithoutTenant;
  }
}