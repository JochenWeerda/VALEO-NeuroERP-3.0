/**
 * VALEO NeuroERP 3.0 - CRM Domain Business Rules
 *
 * Domain-specific business rules for Customer Relationship Management
 */

// @ts-ignore - Cross-package imports
import { BusinessRule, IBusinessRule, ValidationResult } from '../../../business-rules/src/business-rule';
// @ts-ignore - Cross-package imports
import { RuleRegistry } from '../../../business-rules/src/rule-registry';

// Define a context for CRM rules
export interface CrmRuleContext {
  customer: {
    id: string;
    status: 'New' | 'Active' | 'Inactive' | 'VIP';
    totalOrders: number;
    lastOrderDate?: Date;
    creditLimit: number;
    totalRevenue: number;
  };
  action: 'create' | 'update' | 'delete' | 'view';
  isValid: boolean; // To be modified by rules
  messages: string[]; // To collect messages from rules
  auditTrail: string[]; // To track rule executions
}

// Rule 1: Validate New Customer Credit Limit
export class ValidateNewCustomerCreditLimitRule extends BusinessRule<CrmRuleContext> {
  name = 'ValidateNewCustomerCreditLimit';
  description = 'Ensures new customers do not exceed a default credit limit.';
  priority = 10;
  domain = 'crm';

  async validate(context: CrmRuleContext): Promise<ValidationResult> {
    const errors: any[] = [];
    const warnings: any[] = [];

    if (context.action === 'create' && context.customer.status === 'New' && context.customer.creditLimit > 5000) {
      errors.push({
        field: 'creditLimit',
        message: 'New customers cannot have a credit limit greater than 5000.',
        code: 'CRM_NEW_CUSTOMER_CREDIT_LIMIT_EXCEEDED',
        severity: 'error'
      });
      context.auditTrail.push(`Rule executed: ${this.name} - Credit limit validation failed`);
      console.log('Rule executed: ValidateNewCustomerCreditLimit - Credit limit exceeded.');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
}

// Rule 2: Promote Customer to VIP
export class PromoteToVipRule extends BusinessRule<CrmRuleContext> {
  name = 'PromoteToVip';
  description = 'Promotes active customers with more than 10 orders to VIP status.';
  priority = 20;

  applies(context: CrmRuleContext): boolean {
    return context.action === 'update' && context.customer.status === 'Active' && context.customer.totalOrders > 10;
  }

  execute(context: CrmRuleContext): void {
    context.customer.status = 'VIP';
    context.messages.push(`Customer ${context.customer.id} promoted to VIP.`);
    context.auditTrail.push(`Rule executed: ${this.name} - Customer promoted to VIP`);
    console.log('Rule executed: PromoteToVip - Customer promoted.');
  }
}

// Rule 3: Validate Credit Limit Based on Revenue
export class ValidateCreditLimitByRevenueRule extends BusinessRule<CrmRuleContext> {
  name = 'ValidateCreditLimitByRevenue';
  description = 'Adjusts credit limit based on customer revenue history.';
  priority = 15;

  applies(context: CrmRuleContext): boolean {
    return (context.action === 'create' || context.action === 'update') && context.customer.totalRevenue > 0;
  }

  execute(context: CrmRuleContext): void {
    const recommendedLimit = Math.min(context.customer.totalRevenue * 0.1, 50000); // 10% of revenue, max 50k

    if (context.customer.creditLimit > recommendedLimit) {
      context.customer.creditLimit = recommendedLimit;
      context.messages.push(`Credit limit adjusted to ${recommendedLimit} based on revenue.`);
      context.auditTrail.push(`Rule executed: ${this.name} - Credit limit adjusted to ${recommendedLimit}`);
    } else {
      context.auditTrail.push(`Rule executed: ${this.name} - Credit limit validated`);
    }
  }
}

// Rule 4: Deactivate Inactive Customers
export class DeactivateInactiveCustomersRule extends BusinessRule<CrmRuleContext> {
  name = 'DeactivateInactiveCustomers';
  description = 'Deactivates customers who haven\'t ordered in 6 months.';
  priority = 50;

  applies(context: CrmRuleContext): boolean {
    if (context.action !== 'update' || !context.customer.lastOrderDate) return false;

    const sixMonthsAgo = new Date();
    sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);

    return context.customer.status === 'Active' && context.customer.lastOrderDate < sixMonthsAgo;
  }

  execute(context: CrmRuleContext): void {
    context.customer.status = 'Inactive';
    context.messages.push('Customer deactivated due to inactivity (no orders in 6 months).');
    context.auditTrail.push(`Rule executed: ${this.name} - Customer deactivated`);
    console.log('Rule executed: DeactivateInactiveCustomers - Customer deactivated.');
  }
}

// Rule 5: Audit Trail Rule (always executes for logging)
export class AuditTrailRule extends BusinessRule<CrmRuleContext> {
  name = 'AuditTrail';
  description = 'Maintains audit trail for all customer operations.';
  priority = 100; // Lowest priority, executes last

  applies(context: CrmRuleContext): boolean {
    return true; // Always applies
  }

  execute(context: CrmRuleContext): void {
    context.auditTrail.push(`Audit: ${context.action} operation on customer ${context.customer.id} at ${new Date().toISOString()}`);
  }
}

// Register CRM rules
export function registerCrmRules(): void {
  RuleRegistry.registerRule('crm', new ValidateNewCustomerCreditLimitRule());
  RuleRegistry.registerRule('crm', new ValidateCreditLimitByRevenueRule());
  RuleRegistry.registerRule('crm', new PromoteToVipRule());
  RuleRegistry.registerRule('crm', new DeactivateInactiveCustomersRule());
  RuleRegistry.registerRule('crm', new AuditTrailRule());

  console.log('CRM business rules registered successfully');
}