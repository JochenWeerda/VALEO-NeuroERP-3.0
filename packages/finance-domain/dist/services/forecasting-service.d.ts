/**
 * VALEO NeuroERP 3.0 - Forecasting Service
 *
 * AI-powered financial forecasting with cashflow and P&L predictions
 * Supports what-if scenarios, uncertainty bands, and performance metrics
 */
import { Result } from '../core/entities/ar-invoice';
export interface CashflowForecast {
    readonly id: string;
    readonly tenantId: string;
    readonly forecastDate: Date;
    readonly horizonDays: number;
    readonly scenario: string;
    readonly data: CashflowDataPoint[];
    readonly confidence: number;
    readonly metadata: Record<string, any>;
    readonly generatedAt: Date;
}
export interface CashflowDataPoint {
    date: string;
    predicted: number;
    upperBound: number;
    lowerBound: number;
    confidence: number;
    components: {
        operating: number;
        investing: number;
        financing: number;
    };
}
export interface PLForecast {
    readonly id: string;
    readonly tenantId: string;
    readonly forecastDate: Date;
    readonly horizonDays: number;
    readonly scenario: string;
    readonly data: PLDataPoint[];
    readonly metrics: ForecastMetrics;
    readonly generatedAt: Date;
}
export interface PLDataPoint {
    date: string;
    revenue: number;
    costOfSales: number;
    grossProfit: number;
    operatingExpenses: number;
    operatingProfit: number;
    netProfit: number;
    confidence: number;
}
export interface ForecastMetrics {
    mape: number;
    mae: number;
    rmse: number;
    bias: number;
    accuracy: number;
}
export interface ForecastScenario {
    readonly id: string;
    readonly name: string;
    readonly description: string;
    readonly parameters: ScenarioParameters;
    readonly isActive: boolean;
    readonly createdAt: Date;
}
export interface ScenarioParameters {
    revenueGrowth?: number;
    costInflation?: number;
    seasonalityFactor?: number;
    marketConditions?: 'OPTIMISTIC' | 'NEUTRAL' | 'PESSIMISTIC';
    customAdjustments?: Record<string, number>;
}
export interface ForecastComparison {
    scenario: string;
    cashflow: CashflowForecast;
    pl: PLForecast;
    comparison: {
        bestCase: string;
        worstCase: string;
        expectedCase: string;
    };
}
export interface GenerateCashflowForecastCommand {
    readonly tenantId: string;
    readonly horizonDays: number;
    readonly scenario?: string;
    readonly includeComponents?: boolean;
    readonly confidenceLevel?: number;
}
export interface GeneratePLForecastCommand {
    readonly tenantId: string;
    readonly horizonDays: number;
    readonly scenario?: string;
    readonly includeSeasonality?: boolean;
}
export interface CreateScenarioCommand {
    readonly tenantId: string;
    readonly name: string;
    readonly description: string;
    readonly parameters: ScenarioParameters;
}
export interface CompareScenariosCommand {
    readonly tenantId: string;
    readonly scenarioIds: string[];
    readonly horizonDays: number;
}
export declare class ForecastingApplicationService {
    private forecastRepo;
    private scenarioRepo;
    private historicalDataService;
    private aiForecastEngine;
    private eventPublisher;
    constructor(forecastRepo: ForecastRepository, scenarioRepo: ScenarioRepository, historicalDataService: HistoricalDataService, aiForecastEngine: AIForecastEngine, eventPublisher: EventPublisher);
    /**
     * Generate cashflow forecast
     */
    generateCashflowForecast(command: GenerateCashflowForecastCommand): Promise<Result<CashflowForecast>>;
    /**
     * Generate P&L forecast
     */
    generatePLForecast(command: GeneratePLForecastCommand): Promise<Result<PLForecast>>;
    /**
     * Create forecast scenario
     */
    createScenario(command: CreateScenarioCommand): Promise<Result<ForecastScenario>>;
    /**
     * Compare multiple scenarios
     */
    compareScenarios(command: CompareScenariosCommand): Promise<Result<ForecastComparison[]>>;
    /**
     * Get forecast accuracy metrics
     */
    getForecastAccuracy(tenantId: string, days?: number): Promise<Result<ForecastMetrics>>;
    /**
     * Calculate uncertainty bands for forecast
     */
    private calculateUncertaintyBands;
    /**
     * Calculate forecast accuracy metrics
     */
    private calculateAccuracyMetrics;
    /**
     * Calculate forecast metrics
     */
    private calculateForecastMetrics;
}
export interface AIForecastEngine {
    predictCashflow(historicalData: CashflowDataPoint[], horizonDays: number, scenarioParams: ScenarioParameters, confidenceLevel: number): Promise<CashflowDataPoint[]>;
    predictPL(historicalData: PLDataPoint[], horizonDays: number, scenarioParams: ScenarioParameters, includeSeasonality: boolean): Promise<PLDataPoint[]>;
}
export declare class SimpleAIForecastEngine implements AIForecastEngine {
    predictCashflow(historicalData: CashflowDataPoint[], horizonDays: number, scenarioParams: ScenarioParameters, confidenceLevel: number): Promise<CashflowDataPoint[]>;
    predictPL(historicalData: PLDataPoint[], horizonDays: number, scenarioParams: ScenarioParameters, includeSeasonality: boolean): Promise<PLDataPoint[]>;
    private calculateTrend;
}
export interface ForecastRepository {
    saveCashflowForecast(forecast: CashflowForecast): Promise<void>;
    savePLForecast(forecast: PLForecast): Promise<void>;
    findCashflowForecast(tenantId: string, scenario: string, horizonDays: number): Promise<CashflowForecast | null>;
    findPLForecast(tenantId: string, scenario: string, horizonDays: number): Promise<PLForecast | null>;
    findRecentForecasts(tenantId: string, days: number): Promise<CashflowDataPoint[]>;
}
export interface ScenarioRepository {
    save(scenario: ForecastScenario): Promise<void>;
    findById(id: string): Promise<ForecastScenario | null>;
    findByName(tenantId: string, name: string): Promise<ForecastScenario | null>;
    findActiveScenarios(tenantId: string): Promise<ForecastScenario[]>;
}
export interface HistoricalDataService {
    getCashflowHistory(tenantId: string, days: number): Promise<CashflowDataPoint[]>;
    getPLHistory(tenantId: string, days: number): Promise<PLDataPoint[]>;
    getActualData(tenantId: string, days: number): Promise<CashflowDataPoint[]>;
}
export interface EventPublisher {
    publish(event: any): Promise<void>;
}
export declare function generateScenarioComparison(scenarios: ForecastComparison[]): {
    bestCase: string;
    worstCase: string;
    expectedCase: string;
    variance: number;
};
//# sourceMappingURL=forecasting-service.d.ts.map