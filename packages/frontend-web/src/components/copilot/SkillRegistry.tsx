export type SkillCategory = 'data-retrieval' | 'data-modification' | 'analysis' | 'workflow'

export interface SkillContextBase {
  tenantId: string
  userId: string
  locale?: string
}

type ParameterDefinition = {
  description: string
  required: boolean
  type: 'string' | 'number' | 'boolean' | 'json'
}

export type ParameterSchema<Params extends Record<string, unknown>> = {
  parameters: { [K in keyof Params]: ParameterDefinition }
}

export interface OutputDescriptor<Result> {
  type: 'object' | 'array' | 'scalar'
  schema: Result
}

export interface ExecutionResult<Result> {
  success: boolean
  data: Result
  message?: string
}

export type ExecuteFn<Params, Result, Context> = (
  params: Params,
  context: Context
) => Promise<ExecutionResult<Result>>

export interface SkillDefinition<
  Id extends string,
  Params extends Record<string, unknown>,
  Result,
  Context extends SkillContextBase,
> {
  readonly id: Id
  readonly name: string
  readonly description: string
  readonly category: SkillCategory
  readonly input: ParameterSchema<Params>
  readonly output: OutputDescriptor<Result>
  readonly requiredScopes: readonly string[]
  readonly mcp: {
    toolName: string
    grounding: 'user-data' | 'system-data' | 'none'
    explainable: boolean
  }
  readonly execute?: ExecuteFn<Params, Result, Context>
}

const createSkill = <Id extends string, Params extends Record<string, unknown>, Result, Context extends SkillContextBase>(
  definition: SkillDefinition<Id, Params, Result, Context>,
): SkillDefinition<Id, Params, Result, Context> => definition

interface CustomerSummary {
  id: string
  name: string
  city?: string
}

interface SearchCustomerParams extends Record<string, unknown> {
  query: string
}

interface SearchCustomerContext extends SkillContextBase {
  defaultCountry?: string
}

interface ArticlePriceParams extends Record<string, unknown> {
  articleNumber: string
  customer?: string
}

interface ArticlePriceResult {
  price: number
  currency: string
  validUntil?: string
}

interface ArticlePriceContext extends SkillContextBase {
  currency: string
}

interface SalesOrderItemInput {
  articleId: string
  quantity: number
  price?: number
}

interface CreateSalesOrderParams extends Record<string, unknown> {
  customer: string
  items: SalesOrderItemInput[]
  requestedDate?: string
}

interface CreateSalesOrderResult {
  orderId: string
  status: 'draft' | 'submitted'
}

interface CreateSalesOrderContext extends SkillContextBase {
  channel: 'web' | 'mobile' | 'api'
}

interface PolicyCheckParams extends Record<string, unknown> {
  action: string
  data: Record<string, unknown>
}

interface PolicyCheckResult {
  allowed: boolean
  violations: string[]
  warnings: string[]
}

interface PolicyCheckContext extends SkillContextBase {
  policyVersion: string
}

interface StockCheckParams extends Record<string, unknown> {
  articleNumber: string
  warehouse?: string
}

interface StockCheckResult {
  available: number
  reserved: number
  incoming: number
}

interface StockCheckContext extends SkillContextBase {
  defaultWarehouse?: string
}

