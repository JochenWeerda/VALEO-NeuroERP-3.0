import { injectable } from 'inversify';
import { Catalog, CatalogItem } from '../../core/entities/catalog';

export interface BuyingContext {
  userId: string;
  department: string;
  costCenter: string;
  project?: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  budget?: {
    available: number;
    currency: string;
    period: 'monthly' | 'quarterly' | 'yearly';
  };
  previousPurchases?: Array<{
    category: string;
    supplier: string;
    amount: number;
    date: Date;
  }>;
}

export interface GuidedBuyingRecommendation {
  item: CatalogItem;
  recommendation: {
    score: number; // 0-100, higher is better
    reason: string;
    alternatives: CatalogItem[];
    compliance: {
      approved: boolean;
      violations: string[];
      warnings: string[];
    };
    budget: {
      withinBudget: boolean;
      remainingBudget?: number;
      recommendation: 'approved' | 'requires_approval' | 'not_recommended';
    };
    policy: {
      compliant: boolean;
      rules: Array<{
        rule: string;
        status: 'pass' | 'fail' | 'warning';
        message: string;
      }>;
    };
  };
}

export interface SpendAnalysis {
  category: string;
  totalSpend: number;
  transactionCount: number;
  averageOrderValue: number;
  topSuppliers: Array<{
    supplierId: string;
    supplierName: string;
    spend: number;
    percentage: number;
  }>;
  spendTrend: Array<{
    period: string;
    amount: number;
    change: number;
  }>;
  maverickSpend: {
    amount: number;
    percentage: number;
    transactions: number;
  };
  recommendations: string[];
}

@injectable()
export class GuidedBuyingEngine {
  /**
   * Get guided buying recommendations for a search query
   */
  async getRecommendations(
    searchQuery: string,
    context: BuyingContext,
    availableItems: CatalogItem[],
    catalogs: Catalog[]
  ): Promise<GuidedBuyingRecommendation[]> {
    const recommendations: GuidedBuyingRecommendation[] = [];

    // Filter items based on access permissions
    const accessibleItems = this.filterAccessibleItems(availableItems, catalogs, context);

    // Score and rank items
    for (const item of accessibleItems) {
      const recommendation = await this.scoreItem(item, searchQuery, context);
      if (recommendation.recommendation.score > 30) { // Only include reasonably good matches
        recommendations.push(recommendation);
      }
    }

    // Sort by score (highest first)
    recommendations.sort((a, b) => b.recommendation.score - a.recommendation.score);

    // Limit to top 10 recommendations
    return recommendations.slice(0, 10);
  }

  /**
   * Analyze spend patterns for a category or department
   */
  async analyzeSpend(
    category?: string,
    department?: string,
    dateRange?: { from: Date; to: Date }
  ): Promise<SpendAnalysis> {
    // In production, this would query transaction databases
    // For now, return mock analysis

    const mockData: SpendAnalysis = {
      category: category || 'IT Hardware',
      totalSpend: 250000,
      transactionCount: 45,
      averageOrderValue: 5556,
      topSuppliers: [
        { supplierId: 'supplier-a', supplierName: 'TechCorp GmbH', spend: 125000, percentage: 50 },
        { supplierId: 'supplier-b', supplierName: 'GlobalTech Inc', spend: 75000, percentage: 30 },
        { supplierId: 'supplier-c', supplierName: 'LocalTech Ltd', spend: 50000, percentage: 20 }
      ],
      spendTrend: [
        { period: '2024-Q1', amount: 55000, change: 0 },
        { period: '2024-Q2', amount: 62000, change: 12.7 },
        { period: '2024-Q3', amount: 68000, change: 9.7 },
        { period: '2024-Q4', amount: 65000, change: -4.4 }
      ],
      maverickSpend: {
        amount: 25000,
        percentage: 10,
        transactions: 8
      },
      recommendations: [
        'Consolidate purchases with top 2 suppliers to reduce maverick spend',
        'Implement catalog restrictions for high-risk categories',
        'Set up quarterly supplier performance reviews',
        'Consider framework agreements for recurring purchases'
      ]
    };

    return mockData;
  }

