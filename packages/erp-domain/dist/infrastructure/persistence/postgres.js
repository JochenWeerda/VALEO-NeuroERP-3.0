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
    const connectionString = config?.connectionString ?? process.env.ERP_DATABASE_URL;
    if (connectionString === undefined || connectionString === null) {
        throw new Error('ERP_DATABASE_URL is not defined. Set it before initialising the ERP domain.');
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