/**
 * VALEO NeuroERP 3.0 - Inventory Backend for Frontend (BFF)
 *
 * Conversational AI interface for warehouse operations
 */

import { injectable } from 'inversify';
import express from 'express';
import { ReceivingService } from '../services/receiving-service';
import { PutawaySlottingService } from '../services/putaway-slotting-service';
import { InventoryControlService } from '../services/inventory-control-service';
import { ReplenishmentService } from '../services/replenishment-service';
import { PickingService } from '../services/picking-service';
import { PackingShippingService } from '../services/packing-shipping-service';
import { CycleCountingService } from '../services/cycle-counting-service';
import { ReturnsDispositionService } from '../services/returns-disposition-service';
import { WCSWESAdapterService } from '../services/wcs-wes-adapter-service';
import { TraceabilityService } from '../services/traceability-service';
import { InventoryMetricsService } from '../infrastructure/observability/metrics-service';

export interface ConversationContext {
  sessionId: string;
  userId: string;
  currentIntent?: string;
  entities: Record<string, any>;
  conversationHistory: Array<{
    role: 'user' | 'assistant';
    message: string;
    timestamp: Date;
    intent?: string;
    entities?: Record<string, any>;
  }>;
  activeWorkflow?: {
    workflowId: string;
    step: number;
    totalSteps: number;
    data: Record<string, any>;
  };
  preferences: {
    language: string;
    units: 'metric' | 'imperial';
    timezone: string;
    notifications: boolean;
  };
}

export interface AIIntent {
  intent: string;
  confidence: number;
  entities: Record<string, any>;
  response: {
    type: 'text' | 'card' | 'table' | 'chart' | 'action';
    content: any;
    actions?: Array<{
      type: 'button' | 'link' | 'command';
      label: string;
      value: string;
      style?: 'primary' | 'secondary' | 'danger';
    }>;
  };
  followUp?: {
    question: string;
    suggestions: string[];
  };
}

export interface InventoryQuery {
  type: 'status' | 'location' | 'movement' | 'forecast' | 'analytics';
  filters: {
    sku?: string;
    location?: string;
    category?: string;
    dateRange?: { start: Date; end: Date };
    status?: string;
  };
  aggregation?: 'sum' | 'avg' | 'count' | 'min' | 'max';
  groupBy?: string[];
}

@injectable()
export class InventoryBFF {
  private readonly metrics = new InventoryMetricsService();
  private conversations: Map<string, ConversationContext> = new Map();

  constructor(
    private readonly receivingService: ReceivingService,
    private readonly putawaySlottingService: PutawaySlottingService,
    private readonly inventoryControlService: InventoryControlService,
    private readonly replenishmentService: ReplenishmentService,
    private readonly pickingService: PickingService,
    private readonly packingShippingService: PackingShippingService,
    private readonly cycleCountingService: CycleCountingService,
    private readonly returnsDispositionService: ReturnsDispositionService,
    private readonly wcsWesAdapterService: WCSWESAdapterService,
    private readonly traceabilityService: TraceabilityService
  ) {}

  /**
   * Process natural language query
   */
  async processQuery(sessionId: string, userId: string, query: string): Promise<AIIntent> {
    const startTime = Date.now();

    try {
      // Get or create conversation context
      let context = this.conversations.get(sessionId);
      if (!context) {
        context = this.createConversationContext(sessionId, userId);
        this.conversations.set(sessionId, context);
      }

      // Add user message to history
      context.conversationHistory.push({
        role: 'user',
        message: query,
        timestamp: new Date()
      });

      // Analyze intent and entities
      const intent = await this.analyzeIntent(query, context);

      // Update context
      context.currentIntent = intent.intent;
      context.entities = { ...context.entities, ...intent.entities };

      // Add assistant response to history
      context.conversationHistory.push({
        role: 'assistant',
        message: typeof intent.response.content === 'string' ? intent.response.content : JSON.stringify(intent.response.content),
        timestamp: new Date(),
        intent: intent.intent,
        entities: intent.entities
      });

      // Execute any actions
      if (intent.response.actions) {
        await this.executeActions(intent.response.actions, context);
      }

      this.metrics.recordDatabaseQueryDuration('inventory_bff', 'query_processing', (Date.now() - startTime) / 1000);

      return intent;
    } catch (error) {
      this.metrics.incrementErrorCount('inventory_bff', 'query_processing_failed');
      throw error;
    }
  }

