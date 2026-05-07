"use strict";
/**
 * Bootstrap for FinanzKonto domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.initFinanzKontoModule = initFinanzKontoModule;
const finanzKonto_postgres_repository_1 = require("../../infrastructure/repositories/finanzKonto-postgres.repository");
const finanzKonto_service_1 = require("../services/finanzKonto.service");
const finanzKonto_controller_1 = require("../../presentation/controllers/finanzKonto.controller");
function initFinanzKontoModule({ pool }) {
    const repository = new finanzKonto_postgres_repository_1.FinanzKontoPostgresRepository(pool);
    const service = new finanzKonto_service_1.FinanzKontoService(repository);
    const router = (0, finanzKonto_controller_1.buildFinanzKontoRouter)({ service, baseRoute: '/erp/finance/accounts' });
    return { repository, service, router };
}
//# sourceMappingURL=finanzKonto.bootstrap.js.map