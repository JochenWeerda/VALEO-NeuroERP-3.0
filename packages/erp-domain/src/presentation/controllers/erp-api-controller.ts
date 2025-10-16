import { Router } from 'express'
import { AnfrageController } from './anfrage.controller'
import { AngebotController } from './angebot.controller'
import { SalesOfferController } from './sales-offer.controller'
import { AuftragsbestaetigungController } from './auftragsbestaetigung.controller'
import { AnlieferavisController } from './anlieferavis.controller'
import { RechnungseingangController } from './rechnungseingang.controller'
import { WorkflowRuleController } from './workflow-rule.controller'
import { WorkflowExecutionController } from './workflow-execution.controller'
import { AuditLogController } from './audit-log.controller'
import { AnfrageService } from '../../application/services/anfrage.service'
import { AngebotService } from '../../application/services/angebot.service'
import { SalesOfferService } from '../../application/services/sales-offer.service'
import { AuftragsbestaetigungService } from '../../application/services/auftragsbestaetigung.service'
import { AnlieferavisService } from '../../application/services/anlieferavis.service'
import { RechnungseingangService } from '../../application/services/rechnungseingang.service'
import { WorkflowRuleService } from '../../application/services/workflow-rule.service'
import { WorkflowExecutionService } from '../../application/services/workflow-execution.service'
import { AuditLogService } from '../../application/services/audit-log.service'
import { AnfragePostgresRepository } from '../../infrastructure/repositories/anfrage-postgres.repository'
import { AngebotPostgresRepository } from '../../infrastructure/repositories/angebot-postgres.repository'
import { SalesOfferPostgresRepository } from '../../infrastructure/repositories/sales-offer-postgres.repository'
import { AuftragsbestaetigungPostgresRepository } from '../../infrastructure/repositories/auftragsbestaetigung-postgres.repository'
import { AnlieferavisPostgresRepository } from '../../infrastructure/repositories/anlieferavis-postgres.repository'
import { RechnungseingangPostgresRepository } from '../../infrastructure/repositories/rechnungseingang-postgres.repository'
import { WorkflowRulePostgresRepository } from '../../infrastructure/repositories/workflow-rule-postgres.repository'
import { WorkflowExecutionPostgresRepository } from '../../infrastructure/repositories/workflow-execution-postgres.repository'
import { AuditLogPostgresRepository } from '../../infrastructure/repositories/audit-log-postgres.repository'
import { AuditService } from '../../application/services/audit.service'
import { WorkflowService } from '../../application/services/workflow.service'

