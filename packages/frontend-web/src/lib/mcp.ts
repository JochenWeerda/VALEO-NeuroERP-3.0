import { useMutation, useQuery } from '@tanstack/react-query'
import { z } from 'zod'

// MCP Request/Response types
type McpRequest<T> = { service: string; action: string; payload?: T }
type McpResponse<R> = { ok: boolean; data?: R; error?: string }

// Constants for magic numbers
const STALE_TIME_MINUTES = 5
const MINUTES_TO_MS = 60
const SECONDS_TO_MS = 1000

// MCP fetch function (placeholder for actual MCP bridge)
export async function mcpFetch<TReq, TRes>(req: McpRequest<TReq>): Promise<McpResponse<TRes>> {
  // Placeholder - later replace with actual MCP WebSocket/HTTP bridge
  try {
    const res = await fetch(`/api/mcp/${req.service}/${req.action}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.payload ?? {}),
    })

    if (res.status === 404) {
      // Graceful empty response for missing endpoints to avoid noisy console errors
      return { ok: true, data: { data: [] } as unknown as TRes }
    }

    const data = await res.json()
    return data
  } catch (error) {
    // Fallback for network or parsing errors
    return { ok: false, data: undefined, error: (error as Error)?.message ?? 'UNKNOWN_ERROR' }
  }
}

// React Query hooks for MCP
export function useMcpQuery<TRes>(service: string, action: string, key: unknown[]): ReturnType<typeof useQuery<McpResponse<TRes>>> {
  return useQuery({
    queryKey: ['mcp', service, action, ...key],
    queryFn: (): Promise<McpResponse<TRes>> => mcpFetch<void, TRes>({ service, action }),
    staleTime: STALE_TIME_MINUTES * MINUTES_TO_MS * SECONDS_TO_MS,
  })
}

export function useMcpMutation<TReq, TRes>(service: string, action: string): ReturnType<typeof useMutation<McpResponse<TRes>, Error, TReq>> {
  return useMutation({
    mutationFn: (payload: TReq): Promise<McpResponse<TRes>> => mcpFetch<TReq, TRes>({ service, action, payload }),
  })
}

// Domain schemas following our specifications
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

// MCP Tool definitions (following our spec standards)
export const mcpTools = {
  // Inventory optimization tools
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

  // Document processing tools
  'document.extractData': {
    name: 'document.extractData',
    description: 'AI-powered document data extraction',
    parameters: z.object({
      file: z.any(), // File object
      documentType: z.enum(['invoice', 'contract', 'delivery-note']),
      extractionRules: z.array(z.any()).optional(),
    }),
    returns: z.object({
      data: z.any(),
      confidence: z.number(),
      validationErrors: z.array(z.string()),
    }),
  },

  // Equipment orchestration tools
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

// Error handling utilities
export class McpError extends Error {
  constructor(
    message: string,
    public code: string,
    public _details?: unknown
  ) {
    super(message)
    this.name = 'McpError'
  }
}

// Validation helpers
export function validateMcpRequest<T>(schema: z.ZodSchema<T>, data: unknown): T {
  try {
    return schema.parse(data)
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw new McpError('Validation failed', 'VALIDATION_ERROR', error.errors)
    }
    throw error
  }
}

// Audit trail for MCP actions
export interface McpAuditEntry {
  id: string
  timestamp: Date
  service: string
  action: string
  userId?: string
  success: boolean
  duration: number
  error?: string
}

export function createAuditEntry(
  service: string,
  action: string,
  success: boolean,
  duration: number,
  error?: string
): McpAuditEntry {
  return {
    id: crypto.randomUUID(),
    timestamp: new Date(),
    service,
    action,
    success,
    duration,
    error,
  }
}
