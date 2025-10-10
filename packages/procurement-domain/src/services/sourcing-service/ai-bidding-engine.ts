import { injectable } from 'inversify';
import { AwardRecommendation, Bid, Rfq } from '../../core/entities/rfq';
import { SupplierId } from '../../core/entities/supplier';

export interface BidAnalysisResult {
  bidId: string;
  supplierId: string;
  overallScore: number; // 0-100
  categoryScores: {
    price: number;
    quality: number;
    delivery: number;
    experience: number;
    sustainability: number;
    innovation: number;
  };
  pricePosition: 'lowest' | 'competitive' | 'high' | 'outlier';
  riskFactors: string[];
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  confidence: number; // AI confidence in analysis
}

export interface AwardRecommendationResult {
  recommendations: AwardRecommendation[];
  analysis: {
    totalValue: number;
    savingsPotential: number;
    riskDistribution: Record<string, number>;
    supplierConcentration: Record<string, number>;
  };
  confidence: number;
  reasoning: string[];
}

export interface MarketIntelligence {
  category: string;
  averagePrice: number;
  priceRange: { min: number; max: number; median: number };
  marketTrends: string[];
  competitorAnalysis: Array<{
    supplier: string;
    marketShare: number;
    pricingStrategy: string;
  }>;
  recommendations: string[];
}

@injectable()
export class AIBiddingEngine {
  /**
   * Analyze all bids for an RFQ using AI-powered algorithms
   */
  async analyzeBids(rfq: Rfq, supplierData: Map<string, any>): Promise<BidAnalysisResult[]> {
    const results: BidAnalysisResult[] = [];

    for (const bid of rfq.bids) {
      const analysis = await this.analyzeSingleBid(bid, rfq, supplierData.get(bid.supplierId));
      results.push(analysis);
    }

    return results;
  }

  /**
   * Generate award recommendations using AI optimization
   */
  async generateAwardRecommendations(
    rfq: Rfq,
    bidAnalyses: BidAnalysisResult[],
    constraints?: {
      maxAwardPerSupplier?: number;
      minSuppliers?: number;
      maxSuppliers?: number;
      riskTolerance?: 'low' | 'medium' | 'high';
    }
  ): Promise<AwardRecommendationResult> {
    // Score and rank bids
    const scoredBids = bidAnalyses.sort((a, b) => b.overallScore - a.overallScore);

    // Apply business rules and constraints
    const recommendations = await this.optimizeAwardAllocation(rfq, scoredBids, constraints);

    // Calculate analysis metrics
    const analysis = this.calculateAwardAnalysis(rfq, recommendations);

    return {
      recommendations,
      analysis,
      confidence: this.calculateRecommendationConfidence(recommendations, bidAnalyses),
      reasoning: this.generateRecommendationReasoning(recommendations, rfq, constraints)
    };
  }

  /**
   * Get market intelligence for category
   */
  async getMarketIntelligence(category: string, region?: string): Promise<MarketIntelligence> {
    // In a real implementation, this would query external market data APIs
    // For now, return simulated market intelligence

    const basePrice = this.getBasePriceForCategory(category);
    const marketVolatility = Math.random() * 0.3 + 0.1; // 10-40% volatility

    return {
      category,
      averagePrice: basePrice,
      priceRange: {
        min: basePrice * (1 - marketVolatility),
        max: basePrice * (1 + marketVolatility),
        median: basePrice * (1 + marketVolatility * 0.1)
      },
      marketTrends: [
        'Increasing demand for sustainable sourcing',
        'Digital transformation in supply chains',
        'Geopolitical risks affecting pricing',
        'Innovation in product specifications'
      ],
      competitorAnalysis: [
        { supplier: 'Supplier A', marketShare: 25, pricingStrategy: 'Cost leadership' },
        { supplier: 'Supplier B', marketShare: 20, pricingStrategy: 'Differentiation' },
        { supplier: 'Supplier C', marketShare: 15, pricingStrategy: 'Niche focus' }
      ],
      recommendations: [
        'Consider multi-year contracts for price stability',
        'Evaluate supplier innovation capabilities',
        'Include ESG criteria in evaluation',
        'Monitor geopolitical developments'
      ]
    };
  }

