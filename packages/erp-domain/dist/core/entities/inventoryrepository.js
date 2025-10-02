"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InventoryRepositoryEntity = void 0;
const data_models_1 = require("@valero-neuroerp/data-models");
class InventoryRepositoryEntity {
    constructor(props) {
        this.id = props.id;
        this.name = props.name;
        this.description = props.description;
        this.isActive = props.isActive;
        this.createdAt = props.createdAt;
        this.updatedAt = props.updatedAt;
    }
    toPrimitives() {
        return {
            id: this.id,
            name: this.name,
            description: this.description,
            isActive: this.isActive,
            createdAt: this.createdAt,
            updatedAt: this.updatedAt,
        };
    }
    static create(props) {
        const now = new Date();
        return new InventoryRepositoryEntity({
            ...props,
            id: (0, data_models_1.createId)(),
            createdAt: now,
            updatedAt: now,
        });
    }
}
exports.InventoryRepositoryEntity = InventoryRepositoryEntity;
//# sourceMappingURL=inventoryrepository.js.map