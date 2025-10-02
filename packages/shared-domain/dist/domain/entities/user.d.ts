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
export declare class User extends AuditableEntity {
    private _username;
    private _email;
    private _firstName;
    private _lastName;
    private _phoneNumber?;
    private _address?;
    private _isActive;
    private _isEmailVerified;
    private _roles;
    private _tenantId;
    private _lastLoginAt?;
    constructor(props: UserProps);
    get username(): string;
    get email(): Email;
    get firstName(): string;
    get lastName(): string;
    get fullName(): string;
    get phoneNumber(): PhoneNumber | undefined;
    get address(): Address | undefined;
    get isActive(): boolean;
    get isEmailVerified(): boolean;
    get roles(): RoleId[];
    get tenantId(): TenantId;
    get lastLoginAt(): Date | undefined;
    updateProfile(firstName: string, lastName: string, phoneNumber?: PhoneNumber, address?: Address, updatedBy?: AuditId): void;
    updateEmail(email: Email, updatedBy?: AuditId): void;
    verifyEmail(updatedBy?: AuditId): void;
    activate(updatedBy?: AuditId): void;
    deactivate(updatedBy?: AuditId): void;
    addRole(roleId: RoleId, updatedBy?: AuditId): void;
    removeRole(roleId: RoleId, updatedBy?: AuditId): void;
    hasRole(roleId: RoleId): boolean;
    recordLogin(updatedBy?: AuditId): void;
    changeTenant(newTenantId: TenantId, updatedBy?: AuditId): void;
    canLogin(): boolean;
    isInTenant(tenantId: TenantId): boolean;
}
//# sourceMappingURL=user.d.ts.map