  /**
   * Predict bid outcomes using machine learning
   */
  async predictBidOutcomes(rfq: Rfq, historicalData?: any[]): Promise<{
    predictedWinningBid: number;
    confidenceInterval: { min: number; max: number };
    factors: Array<{ factor: string; impact: number; explanation: string }>;
  }> {
    // Simplified prediction based on RFQ characteristics
    const basePrediction = rfq.totalEstimatedValue * 0.85; // Assume 15% discount
    const volatility = rfq.totalEstimatedValue * 0.1; // 10% volatility

    return {
      predictedWinningBid: basePrediction,
      confidenceInterval: {
        min: basePrediction - volatility,
        max: basePrediction + volatility
      },
      factors: [
        {
          factor: 'Market Competition',
          impact: -8,
          explanation: 'High number of invited suppliers suggests competitive pricing'
        },
        {
          factor: 'Category Complexity',
          impact: 5,
          explanation: 'Complex specifications may require premium pricing'
        },
        {
          factor: 'Supplier Experience',
          impact: -3,
          explanation: 'Experienced suppliers offer better value'
        }
      ]
    };
  }

  // Private methods

  private async analyzeSingleBid(
    bid: Bid,
    rfq: Rfq,
    supplierData?: any
  ): Promise<BidAnalysisResult> {
    // Price Analysis
    const priceScore = await this.analyzePrice(bid, rfq);
    const pricePosition = this.determinePricePosition(bid, rfq);

    // Quality Analysis
    const qualityScore = await this.analyzeQuality(bid, rfq, supplierData);

    // Delivery Analysis
    const deliveryScore = await this.analyzeDelivery(bid, rfq);

    // Experience Analysis
    const experienceScore = await this.analyzeExperience(supplierData);

    // Sustainability Analysis
    const sustainabilityScore = await this.analyzeSustainability(supplierData);

    // Innovation Analysis
    const innovationScore = await this.analyzeInnovation(bid, supplierData);

    // Calculate overall score using weighted average
    const weights = rfq.evaluationCriteria.reduce((acc, criterion) => {
      acc[criterion.criterion] = criterion.weight / 100;
      return acc;
    }, {
      price: 0.4,
      quality: 0.2,
      delivery: 0.15,
      experience: 0.1,
      sustainability: 0.1,
      innovation: 0.05
    } as Record<string, number>);

    const overallScore =
      priceScore * (weights.price || 0.4) +
      qualityScore * (weights.quality || 0.2) +
      deliveryScore * (weights.delivery || 0.15) +
      experienceScore * (weights.experience || 0.1) +
      sustainabilityScore * (weights.sustainability || 0.1) +
      innovationScore * (weights.innovation || 0.05);

    // Identify risk factors
    const riskFactors = this.identifyRiskFactors(bid, rfq, supplierData);

    // Identify strengths and weaknesses
    const { strengths, weaknesses } = this.identifyStrengthsAndWeaknesses(bid, rfq, {
      priceScore, qualityScore, deliveryScore, experienceScore, sustainabilityScore, innovationScore
    });

    return {
      bidId: bid.id,
      supplierId: bid.supplierId,
      overallScore,
      categoryScores: {
        price: priceScore,
        quality: qualityScore,
        delivery: deliveryScore,
        experience: experienceScore,
        sustainability: sustainabilityScore,
        innovation: innovationScore
      },
      pricePosition,
      riskFactors,
      strengths,
      weaknesses,
      recommendations: this.generateBidRecommendations(bid, rfq, riskFactors),
      confidence: this.calculateAnalysisConfidence(bid, supplierData)
    };
  }

  private async analyzePrice(bid: Bid, rfq: Rfq): Promise<number> {
    const estimatedValue = rfq.totalEstimatedValue;
    const bidValue = bid.totalValue;

    // Calculate price competitiveness (lower is better, but not too low)
    const priceRatio = bidValue / estimatedValue;

    if (priceRatio < 0.7) {
      // Too low - potential quality concerns
      return Math.max(20, 100 - (0.7 - priceRatio) * 200);
    } else if (priceRatio < 0.9) {
      // Competitive
      return 90 + (0.9 - priceRatio) * 100;
    } else if (priceRatio < 1.1) {
      // Reasonable
      return 80 - (priceRatio - 0.9) * 200;
    } else {
      // Too high
      return Math.max(10, 60 - (priceRatio - 1.1) * 100);
    }
  }

