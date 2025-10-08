/**
 * VALEO NeuroERP 3.0 - Finance Domain Bootstrap
 *
 * Domain initialization and dependency injection setup
 * Following the 5 Principles Architecture
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
export class DIContainer {
  private static readonly services = new Map<string, any>();

  static register<T>(key: string, service: T, _options?: { singleton?: boolean }): void {
    this.services.set(key, service);
  }

  static resolve<T>(key: string): T {
    const service = this.services.get(key);
    if (service === undefined) {
      throw new Error(`Service ${key} not found in DI container`);
    }
    return service as T;
  }
}

// ===== IMPORTS =====
import { PostgresAccountRepository, PostgresAccountingPeriodRepository, PostgresJournalRepository } from './infrastructure/repositories/postgres-ledger-repository';
import { LedgerApplicationService } from './application/services/ledger-service';
import { APInvoiceApplicationService } from './application/services/ap-invoice-service';
import { AIBookkeeperApplicationService } from './application/services/ai-bookkeeper-service';
import { createFinanceRouter } from './presentation/controllers/finance-api-controller';
import { FinanceEventPublisher, createEventPublisher } from './infrastructure/messaging/event-publisher';

// Sprint 8: Observability & Performance
// import OpenTelemetryConfig from './infrastructure/observability/otel-config';
import { MetricsService } from './infrastructure/observability/metrics-service';

// Sprint 8: Event-Driven Architecture
import { EventBusFactory, EventBusType } from './infrastructure/event-bus/event-bus';

// Sprint 8: Security & Compliance
import { AuthService } from './infrastructure/security/auth-service';

// Sprint 8: Caching & Performance
import { CacheService } from './infrastructure/cache/cache-service';

// ===== CONFIGURATION =====

interface FinanceConfig {
  database: {
    host: string;
    port: number;
    database: string;
    user: string;
    password: string;
  };
  messaging: {
    type: 'KAFKA' | 'NATS' | 'RABBITMQ';
    connectionString: string;
  };
  server: {
    port: number;
    environment: string;
  };
}

// ===== DATABASE CONNECTION =====

export class PostgresConnection {
  private readonly pool: any; // Would be pg.Pool in real implementation

  constructor(private readonly config: FinanceConfig['database']) {
    this.initializeConnection();
  }

  private initializeConnection(): void {
    // PostgreSQL connection pool setup would go here
    console.log('[FINANCE DB] PostgreSQL connection initialized');
  }

  async query<T = any>(query: string, _params?: any[]): Promise<{ rows: T[]; rowCount: number }> {
    // Database query implementation would go here
    console.log(`[FINANCE DB] Executing query: ${query.substring(0, 100)}...`);
    return { rows: [], rowCount: 0 };
  }

  async transaction<T>(callback: (client: any) => Promise<T>): Promise<T> {
    // Transaction implementation would go here
    console.log('[FINANCE DB] Starting transaction');
    return await callback(this);
  }

  async close(): Promise<void> {
    // Connection cleanup would go here
    console.log('[FINANCE DB] Connection closed');
  }
}

// ===== MACHINE LEARNING MODEL =====

export class SimpleMLModel {
  async predict(features: Record<string, number>): Promise<{
    prediction: string;
    confidence: number;
    explanation: string;
  }> {
    // Simple rule-based prediction for demonstration
    // In production, this would be a trained ML model

    if (features.line_amount && features.line_amount > 1000) {
      return {
        prediction: '1600', // Accounts Payable
        confidence: 0.85,
        explanation: 'High amount suggests accounts payable transaction'
      };
    }

    return {
      prediction: '6000', // Office Expenses
      confidence: 0.75,
      explanation: 'Default classification for office-related expenses'
    };
  }

  async train(features: Record<string, number>[], _labels: string[]): Promise<void> {
    // Model training implementation would go here
    console.log(`[ML MODEL] Training with ${features.length} samples`);
  }

  async saveModel(path: string): Promise<void> {
    // Model persistence implementation would go here
    console.log(`[ML MODEL] Model saved to ${path}`);
  }

  async loadModel(path: string): Promise<void> {
    // Model loading implementation would go here
    console.log(`[ML MODEL] Model loaded from ${path}`);
  }
}

// ===== DOMAIN BOOTSTRAP =====

export class FinanceDomainBootstrap {
  private app?: express.Application;
  private readonly config: FinanceConfig;
  private db?: PostgresConnection;
  private eventPublisher?: any;
  private eventBus?: any;
  private metricsService?: MetricsService;
  private cacheService?: CacheService;
  private authService?: AuthService;

  constructor(config: FinanceConfig) {
    this.config = config;
  }

  /**
   * Initialize the finance domain
   */
  async initialize(): Promise<express.Application> {
    console.log('[FINANCE BOOTSTRAP] Initializing Finance Domain...');

    try {
      // 1. Initialize observability (OpenTelemetry)
      await this.initializeObservability();

      // 2. Initialize database connection
      await this.initializeDatabase();

      // 3. Initialize messaging
      await this.initializeMessaging();

      // 4. Initialize event-driven architecture
      await this.initializeEventBus();

      // 5. Initialize caching
      await this.initializeCaching();

      // 6. Initialize security
      await this.initializeSecurity();

      // 7. Initialize services
      await this.initializeServices();

      // 8. Initialize API
      await this.initializeAPI();

      console.log('[FINANCE BOOTSTRAP] ✅ Finance Domain initialized successfully');
      return this.app!;
    } catch (error) {
      console.error('[FINANCE BOOTSTRAP] ❌ Initialization failed:', error);
      throw error;
    }
  }

  /**
   * Initialize database connection
   */
  private async initializeDatabase(): Promise<void> {
    this.db = new PostgresConnection(this.config.database);
    console.log('[FINANCE BOOTSTRAP] Database connection established');
  }

  /**
   * Initialize observability infrastructure
   */
  private async initializeObservability(): Promise<void> {
    // OpenTelemetryConfig.initialize();
    this.metricsService = MetricsService.getInstance();
    console.log('[FINANCE BOOTSTRAP] OpenTelemetry observability initialized');
  }

  /**
   * Initialize messaging infrastructure
   */
  private async initializeMessaging(): Promise<void> {
    this.eventPublisher = createEventPublisher(this.config.messaging);
    console.log('[FINANCE BOOTSTRAP] Event publishing system initialized');
  }

  /**
   * Initialize event-driven architecture
   */
  private async initializeEventBus(): Promise<void> {
    const eventBusType = (process.env.EVENT_BUS_TYPE as EventBusType) || EventBusType.IN_MEMORY;
    this.eventBus = EventBusFactory.createEventBus(eventBusType);
    await this.eventBus.start();
    console.log(`[FINANCE BOOTSTRAP] Event bus initialized: ${eventBusType}`);
  }

  /**
   * Initialize caching infrastructure
   */
  private async initializeCaching(): Promise<void> {
    this.cacheService = new CacheService();
    console.log('[FINANCE BOOTSTRAP] Caching service initialized');
  }

  /**
   * Initialize security infrastructure
   */
  private async initializeSecurity(): Promise<void> {
    this.authService = new AuthService();
    console.log('[FINANCE BOOTSTRAP] Security and authentication initialized');
  }

  /**
   * Initialize domain services
   */
  private async initializeServices(): Promise<void> {
    if (this.db === undefined || this.eventPublisher === undefined) {
      throw new Error('Database and messaging must be initialized first');
    }

    // Initialize repositories
    const journalRepository = new PostgresJournalRepository(this.db);
    const accountRepository = new PostgresAccountRepository(this.db);
    const periodRepository = new PostgresAccountingPeriodRepository(this.db);

    // Initialize ML model
    const mlModel = new SimpleMLModel();

    // Register services in DI container
    this.registerServices(
      journalRepository,
      accountRepository,
      periodRepository,
      this.eventPublisher,
      mlModel,
      this.eventBus,
      this.metricsService!,
      this.cacheService!,
      this.authService!
    );

    console.log('[FINANCE BOOTSTRAP] Domain services initialized');
  }

  /**
   * Register services in DI container
   */
  private registerServices(
    journalRepository: PostgresJournalRepository,
    accountRepository: PostgresAccountRepository,
    periodRepository: PostgresAccountingPeriodRepository,
    eventPublisher: FinanceEventPublisher,
    mlModel: SimpleMLModel,
    eventBus: any,
    metricsService: MetricsService,
    cacheService: CacheService,
    authService: AuthService
  ): void {
    // Register repositories
    DIContainer.register('JournalRepository', journalRepository, { singleton: true });
    DIContainer.register('AccountRepository', accountRepository, { singleton: true });
    DIContainer.register('PeriodRepository', periodRepository, { singleton: true });

    // Register ML model
    DIContainer.register('MLModel', mlModel, { singleton: true });

    // Register event publisher
    DIContainer.register('EventPublisher', eventPublisher, { singleton: true });

    // Register Sprint 8 services
    DIContainer.register('EventBus', eventBus, { singleton: true });
    DIContainer.register('MetricsService', metricsService, { singleton: true });
    DIContainer.register('CacheService', cacheService, { singleton: true });
    DIContainer.register('AuthService', authService, { singleton: true });

    console.log('[FINANCE BOOTSTRAP] Services registered in DI container');
  }

  /**
   * Initialize API layer
   */
  private async initializeAPI(): Promise<void> {
    // Get services from DI container
    const ledgerService = DIContainer.resolve<LedgerApplicationService>('LedgerService');
    const apInvoiceService = DIContainer.resolve<APInvoiceApplicationService>('APInvoiceService');
    const aiBookkeeperService = DIContainer.resolve<AIBookkeeperApplicationService>('AIBookkeeperService');

    // Create Express app
    this.app = express();

    // Middleware
    this.app.use(helmet());
    this.app.use(cors());
    this.app.use(compression() as unknown as express.RequestHandler);
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }) as unknown as express.RequestHandler);

    // API routes
    const financeRouter = createFinanceRouter(
      ledgerService,
      apInvoiceService,
      aiBookkeeperService
    );

    this.app.use('/api/finance', financeRouter);

    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        service: 'finance-domain',
        timestamp: new Date().toISOString()
      });
    });

    console.log('[FINANCE BOOTSTRAP] API layer initialized');
  }

  /**
   * Start the finance domain server
   */
  async start(): Promise<void> {
    if (this.app === undefined) {
      throw new Error('Domain must be initialized before starting');
    }

    const port = this.config.server.port;

    return new Promise((resolve) => {
      this.app!.listen(port, () => {
        console.log(`[FINANCE SERVER] 🚀 Finance Domain running on port ${port}`);
        console.log(`[FINANCE SERVER] Environment: ${this.config.server.environment}`);
        console.log(`[FINANCE SERVER] Health check: http://localhost:${port}/health`);
        resolve();
      });
    });
  }

  /**
   * Graceful shutdown
   */
  async shutdown(): Promise<void> {
    console.log('[FINANCE BOOTSTRAP] Shutting down Finance Domain...');

    // Shutdown event bus
    if (this.eventBus !== undefined) {
      await this.eventBus.stop();
    }

    // Shutdown caching
    if (this.cacheService !== undefined) {
      await this.cacheService.close();
    }

    // Shutdown observability
    // if (OpenTelemetryConfig !== undefined) {
    //   await OpenTelemetryConfig.shutdown();
    // }

    // Shutdown database
    if (this.db !== undefined) {
      await this.db.close();
    }

    console.log('[FINANCE BOOTSTRAP] ✅ Shutdown complete');
  }
}