  /**
   * Get inventory dashboard data
   */
  async getDashboardData(userId: string, filters?: { warehouse?: string; dateRange?: { start: Date; end: Date } }): Promise<{
    overview: {
      totalItems: number;
      totalValue: number;
      lowStockItems: number;
      expiringItems: number;
      activeTasks: number;
    };
    alerts: Array<{
      type: 'warning' | 'error' | 'info';
      title: string;
      message: string;
      action?: string;
    }>;
    recentActivity: Array<{
      type: string;
      description: string;
      timestamp: Date;
      user?: string;
    }>;
    performance: {
      receivingAccuracy: number;
      pickingAccuracy: number;
      inventoryAccuracy: number;
      throughput: number;
    };
  }> {
    const startTime = Date.now();

    try {
      // Get overview data
      const overview = await this.getOverviewData(filters);

      // Get alerts
      const alerts = await this.getActiveAlerts(userId);

      // Get recent activity
      const recentActivity = await this.getRecentActivity(filters);

      // Get performance metrics
      const performance = await this.getPerformanceMetrics(filters);

      this.metrics.recordDatabaseQueryDuration('inventory_bff', 'dashboard_data', (Date.now() - startTime) / 1000);

      return {
        overview,
        alerts,
        recentActivity,
        performance
      };
    } catch (error) {
      this.metrics.incrementErrorCount('inventory_bff', 'dashboard_failed');
      throw error;
    }
  }

  /**
   * Execute workflow step
   */
  async executeWorkflowStep(sessionId: string, stepData: Record<string, any>): Promise<{
    completed: boolean;
    nextStep?: number;
    result?: any;
    message: string;
  }> {
    const context = this.conversations.get(sessionId);
    if (!context?.activeWorkflow) {
      throw new Error('No active workflow');
    }

    const workflow = context.activeWorkflow;
    workflow.data = { ...workflow.data, ...stepData };

    // Execute current step
    const result = await this.executeWorkflowStepLogic(workflow, stepData);

    if (result.completed) {
      workflow.step++;
      if (workflow.step >= workflow.totalSteps) {
        // Workflow completed
        context.activeWorkflow = undefined;
        return {
          completed: true,
          result: result.data,
          message: 'Workflow completed successfully'
        };
      } else {
        // Next step
        return {
          completed: false,
          nextStep: workflow.step,
          message: `Step ${workflow.step} completed. Proceeding to next step.`
        };
      }
    } else {
      return {
        completed: false,
        message: result.message || 'Step execution failed'
      };
    }
  }

  /**
   * Get conversation history
   */
  getConversationHistory(sessionId: string): ConversationContext['conversationHistory'] {
    const context = this.conversations.get(sessionId);
    return context?.conversationHistory || [];
  }

  /**
   * Clear conversation context
   */
  clearConversation(sessionId: string): void {
    this.conversations.delete(sessionId);
  }

  // Private helper methods

  private createConversationContext(sessionId: string, userId: string): ConversationContext {
    return {
      sessionId,
      userId,
      entities: {},
      conversationHistory: [],
      preferences: {
        language: 'en',
        units: 'metric',
        timezone: 'UTC',
        notifications: true
      }
    };
  }

  private async analyzeIntent(query: string, context: ConversationContext): Promise<AIIntent> {
    const lowerQuery = query.toLowerCase();

    // Simple rule-based intent recognition (in production, use NLP model)
    if (lowerQuery.includes('inventory') && lowerQuery.includes('status')) {
      return await this.handleInventoryStatusQuery(context);
    }

    if (lowerQuery.includes('pick') || lowerQuery.includes('picking')) {
      return await this.handlePickingQuery(query, context);
    }

    if (lowerQuery.includes('receive') || lowerQuery.includes('receiving')) {
      return await this.handleReceivingQuery(query, context);
    }

    if (lowerQuery.includes('location') || lowerQuery.includes('where')) {
      return await this.handleLocationQuery(query, context);
    }

    if (lowerQuery.includes('forecast') || lowerQuery.includes('predict')) {
      return await this.handleForecastQuery(query, context);
    }

    if (lowerQuery.includes('trace') || lowerQuery.includes('track')) {
      return await this.handleTraceabilityQuery(query, context);
    }

    if (lowerQuery.includes('count') || lowerQuery.includes('cycle')) {
      return await this.handleCycleCountQuery(query, context);
    }

    if (lowerQuery.includes('report') || lowerQuery.includes('analytics')) {
      return await this.handleAnalyticsQuery(context);
    }

    // Default response
    return {
      intent: 'unknown',
      confidence: 0.5,
      entities: {},
      response: {
        type: 'text',
        content: "I'm sorry, I didn't understand that request. Try asking about inventory status, picking, receiving, locations, forecasts, or analytics."
      },
      followUp: {
        question: "What would you like to know about the warehouse?",
        suggestions: [
          "What's the current inventory status?",
          "Show me picking tasks",
          "Where is item XYZ located?",
          "Generate a forecast report",
          "Show analytics dashboard"
        ]
      }
    };
  }