  private determinePricePosition(bid: Bid, rfq: Rfq): 'lowest' | 'competitive' | 'high' | 'outlier' {
    const allBids = rfq.bids.map(b => b.totalValue).sort((a, b) => a - b);
    if (allBids.length === 0) return 'competitive';

    const bidValue = bid.totalValue;
    const median = allBids[Math.floor(allBids.length / 2)];

    if (bidValue < (median || 0) * 0.9) return 'lowest';
    if (bidValue < (median || 0) * 1.1) return 'competitive';
    if (bidValue < (median || 0) * 1.3) return 'high';
    return 'outlier';
  }

  private async analyzeQuality(bid: Bid, rfq: Rfq, supplierData?: any): Promise<number> {
    let score = 50; // Base score

    // Check if bid meets all specifications
    const meetsSpecs = bid.items.every(item => {
      const rfqItem = rfq.items.find(rfqItem => rfqItem.id === item.rfqItemId);
      return rfqItem ? this.checkSpecificationCompliance(item, rfqItem) : false;
    });

    if (meetsSpecs) score += 30;

    // Supplier quality history
    if (supplierData?.qualityScore) {
      score += supplierData.qualityScore - 50; // Normalize around 50
    }

    // Certifications
    if (supplierData?.certifications?.includes('ISO9001')) score += 10;
    if (supplierData?.certifications?.includes('ISO14001')) score += 5;

    return Math.min(100, Math.max(0, score));
  }

  private async analyzeDelivery(bid: Bid, rfq: Rfq): Promise<number> {
    let score = 50; // Base score

    for (const item of bid.items) {
      const rfqItem = rfq.items.find(rfqItem => rfqItem.id === item.rfqItemId);
      if (!rfqItem) continue;

      const requiredDate = rfqItem.requiredDeliveryDate || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
      const proposedDate = item.deliveryDate;
      const daysDifference = (proposedDate.getTime() - requiredDate.getTime()) / (24 * 60 * 60 * 1000);

      if (daysDifference <= 0) {
        score += 20; // Early delivery
      } else if (daysDifference <= 7) {
        score += 10; // On time
      } else if (daysDifference <= 14) {
        score += 0; // Slightly late
      } else {
        score -= Math.min(30, daysDifference - 14); // Significantly late
      }
    }

    // Lead time analysis
    const avgLeadTime = bid.items.reduce((sum, item) => sum + item.leadTime, 0) / bid.items.length;
    if (avgLeadTime < 14) score += 10;
    else if (avgLeadTime > 30) score -= 10;

    return Math.min(100, Math.max(0, score));
  }

  private async analyzeExperience(supplierData?: any): Promise<number> {
    let score = 50; // Base score

    if (!supplierData) return score;

    // Years in business
    if (supplierData.yearsInBusiness) {
      if (supplierData.yearsInBusiness > 10) score += 20;
      else if (supplierData.yearsInBusiness > 5) score += 10;
      else if (supplierData.yearsInBusiness < 2) score -= 10;
    }

    // Previous contracts
    if (supplierData.completedContracts) {
      if (supplierData.completedContracts > 50) score += 15;
      else if (supplierData.completedContracts > 20) score += 10;
      else if (supplierData.completedContracts > 5) score += 5;
    }

    // Industry experience
    if (supplierData.industryExperience) {
      score += Math.min(10, supplierData.industryExperience / 2);
    }

    return Math.min(100, Math.max(0, score));
  }

  private async analyzeSustainability(supplierData?: any): Promise<number> {
    let score = 50; // Base score

    if (!supplierData) return score;

    // ESG score from risk assessment
    if (supplierData.esgScore) {
      score = supplierData.esgScore;
    }

    // Specific sustainability factors
    if (supplierData.renewableEnergyPercentage) {
      score += (supplierData.renewableEnergyPercentage - 50) * 0.4;
    }

    if (supplierData.carbonFootprint) {
      // Lower carbon footprint is better
      const industryAvg = 100000; // Example
      if (supplierData.carbonFootprint < industryAvg * 0.8) score += 10;
      else if (supplierData.carbonFootprint > industryAvg * 1.2) score -= 10;
    }

    return Math.min(100, Math.max(0, score));
  }

