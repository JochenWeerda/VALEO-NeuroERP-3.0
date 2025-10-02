"use strict";
/**
 * Bootstrap for FinanzBankkonto domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.initFinanzBankkontoModule = initFinanzBankkontoModule;
const finanzBankkonto_postgres_repository_1 = require("../../infrastructure/repositories/finanzBankkonto-postgres.repository");
const finanzBankkonto_service_1 = require("../services/finanzBankkonto.service");
const finanzBankkonto_controller_1 = require("../../presentation/controllers/finanzBankkonto.controller");
function initFinanzBankkontoModule({ pool }) {
    const repository = new finanzBankkonto_postgres_repository_1.FinanzBankkontoPostgresRepository(pool);
    const service = new finanzBankkonto_service_1.FinanzBankkontoService(repository);
    const router = (0, finanzBankkonto_controller_1.buildFinanzBankkontoRouter)({ service, baseRoute: '/erp/finance/bank-accounts' });
    return { repository, service, router };
}
