export interface KPIContext {
  commodity?: string;
  contract?: string;
  batch?: string;
  site?: string;
  customer?: string;
  supplier?: string;
  period?: string;
}

export interface KPIMetadata {
  calculationMethod?: string;
  dataSource?: string;
  lastUpdated?: Date;
  confidence?: number;
  unit?: string;
}

export class KPI {
  constructor(
    public readonly id: string,
    public readonly tenantId: string,
    public readonly name: string,
    public readonly description: string,
    public value: number | string | boolean,
    public readonly unit: string,
    public readonly context: KPIContext,
    public readonly calculatedAt: Date,
    public readonly metadata?: KPIMetadata,
    public readonly version: number = 1
  ) {}

  static create(params: {
    id: string;
    tenantId: string;
    name: string;
    description: string;
    value: number | string | boolean;
    unit: string;
    context?: KPIContext;
    metadata?: KPIMetadata;
  }): KPI {
    return new KPI(
      params.id,
      params.tenantId,
      params.name,
      params.description,
      params.value,
      params.unit,
      params.context || {},
      new Date(),
      params.metadata,
      1
    );
  }

  updateValue(newValue: number | string | boolean): KPI {
    return new KPI(
      this.id,
      this.tenantId,
      this.name,
      this.description,
      newValue,
      this.unit,
      this.context,
      new Date(),
      {
        ...this.metadata,
        lastUpdated: new Date(),
      },
      this.version + 1
    );
  }

  isExpired(maxAgeMinutes: number = 60): boolean {
    const ageMs = Date.now() - this.calculatedAt.getTime();
    const maxAgeMs = maxAgeMinutes * 60 * 1000;
    return ageMs > maxAgeMs;
  }

  toJSON() {
    return {
      id: this.id,
      tenantId: this.tenantId,
      name: this.name,
      description: this.description,
      value: this.value,
      unit: this.unit,
      context: this.context,
      calculatedAt: this.calculatedAt.toISOString(),
      metadata: this.metadata,
      version: this.version,
    };
  }
}