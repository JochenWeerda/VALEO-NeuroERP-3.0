export interface MCPMetadata<T extends Record<string, unknown> = Record<string, unknown>> {
  component: string
  category: string
  schema: T
}

export const createMCPMetadata = <T extends Record<string, unknown>>(
  component: string,
  category: string,
  schema: T,
): MCPMetadata<T> => ({
  component,
  category,
  schema,
})
