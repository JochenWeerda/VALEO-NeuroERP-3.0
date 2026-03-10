import { z } from 'zod'

export const ContractSchema = z.object({
  id: z.string(),
  title: z.string(),
  status: z.enum(['draft', 'active', 'closed']),
  value: z.number().optional(),
  createdAt: z.date().optional(),
})

export const InventoryItemSchema = z.object({
  sku: z.string(),
  name: z.string(),
  quantity: z.number(),
  location: z.string().optional(),
  category: z.string().optional(),
})

export const SlotRecommendationSchema = z.object({
  itemId: z.string(),
  recommendedSlot: z.string(),
  confidence: z.number(),
  reasoning: z.array(z.string()),
  expectedImprovement: z.object({
    pickingEfficiency: z.number(),
    spaceUtilization: z.number(),
    accessibility: z.number(),
  }),
})

export type Contract = z.infer<typeof ContractSchema>
export type InventoryItem = z.infer<typeof InventoryItemSchema>
export type SlotRecommendation = z.infer<typeof SlotRecommendationSchema>

export const mcpTools = {
  'inventory.optimizeSlotting': {
    name: 'inventory.optimizeSlotting',
    description: 'AI-powered slotting optimization for warehouse layout',
    parameters: z.object({
      item: InventoryItemSchema,
      warehouse: z.object({ zones: z.array(z.any()) }),
      constraints: z.object({}).optional(),
    }),
    returns: z.array(SlotRecommendationSchema),
  },
  'inventory.optimizePacking': {
    name: 'inventory.optimizePacking',
    description: 'AI-powered packing optimization with space utilization',
    parameters: z.object({
      items: z.array(InventoryItemSchema),
      constraints: z.object({}).optional(),
    }),
    returns: z.object({
      recommendations: z.array(z.any()),
      spaceEfficiency: z.number(),
    }),
  },
  'document.extractData': {
    name: 'document.extractData',
    description: 'AI-powered document data extraction',
    parameters: z.object({
      file: z.any(),
      documentType: z.enum(['invoice', 'contract', 'delivery-note']),
      extractionRules: z.array(z.any()).optional(),
    }),
    returns: z.object({
      data: z.any(),
      confidence: z.number(),
      validationErrors: z.array(z.string()),
    }),
  },
  'equipment.optimizeAutomation': {
    name: 'equipment.optimizeAutomation',
    description: 'AI-powered warehouse equipment orchestration',
    parameters: z.object({
      equipment: z.array(z.any()),
      tasks: z.array(z.any()),
      constraints: z.object({}).optional(),
    }),
    returns: z.object({
      assignments: z.array(z.any()),
      efficiency: z.number(),
      conflicts: z.array(z.any()),
    }),
  },
} as const

export class McpValidationError extends Error {
  constructor(
    message: string,
    public code: string,
    public details?: unknown
  ) {
    super(message)
    this.name = 'McpValidationError'
  }
}

export function validateMcpRequest<T>(schema: z.ZodSchema<T>, data: unknown): T {
  try {
    return schema.parse(data)
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw new McpValidationError('Validation failed', 'VALIDATION_ERROR', error.errors)
    }
    throw error
  }
}
