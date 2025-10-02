"use strict";
/**
 * Repository interfaces for CRM Domain
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.RepositoryBase = void 0;
class RepositoryBase {
    async findOne(query) {
        const results = await this.findMany(query);
        return results[0] ?? null;
    }
}
exports.RepositoryBase = RepositoryBase;
