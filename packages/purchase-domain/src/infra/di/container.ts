/**
 * Dependency Injection Container
 * Enterprise-grade dependency management for Purchase Domain
 * Multi-tenant aware service resolution
 */

import { PurchaseOrderService } from '../../domain/services/purchase-order-service';
import { PurchaseOrderRepository } from '../repositories/purchase-order-repository';
import { ISMSAuditLogger } from '../../security/isms-audit-logger';
import { CryptoService } from '../../security/crypto-service';
import { TenantContext, TenantContextProvider } from './tenant-context';
import { PurchaseOrderEventPublisher, createPurchaseOrderEventPublisher } from '../messaging/event-publisher';
import { PurchaseOrderEventConsumer, createPurchaseOrderEventConsumer } from '../messaging/event-consumers';

export interface ServiceContainer {
  purchaseOrderService: PurchaseOrderService;
  purchaseOrderRepository: PurchaseOrderRepository;
  auditLogger: ISMSAuditLogger;
  cryptoService: CryptoService;
  tenantContextProvider: TenantContextProvider;
  eventPublisher: PurchaseOrderEventPublisher;
  eventConsumer: PurchaseOrderEventConsumer;
}

export class DIContainer {
  private static instance: DIContainer;
  private services: Map<string, any> = new Map();
  private tenantServices: Map<string, Map<string, any>> = new Map();

  private constructor() {}

  public static getInstance(): DIContainer {
    if (!DIContainer.instance) {
      DIContainer.instance = new DIContainer();
    }
    return DIContainer.instance;
  }

  /**
   * Registers a singleton service
   */
  public register<T>(key: string, factory: () => T): void {
    if (!this.services.has(key)) {
      this.services.set(key, factory());
    }
  }

  /**
   * Registers a tenant-specific service
   */
  public registerTenantService<T>(key: string, tenantId: string, factory: (tenantId: string) => T): void {
    if (!this.tenantServices.has(tenantId)) {
      this.tenantServices.set(tenantId, new Map());
    }
    
    const tenantContainer = this.tenantServices.get(tenantId)!;
    if (!tenantContainer.has(key)) {
      tenantContainer.set(key, factory(tenantId));
    }
  }

  /**
   * Resolves a singleton service
   */
  public resolve<T>(key: string): T {
    const service = this.services.get(key);
    if (!service) {
      throw new Error(`Service '${key}' not registered`);
    }
    return service;
  }

  /**
   * Resolves a tenant-specific service
   */
  public resolveTenantService<T>(key: string, tenantId: string): T {
    const tenantContainer = this.tenantServices.get(tenantId);
    if (!tenantContainer) {
      throw new Error(`No services registered for tenant '${tenantId}'`);
    }

    const service = tenantContainer.get(key);
    if (!service) {
      throw new Error(`Service '${key}' not registered for tenant '${tenantId}'`);
    }
    return service;
  }

  /**
   * Creates a complete service container for a tenant
   */
  public createTenantContainer(tenantId: string): ServiceContainer {
    // Ensure tenant-specific services are registered
    this.registerTenantServicesForTenant(tenantId);

    return {
      purchaseOrderService: this.resolveTenantService<PurchaseOrderService>('purchaseOrderService', tenantId),
      purchaseOrderRepository: this.resolveTenantService<PurchaseOrderRepository>('purchaseOrderRepository', tenantId),
      auditLogger: this.resolveTenantService<ISMSAuditLogger>('auditLogger', tenantId),
      cryptoService: this.resolve<CryptoService>('cryptoService'), // Crypto can be singleton
      tenantContextProvider: this.resolve<TenantContextProvider>('tenantContextProvider'),
      eventPublisher: this.resolveTenantService<PurchaseOrderEventPublisher>('eventPublisher', tenantId),
      eventConsumer: this.resolveTenantService<PurchaseOrderEventConsumer>('eventConsumer', tenantId)
    };
  }

