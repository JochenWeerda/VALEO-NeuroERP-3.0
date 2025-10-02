"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createQueryBuilder = exports.QueryBuilder = void 0;
class QueryBuilder {
    conditions = [];
    sort;
    limit;
    offset;
    where(field, operator, value) {
        this.conditions.push({ field, operator, value });
        return this;
    }
    orderBy(field, direction = 'asc') {
        this.sort = { field, direction };
        return this;
    }
    limitCount(count) {
        this.limit = count;
        return this;
    }
    offsetCount(count) {
        this.offset = count;
        return this;
    }
    build() {
        return {
            conditions: this.conditions,
            sort: this.sort,
            limit: this.limit,
            offset: this.offset
        };
    }
}
exports.QueryBuilder = QueryBuilder;
const createQueryBuilder = () => {
    return new QueryBuilder();
};
exports.createQueryBuilder = createQueryBuilder;
