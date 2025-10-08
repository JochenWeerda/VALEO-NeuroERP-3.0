"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildFinanceRouter = buildFinanceRouter;
const express_1 = require("express");
const postgres_1 = require("../../infrastructure/persistence/postgres");
const finanzKonto_bootstrap_1 = require("./finanzKonto.bootstrap");
const finanzBuchung_bootstrap_1 = require("./finanzBuchung.bootstrap");
const finanzDebitor_bootstrap_1 = require("./finanzDebitor.bootstrap");
const finanzKreditor_bootstrap_1 = require("./finanzKreditor.bootstrap");
const finanzBankkonto_bootstrap_1 = require("./finanzBankkonto.bootstrap");
function buildFinanceRouter(_options = {}) {
    const pool = (0, postgres_1.getErpPool)();
    const financeRouter = (0, express_1.Router)();
    const konto = (0, finanzKonto_bootstrap_1.initFinanzKontoModule)({ pool });
    financeRouter.use(konto.router);
    const buchung = (0, finanzBuchung_bootstrap_1.initFinanzBuchungModule)({ pool });
    financeRouter.use(buchung.router);
    const debitor = (0, finanzDebitor_bootstrap_1.initFinanzDebitorModule)({ pool });
    financeRouter.use(debitor.router);
    const kreditor = (0, finanzKreditor_bootstrap_1.initFinanzKreditorModule)({ pool });
    financeRouter.use(kreditor.router);
    const bankkonto = (0, finanzBankkonto_bootstrap_1.initFinanzBankkontoModule)({ pool });
    financeRouter.use(bankkonto.router);
    return financeRouter;
}
//# sourceMappingURL=index.js.map