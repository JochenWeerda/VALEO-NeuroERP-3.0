/**
 * Search Service - MSOA Implementation nach Clean Architecture
 * Infrastructure Layer External Service migrated to VALEO-NeuroERP-3.0
 * Search engine integration (OpenSearch/Elasticsearch)
 */
import { Brand } from '@valero-neuroerp/data-models/src/branded-types';
export type DocumentId = Brand<string, 'DocumentId'>;
export type IndexName = Brand<string, 'IndexName'>;
export type SearchQueryId = Brand<string, 'SearchQueryId'>;
export interface SearchDocument {
    readonly id: DocumentId;
    readonly index: IndexName;
    readonly content: Record<string, any>;
    readonly metadata?: Record<string, any>;
    readonly timestamp: Date;
    readonly validFor: number;
    readonly searchable?: boolean;
}
export interface SearchQuery {
    readonly id: SearchQueryId;
    readonly query: string;
    readonly filters?: SearchFilter[];
    readonly sortFields?: SortField[];
    readonly pagination?: SearchPagination;
    readonly sourceFields?: string[];
    readonly timestamp: Date;
}
export interface SearchFilter {
    readonly field: string;
    readonly operator: 'equals' | 'contains' | 'range' | 'exists' | 'in';
    readonly value: any;
    readonly nested?: boolean;
}
export interface SortField {
    readonly field: string;
    readonly direction: 'asc' | 'desc';
}
export interface SearchPagination {
    readonly from: number;
    readonly size: number;
}
export interface SearchResult {
    readonly totalHitCount: number;
    readonly maxScore: number;
    readonly hits: SearchHit[];
    readonly facets?: Record<string, any>;
    readonly aggregations?: Record<string, any>;
    readonly tookMillis: number;
}
export interface SearchHit {
    readonly id: DocumentId;
    readonly score: number;
    readonly source: Record<string, any>;
    readonly highlights?: Record<string, string[]>;
    readonly matched_fields: string[];
}
export interface SearchIndexMapping {
    readonly properties: Record<string, MappingField>;
    readonly dynamic: boolean;
    readonly date_detection: boolean;
    readonly numeric_detection: boolean;
}
export interface MappingField {
    readonly type: 'text' | 'keyword' | 'date' | 'long' | 'double' | 'boolean' | 'nested';
    readonly analyzer?: string;
    readonly search_analyzer?: string;
    readonly format?: string;
    readonly fields?: Record<string, MappingField>;
}
export declare class SearchService {
    private readonly documents;
    private readonly indexes;
    private readonly searchHistory;
    private readonly configuration;
    constructor();
    /**
     * Initialize Search Service
     */
    private initializeSearchService;
    /**
     * Setup Default Indexes nach Business Model
     */
    private setupDefaultIndexes;
    /**
     * Create Core Business Indexes
     */
    private createCoreBusinessIndexes;
    /**
     * Create Domain-Specific Indexes
     */
    private createDomainIndexes;
    /**
     * Index Document
     */
    indexDocument(index: IndexName, document: SearchDocument, options?: {
        upsert?: boolean;
        refresh?: boolean;
    }): Promise<DocumentId>;
    /**
     * Search Documents
     */
    searchDocuments(searchQuery: SearchQuery, index?: IndexName): Promise<SearchResult>;
    /**
     * Perform Search Hit Matching nach Search Query
     */
    private performSearchHit;
    /**
     * Generate Highlight Text für Search Results
     */
    private generateHighlights;
    /**
     * Delete Document
     */
    deleteDocument(index: IndexName, documentId: DocumentId): Promise<boolean>;
    /**
     * Create Index
     */
    createIndex(indexName: IndexName, mapping: SearchIndexMapping): Promise<boolean>;
    /**
     * Document Validation
     */
    private validateDocument;
    /**
     * Get Search Statistics
     */
    getSearchStatistics(): Promise<{
        totalDocuments: number;
        totalIndexes: number;
        averageHitsPerQuery: number;
        indexStats: Record<string, number>;
    }>;
    /**
     * Health check
     */
    healthCheck(): Promise<boolean>;
    private generateSearchQueryId;
}
/**
 * Register Search Service in DI Container
 */
export declare function registerSearchService(): void;
//# sourceMappingURL=search-service.d.ts.map