  /**
   * Initializes all core singleton services
   */
  public initializeCoreServices(): void {
    // Crypto service is tenant-agnostic and can be singleton
    this.register('cryptoService', () => new CryptoService());

    // Tenant context provider
    this.register('tenantContextProvider', () => new TenantContextProvider());
  }

  /**
   * Registers tenant-specific services for a given tenant
   */
  private registerTenantServicesForTenant(tenantId: string): void {
    // Tenant-specific audit logger
    this.registerTenantService('auditLogger', tenantId, (tid) => 
      new ISMSAuditLogger(`purchase-service-${tid}`, 'production')
    );

    // Tenant-specific repository
    this.registerTenantService('purchaseOrderRepository', tenantId, (tid) => 
      new PurchaseOrderRepository(tid)
    );

    // Tenant-specific event publisher
    this.registerTenantService('eventPublisher', tenantId, (tid) =>
      createPurchaseOrderEventPublisher({ natsUrl: process.env.NATS_URL ?? 'nats://localhost:4222' })
    );

    // Tenant-specific event consumer
    this.registerTenantService('eventConsumer', tenantId, (tid) => {
      const purchaseOrderService = this.resolveTenantService<PurchaseOrderService>('purchaseOrderService', tid);
      return createPurchaseOrderEventConsumer({
        natsUrl: process.env.NATS_URL ?? 'nats://localhost:4222',
        documentServiceUrl: process.env.DOCUMENT_SERVICE_URL,
        notificationServiceUrl: process.env.NOTIFICATION_SERVICE_URL,
        inventoryServiceUrl: process.env.INVENTORY_SERVICE_URL,
        financeServiceUrl: process.env.FINANCE_SERVICE_URL,
        auditServiceUrl: process.env.AUDIT_SERVICE_URL
      }, purchaseOrderService);
    });

    // Tenant-specific service
    this.registerTenantService('purchaseOrderService', tenantId, (tid) => {
      const auditLogger = this.resolveTenantService<ISMSAuditLogger>('auditLogger', tid);
      const cryptoService = this.resolve<CryptoService>('cryptoService');
      const repository = this.resolveTenantService<PurchaseOrderRepository>('purchaseOrderRepository', tid);
      const eventPublisher = this.resolveTenantService<PurchaseOrderEventPublisher>('eventPublisher', tid);

      return new PurchaseOrderService({
        purchaseOrderRepo: repository,
        auditLogger,
        cryptoService,
        eventPublisher
      });
    });
  }

  /**
   * Clears all tenant-specific services (useful for testing)
   */
  public clearTenantServices(tenantId: string): void {
    this.tenantServices.delete(tenantId);
  }

  /**
   * Lists all registered tenants
   */
  public getRegisteredTenants(): string[] {
    return Array.from(this.tenantServices.keys());
  }

  /**
   * Health check for all services
   */
  public async healthCheck(): Promise<{ service: string; status: 'healthy' | 'unhealthy'; tenant?: string }[]> {
    const results: { service: string; status: 'healthy' | 'unhealthy'; tenant?: string }[] = [];

    // Check singleton services
    for (const [key] of Array.from(this.services)) {
      try {
        const service = this.resolve(key);
        results.push({
          service: key,
          status: service ? 'healthy' : 'unhealthy'
        });
      } catch (error) {
        results.push({ service: key, status: 'unhealthy' });
      }
    }

    // Check tenant services
    for (const [tenantId, tenantContainer] of Array.from(this.tenantServices)) {
      for (const [key] of Array.from(tenantContainer)) {
        try {
          const service = this.resolveTenantService(key, tenantId);
          results.push({
            service: key,
            status: service ? 'healthy' : 'unhealthy',
            tenant: tenantId
          });
        } catch (error) {
          results.push({ service: key, status: 'unhealthy', tenant: tenantId });
        }
      }
    }

    return results;
  }
}

// Export singleton instance
export const container = DIContainer.getInstance();
