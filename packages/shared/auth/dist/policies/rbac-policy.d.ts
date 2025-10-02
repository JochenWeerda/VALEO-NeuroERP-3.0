import { UserContext, PolicyResult, Role, Permission } from '../types/auth-types';
export interface RBACOptions {
    roles: Role[];
    permissions: Permission[];
    roleHierarchy?: Map<string, string[]>;
}
export declare class RBACPolicy {
    private roles;
    private permissions;
    private roleHierarchy;
    constructor(options: RBACOptions);
    /**
     * Check if user can perform action on resource
     */
    canAccess(user: UserContext, resource: string, action: string): PolicyResult;
    /**
     * Check if a specific role has permission for resource:action
     */
    private checkRolePermission;
    /**
     * Check if permission matches the requested resource and action
     */
    private matchesResourceAction;
    /**
     * Get all permissions for a user
     */
    getUserPermissions(user: UserContext): Permission[];
    /**
     * Add or update role
     */
    addRole(role: Role): void;
    /**
     * Remove role
     */
    removeRole(roleId: string): void;
    /**
     * Add or update permission
     */
    addPermission(permission: Permission): void;
    /**
     * Get all roles
     */
    getRoles(): Role[];
    /**
     * Get all permissions
     */
    getPermissions(): Permission[];
}
//# sourceMappingURL=rbac-policy.d.ts.map