/**
 * Seasonal Pricing Service
 * Based on OCA sale_agriculture Seasonal Pricing pattern
 */

import { SeasonalPricingRule, Season, getSeasonFromDate, isDateInMonthRange } from '../entities/seasonal-pricing-rule';

export interface SeasonalPricingServiceDependencies {
  // Repository would be injected here in production
  // For now, using in-memory storage
}

export interface SeasonalPriceCalculation {
  basePrice: number;
  adjustedPrice: number;
  adjustment: number;
  adjustmentType: 'PERCENTAGE' | 'FIXED' | 'MULTIPLIER';
  appliedRule?: SeasonalPricingRule;
  season: Season;
}

export class SeasonalPricingService {
  private rules: Map<string, SeasonalPricingRule> = new Map();

  constructor(private deps: SeasonalPricingServiceDependencies) {}

  /**
   * Get seasonal price for a product
   * Based on Odoo sale_agriculture pattern: _get_seasonal_multiplier()
   */
  async getSeasonalPrice(
    tenantId: string,
    productId: string,
    basePrice: number,
    orderDate: Date,
    options: {
      commodity?: string;
      category?: string;
    } = {}
  ): Promise<SeasonalPriceCalculation> {
    const season = getSeasonFromDate(orderDate);
    
    // Find applicable seasonal pricing rule
    const applicableRule = await this.findApplicableRule(
      tenantId,
      productId,
      season,
      orderDate,
      options
    );

    if (!applicableRule) {
      return {
        basePrice,
        adjustedPrice: basePrice,
        adjustment: 0,
        adjustmentType: 'PERCENTAGE',
        season
      };
    }

    // Calculate adjustment based on rule
    let adjustedPrice = basePrice;
    let adjustment = 0;

    switch (applicableRule.adjustmentType) {
      case 'PERCENTAGE':
        adjustment = basePrice * (applicableRule.adjustmentValue / 100);
        adjustedPrice = basePrice + adjustment;
        break;
      
      case 'FIXED':
        adjustment = applicableRule.adjustmentValue;
        adjustedPrice = basePrice + adjustment;
        break;
      
      case 'MULTIPLIER':
        adjustedPrice = basePrice * applicableRule.adjustmentValue;
        adjustment = adjustedPrice - basePrice;
        break;
    }

    return {
      basePrice,
      adjustedPrice: Math.round(adjustedPrice * 100) / 100,
      adjustment: Math.round(adjustment * 100) / 100,
      adjustmentType: applicableRule.adjustmentType,
      appliedRule: applicableRule,
      season
    };
  }

  /**
   * Get seasonal multiplier (for direct use in price calculations)
   */
  async getSeasonalMultiplier(
    tenantId: string,
    productId: string,
    orderDate: Date,
    options: {
      commodity?: string;
      category?: string;
    } = {}
  ): Promise<number> {
    const season = getSeasonFromDate(orderDate);
    
    const applicableRule = await this.findApplicableRule(
      tenantId,
      productId,
      season,
      orderDate,
      options
    );

    if (!applicableRule) {
      return 1.0; // No adjustment
    }

    switch (applicableRule.adjustmentType) {
      case 'MULTIPLIER':
        return applicableRule.adjustmentValue;
      
      case 'PERCENTAGE':
        return 1.0 + (applicableRule.adjustmentValue / 100);
      
      case 'FIXED':
        // For fixed adjustments, we can't return a multiplier
        // This would require base price context
        return 1.0;
      
      default:
        return 1.0;
    }
  }

  /**
   * Find applicable seasonal pricing rule
   * Based on Odoo pattern: _compute_season()
   */
  private async findApplicableRule(
    tenantId: string,
    productId: string,
    season: Season,
    orderDate: Date,
    options: {
      commodity?: string;
      category?: string;
    } = {}
  ): Promise<SeasonalPricingRule | null> {
    const now = new Date();
    const applicableRules: SeasonalPricingRule[] = [];

    // Find all active rules for this tenant
    for (const rule of this.rules.values()) {
      // Check tenant
      if (rule.tenantId !== tenantId) continue;
      
      // Check active status
      if (!rule.active) continue;
      
      // Check validity dates
      if (new Date(rule.validFrom) > now) continue;
      if (rule.validTo && new Date(rule.validTo) < now) continue;
      
      // Check product scope
      if (rule.productId && rule.productId !== productId) continue;
      if (rule.commodity && options.commodity && rule.commodity !== options.commodity) continue;
      if (rule.category && options.category && rule.category !== options.category) continue;
      
      // Check season match
      if (rule.season !== 'ALL' && rule.season !== season) {
        // Check month range if provided
        if (rule.monthRange) {
          if (!isDateInMonthRange(orderDate, rule.monthRange.startMonth, rule.monthRange.endMonth)) {
            continue;
          }
        } else {
          continue; // Season doesn't match and no month range
        }
      } else if (rule.monthRange) {
        // If month range is provided, use it instead of season enum
        if (!isDateInMonthRange(orderDate, rule.monthRange.startMonth, rule.monthRange.endMonth)) {
          continue;
        }
      }
      
      applicableRules.push(rule);
    }

    // Sort by priority (higher priority first)
    applicableRules.sort((a, b) => b.priority - a.priority);

    // Return highest priority rule
    return applicableRules.length > 0 ? applicableRules[0] : null;
  }

  /**
   * Create seasonal pricing rule
   */
  async createSeasonalPricingRule(
    rule: Omit<SeasonalPricingRule, 'id' | 'createdAt' | 'updatedAt'>
  ): Promise<SeasonalPricingRule> {
    const newRule: SeasonalPricingRule = {
      ...rule,
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    this.rules.set(newRule.id, newRule);
    return newRule;
  }

  /**
   * Get seasonal pricing rule by ID
   */
  async getSeasonalPricingRuleById(id: string): Promise<SeasonalPricingRule | null> {
    return this.rules.get(id) || null;
  }

  /**
   * List seasonal pricing rules
   */
  async listSeasonalPricingRules(
    tenantId: string,
    filter?: {
      productId?: string;
      commodity?: string;
      season?: Season;
      active?: boolean;
    }
  ): Promise<SeasonalPricingRule[]> {
    const rules: SeasonalPricingRule[] = [];

    for (const rule of this.rules.values()) {
      if (rule.tenantId !== tenantId) continue;
      
      if (filter?.productId && rule.productId !== filter.productId) continue;
      if (filter?.commodity && rule.commodity !== filter.commodity) continue;
      if (filter?.season && rule.season !== filter.season) continue;
      if (filter?.active !== undefined && rule.active !== filter.active) continue;
      
      rules.push(rule);
    }

    return rules.sort((a, b) => b.priority - a.priority);
  }

  /**
   * Update seasonal pricing rule
   */
  async updateSeasonalPricingRule(
    id: string,
    updates: Partial<Omit<SeasonalPricingRule, 'id' | 'tenantId' | 'createdAt' | 'createdBy'>>
  ): Promise<SeasonalPricingRule> {
    const rule = this.rules.get(id);
    if (!rule) {
      throw new Error('Seasonal pricing rule not found');
    }

    const updatedRule: SeasonalPricingRule = {
      ...rule,
      ...updates,
      updatedAt: new Date().toISOString()
    };

    this.rules.set(id, updatedRule);
    return updatedRule;
  }

  /**
   * Delete seasonal pricing rule
   */
  async deleteSeasonalPricingRule(id: string): Promise<boolean> {
    return this.rules.delete(id);
  }
}
