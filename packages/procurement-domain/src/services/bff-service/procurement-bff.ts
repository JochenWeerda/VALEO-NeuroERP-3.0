/**
 * VALEO NeuroERP 3.0 - Procurement BFF Service
 *
 * Backend for Frontend (BFF) service providing:
 * - Aggregated dashboard data from all procurement services
 * - Conversational AI for procurement tasks
 * - Unified API for frontend applications
 * - Real-time notifications and workflow orchestration
 */

import express, { Request, Response } from 'express';
// import cors from 'cors';
import helmet from 'helmet';
import { injectable } from 'inversify';

export interface ProcurementDashboardData {
  overview: {
    totalSpend: number;
    activePOs: number;
    pendingRequisitions: number;
    supplierCount: number;
    contractCount: number;
    riskAlerts: number;
  };
  spendAnalytics: {
    byCategory: Array<{ category: string; amount: number; percentage: number }>;
    bySupplier: Array<{ supplier: string; amount: number; percentage: number }>;
  };
  alerts: Array<{
    id: string;
    type: 'warning' | 'error' | 'info';
    title: string;
    message: string;
    priority: 'low' | 'medium' | 'high' | 'critical';
  }>;
  recommendations: Array<{
    id: string;
    type: string;
    title: string;
    description: string;
    impact: string;
    confidence: number;
  }>;
}

export interface ConversationalRequest {
  message: string;
  context?: {
    userId: string;
    department: string;
    role: string;
  };
  sessionId?: string;
}

export interface ConversationalResponse {
  response: string;
  actions: Array<{
    type: string;
    label: string;
    data: any;
    confidence: number;
  }>;
  suggestions: string[];
  sessionId: string;
}

@injectable()
export class ProcurementBFFService {
  private app: express.Application;
  private readonly port: number;

  constructor() {
    this.app = express();
    this.port = parseInt(process.env.PROCUREMENT_BFF_PORT || '3003');
    this.setupMiddleware();
    this.setupRoutes();
  }

