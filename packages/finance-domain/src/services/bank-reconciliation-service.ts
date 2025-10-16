/**
 * VALEO NeuroERP 3.0 - Bank Reconciliation Service
 *
 * Handles bank statement import (MT940/CSV/API), AI-assisted matching,
 * and reconciliation of bank transactions with accounting entries
 */

import { Result, err, ok } from '../core/entities/ar-invoice';

// ===== INTERFACES =====

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

// ===== COMMANDS =====

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

// ===== SERVICE =====

export class BankReconciliationApplicationService {
  private readonly parser: BankStatementParser;

  constructor(
    private readonly bankStatementRepo: BankStatementRepository,
    private readonly matchEngine: AIBankMatchEngine,
    private readonly journalService: JournalService,
    private readonly eventPublisher: EventPublisher
  ) {
    this.parser = new BankStatementParser();
  }

  /**
   * Import and process bank statement
   */
  async importStatement(command: ImportBankStatementCommand): Promise<Result<BankStatement>> {
    try {
      // Parse statement based on source type
      let statement: BankStatement;

      switch (command.sourceType) {
        case 'MT940':
          statement = await this.parser.parseMT940(command.content, command);
          break;
        case 'CSV':
          statement = await this.parser.parseCSV(command.content, command);
          break;
        case 'API':
          statement = await this.parser.parseAPIResponse(command.content, command);
          break;
        default:
          return err(`Unsupported source type: ${command.sourceType}`);
      }

      // Save statement
      await this.bankStatementRepo.save(statement);

      // Auto-match if requested
      if (command.autoMatch) {
        await this.processAutoMatching(statement.id);
      }

      // Publish event
      await this.eventPublisher.publish({
        type: 'finance.bank.statement.imported',
        statementId: statement.id,
        tenantId: statement.tenantId,
        accountIban: statement.accountIban,
        lineCount: statement.lines.length,
        openingBalance: statement.openingBalance,
        closingBalance: statement.closingBalance
      });

      return ok(statement);

    } catch (error) {
      return err(error instanceof Error ? error.message : 'Import failed');
    }
  }

  /**
   * Process automatic matching for statement
   */
  async processAutoMatching(statementId: string): Promise<Result<ReconciliationResult>> {
    const statement = await this.bankStatementRepo.findById(statementId);
    if (!statement) {
      return err(`Statement ${statementId} not found`);
    }

    const unmatchedLines = statement.lines.filter(line => line.status === 'UNMATCHED');
    const matches: BankReconciliationMatch[] = [];

    for (const line of unmatchedLines) {
      const matchResult = await this.matchEngine.findMatch(line, statement.tenantId);

      if (matchResult.isSuccess) {
        const match = matchResult.getValue();

        // Update statement line
        await this.bankStatementRepo.updateLineMatch(
          line.id,
          match.matchedEntryId,
          match.confidence,
          match.matchType,
          'MATCHED'
        );

        matches.push({
          id: crypto.randomUUID(),
          statementLineId: line.id,
          matchedEntryId: match.matchedEntryId,
          matchType: match.matchType,
          confidence: match.confidence,
          matchedBy: 'SYSTEM',
          matchedAt: new Date(),
          ...(match.explanation && { explanation: match.explanation }),
          metadata: {}
        });
      }
    }

    const result: ReconciliationResult = {
      statementId,
      totalLines: statement.lines.length,
      matchedLines: matches.length,
      unmatchedLines: statement.lines.length - matches.length,
      conflicts: 0,
      matchRate: statement.lines.length > 0 ? matches.length / statement.lines.length : 0,
      matches,
      processedAt: new Date()
    };

    // Publish match completed event
    await this.eventPublisher.publish({
      type: 'finance.bank.match.completed',
      statementId,
      tenantId: statement.tenantId,
      matchRate: result.matchRate,
      matchedLines: result.matchedLines,
      unmatchedLines: result.unmatchedLines
    });

    return ok(result);
  }

  /**
   * Create manual match
   */
  async createManualMatch(command: CreateManualMatchCommand): Promise<Result<void>> {
    const line = await this.bankStatementRepo.findLineById(command.statementLineId);
    if (!line) {
      return err(`Statement line ${command.statementLineId} not found`);
    }

    await this.bankStatementRepo.updateLineMatch(
      command.statementLineId,
      command.entryId,
      1.0, // Manual matches have 100% confidence
      'MANUAL',
      'MATCHED'
    );

    // Record the match
    const match: BankReconciliationMatch = {
      id: crypto.randomUUID(),
      statementLineId: command.statementLineId,
      matchedEntryId: command.entryId,
      matchType: 'MANUAL',
      confidence: 1.0,
      matchedBy: command.matchedBy,
      matchedAt: new Date(),
      metadata: { notes: command.notes }
    };

    await this.eventPublisher.publish({
      type: 'finance.bank.match.manual',
      match,
      matchedBy: command.matchedBy
    });

    return ok(undefined);
  }

