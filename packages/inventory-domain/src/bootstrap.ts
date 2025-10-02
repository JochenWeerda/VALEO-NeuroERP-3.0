/**
 * VALEO NeuroERP 3.0 - Inventory Domain Bootstrap
 *
 * Domain initialization and dependency injection setup for WMS operations
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
import { ReceivingService } from './services/receiving-service';
import { PutawaySlottingService } from './services/putaway-slotting-service';
import { EventBusFactory, EventBusType } from './infrastructure/event-bus/event-bus';
import { InventoryMetricsService } from './infrastructure/observability/metrics-service';

// ===== CONFIGURATION =====

interface InventoryConfig {
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
  wms: {
    defaultDockCount: number;
    defaultZoneCount: number;
    enableGs1Compliance: boolean;
    enableEpcisTracking: boolean;
  };
}

// ===== DATABASE CONNECTION =====

export class PostgresConnection {
  private readonly pool: any; // Would be pg.Pool in real implementation

  constructor(private readonly config: InventoryConfig['database']) {
    this.initializeConnection();
  }

  private initializeConnection(): void {
    // PostgreSQL connection pool setup would go here
    console.log('[INVENTORY DB] PostgreSQL connection initialized');
  }

  async query<T = any>(query: string, _params?: any[]): Promise<{ rows: T[]; rowCount: number }> {
    // Database query implementation would go here
    console.log(`[INVENTORY DB] Executing query: ${query.substring(0, 100)}...`);
    return { rows: [], rowCount: 0 };
  }

  async transaction<T>(callback: (client: any) => Promise<T>): Promise<T> {
    // Transaction implementation would go here
    console.log('[INVENTORY DB] Starting transaction');
    return await callback(this);
  }

  async close(): Promise<void> {
    // Connection cleanup would go here
    console.log('[INVENTORY DB] Connection closed');
  }
}

// ===== DOMAIN BOOTSTRAP =====

export class InventoryDomainBootstrap {
  private app?: express.Application;
  private readonly config: InventoryConfig;
  private db?: PostgresConnection;
  private eventBus?: any;
  private metricsService?: InventoryMetricsService;

  constructor(config: InventoryConfig) {
    this.config = config;
  }

  /**
   * Initialize the inventory domain
   */
  async initialize(): Promise<express.Application> {
    console.log('[INVENTORY BOOTSTRAP] Initializing Inventory Domain...');

    try {
      // 1. Initialize database connection
      await this.initializeDatabase();

      // 2. Initialize event-driven architecture
      await this.initializeEventBus();

      // 3. Initialize observability
      await this.initializeObservability();

      // 4. Initialize services
      await this.initializeServices();

      // 5. Initialize API
      await this.initializeAPI();

      console.log('[INVENTORY BOOTSTRAP] ✅ Inventory Domain initialized successfully');
      return this.app!;
    } catch (error) {
      console.error('[INVENTORY BOOTSTRAP] ❌ Initialization failed:', error);
      throw error;
    }
  }

  /**
   * Initialize database connection
   */
  private async initializeDatabase(): Promise<void> {
    this.db = new PostgresConnection(this.config.database);
    console.log('[INVENTORY BOOTSTRAP] Database connection established');
  }

  /**
   * Initialize event-driven architecture
   */
  private async initializeEventBus(): Promise<void> {
    const eventBusType = (process.env.EVENT_BUS_TYPE as EventBusType) || 'in-memory';
    this.eventBus = EventBusFactory.create(eventBusType);
    await this.eventBus.start();
    console.log(`[INVENTORY BOOTSTRAP] Event bus initialized: ${eventBusType}`);
  }

  /**
   * Initialize observability infrastructure
   */
  private async initializeObservability(): Promise<void> {
    this.metricsService = new InventoryMetricsService();
    console.log('[INVENTORY BOOTSTRAP] Observability initialized');
  }

  /**
   * Initialize domain services
   */
  private async initializeServices(): Promise<void> {
    if (this.db === undefined || this.eventBus === undefined || this.metricsService === undefined) {
      throw new Error('Database, event bus, and metrics must be initialized first');
    }

    // Initialize services
    const receivingService = new ReceivingService(this.eventBus);
    const putawayService = new PutawaySlottingService(this.eventBus);

    // Register services in DI container
    this.registerServices(receivingService, putawayService);

    console.log('[INVENTORY BOOTSTRAP] Domain services initialized');
  }

  /**
   * Register services in DI container
   */
  private registerServices(receivingService: ReceivingService, putawaySlottingService: PutawaySlottingService): void {
    // Register services
    DIContainer.register('ReceivingService', receivingService, { singleton: true });
    DIContainer.register('PutawaySlottingService', putawaySlottingService, { singleton: true });
    DIContainer.register('EventBus', this.eventBus, { singleton: true });
    DIContainer.register('MetricsService', this.metricsService, { singleton: true });
    DIContainer.register('Database', this.db, { singleton: true });

    console.log('[INVENTORY BOOTSTRAP] Services registered in DI container');
  }

  /**
   * Initialize API layer
   */
  private async initializeAPI(): Promise<void> {
    // Get services from DI container
    const receivingService = DIContainer.resolve<ReceivingService>('ReceivingService');

    // Create Express app
    this.app = express();

    // Middleware
    this.app.use(helmet());
    this.app.use(cors());
    this.app.use(compression());
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));

    // API routes
    this.app.post('/api/receiving/asn', async (req, res) => {
      try {
        const asn = await receivingService.processASN(req.body);
        res.json(asn);
      } catch (error) {
        res.status(500).json({ error: (error as Error).message });
      }
    });

    this.app.post('/api/receiving/start', async (req, res) => {
      try {
        const appointment = await receivingService.startReceiving(
          req.body.asnId,
          req.body.dock,
          req.body.carrierInfo
        );
        res.json(appointment);
      } catch (error) {
        res.status(500).json({ error: (error as Error).message });
      }
    });

    this.app.post('/api/receiving/goods', async (req, res) => {
      try {
        const result = await receivingService.receiveGoods(
          req.body.asnId,
          req.body.receivedLines
        );
        res.json(result);
      } catch (error) {
        res.status(500).json({ error: (error as Error).message });
      }
    });

    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        service: 'inventory-domain',
        timestamp: new Date().toISOString(),
        version: '3.0.0',
        wms: {
          gs1Enabled: this.config.wms.enableGs1Compliance,
          epcisEnabled: this.config.wms.enableEpcisTracking
        }
      });
    });

    // Metrics endpoint
    this.app.get('/metrics', async (req, res) => {
      try {
        const metrics = this.metricsService!.getMetrics();
        res.set('Content-Type', 'text/plain; charset=utf-8');
        res.send(metrics);
      } catch (error) {
        res.status(500).json({ error: (error as Error).message });
      }
    });

    console.log('[INVENTORY BOOTSTRAP] API layer initialized');
  }

  /**
   * Start the inventory domain server
   */
  async start(): Promise<void> {
    if (this.app === undefined) {
      throw new Error('Domain must be initialized before starting');
    }

    const port = this.config.server.port;

    return new Promise((resolve) => {
      this.app!.listen(port, () => {
        console.log(`[INVENTORY SERVER] 🚀 Inventory Domain running on port ${port}`);
        console.log(`[INVENTORY SERVER] Environment: ${this.config.server.environment}`);
        console.log(`[INVENTORY SERVER] GS1 Compliance: ${this.config.wms.enableGs1Compliance}`);
        console.log(`[INVENTORY SERVER] EPCIS Tracking: ${this.config.wms.enableEpcisTracking}`);
        console.log(`[INVENTORY SERVER] Health check: http://localhost:${port}/health`);
        console.log(`[INVENTORY SERVER] Metrics: http://localhost:${port}/metrics`);
        resolve();
      });
    });
  }

  /**
   * Graceful shutdown
   */
  async shutdown(): Promise<void> {
    console.log('[INVENTORY BOOTSTRAP] Shutting down Inventory Domain...');

    if (this.eventBus !== undefined) {
      await this.eventBus.stop();
    }

    if (this.db !== undefined) {
      await this.db.close();
    }

    console.log('[INVENTORY BOOTSTRAP] ✅ Shutdown complete');
  }
}

