/**
 * Enhanced Purchase Order Service
 * Step 3: Add markAsInvoiced method - Completes business workflow
 * Step 4: Enhance search - Improves usability
 */

import { randomUUID } from 'crypto';
import { PurchaseOrder, PurchaseOrderStatus, PurchaseOrderItem, CreatePurchaseOrderInput, UpdatePurchaseOrderInput } from '../entities/purchase-order';
import { ISMSAuditLogger } from '../../security/isms-audit-logger';
import { CryptoService } from '../../security/crypto-service';

export interface EnhancedPaginatedResult<T> {
  items: T[];
  totalCount: number;
  pageSize: number;
  currentPage: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface EnhancedPurchaseOrderFilter {
  status?: PurchaseOrderStatus;
  supplierId?: string;
  dateFrom?: Date;
  dateTo?: Date;
  minAmount?: number;
  maxAmount?: number;
  searchTerm?: string;
  contactPerson?: string;
  paymentTerms?: string;
  currency?: string;
  invoicedStatus?: 'INVOICED' | 'PENDING_INVOICE' | 'PARTIALLY_INVOICED';
}

export interface EnhancedPurchaseOrderSort {
  field: 'orderDate' | 'deliveryDate' | 'totalAmount' | 'purchaseOrderNumber' | 'createdAt' | 'updatedAt';
  direction: 'asc' | 'desc';
}

export interface InvoicingDetails {
  invoiceNumber: string;
  invoiceDate: Date;
  invoiceAmount: number;
  currency: string;
  dueDate: Date;
  paymentTerms: string;
  taxAmount?: number;
  discountAmount?: number;
  notes?: string;
}

export interface SearchResult<T> {
  items: T[];
  totalCount: number;
  searchTime: number;
  facets: SearchFacet[];
  suggestions: string[];
}

export interface SearchFacet {
  field: string;
  values: { value: string; count: number }[];
}

export class EnhancedPurchaseOrderService {
  constructor(
    private auditLogger: ISMSAuditLogger,
    private cryptoService: CryptoService
  ) {}

  /**
   * Enhanced list with better filtering and search capabilities
   */
  async listPurchaseOrders(
    filter: EnhancedPurchaseOrderFilter,
    sort: EnhancedPurchaseOrderSort,
    page: number,
    pageSize: number,
    tenantId: string
  ): Promise<EnhancedPaginatedResult<PurchaseOrder>> {
    try {
      const startTime = Date.now();

      // Mock implementation - enhanced with search capabilities
      let mockOrders: PurchaseOrder[] = [];
      
      // Apply filters
      if (filter.searchTerm) {
        mockOrders = this.performFullTextSearch(mockOrders, filter.searchTerm);
      }

      if (filter.status) {
        mockOrders = mockOrders.filter(order => order.status === filter.status);
      }

      if (filter.supplierId) {
        mockOrders = mockOrders.filter(order => order.supplierId === filter.supplierId);
      }

      if (filter.dateFrom || filter.dateTo) {
        mockOrders = this.filterByDateRange(mockOrders, filter.dateFrom, filter.dateTo);
      }

      if (filter.minAmount || filter.maxAmount) {
        mockOrders = this.filterByAmountRange(mockOrders, filter.minAmount, filter.maxAmount);
      }

      // Apply sorting
      mockOrders = this.applySorting(mockOrders, sort);

      // Apply pagination
      const totalCount = mockOrders.length;
      const totalPages = Math.ceil(totalCount / pageSize);
      const startIndex = (page - 1) * pageSize;
      const items = mockOrders.slice(startIndex, startIndex + pageSize);

      await this.auditLogger.logSecureEvent('ENHANCED_PURCHASE_ORDERS_LISTED', {
        filterApplied: Object.keys(filter).length > 0,
        resultCount: items.length,
        page,
        pageSize,
        searchTerm: filter.searchTerm ? '[REDACTED]' : undefined,
        searchTime: Date.now() - startTime
      }, tenantId);

      return {
        items,
        totalCount,
        pageSize,
        currentPage: page,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1
      };

    } catch (error) {
      await this.auditLogger.logSecurityIncident('ENHANCED_PURCHASE_ORDERS_LIST_FAILED', {
        error: (error as Error).message
      }, tenantId);
      throw error;
    }
  }