  /**
   * Get reconciliation status for statement
   */
  async getReconciliationStatus(statementId: string): Promise<Result<ReconciliationResult>> {
    const statement = await this.bankStatementRepo.findById(statementId);
    if (!statement) {
      return err(`Statement ${statementId} not found`);
    }

    const matchedLines = statement.lines.filter(line => line.status === 'MATCHED').length;
    const unmatchedLines = statement.lines.filter(line => line.status === 'UNMATCHED').length;
    const conflicts = statement.lines.filter(line => line.status === 'CONFLICT').length;

    const result: ReconciliationResult = {
      statementId,
      totalLines: statement.lines.length,
      matchedLines,
      unmatchedLines,
      conflicts,
      matchRate: statement.lines.length > 0 ? matchedLines / statement.lines.length : 0,
      matches: [], // Would be populated from match history
      processedAt: new Date()
    };

    return ok(result);
  }

  /**
   * Get unmatched lines for manual processing
   */
  async getUnmatchedLines(tenantId: string): Promise<BankStatementLine[]> {
    return await this.bankStatementRepo.findUnmatchedLines(tenantId);
  }

  /**
   * Get match suggestions for a statement line
   */
  async getMatchSuggestions(statementLineId: string): Promise<Result<MatchSuggestion[]>> {
    const line = await this.bankStatementRepo.findLineById(statementLineId);
    if (!line) {
      return err(`Statement line ${statementLineId} not found`);
    }

    const statement = await this.bankStatementRepo.findById(line.statementId);
    if (!statement) {
      return err(`Statement ${line.statementId} not found`);
    }

    return await this.matchEngine.getSuggestions(line, statement.tenantId);
  }
}

// ===== PARSERS =====

export class BankStatementParser {
  async parseMT940(content: string | Buffer, command: ImportBankStatementCommand): Promise<BankStatement> {
    const text = content.toString();

    // Mock MT940 parsing - in reality would parse MT940 format
    const lines = this.extractMT940Lines(text);

    return {
      id: crypto.randomUUID(),
      tenantId: command.tenantId,
      accountIban: command.accountIban,
      statementDate: new Date(),
      sourceRef: command.sourceRef,
      openingBalance: 10000.00,
      closingBalance: 15000.00,
      currency: 'EUR',
      lines: lines.map((lineData, index) => ({
        id: crypto.randomUUID(),
        statementId: '', // Will be set when statement is saved
        amount: lineData.amount,
        currency: lineData.currency,
        counterparty: lineData.counterparty,
        purpose: lineData.purpose,
        valueDate: lineData.valueDate,
        bookingDate: lineData.bookingDate,
        status: 'UNMATCHED',
        metadata: {}
      })),
      metadata: { sourceType: 'MT940' },
      createdAt: new Date()
    };
  }

  async parseCSV(content: string | Buffer, command: ImportBankStatementCommand): Promise<BankStatement> {
    const text = content.toString();
    const lines = text.split('\n').slice(1); // Skip header

    const statementLines: BankStatementLine[] = [];

    for (const line of lines) {
      if (!line.trim()) continue;

      const parts = line.split(',');
      const date = parts[0]?.trim();
      const counterparty = parts[1]?.trim();
      const purpose = parts[2]?.trim();
      const amount = parts[3]?.trim();
      const currency = parts[4]?.trim();

      if (!date || !amount) continue; // Skip invalid lines

      statementLines.push({
        id: crypto.randomUUID(),
        statementId: '', // Will be set when statement is saved
        amount: parseFloat(amount) || 0,
        currency: currency || 'EUR',
        counterparty: {
          name: counterparty || 'Unknown'
        },
        purpose: purpose || '',
        valueDate: new Date(date),
        bookingDate: new Date(date),
        status: 'UNMATCHED',
        metadata: {}
      });
    }

    return {
      id: crypto.randomUUID(),
      tenantId: command.tenantId,
      accountIban: command.accountIban,
      statementDate: new Date(),
      sourceRef: command.sourceRef,
      openingBalance: 0,
      closingBalance: statementLines.reduce((sum, line) => sum + line.amount, 0),
      currency: 'EUR',
      lines: statementLines,
      metadata: { sourceType: 'CSV' },
      createdAt: new Date()
    };
  }