  private async handleInventoryStatusQuery(context: ConversationContext): Promise<AIIntent> {
    const dashboard = await this.getDashboardData(context.userId);

    return {
      intent: 'inventory_status',
      confidence: 0.9,
      entities: {},
      response: {
        type: 'card',
        content: {
          title: 'Inventory Overview',
          sections: [
            {
              title: 'Summary',
              items: [
                `Total Items: ${dashboard.overview.totalItems.toLocaleString()}`,
                `Total Value: €${dashboard.overview.totalValue.toLocaleString()}`,
                `Low Stock Items: ${dashboard.overview.lowStockItems}`,
                `Expiring Items: ${dashboard.overview.expiringItems}`
              ]
            },
            {
              title: 'Performance',
              items: [
                `Receiving Accuracy: ${dashboard.performance.receivingAccuracy}%`,
                `Picking Accuracy: ${dashboard.performance.pickingAccuracy}%`,
                `Inventory Accuracy: ${dashboard.performance.inventoryAccuracy}%`,
                `Daily Throughput: ${dashboard.performance.throughput} items`
              ]
            }
          ]
        },
        actions: [
          {
            type: 'button',
            label: 'View Details',
            value: 'show_inventory_details',
            style: 'primary'
          },
          {
            type: 'button',
            label: 'Generate Report',
            value: 'generate_inventory_report',
            style: 'secondary'
          }
        ]
      }
    };
  }

  private async handlePickingQuery(query: string, context: ConversationContext): Promise<AIIntent> {
    // Extract entities from query
    const entities = this.extractEntities(query);

    const tasks = await this.pickingService.getActiveTasks();
    const filteredTasks = tasks.filter(task =>
      !entities.sku || task.items.some(item => item.sku === entities.sku)
    );

    return {
      intent: 'picking_query',
      confidence: 0.85,
      entities,
      response: {
        type: 'table',
        content: {
          title: 'Active Picking Tasks',
          headers: ['Task ID', 'Priority', 'Items', 'Status', 'Assigned To'],
          rows: filteredTasks.slice(0, 10).map(task => [
            task.taskId,
            task.priority,
            task.items.length,
            task.status,
            task.assignedTo || 'Unassigned'
          ]),
          totalRows: filteredTasks.length
        },
        actions: [
          {
            type: 'button',
            label: 'Create New Task',
            value: 'create_picking_task',
            style: 'primary'
          },
          {
            type: 'button',
            label: 'View All Tasks',
            value: 'view_all_picking_tasks',
            style: 'secondary'
          }
        ]
      }
    };
  }

  private async handleReceivingQuery(query: string, context: ConversationContext): Promise<AIIntent> {
    const entities = this.extractEntities(query);

    // Start receiving workflow
    context.activeWorkflow = {
      workflowId: 'receiving_workflow',
      step: 1,
      totalSteps: 3,
      data: { ...entities }
    };

    return {
      intent: 'receiving_assistance',
      confidence: 0.9,
      entities,
      response: {
        type: 'text',
        content: "I'll help you with receiving. Please provide the ASN number or purchase order number."
      },
      followUp: {
        question: "What's the ASN or PO number?",
        suggestions: []
      }
    };
  }

  private async handleLocationQuery(query: string, context: ConversationContext): Promise<AIIntent> {
    const entities = this.extractEntities(query);

    if (!entities.sku) {
      return {
        intent: 'location_query_incomplete',
        confidence: 0.7,
        entities,
        response: {
          type: 'text',
          content: "I need to know which item you're looking for. Please specify the SKU."
        },
        followUp: {
          question: "What's the SKU of the item?",
          suggestions: []
        }
      };
    }

    const locations = await this.inventoryControlService.findItemLocations(entities.sku);

    return {
      intent: 'location_query',
      confidence: 0.9,
      entities,
      response: {
        type: 'table',
        content: {
          title: `Locations for ${entities.sku}`,
          headers: ['Location', 'Quantity', 'Lot', 'Serial', 'Last Updated'],
          rows: locations.map(loc => [
            loc.location,
            loc.quantity,
            loc.lot || 'N/A',
            loc.serial || 'N/A',
            loc.lastUpdated.toLocaleDateString()
          ])
        }
      }
    };
  }