  private setupMiddleware(): void {
    this.app.use(helmet());
    // this.app.use(cors());
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));

    // Request logging
    this.app.use((req: Request, res: Response, next: any) => {
      console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
      next();
    });
  }

  private setupRoutes(): void {
    // Health check
    this.app.get('/health', (req: Request, res: Response) => {
      res.json({
        status: 'healthy',
        service: 'procurement-bff',
        timestamp: new Date().toISOString(),
        version: '3.0.0'
      });
    });

    // Dashboard data aggregation
    this.app.get('/api/dashboard', this.handleDashboard.bind(this));

    // Conversational AI
    this.app.post('/api/chat', this.handleChat.bind(this));

    // Unified search
    this.app.get('/api/search', this.handleSearch.bind(this));

    // Workflow orchestration
    this.app.post('/api/workflows/requisition-to-po', this.handleRequisitionToPO.bind(this));

    // Real-time notifications
    this.app.get('/api/notifications', this.handleNotifications.bind(this));

    // Bulk operations
    this.app.post('/api/bulk/approve-requisitions', this.handleBulkApprove.bind(this));

    // Analytics & reporting
    this.app.get('/api/analytics/spend', this.handleSpendAnalytics.bind(this));

    // Supplier CRUD
    this.app.get('/api/v1/crm/suppliers', this.handleListSuppliers.bind(this));
    this.app.get('/api/v1/crm/suppliers/:id', this.handleGetSupplier.bind(this));
    this.app.post('/api/v1/crm/suppliers', this.handleCreateSupplier.bind(this));
    this.app.put('/api/v1/crm/suppliers/:id', this.handleUpdateSupplier.bind(this));
  }

  // ===== DASHBOARD ENDPOINTS =====

  private async handleDashboard(req: Request, res: Response): Promise<void> {
    try {
      const dashboardData: ProcurementDashboardData = {
        overview: {
          totalSpend: 2500000,
          activePOs: 45,
          pendingRequisitions: 12,
          supplierCount: 89,
          contractCount: 67,
          riskAlerts: 3
        },
        spendAnalytics: {
          byCategory: [
            { category: 'IT Hardware', amount: 850000, percentage: 34 },
            { category: 'Professional Services', amount: 620000, percentage: 25 },
            { category: 'Office Supplies', amount: 380000, percentage: 15 },
            { category: 'Facilities', amount: 350000, percentage: 14 },
            { category: 'Other', amount: 300000, percentage: 12 }
          ],
          bySupplier: [
            { supplier: 'Dell Technologies', amount: 450000, percentage: 18 },
            { supplier: 'Microsoft', amount: 380000, percentage: 15 },
            { supplier: 'SAP', amount: 320000, percentage: 13 },
            { supplier: 'Accenture', amount: 280000, percentage: 11 },
            { supplier: 'AWS', amount: 250000, percentage: 10 }
          ]
        },
        alerts: [
          {
            id: 'alert_1',
            type: 'error',
            title: 'High-Risk Supplier',
            message: 'Supplier ABC Corp has critical risk score',
            priority: 'critical'
          },
          {
            id: 'alert_2',
            type: 'warning',
            title: 'Contract Expiring',
            message: 'IT Services contract expires in 30 days',
            priority: 'high'
          },
          {
            id: 'alert_3',
            type: 'info',
            title: 'New Recommendations Available',
            message: 'AI has generated 5 new procurement recommendations',
            priority: 'medium'
          }
        ],
        recommendations: [
          {
            id: 'rec_1',
            type: 'supplier',
            title: 'Consolidate IT Suppliers',
            description: 'Reduce from 12 to 8 IT suppliers to improve negotiation leverage',
            impact: '€150,000 annual savings',
            confidence: 85
          },
          {
            id: 'rec_2',
            type: 'contract',
            title: 'Renew Facilities Contract',
            description: 'Current contract expires in 45 days with favorable terms',
            impact: '€75,000 cost avoidance',
            confidence: 92
          },
          {
            id: 'rec_3',
            type: 'spend',
            title: 'Optimize Office Supplies',
            description: 'Switch to preferred supplier for 20% cost reduction',
            impact: '€45,000 annual savings',
            confidence: 78
          }
        ]
      };

      res.json(dashboardData);
    } catch (error) {
      console.error('Dashboard error:', error);
      res.status(500).json({ error: 'Failed to load dashboard' });
    }
  }

  // ===== CONVERSATIONAL AI ENDPOINTS =====

  private async handleChat(req: Request, res: Response): Promise<void> {
    try {
      const request: ConversationalRequest = req.body;

      const response: ConversationalResponse = {
        response: `I understand you want to: "${request.message}". How can I help you with your procurement needs?`,
        actions: [
          {
            type: 'create_requisition',
            label: 'Create New Requisition',
            data: { department: request.context?.department },
            confidence: 0.8
          },
          {
            type: 'search_suppliers',
            label: 'Find Suppliers',
            data: { query: request.message },
            confidence: 0.7
          },
          {
            type: 'view_reports',
            label: 'View Reports',
            data: { type: 'spend' },
            confidence: 0.6
          }
        ],
        suggestions: [
          'Create a purchase requisition',
          'Search for suppliers',
          'Check approval status',
          'Generate spend report'
        ],
        sessionId: `session_${Date.now()}`
      };

      res.json(response);
    } catch (error) {
      console.error('Chat error:', error);
      res.status(500).json({ error: 'Chat processing failed' });
    }
  }

  // ===== OTHER ENDPOINTS =====

  private async handleSearch(req: Request, res: Response): Promise<void> {
    try {
      const results = {
        suppliers: [
          { id: 'sup_1', name: 'Dell Technologies', category: 'IT Hardware' },
          { id: 'sup_2', name: 'Microsoft', category: 'Software' }
        ],
        products: [
          { id: 'prod_1', name: 'Dell XPS 15', category: 'Laptop' },
          { id: 'prod_2', name: 'Office 365 License', category: 'Software' }
        ],
        contracts: [
          { id: 'cont_1', title: 'IT Hardware Supply Agreement', supplier: 'Dell Technologies' }
        ]
      };

      res.json(results);
    } catch (error) {
      console.error('Search error:', error);
      res.status(500).json({ error: 'Search failed' });
    }
  }

  private async handleRequisitionToPO(req: Request, res: Response): Promise<void> {
    try {
      const { requisitionId } = req.body;

      const result = {
        requisitionId,
        poId: `PO_${Date.now()}`,
        status: 'completed',
        message: 'Requisition successfully converted to Purchase Order',
        nextSteps: ['Monitor delivery', 'Process goods receipt']
      };

      res.json(result);
    } catch (error) {
      console.error('Workflow error:', error);
      res.status(500).json({ error: 'Workflow orchestration failed' });
    }
  }

  private async handleNotifications(req: Request, res: Response): Promise<void> {
    try {
      const notifications = [
        {
          id: 'notif_1',
          type: 'approval',
          title: 'Requisition Approved',
          message: 'Your IT hardware requisition has been approved',
          timestamp: new Date(),
          read: false
        },
        {
          id: 'notif_2',
          type: 'alert',
          title: 'Contract Expiring',
          message: 'Office supplies contract expires in 15 days',
          timestamp: new Date(),
          read: false
        }
      ];

      res.json(notifications);
    } catch (error) {
      console.error('Notifications error:', error);
      res.status(500).json({ error: 'Failed to fetch notifications' });
    }
  }

  private async handleBulkApprove(req: Request, res: Response): Promise<void> {
    try {
      const { requisitionIds } = req.body;

      const results = requisitionIds.map((id: string) => ({
        requisitionId: id,
        status: 'approved',
        approvedBy: 'system',
        timestamp: new Date()
      }));

      res.json({
        results,
        summary: `${results.length} requisitions approved successfully`
      });
    } catch (error) {
      console.error('Bulk approve error:', error);
      res.status(500).json({ error: 'Bulk approval failed' });
    }
  }

  private async handleSpendAnalytics(req: Request, res: Response): Promise<void> {
    try {
      const analytics = {
        totalSpend: 2500000,
        period: '2024',
        byCategory: [
          { category: 'IT Hardware', amount: 850000, change: 5.2 },
          { category: 'Professional Services', amount: 620000, change: -2.1 },
          { category: 'Office Supplies', amount: 380000, change: 8.7 }
        ],
        bySupplier: [
          { supplier: 'Dell Technologies', amount: 450000, change: 12.3 },
          { supplier: 'Microsoft', amount: 380000, change: -5.4 }
        ],
        trends: [
          { month: 'Jan', spend: 180000 },
          { month: 'Feb', spend: 195000 },
          { month: 'Mar', spend: 210000 }
        ]
      };

      res.json(analytics);
    } catch (error) {
      console.error('Analytics error:', error);
      res.status(500).json({ error: 'Failed to fetch analytics' });
    }
  }

  // ===== SUPPLIER ENDPOINTS =====

  // In-memory store (TODO: connect to real DB/repository)
  private suppliers = [
    { id: 'sup_1', name: 'Saatgut AG', supplier_number: 'LF-001', type: 'Saatgut', city: 'Südhausen', email: 'info@saatgut-ag.de', phone: '+49 123 456789', tax_id: 'DE123456789', rating: 4.5, is_active: true, payment_terms: 30, created_at: '2025-01-15T10:00:00Z' },
    { id: 'sup_2', name: 'Dünger GmbH', supplier_number: 'LF-002', type: 'Düngemittel', city: 'Nordhausen', email: 'kontakt@duenger-gmbh.de', phone: '+49 234 567890', tax_id: 'DE234567890', rating: 4.2, is_active: true, payment_terms: 14, created_at: '2025-02-01T08:30:00Z' },
    { id: 'sup_3', name: 'Technik GmbH', supplier_number: 'LF-003', type: 'Landtechnik', city: 'Osthausen', email: 'info@technik-gmbh.de', phone: '+49 345 678901', tax_id: 'DE345678901', rating: 3.8, is_active: true, payment_terms: 45, created_at: '2025-03-10T14:00:00Z' },
    { id: 'sup_4', name: 'BioFeed KG', supplier_number: 'LF-004', type: 'Futtermittel', city: 'Westhausen', email: 'vertrieb@biofeed.de', phone: '+49 456 789012', tax_id: 'DE456789012', rating: 4.0, is_active: true, payment_terms: 30, created_at: '2025-04-05T11:00:00Z' },
    { id: 'sup_5', name: 'AgroChem AG', supplier_number: 'LF-005', type: 'Pflanzenschutz', city: 'Mittelhausen', email: 'info@agrochem.de', phone: '+49 567 890123', tax_id: 'DE567890123', rating: 3.5, is_active: false, payment_terms: 60, created_at: '2025-05-20T09:00:00Z' },
  ];

  private async handleListSuppliers(req: Request, res: Response): Promise<void> {
    try {
      const { search, is_active } = req.query;
      let result = [...this.suppliers];

      if (search) {
        const s = String(search).toLowerCase();
        result = result.filter(
          (sup) =>
            sup.name.toLowerCase().includes(s) ||
            sup.type.toLowerCase().includes(s) ||
            sup.city.toLowerCase().includes(s) ||
            sup.supplier_number.toLowerCase().includes(s),
        );
      }

      if (is_active !== undefined) {
        const active = is_active === 'true';
        result = result.filter((sup) => sup.is_active === active);
      }

      res.json({ items: result, total: result.length });
    } catch (error) {
      console.error('List suppliers error:', error);
      res.status(500).json({ error: 'Failed to list suppliers' });
    }
  }

  private async handleGetSupplier(req: Request, res: Response): Promise<void> {
    try {
      const supplier = this.suppliers.find((s) => s.id === req.params.id);
      if (!supplier) {
        res.status(404).json({ error: 'Supplier not found' });
        return;
      }
      res.json(supplier);
    } catch (error) {
      console.error('Get supplier error:', error);
      res.status(500).json({ error: 'Failed to get supplier' });
    }
  }

  private async handleCreateSupplier(req: Request, res: Response): Promise<void> {
    try {
      const newSupplier = {
        id: `sup_${Date.now()}`,
        ...req.body,
        supplier_number: `LF-${String(this.suppliers.length + 1).padStart(3, '0')}`,
        created_at: new Date().toISOString(),
      };
      this.suppliers.push(newSupplier);
      res.status(201).json(newSupplier);
    } catch (error) {
      console.error('Create supplier error:', error);
      res.status(500).json({ error: 'Failed to create supplier' });
    }
  }

  private async handleUpdateSupplier(req: Request, res: Response): Promise<void> {
    try {
      const idx = this.suppliers.findIndex((s) => s.id === req.params.id);
      if (idx === -1) {
        res.status(404).json({ error: 'Supplier not found' });
        return;
      }
      this.suppliers[idx] = { ...this.suppliers[idx], ...req.body };
      res.json(this.suppliers[idx]);
    } catch (error) {
      console.error('Update supplier error:', error);
      res.status(500).json({ error: 'Failed to update supplier' });
    }
  }

  // ===== LIFECYCLE METHODS =====

  public async start(): Promise<void> {
    return new Promise((resolve) => {
      this.app.listen(this.port, () => {
        console.log(`[PROCUREMENT BFF] 🚀 Procurement BFF running on port ${this.port}`);
        console.log(`[PROCUREMENT BFF] Environment: ${process.env.NODE_ENV || 'development'}`);
        console.log(`[PROCUREMENT BFF] Health check: http://localhost:${this.port}/health`);
        resolve();
      });
    });
  }

  public async stop(): Promise<void> {
    console.log('[PROCUREMENT BFF] Shutting down Procurement BFF...');
    console.log('[PROCUREMENT BFF] ✅ Shutdown complete');
  }

  public getApp(): express.Application {
    return this.app;
  }
}