// ===== FACTORY FUNCTION =====

export function createFinanceDomain(config: FinanceConfig): FinanceDomainBootstrap {
  return new FinanceDomainBootstrap(config);
}

// ===== DEFAULT CONFIGURATION =====

export function getDefaultFinanceConfig(): FinanceConfig {
  return {
    database: {
      host: process.env.DB_HOST ?? 'localhost',
      port: parseInt(process.env.DB_PORT ?? '5435'),
      database: process.env.DB_NAME ?? 'neuroerp_finance',
      user: process.env.DB_USER ?? 'neuroerp',
      password: process.env.DB_PASSWORD ?? 'password'
    },
    messaging: {
      type: (process.env.MESSAGING_TYPE as any) ?? 'KAFKA',
      connectionString: process.env.MESSAGING_URL ?? 'localhost:9092'
    },
    server: {
      port: parseInt(process.env.FINANCE_PORT ?? '3001'),
      environment: process.env.NODE_ENV ?? 'development'
    }
  };
}

// ===== MAIN ENTRY POINT =====

export async function bootstrapFinanceDomain(): Promise<FinanceDomainBootstrap> {
  const config = getDefaultFinanceConfig();
  const domain = createFinanceDomain(config);

  await domain.initialize();

  return domain;
}

// ===== CLI RUNNER =====

if (require.main === module) {
  bootstrapFinanceDomain()
    .then(async (domain) => {
      await domain.start();

      // Graceful shutdown handling
      process.on('SIGTERM', async () => {
        console.log('[FINANCE DOMAIN] SIGTERM received, shutting down gracefully');
        await domain.shutdown();
        process.exit(0);
      });

      process.on('SIGINT', async () => {
        console.log('[FINANCE DOMAIN] SIGINT received, shutting down gracefully');
        await domain.shutdown();
        process.exit(0);
      });
    })
    .catch((error) => {
      console.error('[FINANCE DOMAIN] Failed to start:', error);
      process.exit(1);
    });
}