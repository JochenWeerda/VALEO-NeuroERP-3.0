/**
 * User Entity for VALEO NeuroERP 3.0
 * Core user management entity
 */
import { AuditableEntity } from './base-entity.js';
export class User extends AuditableEntity {
    _username;
    _email;
    _firstName;
    _lastName;
    _phoneNumber;
    _address;
    _isActive;
    _isEmailVerified;
    _roles;
    _tenantId;
    _lastLoginAt;
    constructor(props) {
        super(props.id, props.createdAt, props.updatedAt, props.version, props.createdBy, props.updatedBy);
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
    get username() {
        return this._username;
    }
    get email() {
        return this._email;
    }
    get firstName() {
        return this._firstName;
    }
    get lastName() {
        return this._lastName;
    }
    get fullName() {
        return `${this._firstName} ${this._lastName}`;
    }
    get phoneNumber() {
        return this._phoneNumber;
    }
    get address() {
        return this._address;
    }
    get isActive() {
        return this._isActive;
    }
    get isEmailVerified() {
        return this._isEmailVerified;
    }
    get roles() {
        return [...this._roles];
    }
    get tenantId() {
        return this._tenantId;
    }
    get lastLoginAt() {
        return this._lastLoginAt;
    }
    // Business methods
    updateProfile(firstName, lastName, phoneNumber, address, updatedBy) {
        this._firstName = firstName;
        this._lastName = lastName;
        this._phoneNumber = phoneNumber;
        this._address = address;
        this.markAsUpdated(updatedBy);
    }
    updateEmail(email, updatedBy) {
        this._email = email;
        this._isEmailVerified = false;
        this.markAsUpdated(updatedBy);
    }
    verifyEmail(updatedBy) {
        this._isEmailVerified = true;
        this.markAsUpdated(updatedBy);
    }
    activate(updatedBy) {
        this._isActive = true;
        this.markAsUpdated(updatedBy);
    }
    deactivate(updatedBy) {
        this._isActive = false;
        this.markAsUpdated(updatedBy);
    }
    addRole(roleId, updatedBy) {
        if (!this._roles.includes(roleId)) {
            this._roles.push(roleId);
            this.markAsUpdated(updatedBy);
        }
    }
    removeRole(roleId, updatedBy) {
        const index = this._roles.indexOf(roleId);
        if (index > -1) {
            this._roles.splice(index, 1);
            this.markAsUpdated(updatedBy);
        }
    }
    hasRole(roleId) {
        return this._roles.includes(roleId);
    }
    recordLogin(updatedBy) {
        this._lastLoginAt = new Date();
        this.markAsUpdated(updatedBy);
    }
    changeTenant(newTenantId, updatedBy) {
        this._tenantId = newTenantId;
        this.markAsUpdated(updatedBy);
    }
    // Validation methods
    canLogin() {
        return this._isActive && this._isEmailVerified;
    }
    isInTenant(tenantId) {
        return this._tenantId === tenantId;
    }
}
//# sourceMappingURL=user.js.map