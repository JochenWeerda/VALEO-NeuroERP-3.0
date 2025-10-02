import { Request, Response } from 'express';
export declare class CRMApiController {
    createCustomer(req: Request, res: Response): Promise<void>;
    getCustomer(req: Request, res: Response): Promise<void>;
    updateCustomer(req: Request, res: Response): Promise<void>;
    deleteCustomer(req: Request, res: Response): Promise<void>;
    getCustomers(req: Request, res: Response): Promise<void>;
    updateCustomerBalance(req: Request, res: Response): Promise<void>;
}
export declare const crmApiController: CRMApiController;
//# sourceMappingURL=customer-list.d.ts.map