  private async analyzeInnovation(bid: Bid, supplierData?: any): Promise<number> {
    let score = 50; // Base score

    // Alternative proposals
    const hasAlternatives = bid.items.some(item => item.alternatives && item.alternatives.length > 0);
    if (hasAlternatives) score += 15;

    // Value-added services
    if (bid.terms.warranty && bid.terms.warranty !== 'standard') score += 10;

    // Supplier innovation history
    if (supplierData?.innovationProjects) {
      score += Math.min(15, supplierData.innovationProjects * 2);
    }

    return Math.min(100, Math.max(0, score));
  }

  private checkSpecificationCompliance(bidItem: any, rfqItem: any): boolean {
    // Simplified compliance check
    // In real implementation, this would validate detailed specifications
    return bidItem.quantity >= 0 && bidItem.unitPrice > 0;
  }

  private identifyRiskFactors(bid: Bid, rfq: Rfq, supplierData?: any): string[] {
    const risks: string[] = [];

    // Price too low
    if (bid.totalValue < rfq.totalEstimatedValue * 0.75) {
      risks.push('Price significantly below estimate - potential quality concerns');
    }

    // Delivery too late
    const lateDeliveries = bid.items.filter(item => {
      const rfqItem = rfq.items.find(r => r.id === item.rfqItemId);
      if (!rfqItem?.requiredDeliveryDate) return false;
      return item.deliveryDate > rfqItem.requiredDeliveryDate;
    });
    if (lateDeliveries.length > bid.items.length * 0.5) {
      risks.push('Multiple items delivered after required dates');
    }

    // Supplier risk
    if (supplierData?.riskLevel === 'high' || supplierData?.riskLevel === 'critical') {
      risks.push(`High supplier risk level: ${supplierData.riskLevel}`);
    }

    // New supplier
    if (!supplierData?.completedContracts || supplierData.completedContracts < 3) {
      risks.push('Limited supplier track record');
    }

    return risks;
  }

  private identifyStrengthsAndWeaknesses(
    bid: Bid,
    rfq: Rfq,
    scores: Record<string, number>
  ): { strengths: string[]; weaknesses: string[] } {
    const strengths: string[] = [];
    const weaknesses: string[] = [];

    const priceScore = scores.price || 50;
    const qualityScore = scores.quality || 50;
    const deliveryScore = scores.delivery || 50;
    const experienceScore = scores.experience || 50;

    // Price analysis
    if (priceScore > 80) {
      strengths.push('Highly competitive pricing');
    } else if (priceScore < 40) {
      weaknesses.push('Pricing above market expectations');
    }

    // Quality analysis
    if (qualityScore > 80) {
      strengths.push('Excellent quality credentials');
    } else if (qualityScore < 40) {
      weaknesses.push('Quality concerns identified');
    }

    // Delivery analysis
    if (deliveryScore > 80) {
      strengths.push('Superior delivery capabilities');
    } else if (deliveryScore < 40) {
      weaknesses.push('Delivery timeline concerns');
    }

    // Experience analysis
    if (experienceScore > 80) {
      strengths.push('Extensive industry experience');
    } else if (experienceScore < 40) {
      weaknesses.push('Limited experience in category');
    }

    return { strengths, weaknesses };
  }

  private generateBidRecommendations(bid: Bid, rfq: Rfq, riskFactors: string[]): string[] {
    const recommendations: string[] = [];

    if (riskFactors.length > 0) {
      recommendations.push('Conduct detailed risk assessment before awarding');
    }

    if (bid.totalValue > rfq.totalEstimatedValue * 1.2) {
      recommendations.push('Request price justification and breakdown');
    }

    if (bid.items.some(item => item.deliveryDate > new Date(Date.now() + 60 * 24 * 60 * 60 * 1000))) {
      recommendations.push('Review delivery schedule feasibility');
    }

    return recommendations;
  }

  private calculateAnalysisConfidence(bid: Bid, supplierData?: any): number {
    let confidence = 70; // Base confidence

    // More supplier data increases confidence
    if (supplierData) confidence += 10;

    // More detailed bid information increases confidence
    if (bid.attachments.length > 0) confidence += 5;
    if (bid.items.every(item => item.notes)) confidence += 5;

    // Historical data increases confidence
    if (supplierData?.completedContracts > 10) confidence += 10;

    return Math.min(95, confidence);
  }

