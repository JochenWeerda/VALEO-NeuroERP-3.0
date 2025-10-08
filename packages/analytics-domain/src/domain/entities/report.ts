export type ReportType =
  | 'Contracts'
  | 'Inventory'
  | 'Weighing'
  | 'Finance'
  | 'Quality'
  | 'Production'
  | 'Regulatory'
  | 'Custom';

export type ReportFormat = 'json' | 'csv' | 'excel' | 'pdf';

export interface ReportParameters {
  tenantId: string;
  dateFrom?: Date;
  dateTo?: Date;
  commodity?: string;
  customerId?: string;
  supplierId?: string;
  siteId?: string;
  status?: string;
  filters?: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
}

export interface ReportMetadata {
  totalRecords?: number;
  executionTimeMs?: number;
  dataSource?: string;
  generatedBy?: string;
  checksum?: string;
}

export class Report {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  constructor(
    public readonly id: string,
    public readonly tenantId: string,
    public readonly type: ReportType,
    public readonly parameters: ReportParameters,
    public readonly generatedAt: Date,
    public uri?: string,
    public readonly format: ReportFormat = 'json',
    public readonly metadata?: ReportMetadata,
    public readonly version: number = 1
  ) {}

  static create(params: {
    id: string;
    tenantId: string;
    type: ReportType;
    parameters: ReportParameters;
    format?: ReportFormat;
    metadata?: ReportMetadata;
  }): Report {
    return new Report(
      params.id,
      params.tenantId,
      params.type,
      params.parameters,
      new Date(),
      undefined,
      params.format || 'json',
      params.metadata,
      1
    );
  }

  setUri(uri: string): Report {
    return new Report(
      this.id,
      this.tenantId,
      this.type,
      this.parameters,
      this.generatedAt,
      uri,
      this.format,
      this.metadata,
      this.version
    );
  }

  updateMetadata(metadata: Partial<ReportMetadata>): Report {
    return new Report(
      this.id,
      this.tenantId,
      this.type,
      this.parameters,
      this.generatedAt,
      this.uri,
      this.format,
      { ...this.metadata, ...metadata },
      this.version
    );
  }

  isExpired(maxAgeHours: number = 24): boolean {
    const ageMs = Date.now() - this.generatedAt.getTime();
    const maxAgeMs = maxAgeHours * 60 * 60 * 1000;
    return ageMs > maxAgeMs;
  }

  getFileName(): string {
    const timestamp = this.generatedAt.toISOString().split('T')[0];
    const type = this.type.toLowerCase();
    return `report-${type}-${timestamp}.${this.format}`;
  }

  toJSON() {
    return {
      id: this.id,
      tenantId: this.tenantId,
      type: this.type,
      parameters: this.parameters,
      generatedAt: this.generatedAt.toISOString(),
      uri: this.uri,
      format: this.format,
      metadata: this.metadata,
      version: this.version,
    };
  }
}