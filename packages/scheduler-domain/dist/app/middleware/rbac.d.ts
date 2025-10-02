import { FastifyRequest, FastifyReply } from 'fastify';
export interface PermissionRequirement {
    roles?: readonly string[];
    permissions?: readonly string[];
    requireAll?: boolean;
}
export declare function requirePermissions(requirements: PermissionRequirement): (request: FastifyRequest, reply: FastifyReply) => Promise<void>;
export declare const Permissions: {
    readonly CREATE_SCHEDULE: {
        readonly permissions: readonly ["schedules:create"];
    };
    readonly READ_SCHEDULE: {
        readonly permissions: readonly ["schedules:read"];
    };
    readonly UPDATE_SCHEDULE: {
        readonly permissions: readonly ["schedules:update"];
    };
    readonly DELETE_SCHEDULE: {
        readonly permissions: readonly ["schedules:delete"];
    };
    readonly EXECUTE_SCHEDULE: {
        readonly permissions: readonly ["schedules:execute"];
    };
    readonly ADMIN_SCHEDULES: {
        readonly roles: readonly ["admin", "scheduler-admin"];
    };
    readonly VIEW_ALL_SCHEDULES: {
        readonly permissions: readonly ["schedules:read-all"];
    };
    readonly MANAGE_WORKERS: {
        readonly permissions: readonly ["workers:manage"];
    };
    readonly VIEW_WORKERS: {
        readonly permissions: readonly ["workers:read"];
    };
};
export declare const requireScheduleRead: (request: FastifyRequest, reply: FastifyReply) => Promise<void>;
export declare const requireScheduleWrite: (request: FastifyRequest, reply: FastifyReply) => Promise<void>;
export declare const requireScheduleCreate: (request: FastifyRequest, reply: FastifyReply) => Promise<void>;
export declare const requireScheduleDelete: (request: FastifyRequest, reply: FastifyReply) => Promise<void>;
export declare const requireAdminAccess: (request: FastifyRequest, reply: FastifyReply) => Promise<void>;
//# sourceMappingURL=rbac.d.ts.map