  private async handleForecastQuery(query: string, context: ConversationContext): Promise<AIIntent> {
    const entities = this.extractEntities(query);

    if (!entities.sku) {
      return {
        intent: 'forecast_query_incomplete',
        confidence: 0.7,
        entities,
        response: {
          type: 'text',
          content: "I'll generate a forecast. Which item would you like to forecast?"
        },
        followUp: {
          question: "What's the SKU for the forecast?",
          suggestions: []
        }
      };
    }

    const forecast = await this.wcsWesAdapterService.generateInventoryForecast(
      entities.sku,
      'demand',
      {
        start: new Date(),
        end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
        granularity: 'day'
      }
    );

    return {
      intent: 'forecast_generated',
      confidence: 0.9,
      entities,
      response: {
        type: 'chart',
        content: {
          title: `Demand Forecast for ${entities.sku}`,
          type: 'line',
          data: {
            labels: forecast.forecast.map(f => f.timestamp.toLocaleDateString()),
            datasets: [{
              label: 'Predicted Demand',
              data: forecast.forecast.map(f => f.predictedValue),
              borderColor: 'rgb(75, 192, 192)',
              tension: 0.1
            }]
          }
        }
      }
    };
  }

  private async handleTraceabilityQuery(query: string, context: ConversationContext): Promise<AIIntent> {
    const entities = this.extractEntities(query);

    if (!entities.epc && !entities.sku) {
      return {
        intent: 'traceability_query_incomplete',
        confidence: 0.7,
        entities,
        response: {
          type: 'text',
          content: "I can help you trace products. Please provide an EPC or SKU."
        },
        followUp: {
          question: "What's the EPC or SKU to trace?",
          suggestions: []
        }
      };
    }

    const genealogy = await this.traceabilityService.getProductGenealogy(entities.epc || entities.sku!);

    return {
      intent: 'traceability_result',
      confidence: 0.9,
      entities,
      response: {
        type: 'card',
        content: {
          title: `Product Genealogy for ${entities.epc || entities.sku}`,
          sections: [
            {
              title: 'Parents',
              items: genealogy.parents.length > 0 ? genealogy.parents : ['None']
            },
            {
              title: 'Children',
              items: genealogy.children.length > 0 ? genealogy.children : ['None']
            },
            {
              title: 'Transformations',
              items: genealogy.transformations.map(t => `${t.type} at ${t.performedAt.toLocaleDateString()}`)
            }
          ]
        }
      }
    };
  }

  private async handleCycleCountQuery(query: string, context: ConversationContext): Promise<AIIntent> {
    const performance = await this.cycleCountingService.getCycleCountPerformance('month');

    return {
      intent: 'cycle_count_status',
      confidence: 0.85,
      entities: {},
      response: {
        type: 'card',
        content: {
          title: 'Cycle Count Performance',
          sections: [
            {
              title: 'Current Month',
              items: [
                `Total Counts: ${performance.metrics.totalCounts}`,
                `Accuracy: ${performance.metrics.accuracy.toFixed(1)}%`,
                `Average Variance: ${performance.metrics.averageVariance.toFixed(2)}%`,
                `Items/Hour: ${performance.metrics.itemsPerHour.toFixed(1)}`
              ]
            }
          ]
        },
        actions: [
          {
            type: 'button',
            label: 'Start New Count',
            value: 'start_cycle_count',
            style: 'primary'
          },
          {
            type: 'button',
            label: 'View Details',
            value: 'view_cycle_count_details',
            style: 'secondary'
          }
        ]
      }
    };
  }

