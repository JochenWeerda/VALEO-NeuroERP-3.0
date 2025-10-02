"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createQuery = exports.InMemoryRepository = exports.RepositoryBase = void 0;
const query_builder_1 = require("./query-builder");
class RepositoryBase {
    async findOne(query) {
        const results = await this.findMany(query);
        return results[0] ?? null;
    }
}
exports.RepositoryBase = RepositoryBase;
class InMemoryRepository extends RepositoryBase {
    idField;
    entities = new Map();
    constructor(idField) {
        super();
        this.idField = idField;
    }
    async findById(id) {
        const entity = this.entities.get(id);
        return entity ? { ...entity } : null;
    }
    async findMany(query) {
        const allEntities = Array.from(this.entities.values()).map(entity => ({ ...entity }));
        if (!query) {
            return allEntities;
        }
        const filtered = allEntities.filter(entity => matchesQuery(entity, query));
        return sortAndPaginate(filtered, query);
    }
    async create(entity) {
        const id = entity[this.idField];
        this.entities.set(id, { ...entity });
        return { ...entity };
    }
    async update(id, updates) {
        const existing = this.entities.get(id);
        if (!existing) {
            throw new Error('Entity with id "' + String(id) + '" not found.');
        }
        const updated = { ...existing, ...updates };
        this.entities.set(id, updated);
        return { ...updated };
    }
    async delete(id) {
        this.entities.delete(id);
    }
}
exports.InMemoryRepository = InMemoryRepository;
const matchesQuery = (entity, query) => {
    return query.conditions.every(condition => matchesCondition(entity, condition));
};
const matchesCondition = (entity, condition) => {
    const value = entity[condition.field];
    const conditionValue = condition.value;
    switch (condition.operator) {
        case 'eq':
            return value === conditionValue;
        case 'ne':
            return value !== conditionValue;
        case 'gt':
            return compare(value, conditionValue) > 0;
        case 'gte':
            return compare(value, conditionValue) >= 0;
        case 'lt':
            return compare(value, conditionValue) < 0;
        case 'lte':
            return compare(value, conditionValue) <= 0;
        case 'in':
            return Array.isArray(conditionValue) && conditionValue.includes(value);
        case 'notIn':
            return Array.isArray(conditionValue) && !conditionValue.includes(value);
        case 'like':
            return stringMatch(value, conditionValue, false);
        case 'ilike':
            return stringMatch(value, conditionValue, true);
        case 'between': {
            if (!Array.isArray(conditionValue) || conditionValue.length !== 2) {
                throw new Error('Between operator requires a tuple [min, max].');
            }
            const [minValue, maxValue] = conditionValue;
            return compare(value, minValue) >= 0 && compare(value, maxValue) <= 0;
        }
        default:
            return false;
    }
};
const compare = (a, b) => {
    if (typeof a === 'number' && typeof b === 'number') {
        return a - b;
    }
    if (a instanceof Date && b instanceof Date) {
        return a.getTime() - b.getTime();
    }
    if (typeof a === 'string' && typeof b === 'string') {
        return a.localeCompare(b);
    }
    if (a === b) {
        return 0;
    }
    return a > b ? 1 : -1;
};
const stringMatch = (value, pattern, caseInsensitive) => {
    if (typeof value !== 'string' || typeof pattern !== 'string') {
        return false;
    }
    const escapeRegex = /[.*+?^${}()|[\]\\]/g;
    const escapedPattern = pattern.replace(escapeRegex, '\\$&');
    const wildcardPattern = '^' + escapedPattern.replace(/%/g, '.*').replace(/_/g, '.') + '$';
    const regex = new RegExp(wildcardPattern, caseInsensitive ? 'i' : undefined);
    return regex.test(value);
};
const sortAndPaginate = (entities, query) => {
    let result = entities;
    if (query.sort) {
        const sortField = query.sort.field;
        const direction = query.sort.direction;
        result = [...result].sort((a, b) => {
            const left = a[sortField];
            const right = b[sortField];
            const comparison = compare(left, right);
            return direction === 'asc' ? comparison : -comparison;
        });
    }
    if (typeof query.offset === 'number') {
        result = result.slice(query.offset);
    }
    if (typeof query.limit === 'number') {
        result = result.slice(0, query.limit);
    }
    return result;
};
const createQuery = (configure) => {
    const builder = new query_builder_1.QueryBuilder();
    return configure(builder).build();
};
exports.createQuery = createQuery;
