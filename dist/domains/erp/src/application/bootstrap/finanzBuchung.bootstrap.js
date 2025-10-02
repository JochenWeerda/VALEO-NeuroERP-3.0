"use strict";
/**
 * Bootstrap for FinanzBuchung domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.initFinanzBuchungModule = initFinanzBuchungModule;
const finanzBuchung_postgres_repository_1 = require("../../infrastructure/repositories/finanzBuchung-postgres.repository");
const finanzBuchung_service_1 = require("../services/finanzBuchung.service");
const finanzBuchung_controller_1 = require("../../presentation/controllers/finanzBuchung.controller");
function initFinanzBuchungModule({ pool }) {
    const repository = new finanzBuchung_postgres_repository_1.FinanzBuchungPostgresRepository(pool);
    const service = new finanzBuchung_service_1.FinanzBuchungService(repository);
    const router = (0, finanzBuchung_controller_1.buildFinanzBuchungRouter)({ service, baseRoute: '/erp/finance/bookings' });
    return { repository, service, router };
}
