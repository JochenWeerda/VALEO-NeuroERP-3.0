import { SalesOffer } from './sales-offer.entity'

export enum CustomerInquiryStatus {
  EINGEGANGEN = 'EINGEGANGEN',
  BEARBEITET = 'BEARBEITET',
  ANGEBOT_ERSTELLT = 'ANGEBOT_ERSTELLT',
  ABGELEHNT = 'ABGELEHNT'
}

export enum InquiryPriority {
  NIEDRIG = 'niedrig',
  NORMAL = 'normal',
  HOCH = 'hoch',
  DRINGEND = 'dringend'
}

export enum InquiryType {
  STANDARD = 'STANDARD',
  PROJEKT = 'PROJEKT',
  SERVICE = 'SERVICE'
}

export class CustomerInquiry {
  constructor(
    public readonly id: string,
    public readonly inquiryNumber: string,
    public readonly customerId: string,
    public readonly type: InquiryType,
    public readonly subject: string,
    public readonly description: string,
    public readonly priority: InquiryPriority,
    public readonly currency: string,
    public readonly status: CustomerInquiryStatus,
    public readonly tenantId: string,
    public readonly contactPerson?: string,
    public readonly requestedDeliveryDate?: Date,
    public readonly budget?: number,
    public readonly assignedTo?: string,
    public readonly notes?: string,
    public readonly version: number = 0,
    public readonly createdAt: Date = new Date(),
    public readonly updatedAt: Date = new Date(),
    public readonly deletedAt?: Date
  ) {}

  static create(data: {
    inquiryNumber: string
    customerId: string
    contactPerson?: string
    type: InquiryType
    subject: string
    description: string
    priority: InquiryPriority
    requestedDeliveryDate?: Date
    budget?: number
    currency: string
    assignedTo?: string
    notes?: string
    tenantId: string
  }): CustomerInquiry {
    return new CustomerInquiry(
      '', // ID wird generiert
      data.inquiryNumber,
      data.customerId,
      data.type,
      data.subject,
      data.description,
      data.priority,
      data.currency,
      CustomerInquiryStatus.EINGEGANGEN,
      data.tenantId,
      data.contactPerson,
      data.requestedDeliveryDate,
      data.budget,
      data.assignedTo,
      data.notes
    )
  }

  bearbeiten(assignedTo?: string): CustomerInquiry {
    if (this.status !== CustomerInquiryStatus.EINGEGANGEN) {
      throw new Error('Nur eingegangene Anfragen können bearbeitet werden')
    }
    return new CustomerInquiry(
      this.id,
      this.inquiryNumber,
      this.customerId,
      this.type,
      this.subject,
      this.description,
      this.priority,
      this.currency,
      CustomerInquiryStatus.BEARBEITET,
      this.tenantId,
      this.contactPerson,
      this.requestedDeliveryDate,
      this.budget,
      assignedTo || this.assignedTo,
      this.notes,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  angebotErstellen(): CustomerInquiry {
    if (this.status !== CustomerInquiryStatus.BEARBEITET) {
      throw new Error('Nur bearbeitete Anfragen können Angebote erhalten')
    }
    return new CustomerInquiry(
      this.id,
      this.inquiryNumber,
      this.customerId,
      this.type,
      this.subject,
      this.description,
      this.priority,
      this.currency,
      CustomerInquiryStatus.ANGEBOT_ERSTELLT,
      this.tenantId,
      this.contactPerson,
      this.requestedDeliveryDate,
      this.budget,
      this.assignedTo,
      this.notes,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  ablehnen(): CustomerInquiry {
    if (this.status === CustomerInquiryStatus.ABGELEHNT) {
      throw new Error('Anfrage ist bereits abgelehnt')
    }
    return new CustomerInquiry(
      this.id,
      this.inquiryNumber,
      this.customerId,
      this.type,
      this.subject,
      this.description,
      this.priority,
      this.currency,
      CustomerInquiryStatus.ABGELEHNT,
      this.tenantId,
      this.contactPerson,
      this.requestedDeliveryDate,
      this.budget,
      this.assignedTo,
      this.notes,
      this.version + 1,
      this.createdAt,
      new Date(),
      this.deletedAt
    )
  }

  istUeberfaellig(): boolean {
    if (!this.requestedDeliveryDate) return false
    return new Date() > this.requestedDeliveryDate
  }

  istDringend(): boolean {
    return this.priority === InquiryPriority.DRINGEND
  }

  getTageBisFaelligkeit(): number | null {
    if (!this.requestedDeliveryDate) return null
    const diffTime = this.requestedDeliveryDate.getTime() - new Date().getTime()
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  }

  hatBudget(): boolean {
    return this.budget !== undefined && this.budget > 0
  }

  /**
   * Rekonstruiert eine CustomerInquiry aus API-Payload (z. B. CRM-Gateway),
   * wenn kein eigenes Prisma-Model im ERP-Domain vorliegt.
   */
  static fromPayload(raw: Record<string, unknown>): CustomerInquiry {
    const id = String(raw.id ?? '').trim()
    if (!id) {
      throw new Error('CustomerInquiry.id ist erforderlich')
    }
    const parseDate = (v: unknown): Date | undefined => {
      if (v === undefined || v === null || v === '') return undefined
      const d = new Date(String(v))
      return Number.isNaN(d.getTime()) ? undefined : d
    }
    const coerceEnum = <T extends string>(val: unknown, allowed: readonly T[], fallback: T): T => {
      const s = String(val ?? '').trim()
      return (allowed as readonly string[]).includes(s) ? (s as T) : fallback
    }

    return new CustomerInquiry(
      id,
      String(raw.inquiryNumber ?? raw.inquiry_number ?? ''),
      String(raw.customerId ?? raw.customer_id ?? ''),
      coerceEnum(raw.type, Object.values(InquiryType), InquiryType.STANDARD),
      String(raw.subject ?? ''),
      String(raw.description ?? ''),
      coerceEnum(raw.priority, Object.values(InquiryPriority), InquiryPriority.NORMAL),
      String(raw.currency ?? 'EUR'),
      coerceEnum(raw.status, Object.values(CustomerInquiryStatus), CustomerInquiryStatus.EINGEGANGEN),
      String(raw.tenantId ?? raw.tenant_id ?? ''),
      raw.contactPerson !== undefined ? String(raw.contactPerson) : raw.contact_person !== undefined ? String(raw.contact_person) : undefined,
      parseDate(raw.requestedDeliveryDate ?? raw.requested_delivery_date),
      raw.budget !== undefined ? Number(raw.budget) : undefined,
      raw.assignedTo !== undefined ? String(raw.assignedTo) : raw.assigned_to !== undefined ? String(raw.assigned_to) : undefined,
      raw.notes !== undefined ? String(raw.notes) : undefined,
      raw.version !== undefined ? Number(raw.version) : 0,
      parseDate(raw.createdAt ?? raw.created_at) ?? new Date(),
      parseDate(raw.updatedAt ?? raw.updated_at) ?? new Date(),
      parseDate(raw.deletedAt ?? raw.deleted_at)
    )
  }
}