  private async handleAnalyticsQuery(context: ConversationContext): Promise<AIIntent> {
    const dashboard = await this.getDashboardData(context.userId);

    return {
      intent: 'analytics_dashboard',
      confidence: 0.9,
      entities: {},
      response: {
        type: 'chart',
        content: {
          title: 'Warehouse Performance Analytics',
          type: 'bar',
          data: {
            labels: ['Receiving', 'Picking', 'Inventory', 'Shipping'],
            datasets: [{
              label: 'Accuracy %',
              data: [
                dashboard.performance.receivingAccuracy,
                dashboard.performance.pickingAccuracy,
                dashboard.performance.inventoryAccuracy,
                98.5 // Shipping accuracy
              ],
              backgroundColor: 'rgba(54, 162, 235, 0.5)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            }]
          }
        }
      }
    };
  }

  private extractEntities(query: string): Record<string, any> {
    const entities: Record<string, any> = {};

    // Simple entity extraction (in production, use NLP)
    const skuMatch = query.match(/sku\s*[\w-]+/i);
    if (skuMatch) {
      entities.sku = skuMatch[0].replace(/sku\s*/i, '');
    }

    const epcMatch = query.match(/epc\s*[\w-]+/i);
    if (epcMatch) {
      entities.epc = epcMatch[0].replace(/epc\s*/i, '');
    }

    const locationMatch = query.match(/location\s*[\w-]+/i);
    if (locationMatch) {
      entities.location = locationMatch[0].replace(/location\s*/i, '');
    }

    return entities;
  }

  private async executeActions(actions: AIIntent['response']['actions'], context: ConversationContext): Promise<void> {
    for (const action of actions || []) {
      switch (action.value) {
        case 'show_inventory_details':
          // Trigger detailed inventory view
          break;
        case 'generate_inventory_report':
          // Generate and send report
          break;
        case 'create_picking_task':
          // Start picking task creation workflow
          break;
        case 'start_cycle_count':
          // Start cycle count workflow
          break;
        // Add more actions as needed
      }
    }
  }

  private async executeWorkflowStepLogic(workflow: ConversationContext['activeWorkflow'], stepData: Record<string, any>): Promise<{ completed: boolean; data?: any; message?: string }> {
    switch (workflow.workflowId) {
      case 'receiving_workflow':
        return await this.executeReceivingWorkflowStep(workflow, stepData);
      default:
        return { completed: false, message: 'Unknown workflow' };
    }
  }

  private async executeReceivingWorkflowStep(workflow: ConversationContext['activeWorkflow'], stepData: Record<string, any>): Promise<{ completed: boolean; data?: any; message?: string }> {
    switch (workflow.step) {
      case 1:
        // Validate ASN/PO
        const asnData = await this.receivingService.validateASN(stepData.asnNumber);
        workflow.data.asnData = asnData;
        return { completed: true, message: 'ASN validated successfully' };

      case 2:
        // Process receiving
        const receivingResult = await this.receivingService.processASN(stepData.asnNumber, stepData.receivedItems);
        workflow.data.receivingResult = receivingResult;
        return { completed: true, message: 'Items received successfully' };

      case 3:
        // Generate putaway tasks
        const putawayTasks = await this.putawaySlottingService.createPutawayTasks(stepData.asnNumber);
        workflow.data.putawayTasks = putawayTasks;
        return { completed: true, data: putawayTasks, message: 'Putaway tasks created' };

      default:
        return { completed: false, message: 'Invalid step' };
    }
  }

  private async getOverviewData(filters?: any): Promise<any> {
    // Mock data - would aggregate from actual services
    return {
      totalItems: 125000,
      totalValue: 2500000,
      lowStockItems: 1250,
      expiringItems: 340,
      activeTasks: 45
    };
  }

  private async getActiveAlerts(userId: string): Promise<any[]> {
    // Mock alerts
    return [
      {
        type: 'warning',
        title: 'Low Stock Alert',
        message: 'Item WIDGET-001 is below minimum stock level',
        action: 'replenish'
      },
      {
        type: 'info',
        title: 'Receiving Due',
        message: 'ASN-2024-001 is expected today',
        action: 'prepare_receiving'
      }
    ];
  }

  private async getRecentActivity(filters?: any): Promise<any[]> {
    // Mock activity
    return [
      {
        type: 'receiving',
        description: 'ASN-2024-001 received with 500 items',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
        user: 'john.doe'
      },
      {
        type: 'picking',
        description: 'Order ORD-2024-001 picked and packed',
        timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000),
        user: 'jane.smith'
      }
    ];
  }

  private async getPerformanceMetrics(filters?: any): Promise<any> {
    return {
      receivingAccuracy: 98.5,
      pickingAccuracy: 97.2,
      inventoryAccuracy: 99.1,
      throughput: 1250
    };
  }
}