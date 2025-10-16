export enum WorkflowExecutionStatus {
  SUCCESS = 'SUCCESS',
  FAILED = 'FAILED',
  PENDING = 'PENDING',
  RUNNING = 'RUNNING'
}

export class WorkflowRule {
  constructor(
    public readonly id: string,
    public readonly triggerEntity: string,
    public readonly triggerAction: string,
    public readonly targetEntity: string,
    public readonly targetAction: string,
    public readonly tenantId: string,
    public readonly condition?: string,
    public readonly active: boolean = true,
    public readonly createdAt: Date = new Date(),
    public readonly updatedAt: Date = new Date()
  ) {}

  static create(data: {
    triggerEntity: string
    triggerAction: string
    targetEntity: string
    targetAction: string
    condition?: string
    active?: boolean
    tenantId: string
  }): WorkflowRule {
    return new WorkflowRule(
      '', // ID wird generiert
      data.triggerEntity,
      data.triggerAction,
      data.targetEntity,
      data.targetAction,
      data.tenantId,
      data.condition,
      data.active ?? true
    )
  }

  activate(): WorkflowRule {
    return new WorkflowRule(
      this.id,
      this.triggerEntity,
      this.triggerAction,
      this.targetEntity,
      this.targetAction,
      this.tenantId,
      this.condition,
      true,
      this.createdAt,
      new Date()
    )
  }

  deactivate(): WorkflowRule {
    return new WorkflowRule(
      this.id,
      this.triggerEntity,
      this.triggerAction,
      this.targetEntity,
      this.targetAction,
      this.tenantId,
      this.condition,
      false,
      this.createdAt,
      new Date()
    )
  }

  matches(triggerEntity: string, triggerAction: string): boolean {
    return this.active &&
           this.triggerEntity === triggerEntity &&
           this.triggerAction === triggerAction
  }

  evaluateCondition(data?: any): boolean {
    if (!this.condition) return true

    // Einfache Bedingungsauswertung - in Realität komplexer
    try {
      // TODO: Implementiere echte Bedingungsauswertung
      return true
    } catch {
      return false
    }
  }
}

export class WorkflowExecution {
  constructor(
    public readonly id: string,
    public readonly ruleId: string,
    public readonly triggerEntity: string,
    public readonly triggerAction: string,
    public readonly targetEntity: string,
    public readonly targetAction: string,
    public readonly status: WorkflowExecutionStatus,
    public readonly startedAt: Date,
    public readonly actorId: string,
    public readonly tenantId: string,
    public readonly completedAt?: Date,
    public readonly errorMessage?: string,
    public readonly createdAt: Date = new Date()
  ) {}

  static create(data: {
    ruleId: string
    triggerEntity: string
    triggerAction: string
    targetEntity: string
    targetAction: string
    actorId: string
    tenantId: string
  }): WorkflowExecution {
    return new WorkflowExecution(
      '', // ID wird generiert
      data.ruleId,
      data.triggerEntity,
      data.triggerAction,
      data.targetEntity,
      data.targetAction,
      WorkflowExecutionStatus.PENDING,
      new Date(),
      data.actorId,
      data.tenantId,
      undefined,
      undefined
    )
  }

  start(): WorkflowExecution {
    return new WorkflowExecution(
      this.id,
      this.ruleId,
      this.triggerEntity,
      this.triggerAction,
      this.targetEntity,
      this.targetAction,
      WorkflowExecutionStatus.RUNNING,
      this.startedAt,
      this.actorId,
      this.tenantId,
      undefined,
      undefined,
      this.createdAt
    )
  }

  succeed(): WorkflowExecution {
    return new WorkflowExecution(
      this.id,
      this.ruleId,
      this.triggerEntity,
      this.triggerAction,
      this.targetEntity,
      this.targetAction,
      WorkflowExecutionStatus.SUCCESS,
      this.startedAt,
      this.actorId,
      this.tenantId,
      new Date(),
      undefined,
      this.createdAt
    )
  }

  fail(errorMessage: string): WorkflowExecution {
    return new WorkflowExecution(
      this.id,
      this.ruleId,
      this.triggerEntity,
      this.triggerAction,
      this.targetEntity,
      this.targetAction,
      WorkflowExecutionStatus.FAILED,
      this.startedAt,
      this.actorId,
      this.tenantId,
      new Date(),
      errorMessage,
      this.createdAt
    )
  }

  isCompleted(): boolean {
    return this.status === WorkflowExecutionStatus.SUCCESS ||
           this.status === WorkflowExecutionStatus.FAILED
  }

  getDuration(): number | null {
    if (!this.completedAt) return null
    return this.completedAt.getTime() - this.startedAt.getTime()
  }
}

export class AuditLog {
  constructor(
    public readonly id: string,
    public readonly actorId: string,
    public readonly entity: string,
    public readonly entityId: string,
    public readonly action: string,
    public readonly tenantId: string,
    public readonly before?: any,
    public readonly after?: any,
    public readonly timestamp: Date = new Date(),
    public readonly ipAddress?: string,
    public readonly userAgent?: string
  ) {}

  static create(data: {
    actorId: string
    entity: string
    entityId: string
    action: string
    before?: any
    after?: any
    tenantId: string
    ipAddress?: string
    userAgent?: string
  }): AuditLog {
    return new AuditLog(
      '', // ID wird generiert
      data.actorId,
      data.entity,
      data.entityId,
      data.action,
      data.tenantId,
      data.before,
      data.after,
      new Date(),
      data.ipAddress,
      data.userAgent
    )
  }

  hasChanges(): boolean {
    return this.before !== undefined || this.after !== undefined
  }

  getChangeSummary(): string {
    if (!this.hasChanges()) return 'Keine Änderungen'

    const changes: string[] = []

    if (this.before && this.after) {
      // Vergleiche before und after
      // TODO: Implementiere detaillierten Vergleich
      changes.push('Daten aktualisiert')
    } else if (this.after) {
      changes.push('Neuer Datensatz erstellt')
    } else if (this.before) {
      changes.push('Datensatz gelöscht')
    }

    return changes.join(', ')
  }
}