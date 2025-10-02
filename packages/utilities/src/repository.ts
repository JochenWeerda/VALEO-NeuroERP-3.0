import { ComparisonOperator, QueryBuilder, QueryDescriptor, QueryValue } from './query-builder';

export type RepositoryQuery<TEntity> = QueryDescriptor<TEntity>;

export interface Repository<TEntity, TId> {
  findById(id: TId): Promise<TEntity | null>;
  findOne(query: RepositoryQuery<TEntity>): Promise<TEntity | null>;
  findMany(query?: RepositoryQuery<TEntity>): Promise<TEntity[]>;
  create(entity: TEntity): Promise<TEntity>;
  update(id: TId, updates: Partial<TEntity>): Promise<TEntity>;
  delete(id: TId): Promise<void>;
}

export abstract class RepositoryBase<TEntity, TId> implements Repository<TEntity, TId> {
  async findOne(query: RepositoryQuery<TEntity>): Promise<TEntity | null> {
    const results = await this.findMany(query);
    return results[0] ?? null;
  }

  abstract findById(id: TId): Promise<TEntity | null>;
  abstract findMany(query?: RepositoryQuery<TEntity>): Promise<TEntity[]>;
  abstract create(entity: TEntity): Promise<TEntity>;
  abstract update(id: TId, updates: Partial<TEntity>): Promise<TEntity>;
  abstract delete(id: TId): Promise<void>;
}

export class InMemoryRepository<TEntity extends Record<IdField, TId>, IdField extends keyof TEntity, TId = TEntity[IdField]>
  extends RepositoryBase<TEntity, TId> {
  private readonly entities = new Map<TId, TEntity>();

  constructor(private readonly idField: IdField) {
    super();
  }

  async findById(id: TId): Promise<TEntity | null> {
    const entity = this.entities.get(id);
    return entity ? { ...entity } : null;
  }

  async findMany(query?: RepositoryQuery<TEntity>): Promise<TEntity[]> {
    const allEntities = Array.from(this.entities.values()).map(entity => ({ ...entity }));
    if (!query) {
      return allEntities;
    }

    const filtered = allEntities.filter(entity => matchesQuery(entity, query));
    return sortAndPaginate(filtered, query);
  }

  async create(entity: TEntity): Promise<TEntity> {
    const id = entity[this.idField];
    this.entities.set(id as TId, { ...entity });
    return { ...entity };
  }

  async update(id: TId, updates: Partial<TEntity>): Promise<TEntity> {
    const existing = this.entities.get(id);
    if (!existing) {
      throw new Error('Entity with id "' + String(id) + '" not found.');
    }

    const updated: TEntity = { ...existing, ...updates } as TEntity;
    this.entities.set(id, updated);
    return { ...updated };
  }

  async delete(id: TId): Promise<void> {
    this.entities.delete(id);
  }
}

const matchesQuery = <TEntity>(entity: TEntity, query: RepositoryQuery<TEntity>): boolean => {
  return query.conditions.every(condition => matchesCondition(entity, condition));
};

const matchesCondition = <TEntity>(
  entity: TEntity,
  condition: { field: keyof TEntity; operator: ComparisonOperator; value: QueryValue<TEntity[keyof TEntity]> }
): boolean => {
  const value = entity[condition.field];
  const conditionValue = condition.value as unknown;

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
      return Array.isArray(conditionValue) && conditionValue.includes(value as never);
    case 'notIn':
      return Array.isArray(conditionValue) && !conditionValue.includes(value as never);
    case 'like':
      return stringMatch(value, conditionValue, false);
    case 'ilike':
      return stringMatch(value, conditionValue, true);
    case 'between': {
      if (!Array.isArray(conditionValue) || conditionValue.length !== 2) {
        throw new Error('Between operator requires a tuple [min, max].');
      }
      const [minValue, maxValue] = conditionValue as [unknown, unknown];
      return compare(value, minValue) >= 0 && compare(value, maxValue) <= 0;
    }
    default:
      return false;
  }
};

const compare = (a: unknown, b: unknown): number => {
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

  return (a as any) > (b as any) ? 1 : -1;
};

const stringMatch = (value: unknown, pattern: unknown, caseInsensitive: boolean): boolean => {
  if (typeof value !== 'string' || typeof pattern !== 'string') {
    return false;
  }

  const escapeRegex = /[.*+?^${}()|[\]\\]/g;
  const escapedPattern = pattern.replace(escapeRegex, '\\$&');
  const wildcardPattern = '^' + escapedPattern.replace(/%/g, '.*').replace(/_/g, '.') + '$';
  const regex = new RegExp(wildcardPattern, caseInsensitive ? 'i' : undefined);
  return regex.test(value);
};

const sortAndPaginate = <TEntity>(entities: TEntity[], query: RepositoryQuery<TEntity>): TEntity[] => {
  let result: TEntity[] = entities;

  if (query.sort) {
    const sortField = query.sort.field;
    const direction = query.sort.direction;
    result = [...result].sort((a, b) => {
      const left = a[sortField] as unknown;
      const right = b[sortField] as unknown;
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

export const createQuery = <TEntity>(configure: (builder: QueryBuilder<TEntity>) => QueryBuilder<TEntity>): RepositoryQuery<TEntity> => {
  const builder = new QueryBuilder<TEntity>();
  return configure(builder).build();
};
