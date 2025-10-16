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
}