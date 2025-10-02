"use strict";
/**
 * Multi-Agent Orchestration Service - VALEO-NeuroERP-3.0
 * Week 7: AI Agent Systems Implementation
 * Clean Architecture integration with Agent Intelligence
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.MultiAgentOrchestrationService = void 0;
// ===== MULTI-AGENT ORCHESTRATION SERVICE =====
class MultiAgentOrchestrationService {
    ragService;
    llmService;
    messageBus;
    eventPublisher;
    activeAgents = new Map();
    agentResults = [];
    orchestrationHistory = [];
    constructor(ragService, llmService, messageBus, eventPublisher) {
        this.ragService = ragService;
        this.llmService = llmService;
        this.messageBus = messageBus;
        this.eventPublisher = eventPublisher;
    }
    /**
     * Execute orchestrated workflow across multiple AI agents
     */
    async executeERPWorkflowAuto(workflowId, context) {
        console.log(`🤖 VALEO-NeuroERP Agent Orchestration Started: ${workflowId}`);
        try {
            // 1. Initialize agents based on workflow requirements
            const configuredAgents = await this.configureWorkflowAgents(workflowId, context);
            // 2. Execute agency v1peги Силистер//
            const orchestrationResult = await this.processAgentsOrchestration(configuredAgents, context);
            // 3. Aggregate agent results
            const workflowResult = await this.aggregateAgentResults(orchestrationResult);
            // 4. Store orchestration knowledge for RAG
            await this.updateKnowledgeBase(workflowResult);
            console.log(`✅ Agent Orchestration Complete: ${workflowId}`);
            return workflowResult;
        }
        catch (error) {
            console.error(`❌ Agent Orchestration Failed: ${error}`);
            throw new Error(`Agent orchestration execution failed: ${error}`);
        }
    }
    async configureWorkflowAgents(workflowId, context) {
        const agents = [];
        // Determine agent requirements based on business context
        if (context.businessContext.involvesCRM) {
            agents.push(new CRMBusinessAgent(this.ragService));
        }
        if (context.businessContext.involvesFinance) {
            agents.push(new FinanceAnalyticsAgent(this.llmService));
        }
        if (context.businessContext.involvesInventory) {
            agents.push(new InventoryOptimizerAgent(this.ragService));
        }
        if (context.businessContext.involvesAnalytics) {
            agents.push(new PredictiveAnalyticsAgent(this.llmService));
        }
        return agents;
    }
    async processAgentsOrchestration(agents, context) {
        const results = [];
        for (const agent of agents) {
            // 1. Retrieve contextual knowledge
            const knowledge = await this.ragService.retrieveRelevantKnowledge(agent.type, context);
            // 2. Execute agent task
            const result = await agent.processTask({
                ...context,
                agentKnowledge: knowledge
            });
            results.push(result);
            this.agentResults.push(result);
            // 3. Publish agent event
            await this.eventPublisher.publishAgentCompleted(result);
            console.log(`🤖 Agent ${agent.id} completed: ${result.status}`);
        }
        return results;
    }
    async aggregateAgentResults(results) {
        return {
            executionId: Date.now().toString(),
            totalAgentsExecuted: results.length,
            successfulAgents: results.filter(r => r.status === 'SUCCESS').length,
            failedAgents: results.filter(r => r.status === 'FAILED').length,
            combinedInsights: this.combineInsights(results),
            overallConfidence: this.calculateOverallConfidence(results),
            recommendations: this.generateFinalRecommendations(results),
            executionMetrics: this.computeExecutionMetrics(results)
        };
    }
    async updateKnowledgeBase(result) {
        const newKnowledge = {
            type: 'Agent Orchestration',
            insights: result.combinedInsights,
            recommendations: result.recommendations,
            executionContext: result.executionMetrics
        };
        await this.ragService.storeNewKnowledge(newKnowledge);
    }
    // ===== INSIGHTS & RECOMMENDATIONS COMPILATION =====
    combineInsights(results) {
        const allInsights = [];
        for (const result of results) {
            allInsights.push(...result.insights);
        }
        // Remove duplicates and rank by confidence
        return this.deduplicateAndRankInsights(allInsights);
    }
    deduplicateInsight(insights, similarThreshold = 0.8) {
        const uniqueInsights = [];
        for (const insight of insights) {
            const isDuplicate = uniqueInsights.some(existing => this.calculateInsightSimilarity(insight, existing) > similarThreshold);
            if (!isDuplicate) {
                uniqueInsights.push(insight);
            }
        }
        return uniqueInsights.sort((a, b) => b.confidence - a.confidence);
    }
}
exports.MultiAgentOrchestrationService = MultiAgentOrchestrationService;
