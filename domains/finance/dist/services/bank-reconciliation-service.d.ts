/**
 * VALEO NeuroERP 3.0 - Bank Reconciliation Service
 *
 * Handles bank statement import (MT940/CSV/API), AI-assisted matching,
 * and reconciliation of bank transactions with accounting entries
 */
import { Result } from '../core/entities/ar-invoice';
export interface BankStatement {
    readonly id: string;
    readonly tenantId: string;
    readonly accountIban: string;
    readonly statementDate: Date;
    readonly sourceRef: string;
    readonly openingBalance: number;
    readonly closingBalance: number;
    readonly currency: string;
    readonly lines: BankStatementLine[];
    readonly metadata: Record<string, any>;
    readonly createdAt: Date;
}
export interface BankStatementLine {
    readonly id: string;
    readonly statementId: string;
    readonly amount: number;
    readonly currency: string;
    readonly counterparty: {
        name: string;
        iban?: string;
        bic?: string;
    };
    readonly purpose: string;
    readonly valueDate: Date;
    readonly bookingDate: Date;
    readonly matchedEntryId?: string;
    readonly matchConfidence?: number;
    readonly matchType?: 'AUTO' | 'AI' | 'MANUAL';
    readonly status: 'UNMATCHED' | 'MATCHED' | 'CONFLICT' | 'EXCLUDED';
    readonly metadata: Record<string, any>;
}
export interface BankReconciliationMatch {
    readonly id: string;
    readonly statementLineId: string;
    readonly matchedEntryId: string;
    readonly matchType: 'AUTO' | 'AI' | 'MANUAL';
    readonly confidence: number;
    readonly matchedBy: string;
    readonly matchedAt: Date;
    readonly explanation?: string;
    readonly metadata: Record<string, any>;
}
export interface ReconciliationResult {
    readonly statementId: string;
    readonly totalLines: number;
    readonly matchedLines: number;
    readonly unmatchedLines: number;
    readonly conflicts: number;
    readonly matchRate: number;
    readonly matches: BankReconciliationMatch[];
    readonly processedAt: Date;
}
export interface ImportBankStatementCommand {
    readonly tenantId: string;
    readonly accountIban: string;
    readonly sourceType: 'MT940' | 'CSV' | 'API';
    readonly content: string | Buffer;
    readonly sourceRef: string;
    readonly autoMatch?: boolean;
}
export interface CreateManualMatchCommand {
    readonly statementLineId: string;
    readonly entryId: string;
    readonly matchedBy: string;
    readonly notes?: string;
}
export interface ResolveConflictCommand {
    readonly statementLineId: string;
    readonly resolution: 'MATCH' | 'EXCLUDE' | 'SPLIT';
    readonly resolvedBy: string;
    readonly resolutionData?: Record<string, any>;
}
export declare class BankReconciliationApplicationService {
    private bankStatementRepo;
    private matchEngine;
    private journalService;
    private eventPublisher;
    private parser;
    constructor(bankStatementRepo: BankStatementRepository, matchEngine: AIBankMatchEngine, journalService: JournalService, eventPublisher: EventPublisher);
    /**
     * Import and process bank statement
     */
    importStatement(command: ImportBankStatementCommand): Promise<Result<BankStatement>>;
    /**
     * Process automatic matching for statement
     */
    processAutoMatching(statementId: string): Promise<Result<ReconciliationResult>>;
    /**
     * Create manual match
     */
    createManualMatch(command: CreateManualMatchCommand): Promise<Result<void>>;
    /**
     * Get reconciliation status for statement
     */
    getReconciliationStatus(statementId: string): Promise<Result<ReconciliationResult>>;
    /**
     * Get unmatched lines for manual processing
     */
    getUnmatchedLines(tenantId: string): Promise<BankStatementLine[]>;
    /**
     * Get match suggestions for a statement line
     */
    getMatchSuggestions(statementLineId: string): Promise<Result<MatchSuggestion[]>>;
}
export declare class BankStatementParser {
    parseMT940(content: string | Buffer, command: ImportBankStatementCommand): Promise<BankStatement>;
    parseCSV(content: string | Buffer, command: ImportBankStatementCommand): Promise<BankStatement>;
    parseAPIResponse(content: string | Buffer, command: ImportBankStatementCommand): Promise<BankStatement>;
    private extractMT940Lines;
}
export interface MatchSuggestion {
    entryId: string;
    confidence: number;
    matchReason: string;
    explanation: string;
}
export interface MatchEngine {
    findMatch(line: BankStatementLine, tenantId: string): Promise<Result<{
        matchedEntryId: string;
        confidence: number;
        matchType: 'AUTO' | 'AI';
        explanation?: string;
    }>>;
    getSuggestions(line: BankStatementLine, tenantId: string): Promise<Result<MatchSuggestion[]>>;
}
export declare class AIBankMatchEngine implements MatchEngine {
    findMatch(line: BankStatementLine, tenantId: string): Promise<Result<{
        matchedEntryId: string;
        confidence: number;
        matchType: 'AUTO' | 'AI';
        explanation?: string;
    }>>;
    getSuggestions(line: BankStatementLine, tenantId: string): Promise<Result<MatchSuggestion[]>>;
    private calculateConfidence;
    private generateExplanation;
}
export interface BankStatementRepository {
    save(statement: BankStatement): Promise<void>;
    findById(id: string): Promise<BankStatement | null>;
    findByAccountIban(tenantId: string, iban: string): Promise<BankStatement[]>;
    findByTenant(tenantId: string): Promise<BankStatement[]>;
    findUnmatchedLines(tenantId: string): Promise<BankStatementLine[]>;
    findLineById(lineId: string): Promise<BankStatementLine | null>;
    updateLineMatch(lineId: string, matchedEntryId: string, confidence: number, matchType: string, status: string): Promise<void>;
}
export interface JournalService {
    createJournalEntry(tenantId: string, entries: Array<{
        accountId: string;
        debit: number;
        credit: number;
        description: string;
    }>): Promise<string>;
}
export interface EventPublisher {
    publish(event: any): Promise<void>;
}
export interface DocumentStore {
    store(content: Buffer, metadata: Record<string, any>): Promise<string>;
    retrieve(ref: string): Promise<Buffer | null>;
}
//# sourceMappingURL=bank-reconciliation-service.d.ts.map