export function createErpApiRouter(): Router {
  const router = Router()

  // TODO: Dependency Injection Container verwenden
  // Mock-Implementierungen für jetzt
  const mockPrisma = {} as any

  // Repositories
  const anfrageRepository = new AnfragePostgresRepository(mockPrisma)
  const angebotRepository = new AngebotPostgresRepository(mockPrisma)
  const salesOfferRepository = new SalesOfferPostgresRepository(mockPrisma)
  const auftragsbestaetigungRepository = new AuftragsbestaetigungPostgresRepository(mockPrisma)
  const anlieferavisRepository = new AnlieferavisPostgresRepository(mockPrisma)
  const rechnungseingangRepository = new RechnungseingangPostgresRepository(mockPrisma)
  const workflowRuleRepository = new WorkflowRulePostgresRepository(mockPrisma)
  const workflowExecutionRepository = new WorkflowExecutionPostgresRepository(mockPrisma)
  const auditLogRepository = new AuditLogPostgresRepository(mockPrisma)

  // Services
  const auditService = new AuditService()
  const workflowService = new WorkflowService()

  const anfrageService = new AnfrageService(
    anfrageRepository,
    auditService,
    workflowService
  )
  const angebotService = new AngebotService(
    angebotRepository,
    auditService,
    workflowService
  )
  const salesOfferService = new SalesOfferService(
    salesOfferRepository,
    auditService,
    workflowService
  )
  const auftragsbestaetigungService = new AuftragsbestaetigungService(
    auftragsbestaetigungRepository,
    auditService,
    workflowService
  )
  const anlieferavisService = new AnlieferavisService(
    anlieferavisRepository,
    auditService,
    workflowService
  )
  const rechnungseingangService = new RechnungseingangService(
    rechnungseingangRepository,
    auditService,
    workflowService
  )
  const workflowRuleService = new WorkflowRuleService(
    workflowRuleRepository,
    auditService
  )
  const workflowExecutionService = new WorkflowExecutionService(
    workflowExecutionRepository,
    auditService
  )
  const auditLogService = new AuditLogService(auditLogRepository)

  // Controllers
  const anfrageController = new AnfrageController(anfrageService)
  const angebotController = new AngebotController(angebotService)
  const salesOfferController = new SalesOfferController(salesOfferService)
  const auftragsbestaetigungController = new AuftragsbestaetigungController(auftragsbestaetigungService)
  const anlieferavisController = new AnlieferavisController(anlieferavisService)
  const rechnungseingangController = new RechnungseingangController(rechnungseingangService)
  const workflowRuleController = new WorkflowRuleController(workflowRuleService)
  const workflowExecutionController = new WorkflowExecutionController(workflowExecutionService)
  const auditLogController = new AuditLogController(auditLogService)

  // Anfrage-Routen
  router.post('/anfragen', (req, res) => anfrageController.createAnfrage(req, res))
  router.get('/anfragen', (req, res) => anfrageController.getAnfragen(req, res))
  router.get('/anfragen/:id', (req, res) => anfrageController.getAnfrage(req, res))
  router.put('/anfragen/:id', (req, res) => anfrageController.updateAnfrage(req, res))
  router.delete('/anfragen/:id', (req, res) => anfrageController.deleteAnfrage(req, res))
  router.post('/anfragen/:id/freigeben', (req, res) => anfrageController.freigebenAnfrage(req, res))
  router.get('/anfragen/ueberfaellig', (req, res) => anfrageController.getUeberfaelligeAnfragen(req, res))
  router.get('/anfragen/dringend', (req, res) => anfrageController.getDringendeAnfragen(req, res))

  // Angebot-Routen
  router.post('/angebote', (req, res) => angebotController.createAngebot(req, res))
  router.get('/angebote', (req, res) => angebotController.getAngebote(req, res))
  router.get('/angebote/:id', (req, res) => angebotController.getAngebot(req, res))
  router.put('/angebote/:id', (req, res) => angebotController.updateAngebot(req, res))
  router.delete('/angebote/:id', (req, res) => angebotController.deleteAngebot(req, res))
  router.post('/angebote/:id/pruefen', (req, res) => angebotController.pruefenAngebot(req, res))
  router.post('/angebote/:id/genehmigen', (req, res) => angebotController.genehmigenAngebot(req, res))
  router.post('/angebote/:id/ablehnen', (req, res) => angebotController.ablehnenAngebot(req, res))
  router.get('/angebote/anfrage/:anfrageId', (req, res) => angebotController.getAngeboteByAnfrage(req, res))
  router.get('/angebote/abgelaufen', (req, res) => angebotController.getAbgelaufeneAngebote(req, res))

  // SalesOffer-Routen
  router.post('/sales-offers', (req, res) => salesOfferController.createSalesOffer(req, res))
  router.post('/sales-offers/from-inquiry/:inquiryId', (req, res) => salesOfferController.createSalesOfferFromInquiry(req, res))
  router.get('/sales-offers', (req, res) => salesOfferController.getSalesOffers(req, res))
  router.get('/sales-offers/:id', (req, res) => salesOfferController.getSalesOffer(req, res))
  router.put('/sales-offers/:id', (req, res) => salesOfferController.updateSalesOffer(req, res))
  router.delete('/sales-offers/:id', (req, res) => salesOfferController.deleteSalesOffer(req, res))
  router.post('/sales-offers/:id/send', (req, res) => salesOfferController.sendSalesOffer(req, res))
  router.post('/sales-offers/:id/accept', (req, res) => salesOfferController.acceptSalesOffer(req, res))
  router.post('/sales-offers/:id/reject', (req, res) => salesOfferController.rejectSalesOffer(req, res))
  router.get('/sales-offers/inquiry/:inquiryId', (req, res) => salesOfferController.getSalesOffersByCustomerInquiry(req, res))
  router.get('/sales-offers/expired', (req, res) => salesOfferController.getExpiredSalesOffers(req, res))
  router.get('/sales-offers/valid', (req, res) => salesOfferController.getValidSalesOffers(req, res))

  // Auftragsbestätigung-Routen
  router.post('/auftragsbestaetigungen', (req, res) => auftragsbestaetigungController.createAuftragsbestaetigung(req, res))
  router.get('/auftragsbestaetigungen', (req, res) => auftragsbestaetigungController.getAuftragsbestaetigungen(req, res))
  router.get('/auftragsbestaetigungen/:id', (req, res) => auftragsbestaetigungController.getAuftragsbestaetigung(req, res))
  router.put('/auftragsbestaetigungen/:id', (req, res) => auftragsbestaetigungController.updateAuftragsbestaetigung(req, res))
  router.delete('/auftragsbestaetigungen/:id', (req, res) => auftragsbestaetigungController.deleteAuftragsbestaetigung(req, res))
  router.post('/auftragsbestaetigungen/:id/pruefen', (req, res) => auftragsbestaetigungController.pruefenAuftragsbestaetigung(req, res))
  router.post('/auftragsbestaetigungen/:id/bestaetigen', (req, res) => auftragsbestaetigungController.bestaetigenAuftragsbestaetigung(req, res))
  router.get('/auftragsbestaetigungen/bestellung/:bestellungId', (req, res) => auftragsbestaetigungController.getAuftragsbestaetigungByBestellung(req, res))
  router.get('/auftragsbestaetigungen/abweichungen', (req, res) => auftragsbestaetigungController.getAuftragsbestaetigungenMitAbweichungen(req, res))

  // Anlieferavis-Routen
  router.post('/anlieferavise', (req, res) => anlieferavisController.createAnlieferavis(req, res))
  router.get('/anlieferavise', (req, res) => anlieferavisController.getAnlieferavise(req, res))
  router.get('/anlieferavise/:id', (req, res) => anlieferavisController.getAnlieferavis(req, res))
  router.put('/anlieferavise/:id', (req, res) => anlieferavisController.updateAnlieferavis(req, res))
  router.delete('/anlieferavise/:id', (req, res) => anlieferavisController.deleteAnlieferavis(req, res))
  router.post('/anlieferavise/:id/bestaetigen', (req, res) => anlieferavisController.bestaetigenAnlieferavis(req, res))
  router.post('/anlieferavise/:id/stornieren', (req, res) => anlieferavisController.stornierenAnlieferavis(req, res))
  router.get('/anlieferavise/bestellung/:bestellungId', (req, res) => anlieferavisController.getAnlieferavisByBestellung(req, res))
  router.get('/anlieferavise/ueberfaellig', (req, res) => anlieferavisController.getUeberfaelligeAnlieferavise(req, res))

  // Rechnungseingang-Routen
  router.post('/rechnungseingaenge', (req, res) => rechnungseingangController.createRechnungseingang(req, res))
  router.get('/rechnungseingaenge', (req, res) => rechnungseingangController.getRechnungseingaenge(req, res))
  router.get('/rechnungseingaenge/:id', (req, res) => rechnungseingangController.getRechnungseingang(req, res))
  router.put('/rechnungseingaenge/:id', (req, res) => rechnungseingangController.updateRechnungseingang(req, res))
  router.delete('/rechnungseingaenge/:id', (req, res) => rechnungseingangController.deleteRechnungseingang(req, res))
  router.post('/rechnungseingaenge/:id/pruefen', (req, res) => rechnungseingangController.pruefenRechnungseingang(req, res))
  router.post('/rechnungseingaenge/:id/freigeben', (req, res) => rechnungseingangController.freigebenRechnungseingang(req, res))
  router.post('/rechnungseingaenge/:id/verbuchen', (req, res) => rechnungseingangController.verbuchenRechnungseingang(req, res))
  router.post('/rechnungseingaenge/:id/bezahlen', (req, res) => rechnungseingangController.bezahlenRechnungseingang(req, res))
  router.get('/rechnungseingaenge/bestellung/:bestellungId', (req, res) => rechnungseingangController.getRechnungseingaengeByBestellung(req, res))
  router.get('/rechnungseingaenge/wareneingang/:wareneingangId', (req, res) => rechnungseingangController.getRechnungseingaengeByWareneingang(req, res))
  router.get('/rechnungseingaenge/ueberfaellig', (req, res) => rechnungseingangController.getUeberfaelligeRechnungseingaenge(req, res))
  router.get('/rechnungseingaenge/abweichungen', (req, res) => rechnungseingangController.getRechnungseingaengeMitAbweichungen(req, res))
  router.get('/rechnungseingaenge/offen/betrag', (req, res) => rechnungseingangController.getGesamtOffenerBetrag(req, res))

  // Audit-Log-Routen
  router.get('/audit-logs', (req, res) => auditLogController.getAuditLogs(req, res))
  router.get('/audit-logs/entity/:entity/:entityId', (req, res) => auditLogController.getAuditLogsByEntity(req, res))
  router.get('/audit-logs/actor/:actorId', (req, res) => auditLogController.getAuditLogsByActor(req, res))
  router.get('/audit-logs/trail/:entity/:entityId', (req, res) => auditLogController.getAuditTrail(req, res))
  router.get('/audit-logs/recent', (req, res) => auditLogController.getRecentAuditLogs(req, res))
  router.get('/audit-logs/report/user/:actorId', (req, res) => auditLogController.getUserActivityReport(req, res))
  router.get('/audit-logs/report/compliance', (req, res) => auditLogController.getComplianceReport(req, res))
  router.get('/audit-logs/count', (req, res) => auditLogController.getAuditLogCount(req, res))

  // WorkflowRule-Routen
  router.post('/workflow-rules', (req, res) => workflowRuleController.createWorkflowRule(req, res))
  router.get('/workflow-rules', (req, res) => workflowRuleController.getWorkflowRules(req, res))
  router.get('/workflow-rules/:id', (req, res) => workflowRuleController.getWorkflowRule(req, res))
  router.put('/workflow-rules/:id', (req, res) => workflowRuleController.updateWorkflowRule(req, res))
  router.delete('/workflow-rules/:id', (req, res) => workflowRuleController.deleteWorkflowRule(req, res))
  router.post('/workflow-rules/:id/activate', (req, res) => workflowRuleController.activateWorkflowRule(req, res))
  router.post('/workflow-rules/:id/deactivate', (req, res) => workflowRuleController.deactivateWorkflowRule(req, res))
  router.get('/workflow-rules/matching/:triggerEntity/:triggerAction', (req, res) => workflowRuleController.getMatchingRules(req, res))
  router.post('/workflow-rules/execute/:triggerEntity/:triggerAction', (req, res) => workflowRuleController.executeWorkflowRules(req, res))

  // WorkflowExecution-Routen
  router.post('/workflow-executions', (req, res) => workflowExecutionController.createWorkflowExecution(req, res))
  router.get('/workflow-executions', (req, res) => workflowExecutionController.getWorkflowExecutions(req, res))
  router.get('/workflow-executions/:id', (req, res) => workflowExecutionController.getWorkflowExecution(req, res))
  router.get('/workflow-executions/rule/:ruleId', (req, res) => workflowExecutionController.getWorkflowExecutionsByRule(req, res))
  router.post('/workflow-executions/:id/start', (req, res) => workflowExecutionController.startWorkflowExecution(req, res))
  router.post('/workflow-executions/:id/succeed', (req, res) => workflowExecutionController.succeedWorkflowExecution(req, res))
  router.post('/workflow-executions/:id/fail', (req, res) => workflowExecutionController.failWorkflowExecution(req, res))
  router.post('/workflow-executions/:id/retry', (req, res) => workflowExecutionController.retryWorkflowExecution(req, res))
  router.get('/workflow-executions/running', (req, res) => workflowExecutionController.getRunningWorkflowExecutions(req, res))
  router.get('/workflow-executions/failed', (req, res) => workflowExecutionController.getFailedWorkflowExecutions(req, res))
  router.get('/workflow-executions/stats', (req, res) => workflowExecutionController.getWorkflowExecutionStats(req, res))

  return router
}
