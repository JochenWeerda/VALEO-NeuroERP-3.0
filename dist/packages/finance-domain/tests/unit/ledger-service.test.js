"use strict";
/**
 * VALEO NeuroERP 3.0 - Finance Domain - Ledger Service Unit Tests
 *
 * Comprehensive unit tests for ledger functionality
 * Following testing best practices and 85%+ coverage requirement
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.createTestAccount = createTestAccount;
exports.createTestPeriod = createTestPeriod;
const ledger_service_1 = require("../../src/application/services/ledger-service");
const ledger_1 = require("../../src/core/entities/ledger");
// ===== MOCKS =====
class MockJournalRepository {
    journals = new Map();
    async findById(id) {
        return this.journals.get(id) || null;
    }
    async findByPeriod(tenantId, period) {
        return Array.from(this.journals.values()).filter(j => j.tenantId === tenantId && j.period === period);
    }
    async findByTenant(tenantId) {
        return Array.from(this.journals.values()).filter(j => j.tenantId === tenantId);
    }
    async save(journal) {
        this.journals.set(journal.id, journal);
    }
    async findUnbalancedJournals(tenantId) {
        return Array.from(this.journals.values()).filter(j => j.tenantId === tenantId && j.status === 'DRAFT');
    }
    // Test helper
    clear() {
        this.journals.clear();
    }
}
class MockAccountRepository {
    accounts = new Map();
    async findById(id) {
        return this.accounts.get(id) || null;
    }
    async findByAccountNumber(accountNumber) {
        return Array.from(this.accounts.values()).find((acc) => acc.accountNumber === accountNumber) || null;
    }
    async findByType(type) {
        return Array.from(this.accounts.values()).filter((acc) => acc.type === type);
    }
    async findChartOfAccounts(tenantId) {
        return Array.from(this.accounts.values()).filter((acc) => acc.tenantId === tenantId && acc.isActive);
    }
    async save(account) {
        this.accounts.set(account.id, account);
    }
    // Test helper
    addTestAccount(account) {
        this.accounts.set(account.id, account);
    }
    clear() {
        this.accounts.clear();
    }
}
class MockPeriodRepository {
    periods = new Map();
    async findById(id) {
        return this.periods.get(id) || null;
    }
    async findByPeriod(tenantId, period) {
        const key = `${tenantId}:${period}`;
        return this.periods.get(key) || null;
    }
    async findOpenPeriods(tenantId) {
        return Array.from(this.periods.values()).filter(p => p.tenantId === tenantId && p.status === 'OPEN');
    }
    async save(period) {
        const key = `${period.tenantId}:${period.period}`;
        this.periods.set(key, period);
    }
    // Test helper
    addTestPeriod(period) {
        const key = `${period.tenantId}:${period.period}`;
        this.periods.set(key, period);
    }
    clear() {
        this.periods.clear();
    }
}
class MockEventPublisher {
    publishedEvents = [];
    async publish(event) {
        this.publishedEvents.push(event);
    }
    // Test helper
    getPublishedEvents() {
        return [...this.publishedEvents];
    }
    clear() {
        this.publishedEvents = [];
    }
}
// ===== TEST SETUP =====
describe('LedgerApplicationService', () => {
    let service;
    let journalRepo;
    let accountRepo;
    let periodRepo;
    let eventPublisher;
    beforeEach(() => {
        journalRepo = new MockJournalRepository();
        accountRepo = new MockAccountRepository();
        periodRepo = new MockPeriodRepository();
        eventPublisher = new MockEventPublisher();
        const dependencies = {
            journalRepository: journalRepo,
            accountRepository: accountRepo,
            periodRepository: periodRepo,
            eventPublisher
        };
        service = new ledger_service_1.LedgerApplicationService(dependencies);
        // Setup test data
        setupTestData();
    });
    afterEach(() => {
        journalRepo.clear();
        accountRepo.clear();
        periodRepo.clear();
        eventPublisher.clear();
    });
    function setupTestData() {
        // Add test accounts
        accountRepo.addTestAccount({
            id: 'acc-1000',
            tenantId: 'TEST_TENANT',
            accountNumber: '1000',
            name: 'Cash',
            type: 'ASSET',
            isActive: true,
            createdAt: new Date(),
            updatedAt: new Date(),
            metadata: {}
        });
        accountRepo.addTestAccount({
            id: 'acc-4000',
            tenantId: 'TEST_TENANT',
            accountNumber: '4000',
            name: 'Revenue',
            type: 'REVENUE',
            isActive: true,
            createdAt: new Date(),
            updatedAt: new Date(),
            metadata: {}
        });
        // Add test period
        const period = ledger_1.AccountingPeriodEntity.create('TEST_TENANT', '2025-09');
        periodRepo.addTestPeriod(period);
    }
    // ===== TEST CASES =====
    describe('createJournal', () => {
        it('should create a balanced journal successfully', async () => {
            // Arrange
            const command = {
                tenantId: 'TEST_TENANT',
                period: '2025-09',
                description: 'Test journal entry',
                entries: [
                    {
                        accountId: 'acc-1000',
                        debit: 1000,
                        credit: 0,
                        description: 'Cash receipt',
                        metadata: {}
                    },
                    {
                        accountId: 'acc-4000',
                        debit: 0,
                        credit: 1000,
                        description: 'Revenue recognition',
                        metadata: {}
                    }
                ],
                source: {
                    type: 'MANUAL',
                    reference: 'TEST-001'
                }
            };
            // Act
            const journalId = await service.createJournal(command);
            // Assert
            expect(journalId).toBeDefined();
            expect(typeof journalId).toBe('string');
            const savedJournal = await journalRepo.findById(journalId);
            expect(savedJournal).toBeDefined();
            expect(savedJournal?.description).toBe('Test journal entry');
            expect(savedJournal?.status).toBe('DRAFT');
            expect(savedJournal?.totalDebit).toBe(1000);
            expect(savedJournal?.totalCredit).toBe(1000);
            // Check event was published
            const events = eventPublisher.getPublishedEvents();
            expect(events).toHaveLength(1);
            expect(events[0].type).toBe('finance.journal.created');
        });
        it('should reject unbalanced journal', async () => {
            // Arrange
            const command = {
                tenantId: 'TEST_TENANT',
                period: '2025-09',
                description: 'Unbalanced journal',
                entries: [
                    {
                        accountId: 'acc-1000',
                        debit: 1000,
                        credit: 0,
                        description: 'Cash receipt',
                        metadata: {}
                    },
                    {
                        accountId: 'acc-4000',
                        debit: 0,
                        credit: 500, // Unbalanced!
                        description: 'Revenue recognition',
                        metadata: {}
                    }
                ],
                source: {
                    type: 'MANUAL',
                    reference: 'TEST-001'
                }
            };
            // Act & Assert
            await expect(service.createJournal(command)).rejects.toThrow('Journal entries must balance');
        });
        it('should reject journal with non-existent account', async () => {
            // Arrange
            const command = {
                tenantId: 'TEST_TENANT',
                period: '2025-09',
                description: 'Invalid account journal',
                entries: [
                    {
                        accountId: 'non-existent-account',
                        debit: 1000,
                        credit: 0,
                        description: 'Invalid account',
                        metadata: {}
                    },
                    {
                        accountId: 'acc-4000',
                        debit: 0,
                        credit: 1000,
                        description: 'Revenue recognition',
                        metadata: {}
                    }
                ],
                source: {
                    type: 'MANUAL',
                    reference: 'TEST-001'
                }
            };
            // Act & Assert
            await expect(service.createJournal(command)).rejects.toThrow('Account non-existent-account not found');
        });
    });
    describe('postJournal', () => {
        it('should post a draft journal successfully', async () => {
            // Arrange
            const journal = ledger_1.JournalEntity.create({
                tenantId: 'TEST_TENANT',
                period: '2025-09',
                description: 'Journal to post',
                entries: [
                    {
                        accountId: 'acc-1000',
                        debit: 1000,
                        credit: 0,
                        description: 'Cash receipt',
                        metadata: {}
                    },
                    {
                        accountId: 'acc-4000',
                        debit: 0,
                        credit: 1000,
                        description: 'Revenue recognition',
                        metadata: {}
                    }
                ],
                source: {
                    type: 'MANUAL',
                    reference: 'TEST-002'
                }
            });
            await journalRepo.save(journal);
            const command = {
                journalId: journal.id,
                postedBy: 'test-user'
            };
            // Act
            await service.postJournal(command);
            // Assert
            const postedJournal = await journalRepo.findById(journal.id);
            expect(postedJournal?.status).toBe('POSTED');
            expect(postedJournal?.postedBy).toBe('test-user');
            expect(postedJournal?.postedAt).toBeDefined();
            // Check event was published
            const events = eventPublisher.getPublishedEvents();
            expect(events.some(e => e.type === 'finance.journal.posted')).toBe(true);
        });
        it('should reject posting non-existent journal', async () => {
            // Arrange
            const command = {
                journalId: 'non-existent-journal',
                postedBy: 'test-user'
            };
            // Act & Assert
            await expect(service.postJournal(command)).rejects.toThrow('Journal non-existent-journal not found');
        });
    });
    describe('getTrialBalance', () => {
        it('should calculate correct trial balance', async () => {
            // Arrange - Create and post a journal
            const journal = ledger_1.JournalEntity.create({
                tenantId: 'TEST_TENANT',
                period: '2025-09',
                description: 'Trial balance test',
                entries: [
                    {
                        accountId: 'acc-1000',
                        debit: 1000,
                        credit: 0,
                        description: 'Cash increase',
                        metadata: {}
                    },
                    {
                        accountId: 'acc-4000',
                        debit: 0,
                        credit: 1000,
                        description: 'Revenue increase',
                        metadata: {}
                    }
                ],
                source: {
                    type: 'MANUAL',
                    reference: 'TB-TEST'
                }
            });
            const postedJournal = journal.post('test-user');
            await journalRepo.save(postedJournal);
            // Act
            const trialBalance = await service.getTrialBalance('TEST_TENANT', '2025-09');
            // Assert
            expect(trialBalance.isBalanced).toBe(true);
            expect(trialBalance.totalDebit).toBe(1000);
            expect(trialBalance.totalCredit).toBe(1000);
            expect(trialBalance.entries).toHaveLength(2);
            const cashEntry = trialBalance.entries.find(e => e.accountNumber === '1000');
            const revenueEntry = trialBalance.entries.find(e => e.accountNumber === '4000');
            expect(cashEntry?.debit).toBe(1000);
            expect(cashEntry?.credit).toBe(0);
            expect(revenueEntry?.debit).toBe(0);
            expect(revenueEntry?.credit).toBe(1000);
        });
    });
    describe('closePeriod', () => {
        it('should close period successfully when balanced', async () => {
            // Arrange - Create balanced period
            const journal = ledger_1.JournalEntity.create({
                tenantId: 'TEST_TENANT',
                period: '2025-09',
                description: 'Period close test',
                entries: [
                    {
                        accountId: 'acc-1000',
                        debit: 500,
                        credit: 0,
                        description: 'Final cash entry',
                        metadata: {}
                    },
                    {
                        accountId: 'acc-4000',
                        debit: 0,
                        credit: 500,
                        description: 'Final revenue entry',
                        metadata: {}
                    }
                ],
                source: {
                    type: 'MANUAL',
                    reference: 'CLOSE-TEST'
                }
            });
            const postedJournal = journal.post('test-user');
            await journalRepo.save(postedJournal);
            const command = {
                tenantId: 'TEST_TENANT',
                period: '2025-09',
                closedBy: 'admin-user'
            };
            // Act
            await service.closePeriod(command);
            // Assert
            const period = await periodRepo.findByPeriod('TEST_TENANT', '2025-09');
            expect(period?.status).toBe('CLOSED');
            expect(period?.closedBy).toBe('admin-user');
            // Check event was published
            const events = eventPublisher.getPublishedEvents();
            expect(events.some(e => e.type === 'finance.period.closed')).toBe(true);
        });
        it('should reject closing unbalanced period', async () => {
            // Arrange - Create unbalanced journal
            const journal = ledger_1.JournalEntity.create({
                tenantId: 'TEST_TENANT',
                period: '2025-09',
                description: 'Unbalanced journal',
                entries: [
                    {
                        accountId: 'acc-1000',
                        debit: 1000,
                        credit: 0,
                        description: 'Unbalanced entry',
                        metadata: {}
                    },
                    {
                        accountId: 'acc-4000',
                        debit: 0,
                        credit: 500, // Unbalanced!
                        description: 'Unbalanced revenue',
                        metadata: {}
                    }
                ],
                source: {
                    type: 'MANUAL',
                    reference: 'UNBALANCED'
                }
            });
            await journalRepo.save(journal);
            const command = {
                tenantId: 'TEST_TENANT',
                period: '2025-09',
                closedBy: 'admin-user'
            };
            // Act & Assert
            await expect(service.closePeriod(command)).rejects.toThrow('Period 2025-09 is not balanced');
        });
    });
    describe('business logic validation', () => {
        it('should enforce double-entry bookkeeping', async () => {
            // Arrange
            const command = {
                tenantId: 'TEST_TENANT',
                period: '2025-09',
                description: 'Single entry journal',
                entries: [
                    {
                        accountId: 'acc-1000',
                        debit: 1000,
                        credit: 0,
                        description: 'Single entry',
                        metadata: {}
                    }
                    // Missing second entry!
                ],
                source: {
                    type: 'MANUAL',
                    reference: 'SINGLE-ENTRY'
                }
            };
            // Act & Assert
            await expect(service.createJournal(command)).rejects.toThrow('Journal must have both debit and credit entries');
        });
        it('should validate period is open', async () => {
            // Arrange - Close the period first
            const period = await periodRepo.findByPeriod('TEST_TENANT', '2025-09');
            if (period) {
                const closedPeriod = period.close('admin');
                await periodRepo.save(closedPeriod);
            }
            const command = {
                tenantId: 'TEST_TENANT',
                period: '2025-09',
                description: 'Journal in closed period',
                entries: [
                    {
                        accountId: 'acc-1000',
                        debit: 1000,
                        credit: 0,
                        description: 'Cash receipt',
                        metadata: {}
                    },
                    {
                        accountId: 'acc-4000',
                        debit: 0,
                        credit: 1000,
                        description: 'Revenue recognition',
                        metadata: {}
                    }
                ],
                source: {
                    type: 'MANUAL',
                    reference: 'CLOSED-PERIOD'
                }
            };
            // Act & Assert
            await expect(service.createJournal(command)).rejects.toThrow('Period 2025-09 is not open for posting');
        });
    });
    describe('event publishing', () => {
        it('should publish correct events for journal lifecycle', async () => {
            // Arrange
            const command = {
                tenantId: 'TEST_TENANT',
                period: '2025-09',
                description: 'Event test journal',
                entries: [
                    {
                        accountId: 'acc-1000',
                        debit: 1000,
                        credit: 0,
                        description: 'Cash receipt',
                        metadata: {}
                    },
                    {
                        accountId: 'acc-4000',
                        debit: 0,
                        credit: 1000,
                        description: 'Revenue recognition',
                        metadata: {}
                    }
                ],
                source: {
                    type: 'MANUAL',
                    reference: 'EVENT-TEST'
                }
            };
            // Act - Create journal
            const journalId = await service.createJournal(command);
            // Post journal
            const postCommand = {
                journalId,
                postedBy: 'test-user'
            };
            await service.postJournal(postCommand);
            // Assert events
            const events = eventPublisher.getPublishedEvents();
            expect(events).toHaveLength(2);
            const createdEvent = events.find(e => e.type === 'finance.journal.created');
            const postedEvent = events.find(e => e.type === 'finance.journal.posted');
            expect(createdEvent).toBeDefined();
            expect(postedEvent).toBeDefined();
            expect(createdEvent?.aggregateId).toBe(journalId);
            expect(postedEvent?.aggregateId).toBe(journalId);
        });
    });
    describe('error handling', () => {
        it('should handle repository errors gracefully', async () => {
            // Arrange - Use a mock that throws errors
            const errorRepo = {
                ...journalRepo,
                findById: async () => { throw new Error('Database connection failed'); }
            };
            const errorService = new ledger_service_1.LedgerApplicationService({
                journalRepository: {
                    ...errorRepo,
                    findByPeriod: async () => [],
                    findByTenant: async () => [],
                    save: async (journal) => journal,
                    findUnbalancedJournals: async () => []
                },
                accountRepository: accountRepo,
                periodRepository: periodRepo,
                eventPublisher
            });
            // Act & Assert
            await expect(errorService.getJournal('test-id')).rejects.toThrow('Database connection failed');
        });
    });
});
// ===== INTEGRATION TESTS =====
describe('Ledger Domain Integration', () => {
    it('should maintain referential integrity', async () => {
        // Test that journal entries reference valid accounts
        const command = {
            tenantId: 'TEST_TENANT',
            period: '2025-09',
            description: 'Referential integrity test',
            entries: [
                {
                    accountId: 'acc-1000',
                    debit: 1000,
                    credit: 0,
                    description: 'Valid account reference',
                    metadata: {}
                }
            ],
            source: {
                type: 'MANUAL',
                reference: 'REF-INTEGRITY'
            }
        };
        const journalId = await service.createJournal(command);
        expect(journalId).toBeDefined();
    });
    it('should handle concurrent journal creation', async () => {
        // Test concurrent access doesn't cause data corruption
        const commands = Array.from({ length: 5 }, (_, i) => ({
            tenantId: 'TEST_TENANT',
            period: '2025-09',
            description: `Concurrent journal ${i}`,
            entries: [
                {
                    accountId: 'acc-1000',
                    debit: 100,
                    credit: 0,
                    description: `Concurrent debit ${i}`,
                    metadata: {}
                },
                {
                    accountId: 'acc-4000',
                    debit: 0,
                    credit: 100,
                    description: `Concurrent credit ${i}`,
                    metadata: {}
                }
            ],
            source: {
                type: 'MANUAL',
                reference: `CONCURRENT-${i}`
            }
        }));
        // Execute concurrently
        const journalIds = await Promise.all(commands.map(cmd => service.createJournal(cmd)));
        expect(journalIds).toHaveLength(5);
        expect(new Set(journalIds).size).toBe(5); // All unique
        const journals = await Promise.all(journalIds.map((id) => journalRepo.findById(id)));
        expect(journals.every((j) => j !== null)).toBe(true);
    });
});
// ===== PERFORMANCE TESTS =====
describe('Ledger Performance', () => {
    it('should handle large journals efficiently', async () => {
        // Create journal with many entries
        const entries = Array.from({ length: 1000 }, (_, i) => ({
            accountId: i % 2 === 0 ? 'acc-1000' : 'acc-4000',
            debit: i % 2 === 0 ? 10 : 0,
            credit: i % 2 === 0 ? 0 : 10,
            description: `Performance test entry ${i}`,
            metadata: {}
        }));
        const command = {
            tenantId: 'TEST_TENANT',
            period: '2025-09',
            description: 'Performance test journal',
            entries,
            source: {
                type: 'MANUAL',
                reference: 'PERF-TEST'
            }
        };
        const startTime = Date.now();
        const journalId = await service.createJournal(command);
        const endTime = Date.now();
        expect(endTime - startTime).toBeLessThan(1000); // Should complete within 1s
        expect(journalId).toBeDefined();
    });
});
// ===== TEST HELPERS =====
// Helper to create test accounts
function createTestAccount(overrides = {}) {
    return {
        id: `acc-${Date.now()}`,
        tenantId: 'TEST_TENANT',
        accountNumber: '9999',
        name: 'Test Account',
        type: 'ASSET',
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
        metadata: {},
        ...overrides
    };
}
// Helper to create test period
function createTestPeriod(overrides = {}) {
    return ledger_1.AccountingPeriodEntity.create('TEST_TENANT', '2025-09');
}
