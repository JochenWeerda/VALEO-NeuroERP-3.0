import { randomUUID } from 'crypto';

export type SupplierId = string & { readonly __brand: 'SupplierId' };
export type SupplierContactId = string & { readonly __brand: 'SupplierContactId' };

export enum SupplierStatus {
  DRAFT = 'draft',
  ONBOARDING = 'onboarding',
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  DEACTIVATED = 'deactivated'
}

export enum SupplierType {
  INDIVIDUAL = 'individual',
  COMPANY = 'company',
  PARTNERSHIP = 'partnership',
  CORPORATION = 'corporation'
}

export enum SupplierCategory {
  STRATEGIC = 'strategic',
  PREFERRED = 'preferred',
  APPROVED = 'approved',
  PROSPECTIVE = 'prospective'
}

export interface SupplierContact {
  id: SupplierContactId;
  supplierId: SupplierId;
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  mobile?: string;
  role: string;
  isPrimary: boolean;
  department?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface SupplierBankAccount {
  id: string;
  supplierId: SupplierId;
  bankName: string;
  accountHolder: string;
  iban: string;
  bic?: string;
  currency: string;
  isPrimary: boolean;
  verified: boolean;
  createdAt: Date;
}

export interface SupplierAddress {
  id: string;
  supplierId: SupplierId;
  type: 'billing' | 'shipping' | 'legal';
  street: string;
  city: string;
  postalCode: string;
  country: string;
  region?: string;
  isPrimary: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface SupplierClassification {
  id: string;
  supplierId: SupplierId;
  category: SupplierCategory;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  industryCode?: string;
  sizeCategory: 'micro' | 'small' | 'medium' | 'large' | 'enterprise';
  certifications: string[];
  complianceFlags: string[];
  createdAt: Date;
  updatedAt: Date;
}

export class Supplier {
  public readonly id: SupplierId;
  public name: string;
  public legalName: string | undefined;
  public type: SupplierType;
  public status: SupplierStatus;
  public category: SupplierCategory;

  // Legal & Tax Information
  public vatId: string | undefined;
  public taxId: string | undefined;
  public dunsNumber: string | undefined;
  public registrationNumber: string | undefined;
  public country: string;

  // Contact & Address Information
  public email: string | undefined;
  public phone: string | undefined;
  public website: string | undefined;

  // Business Information
  public industry: string | undefined;
  public description: string | undefined;
  public paymentTerms: string | undefined;
  public currency: string;

  // System Information
  public tenantId: string;
  public createdBy: string;
  public approvedBy?: string;
  public approvedAt?: Date;
  public readonly createdAt: Date;
  public updatedAt: Date;

  // Related Entities
  public contacts: SupplierContact[] = [];
  public addresses: SupplierAddress[] = [];
  public bankAccounts: SupplierBankAccount[] = [];
  public classifications: SupplierClassification[] = [];

  constructor(props: {
    id?: SupplierId;
    name: string;
    legalName?: string;
    type: SupplierType;
    status?: SupplierStatus;
    category?: SupplierCategory;
    vatId?: string;
    taxId?: string;
    dunsNumber?: string;
    registrationNumber?: string;
    country: string;
    email?: string;
    phone?: string;
    website?: string;
    industry?: string;
    description?: string;
    paymentTerms?: string;
    currency?: string;
    tenantId: string;
    createdBy: string;
  }) {
    this.id = props.id || (randomUUID() as SupplierId);
    this.name = props.name;
    this.legalName = props.legalName;
    this.type = props.type;
    this.status = props.status || SupplierStatus.DRAFT;
    this.category = props.category || SupplierCategory.PROSPECTIVE;
    this.vatId = props.vatId;
    this.taxId = props.taxId;
    this.dunsNumber = props.dunsNumber;
    this.registrationNumber = props.registrationNumber;
    this.country = props.country;
    this.email = props.email;
    this.phone = props.phone;
    this.website = props.website;
    this.industry = props.industry;
    this.description = props.description;
    this.paymentTerms = props.paymentTerms;
    this.currency = props.currency || 'EUR';
    this.tenantId = props.tenantId;
    this.createdBy = props.createdBy;
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  // Business Logic Methods
  public activate(approvedBy: string): void {
    if (this.status !== SupplierStatus.ONBOARDING) {
      throw new Error('Supplier must be in onboarding status to activate');
    }
    this.status = SupplierStatus.ACTIVE;
    this.approvedBy = approvedBy;
    this.approvedAt = new Date();
    this.updatedAt = new Date();
  }

  public suspend(reason: string): void {
    if (this.status !== SupplierStatus.ACTIVE) {
      throw new Error('Only active suppliers can be suspended');
    }
    this.status = SupplierStatus.SUSPENDED;
    this.updatedAt = new Date();
    // TODO: Add suspension reason tracking
  }

  public reactivate(): void {
    if (this.status !== SupplierStatus.SUSPENDED) {
      throw new Error('Only suspended suppliers can be reactivated');
    }
    this.status = SupplierStatus.ACTIVE;
    this.updatedAt = new Date();
  }

  public deactivate(): void {
    this.status = SupplierStatus.DEACTIVATED;
    this.updatedAt = new Date();
  }

  public updateCategory(category: SupplierCategory): void {
    this.category = category;
    this.updatedAt = new Date();
  }

  // Contact Management
  public addContact(contact: Omit<SupplierContact, 'id' | 'supplierId' | 'createdAt' | 'updatedAt'>): SupplierContact {
    const newContact: SupplierContact = {
      id: randomUUID() as SupplierContactId,
      supplierId: this.id,
      ...contact,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.contacts.push(newContact);
    return newContact;
  }

  public removeContact(contactId: SupplierContactId): boolean {
    const index = this.contacts.findIndex(c => c.id === contactId);
    if (index === -1) return false;

    this.contacts.splice(index, 1);
    return true;
  }

  // Address Management
  public addAddress(address: Omit<SupplierAddress, 'id' | 'supplierId' | 'createdAt' | 'updatedAt'>): SupplierAddress {
    const newAddress: SupplierAddress = {
      id: randomUUID(),
      supplierId: this.id,
      ...address,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.addresses.push(newAddress);
    return newAddress;
  }

  // Bank Account Management
  public addBankAccount(account: Omit<SupplierBankAccount, 'id' | 'supplierId' | 'createdAt'>): SupplierBankAccount {
    const newAccount: SupplierBankAccount = {
      id: randomUUID(),
      supplierId: this.id,
      ...account,
      createdAt: new Date()
    };

    this.bankAccounts.push(newAccount);
    return newAccount;
  }

  // Validation Methods
  public validateForActivation(): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!this.vatId && !this.taxId) {
      errors.push('Either VAT ID or Tax ID must be provided');
    }

    if (this.contacts.length === 0) {
      errors.push('At least one contact must be defined');
    }

    if (this.addresses.length === 0) {
      errors.push('At least one address must be defined');
    }

    if (this.bankAccounts.length === 0) {
      errors.push('At least one bank account must be defined');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  public getPrimaryContact(): SupplierContact | undefined {
    return this.contacts.find(c => c.isPrimary);
  }

  public getPrimaryAddress(type: 'billing' | 'shipping' | 'legal' = 'billing'): SupplierAddress | undefined {
    return this.addresses.find(a => a.type === type && a.isPrimary);
  }

  public getPrimaryBankAccount(): SupplierBankAccount | undefined {
    return this.bankAccounts.find(a => a.isPrimary);
  }

  public updateTimestamp(): void {
    this.updatedAt = new Date();
  }
}