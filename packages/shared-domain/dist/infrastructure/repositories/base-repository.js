/**
 * Base Repository Implementation for VALEO NeuroERP 3.0
 * Common repository functionality
 */
export class BaseRepository {
    entities = new Map();
    async exists(id) {
        const entity = await this.findById(id);
        return entity !== null;
    }
    createQueryBuilder() {
        return new InMemoryQueryBuilder(this);
    }
    generateId() {
        return `entity-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
}
// In-Memory Query Builder Implementation
class InMemoryQueryBuilder {
    repository;
    conditions = [];
    orderByField;
    orderByDirection = 'ASC';
    limitCount;
    offsetCount;
    constructor(repository) {
        this.repository = repository;
    }
    where(field, operator, value) {
        this.conditions.push({ field, operator, value, logic: 'AND' });
        return this;
    }
    andWhere(field, operator, value) {
        this.conditions.push({ field, operator, value, logic: 'AND' });
        return this;
    }
    orWhere(field, operator, value) {
        this.conditions.push({ field, operator, value, logic: 'OR' });
        return this;
    }
    orderBy(field, direction) {
        this.orderByField = field;
        this.orderByDirection = direction;
        return this;
    }
    limit(count) {
        this.limitCount = count;
        return this;
    }
    offset(count) {
        this.offsetCount = count;
        return this;
    }
    async execute() {
        const allEntities = await this.repository.findAll();
        let filteredEntities = this.applyConditions(allEntities);
        if (this.orderByField) {
            filteredEntities = this.applySorting(filteredEntities);
        }
        if (this.offsetCount) {
            filteredEntities = filteredEntities.slice(this.offsetCount);
        }
        if (this.limitCount) {
            filteredEntities = filteredEntities.slice(0, this.limitCount);
        }
        return filteredEntities;
    }
    async count() {
        const allEntities = await this.repository.findAll();
        const filteredEntities = this.applyConditions(allEntities);
        return filteredEntities.length;
    }
    applyConditions(entities) {
        if (this.conditions.length === 0) {
            return entities;
        }
        return entities.filter(entity => {
            let result = true;
            let currentLogic = 'AND';
            for (const condition of this.conditions) {
                const conditionResult = this.evaluateCondition(entity, condition);
                if (condition.logic === 'AND') {
                    result = result && conditionResult;
                }
                else {
                    result = result || conditionResult;
                }
                currentLogic = condition.logic;
            }
            return result;
        });
    }
    evaluateCondition(entity, condition) {
        const fieldValue = this.getFieldValue(entity, condition.field);
        switch (condition.operator) {
            case 'equals':
                return fieldValue === condition.value;
            case 'notEquals':
                return fieldValue !== condition.value;
            case 'greaterThan':
                return fieldValue > condition.value;
            case 'greaterThanOrEqual':
                return fieldValue >= condition.value;
            case 'lessThan':
                return fieldValue < condition.value;
            case 'lessThanOrEqual':
                return fieldValue <= condition.value;
            case 'like':
                return fieldValue?.toLowerCase().includes(condition.value?.toLowerCase());
            case 'notLike':
                return !fieldValue?.toLowerCase().includes(condition.value?.toLowerCase());
            case 'in':
                return Array.isArray(condition.value) && condition.value.includes(fieldValue);
            case 'notIn':
                return Array.isArray(condition.value) && !condition.value.includes(fieldValue);
            case 'isNull':
                return fieldValue === null || fieldValue === undefined;
            case 'isNotNull':
                return fieldValue !== null && fieldValue !== undefined;
            case 'between':
                if (!Array.isArray(condition.value) || condition.value.length !== 2)
                    return false;
                return fieldValue >= condition.value[0] &&
                    fieldValue <= condition.value[1];
            case 'notBetween':
                if (!Array.isArray(condition.value) || condition.value.length !== 2)
                    return true;
                return fieldValue < condition.value[0] ||
                    fieldValue > condition.value[1];
            default:
                return false;
        }
    }
    getFieldValue(entity, field) {
        const keys = field.split('.');
        let value = entity;
        for (const key of keys) {
            value = value?.[key];
        }
        return value;
    }
    applySorting(entities) {
        if (!this.orderByField)
            return entities;
        return entities.sort((a, b) => {
            const aValue = this.getFieldValue(a, this.orderByField);
            const bValue = this.getFieldValue(b, this.orderByField);
            if (aValue === bValue)
                return 0;
            const comparison = aValue < bValue ? -1 : 1;
            return this.orderByDirection === 'ASC' ? comparison : -comparison;
        });
    }
}
//# sourceMappingURL=base-repository.js.map