import { publishEvent } from '../../infra/messaging/publisher';
import { createCapa } from './capa-service';
import { createNonConformity, assignNonConformity } from './nc-service';
import { analyzeSample } from './sample-service';
import { NonConformity } from '../entities/non-conformity';
import pino from 'pino';

const logger = pino({ name: 'workflow-automation' });

/**
 * Workflow Rules Configuration
 */
interface WorkflowRule {
  id: string;
  name: string;
  condition: (context: any) => boolean;
  action: (context: any) => Promise<void>;
  enabled: boolean;
}

const workflowRules: WorkflowRule[] = [
  {
    id: 'auto-capa-critical-nc',
    name: 'Automatische CAPA-Erstellung bei Critical NC',
    condition: (nc: NonConformity) => nc.severity === 'Critical',
    action: async (nc: NonConformity) => {
      logger.info({ ncId: nc.id }, 'Auto-creating CAPA for critical NC');
      
      await createCapa({
        tenantId: nc.tenantId,
        linkedNcIds: [nc.id!],
        type: 'Corrective',
        title: `Automatische CAPA für Critical NC: ${nc.title}`,
        description: `Automatisch generierte CAPA zur Behebung der kritischen Abweichung.\n\nOriginal NC: ${nc.description}`,
        action: 'Sofortige Ursachenanalyse und Korrekturmaßnahmen erforderlich',
        responsibleUserId: nc.assignedTo ?? 'quality-manager',
        responsibleDepartment: 'Quality Management',
        dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 Tage
      } as any, 'system-automation');
    },
    enabled: true,
  },
  {
    id: 'auto-assign-nc-by-type',
    name: 'Automatische NC-Zuweisung nach Typ',
    condition: (nc: NonConformity) => !nc.assignedTo,
    action: async (nc: NonConformity) => {
      const assignmentMap: Record<string, string> = {
        'SpecOut': 'quality-lab-lead',
        'Contamination': 'hygiene-manager',
        'ProcessDeviation': 'production-manager',
        'Documentation': 'documentation-lead',
        'PackagingDefect': 'packaging-manager',
      };

      const assignee = assignmentMap[nc.type] || 'quality-manager';
      
      logger.info({ ncId: nc.id, assignee }, 'Auto-assigning NC');
      await assignNonConformity(nc.tenantId, nc.id!, assignee);
    },
    enabled: true,
  },
  {
    id: 'auto-escalate-overdue-capa',
    name: 'Automatische Eskalation überfälliger CAPAs',
    condition: (capa: any) => {
      const now = new Date();
      const dueDate = new Date(capa.dueDate);
      const daysDiff = Math.floor((now.getTime() - dueDate.getTime()) / (1000 * 60 * 60 * 24));
      return daysDiff > 3 && !capa.escalated && (capa.status === 'Open' || capa.status === 'InProgress');
    },
    action: async (capa: any) => {
      logger.warn({ capaId: capa.id }, 'Auto-escalating overdue CAPA');
      
      await publishEvent('capa.auto-escalated', {
        tenantId: capa.tenantId,
        capaId: capa.id,
        capaNumber: capa.capaNumber,
        daysOverdue: Math.floor((new Date().getTime() - new Date(capa.dueDate).getTime()) / (1000 * 60 * 60 * 24)),
        escalatedTo: 'quality-director',
        reason: 'Automatische Eskalation: CAPA mehr als 3 Tage überfällig',
        occurredAt: new Date().toISOString(),
      });
    },
    enabled: true,
  },
];

/**
 * Execute workflow rules for a given context
 */
export async function executeWorkflowRules(entityType: string, entity: any): Promise<void> {
  const relevantRules = workflowRules.filter(rule => rule.enabled);

  for (const rule of relevantRules) {
    try {
      if (rule.condition(entity)) {
        logger.info({ ruleId: rule.id, entityType }, 'Executing workflow rule');
        await rule.action(entity);
      }
    } catch (error) {
      logger.error({ error, ruleId: rule.id, entityType }, 'Workflow rule execution failed');
    }
  }
}

/**
 * Batch Quality Check Automation
 * Automatisch Proben erstellen und analysieren bei Batch-Completion
 */
export async function automateBatchQualityCheck(batchId: string, tenantId: string): Promise<void> {
  logger.info({ batchId, tenantId }, 'Automating batch quality check');

  // Hier würde die Logik für automatische Sample-Erstellung kommen
  // basierend auf Quality Plan Rules
  
  await publishEvent('batch.quality-check.automated', {
    tenantId,
    batchId,
    occurredAt: new Date().toISOString(),
  });
}

/**
 * Smart NC Creation from Failed Samples
 * Automatisch NC erstellen wenn Sample failed
 */
export async function autoCreateNcFromFailedSample(
  sampleId: string,
  tenantId: string,
  failedAnalytes: Array<{ analyte: string; value: number; limit: { min?: number; max?: number } }>
): Promise<void> {
  logger.info({ sampleId, tenantId }, 'Auto-creating NC from failed sample');

  const description = failedAnalytes.map(a => 
    `${a.analyte}: ${a.value} (Spec: ${a.limit.min ?? 'N/A'} - ${a.limit.max ?? 'N/A'})`
  ).join('\n');

  await createNonConformity({
    tenantId,
    sampleId,
    type: 'SpecOut',
    severity: failedAnalytes.length > 2 ? 'Major' : 'Minor',
    title: 'Automatisch: Probe außerhalb Spezifikation',
    description: `Folgende Analyten außerhalb Spezifikation:\n${description}`,
    detectedAt: new Date().toISOString(),
    detectedBy: 'system-automation',
  } as any, 'system-automation');
}

/**
 * Recurring CAPA Effectiveness Check
 * Automatische Überprüfung der CAPA-Wirksamkeit nach X Tagen
 */
export async function scheduleCapaEffectivenessCheck(capaId: string, tenantId: string, daysAfterImplementation: number = 30): Promise<void> {
  logger.info({ capaId, tenantId, daysAfterImplementation }, 'Scheduling CAPA effectiveness check');

  await publishEvent('capa.effectiveness-check.scheduled', {
    tenantId,
    capaId,
    scheduledFor: new Date(Date.now() + daysAfterImplementation * 24 * 60 * 60 * 1000).toISOString(),
    occurredAt: new Date().toISOString(),
  });
}

/**
 * Quality Trend Alert
 * Überwacht Trends und warnt bei Verschlechterung
 */
export async function checkQualityTrends(tenantId: string): Promise<void> {
  // Wird vom ML-Service aufgerufen
  logger.info({ tenantId }, 'Checking quality trends');
  
  // Placeholder für Trend-Analyse
  // Wird von ml-predictions-service.ts implementiert
}