  /**
   * Check if a purchase complies with company policies
   */
  async checkPolicyCompliance(
    item: CatalogItem,
    quantity: number,
    context: BuyingContext
  ): Promise<{
    compliant: boolean;
    violations: string[];
    warnings: string[];
    requiredApprovals: string[];
  }> {
    const violations: string[] = [];
    const warnings: string[] = [];
    const requiredApprovals: string[] = [];

    const totalValue = item.price * quantity;

    // Budget checks
    if (context.budget) {
      if (totalValue > context.budget.available) {
        violations.push(`Purchase exceeds available budget by ${(totalValue - context.budget.available).toFixed(2)} ${item.currency}`);
        requiredApprovals.push('Budget Owner Approval');
      } else if (totalValue > context.budget.available * 0.8) {
        warnings.push('Purchase uses more than 80% of available budget');
        requiredApprovals.push('Budget Owner Review');
      }
    }

    // Amount-based approval rules
    if (totalValue > 50000) {
      requiredApprovals.push('Executive Approval');
    } else if (totalValue > 10000) {
      requiredApprovals.push('Department Head Approval');
    } else if (totalValue > 5000) {
      requiredApprovals.push('Manager Approval');
    }

    // Supplier restrictions
    if (item.restricted) {
      violations.push(`Item is restricted: ${item.restrictionReason}`);
      requiredApprovals.push('Compliance Officer Approval');
    }

    // Category-specific rules
    const categoryRules = this.getCategoryRules(item.category);
    for (const rule of categoryRules) {
      const ruleResult = this.evaluateRule(rule, item, quantity, context);
      if (ruleResult.status === 'fail') {
        violations.push(ruleResult.message);
      } else if (ruleResult.status === 'warning') {
        warnings.push(ruleResult.message);
      }
      if (ruleResult.requiresApproval) {
        requiredApprovals.push(ruleResult.requiresApproval);
      }
    }

    // Previous purchase analysis
    if (context.previousPurchases) {
      const recentPurchases = context.previousPurchases.filter(p =>
        p.category === item.category &&
        p.date > new Date(Date.now() - 90 * 24 * 60 * 60 * 1000) // Last 90 days
      );

      if (recentPurchases.length > 0) {
        const avgPurchase = recentPurchases.reduce((sum, p) => sum + p.amount, 0) / recentPurchases.length;
        if (totalValue > avgPurchase * 2) {
          warnings.push('Purchase amount significantly higher than recent purchases in this category');
        }
      }
    }

    return {
      compliant: violations.length === 0,
      violations,
      warnings,
      requiredApprovals: [...new Set(requiredApprovals)] // Remove duplicates
    };
  }

  /**
   * Get alternative items for comparison
   */
  async getAlternatives(
    item: CatalogItem,
    catalogs: Catalog[]
  ): Promise<CatalogItem[]> {
    // In production, this would search catalogs for similar items
    // For now, return mock alternatives

    const alternatives: CatalogItem[] = [
      {
        ...item,
        id: 'alt-1' as any,
        name: `${item.name} (Alternative Brand)`,
        price: item.price * 0.95,
        supplierId: 'supplier-b'
      },
      {
        ...item,
        id: 'alt-2' as any,
        name: `${item.name} (Budget Option)`,
        price: item.price * 0.85,
        supplierId: 'supplier-c'
      }
    ];

    return alternatives;
  }

  // Private methods

  private filterAccessibleItems(
    items: CatalogItem[],
    catalogs: Catalog[],
    context: BuyingContext
  ): CatalogItem[] {
    const userGroups = this.getUserGroups(context.userId);

    return items.filter(item => {
      const catalog = catalogs.find(c => c.id === item.catalogId);
      return catalog && catalog.hasAccess(userGroups);
    });
  }

  private async scoreItem(
    item: CatalogItem,
    searchQuery: string,
    context: BuyingContext
  ): Promise<GuidedBuyingRecommendation> {
    let score = 50; // Base score
    let reason = '';

    // Relevance to search query
    const relevanceScore = this.calculateRelevanceScore(item, searchQuery);
    score += relevanceScore * 0.3;
    reason += `Relevance: ${relevanceScore.toFixed(0)}/100. `;

    // Policy compliance
    const compliance = await this.checkPolicyCompliance(item, 1, context);
    if (compliance.compliant) {
      score += 20;
      reason += 'Policy compliant. ';
    } else {
      score -= compliance.violations.length * 10;
      reason += `${compliance.violations.length} policy violations. `;
    }

    // Budget alignment
    if (context.budget && item.price <= context.budget.available) {
      score += 15;
      reason += 'Within budget. ';
    } else if (context.budget) {
      score -= 15;
      reason += 'Exceeds budget. ';
    }

    // Previous purchase preference
    if (context.previousPurchases) {
      const hasPurchasedFromSupplier = context.previousPurchases.some(p =>
        p.supplier === item.supplierId
      );
      if (hasPurchasedFromSupplier) {
        score += 10;
        reason += 'Previous supplier relationship. ';
      }
    }

    // Availability and lead time
    if (item.availability === 'in_stock') {
      score += 5;
      reason += 'In stock. ';
    }

    if (item.leadTime && item.leadTime <= 7) {
      score += 5;
      reason += 'Fast delivery. ';
    }

    // Urgency consideration
    if (context.urgency === 'critical' && item.leadTime && item.leadTime <= 1) {
      score += 10;
      reason += 'Meets critical urgency requirements. ';
    }

    // Get alternatives
    const catalog = { id: item.catalogId } as Catalog; // Mock catalog
    const alternatives = await this.getAlternatives(item, [catalog]);

    // Budget analysis
    const budgetAnalysis = this.analyzeBudgetFit(item.price, context.budget);

    return {
      item,
      recommendation: {
        score: Math.max(0, Math.min(100, score)),
        reason: reason.trim(),
        alternatives,
        compliance: {
          approved: compliance.compliant,
          violations: compliance.violations,
          warnings: compliance.warnings
        },
        budget: budgetAnalysis,
        policy: {
          compliant: compliance.compliant,
          rules: [
            ...compliance.violations.map(v => ({
              rule: 'Policy Check',
              status: 'fail' as const,
              message: v
            })),
            ...compliance.warnings.map(w => ({
              rule: 'Policy Warning',
              status: 'warning' as const,
              message: w
            }))
          ]
        }
      }
    };
  }

