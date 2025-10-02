/**
 * User DTOs for VALEO NeuroERP 3.0
 * Data Transfer Objects with Zod validation
 */
import { z } from 'zod';
declare const UserDtoSchema: z.ZodObject<{
    id: z.ZodString;
    username: z.ZodString;
    email: z.ZodString;
    firstName: z.ZodString;
    lastName: z.ZodString;
    phoneNumber: z.ZodOptional<z.ZodString>;
    address: z.ZodOptional<z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        state: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }>>;
    isActive: z.ZodBoolean;
    isEmailVerified: z.ZodBoolean;
    roles: z.ZodArray<z.ZodString, "many">;
    tenantId: z.ZodString;
    lastLoginAt: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    version: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    id: string;
    version: number;
    username: string;
    email: string;
    firstName: string;
    lastName: string;
    isActive: boolean;
    isEmailVerified: boolean;
    roles: string[];
    tenantId: string;
    createdAt: string;
    updatedAt: string;
    phoneNumber?: string | undefined;
    address?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    } | undefined;
    lastLoginAt?: string | undefined;
}, {
    id: string;
    version: number;
    username: string;
    email: string;
    firstName: string;
    lastName: string;
    isActive: boolean;
    isEmailVerified: boolean;
    roles: string[];
    tenantId: string;
    createdAt: string;
    updatedAt: string;
    phoneNumber?: string | undefined;
    address?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    } | undefined;
    lastLoginAt?: string | undefined;
}>;
declare const CreateUserDtoSchema: z.ZodObject<{
    username: z.ZodString;
    email: z.ZodString;
    firstName: z.ZodString;
    lastName: z.ZodString;
    phoneNumber: z.ZodOptional<z.ZodString>;
    address: z.ZodOptional<z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        state: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }>>;
    tenantId: z.ZodString;
    roles: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    username: string;
    email: string;
    firstName: string;
    lastName: string;
    roles: string[];
    tenantId: string;
    phoneNumber?: string | undefined;
    address?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    } | undefined;
}, {
    username: string;
    email: string;
    firstName: string;
    lastName: string;
    tenantId: string;
    phoneNumber?: string | undefined;
    address?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    } | undefined;
    roles?: string[] | undefined;
}>;
declare const UpdateUserDtoSchema: z.ZodObject<{
    firstName: z.ZodOptional<z.ZodString>;
    lastName: z.ZodOptional<z.ZodString>;
    phoneNumber: z.ZodOptional<z.ZodString>;
    address: z.ZodOptional<z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        state: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }>>;
}, "strip", z.ZodTypeAny, {
    firstName?: string | undefined;
    lastName?: string | undefined;
    phoneNumber?: string | undefined;
    address?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    } | undefined;
}, {
    firstName?: string | undefined;
    lastName?: string | undefined;
    phoneNumber?: string | undefined;
    address?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    } | undefined;
}>;
declare const UserSearchDtoSchema: z.ZodObject<{
    searchTerm: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodOptional<z.ZodString>;
    roleId: z.ZodOptional<z.ZodString>;
    isActive: z.ZodOptional<z.ZodBoolean>;
    isEmailVerified: z.ZodOptional<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    isActive?: boolean | undefined;
    isEmailVerified?: boolean | undefined;
    tenantId?: string | undefined;
    searchTerm?: string | undefined;
    roleId?: string | undefined;
}, {
    isActive?: boolean | undefined;
    isEmailVerified?: boolean | undefined;
    tenantId?: string | undefined;
    searchTerm?: string | undefined;
    roleId?: string | undefined;
}>;
declare const PaginationDtoSchema: z.ZodObject<{
    page: z.ZodDefault<z.ZodNumber>;
    pageSize: z.ZodDefault<z.ZodNumber>;
    sortBy: z.ZodOptional<z.ZodString>;
    sortDirection: z.ZodDefault<z.ZodEnum<["ASC", "DESC"]>>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    sortDirection: "ASC" | "DESC";
    sortBy?: string | undefined;
}, {
    page?: number | undefined;
    pageSize?: number | undefined;
    sortBy?: string | undefined;
    sortDirection?: "ASC" | "DESC" | undefined;
}>;
export type UserDto = z.infer<typeof UserDtoSchema>;
export type CreateUserDto = z.infer<typeof CreateUserDtoSchema>;
export type UpdateUserDto = z.infer<typeof UpdateUserDtoSchema>;
export type UserSearchDto = z.infer<typeof UserSearchDtoSchema>;
export type PaginationDto = z.infer<typeof PaginationDtoSchema>;
export interface UserListResponseDto {
    users: UserDto[];
    pagination: {
        page: number;
        pageSize: number;
        totalItems: number;
        totalPages: number;
        hasNext: boolean;
        hasPrevious: boolean;
    };
}
export interface UserStatsDto {
    totalUsers: number;
    activeUsers: number;
    inactiveUsers: number;
    usersByTenant: Record<string, number>;
    usersByRole: Record<string, number>;
}
export declare function validateUserDto(data: unknown): UserDto;
export declare function validateCreateUserDto(data: unknown): CreateUserDto;
export declare function validateUpdateUserDto(data: unknown): UpdateUserDto;
export declare function validateUserSearchDto(data: unknown): UserSearchDto;
export declare function validatePaginationDto(data: unknown): PaginationDto;
export declare function toUserDto(user: any): UserDto;
export declare function fromCreateUserDto(dto: CreateUserDto): any;
export {};
//# sourceMappingURL=user-dto.d.ts.map