  /**
   * STEP 3: Mark purchase order as invoiced - Completes business workflow
   */
  async markAsInvoiced(
    purchaseOrderId: string,
    invoicingDetails: InvoicingDetails,
    userId: string,
    tenantId: string
  ): Promise<PurchaseOrder> {
    try {
      // Validate purchase order exists and is in correct status
      const purchaseOrder = await this.mockGetPurchaseOrder(purchaseOrderId, tenantId);
      if (!purchaseOrder) {
        throw new Error('Purchase order not found');
      }

      if (purchaseOrder.status !== PurchaseOrderStatus.GELIEFERT) {
        throw new Error('Purchase order must be delivered before it can be invoiced');
      }

      // Validate invoice details
      this.validateInvoicingDetails(invoicingDetails);

      // Create updated purchase order with invoicing information
      // In a real implementation, this would update the database
      const updatedOrder = new PurchaseOrder(
        purchaseOrder.supplierId,
        purchaseOrder.subject,
        purchaseOrder.description,
        purchaseOrder.deliveryDate,
        purchaseOrder.items,
        userId,
        {
          id: purchaseOrder.id,
          purchaseOrderNumber: purchaseOrder.purchaseOrderNumber,
          contactPerson: purchaseOrder.contactPerson,
          paymentTerms: invoicingDetails.paymentTerms,
          currency: invoicingDetails.currency,
          taxRate: purchaseOrder.taxRate,
          shippingAddress: purchaseOrder.shippingAddress,
          notes: purchaseOrder.notes + `\n\nINVOICED: ${invoicingDetails.invoiceNumber} on ${invoicingDetails.invoiceDate.toISOString()}`
        }
      );

      // Log the invoicing action
      await this.auditLogger.logSecureEvent('PURCHASE_ORDER_INVOICED', {
        purchaseOrderId,
        invoiceNumber: invoicingDetails.invoiceNumber,
        invoiceAmount: invoicingDetails.invoiceAmount,
        currency: invoicingDetails.currency,
        dueDate: invoicingDetails.dueDate.toISOString(),
        userId
      }, tenantId, userId);

      // Create financial integration event (would integrate with accounting system)
      await this.createFinancialEntry(purchaseOrder, invoicingDetails, tenantId);

      return updatedOrder;

    } catch (error) {
      await this.auditLogger.logSecurityIncident('PURCHASE_ORDER_INVOICING_FAILED', {
        purchaseOrderId,
        error: (error as Error).message,
        userId
      }, tenantId, userId);
      throw error;
    }
  }

  /**
   * STEP 4: Enhanced search functionality - Improves usability
   */
  async searchPurchaseOrders(
    searchTerm: string,
    filters: Partial<EnhancedPurchaseOrderFilter>,
    tenantId: string,
    options: {
      includeFacets?: boolean;
      includeSuggestions?: boolean;
      fuzzy?: boolean;
      limit?: number;
    } = {}
  ): Promise<SearchResult<PurchaseOrder>> {
    try {
      const startTime = Date.now();
      const { includeFacets = false, includeSuggestions = false, fuzzy = true, limit = 50 } = options;

      // Perform full-text search with advanced capabilities
      let results = await this.performAdvancedSearch(searchTerm, filters, tenantId, fuzzy);

      // Limit results
      results = results.slice(0, limit);

      // Generate facets if requested
      const facets = includeFacets ? await this.generateSearchFacets(results) : [];

      // Generate search suggestions if requested
      const suggestions = includeSuggestions ? await this.generateSearchSuggestions(searchTerm, tenantId) : [];

      const searchTime = Date.now() - startTime;

      await this.auditLogger.logSecureEvent('ADVANCED_PURCHASE_ORDER_SEARCH', {
        searchTerm: '[REDACTED]', // Don't log actual search terms for privacy
        resultsCount: results.length,
        searchTime,
        facetsGenerated: facets.length,
        suggestionsGenerated: suggestions.length,
        fuzzySearch: fuzzy
      }, tenantId);

      return {
        items: results,
        totalCount: results.length,
        searchTime,
        facets,
        suggestions
      };

    } catch (error) {
      await this.auditLogger.logSecurityIncident('ADVANCED_SEARCH_FAILED', {
        searchTerm: '[REDACTED]',
        error: (error as Error).message
      }, tenantId);
      throw error;
    }
  }

