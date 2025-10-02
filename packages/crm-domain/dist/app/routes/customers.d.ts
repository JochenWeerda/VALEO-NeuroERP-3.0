import { FastifyInstance } from 'fastify';
import { CustomerService } from '../../domain/services';
export declare function registerCustomerRoutes(fastify: FastifyInstance, services: {
    customerService: CustomerService;
}): Promise<void>;
//***REMOVED*** sourceMappingURL=customers.d.ts.map