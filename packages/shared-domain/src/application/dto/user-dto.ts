/**
 * User DTOs for VALEO NeuroERP 3.0
 * Data Transfer Objects with Zod validation
 */

import { z } from 'zod';
import type { UserId, RoleId, TenantId } from '../../domain/value-objects/branded-types.js';

// Base User DTO Schema
const UserDtoSchema = z.object({
  id: z.string(),
  username: z.string().min(3).max(50),
  email: z.string().email(),
  firstName: z.string().min(1).max(100),
  lastName: z.string().min(1).max(100),
  phoneNumber: z.string().optional(),
  address: z.object({
    street: z.string(),
    city: z.string(),
    postalCode: z.string(),
    country: z.string(),
    state: z.string().optional()
  }).optional(),
  isActive: z.boolean(),
  isEmailVerified: z.boolean(),
  roles: z.array(z.string()),
  tenantId: z.string(),
  lastLoginAt: z.string().datetime().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  version: z.number()
});

// Create User DTO Schema
const CreateUserDtoSchema = z.object({
  username: z.string().min(3).max(50),
  email: z.string().email(),
  firstName: z.string().min(1).max(100),
  lastName: z.string().min(1).max(100),
  phoneNumber: z.string().optional(),
  address: z.object({
    street: z.string(),
    city: z.string(),
    postalCode: z.string(),
    country: z.string(),
    state: z.string().optional()
  }).optional(),
  tenantId: z.string(),
  roles: z.array(z.string()).default([])
});

// Update User DTO Schema
const UpdateUserDtoSchema = z.object({
  firstName: z.string().min(1).max(100).optional(),
  lastName: z.string().min(1).max(100).optional(),
  phoneNumber: z.string().optional(),
  address: z.object({
    street: z.string(),
    city: z.string(),
    postalCode: z.string(),
    country: z.string(),
    state: z.string().optional()
  }).optional()
});

// User Search DTO Schema
const UserSearchDtoSchema = z.object({
  searchTerm: z.string().optional(),
  tenantId: z.string().optional(),
  roleId: z.string().optional(),
  isActive: z.boolean().optional(),
  isEmailVerified: z.boolean().optional()
});

// Pagination DTO Schema
const PaginationDtoSchema = z.object({
  page: z.number().min(1).default(1),
  pageSize: z.number().min(1).max(100).default(20),
  sortBy: z.string().optional(),
  sortDirection: z.enum(['ASC', 'DESC']).default('ASC')
});

// Type definitions
export type UserDto = z.infer<typeof UserDtoSchema>;
export type CreateUserDto = z.infer<typeof CreateUserDtoSchema>;
export type UpdateUserDto = z.infer<typeof UpdateUserDtoSchema>;
export type UserSearchDto = z.infer<typeof UserSearchDtoSchema>;
export type PaginationDto = z.infer<typeof PaginationDtoSchema>;

// Response DTOs
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

// Validation functions
export function validateUserDto(data: unknown): UserDto {
  return UserDtoSchema.parse(data);
}

export function validateCreateUserDto(data: unknown): CreateUserDto {
  return CreateUserDtoSchema.parse(data);
}

export function validateUpdateUserDto(data: unknown): UpdateUserDto {
  return UpdateUserDtoSchema.parse(data);
}

export function validateUserSearchDto(data: unknown): UserSearchDto {
  return UserSearchDtoSchema.parse(data);
}

export function validatePaginationDto(data: unknown): PaginationDto {
  return PaginationDtoSchema.parse(data);
}

// Transformation functions
export function toUserDto(user: any): UserDto {
  return {
    id: user.id,
    username: user.username,
    email: user.email.getValue ? user.email.getValue() : user.email,
    firstName: user.firstName,
    lastName: user.lastName,
    phoneNumber: user.phoneNumber?.getValue ? user.phoneNumber.getValue() : user.phoneNumber,
    address: user.address ? {
      street: user.address.street,
      city: user.address.city,
      postalCode: user.address.postalCode,
      country: user.address.country,
      state: user.address.state
    } : undefined,
    isActive: user.isActive,
    isEmailVerified: user.isEmailVerified,
    roles: user.roles,
    tenantId: user.tenantId,
    lastLoginAt: user.lastLoginAt?.toISOString(),
    createdAt: user.createdAt.toISOString(),
    updatedAt: user.updatedAt.toISOString(),
    version: user.version
  };
}

export function fromCreateUserDto(dto: CreateUserDto): any {
  return {
    username: dto.username,
    email: dto.email,
    firstName: dto.firstName,
    lastName: dto.lastName,
    phoneNumber: dto.phoneNumber,
    address: dto.address,
    tenantId: dto.tenantId,
    roles: dto.roles,
    isActive: true,
    isEmailVerified: false
  };
}