  /**
   * Get purchase order analytics and insights
   */
  async getPurchaseOrderAnalytics(
    tenantId: string,
    timeRange: { from: Date; to: Date }
  ): Promise<{
    totalOrders: number;
    totalValue: number;
    averageValue: number;
    statusBreakdown: Record<string, number>;
    supplierBreakdown: Record<string, { count: number; value: number }>;
    monthlyTrends: Array<{ month: string; count: number; value: number }>;
    invoicingStatus: {
      invoiced: number;
      pendingInvoice: number;
      partiallyInvoiced: number;
    };
  }> {
    try {
      // Mock analytics - in real implementation would query database
      const analytics = {
        totalOrders: 150,
        totalValue: 750000,
        averageValue: 5000,
        statusBreakdown: {
          [PurchaseOrderStatus.ENTWURF]: 25,
          [PurchaseOrderStatus.FREIGEGEBEN]: 40,
          [PurchaseOrderStatus.BESTELLT]: 35,
          [PurchaseOrderStatus.TEILGELIEFERT]: 20,
          [PurchaseOrderStatus.GELIEFERT]: 30
        },
        supplierBreakdown: {
          'supplier-001': { count: 45, value: 225000 },
          'supplier-002': { count: 35, value: 175000 },
          'supplier-003': { count: 70, value: 350000 }
        },
        monthlyTrends: [
          { month: '2025-01', count: 45, value: 225000 },
          { month: '2025-02', count: 52, value: 260000 },
          { month: '2025-03', count: 53, value: 265000 }
        ],
        invoicingStatus: {
          invoiced: 80,
          pendingInvoice: 50,
          partiallyInvoiced: 20
        }
      };

      await this.auditLogger.logSecureEvent('PURCHASE_ORDER_ANALYTICS_RETRIEVED', {
        timeRange: {
          from: timeRange.from.toISOString(),
          to: timeRange.to.toISOString()
        },
        totalOrders: analytics.totalOrders
      }, tenantId);

      return analytics;

    } catch (error) {
      await this.auditLogger.logSecurityIncident('ANALYTICS_RETRIEVAL_FAILED', {
        error: (error as Error).message
      }, tenantId);
      throw error;
    }
  }

  // Private helper methods for enhanced functionality

  private performFullTextSearch(orders: PurchaseOrder[], searchTerm: string): PurchaseOrder[] {
    const term = searchTerm.toLowerCase();
    return orders.filter(order => 
      order.subject.toLowerCase().includes(term) ||
      order.description.toLowerCase().includes(term) ||
      order.purchaseOrderNumber.toLowerCase().includes(term) ||
      order.supplierId.toLowerCase().includes(term) ||
      order.contactPerson?.toLowerCase().includes(term) ||
      order.notes?.toLowerCase().includes(term)
    );
  }

  private filterByDateRange(orders: PurchaseOrder[], from?: Date, to?: Date): PurchaseOrder[] {
    return orders.filter(order => {
      if (from && order.orderDate < from) return false;
      if (to && order.orderDate > to) return false;
      return true;
    });
  }

  private filterByAmountRange(orders: PurchaseOrder[], min?: number, max?: number): PurchaseOrder[] {
    return orders.filter(order => {
      if (min && order.totalAmount < min) return false;
      if (max && order.totalAmount > max) return false;
      return true;
    });
  }

  private applySorting(orders: PurchaseOrder[], sort: EnhancedPurchaseOrderSort): PurchaseOrder[] {
    return orders.sort((a, b) => {
      let comparison = 0;
      
      switch (sort.field) {
        case 'orderDate':
          comparison = a.orderDate.getTime() - b.orderDate.getTime();
          break;
        case 'deliveryDate':
          comparison = a.deliveryDate.getTime() - b.deliveryDate.getTime();
          break;
        case 'totalAmount':
          comparison = a.totalAmount - b.totalAmount;
          break;
        case 'purchaseOrderNumber':
          comparison = a.purchaseOrderNumber.localeCompare(b.purchaseOrderNumber);
          break;
        case 'createdAt':
          comparison = a.createdAt.getTime() - b.createdAt.getTime();
          break;
        case 'updatedAt':
          comparison = a.updatedAt.getTime() - b.updatedAt.getTime();
          break;
      }
      
      return sort.direction === 'desc' ? -comparison : comparison;
    });
  }

