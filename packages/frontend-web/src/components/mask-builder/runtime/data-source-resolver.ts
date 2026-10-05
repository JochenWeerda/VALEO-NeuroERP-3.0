/** Substitutes {entity_id}, {tenant_id}, {q} etc. in endpoint templates */
export function resolveEndpoint(
  template: string,
  vars: Record<string, string>,
): string {
  return template.replace(/\{(\w+)\}/g, (_, k: string) => vars[k] ?? '')
}

/** Appends runtime query parameters without destroying fixed screen parameters. */
export function appendQueryParams(
  endpoint: string,
  params: Record<string, string>,
): string {
  const [pathAndQuery, hash] = endpoint.split('#', 2)
  const separator = pathAndQuery.includes('?') ? '&' : '?'
  const query = new URLSearchParams(params).toString()
  if (!query) return endpoint
  return `${pathAndQuery}${separator}${query}${hash ? `#${hash}` : ''}`
}
