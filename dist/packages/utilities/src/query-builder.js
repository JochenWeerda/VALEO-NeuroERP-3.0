/**
 * Query builder utilities supporting the 5-Principles architecture.
 *
 * The builder is intentionally persistence-agnostic so it can be consumed
 * by in-memory, SQL, NoSQL or remote repositories without leaking
 * implementation details into the domain layer.
 */
export class QueryBuilder {
    conditions = [];
    sort;
    limitValue;
    offsetValue;
    where(field, operator, value) {
        if (operator === 'between' && !Array.isArray(value)) {
            throw new Error('Between operator requires a tuple value.');
        }
        this.conditions.push({ field, operator, value });
        return this;
    }
    orderBy(field, direction = 'asc') {
        this.sort = { field, direction };
        return this;
    }
    limit(count) {
        this.limitValue = count;
        return this;
    }
    offset(count) {
        this.offsetValue = count;
        return this;
    }
    clear() {
        this.conditions.splice(0, this.conditions.length);
        this.sort = undefined;
        this.limitValue = undefined;
        this.offsetValue = undefined;
        return this;
    }
    build() {
        return {
            conditions: [...this.conditions],
            sort: this.sort ? { ...this.sort } : undefined,
            limit: this.limitValue,
            offset: this.offsetValue,
        };
    }
}
export const createQueryBuilder = () => new QueryBuilder();