  private async performAdvancedSearch(
    searchTerm: string,
    filters: Partial<EnhancedPurchaseOrderFilter>,
    tenantId: string,
    fuzzy: boolean
  ): Promise<PurchaseOrder[]> {
    // Mock advanced search implementation
    // In real system would use Elasticsearch, Solr, or database full-text search
    const mockResults: PurchaseOrder[] = [];
    
    // Would implement fuzzy matching, stemming, synonyms, etc.
    if (fuzzy) {
      // Implement fuzzy matching logic
    }
    
    return mockResults;
  }

  private async generateSearchFacets(results: PurchaseOrder[]): Promise<SearchFacet[]> {
    // Generate facets for filtering
    const statusFacet: SearchFacet = {
      field: 'status',
      values: Object.values(PurchaseOrderStatus).map(status => ({
        value: status,
        count: results.filter(r => r.status === status).length
      }))
    };

    const currencyFacet: SearchFacet = {
      field: 'currency',
      values: Array.from(new Set(results.map(r => r.currency))).map(currency => ({
        value: currency,
        count: results.filter(r => r.currency === currency).length
      }))
    };

    return [statusFacet, currencyFacet];
  }

  private async generateSearchSuggestions(searchTerm: string, tenantId: string): Promise<string[]> {
    // Mock search suggestions - would use search analytics in real system
    const suggestions = [
      `${searchTerm} supplier`,
      `${searchTerm} orders`,
      `${searchTerm} delivery`,
      `recent ${searchTerm}`,
      `pending ${searchTerm}`
    ];

    return suggestions.slice(0, 5);
  }

  private validateInvoicingDetails(details: InvoicingDetails): void {
    if (!details.invoiceNumber || details.invoiceNumber.trim().length === 0) {
      throw new Error('Invoice number is required');
    }

    if (!details.invoiceDate || details.invoiceDate > new Date()) {
      throw new Error('Invalid invoice date');
    }

    if (!details.invoiceAmount || details.invoiceAmount <= 0) {
      throw new Error('Invoice amount must be positive');
    }

    if (!details.dueDate || details.dueDate <= details.invoiceDate) {
      throw new Error('Due date must be after invoice date');
    }

    if (!details.currency || details.currency.length !== 3) {
      throw new Error('Invalid currency code');
    }
  }

  private async createFinancialEntry(
    purchaseOrder: PurchaseOrder,
    invoicingDetails: InvoicingDetails,
    tenantId: string
  ): Promise<void> {
    // Create accounting entry - would integrate with finance system
    const financialEntry = {
      type: 'ACCOUNTS_PAYABLE',
      purchaseOrderId: purchaseOrder.id,
      invoiceNumber: invoicingDetails.invoiceNumber,
      amount: invoicingDetails.invoiceAmount,
      currency: invoicingDetails.currency,
      dueDate: invoicingDetails.dueDate,
      supplierId: purchaseOrder.supplierId,
      tenantId
    };

    // Log financial integration
    await this.auditLogger.logSecureEvent('FINANCIAL_ENTRY_CREATED', {
      entryType: financialEntry.type,
      amount: financialEntry.amount,
      currency: financialEntry.currency,
      invoiceNumber: invoicingDetails.invoiceNumber
    }, tenantId);

    console.log('Financial entry created:', financialEntry);
  }

  private async mockGetPurchaseOrder(id: string, tenantId: string): Promise<PurchaseOrder | null> {
    // Mock implementation - would query database
    if (id === 'test-po-id') {
      return new PurchaseOrder(
        'supplier-123',
        'Test Purchase Order',
        'Test purchase order for development',
        new Date(Date.now() + 14 * 24 * 60 * 60 * 1000), // 14 days from now
        [],
        'user-123',
        {
          id: 'test-po-id',
          purchaseOrderNumber: 'PO-TEST-001',
          contactPerson: 'Test Contact',
          paymentTerms: 'NET 30',
          currency: 'EUR',
          taxRate: 19.0,
          notes: 'Test purchase order'
        }
      );
    }
    return null;
  }
}
