"use strict";
/**
 * Bootstrap for FinanzKreditor domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.initFinanzKreditorModule = initFinanzKreditorModule;
const finanzKreditor_postgres_repository_1 = require("../../infrastructure/repositories/finanzKreditor-postgres.repository");
const finanzKreditor_service_1 = require("../services/finanzKreditor.service");
const finanzKreditor_controller_1 = require("../../presentation/controllers/finanzKreditor.controller");
function initFinanzKreditorModule({ pool }) {
    const repository = new finanzKreditor_postgres_repository_1.FinanzKreditorPostgresRepository(pool);
    const service = new finanzKreditor_service_1.FinanzKreditorService(repository);
    const router = (0, finanzKreditor_controller_1.buildFinanzKreditorRouter)({ service, baseRoute: '/erp/finance/creditors' });
    return { repository, service, router };
}
//# sourceMappingURL=finanzKreditor.bootstrap.js.map