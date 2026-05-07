"use strict";
/**
 * Bootstrap for FinanzDebitor domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.initFinanzDebitorModule = initFinanzDebitorModule;
const finanzDebitor_postgres_repository_1 = require("../../infrastructure/repositories/finanzDebitor-postgres.repository");
const finanzDebitor_service_1 = require("../services/finanzDebitor.service");
const finanzDebitor_controller_1 = require("../../presentation/controllers/finanzDebitor.controller");
function initFinanzDebitorModule({ pool }) {
    const repository = new finanzDebitor_postgres_repository_1.FinanzDebitorPostgresRepository(pool);
    const service = new finanzDebitor_service_1.FinanzDebitorService(repository);
    const router = (0, finanzDebitor_controller_1.buildFinanzDebitorRouter)({ service, baseRoute: '/erp/finance/debtors' });
    return { repository, service, router };
}
//# sourceMappingURL=finanzDebitor.bootstrap.js.map