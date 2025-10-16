import { inject, injectable } from 'inversify'
import { PurchaseOrderService } from './purchaseOrder.service'
import { AuditService } from './audit.service'

export interface WorkflowTransition {
  fromEntity: string
  fromId: string
  toEntity: string
  action: string
  actorId: string
  data?: any
}

export interface WorkflowRule {
  triggerEntity: string
  triggerAction: string
  targetEntity: string
  targetAction: string
  condition?: (data: any) => boolean
}

@injectable()
export class WorkflowService {
  private rules: WorkflowRule[] = [
    // Anfrage → Angebot: Wenn Anfrage freigegeben wird
    {
      triggerEntity: 'Anfrage',
      triggerAction: 'FREIGEGEBEN',
      targetEntity: 'Anfrage',
      targetAction: 'ANGEBOTSPHASE'
    },

    // Angebot → Bestellung: Wenn Angebot genehmigt wird
    {
      triggerEntity: 'Angebot',
      triggerAction: 'GENEHMIGT',
      targetEntity: 'Bestellung',
      targetAction: 'CREATE_FROM_ANGEBOT'
    },

    // Bestellung → Auftragsbestätigung: Automatisch nach Freigabe
    {
      triggerEntity: 'Bestellung',
      triggerAction: 'FREIGEGEBEN',
      targetEntity: 'Auftragsbestaetigung',
      targetAction: 'CREATE_FROM_BESTELLUNG'
    },

    // Bestellung → Anlieferavis: Automatisch nach Freigabe
    {
      triggerEntity: 'Bestellung',
      triggerAction: 'FREIGEGEBEN',
      targetEntity: 'Anlieferavis',
      targetAction: 'CREATE_FROM_BESTELLUNG'
    },

    // Wareneingang → Rechnung: Bei vollständigem WE
    {
      triggerEntity: 'Wareneingang',
      triggerAction: 'GEBUCHT',
      targetEntity: 'Rechnungseingang',
      targetAction: 'CREATE_FROM_WE',
      condition: (data) => data.status === 'GEBUCHT'
    },

    // Bestellung → Rechnung: Bei vollständig gelieferten Positionen
    {
      triggerEntity: 'Bestellung',
      triggerAction: 'VOLLGELIEFERT',
      targetEntity: 'Rechnungseingang',
      targetAction: 'CREATE_FROM_BESTELLUNG'
    }
  ]

  constructor(
    @inject('PurchaseOrderService') private poService: PurchaseOrderService,
    @inject('AuditService') private auditService: AuditService
  ) {}

  async executeTransition(transition: WorkflowTransition): Promise<void> {
    const { fromEntity, fromId, toEntity, action, actorId, data } = transition

    // Finde passende Regel
    const rule = this.rules.find(r =>
      r.triggerEntity === fromEntity &&
      r.triggerAction === action &&
      (!r.condition || r.condition(data))
    )

    if (!rule) {
      console.log(`Keine Workflow-Regel gefunden für ${fromEntity}:${action}`)
      return
    }

    try {
      await this.executeTargetAction(rule, fromId, actorId, data)
      console.log(`Workflow ausgeführt: ${fromEntity} → ${toEntity}`)
    } catch (error) {
      console.error('Workflow-Fehler:', error)
      throw error
    }
  }

  private async executeTargetAction(
    rule: WorkflowRule,
    sourceId: string,
    actorId: string,
    data?: any
  ): Promise<void> {
    switch (rule.targetEntity) {
      case 'Anfrage':
        await this.handleAnfrageAction(rule.targetAction, sourceId, actorId, data)
        break
      case 'Bestellung':
        await this.handleBestellungAction(rule.targetAction, sourceId, actorId, data)
        break
      case 'Auftragsbestaetigung':
        await this.handleAuftragsbestaetigungAction(rule.targetAction, sourceId, actorId, data)
        break
      case 'Anlieferavis':
        await this.handleAnlieferavisAction(rule.targetAction, sourceId, actorId, data)
        break
      case 'Rechnungseingang':
        await this.handleRechnungseingangAction(rule.targetAction, sourceId, actorId, data)
        break
      default:
        console.log(`Unbekannte Ziel-Entität: ${rule.targetEntity}`)
    }
  }

  private async handleAnfrageAction(action: string, sourceId: string, actorId: string, data?: any): Promise<void> {
    // Anfrage-Status auf Angebotsphase setzen
    console.log(`Anfrage ${sourceId}: Status auf ANGEBOTSPHASE gesetzt`)
    // Hier würde die Anfrage-Service-Methode aufgerufen werden
  }

  private async handleBestellungAction(action: string, sourceId: string, actorId: string, data?: any): Promise<void> {
    if (action === 'CREATE_FROM_ANGEBOT') {
      // Bestellung aus Angebot erstellen
      console.log(`Bestellung aus Angebot ${sourceId} erstellen`)
      // Hier würde die Bestellung aus Angebotsdaten erstellt werden
    }
  }

  private async handleAuftragsbestaetigungAction(action: string, sourceId: string, actorId: string, data?: any): Promise<void> {
    if (action === 'CREATE_FROM_BESTELLUNG') {
      // Auftragsbestätigung aus Bestellung erstellen
      console.log(`Auftragsbestätigung für Bestellung ${sourceId} erstellen`)
      // Hier würde automatisch eine AB erstellt werden
    }
  }

  private async handleAnlieferavisAction(action: string, sourceId: string, actorId: string, data?: any): Promise<void> {
    if (action === 'CREATE_FROM_BESTELLUNG') {
      // Anlieferavis aus Bestellung erstellen
      console.log(`Anlieferavis für Bestellung ${sourceId} erstellen`)
      // Hier würde automatisch ein Avis erstellt werden
    }
  }

  private async handleRechnungseingangAction(action: string, sourceId: string, actorId: string, data?: any): Promise<void> {
    if (action === 'CREATE_FROM_WE') {
      // Rechnung aus Wareneingang erstellen
      console.log(`Rechnungseingang aus Wareneingang ${sourceId} erstellen`)
    } else if (action === 'CREATE_FROM_BESTELLUNG') {
      // Rechnung aus Bestellung erstellen
      console.log(`Rechnungseingang aus Bestellung ${sourceId} erstellen`)
    }
  }

  // Workflow-Regeln hinzufügen/entfernen
  addRule(rule: WorkflowRule): void {
    this.rules.push(rule)
  }

  removeRule(index: number): void {
    this.rules.splice(index, 1)
  }

  getRules(): WorkflowRule[] {
    return [...this.rules]
  }

  // Prüfen ob Transition erlaubt ist
  canExecuteTransition(transition: WorkflowTransition): boolean {
    const rule = this.rules.find(r =>
      r.triggerEntity === transition.fromEntity &&
      r.triggerAction === transition.action
    )
    return !!rule
  }
}