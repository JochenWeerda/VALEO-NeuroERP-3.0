/* E2E-style smoke for Audit Assist using in-memory repos */
/* eslint-disable no-console */
import { AuditAssistApplicationService } from '../../../finance/src/services/audit-assist-service'

type AuditTrailEntry = {
  id: string
  tenantId: string
  timestamp: Date
  documentRefs: string[]
  meta?: Record<string, any>
}

type AuditDocument = {
  ref: string
  contentType: string
  bytes: Uint8Array
}

class InMemoryAuditTrailRepository {
  private entries: AuditTrailEntry[] = []
  seed(entries: AuditTrailEntry[]) {
    this.entries = entries
  }
  async findByPeriod(tenantId: string, period: { from: string; to: string }): Promise<AuditTrailEntry[]> {
    const from = new Date(period.from).getTime()
    const to = new Date(period.to).getTime()
    return this.entries.filter((e) => e.tenantId === tenantId && e.timestamp.getTime() >= from && e.timestamp.getTime() <= to)
  }
}

class InMemoryDocumentRepository {
  private docs = new Map<string, AuditDocument>()
  seed(docs: AuditDocument[]) {
    docs.forEach((d) => this.docs.set(d.ref, d))
  }
  async findByRef(ref: string): Promise<AuditDocument | null> {
    return this.docs.get(ref) || null
  }
}

class InMemoryAIDecisionRepository {
  async recordAIDecision(): Promise<void> {
    /* noop */
  }
}

class NoopComplianceEngine {
  async checkCompliance(): Promise<any> {
    return { standard: 'GOBD', status: 'PASS', findings: [] }
  }
}

class NoopEventPublisher {
  async publish(): Promise<void> {
    /* noop */
  }
}

async function main() {
  const auditTrailRepo = new InMemoryAuditTrailRepository()
  const documentRepo = new InMemoryDocumentRepository()
  const aiDecisionRepo = new InMemoryAIDecisionRepository()
  const complianceEngine = new NoopComplianceEngine()
  const eventPublisher = new NoopEventPublisher()

  const service = new AuditAssistApplicationService(
    // @ts-expect-error minimal interface compat for test
    auditTrailRepo,
    // @ts-expect-error minimal interface compat for test
    documentRepo,
    // @ts-expect-error minimal interface compat for test
    aiDecisionRepo,
    // @ts-expect-error minimal interface compat for test
    complianceEngine,
    // @ts-expect-error minimal interface compat for test
    eventPublisher
  )

  auditTrailRepo.seed([
    {
      id: 'a1',
      tenantId: 'default',
      timestamp: new Date(),
      documentRefs: ['doc-1'],
      meta: { userId: 'tester' }
    }
  ])
  documentRepo.seed([
    {
      ref: 'doc-1',
      contentType: 'application/pdf',
      bytes: new Uint8Array([1, 2, 3])
    }
  ])

  const result = await service.generateAuditPackage({
    tenantId: 'default',
    period: { from: new Date(Date.now() - 24 * 3600 * 1000).toISOString(), to: new Date().toISOString() },
    includeDocuments: true,
    standards: ['GOBD']
  } as any)

  if (!result || (result as any).isFailure) {
    console.error('Audit E2E failed', result)
    process.exit(1)
  }
  console.log('✅ Audit E2E success')
}

main().catch((err) => {
  console.error('Audit E2E error', err)
  process.exit(1)
})


