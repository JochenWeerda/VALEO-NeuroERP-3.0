/**
 * Seasonal Pricing Rule Entity
 * Based on OCA sale_agriculture Seasonal Pricing pattern
 */

import { z } from 'zod';

export type Season = 'SPRING' | 'AUTUMN' | 'SUMMER' | 'WINTER' | 'ALL';

export const SeasonalPricingRuleSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // Rule identification
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  code: z.string().optional(),
  
  // Product scope
  productId: z.string().optional(), // Specific product
  commodity: z.string().optional(), // Commodity type (WHEAT, RAPE, etc.)
  category: z.string().optional(), // Product category
  
  // Season configuration
  season: z.enum(['SPRING', 'AUTUMN', 'SUMMER', 'WINTER', 'ALL']),
  monthRange: z.object({
    startMonth: z.number().min(1).max(12), // 1-12 (Jan-Dec)
    endMonth: z.number().min(1).max(12),
  }).optional(), // Alternative to season enum
  
  // Pricing adjustment
  adjustmentType: z.enum(['PERCENTAGE', 'FIXED', 'MULTIPLIER']),
  adjustmentValue: z.number(), // Percentage, fixed amount, or multiplier
  
  // Priority (higher = applied first)
  priority: z.number().default(0),
  
  // Validity
  validFrom: z.string().datetime(),
  validTo: z.string().datetime().optional(),
  
  // Status
  active: z.boolean().default(true),
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  createdBy: z.string().optional(),
  updatedAt: z.string().datetime().optional(),
  updatedBy: z.string().optional(),
});

export type SeasonalPricingRule = z.infer<typeof SeasonalPricingRuleSchema>;

export const CreateSeasonalPricingRuleSchema = SeasonalPricingRuleSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type CreateSeasonalPricingRule = z.infer<typeof CreateSeasonalPricingRuleSchema>;

export const UpdateSeasonalPricingRuleSchema = SeasonalPricingRuleSchema.partial().omit({
  id: true,
  tenantId: true,
  createdAt: true,
  createdBy: true,
});

export type UpdateSeasonalPricingRule = z.infer<typeof UpdateSeasonalPricingRuleSchema>;

/**
 * Helper function to determine season from date
 */
export function getSeasonFromDate(date: Date): Season {
  const month = date.getMonth() + 1; // 1-12 (Jan-Dec)
  
  // Spring: March, April, May (3-5)
  if (month >= 3 && month <= 5) {
    return 'SPRING';
  }
  
  // Summer: June, July, August (6-8)
  if (month >= 6 && month <= 8) {
    return 'SUMMER';
  }
  
  // Autumn: September, October, November (9-11)
  if (month >= 9 && month <= 11) {
    return 'AUTUMN';
  }
  
  // Winter: December, January, February (12, 1, 2)
  return 'WINTER';
}

/**
 * Check if date falls within month range
 */
export function isDateInMonthRange(date: Date, startMonth: number, endMonth: number): boolean {
  const month = date.getMonth() + 1; // 1-12
  
  if (startMonth <= endMonth) {
    // Normal range (e.g., 3-5 for March to May)
    return month >= startMonth && month <= endMonth;
  } else {
    // Wrapping range (e.g., 11-2 for November to February)
    return month >= startMonth || month <= endMonth;
  }
}
