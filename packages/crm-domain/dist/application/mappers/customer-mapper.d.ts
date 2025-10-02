import type { Customer, CustomerFilters, CreateCustomerInput, UpdateCustomerInput, CustomerId } from '../../core/entities/customer';
import type { CreateCustomerDTO, CustomerDTO, UpdateCustomerDTO } from '../dto/customer-dto';
export declare function toCustomerDTO(customer: Customer): CustomerDTO;
export declare function toCreateCustomerInput(dto: CreateCustomerDTO): CreateCustomerInput;
export declare function toUpdateCustomerInput(dto: UpdateCustomerDTO): UpdateCustomerInput;
export declare function toCustomerFilters(query: GetCustomersQueryLike): CustomerFilters;
export declare const toCustomerId: (value: string) => CustomerId;
export interface GetCustomersQueryLike {
    search?: string;
    status?: CustomerFilters['status'];
    type?: CustomerFilters['type'];
    tags?: string[];
    limit?: number;
    offset?: number;
}
//# sourceMappingURL=customer-mapper.d.ts.map