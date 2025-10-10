/**
 * VALEO NeuroERP 3.0 - Rule Registry
 *
 * Central registry for business rules with domain isolation
 */

import { IBusinessRule } from './business-rule';

export class RuleRegistry {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private static readonly rules: Map<string, IBusinessRule<any>[]> = new Map();

  /**
   * Register a business rule for a specific domain
   */
  public static registerRule<TContext>(domain: string, rule: IBusinessRule<TContext>): void {
    if (!RuleRegistry.rules.has(domain)) {
      RuleRegistry.rules.set(domain, []);
    }
    RuleRegistry.rules.get(domain)?.push(rule);
    // Sort rules by priority after adding (lower priority number = higher priority)
    RuleRegistry.rules.get(domain)?.sort((a, b) => a.priority - b.priority);
  }

  /**
   * Get all rules for a specific domain, sorted by priority
   */
  public static getRulesForDomain<TContext>(domain: string): IBusinessRule<TContext>[] {
    return (RuleRegistry.rules.get(domain) ?? []) as IBusinessRule<TContext>[];
  }

  /**
   * Get all registered domains
   */
  public static getRegisteredDomains(): string[] {
    return Array.from(RuleRegistry.rules.keys());
  }

  /**
   * Get rule count for a domain
   */
  public static getRuleCountForDomain(domain: string): number {
    const domainRules = RuleRegistry.rules.get(domain);
    return (domainRules !== undefined && domainRules.length > 0) ? domainRules.length : 0;
  }

  /**
   * Clear all rules (useful for testing)
   */
  public static clear(): void {
    RuleRegistry.rules.clear();
  }

  /**
   * Remove a specific rule from a domain
   */
  public static removeRule(domain: string, ruleName: string): boolean {
    const domainRules = RuleRegistry.rules.get(domain);
    if (!domainRules) return false;

    const initialLength = domainRules.length;
    RuleRegistry.rules.set(domain, domainRules.filter(rule => rule.name !== ruleName));

    const updatedRules = RuleRegistry.rules.get(domain);
    return updatedRules !== undefined && updatedRules.length < initialLength;
  }
}