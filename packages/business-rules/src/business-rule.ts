/**
 * VALEO NeuroERP 3.0 - Business Rule Engine
 *
 * Domain-Driven Business Logic Architecture to prevent rule conflicts
 * and ensure consistent business logic execution across all domains.
 */

export interface IBusinessRule<TContext> {
  name: string;
  description: string;
  priority: number; // Lower number means higher priority
  applies(context: TContext): boolean;
  execute(context: TContext): Promise<void> | void;
}

export abstract class BusinessRule<TContext> implements IBusinessRule<TContext> {
  public abstract name: string;
  public abstract description: string;
  public priority: number = 100; // Default priority

  public abstract applies(context: TContext): boolean;
  public abstract execute(context: TContext): Promise<void> | void;
}