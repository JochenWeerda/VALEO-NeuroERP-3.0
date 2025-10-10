/**
 * Role Entity for VALEO NeuroERP 3.0 HR Domain
 * HR-specific roles separate from system-wide roles
 */
import { z } from 'zod';
export declare const RoleSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    key: z.ZodString;
    name: z.ZodString;
    permissions: z.ZodArray<z.ZodString, "many">;
    editable: z.ZodBoolean;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: string;
    tenantId: string;
    createdAt: string;
    updatedAt: string;
    key: string;
    name: string;
    permissions: string[];
    editable: boolean;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
}, {
    id: string;
    tenantId: string;
    createdAt: string;
    updatedAt: string;
    key: string;
    name: string;
    permissions: string[];
    editable: boolean;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
}>;
export type Role = z.infer<typeof RoleSchema>;
export declare class RoleEntity {
    private readonly data;
    constructor(data: Role);
    get id(): string;
    get tenantId(): string;
    get key(): string;
    get name(): string;
    get permissions(): string[];
    get editable(): boolean;
    get createdAt(): string;
    get updatedAt(): string;
    hasPermission(permission: string): boolean;
    canEdit(): boolean;
    updateName(name: string, updatedBy?: string): RoleEntity;
    addPermission(permission: string, updatedBy?: string): RoleEntity;
    removePermission(permission: string, updatedBy?: string): RoleEntity;
    toJSON(): Role;
    private clone;
    static create(data: Omit<Role, 'id' | 'createdAt' | 'updatedAt'>): RoleEntity;
    static fromJSON(data: Role): RoleEntity;
}
//# sourceMappingURL=role.d.ts.map