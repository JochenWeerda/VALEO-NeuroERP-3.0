"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createSyncJobRepository = createSyncJobRepository;
const data_models_1 = require("@valero-neuroerp/data-models");
function createSyncJobRepository(data) {
    return {
        ...data,
        id: (0, data_models_1.createId)('SyncJobRepositoryId'),
        createdAt: new Date(),
        updatedAt: new Date()
    };
}
//# sourceMappingURL=syncjobrepository.js.map