  async parseAPIResponse(content: string | Buffer, command: ImportBankStatementCommand): Promise<BankStatement> {
    // Mock API response parsing
    const data = JSON.parse(content.toString());

    return {
      id: crypto.randomUUID(),
      tenantId: command.tenantId,
      accountIban: command.accountIban,
      statementDate: new Date(data.statementDate),
      sourceRef: command.sourceRef,
      openingBalance: data.openingBalance,
      closingBalance: data.closingBalance,
      currency: data.currency,
      lines: data.lines.map((lineData: any) => ({
        id: crypto.randomUUID(),
        statementId: '', // Will be set when statement is saved
        amount: lineData.amount,
        currency: lineData.currency,
        counterparty: lineData.counterparty,
        purpose: lineData.purpose,
        valueDate: new Date(lineData.valueDate),
        bookingDate: new Date(lineData.bookingDate),
        status: 'UNMATCHED',
        metadata: {}
      })),
      metadata: { sourceType: 'API' },
      createdAt: new Date()
    };
  }

  private extractMT940Lines(mt940Content: string): any[] {
    // Mock MT940 line extraction
    return [
      {
        amount: 1000.00,
        currency: 'EUR',
        counterparty: { name: 'Customer A' },
        purpose: 'Payment for invoice INV-001',
        valueDate: new Date(),
        bookingDate: new Date()
      },
      {
        amount: -500.00,
        currency: 'EUR',
        counterparty: { name: 'Supplier B' },
        purpose: 'Payment for materials',
        valueDate: new Date(),
        bookingDate: new Date()
      }
    ];
  }
}

// ===== MATCH ENGINE =====

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

export class AIBankMatchEngine implements MatchEngine {
  async findMatch(line: BankStatementLine, tenantId: string): Promise<Result<{
    matchedEntryId: string;
    confidence: number;
    matchType: 'AUTO' | 'AI';
    explanation?: string;
  }>> {
    // AI-powered matching logic
    // In reality, this would use ML models to find the best match

    // Simple rule-based matching for demo
    const confidence = this.calculateConfidence(line);
    const explanation = this.generateExplanation(line, confidence);

    if (confidence > 0.8) {
      return ok({
        matchedEntryId: `entry-${crypto.randomUUID()}`,
        confidence,
        matchType: 'AI',
        explanation
      });
    }

    return err('No suitable match found');
  }

  async getSuggestions(line: BankStatementLine, tenantId: string): Promise<Result<MatchSuggestion[]>> {
    // Generate multiple match suggestions with different confidence levels
    const suggestions: MatchSuggestion[] = [
      {
        entryId: `entry-${crypto.randomUUID()}`,
        confidence: 0.95,
        matchReason: 'Amount and counterparty match',
        explanation: 'Transaction amount and counterparty name match exactly with outstanding invoice'
      },
      {
        entryId: `entry-${crypto.randomUUID()}`,
        confidence: 0.75,
        matchReason: 'Amount match with similar purpose',
        explanation: 'Amount matches but counterparty name is similar'
      }
    ];

    return ok(suggestions);
  }

  private calculateConfidence(line: BankStatementLine): number {
    let confidence = 0;

    // Amount-based matching
    if (Math.abs(line.amount) > 1000) confidence += 0.3;
    else if (Math.abs(line.amount) > 100) confidence += 0.2;

    // Purpose analysis
    if (line.purpose.toLowerCase().includes('invoice')) confidence += 0.3;
    if (line.purpose.toLowerCase().includes('payment')) confidence += 0.2;

    // Counterparty analysis
    if (line.counterparty.name.length > 5) confidence += 0.2;

    return Math.min(confidence, 1.0);
  }

  private generateExplanation(line: BankStatementLine, confidence: number): string {
    const reasons: string[] = [];

    if (confidence > 0.8) {
      reasons.push('High confidence match based on amount and purpose analysis');
    } else if (confidence > 0.6) {
      reasons.push('Medium confidence match with partial criteria matching');
    } else {
      reasons.push('Low confidence match requiring manual review');
    }

    return reasons.join('; ');
  }
}

// ===== REPOSITORY INTERFACES =====

export interface BankStatementRepository {
  save(statement: BankStatement): Promise<void>;
  findById(id: string): Promise<BankStatement | null>;
  findByAccountIban(tenantId: string, iban: string): Promise<BankStatement[]>;
  findByTenant(tenantId: string): Promise<BankStatement[]>;
  findUnmatchedLines(tenantId: string): Promise<BankStatementLine[]>;
  findLineById(lineId: string): Promise<BankStatementLine | null>;
  updateLineMatch(
    lineId: string,
    matchedEntryId: string,
    confidence: number,
    matchType: string,
    status: string
  ): Promise<void>;
}

export interface JournalService {
  createJournalEntry(
    tenantId: string,
    entries: Array<{
      accountId: string;
      debit: number;
      credit: number;
      description: string;
    }>
  ): Promise<string>;
}

// ===== ADDITIONAL INTERFACES =====

export interface EventPublisher {
  publish(event: any): Promise<void>;
}

export interface DocumentStore {
  store(content: Buffer, metadata: Record<string, any>): Promise<string>;
  retrieve(ref: string): Promise<Buffer | null>;
}