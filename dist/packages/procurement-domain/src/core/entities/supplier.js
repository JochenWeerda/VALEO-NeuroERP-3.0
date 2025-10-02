"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Supplier = exports.SupplierCategory = exports.SupplierType = exports.SupplierStatus = void 0;
const crypto_1 = require("crypto");
var SupplierStatus;
(function (SupplierStatus) {
    SupplierStatus["DRAFT"] = "draft";
    SupplierStatus["ONBOARDING"] = "onboarding";
    SupplierStatus["ACTIVE"] = "active";
    SupplierStatus["SUSPENDED"] = "suspended";
    SupplierStatus["DEACTIVATED"] = "deactivated";
})(SupplierStatus || (exports.SupplierStatus = SupplierStatus = {}));
var SupplierType;
(function (SupplierType) {
    SupplierType["INDIVIDUAL"] = "individual";
    SupplierType["COMPANY"] = "company";
    SupplierType["PARTNERSHIP"] = "partnership";
    SupplierType["CORPORATION"] = "corporation";
})(SupplierType || (exports.SupplierType = SupplierType = {}));
var SupplierCategory;
(function (SupplierCategory) {
    SupplierCategory["STRATEGIC"] = "strategic";
    SupplierCategory["PREFERRED"] = "preferred";
    SupplierCategory["APPROVED"] = "approved";
    SupplierCategory["PROSPECTIVE"] = "prospective";
})(SupplierCategory || (exports.SupplierCategory = SupplierCategory = {}));
class Supplier {
    id;
    name;
    legalName;
    type;
    status;
    category;
    // Legal & Tax Information
    vatId;
    taxId;
    dunsNumber;
    registrationNumber;
    country;
    // Contact & Address Information
    email;
    phone;
    website;
    // Business Information
    industry;
    description;
    paymentTerms;
    currency;
    // System Information
    tenantId;
    createdBy;
    approvedBy;
    approvedAt;
    createdAt;
    updatedAt;
    // Related Entities
    contacts = [];
    addresses = [];
    bankAccounts = [];
    classifications = [];
    constructor(props) {
        this.id = props.id || (0, crypto_1.randomUUID)();
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
    activate(approvedBy) {
        if (this.status !== SupplierStatus.ONBOARDING) {
            throw new Error('Supplier must be in onboarding status to activate');
        }
        this.status = SupplierStatus.ACTIVE;
        this.approvedBy = approvedBy;
        this.approvedAt = new Date();
        this.updatedAt = new Date();
    }
    suspend(reason) {
        if (this.status !== SupplierStatus.ACTIVE) {
            throw new Error('Only active suppliers can be suspended');
        }
        this.status = SupplierStatus.SUSPENDED;
        this.updatedAt = new Date();
        // TODO: Add suspension reason tracking
    }
    reactivate() {
        if (this.status !== SupplierStatus.SUSPENDED) {
            throw new Error('Only suspended suppliers can be reactivated');
        }
        this.status = SupplierStatus.ACTIVE;
        this.updatedAt = new Date();
    }
    deactivate() {
        this.status = SupplierStatus.DEACTIVATED;
        this.updatedAt = new Date();
    }
    updateCategory(category) {
        this.category = category;
        this.updatedAt = new Date();
    }
    // Contact Management
    addContact(contact) {
        const newContact = {
            id: (0, crypto_1.randomUUID)(),
            supplierId: this.id,
            ...contact,
            createdAt: new Date(),
            updatedAt: new Date()
        };
        this.contacts.push(newContact);
        return newContact;
    }
    removeContact(contactId) {
        const index = this.contacts.findIndex(c => c.id === contactId);
        if (index === -1)
            return false;
        this.contacts.splice(index, 1);
        return true;
    }
    // Address Management
    addAddress(address) {
        const newAddress = {
            id: (0, crypto_1.randomUUID)(),
            supplierId: this.id,
            ...address,
            createdAt: new Date(),
            updatedAt: new Date()
        };
        this.addresses.push(newAddress);
        return newAddress;
    }
    // Bank Account Management
    addBankAccount(account) {
        const newAccount = {
            id: (0, crypto_1.randomUUID)(),
            supplierId: this.id,
            ...account,
            createdAt: new Date()
        };
        this.bankAccounts.push(newAccount);
        return newAccount;
    }
    // Validation Methods
    validateForActivation() {
        const errors = [];
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
    getPrimaryContact() {
        return this.contacts.find(c => c.isPrimary);
    }
    getPrimaryAddress(type = 'billing') {
        return this.addresses.find(a => a.type === type && a.isPrimary);
    }
    getPrimaryBankAccount() {
        return this.bankAccounts.find(a => a.isPrimary);
    }
    updateTimestamp() {
        this.updatedAt = new Date();
    }
}
exports.Supplier = Supplier;