// ===== FACTORY FUNCTION =====

export function createInventoryDomain(config: InventoryConfig): InventoryDomainBootstrap {
  return new InventoryDomainBootstrap(config);
}

// ===== DEFAULT CONFIGURATION =====

export function getDefaultInventoryConfig(): InventoryConfig {
  return {
    database: {
      host: process.env.DB_HOST ?? 'localhost',
      port: parseInt(process.env.DB_PORT ?? '5436'),
      database: process.env.DB_NAME ?? 'neuroerp_inventory',
      user: process.env.DB_USER ?? 'neuroerp',
      password: process.env.DB_PASSWORD ?? 'password'
    },
    messaging: {
      type: (process.env.MESSAGING_TYPE as any) ?? 'KAFKA',
      connectionString: process.env.MESSAGING_URL ?? 'localhost:9092'
    },
    server: {
      port: parseInt(process.env.INVENTORY_PORT ?? '3002'),
      environment: process.env.NODE_ENV ?? 'development'
    },
    wms: {
      defaultDockCount: parseInt(process.env.DEFAULT_DOCK_COUNT ?? '4'),
      defaultZoneCount: parseInt(process.env.DEFAULT_ZONE_COUNT ?? '6'),
      enableGs1Compliance: process.env.ENABLE_GS1 === 'true',
      enableEpcisTracking: process.env.ENABLE_EPCIS === 'true'
    }
  };
}

// ===== MAIN ENTRY POINT =====

export async function bootstrapInventoryDomain(): Promise<InventoryDomainBootstrap> {
  const config = getDefaultInventoryConfig();
  const domain = createInventoryDomain(config);

  await domain.initialize();

  return domain;
}

// ===== CLI RUNNER =====

if (require.main === module) {
  bootstrapInventoryDomain()
    .then(async (domain) => {
      await domain.start();

      // Graceful shutdown handling
      process.on('SIGTERM', async () => {
        console.log('[INVENTORY DOMAIN] SIGTERM received, shutting down gracefully');
        await domain.shutdown();
        process.exit(0);
      });

      process.on('SIGINT', async () => {
        console.log('[INVENTORY DOMAIN] SIGINT received, shutting down gracefully');
        await domain.shutdown();
        process.exit(0);
      });
    })
    .catch((error) => {
      console.error('[INVENTORY DOMAIN] Failed to start:', error);
      process.exit(1);
    });
}