  private calculateRelevanceScore(item: CatalogItem, query: string): number {
    const searchTerms = query.toLowerCase().split(' ');
    const itemText = `${item.name} ${item.description} ${item.category}`.toLowerCase();

    let matches = 0;
    for (const term of searchTerms) {
      if (itemText.includes(term)) {
        matches++;
      }
    }

    return (matches / searchTerms.length) * 100;
  }

  private analyzeBudgetFit(
    price: number,
    budget?: BuyingContext['budget']
  ): GuidedBuyingRecommendation['recommendation']['budget'] {
    if (!budget) {
      return {
        withinBudget: true,
        recommendation: 'approved'
      };
    }

    const withinBudget = price <= budget.available;
    const remainingBudget = budget.available - price;

    let recommendation: 'approved' | 'requires_approval' | 'not_recommended' = 'approved';

    if (!withinBudget) {
      recommendation = 'not_recommended';
    } else if (remainingBudget < budget.available * 0.1) { // Less than 10% remaining
      recommendation = 'requires_approval';
    }

    return {
      withinBudget,
      ...(withinBudget && { remainingBudget }),
      recommendation
    };
  }

  private getUserGroups(userId: string): string[] {
    // In production, this would query user management system
    // For now, return mock groups
    return ['procurement_users', 'department_it', 'budget_approvers'];
  }

  private getCategoryRules(category: string): Array<{
    name: string;
    condition: (item: CatalogItem, quantity: number, context: BuyingContext) => boolean;
    requiresApproval?: string;
  }> {
    const rules: Record<string, Array<{
      name: string;
      condition: (item: CatalogItem, quantity: number, context: BuyingContext) => boolean;
      requiresApproval?: string;
    }>> = {
      'IT Hardware': [
        {
          name: 'Preferred Supplier',
          condition: (item) => ['supplier-a', 'supplier-b'].includes(item.supplierId)
        },
        {
          name: 'Security Compliance',
          condition: (item) => item.complianceFlags.includes('ISO27001'),
          requiresApproval: 'IT Security Approval'
        }
      ],
      'Office Supplies': [
        {
          name: 'Bulk Purchase',
          condition: (item, quantity) => quantity >= (item.minimumOrderQuantity || 100)
        }
      ]
    };

    return rules[category] || [];
  }

  private evaluateRule(
    rule: {
      name: string;
      condition: (item: CatalogItem, quantity: number, context: BuyingContext) => boolean;
      requiresApproval?: string;
    },
    item: CatalogItem,
    quantity: number,
    context: BuyingContext
  ): {
    status: 'pass' | 'fail' | 'warning';
    message: string;
    requiresApproval?: string;
  } {
    const passes = rule.condition(item, quantity, context);

    if (passes) {
      return {
        status: 'pass',
        message: `${rule.name}: Passed`,
        ...(rule.requiresApproval && { requiresApproval: rule.requiresApproval })
      };
    } else {
      return {
        status: 'fail',
        message: `${rule.name}: Failed - requires approval`,
        requiresApproval: rule.requiresApproval || 'Category Manager Approval'
      };
    }
  }

  /**
   * Generate ABC analysis for spend categories
   */
  async generateABCAnalysis(
    categories: Array<{ name: string; spend: number }>
  ): Promise<Array<{
    category: string;
    spend: number;
    percentage: number;
    cumulativePercentage: number;
    abcClass: 'A' | 'B' | 'C';
    recommendations: string[];
  }>> {
    // Sort by spend descending
    const sorted = categories.sort((a, b) => b.spend - a.spend);
    const totalSpend = sorted.reduce((sum, cat) => sum + cat.spend, 0);

    let cumulativePercentage = 0;

    return sorted.map((category, index) => {
      const percentage = (category.spend / totalSpend) * 100;
      cumulativePercentage += percentage;

      let abcClass: 'A' | 'B' | 'C';
      let recommendations: string[] = [];

      if (cumulativePercentage <= 80) {
        abcClass = 'A';
        recommendations = [
          'High priority for supplier relationship management',
          'Implement strategic sourcing initiatives',
          'Consider long-term contracts and volume discounts'
        ];
      } else if (cumulativePercentage <= 95) {
        abcClass = 'B';
        recommendations = [
          'Monitor spending patterns',
          'Standardize purchasing processes',
          'Evaluate consolidation opportunities'
        ];
      } else {
        abcClass = 'C';
        recommendations = [
          'Implement purchase order controls',
          'Use procurement cards for low-value purchases',
          'Focus on process efficiency rather than strategic sourcing'
        ];
      }

      return {
        category: category.name,
        spend: category.spend,
        percentage,
        cumulativePercentage,
        abcClass,
        recommendations
      };
    });
  }
}

export default GuidedBuyingEngine;