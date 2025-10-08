/**
 * VALEO NeuroERP 3.0 - Business Rule Engine
 *
 * Domain-Driven Business Logic Architecture to prevent rule conflicts
 * and ensure consistent business logic execution across all domains.
 */

export interface ValidationResult {
  isValid: boolean;
  errors: Array<{
    field: string;
    message: string;
    code: string;
    severity: 'error' | 'warning';
  }>;
  warnings: Array<{
    field: string;
    message: string;
    code: string;
  }>;
}

export interface IBusinessRule<TContext> {
  name: string;
  description: string;
  priority: number; // Lower number means higher priority
  domain?: string;
  version?: string;
  enabled?: boolean;

  // Legacy validation method for backward compatibility
  validate?(context: TContext): Promise<ValidationResult>;

  // New execution methods
  applies?(context: TContext): boolean;
  execute?(context: TContext): Promise<void> | void;
}

export abstract class BusinessRule<TContext> implements IBusinessRule<TContext> {
  public abstract name: string;
  public abstract description: string;
  public priority: number = 100; // Default priority
  public domain?: string;
  public version: string = '1.0.0';
  public enabled: boolean = true;

  // Legacy validation method - can be overridden
  public async validate(context: TContext): Promise<ValidationResult> {
    const errors: any[] = [];
    const warnings: any[] = [];

    // Default implementation - override in subclasses
    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  // New execution methods - can be overridden
  public applies(context: TContext): boolean {
    return true; // Default: always applies
  }

  public execute(context: TContext): Promise<void> | void {
    // Default: do nothing
  }
}