export const valeoSkills = {
  searchCustomer: createSkill<'search-customer', SearchCustomerParams, CustomerSummary[], SearchCustomerContext>({
    id: 'search-customer',
    name: 'Search customer',
    description: 'Searches customers by name, number or city',
    category: 'data-retrieval',
    input: {
      parameters: {
        query: { type: 'string', required: true, description: 'Query string (name, number, city)' },
      },
    },
    output: {
      type: 'array',
      schema: [],
    },
    requiredScopes: ['sales:read', 'crm:read'],
    mcp: {
      toolName: 'searchCustomer',
      grounding: 'user-data',
      explainable: true,
    },
  }),
  getArticlePrice: createSkill<'get-article-price', ArticlePriceParams, ArticlePriceResult, ArticlePriceContext>({
    id: 'get-article-price',
    name: 'Get article price',
    description: 'Fetches current price for an article optionally for a customer',
    category: 'data-retrieval',
    input: {
      parameters: {
        articleNumber: { type: 'string', required: true, description: 'Article identifier' },
        customer: { type: 'string', required: false, description: 'Customer identifier' },
      },
    },
    output: {
      type: 'object',
      schema: { price: 0, currency: 'EUR' },
    },
    requiredScopes: ['sales:read'],
    mcp: {
      toolName: 'getArticlePrice',
      grounding: 'system-data',
      explainable: true,
    },
  }),
  createSalesOrder: createSkill<'create-sales-order', CreateSalesOrderParams, CreateSalesOrderResult, CreateSalesOrderContext>({
    id: 'create-sales-order',
    name: 'Create sales order',
    description: 'Creates a sales order with validation steps',
    category: 'workflow',
    input: {
      parameters: {
        customer: { type: 'string', required: true, description: 'Customer identifier' },
        items: { type: 'json', required: true, description: 'Array of line items' },
        requestedDate: { type: 'string', required: false, description: 'Requested delivery date (ISO 8601)' },
      },
    },
    output: {
      type: 'object',
      schema: { orderId: 'SO-000001', status: 'draft' as CreateSalesOrderResult['status'] },
    },
    requiredScopes: ['sales:write'],
    mcp: {
      toolName: 'createSalesOrder',
      grounding: 'user-data',
      explainable: true,
    },
  }),
  checkPolicy: createSkill<'check-policy', PolicyCheckParams, PolicyCheckResult, PolicyCheckContext>({
    id: 'check-policy',
    name: 'Check policy',
    description: 'Validates an action against policy rules',
    category: 'analysis',
    input: {
      parameters: {
        action: { type: 'string', required: true, description: 'Action identifier' },
        data: { type: 'json', required: true, description: 'Payload for validation' },
      },
    },
    output: {
      type: 'object',
      schema: { allowed: true, violations: [], warnings: [] },
    },
    requiredScopes: ['policy:read'],
    mcp: {
      toolName: 'checkPolicy',
      grounding: 'system-data',
      explainable: true,
    },
  }),
  checkStock: createSkill<'check-stock', StockCheckParams, StockCheckResult, StockCheckContext>({
    id: 'check-stock',
    name: 'Check stock',
    description: 'Checks inventory levels for an article',
    category: 'data-retrieval',
    input: {
      parameters: {
        articleNumber: { type: 'string', required: true, description: 'Article identifier' },
        warehouse: { type: 'string', required: false, description: 'Warehouse identifier' },
      },
    },
    output: {
      type: 'object',
      schema: { available: 0, reserved: 0, incoming: 0 },
    },
    requiredScopes: ['inventory:read'],
    mcp: {
      toolName: 'checkStock',
      grounding: 'system-data',
      explainable: true,
    },
  }),
} as const

export type ValeoSkillId = keyof typeof valeoSkills

type SkillMap = typeof valeoSkills

type SkillEntry<Id extends ValeoSkillId> = SkillMap[Id]

export type SkillParams<Id extends ValeoSkillId> = SkillEntry<Id> extends SkillDefinition<string, infer Params, unknown, SkillContextBase>
  ? Params
  : never

export type SkillContext<Id extends ValeoSkillId> = SkillEntry<Id> extends SkillDefinition<string, Record<string, unknown>, unknown, infer Context>
  ? Context
  : never

export type SkillResult<Id extends ValeoSkillId> = SkillEntry<Id> extends SkillDefinition<string, Record<string, unknown>, infer Result, SkillContextBase>
  ? Result
  : never

export class SkillExecutor {
  async executeSkill<Id extends ValeoSkillId>(
    skillId: Id,
    params: SkillParams<Id>,
    context: SkillContext<Id>,
  ): Promise<ExecutionResult<SkillResult<Id>>> {
    const skill = valeoSkills[skillId]
    if (!skill.execute) {
      return { success: true, data: skill.output.schema as SkillResult<Id> }
    }
    return skill.execute(params, context) as Promise<ExecutionResult<SkillResult<Id>>>
  }
}
