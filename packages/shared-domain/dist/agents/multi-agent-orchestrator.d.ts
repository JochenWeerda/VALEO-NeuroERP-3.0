/**
 * Multi-Agent Orchestration Service - VALEO-NeuroERP-3.0
 * Week 7: AI Agent Systems Implementation
 * Clean Architecture integration with Agent Intelligence
 */
export interface AIAgent {
    readonly id: string;
    readonly type: AgentType;
    processTask(context: WorkflowContext): Promise<AgentResult>;
    analyzePerformance(): Promise<AgentMetrics>;
}
export type AgentType = 'CRM' | 'Finance' | 'Inventory' | 'Analytics' | 'Security';
export interface WorkflowContext {
    readonly userId: string;
    readonly sessionId: string;
    readonly businessContext: BusinessContext;
    readonly dataPayload: Record<string, any>;
    readonly priority: TaskPriority;
}
export interface AgentResult {
    readonly agentId: string;
    readonly taskId: string;
    readonly status: 'SUCCESS' | 'FAILED' | 'PARTIAL';
    readonly insights: BusinessInsights[];
    readonly recommendations: string[];
    readonly metrics: AgentMetrics;
}
export interface BusinessInsights {
    readonly category: string;
    readonly insight: string;
    readonly confidence: number;
    readonly dataEvidence: any[];
}
export interface AgentMetrics {
    readonly executionTimeMs: number;
    readonly accuracyScore: number;
    readonly confidenceLevel: number;
    readonly businessImpact: number;
}
export declare class MultiAgentOrchestrationService {
    private readonly ragService;
    private readonly llmService;
    private readonly messageBus;
    private readonly eventPublisher;
    private readonly activeAgents;
    private readonly agentResults;
    private readonly orchestrationHistory;
    constructor(ragService: RAGService, llmService: LLMService, messageBus: MessageBus, eventPublisher: EventPublisher);
    /**
     * Execute orchestrated workflow across multiple AI agents
     */
    executeERPWorkflowAuto(workflowId: string, context: WorkflowContext): Promise<WorkflowExecutionResult>;
    private configureWorkflowAgents;
    private processAgentsOrchestration;
    private aggregateAgentResults;
    private updateKnowledgeBase;
    private combineInsights;
    private deduplicateInsight;
}
export interface WorkflowExecutionResult {
    readonly executionId: string;
    readonly totalAgentsExecuted: number;
    readonly successfulAgents: number;
    readonly failedAgents: number;
    readonly combinedInsights: BusinessInsights[];
    readonly overallConfidence: number;
    readonly recommendations: string[];
    readonly executionMetrics: ExecutionMetrics;
}
export interface ExecutionMetrics {
    readonly totalTimeMs: number;
    readonly averageAccuracy: number;
    readonly businessImpactScore: number;
}
export interface MessageBus {
    publish(message: AgentMessage): Promise<void>;
    subscribe(agentId: string, callback: (message: AgentMessage) => void): void;
}
export interface RAGService {
    retrieveRelevantKnowledge(agentType: string, context: WorkflowContext): Promise<Knowledge>;
    storeNewKnowledge(knowledge: Knowledge): Promise<void>;
}
export interface Knowledge {
    readonly type: string;
    readonly insights: BusinessInsights[];
    readonly recommendations: string[];
    readonly executionContext: any;
}
export interface AgentMessage {
    readonly fromAgentId: string;
    readonly toAgentId: string;
    readonly messageType: string;
    readonly payload: any;
}
//# sourceMappingURL=multi-agent-orchestrator.d.ts.map