"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getErpPool = getErpPool;
exports.closeErpPool = closeErpPool;
const pg_1 = require("pg");
let singleton = null;
function getErpPool(config) {
    if (singleton !== null) {
        return singleton;
    }
    const connectionString = config?.connectionString ??
        process.env.ERP_DATABASE_URL ??
        process.env.DATABASE_URL;
    if (connectionString === undefined || connectionString === null) {
        throw new Error('DATABASE_URL oder ERP_DATABASE_URL ist nicht gesetzt. Bitte Umgebungsvariable konfigurieren.');
    }
    singleton = new pg_1.Pool({ ...config, connectionString });
    return singleton;
}
async function closeErpPool() {
    if (singleton !== null) {
        await singleton.end();
        singleton = null;
    }
}
//# sourceMappingURL=postgres.js.map