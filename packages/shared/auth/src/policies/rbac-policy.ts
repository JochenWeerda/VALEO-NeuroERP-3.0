import { UserContext, PolicyResult, Role, Permission } from '../types/auth-types';

export interface RBACOptions {
  roles: Role[];
  permissions: Permission[];
  roleHierarchy?: Map<string, string[]>; // Role inheritance
}

export class RBACPolicy {
  private roles: Map<string, Role> = new Map();
  private permissions: Map<string, Permission> = new Map();
  private roleHierarchy: Map<string, string[]> = new Map();

  constructor(options: RBACOptions) {
    // Initialize roles
    options.roles.forEach(role => {
      this.roles.set(role.id, role);
      this.roles.set(role.name, role); // Allow lookup by name or ID
    });

    // Initialize permissions
    options.permissions.forEach(permission => {
      this.permissions.set(permission.resource + ':' + permission.action, permission);
    });

    // Initialize role hierarchy
    if (options.roleHierarchy) {
      this.roleHierarchy = options.roleHierarchy;
    }
  }

  /**
   * Check if user can perform action on resource
   */
  canAccess(user: UserContext, resource: string, action: string): PolicyResult {
    try {
      // Check each role the user has
      for (const roleName of user.roles) {
        const role = this.roles.get(roleName);
        if (!role || !role.isActive) {
          continue;
        }

        // Check if role has permission for this resource:action
        const hasPermission = this.checkRolePermission(role, resource, action);
        if (hasPermission.allowed) {
          return hasPermission;
        }

        // Check inherited roles
        const inheritedRoles = this.roleHierarchy.get(roleName) || [];
        for (const inheritedRoleName of inheritedRoles) {
          const inheritedRole = this.roles.get(inheritedRoleName);
          if (inheritedRole && inheritedRole.isActive) {
            const inheritedPermission = this.checkRolePermission(inheritedRole, resource, action);
            if (inheritedPermission.allowed) {
              return inheritedPermission;
            }
          }
        }
      }

      return {
        allowed: false,
        reason: `User ${user.userId} does not have permission to ${action} ${resource}`
      };

    } catch (error) {
      return {
        allowed: false,
        reason: `Policy evaluation failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * Check if a specific role has permission for resource:action
   */
  private checkRolePermission(role: Role, resource: string, action: string): PolicyResult {
    // Check role's direct permissions
    for (const permissionId of role.permissions) {
      const permission = this.permissions.get(permissionId);
      if (permission && this.matchesResourceAction(permission, resource, action)) {
        return {
          allowed: true,
          reason: `Role ${role.name} has permission ${permissionId}`
        };
      }
    }

    return {
      allowed: false,
      reason: `Role ${role.name} does not have permission for ${action} ${resource}`
    };
  }

  /**
   * Check if permission matches the requested resource and action
   */
  private matchesResourceAction(permission: Permission, resource: string, action: string): boolean {
    // Exact match
    if (permission.resource === resource && permission.action === action) {
      return true;
    }

    // Wildcard support (e.g., "shipment:*" matches "shipment:read")
    if (permission.resource === '*' || permission.resource === resource) {
      if ((permission.action as any) === '*' || permission.action === action) {
        return true;
      }
    }

    // Pattern matching (e.g., "shipment:*" for "shipment:read")
    const permissionPattern = `${permission.resource}:${permission.action}`;
    const requestedPattern = `${resource}:${action}`;

    if (permissionPattern.includes('*')) {
      const regex = new RegExp(permissionPattern.replace(/\*/g, '.*'));
      return regex.test(requestedPattern);
    }

    return false;
  }

  /**
   * Get all permissions for a user
   */
  getUserPermissions(user: UserContext): Permission[] {
    const permissions: Permission[] = [];

    for (const roleName of user.roles) {
      const role = this.roles.get(roleName);
      if (role && role.isActive) {
        // Add role's direct permissions
        for (const permissionId of role.permissions) {
          const permission = this.permissions.get(permissionId);
          if (permission) {
            permissions.push(permission);
          }
        }

        // Add inherited role permissions
        const inheritedRoles = this.roleHierarchy.get(roleName) || [];
        for (const inheritedRoleName of inheritedRoles) {
          const inheritedRole = this.roles.get(inheritedRoleName);
          if (inheritedRole && inheritedRole.isActive) {
            for (const permissionId of inheritedRole.permissions) {
              const permission = this.permissions.get(permissionId);
              if (permission) {
                permissions.push(permission);
              }
            }
          }
        }
      }
    }

    // Remove duplicates
    return permissions.filter((permission, index, self) =>
      index === self.findIndex(p => p.resource === permission.resource && p.action === permission.action)
    );
  }

  /**
   * Add or update role
   */
  addRole(role: Role): void {
    this.roles.set(role.id, role);
    this.roles.set(role.name, role);
  }

  /**
   * Remove role
   */
  removeRole(roleId: string): void {
    const role = this.roles.get(roleId);
    if (role) {
      this.roles.delete(roleId);
      this.roles.delete(role.name);
    }
  }

  /**
   * Add or update permission
   */
  addPermission(permission: Permission): void {
    this.permissions.set(permission.resource + ':' + permission.action, permission);
  }

  /**
   * Get all roles
   */
  getRoles(): Role[] {
    return Array.from(this.roles.values()).filter((role, index, self) =>
      index === self.findIndex(r => r.id === role.id)
    );
  }

  /**
   * Get all permissions
   */
  getPermissions(): Permission[] {
    return Array.from(this.permissions.values());
  }
}