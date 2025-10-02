"use strict";
/**
 * Search Service - MSOA Implementation nach Clean Architecture
 * Infrastructure Layer External Service migrated to VALEO-NeuroERP-3.0
 * Search engine integration (OpenSearch/Elasticsearch)
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.SearchService = void 0;
exports.registerSearchService = registerSearchService;
const di_container_1 = require("@valeo-neuroerp-3.0/packages/utilities/src/di-container");
// ===== SEARCH SERVICE nach Clean Architecture =====
class SearchService {
    documents = new Map();
    indexes = new Map();
    searchHistory = [];
    configuration = {
        defaultAnalyzer: 'standard',
        maxResults: 10000,
        defaultPageSize: 20
    };
    constructor() {
        console.log('[SEARCH SERVICE] Initializing Search Service nach infrastructure external services architecture...');
        this.initializeSearchService();
    }
    /**
     * Initialize Search Service
     */
    initializeSearchService() {
        console.log('[SEARCH INIT] Search service initialization nach infrastructure requirements...');
        try {
            this.setupDefaultIndexes();
            console.log('[SEARCH INIT] ✓ Search service initialized nach infrastructure architecture');
        }
        catch (error) {
            console.error('[SEARCH INIT] Search service initialization failed:', error);
            throw new Error(`Search service configuration failed: ${error}`);
        }
    }
    /**
     * Setup Default Indexes nach Business Model
     */
    setupDefaultIndexes() {
        console.log('[SEARCH SETUP] Setting up default indexes nach business domain requirements...');
        // Architecture: Core business indexes
        this.createCoreBusinessIndexes();
        this.createDomainIndexes();
        console.log('[SEARCH SETUP] ✓ Default indexes configured nach business model');
    }
    /**
     * Create Core Business Indexes
     */
    createCoreBusinessIndexes() {
        // Architecture: Customer Index
        const customerMapping = {
            properties: {
                customerId: { type: 'keyword' },
                customerName: { type: 'text', analyzer: 'standard' },
                email: { type: 'keyword' },
                phone: { type: 'keyword' },
                company: { type: 'text', analyzer: 'standard' },
                address: {
                    type: 'nested',
                    properties: {
                        street: { type: 'text', analyzer: 'standard' },
                        city: { type: 'keyword' },
                        country: { type: 'keyword' }
                    }
                }
            },
            dynamic: false,
            date_detection: true,
            numeric_detection: true
        };
        this.indexes.set('customers', {
            mapping: customerMapping,
            documents: []
        });
        // Architecture: Product Index
        const productMapping = {
            properties: {
                productId: { type: 'keyword' },
                productName: { type: 'text', analyzer: 'standard' },
                description: { type: 'text', analyzer: 'standard' },
                sku: { type: 'keyword' },
                category: { type: 'keyword' },
                price: { type: 'double' },
                available: { type: 'boolean' }
            },
            dynamic: false,
            date_detection: false,
            numeric_detection: true
        };
        this.indexes.set('products', {
            mapping: productMapping,
            documents: []
        });
        console.log('[SEARCH] ✓ Core business indexes created nach business architecture');
    }
    /**
     * Create Domain-Specific Indexes
     */
    createDomainIndexes() {
        // Architecture: CRM Domain Index
        const crmMapping = {
            properties: {
                leadId: { type: 'keyword' },
                leadName: { type: 'text', analyzer: 'standard' },
                leadStatus: { type: 'keyword' },
                source: { type: 'keyword' },
                created_at: { type: 'date' }
            },
            dynamic: false,
            date_detection: true,
            numeric_detection: true
        };
        this.indexes.set('crm_leads', {
            mapping: crmMapping,
            documents: []
        });
        console.log('[SEARCH] ✓ Domain indexes created nach business architecture');
    }
    /**
     * Index Document
     */
    async indexDocument(index, document, options) {
        try {
            console.log(`[SEARCH INDEX] Indexing document to index: ${index}`);
            // Validate index exists
            if (!this.indexes.has(index)) {
                throw new Error(`Index does not exist: ${index}`);
            }
            // Architecture: Document validation
            if (!this.validateDocument(document, index)) {
                throw new Error('Document validation failed');
            }
            // Store document
            this.documents.set(document.id, document);
            // Update index document list
            const indexData = this.indexes.get(index);
            const documentIndex = indexData.documents.indexOf(document.id);
            if (documentIndex === -1) {
                indexData.documents.push(document.id);
            }
            console.log(`[SEARCH INDEX] ✓ Document indexed successfully: ${document.id}`);
            return document.id;
        }
        catch (error) {
            console.error('[SEARCH INDEX] Document indexing failed:', error);
            throw new Error(`Document indexing failed: ${error}`);
        }
    }
    /**
     * Search Documents
     */
    async searchDocuments(searchQuery, index) {
        try {
            const queryId = this.generateSearchQueryId();
            console.log(`[SEARCH] Executing search query: ${queryId}`);
            const indexesToSearch = index ? [index] : Array.from(this.indexes.keys());
            const documents = new Array();
            let totalHits = 0;
            // Architecture: Search across indexes
            for (const indexName of indexesToSearch) {
                const indexData = this.indexes.get(indexName);
                if (!indexData)
                    continue;
                for (const documentId of indexData.documents) {
                    const document = this.documents.get(documentId);
                    if (!document)
                        continue;
                    // Full-text search
                    const hit = await this.performSearchHit(document, searchQuery);
                    if (hit) {
                        documents.push({ document, hit });
                        totalHits++;
                    }
                }
            }
            // Apply sorting
            const sortedDocuments = documents.sort((a, b) => b.hit.score - a.hit.score);
            // Apply pagination
            const pagination = searchQuery.pagination || { from: 0, size: this.configuration.defaultPageSize };
            const paginatedDocuments = sortedDocuments.slice(pagination.from, pagination.from + pagination.size);
            const searchResult = {
                totalHitCount: totalHits,
                maxScore: paginatedDocuments.length > 0 ? paginatedDocuments[0].hit.score : 0,
                hits: paginatedDocuments.map(({ hit }) => hit),
                tookMillis: Date.now() % 1000 // Mock timing
            };
            console.log(`[SEARCH] ✓ Search completed: ${paginatedDocuments.length} hits found`);
            return searchResult;
        }
        catch (error) {
            console.error('[SEARCH] Search execution failed:', error);
            throw new Error(`Search operation failed: ${error}`);
        }
    }
    /**
     * Perform Search Hit Matching nach Search Query
     */
    async performSearchHit(document, query) {
        try {
            const queryTerm = query.query.toLowerCase();
            const content = JSON.stringify(document.content).toLowerCase();
            if (content.includes(queryTerm)) {
                // Simple scoring: relevance calculation
                const contentFields = Object.values(document.content);
                const fieldsText = contentFields.join(' ').toLowerCase();
                const score = fieldsText.split(queryTerm).length - 1;
                return {
                    id: document.id,
                    score: Math.max(0.1, Math.min(1.0, score / 10)),
                    source: document.content,
                    highlights: this.generateHighlights(document.content, query.query),
                    matched_fields: Object.keys(document.content)
                };
            }
            return null;
        }
        catch (error) {
            console.error('[SEARCH] Hit matching failed:', error);
            return null;
        }
    }
    /**
     * Generate Highlight Text für Search Results
     */
    generateHighlights(content, query) {
        const highlights = {};
        for (const [key, value] of Object.entries(content)) {
            if (typeof value === 'string' && value.toLowerCase().includes(query.toLowerCase())) {
                highlights[key] = [value]; // Architecture: In production use actual highlighting logic
            }
        }
        return highlights;
    }
    /**
     * Delete Document
     */
    async deleteDocument(index, documentId) {
        try {
            console.log(`[SEARCH DELETE] Deleting document: ${documentId} from index: ${index}`);
            if (this.documents.has(documentId)) {
                this.documents.delete(documentId);
                // Remove from index
                const indexData = this.indexes.get(index);
                if (indexData) {
                    const docIndex = indexData.documents.indexOf(documentId);
                    if (docIndex !== -1) {
                        indexData.documents.splice(docIndex, 1);
                    }
                }
                console.log(`[SEARCH DELETE] ✓ Document deleted successfully: ${documentId}`);
                return true;
            }
            return false;
        }
        catch (error) {
            console.error('[SEARCH DELETE] Document deletion failed:', error);
            return false;
        }
    }
    /**
     * Create Index
     */
    async createIndex(indexName, mapping) {
        try {
            console.log(`[SEARCH CREATE INDEX] Creating index: ${indexName}`);
            this.indexes.set(indexName, {
                mapping,
                documents: []
            });
            console.log(`[SEARCH CREATE INDEX] ✓ Index created successfully: ${indexName}`);
            return true;
        }
        catch (error) {
            console.error('[SEARCH CREATE INDEX] Index creation failed:', error);
            return false;
        }
    }
    /**
     * Document Validation
     */
    validateDocument(document, indexName) {
        try {
            // Architecture: More sophisticated validation logic here
            const requiredFields = ['id', 'content', 'timestamp'];
            const hasRequiredFields = requiredFields.every(field => field in document);
            const validIndex = this.indexes.has(indexName);
            return hasRequiredFields && validIndex;
        }
        catch (error) {
            console.error('[SEARCH VALIDATION] Document validation failed:', error);
            return false;
        }
    }
    /**
     * Get Search Statistics
     */
    async getSearchStatistics() {
        const totalDocuments = this.documents.size;
        const totalIndexes = this.indexes.size;
        const indexStats = {};
        for (const [indexName, indexData] of this.indexes.entries()) {
            indexStats[indexName] = indexData.documents.length;
        }
        return {
            totalDocuments,
            totalIndexes,
            averageHitsPerQuery: 15, // Mock
            indexStats
        };
    }
    /**
     * Health check
     */
    async healthCheck() {
        try {
            console.log('[SEARCH HEALTH] Checking search service health nach infrastructure architecture...');
            const indexesCount = this.indexes.size;
            const isHealthy = indexesCount > 0;
            if (!isHealthy) {
                console.error('[SEARCH HEALTH] No search indexes configured');
                return false;
            }
            console.log(`[SEARCH HEALTH] ✓ Search service health validated nach infrastructure architecture (${indexesCount} indexes)`);
            return true;
        }
        catch (error) {
            console.error('[SEARCH HEALTH] Search service health check failed:', error);
            return false;
        }
    }
    // Helper methods
    generateSearchQueryId() {
        const id = 'search_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        return id;
    }
}
exports.SearchService = SearchService;
/**
 * Register Search Service in DI Container
 */
function registerSearchService() {
    console.log('[SEARCH REGISTRATION] Registering Search Service nach infrastructure external services architecture...');
    di_container_1.DIContainer.register('SearchService', new SearchService(), {
        singleton: true,
        dependencies: []
    });
    console.log('[SEARCH REGISTRATION] ✅ Search Service registered successfully nach infrastructure external services architecture');
}
