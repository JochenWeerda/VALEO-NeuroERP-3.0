"use strict";
/**
 * VALEO NeuroERP 3.0 - Bank Reconciliation Service
 *
 * Handles bank statement import (MT940/CSV/API), AI-assisted matching,
 * and reconciliation of bank transactions with accounting entries
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.AIBankMatchEngine = exports.BankStatementParser = exports.BankReconciliationApplicationService = void 0;
const ar_invoice_1 = require("../core/entities/ar-invoice");
// ===== SERVICE =====
class BankReconciliationApplicationService {
    constructor(bankStatementRepo, matchEngine, journalService, eventPublisher) {
        this.bankStatementRepo = bankStatementRepo;
        this.matchEngine = matchEngine;
        this.journalService = journalService;
        this.eventPublisher = eventPublisher;
        this.parser = new BankStatementParser();
    }
    /**
     * Import and process bank statement
     */
    async importStatement(command) {
        try {
            // Parse statement based on source type
            let statement;
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
                    return (0, ar_invoice_1.err)(`Unsupported source type: ${command.sourceType}`);
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
            return (0, ar_invoice_1.ok)(statement);
        }
        catch (error) {
            return (0, ar_invoice_1.err)(error instanceof Error ? error.message : 'Import failed');
        }
    }
    /**
     * Process automatic matching for statement
     */
    async processAutoMatching(statementId) {
        const statement = await this.bankStatementRepo.findById(statementId);
        if (!statement) {
            return (0, ar_invoice_1.err)(`Statement ${statementId} not found`);
        }
        const unmatchedLines = statement.lines.filter(line => line.status === 'UNMATCHED');
        const matches = [];
        for (const line of unmatchedLines) {
            const matchResult = await this.matchEngine.findMatch(line, statement.tenantId);
            if (matchResult.isSuccess) {
                const match = matchResult.getValue();
                // Update statement line
                await this.bankStatementRepo.updateLineMatch(line.id, match.matchedEntryId, match.confidence, match.matchType, 'MATCHED');
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
        const result = {
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
        return (0, ar_invoice_1.ok)(result);
    }
    /**
     * Create manual match
     */
    async createManualMatch(command) {
        const line = await this.bankStatementRepo.findLineById(command.statementLineId);
        if (!line) {
            return (0, ar_invoice_1.err)(`Statement line ${command.statementLineId} not found`);
        }
        await this.bankStatementRepo.updateLineMatch(command.statementLineId, command.entryId, 1.0, // Manual matches have 100% confidence
        'MANUAL', 'MATCHED');
        // Record the match
        const match = {
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
        return (0, ar_invoice_1.ok)(undefined);
    }
    /**
     * Get reconciliation status for statement
     */
    async getReconciliationStatus(statementId) {
        const statement = await this.bankStatementRepo.findById(statementId);
        if (!statement) {
            return (0, ar_invoice_1.err)(`Statement ${statementId} not found`);
        }
        const matchedLines = statement.lines.filter(line => line.status === 'MATCHED').length;
        const unmatchedLines = statement.lines.filter(line => line.status === 'UNMATCHED').length;
        const conflicts = statement.lines.filter(line => line.status === 'CONFLICT').length;
        const result = {
            statementId,
            totalLines: statement.lines.length,
            matchedLines,
            unmatchedLines,
            conflicts,
            matchRate: statement.lines.length > 0 ? matchedLines / statement.lines.length : 0,
            matches: [], // Would be populated from match history
            processedAt: new Date()
        };
        return (0, ar_invoice_1.ok)(result);
    }
    /**
     * Get unmatched lines for manual processing
     */
    async getUnmatchedLines(tenantId) {
        return await this.bankStatementRepo.findUnmatchedLines(tenantId);
    }
    /**
     * Get match suggestions for a statement line
     */
    async getMatchSuggestions(statementLineId) {
        const line = await this.bankStatementRepo.findLineById(statementLineId);
        if (!line) {
            return (0, ar_invoice_1.err)(`Statement line ${statementLineId} not found`);
        }
        const statement = await this.bankStatementRepo.findById(line.statementId);
        if (!statement) {
            return (0, ar_invoice_1.err)(`Statement ${line.statementId} not found`);
        }
        return await this.matchEngine.getSuggestions(line, statement.tenantId);
    }
}
exports.BankReconciliationApplicationService = BankReconciliationApplicationService;
// ===== PARSERS =====
class BankStatementParser {
    async parseMT940(content, command) {
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
    async parseCSV(content, command) {
        const text = content.toString();
        const lines = text.split('\n').slice(1); // Skip header
        const statementLines = [];
        for (const line of lines) {
            if (!line.trim())
                continue;
            const parts = line.split(',');
            const date = parts[0]?.trim();
            const counterparty = parts[1]?.trim();
            const purpose = parts[2]?.trim();
            const amount = parts[3]?.trim();
            const currency = parts[4]?.trim();
            if (!date || !amount)
                continue; // Skip invalid lines
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
    async parseAPIResponse(content, command) {
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
            lines: data.lines.map((lineData) => ({
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
    extractMT940Lines(mt940Content) {
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
exports.BankStatementParser = BankStatementParser;
class AIBankMatchEngine {
    async findMatch(line, tenantId) {
        // AI-powered matching logic
        // In reality, this would use ML models to find the best match
        // Simple rule-based matching for demo
        const confidence = this.calculateConfidence(line);
        const explanation = this.generateExplanation(line, confidence);
        if (confidence > 0.8) {
            return (0, ar_invoice_1.ok)({
                matchedEntryId: `entry-${crypto.randomUUID()}`,
                confidence,
                matchType: 'AI',
                explanation
            });
        }
        return (0, ar_invoice_1.err)('No suitable match found');
    }
    async getSuggestions(line, tenantId) {
        // Generate multiple match suggestions with different confidence levels
        const suggestions = [
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
        return (0, ar_invoice_1.ok)(suggestions);
    }
    calculateConfidence(line) {
        let confidence = 0;
        // Amount-based matching
        if (Math.abs(line.amount) > 1000)
            confidence += 0.3;
        else if (Math.abs(line.amount) > 100)
            confidence += 0.2;
        // Purpose analysis
        if (line.purpose.toLowerCase().includes('invoice'))
            confidence += 0.3;
        if (line.purpose.toLowerCase().includes('payment'))
            confidence += 0.2;
        // Counterparty analysis
        if (line.counterparty.name.length > 5)
            confidence += 0.2;
        return Math.min(confidence, 1.0);
    }
    generateExplanation(line, confidence) {
        const reasons = [];
        if (confidence > 0.8) {
            reasons.push('High confidence match based on amount and purpose analysis');
        }
        else if (confidence > 0.6) {
            reasons.push('Medium confidence match with partial criteria matching');
        }
        else {
            reasons.push('Low confidence match requiring manual review');
        }
        return reasons.join('; ');
    }
}
exports.AIBankMatchEngine = AIBankMatchEngine;
//# sourceMappingURL=bank-reconciliation-service.js.map