  private async optimizeAwardAllocation(
    rfq: Rfq,
    scoredBids: BidAnalysisResult[],
    constraints?: any
  ): Promise<AwardRecommendation[]> {
    const recommendations: AwardRecommendation[] = [];

    // Simple optimization: award to highest scoring bids
    // In real implementation, this would use linear programming or ML optimization

    for (const analysis of scoredBids.slice(0, 3)) { // Top 3 bids
      const bid = rfq.bids.find(b => b.id === analysis.bidId);
      if (!bid) continue;

      const recommendation: AwardRecommendation = {
        bidId: bid.id,
        supplierId: bid.supplierId,
        recommendationReason: `Highest scoring bid with ${analysis.overallScore.toFixed(1)} points`,
        confidence: analysis.confidence,
        totalAwardValue: bid.totalValue,
        items: bid.items.map(item => ({
          rfqItemId: item.rfqItemId,
          awardedQuantity: item.quantity,
          awardedPrice: item.unitPrice,
          reason: 'Optimal price-quality combination'
        })),
        risks: analysis.riskFactors,
        benefits: analysis.strengths
      };

      recommendations.push(recommendation);
    }

    return recommendations;
  }

  private calculateAwardAnalysis(rfq: Rfq, recommendations: AwardRecommendation[]): any {
    const totalValue = recommendations.reduce((sum, rec) => sum + rec.totalAwardValue, 0);
    const savingsPotential = rfq.totalEstimatedValue - totalValue;

    // Simplified risk distribution
    const riskDistribution: Record<string, number> = {
      low: 0,
      medium: 0,
      high: 0,
      critical: 0
    };

    // Simplified supplier concentration
    const supplierConcentration: Record<string, number> = {};
    recommendations.forEach(rec => {
      supplierConcentration[rec.supplierId] = rec.totalAwardValue;
    });

    return {
      totalValue,
      savingsPotential,
      riskDistribution,
      supplierConcentration
    };
  }

  private calculateRecommendationConfidence(
    recommendations: AwardRecommendation[],
    bidAnalyses: BidAnalysisResult[]
  ): number {
    const avgConfidence = recommendations.reduce((sum, rec) => sum + rec.confidence, 0) / recommendations.length;
    const scoreVariance = this.calculateVariance(bidAnalyses.map(a => a.overallScore));

    // Lower variance = higher confidence
    const variancePenalty = Math.min(20, scoreVariance * 2);

    return Math.max(60, avgConfidence - variancePenalty);
  }

  private generateRecommendationReasoning(
    recommendations: AwardRecommendation[],
    rfq: Rfq,
    constraints?: any
  ): string[] {
    const reasoning: string[] = [];

    reasoning.push(`Analyzed ${rfq.bids.length} bids for RFQ ${rfq.id}`);
    reasoning.push(`Selected ${recommendations.length} optimal supplier(s) based on evaluation criteria`);

    if (constraints?.maxAwardPerSupplier) {
      reasoning.push(`Applied supplier award limit: ${constraints.maxAwardPerSupplier}`);
    }

    const totalSavings = recommendations.reduce((sum, rec) => {
      const bid = rfq.bids.find(b => b.id === rec.bidId);
      return sum + ((bid?.totalValue || 0) - rec.totalAwardValue);
    }, 0);

    if (totalSavings > 0) {
      reasoning.push(`Estimated savings: ${totalSavings.toFixed(2)} ${rfq.currency}`);
    }

    return reasoning;
  }

  private calculateVariance(values: number[]): number {
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const squaredDiffs = values.map(val => Math.pow(val - mean, 2));
    return squaredDiffs.reduce((sum, diff) => sum + diff, 0) / values.length;
  }

  private getBasePriceForCategory(category: string): number {
    // Simplified pricing model
    const categoryPrices: Record<string, number> = {
      'IT Services': 150000,
      'Manufacturing': 500000,
      'Consulting': 200000,
      'Facilities': 100000,
      'Office Supplies': 50000
    };

    return categoryPrices[category] || 100000;
  }
}

export default AIBiddingEngine;