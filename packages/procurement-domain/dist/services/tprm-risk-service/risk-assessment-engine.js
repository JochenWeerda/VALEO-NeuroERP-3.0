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
exports.RiskAssessmentEngine = exports.RecommendationType = exports.RiskLevel = void 0;
const inversify_1 = require("inversify");
var RiskLevel;
(function (RiskLevel) {
    RiskLevel["LOW"] = "low";
    RiskLevel["MEDIUM"] = "medium";
    RiskLevel["HIGH"] = "high";
    RiskLevel["CRITICAL"] = "critical"; // 76-100
})(RiskLevel || (exports.RiskLevel = RiskLevel = {}));
var RecommendationType;
(function (RecommendationType) {
    RecommendationType["MONITORING"] = "monitoring";
    RecommendationType["MITIGATION"] = "mitigation";
    RecommendationType["CONTRACTUAL"] = "contractual";
    RecommendationType["ESCALATION"] = "escalation";
    RecommendationType["TERMINATION"] = "termination";
})(RecommendationType || (exports.RecommendationType = RecommendationType = {}));
let RiskAssessmentEngine = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var RiskAssessmentEngine = class {
        static { _classThis = this; }
        static {
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
            __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
            RiskAssessmentEngine = _classThis = _classDescriptor.value;
            if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
            __runInitializers(_classThis, _classExtraInitializers);
        }
        defaultThresholds = {
            cyber: { low: 20, medium: 40, high: 60, critical: 80 },
            compliance: { low: 15, medium: 35, high: 55, critical: 75 },
            financial: { low: 25, medium: 45, high: 65, critical: 85 },
            geographic: { low: 10, medium: 30, high: 50, critical: 70 },
            operational: { low: 20, medium: 40, high: 60, critical: 80 },
            reputational: { low: 15, medium: 35, high: 55, critical: 75 },
            overall: { low: 20, medium: 40, high: 60, critical: 80 }
        };
        /**
         * Perform comprehensive risk assessment for a supplier
         */
        async assessSupplierRisk(supplierId, supplierData, assessmentContext) {
            const factors = await this.collectRiskFactors(supplierId, supplierData, assessmentContext);
            const categories = this.calculateCategoryScores(factors);
            const overallScore = this.calculateOverallScore(categories);
            const riskLevel = this.determineRiskLevel(overallScore);
            const esgScore = await this.assessEsgRisk(supplierData.esgData);
            const recommendations = this.generateRecommendations(categories, riskLevel, factors);
            return {
                assessmentId: this.generateAssessmentId(),
                supplierId,
                overallScore,
                riskLevel,
                categories,
                esgScore,
                assessedAt: new Date(),
                assessedBy: assessmentContext.assessedBy,
                validUntil: this.calculateValidityDate(),
                factors,
                recommendations
            };
        }
        /**
         * Collect all relevant risk factors for assessment
         */
        async collectRiskFactors(supplierId, supplierData, context) {
            const factors = [];
            // Cyber Risk Factors
            factors.push(...await this.assessCyberRisk(supplierData));
            // Compliance Risk Factors
            factors.push(...await this.assessComplianceRisk(supplierData));
            // Financial Risk Factors
            factors.push(...await this.assessFinancialRisk(supplierData));
            // Geographic Risk Factors
            factors.push(...await this.assessGeographicRisk(supplierData));
            // Operational Risk Factors
            factors.push(...await this.assessOperationalRisk(supplierData, context));
            // Reputational Risk Factors
            factors.push(...await this.assessReputationalRisk(supplierData));
            return factors;
        }
        /**
         * Assess cybersecurity risk factors
         */
        async assessCyberRisk(supplierData) {
            const factors = [];
            // SOC 2 Certification
            const hasSoc2 = supplierData.certifications.includes('SOC2');
            factors.push({
                category: 'cyber',
                factor: 'SOC 2 Certification',
                score: hasSoc2 ? 10 : 80,
                weight: 0.3,
                evidence: hasSoc2 ? ['SOC 2 Type II certified'] : ['No SOC 2 certification found'],
                mitigation: hasSoc2 ? undefined : 'Require SOC 2 certification within 6 months'
            });
            // ISO 27001 Certification
            const hasIso27001 = supplierData.certifications.includes('ISO27001');
            factors.push({
                category: 'cyber',
                factor: 'ISO 27001 Certification',
                score: hasIso27001 ? 15 : 75,
                weight: 0.25,
                evidence: hasIso27001 ? ['ISO 27001 certified'] : ['No ISO 27001 certification'],
                mitigation: hasIso27001 ? undefined : 'Implement ISO 27001 framework'
            });
            // Data Breach History
            const breachHistory = supplierData.cyberIncidents || [];
            const recentBreaches = breachHistory.filter(incident => new Date(incident.date).getTime() > Date.now() - (365 * 24 * 60 * 60 * 1000));
            factors.push({
                category: 'cyber',
                factor: 'Data Breach History',
                score: recentBreaches.length > 0 ? 90 : 5,
                weight: 0.25,
                evidence: recentBreaches.length > 0
                    ? recentBreaches.map(b => `Breach on ${b.date}: ${b.description}`)
                    : ['No recent data breaches'],
                mitigation: recentBreaches.length > 0 ? 'Enhanced monitoring and incident response plan' : undefined
            });
            // Geographic Cyber Risk
            const highRiskCountries = ['CN', 'RU', 'IR', 'KP', 'CU'];
            const isHighRiskCountry = highRiskCountries.includes(supplierData.country);
            factors.push({
                category: 'cyber',
                factor: 'Geographic Cyber Risk',
                score: isHighRiskCountry ? 70 : 10,
                weight: 0.2,
                evidence: [`Supplier located in ${supplierData.country}`],
                mitigation: isHighRiskCountry ? 'Additional cyber controls and monitoring' : undefined
            });
            return factors;
        }
        /**
         * Assess compliance risk factors
         */
        async assessComplianceRisk(supplierData) {
            const factors = [];
            // Sanctions Screening
            const sanctionsHits = supplierData.sanctionsScreening?.hits || [];
            factors.push({
                category: 'compliance',
                factor: 'Sanctions Compliance',
                score: sanctionsHits.length > 0 ? 100 : 5,
                weight: 0.4,
                evidence: sanctionsHits.length > 0
                    ? sanctionsHits.map(hit => `Sanctions hit: ${hit.list} - ${hit.reason}`)
                    : ['No sanctions hits found'],
                mitigation: sanctionsHits.length > 0 ? 'Immediate termination consideration' : undefined
            });
            // Regulatory Compliance
            const requiredCertifications = ['ISO9001', 'ISO14001'];
            const missingCerts = requiredCertifications.filter(cert => !supplierData.certifications.includes(cert));
            factors.push({
                category: 'compliance',
                factor: 'Regulatory Certifications',
                score: missingCerts.length > 0 ? 60 : 10,
                weight: 0.3,
                evidence: missingCerts.length > 0
                    ? [`Missing certifications: ${missingCerts.join(', ')}`]
                    : ['All required certifications present'],
                mitigation: missingCerts.length > 0 ? `Obtain missing certifications: ${missingCerts.join(', ')}` : undefined
            });
            // Data Privacy Compliance
            const hasPrivacyFramework = supplierData.certifications.some(cert => ['GDPR', 'CCPA', 'ISO27701'].includes(cert));
            factors.push({
                category: 'compliance',
                factor: 'Data Privacy Compliance',
                score: hasPrivacyFramework ? 15 : 70,
                weight: 0.3,
                evidence: hasPrivacyFramework
                    ? ['Privacy framework implemented']
                    : ['No privacy framework identified'],
                mitigation: hasPrivacyFramework ? undefined : 'Implement GDPR/CCPA compliant privacy framework'
            });
            return factors;
        }
        /**
         * Assess financial risk factors
         */
        async assessFinancialRisk(supplierData) {
            const factors = [];
            // Credit Rating
            const creditRating = supplierData.financialData?.creditRating;
            let creditScore = 50; // Default medium risk
            if (creditRating) {
                switch (creditRating.toLowerCase()) {
                    case 'aaa':
                    case 'aa':
                        creditScore = 10;
                        break;
                    case 'a':
                        creditScore = 20;
                        break;
                    case 'bbb':
                        creditScore = 40;
                        break;
                    case 'bb':
                        creditScore = 70;
                        break;
                    case 'b':
                    case 'ccc':
                        creditScore = 90;
                        break;
                    default: creditScore = 60;
                }
            }
            factors.push({
                category: 'financial',
                factor: 'Credit Rating',
                score: creditScore,
                weight: 0.4,
                evidence: [`Credit rating: ${creditRating || 'Not available'}`],
                mitigation: creditScore > 50 ? 'Require credit insurance or enhanced payment terms' : undefined
            });
            // Financial Health Indicators
            const debtRatio = supplierData.financialData?.debtToEquityRatio;
            if (debtRatio !== undefined) {
                const debtScore = debtRatio > 2 ? 80 : debtRatio > 1 ? 40 : 15;
                factors.push({
                    category: 'financial',
                    factor: 'Debt-to-Equity Ratio',
                    score: debtScore,
                    weight: 0.3,
                    evidence: [`Debt-to-equity ratio: ${debtRatio.toFixed(2)}`],
                    mitigation: debtScore > 50 ? 'Monitor financial health closely' : undefined
                });
            }
            // Payment History
            const latePayments = supplierData.paymentHistory?.latePayments || 0;
            const totalPayments = supplierData.paymentHistory?.totalPayments || 1;
            const latePaymentRatio = latePayments / totalPayments;
            factors.push({
                category: 'financial',
                factor: 'Payment Reliability',
                score: latePaymentRatio > 0.1 ? 70 : latePaymentRatio > 0.05 ? 35 : 10,
                weight: 0.3,
                evidence: [`${latePayments} late payments out of ${totalPayments} total`],
                mitigation: latePaymentRatio > 0.05 ? 'Implement stricter payment terms' : undefined
            });
            return factors;
        }
        /**
         * Assess geographic risk factors
         */
        async assessGeographicRisk(supplierData) {
            const factors = [];
            // High-Risk Countries
            const highRiskCountries = ['SY', 'IR', 'KP', 'CU', 'VE', 'RU'];
            const veryHighRiskCountries = ['SY', 'IR', 'KP'];
            let geoScore = 10; // Default low risk
            let riskReason = 'Low geographic risk';
            if (veryHighRiskCountries.includes(supplierData.country)) {
                geoScore = 95;
                riskReason = 'Extremely high-risk country';
            }
            else if (highRiskCountries.includes(supplierData.country)) {
                geoScore = 75;
                riskReason = 'High-risk country';
            }
            factors.push({
                category: 'geographic',
                factor: 'Country Risk Assessment',
                score: geoScore,
                weight: 0.6,
                evidence: [`Supplier located in ${supplierData.country}`, riskReason],
                mitigation: geoScore > 50 ? 'Diversify suppliers or implement enhanced controls' : undefined
            });
            // Regional Stability
            const unstableRegions = ['Middle East', 'Eastern Europe', 'Africa'];
            const supplierRegion = this.getRegionFromCountry(supplierData.country);
            const isUnstableRegion = unstableRegions.includes(supplierRegion);
            factors.push({
                category: 'geographic',
                factor: 'Regional Stability',
                score: isUnstableRegion ? 60 : 15,
                weight: 0.4,
                evidence: [`Region: ${supplierRegion}`],
                mitigation: isUnstableRegion ? 'Monitor geopolitical developments' : undefined
            });
            return factors;
        }
        /**
         * Assess operational risk factors
         */
        async assessOperationalRisk(supplierData, context) {
            const factors = [];
            // Supplier Size Risk
            const sizeRisk = this.assessSizeRisk(supplierData.companySize);
            factors.push({
                category: 'operational',
                factor: 'Company Size Risk',
                score: sizeRisk.score,
                weight: 0.3,
                evidence: [`Company size: ${supplierData.companySize || 'Unknown'}`],
                mitigation: sizeRisk.mitigation
            });
            // Supply Chain Concentration
            const concentrationRisk = await this.assessConcentrationRisk(supplierData, context);
            factors.push({
                category: 'operational',
                factor: 'Supply Chain Concentration',
                score: concentrationRisk.score,
                weight: 0.3,
                evidence: concentrationRisk.evidence,
                mitigation: concentrationRisk.mitigation
            });
            // Quality Incidents
            const qualityIncidents = supplierData.qualityIncidents || [];
            const recentIncidents = qualityIncidents.filter(incident => new Date(incident.date).getTime() > Date.now() - (365 * 24 * 60 * 60 * 1000));
            factors.push({
                category: 'operational',
                factor: 'Quality Performance',
                score: recentIncidents.length > 5 ? 80 : recentIncidents.length > 2 ? 50 : 15,
                weight: 0.4,
                evidence: [`${recentIncidents.length} quality incidents in past year`],
                mitigation: recentIncidents.length > 2 ? 'Enhanced quality monitoring and testing' : undefined
            });
            return factors;
        }
        /**
         * Assess reputational risk factors
         */
        async assessReputationalRisk(supplierData) {
            const factors = [];
            // Media Mentions (Negative)
            const negativeCoverage = supplierData.mediaCoverage?.negative || 0;
            factors.push({
                category: 'reputational',
                factor: 'Negative Media Coverage',
                score: negativeCoverage > 10 ? 85 : negativeCoverage > 5 ? 60 : negativeCoverage > 0 ? 30 : 5,
                weight: 0.4,
                evidence: [`${negativeCoverage} negative media mentions`],
                mitigation: negativeCoverage > 5 ? 'Enhanced reputation monitoring' : undefined
            });
            // ESG Controversies
            const esgControversies = supplierData.esgData?.controversies || [];
            const recentControversies = esgControversies.filter(c => new Date(c.date).getTime() > Date.now() - (2 * 365 * 24 * 60 * 60 * 1000));
            factors.push({
                category: 'reputational',
                factor: 'ESG Controversies',
                score: recentControversies.length > 0 ? 75 : 10,
                weight: 0.3,
                evidence: recentControversies.length > 0
                    ? recentControversies.map(c => `${c.type}: ${c.description}`)
                    : ['No recent ESG controversies'],
                mitigation: recentControversies.length > 0 ? 'Monitor ESG performance closely' : undefined
            });
            // Industry Reputation
            const industryReputation = this.assessIndustryReputation(supplierData.industry);
            factors.push({
                category: 'reputational',
                factor: 'Industry Reputation',
                score: industryReputation.score,
                weight: 0.3,
                evidence: [`Industry: ${supplierData.industry || 'Unknown'}`],
                mitigation: industryReputation.mitigation
            });
            return factors;
        }
        /**
         * Assess ESG risk factors
         */
        async assessEsgRisk(esgData) {
            if (!esgData)
                return undefined;
            // Environmental Score
            const environmentalScore = this.calculateEnvironmentalScore(esgData);
            // Social Score
            const socialScore = this.calculateSocialScore(esgData);
            // Governance Score
            const governanceScore = this.calculateGovernanceScore(esgData);
            // Overall ESG Score (weighted average)
            const overall = (environmentalScore * 0.4) + (socialScore * 0.3) + (governanceScore * 0.3);
            return {
                environmental: environmentalScore,
                social: socialScore,
                governance: governanceScore,
                overall,
                disclosures: esgData.disclosures || []
            };
        }
        /**
         * Calculate category scores from factors
         */
        calculateCategoryScores(factors) {
            const categories = {
                cyber: 0,
                compliance: 0,
                financial: 0,
                geographic: 0,
                operational: 0,
                reputational: 0
            };
            // Group factors by category
            const categoryFactors = factors.reduce((acc, factor) => {
                if (!acc[factor.category])
                    acc[factor.category] = [];
                acc[factor.category].push(factor);
                return acc;
            }, {});
            // Calculate weighted average for each category
            for (const [category, catFactors] of Object.entries(categoryFactors)) {
                const totalWeight = catFactors.reduce((sum, f) => sum + f.weight, 0);
                const weightedScore = catFactors.reduce((sum, f) => sum + (f.score * f.weight), 0);
                categories[category] = totalWeight > 0 ? weightedScore / totalWeight : 0;
            }
            return categories;
        }
        /**
         * Calculate overall risk score
         */
        calculateOverallScore(categories) {
            // Weighted average of all categories
            const weights = {
                cyber: 0.25,
                compliance: 0.25,
                financial: 0.2,
                geographic: 0.1,
                operational: 0.15,
                reputational: 0.05
            };
            return Object.entries(categories).reduce((sum, [category, score]) => {
                return sum + (score * weights[category]);
            }, 0);
        }
        /**
         * Determine risk level from score
         */
        determineRiskLevel(score) {
            const thresholds = this.defaultThresholds.overall;
            if (score >= thresholds.critical)
                return RiskLevel.CRITICAL;
            if (score >= thresholds.high)
                return RiskLevel.HIGH;
            if (score >= thresholds.medium)
                return RiskLevel.MEDIUM;
            return RiskLevel.LOW;
        }
        /**
         * Generate recommendations based on assessment
         */
        generateRecommendations(categories, riskLevel, factors) {
            const recommendations = [];
            // High-priority factors
            const highRiskFactors = factors.filter(f => f.score > 70);
            for (const factor of highRiskFactors) {
                if (factor.mitigation) {
                    recommendations.push({
                        type: this.mapFactorToRecommendationType(factor),
                        priority: factor.score > 85 ? 'critical' : 'high',
                        description: `Address ${factor.factor}: ${factor.mitigation}`,
                        actions: [factor.mitigation],
                        deadline: this.calculateRecommendationDeadline(riskLevel),
                        responsibleParty: 'Supplier Risk Manager'
                    });
                }
            }
            // Risk level specific recommendations
            switch (riskLevel) {
                case RiskLevel.CRITICAL:
                    recommendations.push({
                        type: RecommendationType.TERMINATION,
                        priority: 'critical',
                        description: 'Critical risk level requires immediate termination consideration',
                        actions: [
                            'Initiate supplier termination process',
                            'Identify alternative suppliers',
                            'Implement business continuity measures'
                        ],
                        deadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days
                        responsibleParty: 'Executive Management'
                    });
                    break;
                case RiskLevel.HIGH:
                    recommendations.push({
                        type: RecommendationType.CONTRACTUAL,
                        priority: 'high',
                        description: 'Implement enhanced contractual protections',
                        actions: [
                            'Add risk mitigation clauses',
                            'Require additional insurance',
                            'Implement enhanced monitoring'
                        ],
                        deadline: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000), // 90 days
                        responsibleParty: 'Legal Department'
                    });
                    break;
            }
            return recommendations;
        }
        // Helper methods
        generateAssessmentId() {
            return `RA-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        }
        calculateValidityDate() {
            // Risk assessments are valid for 1 year
            const validUntil = new Date();
            validUntil.setFullYear(validUntil.getFullYear() + 1);
            return validUntil;
        }
        getRegionFromCountry(country) {
            // Simplified region mapping
            const regions = {
                'DE': 'Western Europe', 'FR': 'Western Europe', 'GB': 'Western Europe',
                'US': 'North America', 'CA': 'North America',
                'CN': 'Asia', 'JP': 'Asia', 'IN': 'Asia',
                'BR': 'South America', 'MX': 'South America',
                'RU': 'Eastern Europe', 'PL': 'Eastern Europe',
                'EG': 'Middle East', 'SA': 'Middle East',
                'ZA': 'Africa', 'NG': 'Africa'
            };
            return regions[country] || 'Unknown';
        }
        assessSizeRisk(companySize) {
            switch (companySize?.toLowerCase()) {
                case 'large':
                case 'enterprise': return { score: 10 };
                case 'medium': return { score: 25 };
                case 'small': return { score: 50, mitigation: 'Monitor financial stability closely' };
                case 'micro': return { score: 75, mitigation: 'Require enhanced risk mitigation measures' };
                default: return { score: 60, mitigation: 'Verify company size and financial stability' };
            }
        }
        async assessConcentrationRisk(supplierData, context) {
            // This would check how concentrated the supply base is for this supplier
            // For now, return a placeholder implementation
            const concentrationScore = 30; // Medium risk by default
            return {
                score: concentrationScore,
                evidence: ['Supply concentration analysis pending'],
                ...(concentrationScore > 50 && { mitigation: 'Develop secondary supplier sources' })
            };
        }
        assessIndustryReputation(industry) {
            const highRiskIndustries = ['defense', 'chemicals', 'pharmaceuticals', 'mining'];
            const isHighRisk = industry && highRiskIndustries.some(i => industry.toLowerCase().includes(i));
            return {
                score: isHighRisk ? 60 : 20,
                ...(isHighRisk && { mitigation: 'Enhanced compliance monitoring required' })
            };
        }
        calculateEnvironmentalScore(esgData) {
            let score = 50; // Base score
            // Carbon emissions impact
            if (esgData.scope3Emissions) {
                score += esgData.scope3Emissions > 100000 ? -30 : esgData.scope3Emissions < 10000 ? 20 : 0;
            }
            // Renewable energy usage
            if (esgData.renewableEnergyPercentage) {
                score += (esgData.renewableEnergyPercentage - 50) * 0.4; // Bonus for >50% renewable
            }
            return Math.max(0, Math.min(100, score));
        }
        calculateSocialScore(esgData) {
            let score = 50; // Base score
            // Diversity ratio
            if (esgData.diversityRatio) {
                score += (esgData.diversityRatio - 0.3) * 100; // Bonus for diversity >30%
            }
            // Labor practices (simplified)
            if (esgData.controversies) {
                const laborControversies = esgData.controversies.filter(c => c.type === 'labor');
                score -= laborControversies.length * 15;
            }
            return Math.max(0, Math.min(100, score));
        }
        calculateGovernanceScore(esgData) {
            let score = 50; // Base score
            // Certifications and disclosures
            const hasCertifications = esgData.disclosures && esgData.disclosures.length > 0;
            if (hasCertifications) {
                score += 25;
            }
            // Audit history
            const recentAudits = esgData.disclosures?.filter(d => d.lastAudit &&
                new Date(d.lastAudit).getTime() > Date.now() - (365 * 24 * 60 * 60 * 1000));
            if (recentAudits && recentAudits.length > 0) {
                score += 15;
            }
            return Math.max(0, Math.min(100, score));
        }
        mapFactorToRecommendationType(factor) {
            if (factor.score > 85)
                return RecommendationType.ESCALATION;
            if (factor.category === 'compliance')
                return RecommendationType.CONTRACTUAL;
            if (factor.category === 'cyber' || factor.category === 'operational')
                return RecommendationType.MITIGATION;
            return RecommendationType.MONITORING;
        }
        calculateRecommendationDeadline(riskLevel) {
            const now = Date.now();
            switch (riskLevel) {
                case RiskLevel.CRITICAL: return new Date(now + 30 * 24 * 60 * 60 * 1000); // 30 days
                case RiskLevel.HIGH: return new Date(now + 90 * 24 * 60 * 60 * 1000); // 90 days
                case RiskLevel.MEDIUM: return new Date(now + 180 * 24 * 60 * 60 * 1000); // 180 days
                default: return new Date(now + 365 * 24 * 60 * 60 * 1000); // 1 year
            }
        }
    };
    return RiskAssessmentEngine = _classThis;
})();
exports.RiskAssessmentEngine = RiskAssessmentEngine;
//# sourceMappingURL=risk-assessment-engine.js.map