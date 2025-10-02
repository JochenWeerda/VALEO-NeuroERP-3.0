"use strict";
var __esDecorate = (this && this.__esDecorate) || function (ctor, descriptorIn, decorators, contextIn, initializers, extraInitializers) {
    function accept(f) { if (f !== void 0 && typeof f !== "function") throw new TypeError("Function expected"); return f; }
    var kind = contextIn.kind, key = kind === "getter" ? "get" : kind === "setter" ? "set" : "value";
    var target = !descriptorIn && ctor ? contextIn["static"] ? ctor : ctor.prototype : null;
    var descriptor = descriptorIn || (target ? Object.getOwnPropertyDescriptor(target, contextIn.name) : {});
    var _, done = false;
    for (var i = decorators.length - 1; i >= 0; i--) {
        var context = {};
        for (var p in contextIn) context[p] = p === "access" ? {} : contextIn[p];
        for (var p in contextIn.access) context.access[p] = contextIn.access[p];
        context.addInitializer = function (f) { if (done) throw new TypeError("Cannot add initializers after decoration has completed"); extraInitializers.push(accept(f || null)); };
        var result = (0, decorators[i])(kind === "accessor" ? { get: descriptor.get, set: descriptor.set } : descriptor[key], context);
        if (kind === "accessor") {
            if (result === void 0) continue;
            if (result === null || typeof result !== "object") throw new TypeError("Object expected");
            if (_ = accept(result.get)) descriptor.get = _;
            if (_ = accept(result.set)) descriptor.set = _;
            if (_ = accept(result.init)) initializers.unshift(_);
        }
        else if (_ = accept(result)) {
            if (kind === "field") initializers.unshift(_);
            else descriptor[key] = _;
        }
    }
    if (target) Object.defineProperty(target, contextIn.name, descriptor);
    done = true;
};
var __runInitializers = (this && this.__runInitializers) || function (thisArg, initializers, value) {
    var useValue = arguments.length > 2;
    for (var i = 0; i < initializers.length; i++) {
        value = useValue ? initializers[i].call(thisArg, value) : initializers[i].call(thisArg);
    }
    return useValue ? value : void 0;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.GuidedBuyingEngine = void 0;
const inversify_1 = require("inversify");
let GuidedBuyingEngine = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var GuidedBuyingEngine = class {
        static { _classThis = this; }
        static {
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
            __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
            GuidedBuyingEngine = _classThis = _classDescriptor.value;
            if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
            __runInitializers(_classThis, _classExtraInitializers);
        }
        /**
         * Get guided buying recommendations for a search query
         */
        async getRecommendations(searchQuery, context, availableItems, catalogs) {
            const recommendations = [];
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
        async analyzeSpend(category, department, dateRange) {
            // In production, this would query transaction databases
            // For now, return mock analysis
            const mockData = {
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
        async checkPolicyCompliance(item, quantity, context) {
            const violations = [];
            const warnings = [];
            const requiredApprovals = [];
            const totalValue = item.price * quantity;
            // Budget checks
            if (context.budget) {
                if (totalValue > context.budget.available) {
                    violations.push(`Purchase exceeds available budget by ${(totalValue - context.budget.available).toFixed(2)} ${item.currency}`);
                    requiredApprovals.push('Budget Owner Approval');
                }
                else if (totalValue > context.budget.available * 0.8) {
                    warnings.push('Purchase uses more than 80% of available budget');
                    requiredApprovals.push('Budget Owner Review');
                }
            }
            // Amount-based approval rules
            if (totalValue > 50000) {
                requiredApprovals.push('Executive Approval');
            }
            else if (totalValue > 10000) {
                requiredApprovals.push('Department Head Approval');
            }
            else if (totalValue > 5000) {
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
                }
                else if (ruleResult.status === 'warning') {
                    warnings.push(ruleResult.message);
                }
                if (ruleResult.requiresApproval) {
                    requiredApprovals.push(ruleResult.requiresApproval);
                }
            }
            // Previous purchase analysis
            if (context.previousPurchases) {
                const recentPurchases = context.previousPurchases.filter(p => p.category === item.category &&
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
        async getAlternatives(item, catalogs) {
            // In production, this would search catalogs for similar items
            // For now, return mock alternatives
            const alternatives = [
                {
                    ...item,
                    id: 'alt-1',
                    name: `${item.name} (Alternative Brand)`,
                    price: item.price * 0.95,
                    supplierId: 'supplier-b'
                },
                {
                    ...item,
                    id: 'alt-2',
                    name: `${item.name} (Budget Option)`,
                    price: item.price * 0.85,
                    supplierId: 'supplier-c'
                }
            ];
            return alternatives;
        }
        // Private methods
        filterAccessibleItems(items, catalogs, context) {
            const userGroups = this.getUserGroups(context.userId);
            return items.filter(item => {
                const catalog = catalogs.find(c => c.id === item.catalogId);
                return catalog && catalog.hasAccess(userGroups);
            });
        }
        async scoreItem(item, searchQuery, context) {
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
            }
            else {
                score -= compliance.violations.length * 10;
                reason += `${compliance.violations.length} policy violations. `;
            }
            // Budget alignment
            if (context.budget && item.price <= context.budget.available) {
                score += 15;
                reason += 'Within budget. ';
            }
            else if (context.budget) {
                score -= 15;
                reason += 'Exceeds budget. ';
            }
            // Previous purchase preference
            if (context.previousPurchases) {
                const hasPurchasedFromSupplier = context.previousPurchases.some(p => p.supplier === item.supplierId);
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
            const catalog = { id: item.catalogId }; // Mock catalog
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
                                status: 'fail',
                                message: v
                            })),
                            ...compliance.warnings.map(w => ({
                                rule: 'Policy Warning',
                                status: 'warning',
                                message: w
                            }))
                        ]
                    }
                }
            };
        }
        calculateRelevanceScore(item, query) {
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
        analyzeBudgetFit(price, budget) {
            if (!budget) {
                return {
                    withinBudget: true,
                    recommendation: 'approved'
                };
            }
            const withinBudget = price <= budget.available;
            const remainingBudget = budget.available - price;
            let recommendation = 'approved';
            if (!withinBudget) {
                recommendation = 'not_recommended';
            }
            else if (remainingBudget < budget.available * 0.1) { // Less than 10% remaining
                recommendation = 'requires_approval';
            }
            return {
                withinBudget,
                ...(withinBudget && { remainingBudget }),
                recommendation
            };
        }
        getUserGroups(userId) {
            // In production, this would query user management system
            // For now, return mock groups
            return ['procurement_users', 'department_it', 'budget_approvers'];
        }
        getCategoryRules(category) {
            const rules = {
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
        evaluateRule(rule, item, quantity, context) {
            const passes = rule.condition(item, quantity, context);
            if (passes) {
                return {
                    status: 'pass',
                    message: `${rule.name}: Passed`,
                    ...(rule.requiresApproval && { requiresApproval: rule.requiresApproval })
                };
            }
            else {
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
        async generateABCAnalysis(categories) {
            // Sort by spend descending
            const sorted = categories.sort((a, b) => b.spend - a.spend);
            const totalSpend = sorted.reduce((sum, cat) => sum + cat.spend, 0);
            let cumulativePercentage = 0;
            return sorted.map((category, index) => {
                const percentage = (category.spend / totalSpend) * 100;
                cumulativePercentage += percentage;
                let abcClass;
                let recommendations = [];
                if (cumulativePercentage <= 80) {
                    abcClass = 'A';
                    recommendations = [
                        'High priority for supplier relationship management',
                        'Implement strategic sourcing initiatives',
                        'Consider long-term contracts and volume discounts'
                    ];
                }
                else if (cumulativePercentage <= 95) {
                    abcClass = 'B';
                    recommendations = [
                        'Monitor spending patterns',
                        'Standardize purchasing processes',
                        'Evaluate consolidation opportunities'
                    ];
                }
                else {
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
    };
    return GuidedBuyingEngine = _classThis;
})();
exports.GuidedBuyingEngine = GuidedBuyingEngine;
exports.default = GuidedBuyingEngine;
