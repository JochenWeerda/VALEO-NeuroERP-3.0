"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createErpApiRouter = createErpApiRouter;
const express_1 = require("express");
const anfrage_controller_1 = require("./anfrage.controller");
const angebot_controller_1 = require("./angebot.controller");
const auftragsbestaetigung_controller_1 = require("./auftragsbestaetigung.controller");
const anlieferavis_controller_1 = require("./anlieferavis.controller");
const rechnungseingang_controller_1 = require("./rechnungseingang.controller");
const workflow_rule_controller_1 = require("./workflow-rule.controller");
const workflow_execution_controller_1 = require("./workflow-execution.controller");
const audit_log_controller_1 = require("./audit-log.controller");
const anfrage_service_1 = require("../../application/services/anfrage.service");
const angebot_service_1 = require("../../application/services/angebot.service");
const auftragsbestaetigung_service_1 = require("../../application/services/auftragsbestaetigung.service");
const anlieferavis_service_1 = require("../../application/services/anlieferavis.service");
const rechnungseingang_service_1 = require("../../application/services/rechnungseingang.service");
const workflow_rule_service_1 = require("../../application/services/workflow-rule.service");
const workflow_execution_service_1 = require("../../application/services/workflow-execution.service");
const audit_log_service_1 = require("../../application/services/audit-log.service");
const anfrage_postgres_repository_1 = require("../../infrastructure/repositories/anfrage-postgres.repository");
const angebot_postgres_repository_1 = require("../../infrastructure/repositories/angebot-postgres.repository");
const auftragsbestaetigung_postgres_repository_1 = require("../../infrastructure/repositories/auftragsbestaetigung-postgres.repository");
const anlieferavis_postgres_repository_1 = require("../../infrastructure/repositories/anlieferavis-postgres.repository");
const rechnungseingang_postgres_repository_1 = require("../../infrastructure/repositories/rechnungseingang-postgres.repository");
const workflow_rule_postgres_repository_1 = require("../../infrastructure/repositories/workflow-rule-postgres.repository");
const workflow_execution_postgres_repository_1 = require("../../infrastructure/repositories/workflow-execution-postgres.repository");
const audit_log_postgres_repository_1 = require("../../infrastructure/repositories/audit-log-postgres.repository");
const audit_service_1 = require("../../application/services/audit.service");
const workflow_service_1 = require("../../application/services/workflow.service");
function createErpApiRouter() {
    const router = (0, express_1.Router)();
    // TODO: Dependency Injection Container verwenden
    // Mock-Implementierungen für jetzt
    const mockPrisma = {};
    // Repositories
    const anfrageRepository = new anfrage_postgres_repository_1.AnfragePostgresRepository(mockPrisma);
    const angebotRepository = new angebot_postgres_repository_1.AngebotPostgresRepository(mockPrisma);
    const auftragsbestaetigungRepository = new auftragsbestaetigung_postgres_repository_1.AuftragsbestaetigungPostgresRepository(mockPrisma);
    const anlieferavisRepository = new anlieferavis_postgres_repository_1.AnlieferavisPostgresRepository(mockPrisma);
    const rechnungseingangRepository = new rechnungseingang_postgres_repository_1.RechnungseingangPostgresRepository(mockPrisma);
    const workflowRuleRepository = new workflow_rule_postgres_repository_1.WorkflowRulePostgresRepository(mockPrisma);
    const workflowExecutionRepository = new workflow_execution_postgres_repository_1.WorkflowExecutionPostgresRepository(mockPrisma);
    const auditLogRepository = new audit_log_postgres_repository_1.AuditLogPostgresRepository(mockPrisma);
    // Services
    const auditService = new audit_service_1.AuditService();
    const workflowService = new workflow_service_1.WorkflowService();
    const anfrageService = new anfrage_service_1.AnfrageService(anfrageRepository, auditService, workflowService);
    const angebotService = new angebot_service_1.AngebotService(angebotRepository, auditService, workflowService);
    const auftragsbestaetigungService = new auftragsbestaetigung_service_1.AuftragsbestaetigungService(auftragsbestaetigungRepository, auditService, workflowService);
    const anlieferavisService = new anlieferavis_service_1.AnlieferavisService(anlieferavisRepository, auditService, workflowService);
    const rechnungseingangService = new rechnungseingang_service_1.RechnungseingangService(rechnungseingangRepository, auditService, workflowService);
    const workflowRuleService = new workflow_rule_service_1.WorkflowRuleService(workflowRuleRepository, auditService);
    const workflowExecutionService = new workflow_execution_service_1.WorkflowExecutionService(workflowExecutionRepository, auditService);
    const auditLogService = new audit_log_service_1.AuditLogService(auditLogRepository);
    // Controllers
    const anfrageController = new anfrage_controller_1.AnfrageController(anfrageService);
    const angebotController = new angebot_controller_1.AngebotController(angebotService);
    const auftragsbestaetigungController = new auftragsbestaetigung_controller_1.AuftragsbestaetigungController(auftragsbestaetigungService);
    const anlieferavisController = new anlieferavis_controller_1.AnlieferavisController(anlieferavisService);
    const rechnungseingangController = new rechnungseingang_controller_1.RechnungseingangController(rechnungseingangService);
    const workflowRuleController = new workflow_rule_controller_1.WorkflowRuleController(workflowRuleService);
    const workflowExecutionController = new workflow_execution_controller_1.WorkflowExecutionController(workflowExecutionService);
    const auditLogController = new audit_log_controller_1.AuditLogController(auditLogService);
    // Anfrage-Routen
    router.post('/anfragen', (req, res) => anfrageController.createAnfrage(req, res));
    router.get('/anfragen', (req, res) => anfrageController.getAnfragen(req, res));
    router.get('/anfragen/:id', (req, res) => anfrageController.getAnfrage(req, res));
    router.put('/anfragen/:id', (req, res) => anfrageController.updateAnfrage(req, res));
    router.delete('/anfragen/:id', (req, res) => anfrageController.deleteAnfrage(req, res));
    router.post('/anfragen/:id/freigeben', (req, res) => anfrageController.freigebenAnfrage(req, res));
    router.get('/anfragen/ueberfaellig', (req, res) => anfrageController.getUeberfaelligeAnfragen(req, res));
    router.get('/anfragen/dringend', (req, res) => anfrageController.getDringendeAnfragen(req, res));
    // Angebot-Routen
    router.post('/angebote', (req, res) => angebotController.createAngebot(req, res));
    router.get('/angebote', (req, res) => angebotController.getAngebote(req, res));
    router.get('/angebote/:id', (req, res) => angebotController.getAngebot(req, res));
    router.put('/angebote/:id', (req, res) => angebotController.updateAngebot(req, res));
    router.delete('/angebote/:id', (req, res) => angebotController.deleteAngebot(req, res));
    router.post('/angebote/:id/pruefen', (req, res) => angebotController.pruefenAngebot(req, res));
    router.post('/angebote/:id/genehmigen', (req, res) => angebotController.genehmigenAngebot(req, res));
    router.post('/angebote/:id/ablehnen', (req, res) => angebotController.ablehnenAngebot(req, res));
    router.get('/angebote/anfrage/:anfrageId', (req, res) => angebotController.getAngeboteByAnfrage(req, res));
    router.get('/angebote/abgelaufen', (req, res) => angebotController.getAbgelaufeneAngebote(req, res));
    // Auftragsbestätigung-Routen
    router.post('/auftragsbestaetigungen', (req, res) => auftragsbestaetigungController.createAuftragsbestaetigung(req, res));
    router.get('/auftragsbestaetigungen', (req, res) => auftragsbestaetigungController.getAuftragsbestaetigungen(req, res));
    router.get('/auftragsbestaetigungen/:id', (req, res) => auftragsbestaetigungController.getAuftragsbestaetigung(req, res));
    router.put('/auftragsbestaetigungen/:id', (req, res) => auftragsbestaetigungController.updateAuftragsbestaetigung(req, res));
    router.delete('/auftragsbestaetigungen/:id', (req, res) => auftragsbestaetigungController.deleteAuftragsbestaetigung(req, res));
    router.post('/auftragsbestaetigungen/:id/pruefen', (req, res) => auftragsbestaetigungController.pruefenAuftragsbestaetigung(req, res));
    router.post('/auftragsbestaetigungen/:id/bestaetigen', (req, res) => auftragsbestaetigungController.bestaetigenAuftragsbestaetigung(req, res));
    router.get('/auftragsbestaetigungen/bestellung/:bestellungId', (req, res) => auftragsbestaetigungController.getAuftragsbestaetigungByBestellung(req, res));
    router.get('/auftragsbestaetigungen/abweichungen', (req, res) => auftragsbestaetigungController.getAuftragsbestaetigungenMitAbweichungen(req, res));
    // Anlieferavis-Routen
    router.post('/anlieferavise', (req, res) => anlieferavisController.createAnlieferavis(req, res));
    router.get('/anlieferavise', (req, res) => anlieferavisController.getAnlieferavise(req, res));
    router.get('/anlieferavise/:id', (req, res) => anlieferavisController.getAnlieferavis(req, res));
    router.put('/anlieferavise/:id', (req, res) => anlieferavisController.updateAnlieferavis(req, res));
    router.delete('/anlieferavise/:id', (req, res) => anlieferavisController.deleteAnlieferavis(req, res));
    router.post('/anlieferavise/:id/bestaetigen', (req, res) => anlieferavisController.bestaetigenAnlieferavis(req, res));
    router.post('/anlieferavise/:id/stornieren', (req, res) => anlieferavisController.stornierenAnlieferavis(req, res));
    router.get('/anlieferavise/bestellung/:bestellungId', (req, res) => anlieferavisController.getAnlieferavisByBestellung(req, res));
    router.get('/anlieferavise/ueberfaellig', (req, res) => anlieferavisController.getUeberfaelligeAnlieferavise(req, res));
    // Rechnungseingang-Routen
    router.post('/rechnungseingaenge', (req, res) => rechnungseingangController.createRechnungseingang(req, res));
    router.get('/rechnungseingaenge', (req, res) => rechnungseingangController.getRechnungseingaenge(req, res));
    router.get('/rechnungseingaenge/:id', (req, res) => rechnungseingangController.getRechnungseingang(req, res));
    router.put('/rechnungseingaenge/:id', (req, res) => rechnungseingangController.updateRechnungseingang(req, res));
    router.delete('/rechnungseingaenge/:id', (req, res) => rechnungseingangController.deleteRechnungseingang(req, res));
    router.post('/rechnungseingaenge/:id/pruefen', (req, res) => rechnungseingangController.pruefenRechnungseingang(req, res));
    router.post('/rechnungseingaenge/:id/freigeben', (req, res) => rechnungseingangController.freigebenRechnungseingang(req, res));
    router.post('/rechnungseingaenge/:id/verbuchen', (req, res) => rechnungseingangController.verbuchenRechnungseingang(req, res));
    router.post('/rechnungseingaenge/:id/bezahlen', (req, res) => rechnungseingangController.bezahlenRechnungseingang(req, res));
    router.get('/rechnungseingaenge/bestellung/:bestellungId', (req, res) => rechnungseingangController.getRechnungseingaengeByBestellung(req, res));
    router.get('/rechnungseingaenge/wareneingang/:wareneingangId', (req, res) => rechnungseingangController.getRechnungseingaengeByWareneingang(req, res));
    router.get('/rechnungseingaenge/ueberfaellig', (req, res) => rechnungseingangController.getUeberfaelligeRechnungseingaenge(req, res));
    router.get('/rechnungseingaenge/abweichungen', (req, res) => rechnungseingangController.getRechnungseingaengeMitAbweichungen(req, res));
    router.get('/rechnungseingaenge/offen/betrag', (req, res) => rechnungseingangController.getGesamtOffenerBetrag(req, res));
    // Audit-Log-Routen
    router.get('/audit-logs', (req, res) => auditLogController.getAuditLogs(req, res));
    router.get('/audit-logs/entity/:entity/:entityId', (req, res) => auditLogController.getAuditLogsByEntity(req, res));
    router.get('/audit-logs/actor/:actorId', (req, res) => auditLogController.getAuditLogsByActor(req, res));
    router.get('/audit-logs/trail/:entity/:entityId', (req, res) => auditLogController.getAuditTrail(req, res));
    router.get('/audit-logs/recent', (req, res) => auditLogController.getRecentAuditLogs(req, res));
    router.get('/audit-logs/report/user/:actorId', (req, res) => auditLogController.getUserActivityReport(req, res));
    router.get('/audit-logs/report/compliance', (req, res) => auditLogController.getComplianceReport(req, res));
    router.get('/audit-logs/count', (req, res) => auditLogController.getAuditLogCount(req, res));
    // WorkflowRule-Routen
    router.post('/workflow-rules', (req, res) => workflowRuleController.createWorkflowRule(req, res));
    router.get('/workflow-rules', (req, res) => workflowRuleController.getWorkflowRules(req, res));
    router.get('/workflow-rules/:id', (req, res) => workflowRuleController.getWorkflowRule(req, res));
    router.put('/workflow-rules/:id', (req, res) => workflowRuleController.updateWorkflowRule(req, res));
    router.delete('/workflow-rules/:id', (req, res) => workflowRuleController.deleteWorkflowRule(req, res));
    router.post('/workflow-rules/:id/activate', (req, res) => workflowRuleController.activateWorkflowRule(req, res));
    router.post('/workflow-rules/:id/deactivate', (req, res) => workflowRuleController.deactivateWorkflowRule(req, res));
    router.get('/workflow-rules/matching/:triggerEntity/:triggerAction', (req, res) => workflowRuleController.getMatchingRules(req, res));
    router.post('/workflow-rules/execute/:triggerEntity/:triggerAction', (req, res) => workflowRuleController.executeWorkflowRules(req, res));
    // WorkflowExecution-Routen
    router.post('/workflow-executions', (req, res) => workflowExecutionController.createWorkflowExecution(req, res));
    router.get('/workflow-executions', (req, res) => workflowExecutionController.getWorkflowExecutions(req, res));
    router.get('/workflow-executions/:id', (req, res) => workflowExecutionController.getWorkflowExecution(req, res));
    router.get('/workflow-executions/rule/:ruleId', (req, res) => workflowExecutionController.getWorkflowExecutionsByRule(req, res));
    router.post('/workflow-executions/:id/start', (req, res) => workflowExecutionController.startWorkflowExecution(req, res));
    router.post('/workflow-executions/:id/succeed', (req, res) => workflowExecutionController.succeedWorkflowExecution(req, res));
    router.post('/workflow-executions/:id/fail', (req, res) => workflowExecutionController.failWorkflowExecution(req, res));
    router.post('/workflow-executions/:id/retry', (req, res) => workflowExecutionController.retryWorkflowExecution(req, res));
    router.get('/workflow-executions/running', (req, res) => workflowExecutionController.getRunningWorkflowExecutions(req, res));
    router.get('/workflow-executions/failed', (req, res) => workflowExecutionController.getFailedWorkflowExecutions(req, res));
    router.get('/workflow-executions/stats', (req, res) => workflowExecutionController.getWorkflowExecutionStats(req, res));
    return router;
}
//# sourceMappingURL=erp-api-controller.js.map