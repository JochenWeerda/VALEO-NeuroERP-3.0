// Services
export * from './bff-service/procurement-bff';
export * from './catalog-service/catalog-service-client';
export * from './catalog-service/punchout-integration';
export * from './contract-service/contract-service-client';
export * from './performance-service/ai-recommendations-client';
export * from './performance-service/performance-analytics';
export * from './performance-service/performance-service-client';
export * from './po-service/po-service-client';
export * from './receiving-service/receiving-service-client';
export * from './receiving-service/three-way-match-engine';
export * from './requisition-service/requisition-service-client';
export * from './sourcing-service/ai-bidding-engine';
export * from './sourcing-service/sourcing-service-client';
export * from './supplier-service/supplier-service-client';
export * from './tprm-risk-service/risk-assessment-engine';
export * from './tprm-risk-service/tprm-risk-service';

// Export specific types to avoid conflicts
export { SpendAnalysis as CatalogSpendAnalysis } from './catalog-service/guided-buying-engine';
export { RiskRecommendation as PerformanceRiskRecommendation } from './performance-service/ai-recommendations-engine';
