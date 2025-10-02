/**
 * User Entity for VALEO NeuroERP 3.0
 * Core user management entity
 */

import { AuditableEntity } from './base-entity.js';
import type { UserId, RoleId, TenantId, AuditId } from '../value-objects/branded-types.js';
import { Email, PhoneNumber, Address } from '../value-objects/common-value-objects.js';

export interface UserProps {
  id: UserId;
  username: string;
  email: Email;
  firstName: string;
  lastName: string;
  phoneNumber?: PhoneNumber;
  address?: Address;
  isActive: boolean;
  isEmailVerified: boolean;
  roles: RoleId[];
  tenantId: TenantId;
  lastLoginAt?: Date;
  createdAt?: Date;
  updatedAt?: Date;
  version?: number;
  createdBy?: AuditId;
  updatedBy?: AuditId;
}

export class User extends AuditableEntity {
  private _username: string;
  private _email: Email;
  private _firstName: string;
  private _lastName: string;
  private _phoneNumber?: PhoneNumber;
  private _address?: Address;
  private _isActive: boolean;
  private _isEmailVerified: boolean;
  private _roles: RoleId[];
  private _tenantId: TenantId;
  private _lastLoginAt?: Date;

  constructor(props: UserProps) {
    super(
      props.id as any,
      props.createdAt,
      props.updatedAt,
      props.version,
      props.createdBy,
      props.updatedBy
    );

    this._username = props.username;
    this._email = props.email;
    this._firstName = props.firstName;
    this._lastName = props.lastName;
    this._phoneNumber = props.phoneNumber;
    this._address = props.address;
    this._isActive = props.isActive;
    this._isEmailVerified = props.isEmailVerified;
    this._roles = [...props.roles];
    this._tenantId = props.tenantId;
    this._lastLoginAt = props.lastLoginAt;
  }

  get username(): string {
    return this._username;
  }

  get email(): Email {
    return this._email;
  }

  get firstName(): string {
    return this._firstName;
  }

  get lastName(): string {
    return this._lastName;
  }

  get fullName(): string {
    return `${this._firstName} ${this._lastName}`;
  }

  get phoneNumber(): PhoneNumber | undefined {
    return this._phoneNumber;
  }

  get address(): Address | undefined {
    return this._address;
  }

  get isActive(): boolean {
    return this._isActive;
  }

  get isEmailVerified(): boolean {
    return this._isEmailVerified;
  }

  get roles(): RoleId[] {
    return [...this._roles];
  }

  get tenantId(): TenantId {
    return this._tenantId;
  }

  get lastLoginAt(): Date | undefined {
    return this._lastLoginAt;
  }

  // Business methods
  updateProfile(
    firstName: string,
    lastName: string,
    phoneNumber?: PhoneNumber,
    address?: Address,
    updatedBy?: AuditId
  ): void {
    this._firstName = firstName;
    this._lastName = lastName;
    this._phoneNumber = phoneNumber;
    this._address = address;
    this.markAsUpdated(updatedBy);
  }

  updateEmail(email: Email, updatedBy?: AuditId): void {
    this._email = email;
    this._isEmailVerified = false;
    this.markAsUpdated(updatedBy);
  }

  verifyEmail(updatedBy?: AuditId): void {
    this._isEmailVerified = true;
    this.markAsUpdated(updatedBy);
  }

  activate(updatedBy?: AuditId): void {
    this._isActive = true;
    this.markAsUpdated(updatedBy);
  }

  deactivate(updatedBy?: AuditId): void {
    this._isActive = false;
    this.markAsUpdated(updatedBy);
  }

  addRole(roleId: RoleId, updatedBy?: AuditId): void {
    if (!this._roles.includes(roleId)) {
      this._roles.push(roleId);
      this.markAsUpdated(updatedBy);
    }
  }

  removeRole(roleId: RoleId, updatedBy?: AuditId): void {
    const index = this._roles.indexOf(roleId);
    if (index > -1) {
      this._roles.splice(index, 1);
      this.markAsUpdated(updatedBy);
    }
  }

  hasRole(roleId: RoleId): boolean {
    return this._roles.includes(roleId);
  }

  recordLogin(updatedBy?: AuditId): void {
    this._lastLoginAt = new Date();
    this.markAsUpdated(updatedBy);
  }

  changeTenant(newTenantId: TenantId, updatedBy?: AuditId): void {
    this._tenantId = newTenantId;
    this.markAsUpdated(updatedBy);
  }

  // Validation methods
  canLogin(): boolean {
    return this._isActive && this._isEmailVerified;
  }

  isInTenant(tenantId: TenantId): boolean {
    return this._tenantId === tenantId;
  }
}
