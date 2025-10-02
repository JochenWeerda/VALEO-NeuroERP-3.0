"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.client = exports.db = void 0;
exports.checkDatabaseConnection = checkDatabaseConnection;
exports.closeDatabaseConnection = closeDatabaseConnection;
const postgres_js_1 = require("drizzle-orm/postgres-js");
const drizzle_orm_1 = require("drizzle-orm");
const postgres_1 = __importDefault(require("postgres"));
const schema = __importStar(require("./schema"));
const connectionString = process.env.POSTGRES_URL || 'postgres://user:pass@localhost:5432/scheduler';
const client = (0, postgres_1.default)(connectionString, {
    max: 10,
    idle_timeout: 20,
    connect_timeout: 10,
});
exports.client = client;
exports.db = (0, postgres_js_1.drizzle)(client, { schema });
async function checkDatabaseConnection() {
    try {
        await exports.db.execute((0, drizzle_orm_1.sql) `SELECT 1`);
        return true;
    }
    catch (error) {
        console.error('Database connection check failed:', error);
        return false;
    }
}
async function closeDatabaseConnection() {
    await client.end();
}
//# sourceMappingURL=connection.js.map